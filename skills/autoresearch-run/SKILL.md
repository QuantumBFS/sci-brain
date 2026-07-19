---
name: autoresearch-run
description: Use when running the autoresearch loop for a project whose survey and validator gates have passed — executes batches of attempts (one git worktree + LOG.md each, scored only by the validator under a hard time limit), then reflects, reports, and re-plans; continues autonomously while authorized_rounds remain, otherwise stops for user review. Stage 5 of the autoresearch pipeline.
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

1. **Plan the batch.** Propose `batch_size` attempts, each a distinct
   falsifiable hypothesis drawing on `## Selected` entries in
   `research/INSIGHTS.md` (name the insight in the attempt's LOG.md). Vary
   the angle across the batch — a batch of near-duplicates wastes the cycle.
2. **Execute** each attempt per `references/attempt-protocol.md`.
3. **Reflect.** Write `docs/discussion/YYYY-MM-DD-HHMMSS-cycle-NN.md` per
   `references/reflection-template.md`; increment `next_cycle`.
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
