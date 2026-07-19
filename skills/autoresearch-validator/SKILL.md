---
name: autoresearch-validator
description: Use when setting the goal and building the validator for an autoresearch topic — defines the publishable bar with the user, splits dev instances from a sealed gitignored holdout, builds a Docker-canonical strict environment (recorded fallback allowed), implements the validate CLI with rich JSON errors, and passes the strictness self-test against negative controls. Owns the validator gate. Stage 3 of the autoresearch pipeline.
---

# Autoresearch Validator

Goal: once the validator's bar is met, the result is publishable — so the
validator must be impossible to satisfy by accident or by cheating. Contract
details: `references/validator-contract.md`; strictness self-test:
`references/negative-controls.md`.

## Procedure

1. **Define the publishable bar** with the user: a goal statement naming the
   primary metric (from `topics.md`), the threshold, and the instance
   families it must hold on. Write it to `research/validator/GOAL.md`.
2. **Split instances.** Development instances (visible to attempts) vs a
   **sealed holdout** under `research/benchmark/private/`:
   - add `research/benchmark/private/` to `.gitignore`;
   - seal **by construction, not convention**: the validator runs as a
     separate process outside the attempt worktree, the holdout is mounted
     read-only into the validator environment only, and neither the holdout
     nor the scorer source is reachable from attempt code (agents hack any
     scorer they can touch — METR measured ~30% hack rates, and "do not
     cheat" prompts do not work; harden the harness instead);
   - holdout labels are never opened in design context — attempts and
     reflection see only aggregate pass/fail from the validator;
   - set a **holdout query budget** in `research/validator/manifest.json`
     (default: 1 aggregate query per 3 cycles); the validator logs every
     holdout query there and refuses queries beyond budget;
   - record instance provenance (where each came from, how labels were
     obtained) in `research/validator/manifest.json`.
3. **Build the canonical environment.** A Docker image: pinned dependencies,
   `--network none` at run time, CPU/memory limits, the wall-clock limit
   from STATE.md enforced by the harness not the candidate. If Docker is
   unavailable or unsuitable (e.g. HPC-only toolchain), fall back to a
   locked venv + subprocess sandbox and record
   `validator_env: fallback (<reason>)` in STATE.md and in the manifest —
   never fall back silently.
4. **Implement the `validate` CLI** per `references/validator-contract.md`,
   under `research/validator/`. Guard metrics from `topics.md` become
   rejection rules. Include the free `--precheck` mode (structure/format
   check, no score) and cascade evaluation (cheap checks first, full scoring
   only for structurally valid candidates) so attempts stop wasting cycles
   on format bugs.
5. **Strictness self-test.** Build the four negative controls
   (`cheater`, `wrong-answer`, `timeout`, `env-escape`) per
   `references/negative-controls.md`, plus one per topic-specific gaming
   risk. Run them; all must be rejected with informative errors. Record
   results under `"self_test"` in `research/validator/manifest.json`.

## Validator gate (owned by this skill)

Flip `validator_gate: passed <date>` and set `stage: run` in
`research/STATE.md` only when all of:

- `GOAL.md` states the bar in terms of the primary metric;
- the holdout is sealed (gitignored, labels unopened) with provenance in the
  manifest;
- `validate` runs end-to-end on a trivial baseline candidate against dev
  instances;
- every negative control is rejected with a specific `errors[]` entry;
- the manifest records the environment (`docker` or `fallback (<reason>)`).
