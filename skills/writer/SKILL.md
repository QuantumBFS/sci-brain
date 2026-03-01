---
name: writer
description: Use when writing the final ideas report after the user picks a research direction — produces a structured document with reasoning trail, chosen direction, and BibTeX references
---

## Refine (exit from loop)

**Report scope:** Ask the user before writing:

> "What scope for the ideas report?"
> - **(a)** Full brainstorming process — complete reasoning trail: what was explored, tried, killed, and why the surviving direction was chosen
> - **(b)** Crystallized idea only — focused writeup of the chosen research direction, skipping the exploration history

**Autonomous research (gap-filling):** Before writing, search for any gaps in the reference list — missing methodology papers for the planned approach, code repos, datasets, or benchmarks. Use available MCP servers (Semantic Scholar, arxiv, paper-search) or WebSearch.

**Output format:** Check `CLAUDE.md`/`AGENTS.md` for a configured report format. If not configured, ask the user:

> "What format for the ideas report?"
> - **(a)** Typst (`.typ`) — recommended, native BibTeX support, compiles to PDF
> - **(b)** LaTeX (`.tex`) — full BibTeX support, traditional academic format
> - **(c)** Markdown (`.md`) — note: limited BibTeX support, citations will be inline text rather than rendered references

Save to `articles/YYYY-MM-DD-<topic>-ideas-report.{md,typ,tex}` (with matching `references.bib`).

---

### Structure A: Full brainstorming process

Draft each section, show, get feedback:

*Part 1 — What we explored (reasoning trail):*

- **Field Landscape** — basic picture of the field and its key problems
- **Key Bottleneck** — the specific bottleneck this work addresses
- **Survey Trail** — what strategies were used per iteration, what was discovered, what shifted our understanding
- **Ideas Explored** — all ideas generated (human + AI), with the reasoning behind each
- **Ideas Killed** — which ideas were eliminated, the evidence and critique that killed them (epitaphs from the AI Judge phase)
- **Ideas Survived** — which ideas survived critique and why

*Part 2 — The chosen direction:*

- **Research Question** — one sentence
- **Novelty Claim** — what's new (survived formal critique)
- **Why Now, Why You** — what changed to make this tractable; unique advantage
- **Cross-field Connections** — unexpected links from cross-vocabulary / transplanter strategies
- **Proposed Approach** — method outline (Polya: what is the plan?)
- **Minimum Viable Experiment** — (Polya: can you solve a part of it?)
- **Success Signal** — what would it look like if this problem is truly solved?
- **Hope Signal** — what would indicate the problem isn't solved yet, but the approach still has hope?
- **Pivot Signal** — what would indicate this approach fundamentally doesn't work, and it's time to abandon or change direction?
- **Open Risks** — unresolved from critique
- **Target Venue**

*Part 3 — References:*

- **Key References** — full BibTeX entries from all survey iterations
- **BibTeX file** — save as `articles/YYYY-MM-DD-<topic>-references.bib`

---

### Structure B: Crystallized idea only

Draft each section, show, get feedback:

- **Research Question** — one sentence
- **Novelty Claim** — what's new (survived formal critique)
- **Why Now, Why You** — what changed to make this tractable; unique advantage
- **Cross-field Connections** — unexpected links from cross-vocabulary / transplanter strategies
- **Proposed Approach** — method outline (Polya: what is the plan?)
- **Minimum Viable Experiment** — (Polya: can you solve a part of it?)
- **Success Signal** — what would it look like if this problem is truly solved?
- **Hope Signal** — what would indicate the problem isn't solved yet, but the approach still has hope?
- **Pivot Signal** — what would indicate this approach fundamentally doesn't work, and it's time to abandon or change direction?
- **Open Risks** — unresolved from critique
- **Target Venue**
- **Key References** — full BibTeX entries; save matching `.bib` file

---

*Polya's "Looking Back":* After drafting either structure, review — can the result be derived differently? Can it be used for some other problem? Can you see the result at a glance?
