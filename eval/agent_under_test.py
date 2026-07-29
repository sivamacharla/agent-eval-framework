"""The 'system under test': a small mock agent whose behavior can be
toggled via AGENT_VERSION to simulate a regression, so the CI gate has
something real to catch. This stands in for whatever agent/prompt/model
the eval suite is actually protecting in a real project.
"""
from __future__ import annotations

import os

from .trace import Trace, ToolCall

KNOWLEDGE_BASE = {
    "refund policy": "Refunds are issued within 14 days of purchase, minus a 5% processing fee.",
    "shipping time": "Standard shipping takes 3-5 business days within the continental US.",
    "password reset": "Users can reset their password from the account settings page via emailed link.",
}


def run_agent(case_id: str, query: str, expected_tool: str | None = None, reference_output: str | None = None) -> Trace:
    version = os.getenv("AGENT_VERSION", "good")

    reasoning = [f"Parsing query: '{query}'", "Searching knowledge base for relevant entry"]
    matched_key = next((k for k in KNOWLEDGE_BASE if k in query.lower()), None)

    tool_calls = []
    if matched_key:
        tool_calls.append(ToolCall(tool="kb_lookup", args={"key": matched_key}, result=KNOWLEDGE_BASE[matched_key], expected_tool=expected_tool))
    else:
        tool_calls.append(ToolCall(tool="kb_lookup", args={"key": query}, result="NOT_FOUND", expected_tool=expected_tool))

    if version == "regressed":
        # Simulates a bad deploy: agent fabricates an answer instead of using the tool result,
        # and skips the tool entirely for some queries -- exactly what the eval suite should catch.
        if matched_key:
            final_output = f"Based on our policy, {matched_key} typically takes about 30 days and costs extra."
        else:
            final_output = "I'm not sure, but it's probably fine."
    else:
        final_output = KNOWLEDGE_BASE.get(matched_key, "I don't have information on that; escalating to a human agent.")

    return Trace(
        case_id=case_id,
        input=query,
        reasoning_steps=reasoning,
        tool_calls=tool_calls,
        final_output=final_output,
        reference_output=reference_output,
    )
