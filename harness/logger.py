"""Trajectory logging: every step of a run as one JSON object per line.

Append-only JSONL so a run can be inspected without re-running anything,
and so later phases can build a viewer/parser against a stable format.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


class TrajectoryLogger:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._steps: list[dict[str, Any]] = []

    def log(self, step_type: str, **fields: Any) -> None:
        """step_type examples: 'start', 'test_run', 'agent_action', 'result'."""
        entry = {"ts": time.time(), "step_type": step_type, **fields}
        self._steps.append(entry)

    def flush(self) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            for entry in self._steps:
                f.write(json.dumps(entry) + "\n")

    @property
    def steps(self) -> list[dict[str, Any]]:
        return list(self._steps)
