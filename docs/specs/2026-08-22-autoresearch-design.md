# Autoresearch skill — design

**Date:** 2026-08-22 (supersedes the 2026-07-19 five-skill design)
**Status:** As built — `skills/autoresearch/`
**Reference run:** `~/agentic/code-distance` — a completed manual execution of
this pipeline (survey gate → sealed benchmark → validator → 100+ attempt
worktrees → reflection logs in `docs/discussion/`).
**Companion docs:** `2026-07-19-sota-autoresearch-survey.md` (lessons adopted
from SOTA frameworks), `2026-07-22-cycle-report-html-design.md` (HTML cycle
reports).

## Goal

Take a research project from "here is a domain" to a running,
publishable-bar-gated research loop: domain → topics with metrics and a
red-teamed acceptance gate → evidence base → strict validator → iterative
attempt/reflect loop. Two properties matter most: a validator that cannot be
satisfied by accident or cheating, and a hypothesis generator that does not
spend attempts on trivial ideas.

## Layout

One skill. The dispatcher reads `research/STATE.md`, verifies the artifacts
the recorded stage implies, and follows the matching stage file in the same
context. (An earlier version split the stages into five skills; none of the
stage skills were ever invoked standalone, so they were merged.)

```
skills/autoresearch/
  SKILL.md                     # dispatcher + hard rules + gate table
  references/
    state-schema.md            # research/STATE.md template and rules
    stages/topics.md           # stage 1
    stages/db.md               # stage 2 — owns survey_gate
    stages/validator.md        # stage 3 — owns validator_gate
    stages/run.md              # stage 4 — the loop
    insights-template.md       # INSIGHTS.md: Selected / Candidate / Shelved
    validator-contract.md      # validate CLI + JSON report
    negative-controls.md       # strictness self-test
    attempt-protocol.md        # worktree + LOG.md + commit, every attempt
    reflection-template.md     # per-cycle report
    report-schema.md           # cycle-NN.json for the HTML renderer
  helpers/report.py            # HTML cycle reports (+ test_report.py)
```

The skill's `description` triggers on stage-level phrases ("choose
autoresearch topics", "build the validator", "run the autoresearch loop") as
well as start/resume/status, so direct requests still enter through the
dispatcher's artifact verification.

## Stages

### Stage 1 — topics (`stages/topics.md`)

- Input: a domain. Output: `<project>/topics.md`, stage → `db`.
- 5–10 web-grounded candidates scored 1–5 on **Checkable / Cheap / Headroom /
  Publishable**; user picks.
- Per chosen topic: 2–5 candidate metrics (definition, computation + cost,
  gaming risks), each **primary** (enters the score) or **guard**
  (anti-gaming side condition); user approves.
- **Acceptance gate**: the user states the publication-bar condition
  (primary metric, threshold, instance families, baseline). It is
  red-teamed — overfitting, lookup tables, weak baseline, threshold below
  published results, narrow instances, metric/claim divergence, the
  metric's own gaming risks — and strengthened until no hack survives, then
  explicitly confirmed. Surviving hacks become negative controls at stage 3.

### Stage 2 — db (`stages/db.md`)

- Maps the **insight areas** an idea-proposer needs (techniques, analysis
  methods, data structures, benchmark practice); downloads references via
  `download-ref` until every area is covered; distills each into
  `research/INSIGHTS.md` (Technique / Applies when / Limits / Sources); user
  selects → `## Selected` vs `## Shelved`. Selected is the run loop's default
  grounding, not a cap.
- Builds `research/database/` (with README provenance), pins reference
  implementations (URL + commit, smoke-tested), writes `research/CATALOG.md`
  (`reproduced` / `pinned` / `paper-only`).
- **Survey gate**: catalog complete, INDEX.md lists every cited reference,
  Selected non-empty, every `reproduced` entry actually ran.

### Stage 3 — validator (`stages/validator.md`)

- Formalizes the acceptance gate into `research/validator/GOAL.md`; presents
  the **validation method** (dev/holdout families and provenance, holdout
  query budget, `time_limit_seconds` — default 300 s, environment, planned
  negative controls) for user confirmation before building.
- **Sealed holdout** under `research/benchmark/private/` (gitignored), sealed
  by construction: validator runs outside the attempt worktree, holdout
  mounted read-only into the validator environment only, scorer source
  unreachable from attempts, metered holdout queries.
