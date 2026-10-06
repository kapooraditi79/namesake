# Agent Evaluation Lab (AEL)
### Project Context, Scope & Phased Roadmap

---

## 0. TL;DR Verdict

**Worth building, with guardrails.** This is not a startup and has no business model — treat that framing as a forcing function for rigor, not literal truth. The real, industry-mirrored problem is: *there is no cheap, reliable way to know whether a change to a coding agent made it better or worse.* That's a genuine open problem (every serious agent team — Cognition, Anthropic, OpenHands, SWE-agent — maintains internal infrastructure for exactly this).

The failure mode to actively avoid: **this becomes "an agent that calls an LLM API and edits files," which is a thin wrapper and teaches almost nothing.** The fix is architectural, not aspirational — it's baked into the phases below: the agent is a *replaceable fixture*, the evaluation/observability layer is the *actual product*. If a phase's effort is going into making the agent smarter rather than making the measurement of the agent better, that phase has drifted off course.

---

## 1. Business Problem

Frame this as if you were an internal platform engineer at a company shipping a coding agent (Cursor, Devin, Copilot Workspace, an internal SWE-agent) to customers or other engineers.

**The problem:** Every time someone changes the agent — a new prompt, a new tool, a new model, a new retry strategy — the team has no fast, trustworthy way to answer:
- Did this change make the agent *better* at resolving real issues?
- Did it make the agent *more efficient* (fewer steps, less cost, less time)?
- Did it introduce new *failure modes* that weren't there before?
- Is a regression in one task type masked by an improvement in another?

Without this, teams either (a) ship on vibes — "it felt better in my five manual tests" — or (b) run ad hoc one-off tests that aren't reproducible or comparable across changes. Both are how agent regressions ship silently and how teams burn weeks debating whether "v2 is actually better than v1" with no data to settle it.

This is not a hypothetical pain. It is *the* bottleneck that determines whether an agent team can iterate quickly and trust its own progress. SWE-bench exists because this problem is real; internal eval harnesses at every serious AI lab exist for the same reason.

---

## 2. Who Has This Pain (Personas)

| Persona | Pain | What they need |
|---|---|---|
| **Agent developer** (building/tuning the coding agent) | Can't tell if a prompt/tool change is a net improvement | Fast, repeatable scorecard across many tasks, not five manual spot-checks |
| **Eng lead / reviewer** | Has to trust a teammate's claim that "the new version is better" with no evidence | An objective comparison report: pass rate, cost, step count, regressions by category |
| **Researcher** (you, later phases) | Wants to test a specific hypothesis (e.g. "does reflection improve recovery after failure?") | Controlled A/B harness holding the task set and scoring fixed while varying one agent variable |

For this project, you are simultaneously the agent developer and the researcher — but designing for these personas (even as an audience of one) is what keeps the scope honest and prevents "cool demo, no rigor."

---

## 3. Pain Points Today (What's Actually Broken, Concretely)

1. **No ground truth at scale.** Anecdotal testing ("I tried it on 3 issues and it seemed fine") doesn't catch regressions that show up on the 4th–50th issue.
2. **No trajectory visibility.** When an agent fails, "it didn't work" tells you nothing. You need to see *what it tried, in what order, and where it diverged from a sane approach.*
3. **No cost/efficiency accounting.** An agent that succeeds by brute-forcing 40 tool calls and $2 of tokens is not the same quality as one that succeeds in 8 calls — but "did it pass" alone can't tell them apart.
4. **No failure taxonomy.** "It failed" is not actionable. *Why* it failed (misread the repo, wrong tool, misinterpreted test output, gave up early) determines what you'd actually fix.
5. **No standardized comparison.** Without a fixed task set and fixed scoring, "agent v2 is better than v1" is an opinion, not a finding.

Every phase below exists to eliminate one of these five gaps. If a feature doesn't map to one of these five, it's scope creep — cut it.

---

## 4. Use Case Narrative (What This Looks Like Working)

