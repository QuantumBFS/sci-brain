---
name: autoresearch-run
description: Use when running the autoresearch loop for a project whose survey and validator gates have passed — executes batches of attempts (one git worktree + LOG.md each, scored only by the validator under a hard time limit), then reflects, reports, and re-plans; continues autonomously while authorized_attempts remain, otherwise stops for user review. Stage 4 of the autoresearch pipeline.
---

# Autoresearch Run

The loop. Protocol per attempt: `references/attempt-protocol.md`. Report per
cycle: `references/reflection-template.md`. Configuration from
`research/STATE.md`: `batch_size` (default 10), `time_limit_seconds`,
`authorized_attempts`, `next_attempt`, `next_cycle`.

## Entry check — refuse to start otherwise

Both `survey_gate` and `validator_gate` must read `passed` in
`research/STATE.md`, and their artifacts must verify on disk (CATALOG.md,
INSIGHTS.md `## Selected`, validator manifest with self-test results). If
not, refuse and route back through the `autoresearch` dispatcher. A missing
gate is never worked around; a user-approved exception goes into
`overrides:` in STATE.md first.

## Hard rules (non-negotiable during the loop)

1. Every attempt in its own `.worktrees/attempt-NNN/` with a `LOG.md`.
2. Every scored run goes through the validator CLI; nothing else counts.
3. Hard wall-clock limit `time_limit_seconds` on every scored run.
4. Holdout labels never enter design context — only aggregate validator
   output.
5. Crashes/timeouts are recorded failures, never silently retried.

## Cycle

1. **Plan the batch.** Generate a surplus of candidate hypotheses (~2×
   `batch_size`). `## Selected` entries in `research/INSIGHTS.md` are the
   default grounding, not a fence — original ideas, cross-insight
   combinations, and directions from fresh literature search are equally
   welcome; each hypothesis names its source (insight / literature /
   original) in the plan. Rank them with a quick rubric (expected
   information gain, cost, distinctness) and promote the top `batch_size`.
   Two filters before anything is implemented:
   - **Novelty check** — compare each candidate against the hypotheses in
     *all* prior attempts' LOG.md files; a near-duplicate of anything
     already tried is rejected and resampled. Never re-spend an attempt on
     a restated old idea.
   - **Batch composition** — mix *drafts* (genuinely different approaches)
     with *improvements* (exactly one atomic change to the best-scoring
     known-good ancestor, so the change's effect is measurable) and at most
     2 *debug* attempts on a promising-but-broken branch. A failing branch
     that exhausts its debug cap is abandoned, not nursed.
   Scope the planning context: drafts see a digest of *sibling* attempts
   (what was tried, what it scored — do something different); improvements
   and debugs see their *ancestral* chain (avoid undo-redo loops). Feed
   forward the failure artifacts (validator `errors[]`, stderr) of the
   previous batch — failures are data.
2. **Confirm the plan.** The first batch of any authorization — cycle 1
   especially — executes only after the user confirms the plan: present
   the promoted hypotheses (one line each, with source) and the batch
   composition, apply any amendments, then start. Later cycles within the
   same authorization run autonomously — their direction was confirmed at
   the previous soft gate alongside the attempts budget.
3. **Execute** each attempt per `references/attempt-protocol.md`.
4. **Reflect.** Write `docs/discussion/YYYY-MM-DD-HHMMSS-cycle-NN.md` per
   `references/reflection-template.md`, then emit `cycle-NN.json`
   (`references/report-schema.md`) and render the HTML report with
   `helpers/report.py` (non-fatal on failure — the md is canonical);
   increment `next_cycle`. Dev-score
   selection overfits over long runs: if the holdout query budget in the
   validator manifest allows, adjudicate the cycle's top candidate on the
   holdout (aggregate result only) and record it.
5. **Sync.** Commit the cycle's artifacts to the main branch — the
   reflection md/json/html and `index.html`, STATE.md, any INSIGHTS.md
   changes, and the validator manifest (holdout query log) — then, when a
   remote is configured, push main plus every `attempt-NNN` branch from
   this cycle (each carries its generated code, `LOG.md`, and
   `report.json`, committed per the attempt protocol). This preserves the
   AI-generated code and results off-machine after every cycle. Never
   push `research/benchmark/private/` — it stays gitignored, and holdout
   results appear only as aggregates in the reports. No remote → recommend
   the user add one, record the skip in the reflection, continue.
6. **Soft gate.** Subtract the cycle's attempts from `authorized_attempts`:
   - if enough remain for another batch, continue autonomously (a remainder
     smaller than `batch_size` runs as a smaller final batch);
   - if exhausted: stop and present the report — summarize in the
     terminal and point the user at `docs/discussion/cycle-NN.html` and
     `index.html` — followed by **2–4 candidate directions** for the next
     batch, grounded in the cycle's lessons: e.g. deepen the winning
     branch, attack the diagnosed root-cause bottleneck, open an untried
     direction, or wind down. One line each: what it is, which lesson or
     root cause motivates it, and what it would settle. The user decides
     both **which direction(s)** to pursue and **how many attempts** to
     authorize (a number; 0 = stop; the user's own directions and
     amendments welcome as free text). Attempts are the unit the user
     authorizes; never ask them to reason in rounds or cycles — those are
     internal bookkeeping. Insight promotions proposed in the report are
     confirmed here.

## Termination

When the validator reports the GOAL.md bar met on dev instances, run
`validate --instances holdout` once, report both results, set
`stage: done`, and hand off to the user — write-up is out of scope for this
skill (use paper-writer).
