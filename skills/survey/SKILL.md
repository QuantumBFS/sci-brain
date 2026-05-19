---
name: survey
description: Use when surveying a research topic — launches parallel exploration strategies via web search, lets user pick interesting directions, then builds a focused survey registry with BibTeX
---

Before starting, check which MCP servers are available (arxiv, paper-search, Semantic Scholar, Sci-Hub, etc.). Present the detected servers to the user and let them choose which ones to use for this session via `AskUserQuestion` (multi-select). If none are configured, warn the user that the survey will rely on WebSearch only.

If the user already provided a research topic or question, skip the clarification step.

## Topic Survey

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

**Step 4 — Build registry.** For the selected directions only, generate the BibTeX. **Never generate BibTeX from memory** — always verify against an authoritative source.

**KB resolution.** The target KB is the project KB by default:

```sh
KB=$(python3 skills/download-ref/helpers/resolve_kb.py)
```

If `KB` is empty (resolve_kb printed `unresolvable from ...`), ask the user via `AskUserQuestion` for an explicit path. When invoked from `/incarnate` against a specific advisor, override with `<plugin-root>/advisors/<slug>/.knowledge`.

Ensure `$KB/.raw/arxiv/` and `$KB/.raw/doi/` exist (`mkdir -p`).

**Pre-sort the picks.** Split selected papers into:

- **ID-known papers** — DOI or arXiv ID was collected during Steps 2-3
- **ID-unknown papers** — neither was found

**arxiv MCP fast path.** If an arxiv MCP with `export_papers` is configured, batch-export papers with arXiv IDs via `export_papers(arxiv_ids, format="bibtex", include_abstract=True)` and remove them from the lists below.

**Subagent A — ID-known papers (batch lookup).**

1. Single batch call to Semantic Scholar:
   ```
   POST https://api.semanticscholar.org/graph/v1/paper/batch?fields=title,authors,year,journal,abstract,externalIds,citationStyles
   Body: {"ids": ["DOI:10.xxxx/yyyy", "ARXIV:2401.12345", ...]}
   ```
   Up to 500 ids per call.
2. **For each returned paper:** write the full response to `$KB/.raw/{arxiv,doi}/<id>.json` in the exact JSON shape `fetch_metadata.py` produces (top-level keys: `title`, `authors`, `year`, `venue`, `abstract`, `externalIds`, `citationStyles`, `openAccessPdf`). Use `<safe-doi>` (DOI with `/` → `-`) for the filename in `.raw/doi/`.
3. For papers returning `null` from the batch, pick the single most effective fallback (CrossRef for DOI-only, title-match for others).

**Subagent B — ID-unknown papers (title-based lookup).**

For each paper, pick the single most effective method (Semantic Scholar title match, CrossRef, MCP servers, WebFetch publisher page). On success, write the result to `$KB/.raw/{arxiv,doi}/<id>.json` in the same shape as Subagent A.

**Step 4 finalize — bib + INDEX.**

After both subagents complete, for each new ref:

```sh
# Get the auto-proposed key from the JSON.
KEY=$(python3 skills/download-ref/helpers/append_bibtex.py propose \
        --kb "$KB" --id "$ID" --type "$TYPE" | python3 -c 'import sys,json; print(json.load(sys.stdin)["proposed_key"])')
# Append to ref.bib (dedup is free — refuses duplicates).
python3 skills/download-ref/helpers/append_bibtex.py append \
  --kb "$KB" --id "$ID" --type "$TYPE" --key "$KEY" \
  --bib "$(dirname $KB)/ref.bib"
```

Skip per-ref user confirmation — at survey scale (30+ refs) it's unworkable, and survey is the authority for its own cite keys.

Finally, regenerate `INDEX.md`:

```sh
python3 skills/download-ref/helpers/index.py \
  --kb "$KB" \
  --title "<topic-slug> — references" \
  --source-note "Built by /survey on $(date -u +%Y-%m-%d)."
```

**Write NOTES.md.** Write or extend `$KB/NOTES.md` with three sections:

- **Field landscape** — key papers clustered by sub-theme with years, active groups, temporal trends. Reference papers as `[@<cite-key>]`.
- **Key open problems** — unsolved questions.
- **Key bottlenecks** — obstacles preventing progress.

If `NOTES.md` already exists, **extend** rather than overwrite: merge new findings into existing sections, preserve user edits.

**Extending an existing KB** (Survey was run before on this project): read `$(dirname $KB)/ref.bib` first; skip papers already present (match by DOI or exact title); append only new entries.

If the survey reveals the idea is already published, present the prior art and ask the user if they see a different angle before proceeding.

## After Survey — transition checkpoint

Before the menu below, scan the conversation for arXiv IDs / DOIs the user mentioned that the parallel-search strategies didn't surface. If any are missing from `ref.bib`, ask via `AskUserQuestion`:

> "You mentioned N papers that didn't come through the parallel search. Want to pull them in directly?"
> - **(a)** Add all — invoke `download-ref` for each (single-shot mode, with cite-key confirmation per ref)
> - **(b)** Pick a subset
> - **(c)** Skip

After the registry is built:

> "Survey complete. What next?"
> - **(a)** Fetch PDFs for all refs — invokes `download-ref --from-bib $(dirname $KB)/ref.bib --kb $KB`
> - **(b)** Add specific refs by ID — invokes `download-ref` with explicit IDs (single-shot)
> - **(c)** Deeper survey — survey a subtopic, append to this registry (go back to Step 2)
> - **(d)** Ideas — continue to brainstorming in the current session

For **(c)**, use the user's subtopic as the new query, go back to Step 2. Append new references to the existing `ref.bib` and extend `NOTES.md`.

**Optional: export to Zotero.** If a Zotero MCP with write support is configured, offer to create items from `ref.bib`. If not, the user can import `ref.bib` manually via Zotero's File > Import.
