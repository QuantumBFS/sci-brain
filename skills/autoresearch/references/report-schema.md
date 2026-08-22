# cycle-NN.json — schema for the HTML report

Written by the agent during the Reflect step, *after* the canonical
`cycle-NN.md`. Rendered by `helpers/report.py` into `cycle-NN.html` +
`index.html`, and aggregated by `helpers/gen_campaign.py` into
`campaign.html` (see each helper's `--help`). The markdown stays canonical;
this JSON is a structured copy for presentation only. Filenames carry no
timestamp prefix (`cycle-03.json`, zero-padded to 2 digits) so prior cycles
are globbable without date parsing.

All fields below are required unless marked optional. The helper fails with
a named field on anything missing — fix the JSON and re-run; a report
failure never blocks the loop (the md is the record).

```json
{
  "schema_version": 1,
  "cycle": 3,
  "date_utc": "2026-07-22T14:03:00Z",
  "project": "code-distance",
  "attempts_range": [21, 35],
  "attempts_remaining": 20,
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
    "review": "…", "evidence": "…", "literature": "…", "next": "…"
  },
  "lessons": [
    {
      "observation": "improve 031 gained +0.05; siblings 032/033 flat",
      "root_cause": "the bond-dimension bottleneck, not the optimizer —
        only the change that raised chi moved any instance",
      "evidence": "per-instance results: gains concentrated on the 4
        largest instances; LOG.md of 032 shows identical scores to parent",
      "implication": "optimizer tweaks blacklisted; next batch varies chi",
      "confidence": "confirmed"
    }
  ],
  "blacklist_new": ["approach ruled out this cycle, with reason"],
  "insight_promotions": ["Shelved insight proposed for promotion"]
}
```

Field notes:

- `direction` is `"min"` or `"max"`; it labels which direction is better,
  identifies the best attempt in the table, and drives the cross-cycle
  best-so-far trajectory in `index.html`. The cycle page itself plots every
  scored attempt's raw `primary` value from that cycle — never a cumulative
  or best-so-far value. Never assume higher-is-better.
- `kind` ∈ `draft | improve | debug`; `parent` is the ancestor attempt id
  for improve/debug, `null` for drafts.
- `status` ∈ `improved | no-change | failed | timeout`. `improved` means
  strictly better than the pre-cycle best on the primary metric. `primary`
  is `null` for failed/timeout attempts.
- `guard_metrics` (optional, default `[]`) defines the guard columns shown in
  the attempt table; each entry may carry a `limit` for interpretation.
  `guards` / `causal_note` on an attempt are optional (default `{}` / empty).
- `reflection.*` mirror the md template's prose sections, copied verbatim
  (minimal markdown is rendered: headings, lists, bold/italic/code/links;
  raw HTML is escaped): `review` = "Review — what we did" (facts + budget
  state), `evidence` = "Evidence carried forward", `literature` =
  "Literature check", `next` = "Next round". `next` contains the ranked 2–4
  promising directions, evidence-backed reasons, discriminating attempts,
  decision signals, and explicit top recommendation required by the reflection
  template. The "Lessons we learnt"
  subsection is carried structured in `lessons` only, never as prose.
- `best_this_cycle` / `best_prior` may be `null` (all attempts failed /
  first cycle). `holdout.result` is a short aggregate string when
  `holdout.spent` is true, else `null`.
- `lessons` (required, at least one entry) is the structured form of the
  md's "Lessons we learnt" section — the core of the Think layer. Each
  entry: `observation` (what happened), `root_cause` (the mechanism — a
  score is a result, not a cause; name something actionable), `evidence`
  (validator errors, per-instance results, LOG.md), `implication` (what
  it changes: blacklist entry, revised assumption, debug target),
  optional `confidence` ∈ `confirmed | suspected`. Off-goal findings from
  the md's "Lessons we learnt" — off-topic but maybe worth publishing, or
  possibly leading to a significant result — go here too, as entries
  whose `implication` starts with `off-goal:`.
- `blacklist_new` and `insight_promotions` duplicate what the prose already
  says so the template can highlight them; empty arrays are fine.
