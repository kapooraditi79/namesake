"""Runs every task in a suite against one (or more, Phase 3+) agent configs.
This is what `cli.py`'s `ael run` calls into.

TODO (Phase 2):
    - load_suite(suite_dir) -> list[TaskSpec], reading every tasks/*/task.yaml
    - for each task: build sandbox, run_agent_on_task(), score(), write
      results/<run_id>/trajectory.jsonl + append to results/<run_id>/results.csv
    - unattended end-to-end: no manual intervention once `ael run` starts.

TODO (Phase 3):
    - accept multiple AgentConfig objects, run the same suite against each,
      and diff results per task to flag regressions (a task config B fails
      that config A passed) — this is the "did config B regress" exit
      criterion from project_context.md Phase 3.
"""

from __future__ import annotations

from pathlib import Path

from agent.loop import AgentConfig


def run_suite(suite_dir: str | Path, configs: list[AgentConfig], results_dir: str | Path) -> None:
    raise NotImplementedError