> You've just changed your agent's planning prompt to make it re-read failing test output before retrying, instead of blindly re-attempting the same edit. You want to know: did this actually help, or does it just feel like it should?
>
> You run `ael run --agent v2 --suite core-20` against your fixed 20-task suite. Fifteen minutes later, you have a report: v2 passes 13/20 vs. v1's 11/20, uses 18% fewer tool calls on average, but has 2 new timeout failures it didn't have before. You open the trajectory viewer for one of those new failures and see the agent looping — re-reading the same test output three times without changing its edit. You now have a concrete, evidenced next hypothesis instead of a guess.

That loop — **change something → get an evidenced verdict → see exactly why it failed → form the next hypothesis** — is the entire product. Nothing else matters if that loop isn't fast and trustworthy.

---

## 5. What This Project Is Explicitly NOT

Stated up front because scope drift is the single biggest risk here:

- **Not a general computer-use agent.** No browser automation, no GUI control, no visual grounding. Terminal + filesystem + code only. Browser tasks are flaky for reasons unrelated to agent quality (DOM timing, selector rot) and would contaminate your measurements with noise you can't attribute.
- **Not a model-training project.** No fine-tuning, no custom model architecture. You are evaluating and orchestrating existing LLMs via API, not building them. (That's the "tiny LLM from scratch" or "multimodal system" project — a different skill target, don't merge them.)
- **Not a SaaS product.** No auth, no multi-tenant anything, no billing. Single-user, local/self-hosted tooling.
- **Not trying to beat SOTA.** You are not competing with Devin or Cursor on raw resolve-rate. Your agent's absolute performance is uninteresting; the *measurement infrastructure* is the point.
- **Not doing LLM-as-judge for everything.** Deterministic, test-verifiable tasks are the default. LLM-judge is a last resort for the handful of things that genuinely can't be scored by a test oracle (e.g., code style), added late, and validated against human-labeled examples before you trust it.

---

## 6. Success Criteria (What "Good" Looks Like)

You'll know this project succeeded if, by the end, you can:

1. Point at a fixed suite of ≥20 verifiable coding tasks and get a reproducible pass/fail score for any agent configuration in one command.
2. Open any failed run and see, without re-running anything, exactly what the agent tried and where it went wrong.
3. Produce a side-by-side comparison table (pass rate, steps, tokens, cost, latency) for 2+ agent variants on the same suite.
4. Categorize failures into at least 4 distinct, non-overlapping failure types with real examples of each — not hypothetical categories, ones you actually observed.
5. Answer one real experimental question with evidence (e.g., "does giving the agent a reflection step before retry improve its recovery rate after test failures?") — not a demo, an actual before/after number with a defensible methodology.

If you hit #1–#4 and stop, you still have a strong portfolio piece. #5 is the "research-worthy" stretch goal — good to have, not required for v1.

---

## 7. Feature Shelf

Organized Now / Next / Later. **"Now" is the only thing that matters until it's solid.**

### Now (v1 — must exist for the project to be real)
- [ ] Fixed task suite: 15–20 tasks, each = (repo snapshot, issue description, test command, pass/fail oracle)
- [ ] Sandboxed execution environment (Docker) — isolated, resettable, reproducible
- [ ] One working agent loop: plan → search → edit → run tests → observe → retry (bounded iterations)
- [ ] Trajectory logger: every tool call, every observation, every model response, timestamped
- [ ] Binary scorer: did the test suite pass at the end — yes/no, no ambiguity
- [ ] Basic metrics per run: pass/fail, iteration count, wall-clock time, token count, estimated cost
- [ ] CLI to run the full suite against one agent config and dump a results table

### Next (v1.5 — makes it a *lab*, not a single script)
- [ ] Multi-agent comparison: run 2+ agent configs (different prompts, different models, different retry strategies) against the same suite in one command
- [ ] Trajectory viewer (even a simple local HTML/terminal viewer) to inspect a run step-by-step
- [ ] Structured failure tagging: manually categorize a batch of failed runs into a taxonomy (bad planning / wrong tool / misread test output / premature stop / other)
- [ ] Regression detection: flag when a new agent variant fails a task the baseline used to pass

### Later (v2 — the research layer)
- [ ] Semi-automated failure classification (rule-based first, LLM-judge only after manual calibration)
- [ ] Reflection/self-critique step added as an experimental agent variant
- [ ] A/B experiment runner with statistical summary (not just raw numbers — confidence given small N)
- [ ] Dashboard (simple web UI) aggregating results across many historical runs over time
- [ ] Cost/latency optimization experiments (e.g., cheaper model for search vs. expensive model for edit)

