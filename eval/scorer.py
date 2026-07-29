from __future__ import annotations

from dataclasses import dataclass

from .checks import instruction_adherence, task_completion, tool_call_correctness
from .judge import LLMJudge
from .trace import Trace

DIMENSION_WEIGHTS = {
    "hallucination": 0.35,
    "tool_call_correctness": 0.25,
    "task_completion": 0.2,
    "instruction_adherence": 0.2,
}


@dataclass
class CaseScore:
    case_id: str
    hallucination: float
    tool_call_correctness: float
    task_completion: float
    instruction_adherence: float
    overall: float
    trace: Trace

    def to_dict(self) -> dict:
        d = self.__dict__.copy()
        d["trace"] = self.trace.to_dict()
        return d


class EvalPipeline:
    def __init__(self):
        self.judge = LLMJudge()

    def score(self, trace: Trace) -> CaseScore:
        hallucination = self.judge.score_hallucination(trace)
        tcc = tool_call_correctness(trace)
        tc = task_completion(trace)
        ia = instruction_adherence(trace)

        overall = (
            hallucination * DIMENSION_WEIGHTS["hallucination"]
            + tcc * DIMENSION_WEIGHTS["tool_call_correctness"]
            + tc * DIMENSION_WEIGHTS["task_completion"]
            + ia * DIMENSION_WEIGHTS["instruction_adherence"]
        )

        return CaseScore(
            case_id=trace.case_id,
            hallucination=hallucination,
            tool_call_correctness=tcc,
            task_completion=tc,
            instruction_adherence=ia,
            overall=round(overall, 3),
            trace=trace,
        )
