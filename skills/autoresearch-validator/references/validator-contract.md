# Validator CLI contract

The validator is a CLI the run loop invokes for every scored attempt. It is
the *only* thing that counts as scoring.

## Invocation

    validate <candidate-dir> [--precheck] [--instances dev|holdout] [--out report.json]

`<candidate-dir>` is an attempt worktree. `--instances dev` (default) scores
the visible development instances; `--instances holdout` scores the sealed
set and prints only aggregate pass/fail per instance — never labels.
Holdout runs are metered: each one is logged in `manifest.json` and refused
once the holdout query budget is exhausted.

`--precheck` is a **free validity check**: it verifies the candidate's
structure and output format only, reveals no score, and does not count as a
scored run. Attempts may call it as often as they like — its purpose is to
stop format bugs from consuming scored attempts.

## Cascade evaluation

Scoring runs as a cascade: cheap structural checks (precheck stage) →
smallest instances → full instance set. A candidate that fails a stage is
rejected there with that stage's diagnostics; expensive stages run only for
survivors. This keeps failed attempts fast and error messages specific.

## Exit codes

- `0` — candidate evaluated; see report for score.
- `1` — candidate rejected (wrong answers, cheating detected, contract
  violation). Report explains why.
- `2` — validator infrastructure error (not the candidate's fault).

## JSON report

Written to `--out` (default `report.json`), always, even on rejection:

    {
      "status": "scored" | "rejected" | "error",
      "score": <number or null>,          // primary metric value
      "per_instance": [
        {"instance": "<id>", "result": "pass" | "fail" | "timeout",
         "seconds": <float>, "detail": "<what happened>"}
      ],
      "errors": [
        {"where": "<instance or phase>", "what": "<precise diagnostic>",
         "hint": "<what a fixer should look at first>"}
      ],
      "environment": {"kind": "docker" | "fallback", "image_or_lock": "<id>"}
    }

## Error-richness rule

Every rejection and every failed instance must produce an `errors[]` entry
specific enough that an agent can debug from the report alone — name the
instance, the observed vs expected behavior, and the first thing to check.
"Validation failed" alone is a contract violation.

## Guard metrics

Guard metrics from `topics.md` (anti-gaming conditions) are enforced here as
rejection rules, not reported as soft warnings.

## Private boundary and manifest

The public launcher and manifest live under `research/validator/`. The scorer
core and private expected values live under
`research/validator/private/`; holdout inputs and labels live under
`research/benchmark/private/`. Both private directories are gitignored,
outside the attempt worktree, and readable only by the validator process.

The manifest records immutable digests without exposing content:

```json
{
  "scorer_hash": "sha256:<hex>",
  "holdout_hash": "sha256:<hex>",
  "sandbox_policy_hash": "sha256:<hex>"
}
```

Attempts and reflection receive aggregate holdout pass/fail, never labels.
Before the validator gate passes, the `env-escape` control must prove that a
candidate process cannot read either private root or open a network
connection. If any forbidden probe succeeds, fail closed and leave the gate
pending.
