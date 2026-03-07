# Video Script: Introducing the LLM Eval Framework (10-15 Minutes)

## 1) Video goals

- Explain the core problem: AI agents can sound good but still be unreliable.
- Show how this app evaluates reliability with structured incident test cases.
- Run a live demo and review the dashboard output.
- Close with roadmap and a clear call-to-action.

## 2) Target audience

- AI engineers, backend engineers, SREs, and technical PMs.
- People with basic LLM/agent knowledge who need a practical quality framework.

## 3) Suggested duration

- Total: 12 minutes (flexible range: 10-15 minutes).

## 4) Detailed timeline + sample narration

### 0:00 - 0:45 | Hook

Narration:
"You might have an AI agent that sounds very confident, but once incidents happen in production, quality becomes inconsistent. In this video, I will show a lightweight framework to measure agent reliability with clear metrics: accuracy, hallucination rate, tool correctness, latency, and cost."

Visuals:
- Fast cuts of 2-3 screens: incident logs, agent output, score dashboard.

### 0:45 - 2:00 | Problem and approach

Narration:
"The hardest part is not always being wrong. It is being unpredictably wrong. So we need structured tests and explicit metrics. This app uses YAML test cases, runs an agent, scores outputs with a judge, and generates reports."

Visuals:
- Open `prd.md` and highlight the architecture.
- Switch to the Architecture section in `README.md`.

### 2:00 - 3:30 | Architecture and component communication

Narration:
"The execution flow is straightforward: test cases -> runner -> output -> judge -> metrics -> dashboard. The key integration detail is the subprocess contract: the framework sends JSON on stdin and expects JSON on stdout."

Visuals:
- Scroll through the 2 Mermaid diagrams in README.
- Zoom in on the `response`, `tool_calls`, `cost_usd` contract.

### 3:30 - 5:00 | Quick code walkthrough

Narration:
"`run_eval.py` orchestrates the pipeline. `agent_runner.py` supports demo and subprocess modes. `judge_model.py` scores expected criteria, tool usage, hallucination heuristic, and latency. Then `metrics.py` aggregates and `reporting.py` exports JSON, Markdown, and HTML."

Visuals:
- Open these files in order:
  - `run_eval.py`
  - `agent_runner.py`
  - `judge_model.py`
  - `reporting.py`

### 5:00 - 7:30 | Live demo

Narration:
"Now I will run the demo runner to show the end-to-end flow."

Terminal commands:

```bash
source .venv/bin/activate
llm-eval --cases test_cases.yaml --output-dir reports/video-demo
```

Follow-up narration:
"The command evaluates 3 cases and produces 3 artifacts: `report.json`, `report.md`, and `dashboard.html`."

Visuals:
- Show terminal output.
- Open `reports/video-demo/dashboard.html`.

### 7:30 - 9:30 | Reading the dashboard

Narration:
"Here I look at overall score, accuracy, hallucination, tool correctness, and latency. In Case Results, I can identify weak cases and debug either prompt quality or tool-use behavior."

Visuals:
- Scroll dashboard sections:
  - Hero KPI cards
  - Category scores
  - Case results
  - Integration readiness (LangSmith/DeepEval/TruLens)

### 9:30 - 11:00 | How teams can use this

Narration:
"A team can use this as a quality gate. Every prompt or model change should run this suite before release. If the score drops below threshold, stop the merge."

Visuals:
- Open `test_cases.yaml` and explain how to add a new case.
- Highlight the "CPU spike" scenario as an example.

### 11:00 - 12:00 | Roadmap and close

Narration:
"Next roadmap includes multi-model benchmark mode, LLM judge backend, LangSmith traces, TruLens feedback, and CI fail thresholds. If you want, I can build part 2: real agent integration via subprocess plus CI gating."

Visuals:
- Open the `Next roadmap` section in README.
- Outro with repository tree.

## 5) Shot list (quick production)

- Shot A: Talking head intro (20-30 seconds).
- Shot B: Screen recording of README architecture.
- Shot C: Split-screen quick code walkthrough.
- Shot D: Terminal demo run.
- Shot E: Dashboard deep dive.
- Shot F: Closing CTA.

## 6) Suggested CTA

- "Comment which model you want to benchmark next."
- "If useful, I will publish part 2: real subprocess agent integration + CI gating."

## 7) Production notes

- Keep pace fast: one key idea every 30-45 seconds.
- Show a lower-third title at each section transition.
- Use larger terminal font when running commands.
- Prefer 1080p, 30fps, clean audio.
