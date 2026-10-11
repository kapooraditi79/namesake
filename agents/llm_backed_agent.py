"""Shared config/state for any agent that calls an LLM.

Agents that never call a model (FakeAgent, DumbAgent) should keep
inheriting directly from Agent -- this class exists so model/cost/step
accounting lives in exactly one place, instead of every LLM-backed agent
redeclaring it.

Note on history: execute_action() used to manage a raw subprocess itself
(Popen + poll + taskkill on hard timeout). That's gone -- the exact bug
that logic hit (killing the host-side process doesn't kill what's running
underneath it) reappears identically at the container boundary, so
containment and timeout enforcement both moved to DockerSandbox, which
solves it from the correct side (see harness/sandbox.py).
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from agents.base import Agent


@dataclass
class ActionResult:
    stdout: str
    stderr: str
    returncode: int | None
    timed_out: bool
    soft_flagged: bool


def check_time_flag(elapsed: float, min_time: float, max_time: float) -> str:
    """Return 'ok', 'soft_flag', or 'hard_timeout' for an action's elapsed time.

    0 for either threshold means that threshold is disabled, matching the
    0-means-no-limit convention already used elsewhere on this class.
    """
    if max_time > 0 and elapsed >= max_time:
        return "hard_timeout"
    if min_time > 0 and elapsed >= min_time:
        return "soft_flag"
    return "ok"


class LLMBackedAgent(Agent):
    def __init__(
        self,
        model: str = "qwen2.5-coder:7b",
        step_limit: int = 0,
        cost_limit: float = 3.0,
        wall_time_limit_seconds: int = 0,
        max_consecutive_format_errors: int = 0,
        min_action_time: float = 5.0,
        max_action_time: float = 30.0,
    ):
        self.model = model
        self.step_limit = step_limit
        self.cost_limit = cost_limit
        self.wall_time_limit_seconds = wall_time_limit_seconds
        self.max_consecutive_format_errors = max_consecutive_format_errors
        self.min_action_time = min_action_time
        self.max_action_time = max_action_time
        # Deliberately NOT set here -- construction time != job-start time.
        # Subclasses must set self.start_time = time.time() as the first
        # line of act()/run(). See PROJECT_CONTEXT.md SS13a.
        self.start_time: float | None = None

    def execute_action(self, command: str, sandbox) -> ActionResult:
        """Run `command` inside the task's container via `sandbox`.

        Containment AND the hard timeout are the sandbox's job now --
        DockerSandbox.exec_command enforces max_action_time with the
        container's own `timeout` utility (see harness/sandbox.py). The
        old approach here (host-side Popen + poll + taskkill) is gone --
        it was solving a problem Docker now solves differently, and more
        reliably, on the other side of the container boundary.

        This method's only remaining job is the soft-flag bookkeeping,
        which is agent-level, not something the sandbox should know about.
        Checked after the fact (exec_command blocks until done or
        hard-killed) rather than via live polling -- nothing consumes a
        mid-run flag yet, so there's nothing to react to in real time.
        """
        start = time.time()
        result = sandbox.exec_command(command, timeout=self.max_action_time)
        elapsed = time.time() - start

        status = check_time_flag(elapsed, self.min_action_time, self.max_action_time)
        return ActionResult(
            stdout=result.stdout,
            stderr=result.stderr,
            returncode=result.returncode,
            timed_out=result.timed_out,
            soft_flagged=(status in ("soft_flag", "hard_timeout")),
        )