### Explicitly out of scope (don't build, don't half-build)
- Browser/GUI agents, visual grounding
- Any model fine-tuning or training
- Multi-tenant/auth/deployment-as-a-service
- Full SWE-bench-scale suites (hundreds of tasks) — 20 well-understood tasks beat 200 you've never read

---

## 8. Architecture Overview

```
                     TASK SUITE (fixed, versioned)
                     [repo snapshot + issue + test oracle] × N
                              │
                              ▼
                     ┌─────────────────┐
                     │  ORCHESTRATOR   │  ← runs suite × agent config
                     └────────┬────────┘
                              │
                              ▼
                     ┌─────────────────┐
                     │  SANDBOX (Docker)│  ← one container per task run
                     └────────┬────────┘
                              │
                    ┌─────────────────────┐
                    │      AGENT LOOP      │
                    │ plan→search→edit→test│
                    │   observe → retry    │
                    └────────┬────────────┘
                              │
                     ┌────────▼────────┐
                     │ TRAJECTORY LOG   │  ← every action, observation, token
                     └────────┬────────┘
                              │
                     ┌────────▼────────┐
                     │  SCORING ENGINE  │  ← pass/fail + metrics
                     └────────┬────────┘
                              │
                     ┌────────▼────────┐
                     │  COMPARISON /    │  ← v1 vs v2 vs baseline
                     │  REPORT LAYER    │
                     └─────────────────┘
```

The agent loop box is intentionally the smallest, most replaceable box in this diagram. Everything else is where the engineering effort should concentrate.

---

## 9. Phased Roadmap

Each phase has a stated goal, concrete deliverables, and an **exit criterion** — a specific, checkable condition that must be true before moving on. Do not start the next phase until the current one's exit criterion is met; that discipline is what prevents this from sprawling into an unfinished mess.

### Phase 0 — Foundations (target: ~1 week)
**Goal:** Get the boring infrastructure working before writing any agent logic.
- Pick 3–5 small, real, permissively-licensed Python repos with existing test suites.
- Write a Docker sandbox that can: check out a repo at a given commit, apply a patch, run its test command, and report pass/fail cleanly.
- Manually curate 5 tasks (not 20 yet) — real GitHub issues on those repos where you've confirmed there's a clean before/after test state.
- **Exit criterion:** you can run `docker run ... test` against a hand-written patch for all 5 tasks and get a correct, repeatable pass/fail.

### Phase 1 — Minimum Agent Loop (target: ~1–2 weeks) → **this is v1's core**
**Goal:** A dumb-but-complete agent that can attempt a task end-to-end.
- Implement plan → search-codebase → edit-file → run-tests → observe → bounded retry.
- No cleverness required — a basic ReAct-style loop calling an LLM with tool definitions (read file, edit file, run tests, list directory) is enough.
- Wire in the trajectory logger from the start (not bolted on later — every action/observation logged as structured data, not just printed to stdout).
- **Exit criterion:** the agent attempts all 5 Phase-0 tasks unattended and produces a trajectory log + pass/fail for each, even if it only solves 1–2 of them. Solving all 5 is not the bar — *running cleanly end-to-end and logging faithfully* is the bar.

### Phase 2 — Expand the Suite + Basic Metrics (target: ~1 week)
**Goal:** Go from "a script that ran 5 tasks once" to "a suite you can rerun."
- Grow the task set to 15–20 verified tasks.
- Add metrics extraction from trajectory logs: iteration count, wall-clock time, token count, cost estimate.
- Build the CLI that runs the whole suite against one agent config and outputs a results table.
- **Exit criterion:** `ael run --suite core-20` completes unattended and produces a results table with per-task pass/fail + metrics, reproducible on a second run (same task → same or explainably-varying outcome).

### Phase 3 — Multi-Agent Comparison (target: ~1–2 weeks)
**Goal:** Turn the single-agent runner into an actual *lab*.
- Parametrize the agent config (prompt variant, model choice, retry strategy) so you can define 2+ named configs.
- Run the same suite across multiple configs and produce a comparison report (pass rate, cost, steps, regressions).
- Build a minimal trajectory viewer (even a plain-text or simple local HTML page) to inspect any run step-by-step without re-running it.
- **Exit criterion:** you can answer "did config B regress on any task config A used to pass?" with an automatically generated answer, not by manually diffing logs.

