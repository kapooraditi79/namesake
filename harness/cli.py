"""Entry point: python -m harness.cli run --task tasks/toy_001 --agent fake"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from agents.dumb_agent import DumbAgent
from agents.fake_agent import FakeAgent
from harness.logger import TrajectoryLogger
from harness.sandbox import LocalCopySandbox
from harness.scorer import score_run

AGENTS = {
    "fake": FakeAgent,
    "dumb": DumbAgent,
}


def run_task(task_dir: Path, agent_name: str) -> int:
    task = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
    repo_dir = task_dir / task["repo_dir"]
    test_command = task["test_command"]

    run_id = time.strftime("%Y%m%d_%H%M%S")
    run_dir = task_dir / "runs" / run_id
    logger = TrajectoryLogger(run_dir / "trajectory.jsonl")

    agent_cls = AGENTS[agent_name]
    agent = agent_cls()

    start = time.time()
    logger.log("start", task_id=task["id"], agent=agent.name, issue=task["issue"])

    with LocalCopySandbox() as sandbox:
        sandbox.setup(repo_dir)

        before = sandbox.run_tests(test_command)
        logger.log("test_run", phase="before", passed=before.passed, returncode=before.returncode)

        step_count = agent.act(sandbox.repo_path, task, logger)

        after = sandbox.run_tests(test_command)
        logger.log("test_run", phase="after", passed=after.passed, returncode=after.returncode)

    duration = time.time() - start
    result = score_run(
        task_id=task["id"],
        agent_name=agent.name,
        before=before,
        after=after,
        duration_seconds=duration,
        step_count=step_count,
    )
    logger.log("result", **result.to_dict())
    logger.flush()

    (run_dir / "result.json").write_text(
        json.dumps(result.to_dict(), indent=2), encoding="utf-8"
    )

    status = "RESOLVED" if result.resolved else "NOT RESOLVED"
    print(f"[{task['id']}] agent={agent.name} -> {status}")
    print(f"  before tests passed: {before.passed}")
    print(f"  after tests passed:  {after.passed}")
    print(f"  steps taken:         {step_count}")
    print(f"  duration:            {duration:.2f}s")
    print(f"  trajectory log:      {run_dir / 'trajectory.jsonl'}")

    return 0 if result.resolved else 1


def main() -> int:
    parser = argparse.ArgumentParser(prog="ael")
    sub = parser.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Run one task with one agent")
    run_p.add_argument("--task", required=True, type=Path, help="Path to task directory")
    run_p.add_argument("--agent", required=True, choices=list(AGENTS.keys()))

    args = parser.parse_args()

    if args.command == "run":
        return run_task(args.task, args.agent)

    return 1


if __name__ == "__main__":
    sys.exit(main())
