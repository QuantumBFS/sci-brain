> **Superseded layout (2026-08-22):** the four stage skills described here were merged into a single `skills/autoresearch/` skill with stage files under `references/stages/`, and the run stage gained an anti-triviality filter and stuck-triggered insight refresh. See `docs/superpowers/specs/2026-08-22-autoresearch-consolidation-design.md`.

# Autoresearch skill family — design

**Date:** 2026-07-19
**Status:** Approved design, pre-implementation
**Home:** sci-brain plugin (`sci-brainstorm` repo), `skills/`
**Reference run:** `~/agentic/code-distance` — a completed manual execution of this
pipeline (survey gate → sealed benchmark → validator → 100+ attempt worktrees →
reflection logs in `docs/discussion/`).

## Goal

Package the autoresearch workflow — domain → topics with metrics → evidence
base → strict validator → iterative attempt/reflect loop — as a family of reusable
skills, so a new research project can be taken from "here is a domain" to a
running, publishable-bar-gated research loop without re-inventing the protocol.

## Skill family

Five skills under `skills/` (topics and metrics were merged into one stage —
scoring a topic's "Checkable" criterion already requires identifying its
metric, and both write to `topics.md` with no independent gate between them):

### `autoresearch` (dispatcher)

- Entry point and resume point. Reads the target project's `research/STATE.md`.
- Reports which stage the project is at, verifies the previous stage's gate
  artifacts exist on disk, and routes to the matching stage skill.
- If no `research/STATE.md` exists, initializes it and routes to
  `autoresearch-topics`.

### `autoresearch-topics` (stage 1)

- Input: a domain from the user.
- Brainstorms candidate research topics scored against autoresearch-suitability
  criteria: machine-checkable success, cheap-enough per-attempt evaluation,
  room for many iterations, publishable if the bar is met.
- User selects; then, for each chosen topic, derives candidate metrics / score
  functions ("what is good"): how each is computed, its cost, and its failure
  modes / gaming risks. Each metric is classified **primary** (enters the
  score function) or **guard** (anti-gaming side condition); the user approves
  the set per topic.
- Output written to `<project>/topics.md`: topic sections with their approved
  `### Metrics` blocks.

### `autoresearch-db` (stage 2)

- Builds the evidence base for the chosen topic:
  - Papers via the existing `download-ref` skill into `<project>/.knowledge/`.
  - **Insight coverage:** the reference set is selected to cover the main
    insight areas needed to *propose new ideas* — algorithmic techniques,
    proof/analysis methods, data structures, benchmark practices — not just
    SOTA results. The skill maps candidate insight areas for the topic and
    checks each is covered by at least one downloaded reference; gaps trigger
    further downloads.
  - **Distillation:** after download, each insight area is distilled from the
    papers into `research/INSIGHTS.md` — one entry per area with the
    transferable technique, when it applies, its limits, and source citations.
    These entries are the "skills to propose new ideas."
  - **User selection:** the distilled insight areas are presented to the user,
    who selects which are needed for idea generation on this topic. The
    selection is recorded in `research/INSIGHTS.md` (selected vs. shelved) and
    `autoresearch-run` draws on the selected entries when proposing each
    batch's attempts.
  - A structured domain database (e.g. QEC codes as JSON) under
    `research/database/`.
  - Pinned reference implementations of key algorithms (source-locked).
  - A complete `research/CATALOG.md` of algorithms and software with sources
    and status: `reproduced` / `pinned` / `paper-only`.
- Passing the **survey gate** means: catalog complete, knowledge base indexed,
  insight areas distilled and user-selected in `research/INSIGHTS.md`,
  reference implementations pinned.

### `autoresearch-validator` (stage 3)

- Sets the goal ("publishable bar") and builds the validator:
  - Dev instances vs a **sealed holdout** under `research/benchmark/private/`
    (gitignored; holdout labels never enter design context).
  - Docker image as the canonical strict environment: pinned dependencies, no
    network, resource limits. Fallback: locked venv / subprocess sandbox when
    Docker is unavailable or unsuitable; any downgrade is recorded in the
    validator manifest.
  - CLI contract: `validate <candidate>` → exit code + rich JSON report
    (status, score, per-instance results, precise diagnostics usable for
    debugging and self-improvement).
- **Strictness self-test (validator gate):** the validator must correctly
  reject a set of negative controls, each with an informative error message:
  a hard-coded-answers cheater, a wrong-answer candidate, a timeout candidate,
  and an environment-escape attempt.

### `autoresearch-run` (stage 4)

- The research loop. Refuses to start until the survey gate and validator gate
  have both passed (recorded in `STATE.md`).
