---
name: survey
description: User trigger. Use when surveying a research topic into a knowledge base or writing a grounded literature, technology, or field assessment.
---

## Installed resources

Keep the working directory at the user's project. Resolve this `SKILL.md` to its
real path before locating bundled resources. `skills/<name>/...` refers to the
installed skill found by public name, not the user's project; dependencies need
not be siblings. Load only resources needed for the current task. If a required
dependency is missing, report it before that dependent step.


## Choose the mode

- **Explore and build the knowledge base:** run Topic Survey below.
- **Write up an existing survey:** when the user asks to "write up the survey", "write a review", assess a technology/field, or otherwise already has a populated project KB, skip Topic Survey and start at Survey Report.
- **Explore, fetch, and write:** complete Topic Survey, invoke `how-to-download-ref --from-bib`, then continue directly to Survey Report in this same skill when the user wants the write-up.

## Topic Survey

Use the user's topic, constraints, output format, and requested endpoint. Choose
available search tools yourself unless the user has a provider preference. A
web-only workflow is valid when no scholarly MCP is configured.

**Step 1 — Clarify only missing scope.** If the topic and intended output are
clear, proceed. Ask about a substantive uncertainty that would change the search.

**Step 2 — Choose strategies & search.** Select the strategies that address the
question, using the table below as guidance. Offer a choice when the user wants
to steer the search or when competing scopes would produce different reports.
Use independent workers when worthwhile and available, otherwise search
sequentially. Prefer authoritative papers and collect source links.

**Strategy menu:**

| # | Strategy | When to use |
|---|----------|-------------|
| 1 | **Landscape mapping** | First iteration default — broad field overview |
| 2 | **Adjacent subfield** | Deep-dive into a neighboring cluster identified in prior iteration |
| 3 | **Cross-vocabulary** | Abstract away jargon, search other fields for the same structural problem |
| 4 | **Cross-method** | Same problem, different computational or experimental approaches |
| 5 | **Historical lineage** | Who tried before, what failed, what changed since |
| 6 | **Negative results** | Search for papers showing what does not work |
| 7 | **Benchmarks and datasets** | What evaluation infrastructure exists |

Briefly explain the selected search scope when it helps the user assess coverage.

Each worker produces a short **findings report** — key papers found, grouped by sub-theme, with titles and one-line descriptions. No BibTeX yet. **Important:** workers must also collect the DOI and arXiv ID for each paper when visible in search results (e.g., DOIs from publisher URLs, arXiv IDs from arxiv.org links like `2401.12345`). Record these alongside titles in the findings report.

**Step 3 — Consolidate and select.** Merge overlapping results by DOI/arXiv
identity or title, preserving source identifiers and complementary evidence.
For an already scoped KB or report request, choose the relevant papers and
continue. For open-ended exploration with materially different research
directions, present the findings by theme and ask which direction to develop.
Do not require the user to select every paper in an already authorized scope.

**Step 4 — Build KB entries.** For the selected scope, invoke `how-to-build-kb` (read `skills/how-to-build-kb/SKILL.md`) with the picked papers — titles plus every DOI / arXiv ID collected in Steps 2–3 — and the target KB (the project KB `<project>/.knowledge/` by default; `--advisor <slug>` when invoked from `create-advisor`). It verifies every entry against an authoritative source, appends to `$KB/references.bib`, regenerates `INDEX.md`, and writes or extends `NOTES.md`. Never generate BibTeX from memory.

If prior work already covers a proposed idea, explain the overlap and possible distinctions. A neutral survey still reports that prior art; only pause if the user must choose a new research goal.

## After Survey — fetch full text, then optionally write

The discovery stage is done once the KB has its references, `NOTES.md`, and `INDEX.md`. Use `how-to-download-ref` to fetch PDFs and render full-text markdown before writing a source-grounded report.

Include any user-supplied papers relevant to the chosen scope that discovery
missed. Pass the selected IDs, existing cite keys, KB, and source preferences to
`how-to-download-ref`. When a full-text KB or report is requested, fetch the
selected set. A full-text KB request ends with the verified KB and acquisition
status; continue directly to Survey Report only when a report was requested.
Use `--from-bib` for a KB whose
whole bibliography is in scope; in a larger shared KB, pass only the scoped IDs.
For a discovery-only request, deliver the findings and KB artifacts; further
acquisition and reporting are optional.

## Survey Report

Write a self-contained survey or technology/field assessment suitable for internal decision-making or team onboarding. This mode can follow Topic Survey in the same conversation or run directly against an existing project KB.

### Setup

Follow `skills/how-to-technical-writing/SKILL.md` for sentence- and paragraph-level prose rules, and `skills/how-to-write-ideas-report/references/writing-workflow.md` for context loading, **source scoping**, citation handling, gap-filling research, output format, diagrams, and finish checks.

