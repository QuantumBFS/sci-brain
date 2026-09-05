---
name: know-me-better
description: User trigger. Use when you want the agent to learn your research style from your papers (Zotero, PDF folder, or Google Scholar) so it speaks your language.
---

## Installed resources

Keep the working directory at the user's project. Resolve this loaded `SKILL.md`
with `Path(path).resolve()` before locating resources; follow symlinks. Bare
`helpers/`, `references/`, and template paths are relative to that real skill
directory. A path written as `skills/<name>/...` means the installed `<name>`
skill's directory from the agent's skill catalog, not a path in the user's project.
Locate each dependency by its public skill name; copied skills need not be siblings.
If a dependency is absent, report the missing skill and install it before that step.
Shared writing files are bundled in `how-to-write-ideas-report/references/`.

Before running the examples, set `DOWNLOAD_REF_DIR` to the absolute directory of `how-to-download-ref`. Quote these variables as shown.


# Know Me Better

Turn an existing paper collection into a structured knowledge base under `<project>/.knowledge/` (or an advisor KB). The output uses the same KB format as the `survey` and `how-to-download-ref` skills — project and advisor KBs can coexist cleanly.

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

   **Important — treat `<output_dir>` as a scratch directory, not the KB.** The script writes legacy-format index files (a topic index and a `.bib` file) into `<output_dir>`. Pick a temp path (e.g., `/tmp/zotero-export-$$/`). Steps 3–6 are the authoritative writes — they read those intermediate files from `<output_dir>` as input data, then emit `.raw/{arxiv,doi}/<id>.json` into `$KB` and append to `$KB/references.bib`. After Steps 3–6 finish, the contents of `<output_dir>` can be deleted.

3. Review the output — the script's topic classification uses keyword matching and may need manual adjustment. Check the topic distribution it prints and offer to re-classify if the user's field isn't well covered by the default patterns.

4. For papers missing abstracts or DOIs, find the PDF via the `itemAttachments` table. PDFs are at `<zotero-data-dir>/storage/<key>/<filename>.pdf`. Read them to extract the abstract.

**PDF folder:**

1. List all PDFs in the given path.
2. Read each PDF — extract title, authors, year, abstract, DOI/URL from the content.
3. For bulk keyword search: `pdfgrep -r -i "KEYWORD" <folder>` (install via package manager if missing, e.g., `apt install pdfgrep` or `brew install pdfgrep`).

**Google Scholar:**

> **Note:** Google Scholar actively blocks automated access — automated fetching may hit CAPTCHAs or rate limits. If scraping fails, suggest alternatives: export BibTeX manually from the Scholar profile page (Scholar → select all → export BibTeX), use [ORCID](https://orcid.org/) or [DBLP](https://dblp.org/) profiles instead (both have machine-friendly APIs), or switch to the PDF folder method with downloaded papers.

1. Fetch the profile page.
2. Extract paper titles, years, citation counts.
3. For each paper, search for the DOI and abstract via web search.

**Processing tips:**

- **Always use bundled scripts** (`parse_zotero.py` for Zotero). Don't try to do it inline with shell commands — even for small libraries, a script is more reliable and easier to debug.
- **Topic classification** in the script uses keyword matching ordered most-specific-first. The default patterns cover quantum computing, physics, CS, and math. For other fields, modify `TOPIC_PATTERNS` in the script or ask the user to provide keywords for their domain.

## Output layout

The KB target is decided by the caller:

```sh
# Standalone (indexes the user's own collection into the project KB):
KB=$(python3 "$DOWNLOAD_REF_DIR/helpers/resolve_kb.py")

# Invoked from /create-advisor (indexes another researcher's collection into the advisor KB):
KB=$(python3 "$DOWNLOAD_REF_DIR/helpers/resolve_kb.py" --advisor <slug>)
```

Ensure `$KB/.raw/arxiv/` and `$KB/.raw/doi/` exist.

## Step 3 — Write `.raw/` JSON per paper

For each indexed paper, write metadata to `$KB/.raw/{arxiv,doi}/<id>.json` in the exact shape `fetch_metadata.py` produces (top-level keys: `title`, `authors`, `year`, `venue`, `abstract`, `externalIds`, `citationStyles`, `openAccessPdf`). Use `<safe-doi>` (DOI with `/` → `-`) for DOI filenames.

For papers without a DOI or arXiv ID, skip — they don't fit the canonical KB; mention them to the user.

## Step 4 — Append to references.bib

Per indexed paper:

```sh
KEY=$(python3 "$DOWNLOAD_REF_DIR/helpers/append_bibtex.py" propose \
        --kb "$KB" --id "$ID" --type "$TYPE" | python3 -c 'import sys,json; print(json.load(sys.stdin)["proposed_key"])')
python3 "$DOWNLOAD_REF_DIR/helpers/append_bibtex.py" append \
  --kb "$KB" --id "$ID" --type "$TYPE" --key "$KEY" \
  --bib "$KB/references.bib"
```

Auto-accept the proposed key — per-paper confirmation is unworkable at 100+ papers.

## Step 5 — Regenerate INDEX.md

```sh
python3 "$DOWNLOAD_REF_DIR/helpers/index.py" \
  --kb "$KB" \
  --title "<advisor-slug or 'project'> — researcher index" \
  --source-note "Built by /know-me-better on $(date -u +%Y-%m-%d)."
```

## Step 6 — Write NOTES.md

Write or extend `$KB/NOTES.md` with:

- **Researcher profile** — name, fields, key themes (from Step 1).
- **Topic clusters** — group cite keys by sub-theme based on the indexed papers.
- **Temporal arc** — early career → recent work, if visible.

Reference papers as `[@<cite-key>]`. If `NOTES.md` exists, extend rather than overwrite.

## After know-me-better — transition checkpoint

After Steps 3–6 complete, the KB is populated with metadata but PDFs aren't downloaded yet. Ask the user in chat:

> "Index built. What next?"
> - **(a)** Fetch PDFs for all refs — invokes `how-to-download-ref --from-bib $KB/references.bib --kb $KB` (bulk mode)
> - **(b)** Add specific refs by ID — invokes `how-to-download-ref` with explicit IDs (single-shot, per-ref cite-key confirmation)
> - **(c)** Continue to `brainstorm-ideas` — start brainstorming with the indexed literature loaded
> - **(d)** Stop — leave the KB as-is

For (a) and (b), see `skills/how-to-download-ref/SKILL.md`. For (c), invoke `brainstorm-ideas` in the current session.
