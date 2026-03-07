---
name: writer
description: Use when writing the final ideas report after the user picks a research direction — produces a structured document with the chosen direction and BibTeX references
---

## Refine (exit from loop)

### Step 0 — Load context

Check whether the current session already has ideas context (from a preceding `/ideas` session). If not — e.g., the user invoked `/writer` in a fresh session — locate the materials:

1. **Conversation log:** Search for files matching `docs/discussion/*-ideas-log.md`. If multiple exist, list them and ask the user which one to use. If one exists, read it. This is the primary source — it contains the full brainstorming history: questions asked, options presented, user choices, ideas explored, and directions taken. If none exist, ask the user: "I don't see a conversation log from a brainstorming session. Run `/ideas` first, or describe the research direction and I'll write from scratch."
2. **Survey registry:** Check global and project registry paths (e.g., `~/.claude/survey/`, `.claude/survey/`). If registries exist, list them and ask which to load. Read the selected `summary.md` and `references.bib`.
3. **User profile:** Check `docs/discussion/user-profile.md`. If found, read it for background context (name, skills, interests).
4. **Personal registry:** Check `~/.claude/survey/personal/`. If found, read `summary.md` for publication history.

Read all selected files before proceeding. The conversation log provides the reasoning trail, explored directions, and chosen ideas that structure the document.

### Step 1 — Gap-filling research

Before writing, search for gaps in the reference list — missing methodology papers for the planned approach, code repos, datasets, or benchmarks. Use available MCP servers (Semantic Scholar, arxiv, paper-search, Sci-Hub) or WebSearch. Aim for 3–5 methodology references and 1–2 datasets/benchmarks per key claim. Stop after covering the main claims — completeness is not the goal, grounding is.

### Step 2 — Output format

Check `CLAUDE.md`/`AGENTS.md` for a configured report format. If not configured, ask the user:

> "What format for the ideas report?"
> - **(a)** Typst (`.typ`) — recommended, native BibTeX support, compiles to PDF
> - **(b)** LaTeX (`.tex`) — full BibTeX support, traditional academic format
> - **(c)** Markdown (`.md`) — note: limited BibTeX support, citations will be inline text rather than rendered references

Save to `articles/YYYY-MM-DD-<topic>-ideas-report.{md,typ,tex}` (with matching `references.bib`).

---

### Report structure

Draft each section, show, get feedback:

- **Research Question** — one sentence
- **Novelty Claim** — what's new and why it matters
- **Why Now, Why You** — what changed to make this tractable; unique advantage
- **Cross-field Connections** — unexpected links discovered during brainstorming
- **Proposed Approach** — method outline (Polya: what is the plan?)
- **Minimum Viable Experiment** — (Polya: can you solve a part of it?)
- **Success Signal** — what would it look like if this problem is truly solved?
- **Hope Signal** — what would indicate the problem isn't solved yet, but the approach still has hope?
- **Pivot Signal** — what would indicate this approach fundamentally doesn't work, and it's time to abandon or change direction?
- **Open Risks** — unresolved uncertainties
- **Target Venue**
- **Key References** — full BibTeX entries; save matching `.bib` file

### Visualize abstract ideas

When a concept is abstract or structural — a reduction between problems, a relationship between methods, a data flow, an architecture — draw a diagram instead of (or alongside) explaining it in prose. A picture makes the idea concrete and shareable in ways that paragraphs of text cannot.

**For Typst reports:** use CeTZ (`@preview/cetz:0.4.0`) to draw inline figures. Refer to `skills/writer/typst-reference.md` for CeTZ patterns and syntax. Common diagram types:
- **Reduction/connection diagrams** — boxes for concepts, arrows for relationships
- **Pipeline/flow diagrams** — stages of a method or data flow
- **Comparison layouts** — side-by-side before/after or method A vs. method B
- **Conceptual sketches** — any visual that makes an abstract idea graspable at a glance

**For LaTeX reports:** use TikZ for equivalent diagrams.

**For Markdown reports:** use ASCII art or Mermaid diagrams where supported.

The goal is not decoration — it's clarity. If drawing the idea makes it easier to understand or critique, draw it.

---

*Polya's "Looking Back":* After drafting, review — can the result be derived differently? Can it be used for some other problem? Can you see the result at a glance?
