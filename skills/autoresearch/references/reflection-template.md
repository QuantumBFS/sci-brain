# Reflection report template

One report per cycle: `docs/discussion/YYYY-MM-DD-HHMMSS-cycle-NN.md`
(timestamp UTC, NN from `next_cycle`). Modeled on the code-distance ideas
logs. Three sections — review the facts, diagnose the causes, plan the
action. Required structure:

    # Cycle NN reflection — attempts AAA–BBB

    ## Review — what we did
    Facts only, no interpretation. Honest denominators, always: "K of N
    attempts improved the primary metric; best <value> vs prior best
    <value>." Per attempt, one line: kind (draft/improve/debug), parent,
    metric, and a one-line causal claim. Close with the budget state:
    attempts used / remaining this authorization, distance to the GOAL.md
    bar, the actual cycle size and why it differed from
    `recommended_cycle_size` (if it did), and any protocol overrides recorded
    this cycle.

    ## Lessons we learnt
    The core of the reflection — what happened and why, down to root
    cause. For the top improvement and for every
    failed or flat branch, one lesson: a why-chain down to an actionable
    root cause —
    - **Observation** — what happened (score moved / didn't / crashed).
    - **Root cause** — the mechanism. A score is a *result*, not a cause;
      "it performed worse" or "the idea didn't work" is a restated
      observation. Keep asking why until the answer names something you
      could act on or test (a wrong assumption in the hypothesis, a
      bottleneck the change didn't touch, a bug class, an insight that
      doesn't transfer to this regime).
    - **Evidence** — what supports that cause: validator `errors[]`,
      per-instance results, LOG.md observations. Mark the cause
      *confirmed* (evidence pins it) or *suspected* (best explanation;
      say what would confirm it).
    - **Implication** — what this changes for the search: blacklist
      entry, revised assumption, debug target, or promoted direction.
    Rank which single change mattered most — that ranking targets the
    next batch's improvements.
    Also record findings that are off-topic but maybe worth publishing,
    or may lead to a significant result — an unexpected pattern in the
    data, a surprising method behavior, a side result with standalone
    value. One entry each, marked *off-goal* so they inform without
    steering the next batch.

    ### Evidence carried forward
    What the batch established, with numbers from validator reports and
    LOG.md files. Failures are evidence: say what each rules out — keep a
    running blacklist of dead approaches with reasons, so no later batch
    retries them. Name the standing risk explicitly: dev-set score can
    improve while holdout performance does not; note whether a budgeted
    holdout adjudication was spent this cycle and what it said.

    ### Literature check
    Re-check the moves against `.knowledge/` and, when needed, fresh
    search: has someone done this; is the emerging claim still novel; do
    any Shelved insights now look relevant?

    ## Next round
    Think hard before recommending: compare the goal gap, root-cause
    diagnoses and their confidence, per-instance evidence, cumulative
    blacklist, relevant insights/catalog entries, literature check, and
    attempt cost. Generate 4–6 materially distinct candidates, reject those
    already tried or contradicted by evidence, then rank the best **2–4
    promising directions** by expected gap closure × distinctness (with cost
    as a constraint). Do not pad the list with cosmetic variants.

    For every ranked direction include:
    - **Hypothesis and mechanism** — falsifiable, against the current gap.
    - **Why promising** — the specific lesson, root cause, validator evidence,
      or prior art that supports it; reasons such as "worth trying" are not
      sufficient.
    - **Novelty / relation to attempts** — why it is not a repeat and what it
      borrows or rejects from prior work.
    - **First discriminating attempt** — the cheapest attempt that separates
      this explanation from alternatives.
    - **Decision signal** — what result would strengthen it, kill it, or force
      a pivot.

    End with **Recommendation:** name the top direction and explain why it
    outranks the alternatives now. A well-supported wind-down/pivot is a valid
    recommendation. If proposing to promote Shelved insights or distill new
    ones, list them here for user confirmation at the gate.

## HTML report (after the markdown)

The markdown above is canonical. After writing it, emit a structured copy
as `docs/discussion/cycle-NN.json` (fields in `report-schema.md` — no
timestamp prefix, NN zero-padded to 2) and render it:

    python3 <skill-dir>/helpers/report.py --cycle NN --dir docs/discussion/

This writes `cycle-NN.html` (one raw primary-score point per scored attempt in
this cycle, with no cumulative headline KPIs; reference lines show the current
best and, when defined, the target) and regenerates `index.html` (the
cross-cycle trajectory). Then refresh the complete attempt inventory:

    python3 <skill-dir>/helpers/gen_campaign.py --dir docs/discussion/

This writes `campaign.html`, linked from `index.html`. Use `--extra <path>`
only for a project-owned JSON array of attempts that are not represented in
any cycle JSON. If either helper exits nonzero, fix the named field and re-run;
if it still fails, record the error in the reflection md and continue. HTML
generation must never block a cycle.
