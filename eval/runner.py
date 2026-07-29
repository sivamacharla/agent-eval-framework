from __future__ import annotations

import json
from pathlib import Path

from .agent_under_test import run_agent
from .golden_dataset import GOLDEN_CASES
from .scorer import EvalPipeline


def run_eval_suite() -> list[dict]:
    pipeline = EvalPipeline()
    results = []
    for case in GOLDEN_CASES:
        trace = run_agent(
            case_id=case["case_id"],
            query=case["query"],
            expected_tool=case.get("expected_tool"),
            reference_output=case.get("reference_output"),
        )
        score = pipeline.score(trace)
        results.append(score.to_dict())
    return results


def write_report(results: list[dict], path: str = "report.json") -> None:
    Path(path).write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    results = run_eval_suite()
    write_report(results)
    print(f"Wrote {len(results)} case results to report.json")
