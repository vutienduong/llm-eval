from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from agent_runner import build_runner
from integrations import detect_integrations
from judge_model import evaluate_case
from metrics import aggregate_results
from reporting import build_report_payload, write_report_artifacts
from test_case_loader import load_test_cases


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate an AI agent against YAML incident-response test cases.")
    parser.add_argument("--cases", default="test_cases.yaml", help="Path to YAML test cases")
    parser.add_argument("--runner", default="demo", choices=["demo", "subprocess"], help="Runner backend")
    parser.add_argument("--command", help="Subprocess command for a real agent")
    parser.add_argument("--model-name", default="demo-agent", help="Model or agent name shown in reports")
    parser.add_argument("--project-name", default="LLM Eval Framework", help="Project label for the dashboard")
    parser.add_argument("--output-dir", help="Directory to write report artifacts")
    return parser


def default_output_dir() -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return Path("reports") / stamp


def main() -> int:
    args = build_arg_parser().parse_args()

    cases = load_test_cases(args.cases)
    runner = build_runner(runner_name=args.runner, model_name=args.model_name, command=args.command)
    integrations = detect_integrations()

    results = []
    for case in cases:
        output = runner.run_case(case)
        results.append(evaluate_case(case, output))

    summary = aggregate_results(results)
    report = build_report_payload(
        project_name=args.project_name,
        cases_path=args.cases,
        summary=summary,
        results=results,
        integrations=integrations,
    )
    output_dir = Path(args.output_dir) if args.output_dir else default_output_dir()
    artifacts = write_report_artifacts(report, output_dir)

    print(f"Evaluated {summary['total_cases']} cases for model '{args.model_name}'.")
    print(f"Overall score: {summary['overall']['overall_score']:.4f}")
    print(f"JSON report: {artifacts['json']}")
    print(f"Markdown report: {artifacts['markdown']}")
    print(f"HTML dashboard: {artifacts['html']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

