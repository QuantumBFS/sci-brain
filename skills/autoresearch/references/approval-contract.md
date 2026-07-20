# Stage approval contract

Every stage decision is explicit and auditable.

1. Check the current conversation for an exact decision that names the
   selected item or approved configuration.
2. Check `research/APPROVALS.md` when `approval_log:` in `STATE.md` points to
   it. A valid entry records UTC date, stage, decision, scope, and provenance
   (`conversation` or `approval-log`).
3. If the exact decision is already pre-authorized, copy it into the approval
   log and continue without asking again.
4. Otherwise use the platform's available user-input mechanism.
   `AskUserQuestion` is one implementation, not a required tool; plain chat or
   another native picker is valid.
5. Never infer approval from silence, a broad project goal, or approval of a
   different metric or stage.

Changing a recorded decision requires a new append-only entry. Protocol
deviations still belong under `overrides:` in STATE.md; an approval is not an
override.
