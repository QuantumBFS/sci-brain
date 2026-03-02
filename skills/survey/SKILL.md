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

This only needs to be asked once per session. If a registry already exists at the chosen location for this topic (i.e., `<registry-root>/<topic>/` already contains `summary.md` and `references.bib`), ask:

> "A survey registry for this topic already exists (N papers). What should I do?"
> - **(a)** Extend — add new findings to the existing registry (keeps existing entries, appends new ones, deduplicates by DOI/title)
> - **(b)** Replace — start fresh (backs up the old registry to `<topic>.bak/` first)
> - **(c)** New subtopic — create a separate registry under a more specific name

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

**Step 3 — Consolidate & user picks directions.** Main agent consolidates all findings reports. **Deduplicate** papers that appear in multiple strategy reports — match by title similarity or DOI. Merge their descriptions (keep the richer one) and note which strategies found each paper. Then present the consolidated findings as numbered options grouped by theme. Ask: "Which directions should I build a literature registry for? Pick one or more." The user can select multiple.

**Step 4 — Build registry.** For the selected directions only, generate the full BibTeX. **Never generate BibTeX from memory** — always verify against an authoritative source. Use the following lookup chain (in priority order):

1. **CrossRef API** (gold standard for DOI-based lookup) — `curl -sL -H "Accept: application/x-bibtex" "https://doi.org/{DOI}"` returns BibTeX directly, no auth needed. Use `WebFetch` if `curl` is blocked.
2. **Semantic Scholar API** — `https://api.semanticscholar.org/graph/v1/paper/DOI:{DOI}?fields=title,authors,year,journal,abstract,externalIds,citationStyles` returns structured metadata. Also supports title search: `https://api.semanticscholar.org/graph/v1/paper/search?query={title}&fields=...`
3. **MCP servers** (if configured):
   - **arxiv MCP** — search for the paper, get abstract and arxiv ID
   - **paper-search-mcp** — PubMed, bioRxiv, CrossRef
   - **Semantic Scholar MCP** — citation metadata, abstract, DOI
4. **WebFetch on publisher page** (fallback) — fetch the paper's landing page and extract metadata. Less reliable but works when APIs are blocked.

If all API methods fail (e.g., network restrictions), BibTeX may be constructed from WebSearch results but **must** flag unverified fields with a comment `% unverified`.

If the survey reveals the idea is already published, present the prior art and ask the user if they see a different angle before proceeding.

**If extending an existing registry** (Step 0 option a): read the existing `references.bib` first, skip papers already present (match by DOI or exact title), and append only new entries. Update `summary.md` by merging new findings into the existing topic sections.

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
> - **(b)** Ideas — continue to ideation (brainstorming, critique, and ranking) in the current session
> - **(c)** Export to Zotero — save discovered papers to your Zotero library (requires Zotero MCP with write support)
> - **(d)** Stop here — keep the survey registry, end the session

For **(c)**: if a Zotero MCP server with write support is configured, create items from `references.bib` entries in the user's Zotero library. Ask which collection to add them to. If no write-capable Zotero MCP is available, tell the user they can import `references.bib` manually via Zotero's File > Import.

For **(a)**: use the user's subtopic as the new query, go back to Step 2 (pick strategies & search). Append new references to the existing `references.bib` and update `summary.md` with the new findings.
