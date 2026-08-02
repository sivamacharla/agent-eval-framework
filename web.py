"""Interactive web demo: runs the same eval suite used by ci_gate.py, but
lets a visitor trigger both the "good" and "regressed" agent versions and
see the gate verdict for each side by side, live.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from eval.gate import OVERALL_THRESHOLD, PER_CASE_FLOOR, evaluate_gate
from eval.runner import run_eval_suite

app = FastAPI(title="AI Agent Evaluation & Observability Framework")


class RunRequest(BaseModel):
    version: str = "good"


@app.post("/api/run")
def run(req: RunRequest):
    version = req.version if req.version in ("good", "regressed") else "good"
    results = run_eval_suite(version=version)
    verdict = evaluate_gate(results)

    return {
        "version": version,
        "results": results,
        "average": verdict.average,
        "passed": verdict.passed,
        "below_floor": verdict.below_floor,
        "threshold": OVERALL_THRESHOLD,
        "floor": PER_CASE_FLOOR,
    }


@app.get("/health")
def health():
    return {"status": "ok"}


app.mount("/", StaticFiles(directory="static", html=True), name="static")
