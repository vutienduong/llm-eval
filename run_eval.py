from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import Any

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
    parser.add_argument(
        "--model",
        action="append",
        help=(
            "Repeatable model selector. Format: NAME or NAME=COMMAND. "
            "Use NAME=COMMAND to override command per model in subprocess mode."
        ),
    )
    parser.add_argument(
        "--judge",
        default="heuristic",
        choices=["heuristic", "deepeval"],
        help="Judge backend. deepeval falls back to heuristic when unavailable.",
    )
    parser.add_argument("--project-name", default="LLM Eval Framework", help="Project label for the dashboard")
    parser.add_argument("--output-dir", help="Directory to write report artifacts")
    return parser


def default_output_dir() -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return Path("reports") / stamp


def parse_model_specs(
    *,
    runner_name: str,
    model_flags: list[str] | None,
    default_model_name: str,
    default_command: str | None,
) -> list[dict[str, Any]]:
    if not model_flags:
        if runner_name == "subprocess" and not default_command:
            raise ValueError("--command is required when --runner subprocess and no --model overrides are provided")
        return [{"name": default_model_name, "command": default_command}]

    specs: list[dict[str, Any]] = []
    for raw_model in model_flags:
        raw_model = raw_model.strip()
        if not raw_model:
            raise ValueError("Empty --model value is not allowed")

        command_override: str | None
        if "=" in raw_model:
            model_name, command_override = raw_model.split("=", 1)
            model_name = model_name.strip()
            command_override = command_override.strip()
        else:
            model_name = raw_model
            command_override = default_command

        if not model_name:
            raise ValueError(f"Invalid --model value '{raw_model}'. Expected NAME or NAME=COMMAND.")
        if runner_name == "subprocess" and not command_override:
            raise ValueError(
                f"Missing command for model '{model_name}'. "
                "Use --command as default or pass --model NAME=COMMAND."
            )
        specs.append({"name": model_name, "command": command_override})
    return specs


def main() -> int:
    args = build_arg_parser().parse_args()

    cases = load_test_cases(args.cases)
    model_specs = parse_model_specs(
        runner_name=args.runner,
        model_flags=args.model,
        default_model_name=args.model_name,
        default_command=args.command,
    )
    integrations = detect_integrations()

    results = []
    for model_spec in model_specs:
        runner = build_runner(
            runner_name=args.runner,
            model_name=str(model_spec["name"]),
            command=model_spec["command"],
        )
        for case in cases:
            output = runner.run_case(case)
            results.append(evaluate_case(case, output, judge_backend=args.judge))

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

    print(f"Evaluated {summary['total_cases']} case-runs across {summary['total_models']} model(s).")
    print(f"Requested judge backend: {args.judge}")
    print(f"Overall score: {summary['overall']['overall_score']:.4f}")
    if summary.get("leaderboard"):
        best = summary["leaderboard"][0]
        print(f"Top model: {best['model_name']} ({best['overall_score']:.4f})")
    print(f"JSON report: {artifacts['json']}")
    print(f"Markdown report: {artifacts['markdown']}")
    print(f"HTML dashboard: {artifacts['html']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
