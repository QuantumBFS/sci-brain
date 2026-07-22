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

    ## Lessons we learnt
    The core of the reflection. For the top improvement and for every
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

## HTML report (after the markdown)

The markdown above is canonical. After writing it, emit a structured copy
as `docs/discussion/cycle-NN.json` (fields in `report-schema.md` — no
timestamp prefix, NN zero-padded to 2) and render it:

    python3 <skill-dir>/helpers/report.py --cycle NN --dir docs/discussion/

This writes `cycle-NN.html` and regenerates `index.html` (the cross-cycle
view). If the helper exits nonzero it names the bad field — fix the JSON
and re-run; if it still fails, record the error in the reflection md and
continue. The HTML must never block a cycle.