- Per cycle (batch size default 10, from `STATE.md`):
  1. Run the batch of attempts.
  2. Write a reflection report to `docs/discussion/<timestamp>-cycle-NN.md`
     following the code-distance ideas-log shape: evidence carried forward,
     literature re-check, decision for the next batch. Attempt proposals draw
     on the selected entries in `research/INSIGHTS.md`; reflection may propose
     promoting shelved insights or distilling new ones (user confirms at the
     next gate).
  3. Propose an updated plan.
- **Soft gate with timeout:** `STATE.md` holds `authorized_rounds`. If rounds
  remain, the loop continues autonomously and decrements; otherwise it stops
  and waits for the user to review the report and re-authorize or amend.

## Hard protocol rules

Enforced by `autoresearch-run`, not advisory:

1. Survey gate before any attempt.
2. Validator gate (strictness self-test passed, holdout sealed) before any
   attempt.
3. Every attempt runs in its own git worktree `.worktrees/attempt-NNN/` with a
   `LOG.md`.
4. Every scored run goes through the validator; nothing else counts.
5. Hard wall-clock limit per run (default 300 s, configurable in `STATE.md`).
6. Holdout labels never enter design context.

## Project layout produced in a target research repo

```
<project>/
  topics.md                    # stage 1 output (topics + metrics)
  research/
    STATE.md                   # stage, config, gates passed, rounds authorized
    CATALOG.md                 # algorithms/software catalog
    INSIGHTS.md                # distilled idea-generation insights (selected/shelved)
    database/                  # structured domain data (JSON)
    validator/                 # Dockerfile, validate CLI, manifest, negative controls
    benchmark/private/         # sealed holdout (gitignored)
  .knowledge/                  # papers (download-ref, existing convention)
  .worktrees/attempt-NNN/      # one per attempt, each with LOG.md
  docs/discussion/             # reflection reports
```

## Reuse

- Stage 2 delegates paper acquisition to the existing `download-ref` skill.
- Stage 1 borrows suitability heuristics from `brainstorm-ideas` conventions
  but is its own skill (different output contract: `topics.md`, not an ideas
  log).
- Distinct from `flow`: `flow` is a within-session single-goal solver;
  `autoresearch-run` is a multi-session, validator-gated batch loop.

## Packaging and testing

- Each skill: `SKILL.md` with frontmatter description; heavy rubrics
  (validator CLI contract, negative-control checklist, reflection-report
  template, STATE.md schema) live in `references/`.
- Structural tests added under `tests/` following existing sci-brainstorm
  conventions.

## SOTA-informed refinements (2026-07-19 survey)

Adopted after surveying evolutionary code-discovery frameworks (FunSearch,
AlphaEvolve, OpenEvolve, ShinkaEvolve), end-to-end AI-scientist systems
(Sakana v2, Google co-scientist, CodeScientist, FutureHouse), and
ML-engineering loops (AIDE, MLE-bench, METR RE-Bench, Meta AIRA):

- **Seal by construction** — validator runs outside the attempt worktree;
  holdout mounted read-only into the validator environment only; scorer
  source unreachable from attempts. Hacks are fixed by patching the harness
  and adding a reproducing negative control, never by prompt instructions.
- **Budgeted holdout access** — holdout queries are metered by a budget in
  the validator manifest (default 1 aggregate query per 3 cycles, spent on
  the cycle's top candidate) to catch dev-set overfitting without turning
  the holdout into a second dev set.
- **Cascade evaluation + free `--precheck`** — structure/format validity is
  checkable without revealing a score; expensive scoring runs only for
  structurally valid candidates.
- **Batch composition** — each batch mixes diverse drafts, single-atomic-
  change improvements on the best known-good ancestor (lineage recorded in
  LOG.md via `kind` and `parent` fields), and capped debug attempts.
- **Novelty check before implementation** — candidate hypotheses are
  compared against all prior attempts' LOG.md hypotheses; near-duplicates
  are resampled before any compute is spent.
- **Scoped memory** — drafts see sibling digests (forcing diversity);
  improvements/debugs see their ancestral chain (preventing undo-redo).
  Failure artifacts (validator errors, stderr) feed the next batch's
  planning context.
- **Honest yield reporting** — reflection reports open with denominators
  ("K of N attempts improved the metric") and an ablation-style ranking of
  which change mattered most.

## Error handling

- Dispatcher: missing or corrupt `STATE.md` → re-derive stage from artifacts
  on disk, confirm with user before overwriting.
- Run loop: attempt crash or timeout → recorded in the attempt's `LOG.md` and
  counted as a failed attempt; never silently retried.
- Validator fallback (no Docker) → recorded in manifest; reports must state
  the environment used.
