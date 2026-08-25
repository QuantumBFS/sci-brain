# Stage 4: Run (the loop)

The loop. Protocol per attempt: `../attempt-protocol.md`. Report per
cycle: `../reflection-template.md`. Configuration from
`research/STATE.md`: `recommended_cycle_size`, `time_limit_seconds`,
`authorized_attempts`, `next_attempt`, `next_cycle`.

## Entry check — refuse to start otherwise

Both `survey_gate` and `validator_gate` must read `passed` in
`research/STATE.md`, and their artifacts must verify on disk (CATALOG.md,
INSIGHTS.md `## Selected`, validator manifest with self-test results). If
not, refuse and route back through the `autoresearch` dispatcher. A missing
gate is never worked around; a user-approved exception goes into
`overrides:` in STATE.md first.

## Hard rules (non-negotiable during the loop)

1. Every attempt in its own `.worktrees/attempt-NNN/` with a `LOG.md`.
2. Every scored run goes through the validator CLI; nothing else counts.
3. Hard wall-clock limit `time_limit_seconds` on every scored run.
4. Holdout labels never enter design context — only aggregate validator
   output.
5. Crashes/timeouts are recorded failures, never silently retried.

## Cycle

0. **Stuck?** Skip on cycle 1. **Stuck** means either (a) after the
   novelty and triviality checks of the previous planning pass the pool
   held fewer useful drafts + improvements than that cycle's initial
   target — the `cycle_size` it started from in step 1 (normally
   `recommended_cycle_size`) *before* any reduction made because the pool
   was thin — or (b) two consecutive cycles produced no improvement in
   best dev score. Shrinking `cycle_size` to fit a thin pool does not
   clear condition (a); the cycle still counts as stuck. When
   stuck, refresh insights before planning:
   - take the diagnosed bottleneck / root cause from the latest
     reflection report;
   - invoke the `survey` skill scoped to that bottleneck (or
     `download-ref` for specific IDs already known) into
     `<project>/.knowledge/`;
   - distill what is new into `research/INSIGHTS.md` under `## Candidate`
     (entry format per `../insights-template.md`). Candidate entries are
     valid grounding for hypotheses immediately — the loop is not blocked
     on user confirmation; they are promoted to Selected or moved to
     Shelved at the next soft gate;
   - record the refresh (query, what was added, what it unblocked) in this
     cycle's reflection report.
   At most one refresh per cycle. Skip the refresh when the previous
   reflection's TODO check already covered the diagnosed bottleneck —
   reuse its findings instead of re-running the same query.
   If a refresh adds nothing and the loop
   is still stuck, the next soft gate presents "wind down / pivot" as a
   direction instead of spending more attempts.
