---
name: survey-writer
description: Use when writing up a literature survey, technology review, field assessment, SOTA report, or pros/cons report from a populated knowledge base — the write-up stage of the survey pipeline
---

Write a structured survey/assessment report for a technology, research field, or platform. The output is a self-contained document suitable for internal decision-making or team onboarding.

**Pipeline:** This skill is the final stage of the `survey` → `download-ref` → `survey-writer` pipeline. Run `/survey` first to build a literature KB, then `/download-ref` to fetch PDFs and render full-text markdown, then this skill to produce the report. The skill can also run standalone if a project KB already exists.

Trigger phrases: "write up the survey", "write a review", "technology assessment", "what is it / pros and cons / SOTA", "evaluate this field", "write a report on X".

## Setup

Follow `skills/_shared/writing-workflow.md` for context loading, **source scoping**, citation handling, gap-filling research, output format, diagrams, and finish checks.

- If no KB exists, offer to run `/survey` first — the review needs a grounded reference base.
- **Scope the source set first.** Run `scope_refs.py` (see writing-workflow → "Scope the source set") to get the cite keys this review covers from `NOTES.md`, and fix any dangling anchors before drafting. The review's approaches and claims are built from these keys, not the whole bib.
- Check `CLAUDE.md`/`AGENTS.md` for a deliverables-location convention before choosing an output path (this repo, for example, puts deliverables under `projects/<topic>/`).
- Tailor technical depth to the user's role from `docs/discussion/user-profile.md` or memory.
- Save to `articles/YYYY-MM-DD-<topic>-review.{md,typ,tex}` or a project-specific path if the user prefers.
- For a Typst report, start from the bundled scaffold `template.typ` (in this skill's directory, with `template.bib`): copy it to the output path and fill it in. It already encodes the § Report structure below and ships helper functions — `section_box`, `stage` (flow/era strips), `proscons` (per-approach unpaired strengths/limitations — use only when approaches compete for the same problem; see § 2), `compare_table`, `problem_table`. Delete unused helpers from the copy.

## Gap-Filling Focus

- Missing SOTA results mentioned in the survey but lacking citations
- Key groups/companies active in the field but not yet referenced
- Approaches or method families that belong in § 2 but are not yet covered or referenced
- Recent results (last 6 months) that may have superseded older survey entries

## Report structure

When the source set comes from an existing, recent `NOTES.md` (the normal case — `/survey` just ran), **draft the whole report end-to-end, then show the user the compiled result for one round of review.** The content is already grounded in approved notes, so per-section gating only adds latency. Reserve section-by-section drafting for the cold-start case where no `NOTES.md` exists and you are composing the substance as you go.

Organize the review **by technical approach**. The bulk of the report explains the approaches, and the state of the art and trade-offs live *inside each approach* rather than in separate global sections. Do not write a standalone global "Pros and Cons" or "State of the Art" section — those belong per-approach (see § 2).

### 1. What and Why
Define the topic in 2–3 paragraphs for a reader who has never heard of it. Cover:
- What it is and what problem it solves
- Why it matters now — the motivation and stakes
- How it differs from the dominant or prior approach

Include a **diagram** showing the key concept (architecture, data flow, or the problem framing). Use `grid` + `rect`/`box` for side-by-side layouts to avoid CeTZ overflow issues. Keep text inside fixed-width `box()` elements.

**Comparability gate for a side-by-side approaches figure.** Only lay the approaches out side by side (a stack/row of approach boxes) when they are *the same task with different methods* — then a comparison reads fairly. When the "approaches" are different task families (e.g. discovery vs. decoding vs. compilation), a side-by-side strip implies a false equivalence; instead draw their *relationship* (a pipeline or dependency diagram) only if it adds something, or omit the figure. Do not force a concept diagram that lines up non-comparable approaches.

### 2. Technical Approaches
This is the core of the review. Identify the main approaches / method families in the field (typically 3–6) and give **one subsection per approach**. Optionally open with a short field-wide **timeline or landscape** (a CeTZ timeline, or a one-line-per-era list) to orient the reader before the per-approach detail.

For each approach, cover three things in order:
- **What it is** — the mechanism at one level of detail: the representation, objective, or trick that defines it.
- **State of the art** — the strongest current results, leading groups, and maturity, each with a `@citekey` citation. Lead with the best result, not a chronology.
- **Assessment** — the genuine strengths and limitations *of this approach*, every claim cited. **Choose the form by what the approaches are:**
  - Use the **pros/cons two-list style** (the `proscons` helper) *only* when the approaches are competing solutions to the *same problem* — the reader's question is "which one should I pick?", and the bullet lists support that decision. Do **not** force advantages and limitations into matched pairs or equal counts — list the real ones.
  - When the "approaches" are complementary capabilities, platform branches, historical stages, or otherwise *not* alternatives for one decision, write the assessment as a short **prose paragraph** (e.g. a *Character.* paragraph) that weaves strengths and limits together. Boxed pros/cons lists misframe complements as rivals.
  - Either way, this per-approach treatment replaces the old global pros/cons table.

End the section with an **optional cross-approach comparison table** — rows = approaches, columns = a few shared criteria, cells cited where they make a claim. **Choose the columns adaptively** to the field: pick the criteria that actually discriminate the approaches (e.g. scalability, verifiability/cost, maturity, best-fit use case), not a fixed template. Because the columns adapt, this table can still summarize approaches from different task families — the "best-fit use case" column carries the distinction the side-by-side *figure* could not. Use it as the at-a-glance summary when the field has several approaches worth tabulating; skip it for a single-approach topic.

### 3. Open Problems
Ranked **table** with columns: #, Problem, Why it matters, Who could solve it, Urgency (Critical / High / Medium). 4–8 rows. Order by urgency descending. For each problem, cite the paper(s) that define the gap or the closest existing work.

The report ends at Open Problems. Keep it a neutral technical assessment — do **not** add a
business-relevance, strategy, product-fit, or investor section. Personalized direction lives in
the optional post-report step below, not in the document.

## After the report — direction fit (optional)

Once the report is generated and shown, ask the user exactly one question:

> "Do you want me to analyse which direction is most suited for you?"

If **no**, stop here. If **yes**:

1. **Load the user's research profile.** Look in `docs/discussion/user-profile.md`, the project
   `profiles/`, and memory. If no profile exists, generate one with the appropriate profile
   skill (e.g. `create-profile`) — or, if none is available, ask the user a few quick questions
   about their background, technical strengths, current tools/assets, and goals — then save it
   for reuse.
2. **Recommend next steps**, grounded in *both* the report and the profile. For each
   recommendation give: which approach or open problem (by § / row number) to pursue, why it
   fits this user specifically (their strengths, existing assets, unique advantage), the
   smallest first experiment, and what to deliberately avoid. Keep it to 2–4 ranked directions.

This keeps the report objective and reusable while the personalized analysis stays a separate,
conversational layer.

## Visualization guidelines

Use diagrams to make abstract concepts concrete. Prefer simple layouts over complex CeTZ canvases.

**Typst reports:** Use CeTZ (`@preview/cetz:0.4.0`) for timeline and dependency diagrams. For side-by-side comparisons and role diagrams, prefer Typst's native `grid` + `rect` + `box` — these handle text wrapping and overflow better than CeTZ `content()` nodes. Refer to `skills/_shared/typst-reference.md` for CeTZ patterns.

**Common diagram types for reviews:**
- **Role/architecture diagram** in "What and Why" — `grid(columns: 3)` with `rect` boxes and a center connector
- **Timeline** for the optional field-wide overview in "Technical Approaches" — CeTZ with `line` axis, `circle` milestones, `content` labels
- **Cross-approach comparison matrix** at the end of "Technical Approaches" — a native `table` (rows = approaches, columns = shared criteria), not CeTZ
- **Dependency graph** in "Open Problems" — CeTZ with `rect` nodes (string names, not content), `line` arrows, color-coded by urgency

**Layout rules:**
- Always wrap multi-line text inside CeTZ `content()` with a fixed-width `box()` to prevent overflow
- Use string identifiers for CeTZ `name:` parameters, never content blocks
- For side-by-side boxes with bullet lists, use `grid` instead of CeTZ — it handles text reflow
- Test compile after each figure before proceeding

Every claim in the technical tables (the cross-approach comparison matrix and the open-problems table) should have at least one `@citekey` citation.
