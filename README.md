# AI Agent Evaluation & Observability Framework

A continuous evaluation pipeline that scores every agent output on
hallucination rate, tool-call correctness, task completion, and
instruction adherence — wired into CI so "did the AI get worse?" is a gate,
not a guess.

## Architecture

- **Deterministic checks** (`eval/checks.py`) — tool-call correctness,
  task completion, instruction adherence: anything checkable in code.
- **LLM-as-judge** (`eval/judge.py`) — hallucination scoring by checking
  whether claims in the output are grounded in the input/tool
  results/reference. Offline heuristic judge by default; swap in a real
  model call if you have API access.
- **Trace capture** (`eval/trace.py`) — every run records reasoning steps,
  tool calls, and final output for root-causing failures instead of
  re-running and guessing.
- **Golden dataset** (`eval/golden_dataset.py`) — fixed cases with known
  expected behavior.
- **CI gate** (`ci_gate.py`) — runs the suite, fails the build if the
  average score drops below threshold or any case falls below the floor.
  Wired into `.github/workflows/eval-gate.yml`.
- **Trace viewer** (`static/trace_viewer.html`) — inspect exactly what the
  agent saw and did on any case.

## Run it

```bash
pip install -r requirements.txt
python ci_gate.py          # should PASS
```

Now simulate a bad deploy and watch the gate catch it:

```bash
# Windows PowerShell
$env:AGENT_VERSION="regressed"; python ci_gate.py
```

```bash
# bash
AGENT_VERSION=regressed python ci_gate.py   # should FAIL — fabricated answers, dropped tool calls
```

Then view traces:

```bash
python -m http.server 8080
# open http://localhost:8080/static/trace_viewer.html
```
