# Run summary

## Gates

- topics: selected “Robust recovery of microwave Rabi frequency and envelope
  dynamics from a sparse processed population scan.”
- survey gate: passed after five selected, source-grounded insights and three
  reproduced envelope references.
- validator gate: passed after baseline end-to-end scoring and 4/4 strictness
  controls rejected.
- environment: fallback, CPython 3.12.13 plus a hashed macOS Seatbelt policy.

## Attempts

| Attempt | Kind | Change | Development result |
|---|---|---|---:|
| attempt-001 | draft | Gaussian frequency-spread envelope | `4.372371385616318`, scored |
| attempt-002 | draft | exponential envelope | rejected: one population outside `[0,1]` |
| attempt-003 | improve 001 | uncertainty floor `1e-4` → `1e-3` | `4.474516584277779`, scored but worse |

The baseline score was `40.86068140668919`; the best development score was
`4.372371385616318` from attempt-001.

## Sealed adjudication and reflection

The single holdout query was spent on attempt-001. Its aggregate normalized
RMSE was `1.4843925406501801`, versus the frozen holdout baseline
`37.3765738659451`; the non-inferiority bar passed. Labels were never copied
into the reflection or this report.

Cycle reflection:

- the Gaussian envelope was the only primary-metric improvement;
- the unconstrained exponential form was blacklisted because it violated the
  population guard;
- the `1e-3` weighting floor was retained as negative evidence;
- the result supports an effective ensemble frequency-spread model, not a
  unique microscopic coherent-error identification.

## Skill friction found during the run

Four reproducible protocol problems were repaired with regression tests:

1. the Codex installer linked a nonexistent aggregate skill directory;
2. approval handling named a platform-specific UI tool and could not consume
   exact pre-authorization portably;
3. validator-private state and attempt lineage were described but not
   enforceably pinned;
4. an exact pre-approved reference batch still prompted once per cite key.

The real smoke validator also demonstrated why environment failure must remain
fail-closed: `sandbox-exec` cannot be nested inside the Codex outer sandbox,
so the same tests were rerun with explicit permission where the inner policy
could take effect.
