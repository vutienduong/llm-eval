from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agent_runner import build_runner
from integrations import detect_integrations
from judge_model import evaluate_case
from metrics import aggregate_results
from reporting import build_report_payload, write_report_artifacts
from run_eval import parse_model_specs
from test_case_loader import load_test_cases


ROOT = Path(__file__).resolve().parents[1]


class EvalPipelineTest(unittest.TestCase):
    def test_parse_model_specs_multi_model(self) -> None:
        specs = parse_model_specs(
            runner_name="subprocess",
            model_flags=["alpha=python3 alpha.py", "beta=python3 beta.py"],
            default_model_name="default",
            default_command=None,
        )
        self.assertEqual(specs[0]["name"], "alpha")
        self.assertEqual(specs[0]["command"], "python3 alpha.py")
        self.assertEqual(specs[1]["name"], "beta")
        self.assertEqual(specs[1]["command"], "python3 beta.py")

    def test_demo_pipeline_end_to_end(self) -> None:
        cases = load_test_cases(ROOT / "test_cases.yaml")
        runner = build_runner("demo", model_name="demo-agent")
        results = [evaluate_case(case, runner.run_case(case)) for case in cases]

        summary = aggregate_results(results)
        self.assertEqual(summary["total_cases"], 3)
        self.assertEqual(summary["total_models"], 1)
        self.assertGreater(summary["overall"]["accuracy"], 0.7)
        self.assertGreater(summary["overall"]["tool_correctness"], 0.9)
        self.assertEqual(len(summary["leaderboard"]), 1)
        self.assertEqual(summary["leaderboard"][0]["model_name"], "demo-agent")

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

    def test_multi_model_leaderboard(self) -> None:
        cases = load_test_cases(ROOT / "test_cases.yaml")
        results = []
        for model_name in ["alpha-model", "beta-model"]:
            runner = build_runner("demo", model_name=model_name)
            for case in cases:
                results.append(evaluate_case(case, runner.run_case(case)))

        summary = aggregate_results(results)
        self.assertEqual(summary["total_cases"], 6)
        self.assertEqual(summary["total_models"], 2)
        self.assertEqual(len(summary["leaderboard"]), 2)
        self.assertEqual(summary["leaderboard"][0]["rank"], 1)
        self.assertEqual(summary["leaderboard"][1]["rank"], 2)


if __name__ == "__main__":
    unittest.main()
