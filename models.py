from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class Expectation:
    label: str
    keywords: list[str]
    weight: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class TestCase:
    id: str
    category: str
    scenario: str
    prompt: str
    expected: list[Expectation]
    expected_tools: list[str] = field(default_factory=list)
    allowed_tools: list[str] = field(default_factory=list)
    max_latency_ms: int = 5000
    context: dict[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "category": self.category,
            "scenario": self.scenario,
            "prompt": self.prompt,
            "expected": [item.to_dict() for item in self.expected],
            "expected_tools": self.expected_tools,
            "allowed_tools": self.allowed_tools,
            "max_latency_ms": self.max_latency_ms,
            "context": self.context,
        }


@dataclass(slots=True)
class AgentOutput:
    model_name: str
    response: str
    tool_calls: list[str]
    latency_ms: float
    cost_usd: float = 0.0
    raw_output: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CaseEvaluation:
    case_id: str
    category: str
    model_name: str
    accuracy: float
    hallucination_rate: float
    tool_correctness: float
    latency_ms: float
    cost_usd: float
    overall_score: float
    criterion_scores: list[dict[str, Any]]
    tool_analysis: dict[str, Any]
    judge_notes: list[str]
    response: str
    tool_calls: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class IntegrationStatus:
    name: str
    installed: bool
    configured: bool
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

