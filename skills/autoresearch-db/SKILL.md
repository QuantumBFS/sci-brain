---
name: autoresearch-db
description: Use when building the evidence base for a chosen autoresearch topic — maps the insight areas needed to propose new ideas, downloads references to cover them via download-ref, distills each area into research/INSIGHTS.md for user selection, builds a structured domain database and pinned reference implementations, and catalogs all algorithms/software in research/CATALOG.md. Owns the survey gate. Stage 2 of the autoresearch pipeline.
---

# Autoresearch DB

Input: a topic with metrics in `topics.md`. Output: a knowledge base, an
insight file, a domain database, pinned reference code, a catalog — and the
survey gate passed. The point is not "papers exist on disk" but "the agent
holds the insights needed to *propose new ideas*".
Resolve insight-map and Selected/Shelved choices through
`skills/autoresearch/references/approval-contract.md`. Consume an exact
pre-authorized decision without prompting; otherwise use the platform's
available user-input mechanism.

## Procedure

1. **Map insight areas.** From the topic and its metrics, list the insight
   areas an idea-proposer needs: algorithmic techniques, proof/analysis
   methods, data structures, benchmark practices for this problem class.
   Resolve user approval of the list before downloading anything.
2. **Download for coverage.** Build the exact reference manifest needed to
   cover the approved insight areas. Resolve a single approval decision that
   covers both that manifest and the deterministic cite-key policy: accept
   `download-ref`'s collision-free proposed keys, but stop on any collision
   or missing proposal. Record the decision through the shared approval
   contract, then acquire the references with the `download-ref` skill into
   `<project>/.knowledge/`. An exact pre-authorized decision is consumed
   without another prompt. Coverage check: every insight area is covered by
   ≥1 downloaded reference; areas with no coverage trigger further
   search/downloads. SOTA-results-only coverage is insufficient.
3. **Distill.** For each insight area, write one entry in
   `research/INSIGHTS.md` following
   `skills/autoresearch-db/references/insights-template.md` (Technique /
   Applies when / Limits / Sources). Distill from the rendered papers in
   `.knowledge/`, not from memory.
4. **User selects.** Resolve which distilled areas are needed for idea
   generation through
   `skills/autoresearch/references/approval-contract.md`. Selected entries go
   under `## Selected`, the rest under `## Shelved`. The run loop draws only
   on Selected.
5. **Domain database.** Build the structured dataset the topic needs (e.g.
   QEC codes as JSON) under `research/database/`, with a `README.md`
   documenting schema and provenance of every record.
6. **Pin reference implementations.** For each key algorithm with public
   code: record URL + commit hash, build it, and run its own smoke
   test/example. Implement small reference versions only where no code
   exists and the algorithm is load-bearing.
7. **Catalog.** Write `research/CATALOG.md`: every algorithm/software
   relevant to the topic, one row each — name, source (paper/repo),
   status `reproduced` (we ran it) / `pinned` (source-locked, not yet run) /
   `paper-only` (no code exists), and notes.

## Survey gate (owned by this skill)

Flip `survey_gate: passed <date>` and set `stage: validator` in
`research/STATE.md` only when all of:

- `research/CATALOG.md` exists and every key algorithm from the insight map
  appears in it;
- `.knowledge/INDEX.md` lists every reference cited in INSIGHTS.md and
  CATALOG.md;
- `research/INSIGHTS.md` has a non-empty `## Selected` section chosen by the
  user;
- every `reproduced`-status entry actually ran (its output is recorded in
  CATALOG.md notes).
