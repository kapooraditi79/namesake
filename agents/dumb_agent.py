"""A baseline agent that takes no action at all.

Purpose: a zero-intelligence floor to compare real agents against. If
FakeAgent or a future LLMAgent can't beat DumbAgent's resolve rate on a
task, that task isn't testing anything. Deliberately has no knowledge of
KNOWN_FIXES or any task specifics -- doing nothing must work the same way
on every task, including ones FakeAgent can't solve (e.g. toy_003).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agents.base import Agent
from harness.logger import TrajectoryLogger


class DumbAgent(Agent):
    name = "dumb"

    def act(self, repo_path: Path, task: dict[str, Any], logger: TrajectoryLogger) -> int:
        logger.log("agent_action", action="no_action_taken", task_id=task["id"])
        return 0
