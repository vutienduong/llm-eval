# LLM Eval Framework

Python app to evaluate incident-response agents against YAML test cases and produce JSON, Markdown, and HTML score dashboards.

## What it includes

- `test_cases.yaml`: sample cases for incident triage, root cause detection, and log analysis
- `agent_runner.py`: demo runner plus subprocess adapter for a real agent
- `judge_model.py`: rule-based judge for accuracy, hallucination rate, latency, tool correctness, and cost
- `metrics.py`: aggregate metrics by model and category
- `reporting.py`: JSON, Markdown, and HTML report generation
- `run_eval.py`: CLI entry point

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
llm-eval --cases test_cases.yaml
```

## Use your own agent

Run the evaluator against a subprocess that reads a test-case payload on stdin and returns JSON on stdout:

```json
{
  "response": "Root cause is a bad deploy...",
  "tool_calls": ["metrics_api", "deploy_history"],
  "cost_usd": 0.014
}
```

Example:

```bash
llm-eval --runner subprocess --command "python3 path/to/your_agent.py" --model-name my-agent
```

Reports are written into `reports/<timestamp>/`.

