---
name: autoresearch
description: Use when starting or resuming an autoresearch project — reads research/STATE.md to find the current stage of the pipeline (topics → metrics → db → validator → run), verifies the previous stage's gate artifacts exist on disk, and routes to the matching stage skill. Triggers on "start autoresearch", "resume autoresearch", "autoresearch status", "what stage is my research project at".
---

# Autoresearch (dispatcher)

Pipeline: `autoresearch-topics` → `autoresearch-metrics` → `autoresearch-db`
→ `autoresearch-validator` → `autoresearch-run`. State lives in
`<project>/research/STATE.md` (schema and template:
`skills/autoresearch/references/state-schema.md`).

## Procedure

1. **Locate state.** Read `<project>/research/STATE.md`.
   - **Missing** → new project: create `research/STATE.md` from the template
     in `references/state-schema.md` (stage `topics`), then invoke
     `autoresearch-topics`.
   - **Corrupt/unreadable** → re-derive the stage from the artifact table
     below (earliest stage whose required artifacts are missing), show the
     user the derived state, and confirm with them before overwriting
     STATE.md. Never overwrite a readable STATE.md.
2. **Verify, don't trust.** Check the artifacts the recorded stage implies.
   If any are missing, drop back to the earliest stage whose artifacts are
   missing and tell the user what was expected and not found.
3. **Report and route.** Summarize in a few sentences: stage, gates passed,
   attempts completed, authorized rounds remaining. Then invoke the stage
   skill.

| `stage` | required artifacts before entering | route to |
|---|---|---|
| topics | — | autoresearch-topics |
| metrics | `topics.md` with ≥1 chosen topic | autoresearch-metrics |
| db | a `### Metrics` block under each topic in `topics.md` | autoresearch-db |
| validator | survey gate passed: `research/CATALOG.md`, `.knowledge/INDEX.md`, `research/INSIGHTS.md` with a user-selected section | autoresearch-validator |
| run | validator gate passed: `research/validator/manifest.json` recording self-test results | autoresearch-run |
| done | final report exists in `docs/discussion/` | report status only |

Gates are never skipped on request without appending the deviation to
`overrides:` in STATE.md (see schema).
