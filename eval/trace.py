"""Trace-level observability: captures inputs, intermediate tool calls,
reasoning steps, and final output for a single agent run, so a failure
can be root-caused from the trace instead of re-run and guessed at.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ToolCall:
    tool: str
    args: dict
    result: str
    expected_tool: str | None = None


@dataclass
class Trace:
    case_id: str
    input: str
    reasoning_steps: list[str]
    tool_calls: list[ToolCall]
    final_output: str
    reference_output: str | None = None

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "input": self.input,
            "reasoning_steps": self.reasoning_steps,
            "tool_calls": [tc.__dict__ for tc in self.tool_calls],
            "final_output": self.final_output,
            "reference_output": self.reference_output,
        }
