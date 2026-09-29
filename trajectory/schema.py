"""One structured record per agent action or observation. Written as JSONL —
one line per step, so a trajectory can be tailed, diffed, or streamed without
re-running anything."""

from __future__ import annotations

import time
from typing import Any, Literal

from pydantic import BaseModel, Field


class TrajectoryStep(BaseModel):
    task_id: str
    run_id: str  # unique per (task, agent_config) attempt
    step_index: int
    kind: Literal["model_call", "tool_call", "tool_result", "final_status"]
    timestamp: float = Field(default_factory=time.time)

    # model_call
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    model_name: str | None = None

    # tool_call / tool_result
    tool_name: str | None = None
    tool_input: dict[str, Any] | None = None
    tool_output: str | None = None

    # free-form payload for anything else (raw model text, error messages)
    content: str | None = None
