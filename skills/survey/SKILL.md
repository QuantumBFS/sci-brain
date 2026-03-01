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

**Step 2 — Pick strategies & search.** Present the strategy menu to the user as a multi-select question. Recommend 3-4 strategies based on the topic context, but let the user choose. Then launch one subagent per selected strategy in parallel. Every subagent uses **WebSearch only** at this stage — fast and broad.

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

Each subagent produces a short **findings report** — key papers found, grouped by sub-theme, with titles and one-line descriptions. No BibTeX yet.

**Step 3 — User picks directions.** Main agent consolidates all findings reports and presents them as numbered options. Ask: "Which directions should I build a literature registry for? Pick one or more." The user can select multiple.

**Step 4 — Build registry.** For the selected directions only, generate the full BibTeX. **Never generate BibTeX from memory** — always verify against an authoritative source. Use the following lookup chain (in priority order):

1. **CrossRef API** (gold standard for DOI-based lookup) — `curl -sL -H "Accept: application/x-bibtex" "https://doi.org/{DOI}"` returns BibTeX directly, no auth needed. Use `WebFetch` if `curl` is blocked.
2. **Semantic Scholar API** — `https://api.semanticscholar.org/graph/v1/paper/DOI:{DOI}?fields=title,authors,year,journal,abstract,externalIds,citationStyles` returns structured metadata. Also supports title search: `https://api.semanticscholar.org/graph/v1/paper/search?query={title}&fields=...`
3. **MCP servers** (if configured):
   - **arxiv MCP** — search for the paper, get abstract and arxiv ID
   - **paper-search-mcp** — PubMed, bioRxiv, CrossRef
   - **Semantic Scholar MCP** — citation metadata, abstract, DOI
4. **WebFetch on publisher page** (fallback) — fetch the paper's landing page and extract metadata. Less reliable but works when APIs are blocked.

If all API methods fail (e.g., network restrictions), BibTeX may be constructed from WebSearch results but **must** flag unverified fields with a comment `% unverified`.

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
> - **(a)** Deeper survey — survey a specific subtopic and add results to this registry (user types the subtopic, then go back to Step 2)
> - **(b)** Brainstorm — continue to brainstorming in the current session
> - **(c)** Clear context and brainstorm — compact the conversation first (frees context for a longer brainstorm), then continue to brainstorming
> - **(d)** Stop here — keep the survey registry, end the session

For **(a)**: use the user's subtopic as the new query, go back to Step 2 (pick strategies & search). Append new references to the existing `references.bib` and update `summary.md` with the new findings.

For **(c)**: save the survey registry path, compact the conversation, then re-read the survey report and personal registry before starting brainstorming.
