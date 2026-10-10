from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from agents.known_fixes import KNOWN_FIXES
from agents.llm_backed_agent import LLMBackedAgent
from harness.logger import TrajectoryLogger
from harness.sandbox import LocalCopySandbox


class llmAgent(LLMBackedAgent):
    def __init__(self, model: str = "qwen2.5-coder:7b"):
        super().__init__(model=model)
        self.messages: list[dict] = []

    def act(self, repo_path: Path, task: dict[str, Any], logger: TrajectoryLogger) -> int:
        self.start_time = time.time()
        raise NotImplementedError  # the actual loop -- still yours to build
