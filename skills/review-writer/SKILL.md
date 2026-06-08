---
name: review-writer
description: Use when writing a technology review, field assessment, SOTA report, pros/cons report, or business-relevance assessment
---

Write a structured review/assessment report for a technology, research field, or platform. The output is a self-contained document suitable for internal decision-making, investor communication, or team onboarding.

**Pipeline:** This skill is the final stage of the `survey` → `download-ref` → `review-writer` pipeline. Run `/survey` first to build a literature KB, then `/download-ref` to fetch PDFs and render full-text markdown, then this skill to produce the report. The skill can also run standalone if a project KB already exists.

Trigger phrases: "write a review", "technology assessment", "what is it / pros and cons / SOTA", "evaluate this field", "business relevance of X", "write a report on X".

## Setup

Follow `skills/_shared/writing-workflow.md` for context loading, citation handling, gap-filling research, output format, diagrams, and finish checks.

- If no KB exists, offer to run `/survey` first — the review needs a grounded reference base.
- Check `CLAUDE.md` for company description, product portfolio, customer map, or team structure. If found, include "Business Relevance"; if not found, ask whether to include it.
- Tailor technical depth to the user's role from `docs/discussion/user-profile.md` or memory.
- Save to `articles/YYYY-MM-DD-<topic>-review.{md,typ,tex}` or a project-specific path if the user prefers.
- For a Typst report, start from the bundled scaffold `template.typ` (in this skill's directory, with `template.bib`): copy it to the output path and fill it in. It already encodes the § Report structure below and ships helper functions — `section_box`, `stage` (flow/era strips), `proscons` (per-approach unpaired strengths/limitations), `compare_table`, `problem_table`.

## Gap-Filling Focus

- Missing SOTA results mentioned in the survey but lacking citations
- Key groups/companies active in the field but not yet referenced
- Approaches or method families that belong in § 2 but are not yet covered or referenced
- Recent results (last 6 months) that may have superseded older survey entries

## Report structure

Draft each section, show the user, get feedback before proceeding to the next:

Organize the review **by technical approach**. The bulk of the report explains the approaches, and the state of the art and trade-offs live *inside each approach* rather than in separate global sections. Do not write a standalone global "Pros and Cons" or "State of the Art" section — those belong per-approach (see § 2).

### 1. What and Why
Define the topic in 2–3 paragraphs for a reader who has never heard of it. Cover:
- What it is and what problem it solves
- Why it matters now — the motivation and stakes
- How it differs from the dominant or prior approach

Include a **diagram** showing the key concept (architecture, data flow, or the problem framing). Use `grid` + `rect`/`box` for side-by-side layouts to avoid CeTZ overflow issues. Keep text inside fixed-width `box()` elements.

### 2. Technical Approaches
This is the core of the review. Identify the main approaches / method families in the field (typically 3–6) and give **one subsection per approach**. Optionally open with a short field-wide **timeline or landscape** (a CeTZ timeline, or a one-line-per-era list) to orient the reader before the per-approach detail.

For each approach, cover three things in order:
- **What it is** — the mechanism at one level of detail: the representation, objective, or trick that defines it.
- **State of the art** — the strongest current results, leading groups, and maturity, each with a `@citekey` citation. Lead with the best result, not a chronology.
- **Pros and cons** — the genuine strengths and limitations *of this approach*, as two short bullet lists (2–4 bullets each), every bullet cited. Do **not** force advantages and limitations into matched pairs or equal counts — list the real ones. This per-approach treatment replaces the old global pros/cons table.

End the section with an **optional cross-approach comparison table** — rows = approaches, columns = a few shared criteria (e.g. scalability, verifiability/cost, maturity, best-fit use case), cells cited where they make a claim. Use it as the at-a-glance summary when the field has several comparable approaches; skip it for a single-approach topic.

### 3. Open Problems
Ranked **table** with columns: #, Problem, Why it matters, Who could solve it, Urgency (Critical / High / Medium). 4–8 rows. Order by urgency descending. For each problem, cite the paper(s) that define the gap or the closest existing work.

### 4. Business Relevance *(include only if business context is available)*

Structure:
- **Strategic fit** — 2–3 numbered points explaining why this technology amplifies the company's thesis
- **Product-level impact table** — columns: Product, What the technology adds, Effort to support. One row per existing product.
- **Customer map table** — columns: Customer, Their platform, Their gap, Our offering.
- **Recommended actions** — 3–5 concrete next steps in a highlighted box (`rect` with colored border)
- **What we should _not_ do** — 2–3 explicit guardrails to prevent over-investment or scope creep

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

Every claim in tables should have at least one `@citekey` citation.
