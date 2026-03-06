---
name: writer
description: Use when writing the final ideas report after the user picks a research direction — produces a structured document with reasoning trail, chosen direction, and BibTeX references
---

## Refine (exit from loop)

### Step 0 — Load context

Check whether the current session already has ideas context (from a preceding `/ideas` session). If not — e.g., the user invoked `/writer` in a fresh session — locate the materials:

1. **Conversation log:** Search for files matching `docs/discussion/*-ideas-log.md`. If multiple exist, list them and ask the user which one to use. If one exists, read it. This is the primary source — it contains the full brainstorming history: questions asked, options presented, user choices, ideas explored, and directions taken. If none exist, ask the user: "I don't see a conversation log from a brainstorming session. Run `/ideas` first, or describe the research direction and I'll write from scratch."
2. **Survey registry:** Check global and project registry paths (e.g., `~/.claude/survey/`, `.claude/survey/`). If registries exist, list them and ask which to load. Read the selected `summary.md` and `references.bib`.
3. **Personal registry:** Check `~/.claude/survey/personal/`. If found, read `summary.md` for background context.

Read all selected files before proceeding. The conversation log provides the reasoning trail, explored directions, and chosen ideas that structure the document.

### Step 1 — Report scope

**Report scope:** Ask the user before writing:

> "What scope for the ideas report?"
> - **(a)** Full brainstorming process — complete reasoning trail: what was explored, tried, killed, and why the surviving direction was chosen
> - **(b)** Crystallized idea only — focused writeup of the chosen research direction, skipping the exploration history

### Step 2 — Gap-filling research

Before writing, search for gaps in the reference list — missing methodology papers for the planned approach, code repos, datasets, or benchmarks. Use available MCP servers (Semantic Scholar, arxiv, paper-search) or WebSearch. Aim for 3–5 methodology references and 1–2 datasets/benchmarks per key claim. Stop after covering the main claims — completeness is not the goal, grounding is.

### Step 3 — Output format

Check `CLAUDE.md`/`AGENTS.md` for a configured report format. If not configured, ask the user:

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