- If no KB exists, build the requested evidence base from the supplied sources or Topic Survey as part of the report task. Ask only if its substantive scope is missing.
- **Scope the source set first.** Run `scope_refs.py` as specified in the shared workflow. Fix dangling anchors before drafting. Build the report's approaches and claims from those scoped keys, not the entire bibliography.
- Check `CLAUDE.md`/`AGENTS.md` for a deliverables-location convention before choosing an output path.
- Tailor technical depth to the user's role from `docs/discussion/user-profile.md` or available context.
- Save to `articles/YYYY-MM-DD-<topic>-review.{md,typ,tex}` or a project-specific path if the user prefers.
- For Typst, start from `skills/survey/template.typ` with `skills/survey/template.bib`. The scaffold provides `stage`, `proscons`, `compare_table`, and `problem_table`; delete unused helpers from the copied document.
- Put only the review date beneath the title. Open with the single **Overview** described below, and end the body with **Open Problems**, followed by references. Do not add a separate scope block, assessment box, or closing "Next step" section.
- Keep the template's dense, restrained layout: a plain title line, 10 pt justified body text, one accent color, and horizontal table rules. `compare_table` and `problem_table` accept custom `headers` and `columns`; choose them together, since a count mismatch fails the compile with a message. Write urgency labels as text. Keep long tables in the page flow so headers repeat across pages, and inspect the rendered result with realistic cell text.
- The heading font can be changed with `--input heading-font="Your installed font"`. For a build using only Typst's bundled fonts, use `--input heading-font="Libertinus Serif"`.

### Gap-filling focus

- Missing SOTA results mentioned in the survey but lacking citations
- Key groups or companies active in the field but not yet referenced
- Approaches or method families that belong in the technical assessment but are not covered
- Results from the last six months that may have superseded older survey entries

### Drafting flow

When the source set comes from an existing, recent `NOTES.md` (the normal case), draft the whole report end-to-end and show the compiled result for one review round. Reserve section-by-section drafting for a cold start where no `NOTES.md` exists and the substance is being composed as you go.

Organize the review **by technical approach**. State of the art and trade-offs live inside each approach, not in separate global sections. Do not add standalone global "Pros and Cons" or "State of the Art" sections.

#### 1. Overview

Write two connected paragraphs for a new reader, without inline labels:

- Define the topic and problem, explain why it matters, and state the report's scope and intended audience. Distinguish it from the prior approach where that helps define the topic.
- State the principal finding and its supporting evidence, then identify the unresolved constraint that motivates the key questions below. Cite the claims.

Include a diagram only when it clarifies the architecture, data flow, or problem framing. Lay approaches side by side only when they solve the same task and are genuinely comparable; otherwise show their relationship or omit the figure.

#### 2. Key Questions

Give one subsection to each subtopic or open question the field is trying to settle (typically 2–5). For each, cover:

- **The question** — one sentence, stated as a question.
- **Why it matters** — what answering it gives: deeper understanding (what it would settle or unify) and/or practical value (what it would enable). Say which applies; a question with neither does not belong in the review.
- **Where it stands** — the best partial answer and its limits, cited.

Questions are ends, not means: do not give them strengths and limitations.

#### 3. Technical Approaches

Identify the main method families (typically 3–6) and give one subsection per approach. Optionally begin with a short field-wide timeline or landscape.

For each approach, cover:

- **What it is** — the defining representation, objective, or mechanism.
- **State of the art** — strongest current results, leading groups, and maturity, each cited. Lead with the best result rather than a chronology.
- **Assessment** — genuine strengths and limitations, with citations. Use the `proscons` two-list style only for competing solutions to the same problem. For complementary capabilities, platform branches, or historical stages, use a short prose assessment instead.

Optionally finish with a cross-approach comparison table when several approaches share meaningful criteria. Choose columns that actually discriminate this field (for example scalability, verifiability/cost, maturity, and best-fit use case). Skip it for a single-approach topic.

#### 4. Open Problems

End with a ranked table of 4–8 problems: number, problem, why it matters, who could solve it, and urgency (Critical / High / Medium). Cite the work that defines each gap or the closest existing result. Do not add business strategy, product fit, or investor sections to the neutral report.

### Visualization guidelines

- Typst: use CeTZ for timelines and dependency diagrams; use native `grid`, `block`, and fixed-width `box()` for text-heavy comparisons and role diagrams. See `skills/how-to-write-ideas-report/references/typst-reference.md`.
- Use a native table for cross-approach comparisons.
- Wrap multiline CeTZ content in a fixed-width box and use string identifiers for `name:`.
- Compile after each figure; every claim in technical and open-problem tables needs at least one citation.

### Optional direction fit

If personalized direction advice was requested, include it after the report. Otherwise it is an optional follow-up, not a required question.

For that advice, load the user's profile (or collect brief background, strengths, assets, and goals if none exists) and recommend 2–4 ranked directions. For each, name the report section/problem, explain the specific fit, give the smallest first experiment, and say what to avoid. Keep this personalized analysis outside the neutral report.
