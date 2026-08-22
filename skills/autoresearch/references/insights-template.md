# INSIGHTS.md template

`<project>/research/INSIGHTS.md` holds the distilled "skills to propose new
ideas". Three sections: `## Selected` (entries the run loop draws on by
default), `## Candidate` (added by a stuck-triggered insight refresh during
the run stage; usable immediately, promoted or shelved at the next soft
gate), and `## Shelved` (distilled but not selected; promotable at a cycle
gate). `## Candidate` may be absent until the first refresh.

Entry format — one `###` per insight area, all four lines required:

    ## Selected

    ### <insight area, e.g. "Branch-and-bound with algebraic lower bounds">
    - **Technique**: the transferable idea, stated so it can be applied to a
      new attempt without rereading the paper.
    - **Applies when**: preconditions — problem structure, size regime, data
      available.
    - **Limits**: where it breaks down, known failure modes, complexity walls.
    - **Sources**: citation keys from references.bib, e.g. [smith2025exact].

    ## Candidate

    ### <insight area>
    - ... same four lines, plus **Added**: cycle NN refresh, YYYY-MM-DD ...

    ## Shelved

    ### <insight area>
    - ... same four lines ...

Rules:

- Every entry's **Sources** must cite at least one reference present in
  `.knowledge/INDEX.md` — no from-memory insights.
- Moving an entry between Selected and Shelved is a user decision, made
  during db-stage selection or at a run-loop soft gate; record the date in
  the entry when moved.
