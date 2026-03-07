from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_runner import build_runner
from integrations import detect_integrations
from judge_model import evaluate_case
from metrics import aggregate_results
from reporting import build_report_payload, write_report_artifacts
from test_case_loader import load_test_cases


ROOT = Path(__file__).resolve().parents[1]


class EvalPipelineTest(unittest.TestCase):
    def test_demo_pipeline_end_to_end(self) -> None:
        cases = load_test_cases(ROOT / "test_cases.yaml")
        runner = build_runner("demo", model_name="demo-agent")
        results = [evaluate_case(case, runner.run_case(case)) for case in cases]

        summary = aggregate_results(results)
        self.assertEqual(summary["total_cases"], 3)
        self.assertGreater(summary["overall"]["accuracy"], 0.7)
        self.assertGreater(summary["overall"]["tool_correctness"], 0.9)

        report = build_report_payload(
            project_name="LLM Eval Framework",
            cases_path="test_cases.yaml",
            summary=summary,
            results=results,
            integrations=detect_integrations(),
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            artifacts = write_report_artifacts(report, tmp_dir)
            for path in artifacts.values():
                self.assertTrue(Path(path).exists())


if __name__ == "__main__":
    unittest.main()
