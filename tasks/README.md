# Task suite

Each task is a directory: `tasks/<task_id>/task.yaml` (+ optional `golden_patch.diff`).

## Curation checklist (Phase 0 — do this for 5 tasks before writing any agent code)

1. Pick a closed GitHub issue on one of your target repos.
2. Find the PR that fixed it. Confirm it touches 1-2 files — bigger diffs make
   weak tasks (ambiguous scoring, agent can "accidentally" pass).
3. Confirm the PR added or modified a test that fails before the fix and
   passes after. This test is your oracle — without it you can't score
   objectively.
4. Set `base_commit` to the PR's parent commit (bug present, test not yet added
   — or present and failing).
5. Copy the merged fix into `golden_patch.diff` as a sanity oracle: applying it
   inside the sandbox and running `test_cmd` MUST pass. If it doesn't, the task
   is broken — fix or drop it before it ever reaches the agent.
6. Write `issue_text` in your own words from the original issue — plain
   problem description, no hints about the fix.

## task.yaml format

```yaml
task_id: tinydb-issue-042
repo_url: https://github.com/msiemens/tinydb
base_commit: <sha>
issue_text: |
  Querying with `where('field').one_of([...])` raises a TypeError when
  the field value is a list instead of a scalar.
test_cmd: pytest tests/test_queries.py -x
install_cmd: pip install -e .
golden_patch_path: golden_patch.diff
```
