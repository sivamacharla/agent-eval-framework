"""Deterministic, rule-based checks for anything that's checkable in code —
cheaper and more reliable than LLM-as-judge for these dimensions.
"""
from __future__ import annotations

from .trace import Trace


def tool_call_correctness(trace: Trace) -> float:
    """Fraction of tool calls that matched the expected tool for that step."""
    if not trace.tool_calls:
        return 1.0
    scored = [tc for tc in trace.tool_calls if tc.expected_tool is not None]
    if not scored:
        return 1.0
    correct = sum(1 for tc in scored if tc.tool == tc.expected_tool)
    return round(correct / len(scored), 3)


def task_completion(trace: Trace) -> float:
    """Did the run produce a non-empty final answer without an unhandled error?"""
    if not trace.final_output.strip():
        return 0.0
    if "ERROR" in trace.final_output or "traceback" in trace.final_output.lower():
        return 0.0
    return 1.0


def instruction_adherence(trace: Trace) -> float:
    """Rough proxy: does the output address the key nouns/verbs from the input?"""
    input_terms = {w.lower() for w in trace.input.split() if len(w) > 4}
    if not input_terms:
        return 1.0
    output_terms = {w.lower() for w in trace.final_output.split()}
    hits = sum(1 for t in input_terms if t in output_terms)
    return round(min(1.0, hits / max(1, len(input_terms) * 0.3)), 3)
