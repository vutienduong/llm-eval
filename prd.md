### Side project

Build **LLM Eval Framework**

Test cases:

```
incident triage
root cause detection
log analysis
```

Evaluation metrics:

```
accuracy
hallucination rate
latency
tool correctness
```

Architecture:

```
test_cases.yaml
        ↓
agent runner
        ↓
LLM output
        ↓
judge model
        ↓
score dashboard
```

Tech:

```
LangSmith
DeepEval
TruLens
Python
```
---

Purpose: test reliability of AI agents.

Structure:

```
test_cases.yaml
agent_runner.py
judge_model.py
metrics.py
```

Test case example:

```
scenario: CPU spike
expected:
  detect root cause
  propose fix
```

Metrics:

```
tool call correctness
response accuracy
latency
cost
```

Output dashboard:

```
eval report
score per model
```

Tools:

```
DeepEval
LangSmith
TruLens
```

Deliverable:

```
AI evaluation pipeline
```
---

## Architecture diagram

```
        +------------------+
        | Test Cases       |
        +------------------+
                 |
                 v
           Agent Runner
                 |
                 v
          LLM Responses
                 |
                 v
            Judge Model
                 |
                 v
        +----------------+
        | Metrics        |
        | accuracy       |
        | hallucination  |
        | tool success   |
        +----------------+
                 |
                 v
           Eval Dashboard
```