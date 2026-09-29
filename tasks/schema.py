"""Data contract for a single AEL task. Load with `TaskSpec.from_yaml(path)`."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel


class TaskSpec(BaseModel):
    task_id: str  # e.g. "tinydb-issue-042"
    repo_url: str  # e.g. "https://github.com/msiemens/tinydb"
    base_commit: str  # commit sha the agent starts from (bug still present)
    issue_text: str  # the prompt the agent sees — what a human filed
    test_cmd: str  # e.g. "pytest tests/test_queries.py -x"
    install_cmd: str = "pip install -e ."  # run before test_cmd
    golden_patch_path: str | None = None  # optional hand-written fix, for oracle validation

    @classmethod
    def from_yaml(cls, path: str | Path) -> "TaskSpec":
        data = yaml.safe_load(Path(path).read_text())
        return cls(**data)

    def to_yaml(self, path: str | Path) -> None:
        Path(path).write_text(yaml.safe_dump(self.model_dump(exclude_none=True), sort_keys=False))
