---
name: how-to-write-ideas-report
description: Agentic trigger. Use when writing a proposal-style ideas report from a finished brainstorm-ideas session or a chosen research direction.
---

## Installed resources

Keep the working directory at the user's project. Resolve this `SKILL.md` to its
real path before locating bundled resources. `skills/<name>/...` refers to the
installed skill found by public name, not the user's project; dependencies need
not be siblings. Load only resources needed for the current task. If a required
dependency is missing, report it before that dependent step.


**Path conventions:** `docs/discussion/` and `articles/` resolve from the **project working directory**; resource paths follow Installed resources above.

# Write an ideas report

Write a structured ideas report after a `brainstorm-ideas` session has converged on a research direction. Invoked by `brainstorm-ideas` at Phase 3 wrap-up, or directly on a past session log. This is an upstream proposal/research-plan artifact, not a manuscript with completed results; redirect field/technology assessments to `survey` report mode and real manuscripts to `write-paper`.

### Setup

Follow `skills/how-to-technical-writing/SKILL.md` for sentence- and paragraph-level prose rules. Follow `skills/how-to-write-ideas-report/references/writing-workflow.md` for context loading, citation handling, gap-filling research, output format, diagrams, and finish checks.

- Primary source: `docs/discussion/*-brainstorm-ideas-log.md`. If multiple logs exist and the request does not identify one, ask which to use.
- If no log exists, use the chosen direction and reasoning already in the conversation or supplied notes. Ask only for substance needed to write the requested report.
- Save to `articles/YYYY-MM-DD-<topic>-ideas-report.{md,typ,tex}` with a matching bibliography when citations are used.
- When entering from `brainstorm-ideas` Phase 3, carry forward the active conversation log, user profile, chosen direction, key references, and concrete action plan without asking the user to repeat them.

### Report structure

With a chosen direction and supporting material, draft the complete report and
verify it before presenting it for review. Use section-by-section feedback only
when the user requests collaborative drafting or an unresolved substantive
choice prevents a coherent draft. Include the relevant parts below:

- **Research Question** — one sentence
- **Novelty Claim** — what is new and why it matters
- **Why Now, Why You** — what changed to make this tractable and the user's specific advantage
- **Cross-field Connections** — unexpected links discovered during brainstorming
- **Proposed Approach** — the method outline
- **Minimum Viable Experiment** — the smallest useful part that can be solved or tested
- **Success Signal** — evidence the problem is truly solved
- **Hope Signal** — evidence it is not solved yet but the approach remains promising
- **Pivot Signal** — evidence the approach fundamentally fails and should be abandoned or changed
- **Open Risks** — unresolved uncertainties
- **Target Venue**
- **Key References** — verified entries from the active KB; save the matching `.bib`

### Diagrams and final look-back

Use a diagram when it makes an abstract structure easier to critique: reductions, relationships between methods, pipelines, data flow, architecture, or meaningful before/after comparisons. After drafting, apply Polya's "Looking Back": can the result be derived another way, used for another problem, and understood at a glance? Then run the shared workflow's compile, citation, and bibliography checks.
