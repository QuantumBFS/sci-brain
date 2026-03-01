---
name: survey
description: Use when surveying a research topic — launches parallel exploration strategies via web search, lets user pick interesting directions, then builds a focused survey registry with BibTeX
---

Before starting, check which MCP servers are available (arxiv, paper-search, Semantic Scholar). If none are configured, warn the user that the survey will rely on WebSearch only.

If the user already provided a research topic or question, skip the clarification step.

## Topic Survey

**Step 0 — Registry location.** Check `CLAUDE.md`/`AGENTS.md` for a configured survey registry path. If not configured, ask:

> "Where should I store the survey registry? It persists across sessions so you can reuse it later."
> - **(a)** Global — shared across all projects (auto-detected path based on platform, e.g., `~/.claude/survey/` for Claude Code, `~/.codex/survey/` for Codex, `~/.config/opencode/survey/` for OpenCode)
> - **(b)** Project — scoped to this project (`.claude/survey/`)

This only needs to be asked once per session. If a registry already exists at either location, detect it and confirm with the user.

**Step 1 — Clarify.** Ask one question to narrow the research topic. Give 2-4 choice options.

**Step 2 — Web search.** Launch N subagents in parallel, each with a different exploration strategy. Every subagent uses **WebSearch only** at this stage — fast and broad.

**Strategy menu (AI picks from these based on iteration context):**

| # | Strategy | When to use |
|---|----------|-------------|
| 1 | **Landscape mapping** | First iteration default — broad field overview |
| 2 | **Adjacent subfield** | Deep-dive into a neighboring cluster identified in prior iteration |
| 3 | **Cross-vocabulary** | Abstract away jargon, search other fields for the same structural problem |
| 4 | **Cross-method** | Same problem, different computational or experimental approaches |
| 5 | **Historical lineage** | Who tried before, what failed, what changed since |
| 6 | **Negative results** | Search for papers showing what does not work |
| 7 | **Benchmarks and datasets** | What evaluation infrastructure exists |

Each subagent produces a short **findings report** — key papers found, grouped by sub-theme, with titles and one-line descriptions. No BibTeX yet.

**Step 3 — User picks directions.** Main agent consolidates all findings reports and presents them as numbered options. "Which directions interest you? Pick one or more." The user can select multiple.

**Step 4 — Build registry.** For the selected directions only, generate the full BibTeX. If a reference lacks DOI/URL or abstract, try one of:

- **arxiv MCP** — search for the paper, get abstract and arxiv ID
- **paper-search-mcp** — PubMed, bioRxiv, CrossRef
- **Semantic Scholar MCP** — citation metadata, abstract, DOI

Output the **survey registry** — a folder `<registry-root>/<topic>/` (where `<registry-root>` is the global or project path chosen in Step 0) containing:

**1. `summary.md`** — references listed as indices categorized by topic, using BibTeX cite keys (e.g., `[AuthorYear]`). Include:

- **Field landscape** — key papers clustered by sub-theme with publication years, active groups, temporal trends
- **Key open problems** — unsolved questions
- **Key bottlenecks** — obstacles preventing progress

**2. `references.bib`** — BibTeX for all references. Every entry **must** contain:

- `abstract` — the paper's abstract
- `doi` or `url` — at least one identifier for retrieval

## After Survey — transition checkpoint

After the survey registry is built, ask:

> "Survey complete. What next?"
> - **(a)** Brainstorm — continue to Step 2 in the current session
> - **(b)** Clear context and brainstorm — compact the conversation first (frees context for a longer brainstorm), then continue to Step 2
> - **(c)** Stop here — keep the survey registry, end the session

For **(b)**: save the survey registry path, compact the conversation, then re-read the survey report and personal registry before starting Step 2.
