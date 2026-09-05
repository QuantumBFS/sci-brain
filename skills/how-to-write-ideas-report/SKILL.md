---
name: how-to-write-ideas-report
description: Agentic trigger. Use when writing a proposal-style ideas report from a finished brainstorm-ideas session or a chosen research direction.
---

## Installed resources

Keep the working directory at the user's project. Resolve this loaded `SKILL.md`
with `Path(path).resolve()` before locating resources; follow symlinks. Bare
`helpers/`, `references/`, and template paths are relative to that real skill
directory. A path written as `skills/<name>/...` means the installed `<name>`
skill's directory from the agent's skill catalog, not a path in the user's project.
Locate each dependency by its public skill name; copied skills need not be siblings.
If a dependency is absent, report the missing skill and install it before that step.
Shared writing files are bundled in `how-to-write-ideas-report/references/`.


**Path conventions:** `docs/discussion/` and `articles/` resolve from the **project working directory**; resource paths follow Installed resources above.

# Write an ideas report

Write a structured ideas report after a `brainstorm-ideas` session has converged on a research direction. Invoked by `brainstorm-ideas` at Phase 3 wrap-up, or directly on a past session log. This is an upstream proposal/research-plan artifact, not a manuscript with completed results; redirect field/technology assessments to `survey` report mode and real manuscripts to `write-paper`.

### Setup

Follow `skills/how-to-write-ideas-report/references/writing-workflow.md` for context loading, citation handling, gap-filling research, output format, diagrams, and finish checks.

- Primary source: `docs/discussion/*-brainstorm-ideas-log.md`. If multiple logs exist and the request does not identify one, ask which to use.
- If no log exists, ask the user to brainstorm first or describe the chosen direction and reasoning to preserve.
- Save to `articles/YYYY-MM-DD-<topic>-ideas-report.{md,typ,tex}` with a matching bibliography when citations are used.
- When entering from `brainstorm-ideas` Phase 3, carry forward the active conversation log, user profile, chosen direction, key references, and concrete action plan without asking the user to repeat them.

### Report structure

Draft each section, show it, and incorporate feedback:

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
