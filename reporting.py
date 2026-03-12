from __future__ import annotations

import json
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any

from models import CaseEvaluation, IntegrationStatus


def _pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def build_report_payload(
    *,
    project_name: str,
    cases_path: str,
    summary: dict[str, Any],
    results: list[CaseEvaluation],
    integrations: list[IntegrationStatus],
) -> dict[str, Any]:
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "project_name": project_name,
        "cases_path": cases_path,
        "summary": summary,
        "integrations": [item.to_dict() for item in integrations],
        "results": [item.to_dict() for item in results],
    }


def write_report_artifacts(report: dict[str, Any], output_dir: str | Path) -> dict[str, str]:
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)

    json_path = target / "report.json"
    markdown_path = target / "report.md"
    html_path = target / "dashboard.html"

    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    html_path.write_text(render_html(report), encoding="utf-8")

    return {
        "json": str(json_path),
        "markdown": str(markdown_path),
        "html": str(html_path),
    }


def render_markdown(report: dict[str, Any]) -> str:
    summary = report["summary"]
    overall = summary.get("overall", {})
    if not overall:
        return "# Eval Report\n\nNo results available."

    lines = [
        "# Eval Report",
        "",
        f"- Generated at: {report['generated_at']}",
        f"- Cases file: `{report['cases_path']}`",
        f"- Total cases: {summary['total_cases']}",
        f"- Total models: {summary.get('total_models', 1)}",
        f"- Judge backend usage: {summary.get('by_judge_backend', {})}",
        f"- Overall score: {_pct(overall['overall_score'])}",
        f"- Accuracy: {_pct(overall['accuracy'])}",
        f"- Hallucination rate: {_pct(overall['hallucination_rate'])}",
        f"- Tool correctness: {_pct(overall['tool_correctness'])}",
        f"- Avg latency: {overall['latency_ms']:.2f} ms",
        f"- Avg cost: ${overall['cost_usd']:.4f}",
        "",
    ]

    leaderboard = summary.get("leaderboard", [])
    if leaderboard:
        lines.extend(
            [
                "## Model Leaderboard",
                "",
                "| Rank | Model | Score | Accuracy | Hallucination | Tool correctness | Latency (ms) | Cost (USD) |",
                "| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in leaderboard:
            lines.append(
                f"| {row['rank']} | {row['model_name']} | {_pct(row['overall_score'])} | "
                f"{_pct(row['accuracy'])} | {_pct(row['hallucination_rate'])} | "
                f"{_pct(row['tool_correctness'])} | {row['latency_ms']:.2f} | ${row['cost_usd']:.4f} |"
            )
        lines.append("")

    lines.extend(
        [
        "## By Category",
        "",
        "| Category | Score | Accuracy | Hallucination | Tool correctness |",
        "| --- | ---: | ---: | ---: | ---: |",
        ]
    )

    for category, row in report["summary"]["by_category"].items():
        lines.append(
            f"| {category} | {_pct(row['overall_score'])} | {_pct(row['accuracy'])} "
            f"| {_pct(row['hallucination_rate'])} | {_pct(row['tool_correctness'])} |"
        )

    lines.extend(["", "## Case Details", ""])
    for result in report["results"]:
        lines.extend(
            [
                f"### {result['case_id']} ({result['model_name']})",
                "",
                f"- Model: {result['model_name']}",
                f"- Judge backend: {result['judge_backend']}",
                f"- Category: {result['category']}",
                f"- Score: {_pct(result['overall_score'])}",
                f"- Accuracy: {_pct(result['accuracy'])}",
                f"- Hallucination rate: {_pct(result['hallucination_rate'])}",
                f"- Tool correctness: {_pct(result['tool_correctness'])}",
                f"- Latency: {result['latency_ms']:.2f} ms",
                f"- Cost: ${result['cost_usd']:.4f}",
                f"- Tools: {', '.join(result['tool_calls']) if result['tool_calls'] else 'none'}",
                f"- Judge notes: {'; '.join(result['judge_notes']) if result['judge_notes'] else 'none'}",
                "",
                "```text",
                result["response"],
                "```",
                "",
            ]
        )

    return "\n".join(lines)


def render_html(report: dict[str, Any]) -> str:
    summary = report["summary"]
    overall = summary["overall"]
    category_rows = "".join(
        "<tr>"
        f"<td>{escape(category)}</td>"
        f"<td>{_pct(row['overall_score'])}</td>"
        f"<td>{_pct(row['accuracy'])}</td>"
        f"<td>{_pct(row['hallucination_rate'])}</td>"
        f"<td>{_pct(row['tool_correctness'])}</td>"
        "</tr>"
        for category, row in report["summary"]["by_category"].items()
    )
    leaderboard_rows = "".join(
        "<tr>"
        f"<td>{row['rank']}</td>"
        f"<td>{escape(row['model_name'])}</td>"
        f"<td>{_pct(row['overall_score'])}</td>"
        f"<td>{_pct(row['accuracy'])}</td>"
        f"<td>{_pct(row['hallucination_rate'])}</td>"
        f"<td>{_pct(row['tool_correctness'])}</td>"
        f"<td>{row['latency_ms']:.2f}</td>"
        f"<td>${row['cost_usd']:.4f}</td>"
        "</tr>"
        for row in summary.get("leaderboard", [])
    )
    judge_backend_rows = "".join(
        "<tr>"
        f"<td>{escape(backend)}</td>"
        f"<td>{count}</td>"
        "</tr>"
        for backend, count in summary.get("by_judge_backend", {}).items()
    )
    case_rows = "".join(
        "<tr>"
        f"<td>{escape(result['case_id'])}</td>"
        f"<td>{escape(result['model_name'])}</td>"
        f"<td>{escape(result['judge_backend'])}</td>"
        f"<td>{escape(result['category'])}</td>"
        f"<td>{_pct(result['overall_score'])}</td>"
        f"<td>{_pct(result['accuracy'])}</td>"
        f"<td>{_pct(result['hallucination_rate'])}</td>"
        f"<td>{_pct(result['tool_correctness'])}</td>"
        f"<td>{result['latency_ms']:.2f}</td>"
        f"<td>{escape(', '.join(result['tool_calls']) if result['tool_calls'] else 'none')}</td>"
        "</tr>"
        for result in report["results"]
    )
    integration_rows = "".join(
        "<tr>"
        f"<td>{escape(item['name'])}</td>"
        f"<td>{'yes' if item['installed'] else 'no'}</td>"
        f"<td>{'yes' if item['configured'] else 'no'}</td>"
        f"<td>{escape(item['notes'])}</td>"
        "</tr>"
        for item in report["integrations"]
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>LLM Eval Dashboard</title>
  <style>
    :root {{
      --bg: #f3efe6;
      --panel: rgba(255, 252, 245, 0.88);
      --ink: #1d2a38;
      --muted: #52606d;
      --accent: #9d4edd;
      --accent-2: #f4a261;
      --line: rgba(29, 42, 56, 0.12);
      --shadow: 0 24px 80px rgba(21, 31, 46, 0.14);
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(157, 78, 221, 0.18), transparent 32%),
        radial-gradient(circle at top right, rgba(244, 162, 97, 0.28), transparent 24%),
        linear-gradient(180deg, #f9f4ec 0%, #efe8dd 100%);
      min-height: 100vh;
    }}
    .shell {{
      width: min(1120px, calc(100vw - 32px));
      margin: 32px auto;
      padding: 28px;
      background: var(--panel);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255,255,255,0.65);
      border-radius: 28px;
      box-shadow: var(--shadow);
    }}
    h1, h2 {{
      margin: 0 0 12px;
      font-weight: 600;
      letter-spacing: -0.02em;
    }}
    p {{
      color: var(--muted);
      margin: 0;
    }}
    .hero {{
      display: grid;
      gap: 12px;
      margin-bottom: 24px;
    }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
      margin: 24px 0;
    }}
    .card {{
      padding: 18px;
      border-radius: 20px;
      background: rgba(255, 255, 255, 0.7);
      border: 1px solid var(--line);
    }}
    .card-label {{
      display: block;
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--muted);
      margin-bottom: 8px;
    }}
    .card-value {{
      font-size: 2rem;
      font-weight: 700;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 16px;
      overflow: hidden;
      border-radius: 18px;
      background: rgba(255,255,255,0.72);
    }}
    th, td {{
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }}
    th {{
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--muted);
    }}
    tr:last-child td {{
      border-bottom: none;
    }}
    .section {{
      margin-top: 28px;
    }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <h1>LLM Eval Dashboard</h1>
      <p>{escape(report['project_name'])} | Generated {escape(report['generated_at'])} | Cases file: {escape(report['cases_path'])}</p>
    </section>

    <section class="cards">
      <article class="card"><span class="card-label">Overall score</span><span class="card-value">{_pct(overall['overall_score'])}</span></article>
      <article class="card"><span class="card-label">Accuracy</span><span class="card-value">{_pct(overall['accuracy'])}</span></article>
      <article class="card"><span class="card-label">Hallucination</span><span class="card-value">{_pct(overall['hallucination_rate'])}</span></article>
      <article class="card"><span class="card-label">Tool correctness</span><span class="card-value">{_pct(overall['tool_correctness'])}</span></article>
      <article class="card"><span class="card-label">Avg latency</span><span class="card-value">{overall['latency_ms']:.0f} ms</span></article>
      <article class="card"><span class="card-label">Models compared</span><span class="card-value">{summary.get('total_models', 1)}</span></article>
    </section>

    <section class="section">
      <h2>Model Leaderboard</h2>
      <table>
        <thead>
          <tr>
            <th>Rank</th>
            <th>Model</th>
            <th>Score</th>
            <th>Accuracy</th>
            <th>Hallucination</th>
            <th>Tool correctness</th>
            <th>Latency (ms)</th>
            <th>Cost (USD)</th>
          </tr>
        </thead>
        <tbody>{leaderboard_rows}</tbody>
      </table>
    </section>

    <section class="section">
      <h2>Judge Backend Usage</h2>
      <table>
        <thead>
          <tr>
            <th>Backend</th>
            <th>Case count</th>
          </tr>
        </thead>
        <tbody>{judge_backend_rows}</tbody>
      </table>
    </section>

    <section class="section">
      <h2>Category Scores</h2>
      <table>
        <thead>
          <tr>
            <th>Category</th>
            <th>Score</th>
            <th>Accuracy</th>
            <th>Hallucination</th>
            <th>Tool correctness</th>
          </tr>
        </thead>
        <tbody>{category_rows}</tbody>
      </table>
    </section>

    <section class="section">
      <h2>Case Results</h2>
      <table>
        <thead>
          <tr>
            <th>Case</th>
            <th>Model</th>
            <th>Judge backend</th>
            <th>Category</th>
            <th>Score</th>
            <th>Accuracy</th>
            <th>Hallucination</th>
            <th>Tool correctness</th>
            <th>Latency (ms)</th>
            <th>Tools</th>
          </tr>
        </thead>
        <tbody>{case_rows}</tbody>
      </table>
    </section>

    <section class="section">
      <h2>Integration Readiness</h2>
      <table>
        <thead>
          <tr>
            <th>Tool</th>
            <th>Installed</th>
            <th>Configured</th>
            <th>Notes</th>
          </tr>
        </thead>
        <tbody>{integration_rows}</tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""
