# STATE.md schema

`<project>/research/STATE.md` is the single source of truth for pipeline
position and loop configuration. Skills update it; humans may edit it.

Template (copy verbatim when initializing a project; `#` lines are guidance,
keep them):

    # Autoresearch State

    - stage: topics            # topics | db | validator | run | done
    - topic: (unset)           # slug of the chosen topic once stage >= db
    - recommended_cycle_size: 10  # planning default chosen during initial setup;
                                  # the agent may adjust each actual cycle by need
    - time_limit_seconds: 300  # hard wall-clock limit per scored run
                               # (default 5 min; user-confirmed, and
                               # adjustable, at the validator stage)
    - authorized_attempts: 0   # attempts the loop may run without user review
    - next_attempt: 1          # next .worktrees/attempt-NNN number
    - next_cycle: 1            # next reflection cycle number
    - gates:
      - survey_gate: pending     # pending | passed YYYY-MM-DD
      - validator_gate: pending  # pending | passed YYYY-MM-DD
    - validator_env: (unset)   # docker | fallback (<reason>)
    - overrides: (none)        # every user-approved protocol deviation, dated

Rules:

- `recommended_cycle_size` is guidance, not a cap or hard batch size. At the
  start of each cycle, the agent chooses and explains the actual cycle size
  based on the useful candidate pool, uncertainty, attempt cost, available
  parallelism, and remaining `authorized_attempts`. A different actual size is
  not a protocol override. It must never exceed the remaining authorization.
- Existing projects with `batch_size` migrate that value to
  `recommended_cycle_size`; do not ask the user to configure it again.
- A gate flips to `passed` only by the stage that owns it (`db`
  for `survey_gate`, `validator` for `validator_gate`), after its
  checklist verifies on disk.
- `overrides:` is append-only. Any deviation from the hard protocol rules must
  be recorded here with a date and reason; skills never deviate silently.
- `attempt-NNN` numbering is zero-padded to 3 digits and never reused, even
  for crashed attempts.
