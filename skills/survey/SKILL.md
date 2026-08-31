---
name: survey
description: User trigger. Use when surveying a research topic into a knowledge base or writing a grounded literature, technology, or field assessment.
---

## Choose the mode

- **Explore and build the knowledge base:** run Topic Survey below.
- **Write up an existing survey:** when the user asks to "write up the survey", "write a review", assess a technology/field, or otherwise already has a populated project KB, skip Topic Survey and start at Survey Report.
- **Explore, fetch, and write:** complete Topic Survey, invoke `how-to-download-ref --from-bib`, then continue directly to Survey Report in this same skill when the user wants the write-up.

## Topic Survey

Before starting this mode, check which MCP servers are available (arxiv, paper-search, Semantic Scholar, Sci-Hub, etc.). Present the detected servers to the user and let them choose which ones to use for this session (multi-select in chat). If none are configured, warn the user that the survey will rely on web search only.

If the user already provided a research topic or question, skip the clarification step.

**Step 1 — Clarify.** Ask one question to narrow the research topic. Give 2-4 choice options.

**Step 2 — Pick strategies & search.** Present the strategy menu to the user as a multi-select question. Recommend 3-4 strategies based on the topic context, but let the user choose. Then run one search worker per selected strategy in parallel when available, or sequentially otherwise. Each worker uses **broad web search only** at this stage — fast and exploratory.

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

When presenting to the user, briefly explain why you recommend each strategy for their specific topic (e.g., "Cross-vocabulary recommended because your problem — buffering stochastic supply — appears in operations research and hydrology too").

Each worker produces a short **findings report** — key papers found, grouped by sub-theme, with titles and one-line descriptions. No BibTeX yet. **Important:** workers must also collect the DOI and arXiv ID for each paper when visible in search results (e.g., DOIs from publisher URLs, arXiv IDs from arxiv.org links like `2401.12345`). Record these alongside titles in the findings report.

**Step 3 — Consolidate & user picks directions.** Main agent consolidates all findings reports. **Deduplicate** papers that appear in multiple strategy reports — match by title similarity or DOI. Merge their descriptions (keep the richer one), **preserve any DOIs and arXiv IDs collected** during Step 2, and note which strategies found each paper. Then present the consolidated findings as numbered options grouped by theme. Ask: "Which directions should I add to the knowledge base? Pick one or more." The user can select multiple.

**Step 4 — Build KB entries.** For the selected directions only, invoke `how-to-build-kb` (read `skills/how-to-build-kb/SKILL.md`) with the picked papers — titles plus every DOI / arXiv ID collected in Steps 2–3 — and the target KB (the project KB `<project>/.knowledge/` by default; `--advisor <slug>` when invoked from `create-advisor`). It verifies every entry against an authoritative source, appends to `$KB/references.bib`, regenerates `INDEX.md`, and writes or extends `NOTES.md`. Never generate BibTeX from memory.

If the survey reveals the idea is already published, present the prior art and ask the user if they see a different angle before proceeding.

## After Survey — fetch full text, then optionally write

The discovery stage is done once the KB has its references, `NOTES.md`, and `INDEX.md`. Use `how-to-download-ref` to fetch PDFs and render full-text markdown before writing a source-grounded report.

First, scan the conversation for arXiv IDs / DOIs the user mentioned that the parallel search didn't surface. If any are missing from `references.bib`, pull them in (invoke `how-to-download-ref` single-shot, cite-key confirmation per ref) so the reference set is complete before downloading.

Then offer the next step:

> "Survey complete. Fetch the PDFs?"
> - **(a)** Fetch + render all refs — invokes `how-to-download-ref --from-bib $KB/references.bib --kb $KB`; after it finishes, offer to continue to Survey Report below.
> - **(b)** Done — stop here.

## Survey Report

Write a self-contained survey or technology/field assessment suitable for internal decision-making or team onboarding. This mode can follow Topic Survey in the same conversation or run directly against an existing project KB.

