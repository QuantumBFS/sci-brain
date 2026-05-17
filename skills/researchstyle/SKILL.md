---
name: researchstyle
description: Use when indexing a paper collection (your own or another researcher's) into a survey registry — supports Zotero library, a PDF folder, or a Google Scholar profile
---

# Researcher Survey Registry

Turn an existing paper collection into a structured survey registry (`summary.md` + `references.bib`). The output uses the same registry format as the `survey` skill — so personal, per-researcher, and topic registries can all be merged.

**Step 1 — Identify the researcher and source.** First, ask whose papers to index:

> "Whose papers should I index? (Give me a name, or leave blank for your own collection.)"

Derive a slug from the name: lowercase, hyphenated (e.g., `jin-guo-liu`, `john-preskill`). If no name is given, or the user says "me" / "myself" / "personal", use the slug `personal`.

Then ask which source to use:

> "Where are the papers?"
> - **(a)** Zotero library
> - **(b)** A PDF folder (give me the path)
> - **(c)** Google Scholar profile (give me the URL)

Note: the Zotero option is only meaningful for the `personal` slug (it's your local DB). For another researcher, choose **(b)** or **(c)**.

**Step 2 — Index the collection.**

**Zotero:**

1. Locate `zotero.sqlite` — check in order: `~/Zotero/`, `~/Library/Application Support/Zotero/`, `~/snap/zotero-snap/common/Zotero/`. If not found, use `find ~ -maxdepth 4 -name "zotero.sqlite"` as fallback. If still not found, ask for the path.

2. Run the bundled script:

```bash
python3 <skill-base-dir>/parse_zotero.py <path-to-zotero.sqlite> <output_dir>
```

The script handles: copying the DB to avoid locking, pivot queries to avoid cartesian products, author extraction, cite key deduplication, topic classification, and generating both `summary.md` and `references.bib`.

3. Review the output — the script's topic classification uses keyword matching and may need manual adjustment. Check the topic distribution it prints and offer to re-classify if the user's field isn't well covered by the default patterns.

4. For papers missing abstracts or DOIs, find the PDF via the `itemAttachments` table. PDFs are at `<zotero-data-dir>/storage/<key>/<filename>.pdf`. Read them to extract the abstract.

**PDF folder:**

1. List all PDFs in the given path.
2. Read each PDF — extract title, authors, year, abstract, DOI/URL from the content.
3. For bulk keyword search: `pdfgrep -r -i "KEYWORD" <folder>` (install via package manager if missing, e.g., `apt install pdfgrep` or `brew install pdfgrep`).

**Google Scholar:**

> **Note:** Google Scholar actively blocks automated access — WebFetch may hit CAPTCHAs or rate limits. If scraping fails, suggest alternatives: export BibTeX manually from the Scholar profile page (Scholar → select all → export BibTeX), use [ORCID](https://orcid.org/) or [DBLP](https://dblp.org/) profiles instead (both have machine-friendly APIs), or switch to the PDF folder method with downloaded papers.

1. Fetch the profile page.
2. Extract paper titles, years, citation counts.
3. For each paper, search for the DOI and abstract via WebSearch.

**Step 3 — Produce the registry.** Output to the global registry path at `<global-registry-root>/<slug>/` (e.g., `~/.claude/survey/personal/` for your own collection, `~/.claude/survey/jin-guo-liu/` for a named researcher), containing:

**1. `summary.md`** — all papers listed by topic cluster, with BibTeX cite keys (e.g., `[AuthorYear]`) as indices.

**2. `references.bib`** — BibTeX entries. Only include entries that have at least a DOI or URL — skip the rest. Every included entry **must** contain:

- `abstract` — the paper's abstract
- `doi` or `url` — at least one identifier for retrieval

**Processing tips:**

- **Always use bundled scripts** (`parse_zotero.py` for Zotero). Don't try to do it inline with shell commands — even for small libraries, a script is more reliable and easier to debug.
- **Topic classification** in the script uses keyword matching ordered most-specific-first. The default patterns cover quantum computing, physics, CS, and math. For other fields, modify `TOPIC_PATTERNS` in the script or ask the user to provide keywords for their domain.

**Step 4 — Wrap-up menu.**

After the registry is written, ask via `AskUserQuestion`:

> "Registry built at `<registry-root>/<slug>/` (N papers). What next?"
> - **(a)** Fetch PDFs for all refs — bulk-download arXiv PDFs and render each to markdown (invokes `fetch-papers`)
> - **(b)** Add specific refs by ID — paste arXiv IDs / DOIs of papers cited in conversation but missing from the source, append them to the registry (invokes `download-ref`)
> - **(c)** Continue to brainstorming — start `/sci-brain:ideas` using this registry as background
> - **(d)** Stop here — keep the registry, end the session

For **(a)**, invoke the `fetch-papers` skill (read `skills/fetch-papers/SKILL.md`) targeting the registry just built. It reads `references.bib`, downloads each arXiv PDF (with arXiv-preprint fallback for paywalled DOIs), and renders to markdown under `.raw/`, `.figures/`, and per-paper `<id>_<slug>.md`.

For **(b)**, invoke the `download-ref` skill (read `skills/download-ref/SKILL.md`) targeting the registry just built. It handles metadata fetch, cite-key confirmation, BibTeX append, PDF render, and `summary.md` row insertion per ref.
