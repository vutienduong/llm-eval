from __future__ import annotations

import importlib.util
import os

from models import IntegrationStatus


def _is_installed(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def detect_integrations() -> list[IntegrationStatus]:
    return [
        IntegrationStatus(
            name="LangSmith",
            installed=_is_installed("langsmith"),
            configured=bool(os.getenv("LANGSMITH_API_KEY") or os.getenv("LANGCHAIN_API_KEY")),
            notes="Tracing can be enabled later for agent run collection.",
        ),
        IntegrationStatus(
            name="DeepEval",
            installed=_is_installed("deepeval"),
            configured=bool(os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")),
            notes="Can replace the built-in judge with model-based evals.",
        ),
        IntegrationStatus(
            name="TruLens",
            installed=_is_installed("trulens"),
            configured=_is_installed("trulens"),
            notes="Can be layered on top for feedback-function monitoring.",
        ),
    ]
