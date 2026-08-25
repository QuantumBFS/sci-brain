# Reflection report template

One report per cycle: `docs/discussion/YYYY-MM-DD-HHMMSS-cycle-NN.md`
(timestamp UTC, NN from `next_cycle`). Modeled on the code-distance ideas
logs. Four sections — review the facts, diagnose the causes, check the
open questions, plan the action. Required structure:

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

    ## TODO — worth checking
    Mark, then check — the last section written before Next round. List
    what this cycle surfaced that `.knowledge/` and INSIGHTS.md cannot
    yet answer: an unexplained result, a suspected root cause that needs
    prior art, a technique someone may already have published, a Shelved
    insight that may have become relevant. One line per item — what to
    check and why it matters to the gap. Then resolve the list now:
    invoke the `survey` skill scoped to the items (or `download-ref` for
    specific known IDs) into `<project>/.knowledge/`, distill anything
    new into `research/INSIGHTS.md` under `## Candidate`, and record
    under each item what the check found. An item too large to settle
    this cycle is marked `remains open` and carried into the next
    cycle's TODO. No open questions is stated explicitly ("nothing worth
    checking this cycle" — rare after an honest lessons pass), never
    silently omitted. Next round is written only after these checks, so
    the ranked directions can build on what they surfaced.

    ## Next round
    Think hard before recommending: compare the goal gap, root-cause
    diagnoses and their confidence, per-instance evidence, cumulative
    blacklist, relevant insights/catalog entries, literature check, TODO
    check findings, and attempt cost. Generate 4–6 materially distinct candidates, reject those
    already tried or contradicted by evidence, then rank the best **2–4
    promising directions** by expected gap closure × distinctness (with cost
    as a constraint). Do not pad the list with cosmetic variants.

    For every ranked direction include:
    - **Hypothesis and mechanism** — falsifiable, against the current gap.
    - **Why promising** — 2–3 sentences justifying the intuition and the
      value. First the intuition: what makes this mechanism likely to work
      here, named from a specific lesson, root cause, validator number, or
      prior-art result (not "worth trying"). Then the value: what it buys
      if it works — roughly how much of the gap it closes, or what
      competing explanation it kills.
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

## Report style

Write like a lab notebook, not a press release. The report is read by the
next planning pass and by the user deciding where to spend attempts, so
every sentence must hand them a fact, a number, or a decision.

- Numbers over adjectives. Never "improved significantly"; write the
  measured delta. A claim with no number and no citation is cut or marked
  *suspected*.
- Plain words, active voice. "We varied chi", not "chi was varied"; "use",
  not "leverage"; no "delve", "showcase", "landscape", "pivotal",
  "crucial".
- One idea per sentence. If a sentence needs a second read, split it.
- Have opinions. Say which result surprised you and which number you
  distrust, and why. A neutral list of pros and cons hides the diagnosis.
- Cut filler and stacked hedges. "It is important to note that" says
  nothing; "could potentially possibly" collapses to "may".
- Specific beats generic. A sentence that could appear unchanged in
  another project's report says nothing about this one; delete it.

## HTML report (after the markdown)

The markdown above is canonical. After writing it, emit a structured copy
as `docs/discussion/cycle-NN.json` (fields in `report-schema.md` — no
timestamp prefix, NN zero-padded to 2) and render it:

    python3 <skill-dir>/helpers/report.py --cycle NN --dir docs/discussion/

This writes `cycle-NN.html` (one raw primary-score point per scored attempt in
this cycle, with no cumulative headline KPIs; reference lines show the current
best and, when defined, the target; an optional `score_formula` note sits above
the plot) and regenerates `index.html` (the
cross-cycle trajectory). Then refresh the complete attempt inventory:

    python3 <skill-dir>/helpers/gen_campaign.py --dir docs/discussion/

This writes `campaign.html`, linked from `index.html`. Use `--extra <path>`
only for a project-owned JSON array of attempts that are not represented in
any cycle JSON. If either helper exits nonzero, fix the named field and re-run;
if it still fails, record the error in the reflection md and continue. HTML
generation must never block a cycle.
