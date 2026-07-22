# cycle-NN.json — schema for the HTML report

Written by the agent during the Reflect step, *after* the canonical
`cycle-NN.md`. Rendered by `helpers/report.py` into `cycle-NN.html` +
`index.html` (see `report.py --help`). The markdown stays canonical; this
JSON is a structured copy for presentation only. Filenames carry no
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
    "yield": "…", "evidence": "…", "literature": "…",
    "decision": "…", "state": "…"
  },
  "blacklist_new": ["approach ruled out this cycle, with reason"],
  "insight_promotions": ["Shelved insight proposed for promotion"]
}
```

Field notes:

- `direction` is `"min"` or `"max"`; it drives the trajectory's
  best-so-far accumulation and the ▲/▼ delta coloring. Never assume
  higher-is-better.
- `kind` ∈ `draft | improve | debug`; `parent` is the ancestor attempt id
  for improve/debug, `null` for drafts.
- `status` ∈ `improved | no-change | failed | timeout`. `improved` means
  strictly better than the pre-cycle best on the primary metric. `primary`
  is `null` for failed/timeout attempts.
- `guard_metrics` (optional, default `[]`): each entry may carry a `limit`
  drawn as a threshold line; per-cycle guard charts plot the guard value of
  each cycle's best attempt. `guards` / `causal_note` on an attempt are
  optional (default `{}` / empty).
- `reflection.*` are the five sections of `cycle-NN.md`, copied verbatim
  (minimal markdown is rendered: headings, lists, bold/italic/code/links;
  raw HTML is escaped).
- `best_this_cycle` / `best_prior` may be `null` (all attempts failed /
  first cycle). `holdout.result` is a short aggregate string when
  `holdout.spent` is true, else `null`.
- `blacklist_new` and `insight_promotions` duplicate what the prose already
  says so the template can highlight them; empty arrays are fine.
