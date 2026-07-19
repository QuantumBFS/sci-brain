# STATE.md schema

`<project>/research/STATE.md` is the single source of truth for pipeline
position and loop configuration. Skills update it; humans may edit it.

Template (copy verbatim when initializing a project; `#` lines are guidance,
keep them):

    # Autoresearch State

    - stage: topics            # topics | db | validator | run | done
    - topic: (unset)           # slug of the chosen topic once stage >= db
    - batch_size: 10           # attempts per cycle
    - time_limit_seconds: 300  # hard wall-clock limit per scored run
    - authorized_rounds: 0     # cycles the loop may run without user review
    - next_attempt: 1          # next .worktrees/attempt-NNN number
    - next_cycle: 1            # next reflection cycle number
    - gates:
      - survey_gate: pending     # pending | passed YYYY-MM-DD
      - validator_gate: pending  # pending | passed YYYY-MM-DD
    - validator_env: (unset)   # docker | fallback (<reason>)
    - overrides: (none)        # every user-approved protocol deviation, dated

Rules:

- A gate flips to `passed` only by the skill that owns it (`autoresearch-db`
  for `survey_gate`, `autoresearch-validator` for `validator_gate`), after its
  checklist verifies on disk.
- `overrides:` is append-only. Any deviation from the hard protocol rules must
  be recorded here with a date and reason; skills never deviate silently.
- `attempt-NNN` numbering is zero-padded to 3 digits and never reused, even
  for crashed attempts.
