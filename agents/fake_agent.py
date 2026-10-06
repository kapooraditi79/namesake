"""A fully offline, non-LLM agent that applies a hardcoded fix.

Purpose: prove the sandbox -> test -> edit -> test -> score -> log loop
works correctly before any real intelligence (or API key, or internet
connection) is involved. If this agent can't make toy_001 go from fail to
pass, the bug is in your harness, not in an LLM's reasoning.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agents.base import Agent
from harness.logger import TrajectoryLogger

KNOWN_FIXES = {
    "toy_001": {
        "file": "toy_calc/ops.py",
        "find": "return price - (price * percent)",
        "replace": "return price - (price * (percent / 100))",
    },
    "toy_002":{
        "file": "toy_calc/ops.py",
        "find": "for i in range (start, end):",
        "replace": "for i in range (start, end+1):"
    }
}


class FakeAgent(Agent):
    name = "fake"

    def act(self, repo_path: Path, task: dict[str, Any], logger: TrajectoryLogger) -> int:
        task_id = task["id"]
        fix = KNOWN_FIXES.get(task_id)
        steps = 0

        if fix is None:
            logger.log("agent_action", action="no_known_fix", task_id=task_id)
            return steps

        target = repo_path / fix["file"]
        logger.log("agent_action", action="read_file", path=str(target))
        steps += 1

        content = target.read_text(encoding="utf-8")
        if fix["find"] not in content:
            logger.log("agent_action", action="fix_pattern_not_found", path=str(target))
            steps += 1
            return steps

        new_content = content.replace(fix["find"], fix["replace"])
        target.write_text(new_content, encoding="utf-8")
        logger.log(
            "agent_action",
            action="edit_file",
            path=str(target),
            find=fix["find"],
            replace=fix["replace"],
        )
        steps += 1

        return steps
