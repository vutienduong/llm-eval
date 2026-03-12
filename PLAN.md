# PLAN

Last updated: 2026-03-12 (Asia/Ho_Chi_Minh)

## Roadmap execution status

- [x] Phase 1 / Step 1: Multi-model comparison in one run with repeated `--model`.
- [x] Phase 1 / Step 1: Leaderboard output in JSON, Markdown, and HTML dashboard.
- [x] Phase 1 / Step 2: Optional LLM-as-a-judge backend (DeepEval) with deterministic fallback.
- [ ] Phase 2 / Step 1: LangSmith tracing integration and trace links in report.
- [ ] Phase 2 / Step 2: TruLens feedback functions for faithfulness/safety.
- [ ] Phase 3 / Step 1: CI fail threshold mode (`--fail-threshold`).
- [ ] Phase 3 / Step 2: Scenario packs and regression snapshots by incident domain.

## What was implemented in this iteration

- Added optional judge backend selection in CLI:
  - `--judge heuristic` (default)
  - `--judge deepeval`
- Added safe DeepEval path with deterministic fallback:
  - If DeepEval fails or is unavailable, scoring falls back to heuristic.
  - Case result records backend as `deepeval-fallback`.
- Added judge backend visibility:
  - New `judge_backend` field per case result.
  - New summary `by_judge_backend` count.
  - Dashboard and markdown now display judge backend usage.
- Added regression test for deepeval fallback behavior.
- Kept previous multi-model + leaderboard features working.

## Validation

- `python -m unittest discover -s tests -v`
- `llm-eval --cases test_cases.yaml --runner demo --model model-a --model model-b`
- `llm-eval --cases test_cases.yaml --judge deepeval`

## Next implementation target

- Phase 2 / Step 1: LangSmith tracing integration and trace links in `report.json`.
