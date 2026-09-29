"""Append-only JSONL writer for a single run's trajectory.

Usage:
    log = TrajectoryLogger(results_dir / run_id / "trajectory.jsonl")
    log.write(TrajectoryStep(task_id=..., run_id=..., step_index=0, kind="model_call", ...))
"""

from __future__ import annotations

from pathlib import Path

from trajectory.schema import TrajectoryStep


class TrajectoryLogger:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = self.path.open("a", encoding="utf-8")

    def write(self, step: TrajectoryStep) -> None:
        self._fh.write(step.model_dump_json() + "\n")
        self._fh.flush()  # a crash mid-run should still leave a readable partial log

    def close(self) -> None:
        self._fh.close()

    def __enter__(self) -> "TrajectoryLogger":
        return self

    def __exit__(self, *exc) -> None:
        self.close()


def read_trajectory(path: str | Path) -> list[TrajectoryStep]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [TrajectoryStep.model_validate_json(line) for line in lines if line.strip()]
