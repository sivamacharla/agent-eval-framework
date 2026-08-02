"""CI/CD gate: wire this into a pipeline step so any prompt, model, or
agent-logic change is automatically regression-tested against the golden
dataset before it can ship. Exits non-zero (fails the build) if the
average score across dimensions drops below threshold, or any single case
falls below the floor.

Usage:
    python ci_gate.py                 # uses AGENT_VERSION=good by default
    AGENT_VERSION=regressed python ci_gate.py   # simulates a bad deploy -> should fail
"""
from __future__ import annotations

import sys

from rich.console import Console
from rich.table import Table

from eval.gate import OVERALL_THRESHOLD, evaluate_gate
from eval.runner import run_eval_suite, write_report

console = Console()


def main() -> int:
    results = run_eval_suite()
    write_report(results)

    table = Table(title="Eval report")
    for col in ["case_id", "hallucination", "tool_call_correctness", "task_completion", "instruction_adherence", "overall"]:
        table.add_column(col)
    for r in results:
        table.add_row(
            r["case_id"], str(r["hallucination"]), str(r["tool_call_correctness"]),
            str(r["task_completion"]), str(r["instruction_adherence"]), str(r["overall"]),
        )
    console.print(table)

    verdict = evaluate_gate(results)
    console.print(f"\n[bold]Average overall score:[/bold] {verdict.average} (threshold: {OVERALL_THRESHOLD})")

    if not verdict.passed:
        console.print(f"[bold red]GATE FAILED[/bold red] — cases below floor: {verdict.below_floor or 'none'}, avg below threshold: {verdict.below_threshold}")
        return 1

    console.print("[bold green]GATE PASSED[/bold green]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
