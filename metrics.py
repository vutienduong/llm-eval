from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Any

from models import CaseEvaluation


def _round(value: float) -> float:
    return round(value, 4)


def _build_leaderboard(by_model: dict[str, dict[str, float]]) -> list[dict[str, float | int | str]]:
    rows: list[dict[str, float | int | str]] = []
    for model_name, row in by_model.items():
        rows.append(
            {
                "model_name": model_name,
                "overall_score": row["overall_score"],
                "accuracy": row["accuracy"],
                "hallucination_rate": row["hallucination_rate"],
                "tool_correctness": row["tool_correctness"],
                "latency_ms": row["latency_ms"],
                "cost_usd": row["cost_usd"],
            }
        )
    rows.sort(
        key=lambda item: (
            -float(item["overall_score"]),
            -float(item["accuracy"]),
            float(item["hallucination_rate"]),
            float(item["latency_ms"]),
            float(item["cost_usd"]),
            str(item["model_name"]),
        )
    )
    for index, row in enumerate(rows, start=1):
        row["rank"] = index
    return rows


def aggregate_results(results: list[CaseEvaluation]) -> dict[str, Any]:
    if not results:
        return {
            "total_cases": 0,
            "total_models": 0,
            "overall": {},
            "by_category": {},
            "by_model": {},
            "leaderboard": [],
        }

    def build_bucket(rows: list[CaseEvaluation]) -> dict[str, float]:
        return {
            "accuracy": _round(mean(item.accuracy for item in rows)),
            "hallucination_rate": _round(mean(item.hallucination_rate for item in rows)),
            "tool_correctness": _round(mean(item.tool_correctness for item in rows)),
            "latency_ms": _round(mean(item.latency_ms for item in rows)),
            "cost_usd": _round(mean(item.cost_usd for item in rows)),
            "overall_score": _round(mean(item.overall_score for item in rows)),
        }

    by_category_rows: dict[str, list[CaseEvaluation]] = defaultdict(list)
    by_model_rows: dict[str, list[CaseEvaluation]] = defaultdict(list)
    for result in results:
        by_category_rows[result.category].append(result)
        by_model_rows[result.model_name].append(result)

    by_model = {key: build_bucket(rows) for key, rows in sorted(by_model_rows.items())}
    return {
        "total_cases": len(results),
        "total_models": len(by_model_rows),
        "overall": build_bucket(results),
        "by_category": {key: build_bucket(rows) for key, rows in sorted(by_category_rows.items())},
        "by_model": by_model,
        "leaderboard": _build_leaderboard(by_model),
    }