### Setup

Follow `skills/_shared/writing-workflow.md` for context loading, **source scoping**, citation handling, gap-filling research, output format, diagrams, and finish checks.

- If no KB exists, offer to run Topic Survey first; the report needs a grounded reference base.
- **Scope the source set first.** Run `scope_refs.py` as specified in the shared workflow. Fix dangling anchors before drafting. Build the report's approaches and claims from those scoped keys, not the entire bibliography.
- Check `CLAUDE.md`/`AGENTS.md` for a deliverables-location convention before choosing an output path.
- Tailor technical depth to the user's role from `docs/discussion/user-profile.md` or available context.
- Save to `articles/YYYY-MM-DD-<topic>-review.{md,typ,tex}` or a project-specific path if the user prefers.
- For Typst, start from `skills/survey/template.typ` with `skills/survey/template.bib`. The scaffold provides `section_box`, `stage`, `proscons`, `compare_table`, and `problem_table`; delete unused helpers from the copied document.

### Gap-filling focus

- Missing SOTA results mentioned in the survey but lacking citations
- Key groups or companies active in the field but not yet referenced
- Approaches or method families that belong in the technical assessment but are not covered
- Results from the last six months that may have superseded older survey entries

### Drafting flow

When the source set comes from an existing, recent `NOTES.md` (the normal case), draft the whole report end-to-end and show the compiled result for one review round. Reserve section-by-section drafting for a cold start where no `NOTES.md` exists and the substance is being composed as you go.

Organize the review **by technical approach**. State of the art and trade-offs live inside each approach, not in separate global sections. Do not add standalone global "Pros and Cons" or "State of the Art" sections.

#### 1. What and Why

Define the topic in 2–3 paragraphs for a new reader:

- What it is and what problem it solves
- Why it matters now
- How it differs from the dominant or prior approach

Include a diagram only when it clarifies the architecture, data flow, or problem framing. Lay approaches side by side only when they solve the same task and are genuinely comparable; otherwise show their relationship or omit the figure.

#### 2. Technical Approaches

Identify the main method families (typically 3–6) and give one subsection per approach. Optionally begin with a short field-wide timeline or landscape.

For each approach, cover:

- **What it is** — the defining representation, objective, or mechanism.
- **State of the art** — strongest current results, leading groups, and maturity, each cited. Lead with the best result rather than a chronology.
- **Assessment** — genuine strengths and limitations, with citations. Use the `proscons` two-list style only for competing solutions to the same problem. For complementary capabilities, platform branches, or historical stages, use a short prose assessment instead.

Optionally finish with a cross-approach comparison table when several approaches share meaningful criteria. Choose columns that actually discriminate this field (for example scalability, verifiability/cost, maturity, and best-fit use case). Skip it for a single-approach topic.

#### 3. Open Problems

End with a ranked table of 4–8 problems: number, problem, why it matters, who could solve it, and urgency (Critical / High / Medium). Cite the work that defines each gap or the closest existing result. Do not add business strategy, product fit, or investor sections to the neutral report.

### Visualization guidelines

- Typst: use CeTZ for timelines and dependency diagrams; use native `grid`, `rect`, and fixed-width `box()` for text-heavy comparisons and role diagrams. See `skills/_shared/typst-reference.md`.
- Use a native table for cross-approach comparisons.
- Wrap multiline CeTZ content in a fixed-width box and use string identifiers for `name:`.
- Compile after each figure; every claim in technical and open-problem tables needs at least one citation.

### Optional direction fit

After showing the report, ask exactly once: "Do you want me to analyse which direction is most suited for you?"

If yes, load the user's profile (or collect brief background, strengths, assets, and goals if none exists) and recommend 2–4 ranked directions. For each, name the report section/problem, explain the specific fit, give the smallest first experiment, and say what to avoid. Keep this personalized analysis outside the neutral report.
