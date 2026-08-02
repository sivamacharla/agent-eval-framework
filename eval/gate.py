"""Shared gate logic used by both the CLI (ci_gate.py) and the web demo
(web.py), so "does this pass?" is defined in exactly one place.
"""
from __future__ import annotations

from dataclasses import dataclass

OVERALL_THRESHOLD = 0.75
PER_CASE_FLOOR = 0.5


@dataclass
class GateVerdict:
    passed: bool
    average: float
    below_floor: list[str]
    below_threshold: bool


def evaluate_gate(results: list[dict]) -> GateVerdict:
    if not results:
        return GateVerdict(passed=False, average=0.0, below_floor=[], below_threshold=True)

    total = sum(r["overall"] for r in results)
    average = round(total / len(results), 3)
    below_floor = [r["case_id"] for r in results if r["overall"] < PER_CASE_FLOOR]
    below_threshold = average < OVERALL_THRESHOLD

    return GateVerdict(
        passed=not (below_threshold or below_floor),
        average=average,
        below_floor=below_floor,
        below_threshold=below_threshold,
    )
