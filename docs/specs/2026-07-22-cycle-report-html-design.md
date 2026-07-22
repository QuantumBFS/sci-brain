# Per-cycle HTML report for autoresearch-run

**Date:** 2026-07-22
**Status:** approved design, not yet implemented
**Scope:** `skills/autoresearch-run/` only (template, helper script, SKILL.md wiring)

## Problem

A round (cycle) of autoresearch-run contains 5–20 attempts. The current
per-cycle artifact is a prose markdown reflection
(`docs/discussion/YYYY-MM-DD-HHMMSS-cycle-NN.md`), which handles lineage
tables, score comparisons, and cross-round trends poorly. The soft gate says
"present the report" without specifying how, and there is no cross-round
view (score trajectory, blacklist growth, bar distance) short of opening N
files.

## Decisions made during design

1. **Surface:** a templated, self-contained HTML report per cycle.
2. **Scope:** per-round HTML files plus a rolling `index.html` — not a
   single mutating dashboard.
3. **Markdown stays canonical.** `cycle-NN.md` (the existing reflection
   template) remains the agent-readable source of truth that future cycles
   read for planning and the blacklist. The HTML is a pure presentation
   layer rendered from structured data; it is never the input to anything.
4. **Generation:** a bundled Python helper renders the HTML from a small
   per-cycle JSON file. The agent never hand-writes HTML.

## Artifacts per cycle

All in the target project's `docs/discussion/`:

| File | Writer | Role |
|---|---|---|
| `YYYY-MM-DD-HHMMSS-cycle-NN.md` | agent (existing) | canonical reflection, unchanged |
| `cycle-NN.json` | agent | structured extract: attempts + reflection prose + metrics |
| `cycle-NN.html` | `report.py` | rendered per-cycle report |
| `index.html` | `report.py` | rolling index across all cycles, regenerated every run |

`NN` is zero-padded to 2 digits from `next_cycle` (matching the md naming).
JSON/HTML deliberately omit the timestamp prefix so prior cycles are
discoverable by glob (`cycle-*.json`) without parsing dates.

## `cycle-NN.json` schema

Written by the agent during the Reflect step, after `cycle-NN.md`. The
helper validates it and fails loudly (nonzero exit, named missing field) —
a malformed JSON must never produce a silently incomplete report.

```json
{
  "schema_version": 1,
  "cycle": 3,
  "date_utc": "2026-07-22T14:03:00Z",
  "project": "code-distance",
  "attempts_range": [21, 35],
  "rounds_remaining": 2,
  "primary_metric": {"name": "dev score", "direction": "max"},
  "guard_metrics": [{"name": "runtime_s", "direction": "min", "limit": 600}],
  "bar": {"value": 0.90, "source": "GOAL.md"},
  "best_this_cycle": 0.847,
  "best_prior": 0.835,
  "holdout": {"spent": false, "result": null},
  "attempts": [
    {
      "id": 21,
      "kind": "draft",
      "parent": null,
      "hypothesis": "one-liner",
      "primary": 0.812,
      "guards": {"runtime_s": 512},
      "status": "no-change",
      "causal_note": "one-line causal claim from Yield",
      "log_path": ".worktrees/attempt-021/LOG.md"
    }
  ],
  "reflection": {
    "review": "markdown string — facts + budget state",
    "evidence": "markdown string",
    "literature": "markdown string",
    "next": "markdown string"
  },
  "lessons": [
    {
      "observation": "what happened",
      "root_cause": "the mechanism — must name something actionable",
      "evidence": "validator errors / per-instance results / LOG.md",
      "implication": "what it changes for the search",
      "confidence": "confirmed | suspected (optional)"
    }
  ],
  "blacklist_new": ["approach ruled out this cycle, with reason"],
  "insight_promotions": ["Shelved insight proposed for promotion"]
}
```

Field notes:

- `status` ∈ `improved | no-change | failed | timeout`. `improved` means
  strictly better than the pre-cycle best on the primary metric.
- `primary` is `null` for `failed`/`timeout` attempts.
- `direction` (`min`/`max`) drives chart orientation and the ▲/▼ delta
  arrows; never assume higher-is-better.
- `reflection.*` strings are the corresponding sections of `cycle-NN.md`,
  copied verbatim (the md remains canonical; the JSON carries a copy for
  rendering only).
- `blacklist_new` and `insight_promotions` are duplicated out of the prose
  so the template can highlight them; the prose remains the full record.

## Helper: `skills/autoresearch-run/helpers/report.py`

```
python3 helpers/report.py --cycle NN --dir docs/discussion/
```

- Python 3 stdlib only (`json`, `html`, `pathlib`, `argparse`, `re`).
  No pip dependencies — the skill must run in any user project.
- Reads `cycle-NN.json` plus **all** `cycle-*.json` in `--dir` for the
  trajectory strip and the index.
- Writes `cycle-NN.html` and regenerates `index.html`.
- Markdown-to-HTML for the reflection prose: minimal internal converter
  (headings, bold/italic, inline code, lists, links, paragraphs). Anything
  it doesn't recognize passes through escaped — never raw.
- All user-originated strings are HTML-escaped.
- Validation failures: exit 1 with `report.py: cycle-03.json: missing
  required field "attempts[2].status"`-style messages.
- Re-runnable: regenerating any old cycle after a template change is
  supported and produces a fresh render from the stored JSON.

The HTML template lives inside `report.py` as string constants (single-file
helper, nothing to locate at runtime).

## `cycle-NN.html` layout