### Phase 4 — Failure Taxonomy (target: ~1–2 weeks)
**Goal:** Move from "it failed" to "it failed *because*."
- Manually read through 15–20 failed trajectories and derive a real taxonomy from what you actually observed (expect this to look different from any taxonomy you'd guess up front).
- Tag every failed run in your results with a category.
- Report failure breakdown by category, not just aggregate pass rate.
- **Exit criterion:** you can state, with evidence, which failure category is most common and why — e.g. "60% of failures are premature termination: the agent declares success without re-running tests."

### Phase 5 — One Real Experiment (target: ~1–2 weeks, stretch goal)
**Goal:** Answer a genuine research question with your own infrastructure.
- Pick one variable informed by Phase 4's findings (e.g., if premature termination is the top failure, test: does forcing a mandatory test-rerun before declaring done reduce it?).
- Hold the task suite and scoring fixed, vary only that one thing, run both configs, report the before/after with the same rigor as Phase 3's comparisons.
- **Exit criterion:** a short write-up — hypothesis, method, result, and whether the result changes how you'd build the agent next.

---

## 10. V1 Definition (Explicit)

**V1 = Phases 0–2, complete.** Concretely, v1 is done when:
- A fixed suite of 15–20 verifiable tasks exists and is checked into version control.
- One agent config can run the full suite unattended in a Docker sandbox.
- Every run produces a structured trajectory log and a results table (pass/fail, steps, time, tokens, cost).
- Results are reproducible — rerunning the suite doesn't require re-reading code to understand what happened.

**Not required for v1:** multi-agent comparison, failure taxonomy, dashboard, any research question. Those are what make it impressive later — v1's job is to prove the measurement loop works at all, end to end, without cutting corners on logging or scoring rigor. A v1 that fudges the scoring or skips the trajectory log is worse than no v1, because everything downstream depends on trusting these numbers.

---

## 11. Suggested Tech Stack (lightweight, not prescriptive)

- **Language:** Python (ecosystem fit for both agent code and target repos)
- **Sandbox:** Docker, one throwaway container per task run
- **Agent/LLM calls:** Claude API or OpenAI API directly — no heavyweight agent framework in Phase 1 (frameworks hide the loop you're trying to learn; add one later only if it's saving real time)
- **Logging:** structured JSON lines per trajectory step — easy to query, easy to diff between runs
- **Task suite storage:** plain directory per task (repo snapshot reference, issue text, test command, expected pass state) — no database needed until Phase 4+
- **Reporting:** a script that reads JSON logs and prints/exports a table (CSV or a simple local HTML) — no need for a real dashboard until Phase 5+

---

## 12. Risks & Kill Criteria

| Risk | Mitigation |
|---|---|
| Task curation eats all your time (finding "clean" issues with reliable test oracles is harder than it sounds) | Cap Phase 0 at 5 tasks. If even 5 is taking >1 week, your repo choice is wrong — pick simpler, smaller repos. |
| Agent-tuning rabbit hole (endless prompt fiddling to make it "smarter") | Timebox Phase 1. A mediocre agent that produces honest, complete trajectory logs is more valuable right now than a clever one that's a black box. |
| Docker/sandboxing becomes the whole project | Timebox Phase 0 to ~1 week. If you're still fighting environment setup after that, simplify (fewer repos, pin exact dependency versions, accept less generality). |
| Scope creep toward browser/GUI/multimodal | Re-read Section 5 whenever tempted. Those are different projects with different goals — not phases of this one. |
| No stopping point — this could run forever | V1 (Phases 0–2) is a complete, showable deliverable on its own. Treat Phases 3–5 as optional extensions you stop at whichever point your interest or time runs out — each phase-end is a legitimate finish line, not just Phase 5. |

**Kill/pivot signal:** if by the end of Phase 1 you find yourself unable to get *any* task passing even with a hand-written correct patch fed through your sandbox, the infrastructure (not the agent) is broken — stop and fix Phase 0 before writing more agent code.

---

## 13a. Design Patterns Adopted From Prior Art (apply at Phase 1, not retrofitted into Phase 0)

Source review of `SWE-bench/mini-swe-agent` (the team's own recommended successor
to the original SWE-agent — ~190 lines, >74% on SWE-bench Verified) and
`SWE-bench/SWE-bench` surfaced five concrete decisions to carry into the real
`LLMAgent` build in Phase 1. These are **not** retrofitted into the current
toy/`FakeAgent` code — `FakeAgent` has no loop, no cost, no multiple actions,
so this scaffolding would be dead weight with nothing exercising it. Apply
these when Phase 1 actually starts:

1. **Three strictly separate components: Model, Environment, Agent.** The
   agent never calls an LLM API or runs a command directly — only
   `model.query()` and `env.execute()`. `harness/sandbox.py` already plays
   the Environment role. Add a `Model` abstraction (thin wrapper: call LLM,
   track cost/tokens, return a structured message) so swapping a local
   open-weight model for an API model is a one-line change, not a rewrite.

2. **One `execute_bash` action, not five bespoke tools.** Neither SWE-agent
   nor mini-swe-agent gives the model separate `read_file`/`edit_file`/
   `list_dir` tool definitions — they give it one action (run a shell
   command) and let the model compose `cat`/`grep`/`sed`/`python -c` itself.
   Simpler to implement, and it's what actually reaches SOTA. Shrink the
   planned `LLMAgent` tool surface to this.

3. **Every run ends through one uniform `exit_status`.** Limits exceeded,
   repeated unparseable model output, an uncaught exception, or the model's
   own "submit" — all funnel into the same structured exit record
   (`exit_status`, `submission`). This *is* the failure taxonomy, captured
   by construction instead of reconstructed later from logs. Extend
   `harness/scorer.py`'s `RunScore` with an `exit_status` field once there
   are real exit paths to distinguish (there's only one today: test
   pass/fail).

4. **Hard limits are config, not afterthoughts**: `step_limit`, `cost_limit`,
   `wall_time_limit_seconds`, `max_consecutive_format_errors`, checked before
   every model call. Add to `AgentConfig` once `LLMAgent` has an actual loop
   to bound.

5. **Trajectory flushes after every step**, not once at the end — so a
   killed or crashed run still leaves an inspectable partial log. Change
   `TrajectoryLogger` to flush incrementally once runs are long enough to
   crash mid-way (not needed for the single-shot `FakeAgent`).

## 13b. Future Scope (next project, not this one)

Once this project's learning goals (Phases 0-5) are met, the natural next
iteration is **Agent Evaluation Lab v2**: drop the hand-curated real-repo
task suite and hand-rolled Docker sandboxing, and rebuild the task/sandbox
layer on top of **SWE-bench-lite** instead (curated issues, verified test
oracles, proven Docker harness — see swebench.com). Redirect all the effort
currently spent on task curation and sandbox plumbing toward the
genuinely-less-commoditized layer: multi-agent comparison, failure taxonomy
depth, and the adaptive-recovery research question (Phase 5). This project's
own Docker/task-curation work is still worth doing once, by hand, for the
engineering understanding it forces — it just shouldn't be redone at
real-repo scale a second time.

## 13c. Attribution

Design ideas in 13a are drawn from publicly available documentation and
source of `SWE-bench/SWE-bench` and `SWE-bench/mini-swe-agent` (MIT
licensed, Princeton/Stanford). No code was copied — these are architectural
patterns, reimplemented independently.

---

## 14. Metrics That Matter (Don't Drown in Vanity Metrics)

Track these, ignore the temptation to add more before you need them:

- **Pass rate** (the only metric that answers "did it work")
- **Steps to resolution** (efficiency proxy)
- **Token cost per task** (efficiency proxy, and the one that scales to "is this economically sane")
- **Regression count** (tasks a new config fails that an old config passed — this is the one that actually matters for trust)
- **Failure category distribution** (only from Phase 4 onward, and only once you have real failures to categorize)

Everything else (latency percentiles, fine-grained tool-call breakdowns, etc.) is a Phase 5+ nice-to-have, not a v1 requirement.
