"""Shared config/state for any agent that calls an LLM.

Agents that never call a model (FakeAgent, DumbAgent) should keep
inheriting directly from Agent -- this class exists so model/cost/step
accounting lives in exactly one place, instead of every LLM-backed agent
redeclaring it.
"""


# killing of a process
# proc.kill() only kills the cmd.exe shell on Windows,
# not the actual command running underneath it as a grandchild process. 
# I proved this by testing a genuinely hanging command: 
# it took the full 10 seconds instead of stopping at the 2-second max_action_time.
# Root cause: the orphaned grandchild kept the piped stdout/stderr open, 
# so communicate() kept blocking on it. 
# Fixed with taskkill /F /T /PID (/T = kill the whole tree),

from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

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

    def execute_action(self, command: str, cwd: Path) -> ActionResult:
        """Run `command` inside `cwd`. Polls instead of blocking so a soft
        flag can fire at min_action_time before a hard kill at
        max_action_time (subprocess.run's single timeout can't do this --
        it only ever gives you a hard kill at one value).
        """
        # subprocess.popen() lets us manage a running process. we can interact with it
        # subprocess.rn will rather wait for the entire run to get completed 
        start = time.time()
        proc = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE, # capture output.
            stderr=subprocess.PIPE, # .PIPE creates a channel between my python process and the output returned
            text=True,
        )

        soft_flagged = False
        poll_interval = 0.5 # what is this??
        while True:
            try:
                # communicating with the running process
                stdout, stderr = proc.communicate(timeout=poll_interval)
                # if the timeout expires, it does not automatically shut it.
                # we get to manage it since its a popen, and manage it as an exception
                return ActionResult(
                    stdout=stdout,
                    stderr=stderr,
                    returncode=proc.returncode,
                    timed_out=False,
                    soft_flagged=soft_flagged,
                )
            except subprocess.TimeoutExpired:
                elapsed = time.time() - start
                status = check_time_flag(elapsed, self.min_action_time, self.max_action_time)
                if status == "hard_timeout":
                    # proc.kill() only kills the shell (shell=True spawns
                    # cmd.exe as the direct child) -- the actual command
                    # runs as a grandchild and survives, keeping the piped
                    # stdout/stderr open so communicate() below would hang
                    # until THAT process finishes on its own. Confirmed by
                    # reproducing it: killed at 2s, communicate() still
                    # didn't return until 10s. taskkill /T kills the whole
                    # tree, not just the top PID.

                    # windows
                    if os.name == "nt":
                        subprocess.run(
                            ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                            capture_output=True,
                        ) 
                                # - taskkill terminates processes by PID.
                                # - /F forces termination.
                                # - /T terminates the process and its child processes.
                                # - /PID specifies the process ID (proc.pid).
                                # - capture_output=True captures the command's output instead of printing it.
                    else:
                        proc.kill()
                    stdout, stderr = proc.communicate()
                    return ActionResult(
                        stdout=stdout,
                        stderr=stderr,
                        returncode=proc.returncode,
                        timed_out=True,
                        soft_flagged=soft_flagged,
                    )
                if status == "soft_flag":
                    # Nothing consumes this yet (no logger passed in here --
                    # by design, see the earlier discussion on what this
                    # method needs access to). Flag is still returned on
                    # ActionResult so it's not silently lost.
                    soft_flagged = True
