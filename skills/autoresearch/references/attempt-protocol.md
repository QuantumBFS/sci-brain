# Attempt protocol

Every attempt, no exceptions:

1. **Worktree.** `git worktree add .worktrees/attempt-NNN` (NNN from
   `next_attempt` in STATE.md, zero-padded to 3 digits; increment
   immediately; numbers are never reused, even for crashes).
2. **LOG.md first.** Before writing code, create `LOG.md` in the worktree:
   - attempt number and date;
   - **kind** — `draft` | `improve` | `debug` | `baseline`;
   - **parent** — for `improve`/`debug`, the ancestor attempt number this
     builds on (`none` for drafts). Lineage is how later batches know which
     branch a result belongs to;
   - **hypothesis** — the idea being tried, naming which `## Selected`
     insight(s) from `research/INSIGHTS.md` it draws on; for `improve`, the
     single atomic change being made;
   - **mechanism** — for `draft`: the bottleneck removed and the
     effect-size ceiling against the gap to the GOAL.md bar (copied from
     the batch plan); for `improve`/`debug`: inherited from the parent;
     for `baseline`: `n/a (reproduction)`;
   - **prior art** — `none found`, or the citation checked at planning;
   - **expected evidence** — what result would confirm or kill it.
3. **Implement** the candidate in the worktree. It may read dev instances
   and everything in `research/` except `benchmark/private/`. Use
   `validate --precheck` freely while developing — it checks structure and
   format without revealing a score and does not consume anything.
4. **Score** by invoking the validator CLI
   (`validate <worktree> --out <worktree>/report.json`), which enforces
   `time_limit_seconds` and the environment. Nothing else counts as a
   result — no eyeballed timings, no partial credit. `report.json` stays
   in the worktree: it is the machine-readable result of the attempt.
5. **Record outcome** in LOG.md: the validator's JSON summary (score,
   per-instance results, errors), plus what was learned — especially from
   failures. A crash or timeout is recorded as a failed attempt and is
   never silently retried; retrying with a fix is a *new* attempt.
6. **Commit and leave intact.** Commit everything on the worktree's
   `attempt-NNN` branch — the generated code, `LOG.md`, `report.json` —
   and leave the worktree in place. Worktrees are the audit trail:
   reflection reads their LOG.md files, and the cycle-end sync pushes the
   `attempt-NNN` branches to the remote.