Self-contained: inline CSS, inline SVG charts, **no CDN, no external
requests, no JS required** (a small amount of inline JS is allowed for
progressive niceties but every feature must degrade to static HTML). Light
background only (print/email-safe). Chart colors, mark design, and axis
rules follow the dataviz skill; the implementer must load that skill before
writing the chart code.

Organized as a retrospective cycle — **Review** (what we did) → **Think**
(what happened and why; root cause) → **Next round** (what to do) — the
user's chosen logic, revised 2026-07-22. (History: the first cut
transcribed the reflection sections into nine flat headings, scattering
each answer and duplicating facts between KPIs, table, a separate lineage
card, and Yield/State prose; an intermediate cut used outcome/evidence/next
with the yield narrative chart-adjacent — moved to Think because "which
change mattered" is diagnosis, not fact.) Each fact appears exactly once.
Top to bottom:

1. **Summary top** (no heading): header — project, "cycle NN", attempts
   AAA–BBB, date, rounds remaining; KPI strip — four tiles: best this
   cycle (▲/▼ delta vs prior best), bar value and remaining gap, yield
   "K/N improved", holdout status.
2. **Review — what we did**: trajectory card — inline SVG line chart of
   best-so-far primary metric vs cycle (from all `cycle-*.json`), GOAL
   bar as labeled threshold, one small *separate* chart per guard metric
   (never a second axis) — then one lineage-ordered attempt table
   carrying both results and parent structure: rows grouped by chain,
   descendants indented (`└`) under their ancestor, earlier-cycle
   ancestors as grey label rows, chains ordered by earliest attempt id.
   Columns: id (links to `log_path`), kind badge, hypothesis, primary,
   guard(s), status chip, causal note; best row highlighted. The section
   closes with `reflection.review` prose (honest denominators, per-attempt
   causal claims, budget state).
3. **Think — what happened and why**: **Lessons we learnt** — the core
   of the layer
   (added 2026-07-22 after feedback that Think was too shallow: nothing
   forced root-cause reasoning). A required `lessons` array (≥1 entry;
   validation rejects missing/blank fields) renders as structured blocks:
   observation headline + confirmed/suspected tag, then root cause /
   evidence / implication rows. The md reflection template carries a
   matching "Lessons we learnt" subsection with the why-chain rule: a
   score is a result, not a cause — keep asking why until the answer
   names something actionable. Then `reflection.evidence`
   (`blacklist_new` highlighted) and Literature check, both as h3
   subsections. (2026-07-22: the md template's own sections were renamed
   to the same three-part logic — Review merges the old Yield + State,
   Think holds Lessons/Evidence/Literature, Next round is the old
   Decision — so agent and reader share one structure; `reflection.*`
   keys became review/evidence/literature/next.)
4. **Next round**: `reflection.decision` (next-batch hypothesis,
   abandonment condition) with `insight_promotions` in an "awaiting user
   confirmation" box.
5. **Footer** — `← cycle-(NN-1) · index · cycle-(NN+1) →` (missing
   neighbors rendered as disabled).

## `index.html`

Regenerated on every helper run from all `cycle-*.json`:

- The same cross-round trajectory chart, full width.
- A table of cycles: NN (link), date, attempt range, yield K/N, best
  score, holdout spent?, one-line decision excerpt (first sentence of
  `reflection.decision`).
- Cumulative counters: total attempts, total blacklisted approaches.

## Skill wiring (`SKILL.md` + references)

- `references/reflection-template.md`: after the md report, add the step —
  write `cycle-NN.json` (schema above; reference a new
  `references/report-schema.md` or inline the field list), then run
  `python3 <skill-dir>/helpers/report.py --cycle NN --dir docs/discussion/`.
- `SKILL.md` Cycle step 3 (Reflect): one added sentence naming the JSON +
  helper invocation.
- `SKILL.md` step 4 (Soft gate): when stopping for re-authorization,
  present the terminal digest as now **and** print the path to
  `cycle-NN.html` (and `index.html`) for the user to open.
- Helper failure is non-fatal to the loop: if `report.py` exits nonzero,
  record the error in the reflection md and continue — the md is canonical;
  the HTML must never block a cycle.

## Error handling summary

- Malformed/missing JSON fields → helper exits 1 with a named field; agent
  fixes the JSON and re-runs; loop never blocked.
- Missing prior cycle JSONs (e.g., pre-adoption cycles) → trajectory chart
  simply starts at the first cycle that has JSON; no backfill required.
- `log_path` links may dangle if worktrees are pruned later; acceptable —
  they are audit links, not load-bearing.

## Testing

- `helpers/test_report.py` (stdlib `unittest`, runnable via
  `python3 -m unittest`) with a fixture set of 3 synthetic cycle JSONs
  covering: min- and max-direction metrics, failed/timeout attempts,
  a cycle with no improvement, holdout spent, empty `blacklist_new`.
- Assertions: helper exits nonzero on each required-field deletion;
  generated HTML contains no unescaped `<` from data strings; trajectory
  SVG present when ≥2 cycles, single-point fallback at 1 cycle; index
  lists all fixture cycles.
- Visual check at implementation time: render the fixtures, open in a
  browser, and run `figure-taste`-level judgment on the charts manually
  (no automated pixel tests).

## Out of scope

- Full-run lineage DAG (future index.html enhancement).
- Dark-mode styling, JS interactivity (sorting/filtering).
- Backfilling JSON for cycles run before this feature existed.
- Any change to `cycle-NN.md`'s content or its role as canonical.
