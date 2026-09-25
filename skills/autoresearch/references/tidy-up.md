# Tidy up (pause a campaign, keep everything that matters)

Tidy-up is not an end state. It packs every attempt into its own branch,
removes the worktree directories, and writes one index so the campaign can be
resumed later, by anyone, on any machine that has the branches. Enter it
when the user asks to tidy, pause, or close a campaign, or answers `0` at a
soft gate and wants the workspace cleaned.

Hard rules: no new attempts, no holdout query, no edits to any attempt's
code or LOG.md, and never describe local commits as a backup.

## Procedure

1. **Inventory (read-only).** Run from the project root; the helper path is
   relative to this file's installed skill directory:

   ```sh
   python3 ../helpers/tidy_attempts.py inventory --json research/.tidy-inventory.json
   ```

   It prints the remote, the counts per decision, the empty worktrees it will
   drop, and only the `ask` rows. The full table is in the JSON. Decisions:
   - **keep** — has a LOG.md, a `report.json`, or code changes. Also every
     branch that no longer has a worktree.
   - **drop** — an empty worktree: no log, no report, no commits, no changes.
     Nothing is lost by deleting it.
   - **ask** — changes but no LOG.md (an attempt that skipped the protocol),
     or an untracked file over 10 MB that matches no build-artifact pattern.
2. **Apply the clear cases first.** Do not ask about them; with a hundred
   attempts most rows are obvious.

   ```sh
   python3 ../helpers/tidy_attempts.py apply --from research/.tidy-inventory.json
   ```

   For each kept worktree this appends the detected artifact patterns
   (`__pycache__/`, `build/`, `*.so`, …) to its `.gitignore`, commits
   everything else on its `attempt-NNN` branch, pushes when a remote exists,
   and removes the worktree directory. Dropped worktrees and their branches are
   deleted. `ask` rows are left untouched. Push failures are printed as
   warnings and the run continues; report them.
3. **One question for the rest.** Group the `ask` rows by reason and ask once,
   with a recommended default per group: attempts without a LOG.md are
   usually worth keeping if they have commits and dropping if they only have
   scratch edits; large files are usually results worth keeping or artifacts
   worth ignoring. Accept per-id overrides in free text. Then re-run `apply`
   on the same snapshot with `--drop <ids>` and `--keep <ids>`; rows handled
   in the first pass are skipped. To keep an attempt but not a large file,
   add the file to that worktree's `.gitignore` before the second pass.
4. **Record.**

   ```sh
   python3 ../helpers/tidy_attempts.py record --from research/.tidy-inventory.json
   ```

   Writes `research/ATTEMPTS.md`: the STATE.md position, one row per attempt
   (kind, parent, validator status and score, branch, disposition
   `pushed` / `local only` / `dropped`, hypothesis), and how to resume. Dropped
   rows keep their hypothesis and outcome from the snapshot. With no remote the
   file opens with a local-only warning and the two ways to fix it (add a
   remote and push, or copy a `git bundle --all` off the machine).
5. **State and sync.** Set `last_tidy: YYYY-MM-DD` in `research/STATE.md`,
   leave `stage` as it is, commit `ATTEMPTS.md` and `STATE.md` on main, push
   main when a remote exists, and delete `research/.tidy-inventory.json`.
   Tell the user the counts, the warnings, and whether the branches are off
   the machine.

## Resuming

A status request reports the last tidy date and the counts from
`ATTEMPTS.md`. To continue, the user authorizes attempts at the soft gate as
usual; the loop keeps numbering from `next_attempt`. Any kept attempt is
restored with `git worktree add .worktrees/attempt-NNN attempt-NNN` when a
new attempt needs to build on it.
