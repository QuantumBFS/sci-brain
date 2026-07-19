# Attempt protocol

Every attempt, no exceptions:

1. **Worktree.** `git worktree add .worktrees/attempt-NNN` (NNN from
   `next_attempt` in STATE.md, zero-padded to 3 digits; increment
   immediately; numbers are never reused, even for crashes).
2. **LOG.md first.** Before writing code, create `LOG.md` in the worktree:
   - attempt number and date;
   - **hypothesis** — the idea being tried, naming which `## Selected`
     insight(s) from `research/INSIGHTS.md` it draws on;
   - **expected evidence** — what result would confirm or kill it.
3. **Implement** the candidate in the worktree. It may read dev instances
   and everything in `research/` except `benchmark/private/`.
4. **Score** by invoking the validator CLI (`validate <worktree>`), which
   enforces `time_limit_seconds` and the environment. Nothing else counts
   as a result — no eyeballed timings, no partial credit.
5. **Record outcome** in LOG.md: the validator's JSON summary (score,
   per-instance results, errors), plus what was learned — especially from
   failures. A crash or timeout is recorded as a failed attempt and is
   never silently retried; retrying with a fix is a *new* attempt.
6. **Leave the worktree intact.** Worktrees are the audit trail; reflection
   reads their LOG.md files.
