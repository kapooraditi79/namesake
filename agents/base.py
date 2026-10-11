"""Agent interface. The agent is a replaceable fixture, not the product --
keep this interface stable so LLM-backed agents and the fake agent are
interchangeable from the CLI's point of view.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from harness.logger import TrajectoryLogger


class Agent:
    name: str = "base"

    def act(self, repo_path: Path, task: dict[str, Any], logger: TrajectoryLogger, sandbox=None) -> int:
        """Attempt to resolve the task by editing files under repo_path.

        Must call logger.log(...) for every meaningful step it takes.
        Returns the number of steps/actions taken (used as a metric).

        sandbox is optional and unused by agents that never execute a
        model-chosen command (FakeAgent, DumbAgent edit files directly via
        repo_path). LLMBackedAgent subclasses need it to run commands
        inside the same container the harness scores against.
        """
        raise NotImplementedError