1. **Plan the cycle.** Start from `recommended_cycle_size`, then choose the
   actual `cycle_size` for this cycle. Adjust it when the remaining authorized
   budget is smaller, the post-filter candidate pool is unusually thin or
   rich, attempts are unusually expensive, uncertainty favors a shorter
   feedback loop, or independent hypotheses make more parallel work useful.
   State the chosen size and the reason in the plan. This is agent judgment,
   not a protocol override; never exceed remaining `authorized_attempts`.

   Generate a surplus of candidate hypotheses (~2× `cycle_size`). `## Selected` entries in `research/INSIGHTS.md` are the
   default grounding, not a fence — `## Candidate` entries (from a
   stuck-triggered refresh, step 0), original ideas, cross-insight
   combinations, and directions from fresh literature search are equally
   welcome; each hypothesis names its source (insight / literature /
   original) in the plan.

   Every **draft** hypothesis must also carry two lines, written before
   it is ranked:
   - **mechanism** — the bottleneck it removes (named from the latest
     reflection's root-cause diagnosis where one exists) and a rough
     effect-size ceiling, stated against the **gap** = GOAL.md threshold −
     current best dev score. "Might help" is not a mechanism.
   - **prior art** — checked against `.knowledge/INDEX.md` +
     `research/INSIGHTS.md` and one quick web search: `none found`, or a
     citation. If the technique is already published *for this problem*,
     the hypothesis is relabeled kind `baseline` (below) — it never
     counts as a draft.
   `improve` and `debug` attempts inherit their ancestor's mechanism and
   state only the atomic change.

   Rank candidates by **expected gap closure × distinctness**. Cost is a
   constraint (the attempt must fit `time_limit_seconds`), never a score
   term — ranking on cost is how cheap tweaks crowd out real ideas.
   Promote the top `cycle_size` after three filters. If the filters leave
   fewer genuinely useful candidates, reduce `cycle_size` instead of padding
   the cycle with weak or duplicate work:
   - **Novelty check** — compare each candidate against the hypotheses in
     *all* prior attempts' LOG.md files; a near-duplicate of anything
     already tried is rejected and resampled. Never re-spend an attempt on
     a restated old idea.
   - **Triviality check** — a draft is rejected and resampled if its
     mechanism cannot plausibly close a measurable fraction of the gap
     (say why in one line); if it is a parameter, config, or constant
     change (those are only ever `improve` on a scored ancestor); or if
     its prior art is a published application to this problem and it was
     not relabeled `baseline`.
   - **Batch composition** — mix *drafts* (genuinely different approaches)
     with *improvements* (exactly one atomic change to the best-scoring
     known-good ancestor, so the change's effect is measurable), at most
     2 *debug* attempts on a promising-but-broken branch, and at most one
     *baseline* per batch (a reproduction of a published technique,
     scored like any attempt; allowed only while no scored baseline for
     that technique exists in any prior LOG.md). A failing branch that
     exhausts its debug cap is abandoned, not nursed.
   Scope the planning context: drafts see a digest of *sibling* attempts
   (what was tried, what it scored — do something different); improvements
   and debugs see their *ancestral* chain (avoid undo-redo loops). Feed
   forward the failure artifacts (validator `errors[]`, stderr) of the
   previous batch — failures are data.
2. **Confirm the plan.** The first batch of any authorization — cycle 1
   especially — executes only after the user confirms the plan: present
   the promoted hypotheses (one line each: kind, source, mechanism, prior
   art), the chosen `cycle_size` with any deviation from the recommendation,
   and the batch composition; apply any amendments, then start. Later cycles within the
   same authorization run autonomously — their direction was confirmed at
   the previous soft gate alongside the attempts budget.
3. **Execute** each attempt per `../attempt-protocol.md`.
4. **Reflect.** Write `docs/discussion/YYYY-MM-DD-HHMMSS-cycle-NN.md` per
   `../reflection-template.md`, then emit `cycle-NN.json`
   (`../report-schema.md`) and render the HTML report with
   `../../helpers/report.py` (non-fatal on failure — the md is canonical);
   increment `next_cycle`.
   After every cycle, also run
   `../../helpers/gen_campaign.py --dir docs/discussion/ [--records "..."]`
   to refresh `campaign.html` — one page listing every attempt across all
   cycles (per-cycle summary + complete table with LOG links). If a campaign
   has worktree-only attempts outside the cycle JSON, record them in a
   project-owned JSON array and pass `--extra <path>`; never hard-code campaign
   data into the shared helper. Non-fatal on failure, like `report.py`.

   The report's last section before **Next round** is
   **TODO — worth checking** (see the template): mark the open questions this cycle
   surfaced that `.knowledge/` and INSIGHTS.md cannot answer, then check
   them now — invoke the `survey` skill scoped to those items (or
   `download-ref` for known IDs) into `<project>/.knowledge/`, distill
   what is new into `research/INSIGHTS.md` under `## Candidate`, and
   record under each item what the check found or that it `remains open`.
   Only after the TODO checks, write **Next round**.

   Before writing **Next round**, perform a deliberate recommendation pass —
   do not stop at the first plausible continuation. Re-read the gap to the
   GOAL.md bar, every lesson and root-cause confidence, per-instance evidence,
   the cumulative blacklist, relevant INSIGHTS/CATALOG entries, the literature
   check, the TODO check findings, and attempt cost. Generate 4–6 materially distinct candidates, remove
   anything contradicted by evidence, already tried, weak against the diagnosed
   bottleneck, or merely a parameter tweak, then rank the survivors by expected
   gap closure × distinctness (cost remains a constraint). Put the best 2–4 in
   the report and explicitly recommend the top choice. For each direction give:
   the falsifiable mechanism, a 2–3 sentence justification of the intuition
   (the specific evidence behind it) and the value (what it buys if it works),
   its relation to prior art and prior attempts, the first discriminating
   attempt, and the result that would support or kill it. If wind-down/pivot ranks first,
   say so honestly rather than manufacturing another experiment.

   Dev-score
   selection overfits over long runs: if the holdout query budget in the
   validator manifest allows, adjudicate the cycle's top candidate on the
   holdout (aggregate result only) and record it.
5. **Sync.** Commit the cycle's artifacts to the main branch — the
   reflection md/json/html, `index.html`, `campaign.html`, STATE.md, any INSIGHTS.md
   changes, and the validator manifest (holdout query log) — then, when a
   remote is configured, push main plus every `attempt-NNN` branch from
   this cycle (each carries its generated code, `LOG.md`, and
   `report.json`, committed per the attempt protocol). This preserves the
   AI-generated code and results off-machine after every cycle. Never
   push `research/benchmark/private/` — it stays gitignored, and holdout
   results appear only as aggregates in the reports. No remote → recommend
   the user add one, record the skip in the reflection, continue.
6. **Soft gate.** Subtract the cycle's attempts from `authorized_attempts`:
   - if any remain, continue autonomously; choose the next cycle's actual size
     again from the recommendation, evidence, and remaining authorization;
   - if exhausted: stop and present the report — summarize in the
     terminal and point the user at `docs/discussion/cycle-NN.html` and
     `index.html` — followed by the same **2–4 ranked directions** from the
     report, not a newly improvised list. State which one the agent recommends
     and why it outranks the alternatives. The user decides
     both **which direction(s)** to pursue and **how many attempts** to
     authorize (a number; 0 = stop; the user's own directions and
     amendments welcome as free text). Attempts are the unit the user
     authorizes; never ask them to reason in rounds or cycles — those are
     internal bookkeeping. Insight promotions proposed in the report — including every
     `## Candidate` entry added by a refresh (promote to Selected or move
     to Shelved) — are confirmed here.

## Termination

When the validator reports the GOAL.md bar met on dev instances, run
`validate --instances holdout` once, report both results, set
`stage: done`, and hand off to the user — write-up is out of scope for this
skill (use paper-writer).
