---
name: review-writer
description: Use when writing a technology review or assessment report — produces a structured document covering what it is, pros/cons, state of the art, key problems, and optionally business relevance. Distinct from `writer`, which produces ideas reports from brainstorming sessions.
---

Write a structured review/assessment report for a technology, research field, or platform. The output is a self-contained document suitable for internal decision-making, investor communication, or team onboarding.

**Pipeline:** This skill is the final stage of the `survey` → `download-ref` → `review-writer` pipeline. Run `/survey` first to build a reference registry, then `/download-ref` to fetch PDFs and render full-text markdown, then this skill to produce the report. The skill can also run standalone if a survey registry already exists.

Trigger phrases: "write a review", "technology assessment", "what is it / pros and cons / SOTA", "evaluate this field", "business relevance of X", "write a report on X".

## Step 0 — Load context

1. **Survey registry:** Check project and global registry paths (`.knowledge/<topic>/`, `~/.claude/survey/<topic>/`). If registries exist, list them and ask which to load. Read `summary.md` and `references.bib`. If no survey exists, offer to run `/survey` first — the review needs a grounded reference base.
2. **Business context:** Check `CLAUDE.md` for company description, product portfolio, customer map, or team structure. If found, include a "Business Relevance" section in the report. If not found, ask: "Should the report include a business-relevance section? If so, briefly describe your company's position."
3. **User profile:** Check `docs/discussion/user-profile.md` or memory for the user's role and background. Tailor the level of technical detail accordingly (e.g., physicist vs. investor vs. engineer).

Read all selected files before proceeding.

## Step 1 — Gap-filling research

Before writing, search for gaps in the reference list. Use WebSearch or available MCP servers (Semantic Scholar, arxiv, paper-search) to find:
- Missing SOTA results mentioned in the survey but lacking citations
- Key groups/companies active in the field but not yet referenced
- Competing approaches or alternative platforms for the "Pros and Cons" section
- Recent results (last 6 months) that may have superseded older survey entries

Stop after covering the main claims — completeness is not the goal, grounding is.

## Step 2 — Output format

Check `CLAUDE.md`/`AGENTS.md` for a configured report format. If not configured, ask:

> "What format for the review?"
> - **(a)** Typst (`.typ`) — recommended, native BibTeX support, compiles to PDF
> - **(b)** LaTeX (`.tex`) — full BibTeX support, traditional academic format
> - **(c)** Markdown (`.md`) — note: limited BibTeX support, citations will be inline text rather than rendered references

Save to `articles/YYYY-MM-DD-<topic>-review.{md,typ,tex}` or a project-specific path (e.g., `projects/<topic>/report.typ`) if the user prefers. Copy the survey's `references.bib` alongside the report file.

---

## Report structure

Draft each section, show the user, get feedback before proceeding to the next:

### 1. What Is It
Define the technology in 2–3 paragraphs for a reader who has never heard of it. Cover:
- What problem it solves
- How it works (one level of detail — not a textbook, but enough to understand the pros/cons)
- What makes it different from the dominant approach

Include a **diagram** showing the key architectural concept (role separation, data flow, interaction mechanism). Use `grid` + `rect`/`box` for side-by-side layouts to avoid CeTZ overflow issues. Keep text inside fixed-width `box()` elements.

### 2. Pros and Cons
Structured **table** with numbered rows:
- Left column: advantage (bold heading + 1–2 sentence explanation + citation)
- Right column: corresponding disadvantage/limitation (bold heading + explanation + citation)

Aim for 4–8 rows covering orthogonal dimensions (performance, scalability, complexity, maturity, cost, risk). Every claim must have at least one `@citekey` citation.

### 3. State of the Art
Two parts:

**Milestone table:** columns = Milestone, Result, Group/Company, Year. Include citations in the Milestone column (e.g., `[First demonstration @Author2024]`). Order by year ascending. 8–12 rows.

**Who is building what:** Bulleted prose listing active groups and companies with their species/platform, recent results (with citations), and commercial vs. academic status.

### 4. Key Problems
Ranked **table** with columns: #, Problem, Why it matters, Who could solve it, Urgency (Critical / High / Medium). 4–8 rows. Order by urgency descending.

For each problem, cite the paper(s) that define the gap or the closest existing work.

### 5. Business Relevance *(include only if business context is available)*

Structure:
- **Strategic fit** — 2–3 numbered points explaining why this technology amplifies the company's thesis
- **Product-level impact table** — columns: Product, What the technology adds, Effort to support. One row per existing product.
- **Customer map table** — columns: Customer, Their platform, Their gap, Our offering.
- **Recommended actions** — 3–5 concrete next steps in a highlighted box (`rect` with colored border)
- **What we should _not_ do** — 2–3 explicit guardrails to prevent over-investment or scope creep

### 6. Key References
BibTeX bibliography via `#bibliography("references.bib")`. Every claim in the tables above should have at least one `@citekey` citation so the bibliography is fully populated — an empty bibliography means citations are missing.

---

## Visualization guidelines

Use diagrams to make abstract concepts concrete. Prefer simple layouts over complex CeTZ canvases.

**Typst reports:** Use CeTZ (`@preview/cetz:0.4.0`) for timeline and dependency diagrams. For side-by-side comparisons and role diagrams, prefer Typst's native `grid` + `rect` + `box` — these handle text wrapping and overflow better than CeTZ `content()` nodes. Refer to `skills/writer/typst-reference.md` for CeTZ patterns.

**Common diagram types for reviews:**
- **Role/architecture diagram** in "What Is It" — `grid(columns: 3)` with `rect` boxes and a center connector
- **Timeline** in "State of the Art" — CeTZ with `line` axis, `circle` milestones, `content` labels
- **Dependency graph** in "Key Problems" — CeTZ with `rect` nodes (string names, not content), `line` arrows, color-coded by urgency

**Layout rules:**
- Always wrap multi-line text inside CeTZ `content()` with a fixed-width `box()` to prevent overflow
- Use string identifiers for CeTZ `name:` parameters, never content blocks
- For side-by-side boxes with bullet lists, use `grid` instead of CeTZ — it handles text reflow
- Test compile after each figure before proceeding

---

## After writing

1. Compile to PDF and visually verify all diagrams render without overflow
2. Check that the bibliography is non-empty (if empty, add missing `@citekey` citations)
3. Report the output path and page count to the user
