# INSIGHTS.md template

`<project>/research/INSIGHTS.md` holds the distilled "skills to propose new
ideas". Two sections: `## Selected` (entries the run loop may draw on) and
`## Shelved` (distilled but not selected; promotable at a cycle gate).

Entry format — one `###` per insight area, all four lines required:

    ## Selected

    ### <insight area, e.g. "Branch-and-bound with algebraic lower bounds">
    - **Technique**: the transferable idea, stated so it can be applied to a
      new attempt without rereading the paper.
    - **Applies when**: preconditions — problem structure, size regime, data
      available.
    - **Limits**: where it breaks down, known failure modes, complexity walls.
    - **Sources**: citation keys from ref.bib, e.g. [smith2025exact].

    ## Shelved

    ### <insight area>
    - ... same four lines ...

Rules:

- Every entry's **Sources** must cite at least one reference present in
  `.knowledge/INDEX.md` — no from-memory insights.
- Moving an entry between Selected and Shelved is a user decision, made
  during stage 3 selection or at a run-loop cycle gate; record the date in
  the entry when moved.
