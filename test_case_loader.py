from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from models import Expectation, TestCase


def _parse_expectation(raw_item: str | dict[str, Any]) -> Expectation:
    if isinstance(raw_item, str):
        keywords = [token for token in raw_item.lower().split() if token]
        return Expectation(label=raw_item, keywords=keywords)
    return Expectation(
        label=str(raw_item["label"]),
        keywords=[str(item).lower() for item in raw_item.get("keywords", [])],
        weight=float(raw_item.get("weight", 1.0)),
    )


def load_test_cases(path: str | Path) -> list[TestCase]:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    rows = raw.get("test_cases", raw)
    cases: list[TestCase] = []
    for row in rows:
        expected = [_parse_expectation(item) for item in row.get("expected", [])]
        cases.append(
            TestCase(
                id=str(row["id"]),
                category=str(row["category"]),
                scenario=str(row["scenario"]),
                prompt=str(row["prompt"]),
                expected=expected,
                expected_tools=[str(item) for item in row.get("expected_tools", [])],
                allowed_tools=[str(item) for item in row.get("allowed_tools", [])],
                max_latency_ms=int(row.get("max_latency_ms", 5000)),
                context=dict(row.get("context", {})),
            )
        )
    return cases

