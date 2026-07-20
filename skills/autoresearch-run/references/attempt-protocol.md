# Attempt protocol

Every attempt, no exceptions:

1. **Resolve lineage and create the worktree.** NNN comes from `next_attempt`
   in STATE.md, zero-padded to 3 digits; increment it immediately and never
   reuse a number, even for crashes. Resolve `<parent-ref>` before creation:
   - `draft` → `baseline_commit` from STATE.md;
   - `improve` → **result commit** of the named successful parent attempt;
   - `debug` → **result commit** of the named failed parent attempt.

   Verify the ref exists, then run
   `git worktree add -b autoresearch/attempt-NNN .worktrees/attempt-NNN <parent-ref>`.
2. **LOG.md first.** Before writing code, create `LOG.md` in the worktree:
   - attempt number and date;
   - **kind** — `draft` | `improve` | `debug`;
   - **parent** — for `improve`/`debug`, the ancestor attempt number this
     builds on (`none` for drafts). Lineage is how later batches know which
     branch a result belongs to;
   - **base commit** — the resolved full SHA of `<parent-ref>`;
   - **result commit** — initially `(pending)`;
   - **hypothesis** — the idea being tried, naming which `## Selected`
     insight(s) from `research/INSIGHTS.md` it draws on; for `improve`, the
     single atomic change being made;
   - **expected evidence** — what result would confirm or kill it.
3. **Implement** the candidate in the worktree. It may read dev instances
   and public research artifacts, but neither `benchmark/private/` nor
   `validator/private/`. Use
   `validate --precheck` freely while developing — it checks structure and
   format without revealing a score and does not consume anything.
4. **Score** by invoking the validator CLI (`validate <worktree>`), which
   enforces `time_limit_seconds` and the environment. Nothing else counts
   as a result — no eyeballed timings, no partial credit.
5. **Record outcome and commits** in LOG.md: the validator's JSON summary (score,
   per-instance results, errors), plus what was learned — especially from
   failures. A crash or timeout is recorded as a failed attempt and is
   never silently retried; retrying with a fix is a *new* attempt. For a
   completed candidate:
   - commit candidate code plus the outcome log;
   - capture that SHA as the **result commit** used by descendants;
   - replace `(pending)` in LOG.md with the captured SHA and make a second,
     log-only audit commit.

   If no candidate commit exists because the attempt crashed before
   implementation, set **result commit** to `(none—crashed)` and commit the
   audit log only.
6. **Leave the worktree intact.** Worktrees are the audit trail; reflection
   reads their LOG.md files.
