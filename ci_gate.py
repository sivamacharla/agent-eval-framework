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

from eval.runner import run_eval_suite, write_report

OVERALL_THRESHOLD = 0.75
PER_CASE_FLOOR = 0.5

console = Console()


def main() -> int:
    results = run_eval_suite()
    write_report(results)

    table = Table(title="Eval report")
    for col in ["case_id", "hallucination", "tool_call_correctness", "task_completion", "instruction_adherence", "overall"]:
        table.add_column(col)

    failures = []
    total = 0.0
    for r in results:
        table.add_row(
            r["case_id"], str(r["hallucination"]), str(r["tool_call_correctness"]),
            str(r["task_completion"]), str(r["instruction_adherence"]), str(r["overall"]),
        )
        total += r["overall"]
        if r["overall"] < PER_CASE_FLOOR:
            failures.append(r["case_id"])

    console.print(table)
    avg = round(total / len(results), 3) if results else 0.0
    console.print(f"\n[bold]Average overall score:[/bold] {avg} (threshold: {OVERALL_THRESHOLD})")

    gate_failed = avg < OVERALL_THRESHOLD or bool(failures)
    if gate_failed:
        console.print(f"[bold red]GATE FAILED[/bold red] — cases below floor: {failures or 'none'}, avg below threshold: {avg < OVERALL_THRESHOLD}")
        return 1

    console.print("[bold green]GATE PASSED[/bold green]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
