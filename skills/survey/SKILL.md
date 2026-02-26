---
name: survey
description: Use when building a literature survey — either indexing a personal paper collection (Zotero, PDF folder, Google Scholar) into a survey registry, or surveying a research topic via parallel exploration strategies
---

Identify available tools. If arxiv MCP is missing, print a warning to the user.

**Two modes — auto-detect or ask:**

If the user already provided a research topic or question, go directly to **Mode B**. Otherwise ask:

> "What kind of survey?"
> - **(a)** Index my papers — build a survey registry from your Zotero library, a PDF folder, or your Google Scholar profile
> - **(b)** Survey a topic — explore a research question using parallel search strategies

---

## Mode A — Personal survey registry

Turn an existing paper collection into a structured survey registry. The output is the same registry format as Mode B — so personal and topic registries can be merged later.

**Step 1 — Locate the source.** Ask which source to index:

> "Where are your papers?"
> - **(a)** Zotero library
> - **(b)** A PDF folder (give me the path)
> - **(c)** Google Scholar profile (give me the URL)

**Step 2 — Index the collection.**

**Zotero:**
1. Locate `zotero.sqlite` at standard paths (`~/Zotero/`, `~/Library/Application Support/Zotero/`). If not found, ask for the path.
2. Query all items:

```bash
sqlite3 ~/Zotero/zotero.sqlite "
  SELECT i.itemID, v_title.value AS title, v_abstract.value AS abstract
  FROM items i
  JOIN itemData id_t ON i.itemID = id_t.itemID
  JOIN itemDataValues v_title ON id_t.valueID = v_title.valueID
  JOIN fields f_t ON id_t.fieldID = f_t.fieldID AND f_t.fieldName = 'title'
  LEFT JOIN itemData id_a ON i.itemID = id_a.itemID
  LEFT JOIN fields f_a ON id_a.fieldID = f_a.fieldID AND f_a.fieldName = 'abstractNote'
  LEFT JOIN itemDataValues v_abstract ON id_a.valueID = v_abstract.valueID
  LIMIT 200;
"
```

3. For papers missing abstracts or DOIs, find the PDF via:

```bash
sqlite3 ~/Zotero/zotero.sqlite "
  SELECT ia.parentItemID, ia.key, ia.contentType
  FROM itemAttachments ia
  WHERE ia.parentItemID IN (ITEM_IDS)
    AND ia.contentType = 'application/pdf';
"
```

PDFs are at `~/Zotero/storage/<key>/<filename>.pdf`. Read them to extract the abstract.

**PDF folder:**
1. List all PDFs in the given path.
2. Read each PDF — extract title, authors, year, abstract, DOI/URL from the content.
3. For bulk keyword search: `pdfgrep -r -i "KEYWORD" <folder>` (install via `brew install pdfgrep` if missing).

**Google Scholar:**
1. Fetch the profile page.
2. Extract paper titles, years, citation counts.
3. For each paper, search for the DOI and abstract via WebSearch.

**Step 3 — Produce the registry.** Output the same two-file format as Mode B:

- `summary.md` — all papers listed by topic cluster, with BibTeX cite keys as indices
- `references.bib` — BibTeX entries with `abstract` and `doi`/`url` for every entry

Save to a location the user specifies, or default to `articles/personal-registry/`.

---

## Mode B — Topic survey

Survey a research topic and produce a focused registry.

**Step 0 — Clarify.** Ask one question to narrow the research topic. Give 2-4 choice options.

**Step 1 — Web search.** Launch N subagents in parallel, each with a different exploration strategy. Every subagent uses **WebSearch only** at this stage — fast and broad.

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

**Step 2 — User picks directions.** Main agent consolidates all findings reports and presents them as numbered options. "Which directions interest you? Pick one or more." The user can select multiple.

**Step 3 — Build registry.** For the selected directions only, generate the full BibTeX. If a reference lacks DOI/URL or abstract, try one of:

- **arxiv MCP** — search for the paper, get abstract and arxiv ID
- **paper-search-mcp** — PubMed, bioRxiv, CrossRef
- **Semantic Scholar MCP** — citation metadata, abstract, DOI

Output the **survey registry** — a folder `articles/survey/<topic>/` containing:

**1. `summary.md`** — references listed as indices categorized by topic, using BibTeX cite keys (e.g., `[AuthorYear]`). Include:

- **Field landscape** — key papers clustered by sub-theme with publication years, active groups, temporal trends
- **Key open problems** — unsolved questions
- **Key bottlenecks** — obstacles preventing progress

**2. `references.bib`** — BibTeX for all references. Every entry **must** contain:

- `abstract` — the paper's abstract
- `doi` or `url` — at least one identifier for retrieval