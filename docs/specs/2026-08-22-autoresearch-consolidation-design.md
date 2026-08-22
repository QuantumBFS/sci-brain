# Autoresearch consolidation and anti-triviality design (2026-08-22)

## Motivation

1. The autoresearch pipeline is split across five skills (`autoresearch`,
   `autoresearch-topics`, `autoresearch-db`, `autoresearch-validator`,
   `autoresearch-run`). In practice only the dispatcher is ever invoked;
   the four stage skills are never used standalone, so the split is
   fragmentation without benefit.
2. Run-stage hypotheses are sometimes trivial (parameter tweaks, caching,
   the obvious variant). Root cause: the planning rubric ranks on
   "information gain, cost, distinctness" — cost rewards cheap ideas — and
   the only filter is novelty against *prior attempts*, not against the
   literature or the publishable bar.

## 1. Merge into one skill

Target layout:

```
skills/autoresearch/
  SKILL.md                     # dispatcher + hard rules + gate table
  references/
    state-schema.md
    stages/topics.md           # body of former autoresearch-topics/SKILL.md
    stages/db.md               # body of former autoresearch-db/SKILL.md
    stages/validator.md        # body of former autoresearch-validator/SKILL.md
    stages/run.md              # body of former autoresearch-run/SKILL.md
    insights-template.md       # from autoresearch-db/references/
    validator-contract.md      # from autoresearch-validator/references/
    negative-controls.md       # from autoresearch-validator/references/
    attempt-protocol.md        # from autoresearch-run/references/
    reflection-template.md     # from autoresearch-run/references/
    report-schema.md           # from autoresearch-run/references/
  helpers/
    report.py                  # from autoresearch-run/helpers/
    test_report.py
```

Rules:

- Stage files drop their YAML frontmatter; their first heading becomes
  `# Stage N: <name>`. Content is otherwise moved verbatim, except for
  the run-stage changes in sections 2–3 and path fixes.
- `SKILL.md` keeps the dispatcher procedure. Step 3 ("Report and route")
  reads `references/stages/<stage>.md` and follows it in the same
  context instead of invoking a sibling skill. The gate table's
  "route to" column names the stage file.
- Gate ownership wording ("owned by this skill") becomes "owned by this
  stage". STATE.md schema rule about which skill flips which gate is
  reworded to stages.
- All internal cross-references (`skills/autoresearch-db/references/…`,
  `skills/autoresearch/references/state-schema.md`, `references/…`
  relative paths) are rewritten to the new locations.
- The four `skills/autoresearch-*/` directories are deleted, including
  `__pycache__`.
- Collateral edits: `CLAUDE.md` skill list (one `autoresearch` entry
  describing the four stages; count 15 → 12), the
  `.claude-plugin` metadata if it enumerates skills (verify),
  `tests/test_autoresearch_skills.py` paths, and a one-line "superseded
  layout" note at the top of
  `docs/specs/2026-07-19-autoresearch-skills-design.md`.
- The `description:` of the merged skill must still trigger on the
  stage-level phrases ("choose autoresearch topics", "build the
  validator", "run the autoresearch loop") so direct requests still land.

## 2. Anti-triviality in the run stage

Edits to `references/stages/run.md` step 1 and
`references/attempt-protocol.md` LOG.md block.

### Hypothesis card

Every **draft** hypothesis carries, in addition to source and expected
evidence:

- **mechanism** — the bottleneck it removes (named from the latest
  reflection's root-cause diagnosis where one exists) and a rough
  effect-size ceiling, stated against the **gap** = GOAL.md threshold −
  current best dev score.
- **prior art** — result of checking `.knowledge/INDEX.md` +
  `research/INSIGHTS.md` and one quick web search. Values: `none found`,
  or a citation. If the technique is already published *for this
  problem*, the hypothesis is relabeled kind `baseline`.

`improve` and `debug` attempts inherit mechanism from their ancestor and
state only the atomic change.

### New attempt kind: `baseline`

- A reproduction of a published technique, scored by the validator like
  any attempt.
- At most one per batch; allowed only while no scored baseline for that
  technique exists in any prior LOG.md.
- Never counted as a draft for batch-composition purposes.

### Triviality filter

Runs alongside the novelty filter before anything is implemented. A draft
is rejected and resampled if any of:

- its mechanism cannot plausibly close a measurable fraction of the gap
  (state the reasoning in one line);
- it is a parameter, config, or constant change — those are only ever
  `improve` on a scored ancestor;
- prior art is a published application to this problem and it was not
  relabeled `baseline`.

### Ranking

Candidates are ranked by **expected gap closure × distinctness**. Cost is
a hard constraint (the attempt must fit `time_limit_seconds`), not a
score term.

### Batch confirmation

The plan presented for user confirmation shows, per hypothesis: kind,
source, mechanism, prior art — one line each — so the argument is
visible before authorization.

## 3. Stuck → insight refresh

Added to `references/stages/run.md` as a step between Reflect and Plan.

### Definition of stuck

Either:

- (a) after novelty + triviality filters, the candidate pool holds fewer
  than `batch_size` drafts + improvements; or
- (b) two consecutive cycles with no improvement in best dev score.

### Refresh procedure

When stuck, before planning the next batch:

1. Take the diagnosed bottleneck / root cause from the latest reflection.
2. Invoke the `survey` skill scoped to that bottleneck (or `download-ref`
   for specific IDs already known) into `<project>/.knowledge/`.
3. Distill new entries into `research/INSIGHTS.md` under a new
   `## Candidate` section (same entry format as Selected). Candidate
   entries are valid grounding for hypotheses immediately — the
   autonomous loop is not blocked on user confirmation.
4. Record the refresh (query, what was added, what it unblocked) in the
   cycle's reflection report.

Constraints:

- At most one refresh per cycle.
- If a refresh adds nothing and the loop remains stuck, the next soft
  gate presents "wind down / pivot" as a direction instead of spending
  more attempts.

### Promotion

At the soft gate, `## Candidate` entries are promoted to `## Selected`
or moved to `## Shelved` with user confirmation, as part of the existing
insight-promotion step. `insights-template.md` documents the three
sections.

## Testing

`tests/test_autoresearch_skills.py`:

- Rewrite all path constants to the merged layout; assert the four old
  directories no longer exist.
- Dispatcher: routes by reading `references/stages/<stage>.md`.
- Run stage: asserts for mechanism and prior-art lines, the triviality
  filter, the `baseline` kind and its one-per-batch cap, ranking on gap
  closure with cost as a constraint, the stuck definition (both
  conditions), the insight refresh invoking `survey`, and the
  `## Candidate` section with promotion at the soft gate.
- Attempt protocol: LOG.md block includes mechanism and prior-art;
  kind vocabulary includes `baseline`.
- `helpers/test_report.py` still passes from the new location.

## Out of scope

- Changing the topics, db, or validator stage procedures beyond path
  and wording fixes.
- Any change to `report.py` output.
