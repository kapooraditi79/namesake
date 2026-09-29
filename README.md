# Agent Evaluation Lab (AEL)

Infrastructure for answering one question reliably: *did this change to my
coding agent make it better, worse, or just different?*

The agent is a replaceable fixture. The evaluation/observability layer —
sandbox, trajectory logging, scoring, comparison reporting — is the actual
product. Full context, rationale, and phased roadmap: `project_context.md`.
Current phase checklist: `PROGRESS.md`.

## Layout

| Path | Role |
|---|---|
| `docker/sandbox.Dockerfile` | Base image every task container is built from |
| `sandbox/runner.py` | Runs one task attempt in a throwaway container, returns pass/fail |
| `tasks/` | Fixed, versioned task suite — one dir per task, `task.yaml` + optional golden patch |
| `agent/` | The agent loop, its tools, and the LLM client — deliberately the smallest/most replaceable part |
| `trajectory/` | Structured JSONL logging of every model call and tool call, per run |
| `scoring/` | Turns a run into pass/fail + metrics (iterations, tokens, cost, time) |
| `orchestrator/` | Runs a suite × one or more agent configs, writes results |
| `reporting/` | Reads results, prints/exports comparison tables |
| `cli.py` | `python cli.py run --suite core-20 --agent v1` |
| `results/` | Gitignored run outputs (trajectories + results tables) |

## Setup

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env` with `ANTHROPIC_API_KEY=...` (never commit this file).

## Start here

You're at Phase 0. Read `tasks/README.md` for the task curation checklist,
then implement `sandbox/runner.py`. Nothing else in this repo should be
touched until a hand-written patch passes through the sandbox for 5 tasks,
repeatably — see `PROGRESS.md` for the exact exit criterion.
