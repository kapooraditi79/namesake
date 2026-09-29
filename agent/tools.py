"""Tool definitions the agent loop exposes to the model, plus their execution
against a live sandbox container. Keep this list minimal for Phase 1 — a
ReAct loop with exactly these four tools is enough to attempt real tasks:

    read_file(path) -> file contents
    list_dir(path) -> directory listing
    edit_file(path, content) -> overwrite a file (start dumb: full-file
        replacement, not diff-based patching — diff application is an
        optimization, not a Phase 1 requirement)
    run_tests() -> stdout/stderr/exit code from task.test_cmd

TODO (Phase 1):
    - Define each tool's JSON schema for the Anthropic tool-use API.
    - Implement execution by exec-ing into the running sandbox container
      (`docker exec`), not by touching files on the host.
    - Every call here MUST also go through trajectory.logger — a tool call
      that isn't logged didn't happen, as far as this project is concerned.
"""

from __future__ import annotations

TOOL_DEFINITIONS = [
    # TODO: fill in Anthropic tool-use schema dicts for read_file, list_dir,
    # edit_file, run_tests.
]


def execute_tool(container_id: str, tool_name: str, tool_input: dict) -> str:
    """Dispatch a single tool call against the running sandbox container.
    Returns the string observation to feed back to the model."""
    raise NotImplementedError
