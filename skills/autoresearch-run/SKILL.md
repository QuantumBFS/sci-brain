---
name: autoresearch-run
description: Use when running the autoresearch loop for a project whose survey and validator gates have passed — executes batches of attempts (one git worktree + LOG.md each, scored only by the validator under a hard time limit), then reflects, reports, and re-plans; continues autonomously while authorized_rounds remain, otherwise stops for user review. Stage 4 of the autoresearch pipeline.
---

# Autoresearch Run

The loop. Protocol per attempt: `references/attempt-protocol.md`. Report per
cycle: `references/reflection-template.md`. Configuration from
`research/STATE.md`: `batch_size` (default 10), `time_limit_seconds`,
`authorized_rounds`, `next_attempt`, `next_cycle`.

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
   `batch_size`), each drawing on `## Selected` entries in
   `research/INSIGHTS.md`, then rank them with a quick rubric (expected
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
2. **Execute** each attempt per `references/attempt-protocol.md`.
3. **Reflect.** Write `docs/discussion/YYYY-MM-DD-HHMMSS-cycle-NN.md` per
   `references/reflection-template.md`; increment `next_cycle`. Dev-score
   selection overfits over long runs: if the holdout query budget in the
   validator manifest allows, adjudicate the cycle's top candidate on the
   holdout (aggregate result only) and record it.
4. **Soft gate.** Decrement `authorized_rounds`:
   - if > 0 remain: continue to the next cycle autonomously;
   - if 0: stop, present the report and the proposed next-batch plan, and
     wait for the user to re-authorize (set a new `authorized_rounds`),
     amend the plan, or stop. Insight promotions proposed in the report are
     confirmed here.

## Termination

When the validator reports the GOAL.md bar met on dev instances, run
`validate --instances holdout` once, report both results, set
`stage: done`, and hand off to the user — write-up is out of scope for this
skill (use paper-writer).
