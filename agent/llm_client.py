"""Thin wrapper around the Anthropic API for the agent loop.

Deliberately not a framework — Phase 1's whole point is seeing the raw
request/response/tool-use cycle, not hiding it behind an abstraction. Add
retries/backoff for rate limits, but resist adding anything else here.

TODO (Phase 1):
    - call_model(messages, tools, system_prompt) -> the API response,
      including any tool_use blocks.
    - Track prompt_tokens/completion_tokens from the response so
      trajectory.schema.TrajectoryStep.model_call entries can be populated —
      this is what Phase 2's cost-per-task metric is built from.
    - Model id: use a current Claude model (see the `claude-api` skill for
      current ids/pricing before hardcoding one).
"""

from __future__ import annotations

import os

import anthropic


def get_client() -> anthropic.Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set (put it in .env)")
    return anthropic.Anthropic(api_key=api_key)


def call_model(client: anthropic.Anthropic, *, model: str, system: str, messages: list, tools: list):
    raise NotImplementedError
