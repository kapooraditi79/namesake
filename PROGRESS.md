# AEL — Phase checklist

Don't start the next phase until the current one's exit criterion is
checkable-true. See project_context.md section 9 for full detail.

## Phase 0 — Foundations
- [ ] 3-5 small, permissively-licensed Python repos picked (pure-Python,
      no system deps preferred — see README for candidates)
- [ ] `docker/sandbox.Dockerfile` builds
- [ ] `sandbox/runner.py` implemented: checkout @ commit, apply patch, run
      test_cmd, report pass/fail
- [ ] 5 tasks curated in `tasks/` (see `tasks/README.md` checklist)
- [ ] Exit criterion: hand-written golden patch for all 5 tasks passes
      through the sandbox, repeatably, via `sandbox.runner.run_task_in_sandbox`

## Phase 1 — Minimum agent loop
- [ ] `agent/tools.py` tool schemas + execution implemented
- [ ] `agent/llm_client.py` implemented
- [ ] `agent/loop.py` implemented (bounded ReAct loop)
- [ ] Trajectory logging wired in from the start, not bolted on after
- [ ] Exit criterion: agent attempts all 5 Phase-0 tasks unattended,
      produces a trajectory log + pass/fail for each (1-2/5 passing is fine)

## Phase 2 — Expand suite + metrics
- [ ] Suite grown to 15-20 verified tasks
- [ ] `scoring/scorer.py` metrics extraction implemented
- [ ] `orchestrator/run_suite.py` + `cli.py` implemented
- [ ] Exit criterion: `ael run --suite core-20` completes unattended,
      reproducible results table

## Phase 3 — Multi-agent comparison
- [ ] `AgentConfig` supports named variants (prompt/model/retry strategy)
- [ ] Regression detection (task config B fails that A used to pass)
- [ ] Minimal trajectory viewer
- [ ] Exit criterion: "did config B regress?" answered automatically

## Phase 4 — Failure taxonomy
- [ ] 15-20 failed trajectories read manually, taxonomy derived from
      what was actually observed
- [ ] Every failed run tagged
- [ ] Exit criterion: can state which failure category dominates, with evidence

## Phase 5 — One real experiment (stretch)
- [ ] Hypothesis picked from Phase 4 findings
- [ ] Before/after run with suite+scoring held fixed
- [ ] Exit criterion: short write-up — hypothesis, method, result, implication
