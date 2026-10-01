"""Turns raw run data (test results + trajectory) into a results record.

Deliberately dumb for Phase 0: resolved = tests failed before the agent
touched anything and pass after. No LLM judging, no partial credit.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

from .sandbox import TestResult


@dataclass
class RunScore:
    task_id: str
    agent_name: str
    resolved: bool
    before_passed: bool
    after_passed: bool
    duration_seconds: float
    step_count: int

    def to_dict(self) -> dict:
        return asdict(self)


def score_run(
    task_id: str,
    agent_name: str,
    before: TestResult,
    after: TestResult,
    duration_seconds: float,
    step_count: int,
) -> RunScore:
    resolved = (not before.passed) and after.passed
    return RunScore(
        task_id=task_id,
        agent_name=agent_name,
        resolved=resolved,
        before_passed=before.passed,
        after_passed=after.passed,
        duration_seconds=duration_seconds,
        step_count=step_count,
    )
