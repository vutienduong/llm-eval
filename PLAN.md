# PLAN

Last updated: 2026-03-12 (Asia/Ho_Chi_Minh)

## Roadmap execution status

- [x] Phase 1 / Step 1: Multi-model comparison in one run with repeated `--model`.
- [x] Phase 1 / Step 1: Leaderboard output in JSON, Markdown, and HTML dashboard.
- [ ] Phase 1 / Step 2: Optional LLM-as-a-judge backend (DeepEval) with deterministic fallback.
- [ ] Phase 2 / Step 1: LangSmith tracing integration and trace links in report.
- [ ] Phase 2 / Step 2: TruLens feedback functions for faithfulness/safety.
- [ ] Phase 3 / Step 1: CI fail threshold mode (`--fail-threshold`).
- [ ] Phase 3 / Step 2: Scenario packs and regression snapshots by incident domain.

## What was implemented in this iteration

- Added repeatable `--model` support in CLI:
  - `--model NAME`
  - `--model NAME=COMMAND` for subprocess per-model command override.
- Kept backward compatibility:
  - Existing single-model flags (`--model-name`, `--runner`, `--command`) still work.
- Added summary fields:
  - `total_models`
  - `leaderboard` with rank and model metrics.
- Added leaderboard rendering:
  - Markdown report section.
  - HTML dashboard table.
  - Case results table now includes model column.
- Added tests for:
  - Model spec parsing.
  - Multi-model leaderboard aggregation.
- Updated README usage docs for multi-model execution.

## Validation

- `python -m unittest discover -s tests -v`
- `llm-eval --cases test_cases.yaml --runner demo --model model-a --model model-b`

## Next implementation target

- Phase 1 / Step 2: Add judge backend selection (heuristic vs DeepEval) with a clean interface:
  - `--judge heuristic` (default)
  - `--judge deepeval`
  - strict fallback to heuristic when API key or dependency is missing.
