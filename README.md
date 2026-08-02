# AI Agent Evaluation & Observability Framework

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/sivamacharla/agent-eval-framework)

**[Live demo →](https://macharla-agent-eval-demo.onrender.com)** — runs the real eval suite against a good agent and a simulated
bad deploy side by side, live, and shows the gate flip from PASS to FAIL.
(Sleeps after 15 min idle on Render's free tier; first load takes ~30-50s.)

There's also a static trace-level viewer of one such run at
[macharla-agent-eval-viewer.netlify.app](https://macharla-agent-eval-viewer.netlify.app),
for inspecting full input/tool-calls/output per case.

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
