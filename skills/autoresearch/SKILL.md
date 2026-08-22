---
name: autoresearch
description: Use when starting, resuming, or asking about an autoresearch project — a four-stage pipeline (topics → db → validator → run) that chooses machine-checkable research topics with score metrics and a red-teamed acceptance gate, builds the evidence base (references, INSIGHTS.md, domain database, CATALOG.md), builds a sealed Docker-canonical validator with negative controls, then runs the loop of validator-scored attempts with reflection reports and stuck-triggered insight refresh. Reads research/STATE.md to find the current stage, verifies the previous stage's gate artifacts exist on disk, and follows the matching stage file. Triggers on "start autoresearch", "resume autoresearch", "autoresearch status", "choose autoresearch topics", "build the validator", "run the autoresearch loop", "what stage is my research project at".
---

# Autoresearch

One skill, four stages. State lives in `<project>/research/STATE.md`
(schema and template: `references/state-schema.md`). Each stage's procedure
is a file under `references/stages/`; this file decides which one applies
and then follows it in the same context.

| stage | what it produces | procedure |
|---|---|---|
| topics | `topics.md` — chosen topics, metrics, user-confirmed acceptance gate | `references/stages/topics.md` |
| db | `.knowledge/`, `research/INSIGHTS.md`, `research/database/`, `research/CATALOG.md`; flips `survey_gate` | `references/stages/db.md` |
| validator | `research/validator/` (GOAL.md, `validate` CLI, manifest), sealed holdout; flips `validator_gate` | `references/stages/validator.md` |
| run | `.worktrees/attempt-NNN/`, `docs/discussion/` reflection reports | `references/stages/run.md` |

Supporting references: `references/insights-template.md` (db),
`references/validator-contract.md` + `references/negative-controls.md`
(validator), `references/attempt-protocol.md` +
`references/reflection-template.md` + `references/report-schema.md` (run),
`helpers/report.py` (HTML cycle reports) and `helpers/gen_campaign.py`
(cross-cycle full-campaign overview).

## Procedure

1. **Locate state.** Read `<project>/research/STATE.md`.
   - **Missing** → new project: ask the user for a recommended number of
     attempts per cycle (suggest 10). Explain that this is a planning default,
     not a fixed batch size: the agent may choose a smaller or larger cycle
     when the evidence, candidate pool, cost, or available parallelism calls
     for it, without exceeding the authorized attempt budget. Create
     `research/STATE.md` from `references/state-schema.md` (stage `topics`),
     record the answer as `recommended_cycle_size`, then follow
     `references/stages/topics.md`.
   - **Readable legacy state with `batch_size`** → preserve its value by
     migrating it to `recommended_cycle_size` on the next state write. Treat
     it as guidance, not a hard protocol rule.
   - **Corrupt/unreadable** → re-derive the stage from the artifact table
     below (earliest stage whose required artifacts are missing), show the
     user the derived state, and confirm with them before overwriting
     STATE.md. Never overwrite a readable STATE.md.
2. **Verify, don't trust.** Check the artifacts the recorded stage implies.
   If any are missing, drop back to the earliest stage whose artifacts are
   missing and tell the user what was expected and not found.
3. **Report and route.** Summarize in a few sentences: stage, gates passed,
   attempts completed, authorized attempts remaining. Then read the stage's
   procedure file and follow it. When a stage advances `stage:` in
   STATE.md, return to step 2 for the next stage unless the stage file says
   to stop for user review.

| `stage` | required artifacts before entering | procedure |
|---|---|---|
| topics | — | `references/stages/topics.md` |
| db | `topics.md` with ≥1 chosen topic, each with a `### Metrics` block and a user-confirmed `### Acceptance gate` block | `references/stages/db.md` |
| validator | survey gate passed: `research/CATALOG.md`, `.knowledge/INDEX.md`, `research/INSIGHTS.md` with a user-selected section | `references/stages/validator.md` |
| run | validator gate passed: `research/validator/manifest.json` recording self-test results | `references/stages/run.md` |
| done | final report exists in `docs/discussion/` | report status only |

A user asking for one stage directly ("brainstorm autoresearch topics for
X", "build the validator") still goes through steps 1–2: the stage file is
followed only once its entry artifacts verify, or the user records an
override.

## Hard rules (all stages)

- Gates flip to `passed` only by the stage that owns them (`db` →
  `survey_gate`, `validator` → `validator_gate`), after the checklist in
  that stage file verifies on disk.
- Gates are never skipped on request without appending the deviation to
  `overrides:` in STATE.md (see schema).
- Holdout labels (`research/benchmark/private/`) never enter design
  context, at any stage.
