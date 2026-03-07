from __future__ import annotations

import json
import subprocess
import time
from abc import ABC, abstractmethod
from typing import Any

from models import AgentOutput, TestCase


class AgentRunner(ABC):
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    @abstractmethod
    def run_case(self, case: TestCase) -> AgentOutput:
        raise NotImplementedError


class DemoAgentRunner(AgentRunner):
    def run_case(self, case: TestCase) -> AgentOutput:
        started = time.perf_counter()
        response, tool_calls = self._build_demo_response(case)
        latency_ms = (time.perf_counter() - started) * 1000
        return AgentOutput(
            model_name=self.model_name,
            response=response,
            tool_calls=tool_calls,
            latency_ms=latency_ms,
            cost_usd=0.0,
            raw_output={"runner": "demo"},
        )

    def _build_demo_response(self, case: TestCase) -> tuple[str, list[str]]:
        context = case.context
        evidence = context.get("evidence", [])
        root_cause = context.get("root_cause", "The agent needs more telemetry to isolate the issue.")
        remediation = context.get("remediation", "Collect more evidence and apply the lowest-risk rollback.")

        selected_tools = case.expected_tools[:]
        evidence_text = " ".join(f"- {item}" for item in evidence)
        response = (
            f"Incident summary: {case.scenario}.\n"
            f"Likely root cause: {root_cause}\n"
            f"Evidence reviewed from metrics/logs: {evidence_text}\n"
            f"Recommended action: {remediation}\n"
            f"Tools used: {', '.join(selected_tools) if selected_tools else 'none'}."
        )
        return response, selected_tools


class SubprocessAgentRunner(AgentRunner):
    def __init__(self, model_name: str, command: str, timeout_seconds: int = 60) -> None:
        super().__init__(model_name=model_name)
        self.command = command
        self.timeout_seconds = timeout_seconds

    def run_case(self, case: TestCase) -> AgentOutput:
        payload = json.dumps(case.to_payload())
        started = time.perf_counter()
        completed = subprocess.run(
            self.command,
            input=payload,
            capture_output=True,
            text=True,
            shell=True,
            timeout=self.timeout_seconds,
            check=False,
        )
        latency_ms = (time.perf_counter() - started) * 1000

        if completed.returncode != 0:
            stderr = completed.stderr.strip() or "subprocess failed without stderr"
            raise RuntimeError(f"Agent subprocess failed: {stderr}")

        stdout = completed.stdout.strip()
        parsed = self._parse_stdout(stdout)
        response = str(parsed.get("response", stdout))
        tool_calls = [str(item) for item in parsed.get("tool_calls", [])]
        cost_usd = float(parsed.get("cost_usd", 0.0))
        return AgentOutput(
            model_name=self.model_name,
            response=response,
            tool_calls=tool_calls,
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            raw_output=parsed,
        )

    @staticmethod
    def _parse_stdout(stdout: str) -> dict[str, Any]:
        if not stdout:
            return {}
        try:
            parsed = json.loads(stdout)
        except json.JSONDecodeError:
            return {"response": stdout}
        if isinstance(parsed, dict):
            return parsed
        return {"response": stdout}


def build_runner(runner_name: str, model_name: str, command: str | None = None) -> AgentRunner:
    if runner_name == "demo":
        return DemoAgentRunner(model_name=model_name)
    if runner_name == "subprocess":
        if not command:
            raise ValueError("--command is required when --runner subprocess")
        return SubprocessAgentRunner(model_name=model_name, command=command)
    raise ValueError(f"Unsupported runner: {runner_name}")

