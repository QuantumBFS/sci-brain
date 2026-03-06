---
name: survey
description: Use when surveying a research topic — launches parallel exploration strategies via web search, lets user pick interesting directions, then builds a focused survey registry with BibTeX
---

Before starting, check which MCP servers are available (arxiv, paper-search, Semantic Scholar, Sci-Hub, etc.). Present the detected servers to the user and let them choose which ones to use for this session via `AskUserQuestion` (multi-select). If none are configured, warn the user that the survey will rely on WebSearch only.

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

Each subagent produces a short **findings report** — key papers found, grouped by sub-theme, with titles and one-line descriptions. No BibTeX yet. **Important:** subagents must also collect the DOI and arXiv ID for each paper when visible in search results (e.g., DOIs from publisher URLs, arXiv IDs from arxiv.org links like `2401.12345`). Record these alongside titles in the findings report.

**Step 3 — Consolidate & user picks directions.** Main agent consolidates all findings reports. **Deduplicate** papers that appear in multiple strategy reports — match by title similarity or DOI. Merge their descriptions (keep the richer one), **preserve any DOIs and arXiv IDs collected** during Step 2, and note which strategies found each paper. Then present the consolidated findings as numbered options grouped by theme. Ask: "Which directions should I build a literature registry for? Pick one or more." The user can select multiple.

**Step 4 — Build registry.** For the selected directions only, generate the full BibTeX. **Never generate BibTeX from memory** — always verify against an authoritative source.

First, **pre-sort papers** from Step 3 into two groups based on whether a DOI or arXiv ID was collected during Steps 2-3:

- **ID-known papers** — papers where a DOI or arXiv ID was found in search results
- **ID-unknown papers** — papers where neither was found

**arxiv MCP fast path:** If an arxiv MCP server with `export_papers` is configured (e.g., `anuj0456/arxiv-mcp-server`), check which papers have arXiv IDs (from `externalIds` or arXiv URLs collected in Steps 2-3). Batch-export those via `export_papers(arxiv_ids, format="bibtex", include_abstract=True)` before launching the subagents below, and remove them from the DOI-known/unknown lists.

Then launch **two subagents in parallel**, one per group:

**Subagent A — ID-known papers (batch lookup):**

1. Make a single batch call to the Semantic Scholar API:
   ```
   POST https://api.semanticscholar.org/graph/v1/paper/batch?fields=title,authors,year,journal,abstract,externalIds,citationStyles
   Body: {"ids": ["DOI:10.xxxx/yyyy", "ARXIV:2401.12345", ...]}
   ```
   Use `DOI:` prefix for DOIs, `ARXIV:` prefix for arXiv IDs. Returns BibTeX (via `citationStyles.bibtex`), abstract, and DOI for all papers in one request (up to 500).
2. **Enrich each BibTeX entry** — the `citationStyles.bibtex` field does not include `abstract` or `doi`. Inject these from the response's `abstract` and `externalIds.DOI` fields into each BibTeX string.
3. For any papers that return `null` from the batch call, the agent should pick the single most effective method for each paper and try that (e.g., CrossRef for DOI-only papers, title match for others).

**Subagent B — ID-unknown papers (title-based lookup):**

For each paper, the agent picks the single most effective lookup method based on available context (e.g., publisher, field, available MCP servers). Available methods:

- **Semantic Scholar title match** — `GET https://api.semanticscholar.org/graph/v1/paper/search/match?query={title}&fields=title,authors,year,journal,abstract,externalIds,citationStyles` (rate limit: ~1 req/s unauthenticated)
- **CrossRef title search** — `https://api.crossref.org/works?query.bibliographic={title}&rows=1`
- **MCP servers** (if configured): arxiv MCP, paper-search-mcp, Semantic Scholar MCP, Sci-Hub MCP (`search_scihub_by_title`, `get_paper_metadata`)
- **WebFetch on publisher page** — extract metadata from the paper's landing page

**Enrich the BibTeX** with `abstract` and `doi`/`url` if missing. If the abstract is still missing and a Sci-Hub MCP server is configured, use `download_scihub_pdf` to get the full text and extract the abstract from it. If the chosen method fails, try one alternative. If that also fails, BibTeX may be constructed from WebSearch results but **must** flag unverified fields with `% unverified`.

After both subagents complete, **merge their results** into the final registry files.

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
> - **(b)** Ideas — continue to brainstorming in the current session
> - **(c)** Export to Zotero — save discovered papers to your Zotero library (requires Zotero MCP with write support)
> - **(d)** Stop here — keep the survey registry, end the session

For **(c)**: if a Zotero MCP server with write support is configured, create items from `references.bib` entries in the user's Zotero library. Ask which collection to add them to. If no write-capable Zotero MCP is available, tell the user they can import `references.bib` manually via Zotero's File > Import.

For **(a)**: use the user's subtopic as the new query, go back to Step 2 (pick strategies & search). Append new references to the existing `references.bib` and update `summary.md` with the new findings.
