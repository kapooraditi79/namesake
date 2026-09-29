"""The agent loop itself — deliberately the smallest, most replaceable file
in this project (see project_context.md section 8). If you find yourself
spending more time tuning this file than the sandbox/scoring/trajectory
infra, that's the scope-drift warning sign called out in the project doc.

Loop shape (Phase 1, ReAct-style, bounded iterations):

    1. Seed messages with system prompt + task.issue_text.
    2. Loop up to `max_iterations` times:
        a. call_model() with the current message history + TOOL_DEFINITIONS
        b. log a "model_call" trajectory step
        c. for each tool_use block in the response:
             - execute_tool() against the sandbox container
             - log "tool_call" then "tool_result" trajectory steps
             - append the tool result to message history
        d. if the model calls run_tests and it passes, or the model
           declares done, break
    3. Log a final "final_status" step with the terminal state.
    4. Return the run's outcome for scoring.scorer to grade.

Guardrails to keep from day one, not add later:
    - Hard cap on iterations (e.g. 15) — an ungoverned loop is a cost risk
      and a broken measurement (you can't compare "steps to resolution"
      across runs if one run can loop forever).
    - Every single step gets logged, unconditionally — this is not
      optional instrumentation, it's the trajectory log's entire job.
"""

from __future__ import annotations

from dataclasses import dataclass

from tasks.schema import TaskSpec


@dataclass
class AgentConfig:
    name: str  # e.g. "v1-baseline"
    model: str
    system_prompt_path: str
    max_iterations: int = 15


@dataclass
class RunOutcome:
    run_id: str
    task_id: str
    agent_config_name: str
    final_patch: str | None
    iterations_used: int
    terminated_reason: str  # "declared_done" | "max_iterations" | "error"


def run_agent_on_task(task: TaskSpec, config: AgentConfig, container_id: str) -> RunOutcome:
    raise NotImplementedError
