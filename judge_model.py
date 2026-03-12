from __future__ import annotations

import json
import math
import re
from typing import Any

from models import AgentOutput, CaseEvaluation, Expectation, TestCase

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "after",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[a-z0-9_]+", _normalize(text))
        if len(token) > 1 and token not in STOPWORDS
    }


def _score_expectation(expectation: Expectation, response_text: str) -> dict[str, float | str]:
    if not expectation.keywords:
        return {"label": expectation.label, "score": 0.0}
    matches = sum(1 for keyword in expectation.keywords if keyword in response_text)
    score = matches / len(expectation.keywords)
    return {"label": expectation.label, "score": round(score, 4)}


def _score_tool_calls(case: TestCase, output: AgentOutput) -> tuple[float, dict[str, object]]:
    expected = set(case.expected_tools)
    actual = set(output.tool_calls)
    allowed = set(case.allowed_tools)

    if not actual and not expected:
        return 1.0, {
            "expected": sorted(expected),
            "actual": sorted(actual),
            "unexpected": [],
            "missing": [],
        }

    unexpected = sorted(actual - allowed)
    missing = sorted(expected - actual)
    matched = actual & expected

    precision = len(matched) / len(actual) if actual else 0.0
    recall = len(matched) / len(expected) if expected else 1.0
    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * recall / (precision + recall)

    penalty = 0.15 * len(unexpected)
    score = max(0.0, min(1.0, f1 - penalty))
    return round(score, 4), {
        "expected": sorted(expected),
        "actual": sorted(actual),
        "unexpected": unexpected,
        "missing": missing,
    }


def _score_hallucination(case: TestCase, response: str) -> tuple[float, list[str]]:
    sentences = [item.strip() for item in re.split(r"[.!?\n]+", response) if item.strip()]
    grounding_terms = _tokenize(case.scenario)
    grounding_terms |= set(case.allowed_tools)
    for expectation in case.expected:
        grounding_terms |= set(expectation.keywords)
    for value in case.context.values():
        if isinstance(value, list):
            for item in value:
                grounding_terms |= _tokenize(str(item))
        else:
            grounding_terms |= _tokenize(str(value))

    hallucinated: list[str] = []
    for sentence in sentences:
        tokens = _tokenize(sentence)
        if not tokens:
            continue
        overlap = tokens & grounding_terms
        overlap_ratio = len(overlap) / len(tokens)
        if overlap_ratio < 0.2:
            hallucinated.append(sentence)

    rate = len(hallucinated) / len(sentences) if sentences else 0.0
    return round(rate, 4), hallucinated


def _latency_score(latency_ms: float, max_latency_ms: int) -> float:
    if latency_ms <= max_latency_ms:
        return 1.0
    overflow_ratio = (latency_ms - max_latency_ms) / max_latency_ms
    return max(0.0, 1.0 - overflow_ratio)


def _build_expected_text(case: TestCase) -> str:
    lines = []
    for item in case.expected:
        keyword_text = ", ".join(item.keywords) if item.keywords else "none"
        lines.append(f"- {item.label}: {keyword_text}")
    return "\n".join(lines)


def _score_with_deepeval(case: TestCase, output: AgentOutput) -> tuple[float, float, list[str]]:
    from deepeval.metrics import GEval
    from deepeval.test_case import LLMTestCase, LLMTestCaseParams

    context_blob = json.dumps(case.context, ensure_ascii=True, sort_keys=True)
    test_case = LLMTestCase(
        input=f"Scenario: {case.scenario}\nPrompt: {case.prompt}\nContext: {context_blob}",
        actual_output=output.response,
        expected_output=_build_expected_text(case),
    )

    accuracy_metric = GEval(
        name="CriteriaCoverage",
        criteria=(
            "Score how well the actual output covers expected criteria and remediation quality. "
            "Give high score when root cause, evidence, and actionable fix are all present."
        ),
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
    )
    groundedness_metric = GEval(
        name="Groundedness",
        criteria=(
            "Score how grounded the answer is in the provided scenario and context. "
            "Give low score when the answer introduces unsupported claims."
        ),
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.EXPECTED_OUTPUT,
        ],
    )

    accuracy_metric.measure(test_case)
    groundedness_metric.measure(test_case)

    accuracy = round(max(0.0, min(1.0, float(getattr(accuracy_metric, "score", 0.0)))), 4)
    groundedness = round(max(0.0, min(1.0, float(getattr(groundedness_metric, "score", 0.0)))), 4)
    hallucination_rate = round(1.0 - groundedness, 4)

    notes: list[str] = []
    if getattr(accuracy_metric, "reason", ""):
        notes.append(f"DeepEval accuracy reason: {accuracy_metric.reason}")
    if getattr(groundedness_metric, "reason", ""):
        notes.append(f"DeepEval groundedness reason: {groundedness_metric.reason}")
    return accuracy, hallucination_rate, notes


def evaluate_case(case: TestCase, output: AgentOutput, judge_backend: str = "heuristic") -> CaseEvaluation:
    response_text = _normalize(output.response)
    criterion_scores = [_score_expectation(expectation, response_text) for expectation in case.expected]
    weighted_total = sum(expectation.weight for expectation in case.expected) or 1.0
    weighted_score = 0.0
    for expectation, score_row in zip(case.expected, criterion_scores, strict=True):
        weighted_score += expectation.weight * float(score_row["score"])
    heuristic_accuracy = round(weighted_score / weighted_total, 4)

    tool_correctness, tool_analysis = _score_tool_calls(case, output)
    heuristic_hallucination_rate, hallucinated_sentences = _score_hallucination(case, output.response)

    accuracy = heuristic_accuracy
    hallucination_rate = heuristic_hallucination_rate
    effective_backend = "heuristic"
    backend_notes: list[str] = []
    if judge_backend == "deepeval":
        try:
            accuracy, hallucination_rate, backend_notes = _score_with_deepeval(case, output)
            effective_backend = "deepeval"
        except Exception as exc:
            effective_backend = "deepeval-fallback"
            backend_notes.append(f"DeepEval unavailable, used heuristic fallback: {exc.__class__.__name__}: {exc}")

    latency_component = _latency_score(output.latency_ms, case.max_latency_ms)

    overall_score = (
        0.45 * accuracy
        + 0.2 * (1.0 - hallucination_rate)
        + 0.2 * tool_correctness
        + 0.15 * latency_component
    )
    overall_score = round(max(0.0, min(1.0, overall_score)), 4)

    judge_notes = []
    if tool_analysis["missing"]:
        judge_notes.append(f"Missing expected tools: {', '.join(tool_analysis['missing'])}")
    if tool_analysis["unexpected"]:
        judge_notes.append(f"Unexpected tools: {', '.join(tool_analysis['unexpected'])}")
    if effective_backend != "deepeval" and hallucinated_sentences:
        judge_notes.append(f"Potential hallucination sentences: {len(hallucinated_sentences)}")
    judge_notes.extend(backend_notes)
    if math.isclose(accuracy, 1.0):
        judge_notes.append("All expected criteria were covered.")

    return CaseEvaluation(
        case_id=case.id,
        category=case.category,
        model_name=output.model_name,
        judge_backend=effective_backend,
        accuracy=accuracy,
        hallucination_rate=hallucination_rate,
        tool_correctness=tool_correctness,
        latency_ms=round(output.latency_ms, 2),
        cost_usd=round(output.cost_usd, 6),
        overall_score=overall_score,
        criterion_scores=criterion_scores,
        tool_analysis=tool_analysis,
        judge_notes=judge_notes,
        response=output.response,
        tool_calls=output.tool_calls,
    )
