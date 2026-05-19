---
name: researchstyle
description: Use when indexing a paper collection (your own or another researcher's) into a knowledge base — supports Zotero library, a PDF folder, or a Google Scholar profile
---

# Researcher Survey Registry

Turn an existing paper collection into a structured knowledge base under `<project>/.knowledge/` (or an advisor KB). The output uses the same KB format as the `survey` and `download-ref` skills — project and advisor KBs can coexist cleanly.

**Step 1 — Identify the researcher and source.** First, ask whose papers to index:

> "Whose papers should I index? (Give me a name, or leave blank for your own collection.)"

Then ask which source to use:

> "Where are the papers?"
> - **(a)** Zotero library
> - **(b)** A PDF folder (give me the path)
> - **(c)** Google Scholar profile (give me the URL)

Note: the Zotero option is only meaningful for indexing your own collection (it's your local DB). For another researcher, choose **(b)** or **(c)**.

**Step 2 — Index the collection.**

**Zotero:**

1. Locate `zotero.sqlite` — check in order: `~/Zotero/`, `~/Library/Application Support/Zotero/`, `~/snap/zotero-snap/common/Zotero/`. If not found, use `find ~ -maxdepth 4 -name "zotero.sqlite"` as fallback. If still not found, ask for the path.

2. Run the bundled script:

```bash
python3 <skill-base-dir>/parse_zotero.py <path-to-zotero.sqlite> <output_dir>
```

The script handles: copying the DB to avoid locking, pivot queries to avoid cartesian products, author extraction, cite key deduplication, topic classification, and generating structured output.

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

**Processing tips:**

- **Always use bundled scripts** (`parse_zotero.py` for Zotero). Don't try to do it inline with shell commands — even for small libraries, a script is more reliable and easier to debug.
- **Topic classification** in the script uses keyword matching ordered most-specific-first. The default patterns cover quantum computing, physics, CS, and math. For other fields, modify `TOPIC_PATTERNS` in the script or ask the user to provide keywords for their domain.

## Output layout

The KB target is decided by the caller:

```sh
# Standalone (indexes the user's own collection into the project KB):
KB=$(python3 skills/download-ref/helpers/resolve_kb.py)

# Invoked from /incarnate (indexes another researcher's collection into the advisor KB):
KB="<plugin-root>/advisors/<slug>/.knowledge"
```

Ensure `$KB/.raw/arxiv/` and `$KB/.raw/doi/` exist.

## Step 3 — Write `.raw/` JSON per paper

For each indexed paper, write metadata to `$KB/.raw/{arxiv,doi}/<id>.json` in the exact shape `fetch_metadata.py` produces (top-level keys: `title`, `authors`, `year`, `venue`, `abstract`, `externalIds`, `citationStyles`, `openAccessPdf`). Use `<safe-doi>` (DOI with `/` → `-`) for DOI filenames.

For papers without a DOI or arXiv ID, skip — they don't fit the canonical KB; mention them to the user.

## Step 4 — Append to ref.bib

Per indexed paper:

```sh
KEY=$(python3 skills/download-ref/helpers/append_bibtex.py propose \
        --kb "$KB" --id "$ID" --type "$TYPE" | python3 -c 'import sys,json; print(json.load(sys.stdin)["proposed_key"])')
python3 skills/download-ref/helpers/append_bibtex.py append \
  --kb "$KB" --id "$ID" --type "$TYPE" --key "$KEY" \
  --bib "$(dirname $KB)/ref.bib"
```

Auto-accept the proposed key — per-paper confirmation is unworkable at 100+ papers.

## Step 5 — Regenerate INDEX.md

```sh
python3 skills/download-ref/helpers/index.py \
  --kb "$KB" \
  --title "<advisor-slug or 'project'> — researcher index" \
  --source-note "Built by /researchstyle on $(date -u +%Y-%m-%d)."
```

## Step 6 — Write NOTES.md

Write or extend `$KB/NOTES.md` with:

- **Researcher profile** — name, fields, key themes (from Step 1).
- **Topic clusters** — group cite keys by sub-theme based on the indexed papers.
- **Temporal arc** — early career → recent work, if visible.

Reference papers as `[@<cite-key>]`. If `NOTES.md` exists, extend rather than overwrite.
