# Offline Task List (flight-friendly)

Everything below needs only Python + a text editor. No internet, no Docker,
no API keys. Verify each one by rerunning:

```bash
python -m harness.cli run --task tasks/<id> --agent fake
```

## 1. Add a second toy task (different bug shape)
Create `tasks/toy_002/` the same way `toy_001` is structured:
- `task.json`
- `repo/<package>/...` with a deliberate bug
- `repo/tests/...` with a test that currently fails
- Register the fix in `agents/fake_agent.py`'s `KNOWN_FIXES`

Make the bug *categorically different* from toy_001 — e.g. an off-by-one in
a loop, a wrong default argument, a missing edge-case branch (empty list,
zero, negative number). The goal is to stress the harness with variety, not
to make a hard bug.

## 2. Add a third toy task the fake agent CANNOT fix
Create `tasks/toy_003/` but do NOT add an entry to `KNOWN_FIXES`. Run it and
confirm you get a clean "NOT RESOLVED" with a correct trajectory log — this
proves your harness handles failure as cleanly as success. This matters more
than it sounds: a harness that only looks right on the happy path is not
trustworthy later.

## 3. Add a "dumb_agent" that intentionally does nothing
`agents/dumb_agent.py` — an `Agent` subclass whose `act()` logs a step and
returns without touching any files. Register it in `harness/cli.py`'s
`AGENTS` dict. Run it against all three toy tasks. You now have your first
real baseline-vs-agent comparison, even with zero intelligence involved.

## 4. Write unit tests for the harness itself
`tests/test_sandbox.py`, `tests/test_scorer.py`, `tests/test_logger.py`
(top-level `tests/`, separate from the toy repos' own tests). Use `tmp_path`
pytest fixtures to avoid touching real files. This is the part most people
skip and regret later when the harness itself has a silent bug.

Things worth asserting:
- `LocalCopySandbox.setup()` doesn't mutate the original task repo (copy, not move)
- `LocalCopySandbox.teardown()` actually removes the temp dir
- `score_run()` returns `resolved=False` when tests failed both before and after
- `score_run()` returns `resolved=False` when tests passed before AND after (not a real fix, nothing to resolve)
- `TrajectoryLogger.flush()` produces valid JSON on every line

## 5. Draft the failure taxonomy (pen-and-paper is fine)
You won't have real failure data until Phase 1/2, but draft your working
hypotheses now so you can compare against reality later. Write 4-6 categories
you'd *expect* to see (e.g. "misread the issue," "fixed wrong file," "broke
an unrelated test," "gave up without re-running tests"). Put it in
`docs/failure_taxonomy_draft.md`. Expect it to be wrong — that's fine, that's
the point of writing it down before you have data.

## 6. Write the `LLMAgent` class *interface* (no API calls)
In `agents/llm_agent.py`, stub out the class structure for the real agent
you'll build in Phase 1: what tools will it expose (read_file, edit_file,
list_dir, run_tests)? What does its `act()` loop look like structurally
(plan -> pick tool -> execute -> observe -> repeat -> stop condition)? Write
it with `raise NotImplementedError` bodies. This is pure design work — you
are deciding the shape of the loop before you wire up any API key, which
means you'll write a cleaner loop than if you start by fighting the API.

## 7. Review PROJECT_CONTEXT.md and mark anything that already feels wrong
Now that you have working code, some assumptions in the doc may already look
off (e.g. maybe 15-20 tasks is too many/too few, maybe a metric is missing).
Note disagreements in `docs/context_revisions.md` rather than editing the
doc live — we'll reconcile when you're back online.

## Before you lose signal, run once more to confirm a clean baseline:
```bash
git init
git add .
git commit -m "Phase 0 skeleton: local sandbox, logger, scorer, fake agent, toy_001"
```
This gives you a known-good commit to diff against for everything you build
on the flight.