- Docker-canonical environment (pinned deps, no network, resource limits,
  harness-enforced wall clock); recorded fallback otherwise.
- `validate` CLI per `validator-contract.md`: exit code + JSON (status, score,
  per-instance, errors), free `--precheck`, cascade evaluation; guard metrics
  become rejection rules.
- **Validator gate**: GOAL.md matches the confirmed acceptance gate; holdout
  sealed; validate runs on a trivial baseline; all negative controls
  (`cheater`, `wrong-answer`, `timeout`, `env-escape`, plus one per
  acceptance-gate hack) rejected with specific errors; everything the run
  stage needs committed to main.

### Stage 4 — run (`stages/run.md`)

Entry refused unless both gates read `passed` and verify on disk. Hard
rules: one worktree + `LOG.md` per attempt; only validator scores count;
hard wall-clock limit; holdout labels never in design context; crashes are
recorded failures, never silently retried.

Cycle:

0. **Stuck?** (skipped on cycle 1) Stuck = the previous planning pass had
   fewer than `batch_size` drafts + improvements after filters, **or** two
   consecutive cycles without best-dev-score improvement. Then: take the
   latest reflection's root cause, invoke `survey` (or `download-ref`)
   scoped to it, distill into `INSIGHTS.md` `## Candidate` (usable
   immediately; promoted/shelved at the next soft gate), record the refresh
   in the reflection. At most one refresh per cycle; a fruitless refresh
   surfaces "wind down / pivot" at the next soft gate.
1. **Plan the batch.** ~2× `batch_size` candidates, each naming its source
   (insight / literature / original). Every **draft** carries:
   - **mechanism** — the bottleneck removed (from the latest root-cause
     diagnosis where one exists) and an effect-size ceiling against the
     **gap** = GOAL.md threshold − current best dev score;
   - **prior art** — KB + one web search; if already published for this
     problem the attempt is relabeled kind `baseline`.
   Rank by **expected gap closure × distinctness**; cost is a constraint
   (fits `time_limit_seconds`), never a score term. Filters: **novelty**
   (vs all prior LOG.md hypotheses), **triviality** (mechanism can't close a
   measurable fraction of the gap; parameter/config change — those are
   `improve`-only; unlabeled reproduction), **batch composition** (drafts +
   single-atomic-change improvements on the best ancestor + ≤2 debugs +
   ≤1 baseline). Drafts see sibling digests; improvements/debugs see their
   ancestral chain; previous failure artifacts feed forward.
2. **Confirm the plan** with the user on the first batch of each
   authorization (kind, source, mechanism, prior art per hypothesis).
3. **Execute** per `attempt-protocol.md` (LOG.md records kind, parent,
   hypothesis, mechanism, prior art, expected evidence, validator outcome;
   code + LOG.md + report.json committed on `attempt-NNN`).
4. **Reflect**: `docs/discussion/<ts>-cycle-NN.md` + `cycle-NN.json` + HTML;
   optional budgeted holdout adjudication of the top candidate.
5. **Sync**: commit cycle artifacts to main; push main + attempt branches.
6. **Soft gate**: decrement `authorized_attempts`; continue autonomously
   while a batch remains, else stop with the report, 2–4 lesson-grounded
   directions, and Candidate-insight promotions. The user picks
   direction(s) and authorizes a number of **attempts** — never rounds.

Termination: bar met on dev → one holdout run → report both → `stage: done`;
write-up is `paper-writer`'s job.

## Target-project layout

```
<project>/
  topics.md                    # stage 1: topics, metrics, acceptance gates
  research/
    STATE.md                   # stage, config, gates, authorized_attempts
    CATALOG.md  INSIGHTS.md    # stage 2
    database/                  # structured domain data
    validator/                 # GOAL.md, validate CLI, manifest, controls
    benchmark/private/         # sealed holdout (gitignored)
  .knowledge/                  # papers (download-ref)
  .worktrees/attempt-NNN/      # one per attempt, each with LOG.md
  docs/discussion/             # reflection reports (md/json/html)
```

## Testing

`tests/test_autoresearch_skills.py` — grep-based structural tests over
SKILL.md, the stage files, and references (dispatcher routing, gate
ownership, mechanism/prior-art lines, triviality check, `baseline` kind,
stuck definition and `survey` refresh, `## Candidate`). `helpers/test_report.py`
covers the HTML renderer.
