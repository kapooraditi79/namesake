"""Sandbox interface: isolates a task's repo and runs its test command.

Two implementations share the same interface on purpose. LocalCopySandbox
works fully offline with nothing but Python — use it for all Phase 0/1
development. DockerSandbox is a stub for later, once real-world repos need
stronger isolation (pinned system deps, no accidental host pollution).
Swapping one for the other should never require touching harness/cli.py.
"""

from __future__ import annotations

import shlex
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


@dataclass
class TestResult:
    passed: bool
    returncode: int
    stdout: str
    stderr: str


@dataclass
class ExecResult:
    """Generic container command result. Deliberately has no 'soft_flagged'
    concept -- that's agent-level bookkeeping (LLMBackedAgent), not
    something the sandbox itself should know about.
    """

    stdout: str
    stderr: str
    returncode: int
    timed_out: bool


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

    # is this the scoring run? where once the task is executed by the agent, it gets scored here? using this cmd?
    def run_tests(self, test_command: str) -> TestResult:
        if self._workdir is None:
            raise RuntimeError("setup() must be called before run_tests()")
        repo_path = self._workdir / "repo"
        proc = subprocess.run(
            test_command,
            shell=True, #Allows running arbitrary shell commands given as a string (like cd, ls, pipes, etc.)
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
    """One container per task attempt. Repo is copied in fresh (docker cp),
    never bind-mounted -- the container has no view of the host filesystem
    beyond what's explicitly copied.

    exec_command() is the one agents call for arbitrary (model-chosen)
    commands. run_tests() is the harness's own fixed scoring command. Both
    share the same container, which is the whole point: an edit the agent
    makes must be visible to the harness's own before/after test run.
    """

    IMAGE_TAG = "ael-sandbox:latest"

    def __init__(self):
        self.container_id: str | None = None

    def _dockerfile_path(self) -> Path:
        return Path(__file__).resolve().parent.parent / "docker" / "sandbox.Dockerfile"

    def _ensure_image(self) -> None:
        check = subprocess.run(
            ["docker", "image", "inspect", self.IMAGE_TAG], capture_output=True
        )
        if check.returncode != 0:
            dockerfile = self._dockerfile_path()
            subprocess.run(
                ["docker", "build", "-f", str(dockerfile), "-t", self.IMAGE_TAG, str(dockerfile.parent)],
                check=True,
            )

    def setup(self, repo_dir: Path) -> PurePosixPath:
        self._ensure_image()
        run = subprocess.run(
            [
                "docker", "run", "-d", "--rm",
                "--memory", "2g", "--cpus", "2",
                self.IMAGE_TAG, "tail", "-f", "/dev/null",
            ],
            capture_output=True, text=True, check=True,
        )
        self.container_id = run.stdout.strip()

        subprocess.run(["docker", "cp", f"{repo_dir}/.", f"{self.container_id}:/repo"], check=True)

        req_file = repo_dir / "requirements.txt"
        if req_file.exists():
            # Preinstalled deterministically before the agent ever runs --
            # the "default is deterministic, agent can also install more
            # at runtime via exec_command" split decided earlier.
            self.exec_command("pip install -q -r requirements.txt", timeout=120)

        return PurePosixPath("/repo")

    def exec_command(self, command: str, timeout: float = 0) -> ExecResult:
        if self.container_id is None:
            raise RuntimeError("setup() must be called before exec_command()")

        # Hard limit enforced INSIDE the container by coreutils `timeout`,
        # not by killing the host-side `docker exec` process. Killing the
        # host process only kills the CLI call watching the container --
        # it does not stop the command actually running inside it (two
        # separate process layers; confirmed the hard way with the
        # Windows taskkill bug on the non-Docker path).
        inner = f"bash -lc {shlex.quote(command)}"
        if timeout > 0:
            inner = f"timeout -k 2 {timeout}s {inner}"

        proc = subprocess.run(
            ["docker", "exec", "-w", "/repo", self.container_id, "bash", "-c", inner],
            capture_output=True, text=True,
        )
        # exit code 124 is `timeout`'s own signal that it killed the command.
        timed_out = timeout > 0 and proc.returncode == 124
        return ExecResult(
            stdout=proc.stdout, stderr=proc.stderr, returncode=proc.returncode, timed_out=timed_out
        )

    def run_tests(self, test_command: str) -> TestResult:
        result = self.exec_command(test_command)
        return TestResult(
            passed=(result.returncode == 0),
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )

    def teardown(self) -> None:
        if self.container_id is not None:
            subprocess.run(["docker", "rm", "-f", self.container_id], capture_output=True)
            self.container_id = None
