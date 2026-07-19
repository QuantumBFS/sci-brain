# Reflection report template

One report per cycle: `docs/discussion/YYYY-MM-DD-HHMMSS-cycle-NN.md`
(timestamp UTC, NN from `next_cycle`). Modeled on the code-distance ideas
logs. Required sections:

    # Cycle NN reflection — attempts AAA–BBB

    ## Yield
    Honest denominators, always: "K of N attempts improved the primary
    metric; best <value> vs prior best <value>." Per attempt, one line:
    kind (draft/improve/debug), parent, metric, and a one-line causal claim.
    Rank which single change mattered most — that ranking targets the next
    batch's improvements.

    ## Evidence carried forward
    What the batch established, with numbers from validator reports and
    LOG.md files. Failures are evidence: say what each rules out — keep a
    running blacklist of dead approaches with reasons, so no later batch
    retries them. Name the standing risk explicitly: dev-set score can
    improve while holdout performance does not; note whether a budgeted
    holdout adjudication was spent this cycle and what it said.

    ## Literature check
    Re-check the moves against `.knowledge/` and, when needed, fresh search:
    has someone done this; is the emerging claim still novel; do any Shelved
    insights now look relevant?

    ## Decision
    The next batch's research hypothesis (falsifiable, one paragraph), the
    planned attempts sketched in one line each, and what would make this
    direction abandoned. If proposing to promote Shelved insights or distill
    new ones, list them here for user confirmation at the gate.

    ## State
    Attempts used / remaining this authorization; bar status (distance to
    GOAL.md threshold); any protocol overrides recorded this cycle.
