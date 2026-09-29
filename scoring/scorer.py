"""Turns a completed run into a scored result. Two jobs, kept separate on
purpose:

  1. score() — binary pass/fail, no ambiguity. This IS the sandbox's final
     run_tests() exit code, nothing fuzzier. Don't let this drift into
     partial-credit scoring — project_context.md section 6/13 is explicit
     that pass/fail is the only metric that answers "did it work."
  2. extract_metrics() — everything else: iteration count, wall-clock time,
     token count, estimated cost. Read from the trajectory log, not from
     the agent loop's return value, so metrics stay reconstructable from
     logs alone even if you rerun analysis later without re-running agents.

TODO (Phase 2):
    - extract_metrics: sum prompt/completion tokens across all model_call
      steps, multiply by the model's per-token price (see claude-api skill
      for current pricing) for the cost estimate.
    - wall-clock time = last step timestamp - first step timestamp.
"""

from __future__ import annotations

from dataclasses import dataclass

from sandbox.runner import SandboxResult
from trajectory.schema import TrajectoryStep


@dataclass
class ScoredResult:
    task_id: str
    run_id: str
    agent_config_name: str
    passed: bool
    iterations: int
    wall_clock_seconds: float
    prompt_tokens: int
    completion_tokens: int
    estimated_cost_usd: float


def score(sandbox_result: SandboxResult) -> bool:
    return sandbox_result.passed


def extract_metrics(steps: list[TrajectoryStep]) -> dict:
    raise NotImplementedError
