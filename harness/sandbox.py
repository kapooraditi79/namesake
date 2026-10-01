"""Sandbox interface: isolates a task's repo and runs its test command.

Two implementations share the same interface on purpose. LocalCopySandbox
works fully offline with nothing but Python — use it for all Phase 0/1
development. DockerSandbox is a stub for later, once real-world repos need
stronger isolation (pinned system deps, no accidental host pollution).
Swapping one for the other should never require touching harness/cli.py.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TestResult:
    passed: bool
    returncode: int
    stdout: str
    stderr: str


class Sandbox:
    """Interface. Subclasses must implement setup(), run_tests(), teardown()."""

    def setup(self, repo_dir: Path) -> Path:
        raise NotImplementedError

    def run_tests(self, test_command: str) -> TestResult:
        raise NotImplementedError

    def teardown(self) -> None:
        raise NotImplementedError

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.teardown()


class LocalCopySandbox(Sandbox):
    """Copies the repo into a temp dir and runs commands there via subprocess.

    No Docker, no network. Weaker isolation than a container, but it proves
    the whole pipeline (copy -> test -> patch -> test -> score -> log) works
    before you add containerization on top.
    """

    def __init__(self):
        self._workdir: Path | None = None

    def setup(self, repo_dir: Path) -> Path:
        self._workdir = Path(tempfile.mkdtemp(prefix="ael_sandbox_"))
        dest = self._workdir / "repo"
        shutil.copytree(repo_dir, dest)
        return dest

    def run_tests(self, test_command: str) -> TestResult:
        if self._workdir is None:
            raise RuntimeError("setup() must be called before run_tests()")
        repo_path = self._workdir / "repo"
        proc = subprocess.run(
            test_command,
            shell=True,
            cwd=repo_path,
            capture_output=True,
            text=True,
        )
        return TestResult(
            passed=(proc.returncode == 0),
            returncode=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
        )

    def teardown(self) -> None:
        if self._workdir is not None:
            shutil.rmtree(self._workdir, ignore_errors=True)
            self._workdir = None

    @property
    def repo_path(self) -> Path:
        if self._workdir is None:
            raise RuntimeError("setup() must be called first")
        return self._workdir / "repo"


class DockerSandbox(Sandbox):
    """Stub. Implement once you have Docker + a pulled base image and are
    back online. Same interface as LocalCopySandbox so nothing else changes.
    """

    def setup(self, repo_dir: Path) -> Path:
        raise NotImplementedError("Implement after Phase 0 offline work is done")

    def run_tests(self, test_command: str) -> TestResult:
        raise NotImplementedError

    def teardown(self) -> None:
        raise NotImplementedError
