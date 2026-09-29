"""Sandbox runner — executes one task attempt inside a throwaway Docker container.

This module knows nothing about agents or LLMs. Its whole contract is:
given a task and an optional patch, return whether the tests passed. That
narrow contract is what makes it independently testable: Phase 0's exit
criterion is proving this file works using a *hand-written* patch, before
any agent-generated patch ever touches it.

TODO (Phase 0):
    1. build_sandbox_image() — `docker build -f docker/sandbox.Dockerfile -t ael-sandbox .`
       once; reuse the image across runs (don't rebuild per task).
    2. start_container(task) — `docker run` a container, clone task.repo_url,
       `git checkout task.base_commit`, run task.install_cmd inside it.
       Prefer subprocess + the docker CLI over the docker-py SDK at first —
       it's more transparent while you're learning what's actually happening.
    3. apply_patch(container, patch) — write the patch to a temp file, copy
       it into the container (`docker cp`), `git apply` it.
    4. run_tests(container, task) — run task.test_cmd inside the container,
       capture stdout/stderr/exit code.
    5. teardown — always remove the container (`docker rm -f`), even on
       exceptions. Use try/finally, not a happy-path-only cleanup.

Design note: one container per task *attempt*, not one container reused
across the whole suite. Reuse is how state leaks between tasks and makes
results non-reproducible — the thing Phase 2's exit criterion checks for.
"""

from __future__ import annotations

from dataclasses import dataclass

from tasks.schema import TaskSpec


@dataclass
class SandboxResult:
    passed: bool
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float


def run_task_in_sandbox(task: TaskSpec, patch: str | None) -> SandboxResult:
    """Checkout task.base_commit, optionally apply `patch`, run task.test_cmd.

    `patch` is a unified diff string (or None to test the unmodified repo —
    useful as a sanity check that base_commit actually fails first).
    """
    raise NotImplementedError
