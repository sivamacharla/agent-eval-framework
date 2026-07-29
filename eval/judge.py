"""LLM-as-judge scoring for dimensions that aren't cleanly rule-checkable,
like hallucination. Defaults to a deterministic heuristic judge (offline,
no API key) that compares output claims against the reference/context;
swap in a real model call in `LLMJudge._judge_call` if you have API access.
"""
from __future__ import annotations

import os
import re

from .trace import Trace


class HeuristicJudge:
    """Flags likely hallucination when the output asserts specifics
    (numbers, proper nouns) that don't appear anywhere in the input,
    tool results, or reference output available to the run.
    """

    def score_hallucination(self, trace: Trace) -> float:
        grounding_text = " ".join(
            [trace.input, trace.reference_output or ""] + [tc.result for tc in trace.tool_calls]
        ).lower()

        claims = re.findall(r"\b\d+(?:\.\d+)?%?\b|\b[A-Z][a-zA-Z]{2,}\b", trace.final_output)
        if not claims:
            return 1.0  # nothing asserted, nothing to hallucinate

        ungrounded = [c for c in claims if c.lower() not in grounding_text]
        hallucination_rate = len(ungrounded) / len(claims)
        return round(1 - hallucination_rate, 3)


class LLMJudge:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "mock")
        self._heuristic = HeuristicJudge()

    def score_hallucination(self, trace: Trace) -> float:
        if self.provider == "openai":
            return self._judge_call(trace)
        return self._heuristic.score_hallucination(trace)

    def _judge_call(self, trace: Trace) -> float:
        from openai import OpenAI  # optional dependency, only imported if configured

        client = OpenAI()
        prompt = (
            "Score 0-1 how grounded this agent output is in the given context "
            "(1 = fully grounded, 0 = fabricated). Reply with only a number.\n"
            f"Context: {trace.input}\nReference: {trace.reference_output}\n"
            f"Output: {trace.final_output}"
        )
        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
        )
        try:
            return float(resp.choices[0].message.content.strip())
        except (ValueError, AttributeError):
            return self._heuristic.score_hallucination(trace)
