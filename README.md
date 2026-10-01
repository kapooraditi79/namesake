# Agent Evaluation Lab (AEL)

See [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md) for the full business context, scope, and phased roadmap.
See [OFFLINE_TASKS.md](OFFLINE_TASKS.md) for a checklist of work that needs no internet connection.

## Quickstart (fully offline, no Docker, no API keys)

```bash
pip install -r requirements.txt
python -m harness.cli run --task tasks/toy_001 --agent fake
```

This runs the entire Phase-0 loop against a synthetic, intentionally-buggy toy
repo: copy repo to a sandbox -> run tests (fail) -> let an agent try to fix it
-> run tests again -> score -> write a trajectory log.

`--agent fake` uses a hardcoded patch so the loop is provable without calling
any LLM. This is the thing to get green before you ever touch a real repo or
a real agent.
