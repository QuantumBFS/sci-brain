---
name: fetch-papers
description: Use after a survey registry exists — reads its references.bib, downloads arXiv PDFs (with arXiv-preprint fallback for paywalled DOIs), and renders each PDF to markdown alongside the registry. Adapted from the build-harness pipeline.
---

# fetch-papers

## When to use

- A survey registry has been built (by `survey`, `researchstyle`, or by hand) and you now want the **full text** of those papers — PDFs and rendered markdown — sitting next to the registry for offline reading or downstream processing.
- The user says: "download these papers", "render the registry to markdown", "fetch full text for the survey".

Do NOT use:
- To *create* BibTeX entries — that's `survey` / `researchstyle`. This skill assumes `references.bib` is already populated.
- For sources that aren't arXiv preprints or DOIs (e.g., GitHub repos, web pages, books). The pipeline only handles arXiv and DOI.
- For PDFs gated behind a publisher paywall *with no arXiv preprint* — about 20–40% of recent physics DOIs fall into this gap. The entry will still be processed but rendered with `full_text: no`.

## Inputs

- A registry directory: `<registry-root>/<slug>/` containing `summary.md` and `references.bib`. The user picks the slug.
- BibTeX entries with at least one of:
  - `eprint = {<arxiv-id>}` (e.g., `2401.12345` or `cond-mat/0506438`) — preferred
  - `doi = {<doi>}` — used with arXiv-preprint fallback when available

## Output layout

Everything lands inside the registry directory:

```
<registry-root>/<slug>/
  summary.md                            # untouched
  references.bib                        # untouched
  .raw/arxiv/<id>.{json,pdf}            # metadata + PDF
  .raw/doi/<safe-doi>.{json,pdf}        # metadata + PDF (arxiv-preprint fallback)
  .figures/arxiv__<id>/...              # extracted figures (pymupdf4llm)
  .figures/doi__<safe>/...
  <id>_<title-slug>.md                  # rendered markdown, one per paper
```

`.raw/` and `.figures/` should be gitignored — append them to `.gitignore` if not already excluded.

## Workflow

### 1. Pick the registry

Ask the user which registry to operate on:

> "Which registry's papers should I fetch?"
> Provide `<registry-root>/<slug>/` (e.g., `~/.claude/survey/personal/`, `~/.claude/survey/topological-orders/`).

If the user has only one registry, default to it; otherwise list available slugs by globbing `<registry-root>/*/references.bib`.

Set:

```sh
KB="<registry-root>/<slug>"   # absolute path
```

### 2. Build the manifest from references.bib

```sh
python3 <skill-base-dir>/helpers/bibtex_to_manifest.py "$KB/references.bib" > /tmp/fetch-papers-manifest.json
```

This emits `{"arxiv": [...], "doi": [...]}`. The script logs a count to stderr.

### 3. Confirm scope

Show the user the counts (e.g., `42 arxiv ids, 17 dois`) and ask:

> "Render all 59 papers, or just a subset?"
> - **(a)** All — proceed
> - **(b)** Topic-filtered — name a topic from `summary.md` (skill greps for cite keys under that heading)
> - **(c)** Specific IDs — paste arXiv IDs / DOIs

For (b) and (c), edit `/tmp/fetch-papers-manifest.json` accordingly before continuing.

### 4. Fetch metadata + PDFs

```sh
python3 <skill-base-dir>/helpers/fetch_metadata.py \
  --kb "$KB" \
  --manifest /tmp/fetch-papers-manifest.json \
  --download-arxiv-pdfs
```

This populates `$KB/.raw/{arxiv,doi}/<id>.{json,pdf}` idempotently — re-running won't re-fetch what's already there.

For DOIs whose publisher gates the PDF (APS / Nature / IOP / AAAS), the helper falls back to the arXiv preprint via `externalIds.ArXiv` when present. If even that fails, you'll see a `miss` line in the output and the entry will render with `full_text: no`.

### 5. Render PDFs to markdown

```sh
python3 <skill-base-dir>/helpers/render.py --kb "$KB"
```

No manifest needed — the renderer auto-discovers `.raw/{arxiv,doi}/*.json` under `--kb`. New entries are rendered; existing ones get overwritten.

PDF backend priority (first one that works wins):
1. **`pymupdf4llm`** (preferred) — produces markdown directly from the PDF and **also extracts embedded images**. Images are written to `$KB/.figures/arxiv__<id>/` (or `doi__<safe>/`); the rendered `<id>_<slug>.md` references them via relative `.figures/...` paths so figures display in any markdown viewer rooted at `$KB/`.
2. `markitdown` — text-only fallback for table-heavy PDFs.
3. `pdftotext -layout` — last-resort plain-text fallback.

Install pymupdf4llm with `pip install pymupdf4llm` (pulls in `pymupdf`). If you see `pymupdf4llm not installed; falling back ...` in stderr, the rendered `.md` is still fine but **figures will be missing** — install pymupdf4llm and re-render.

The renderer also has handlers for `github`, `web`, and `stub` sources from the upstream pipeline. They are no-ops here because this skill only feeds it `.raw/arxiv/` and `.raw/doi/`.

### 6. Verify and report

```sh
# Newly rendered files:
ls -t "$KB"/*.md | head
# Frontmatter present:
for f in "$KB"/*.md; do
  case "$(basename "$f")" in summary.md) continue ;; esac
  head -1 "$f" | grep -q '^---$' || echo "MISSING FRONTMATTER: $f"
done
# .raw/ and .figures/ gitignored:
git -C "$KB" check-ignore .raw/ .figures/ 2>/dev/null \
  || echo "WARN: add .raw/ and .figures/ to .gitignore"
```

Tell the user:
- How many papers rendered with `full_text: yes` vs `no`.
- Any `miss` lines from Step 4 (paywalled DOIs with no arXiv preprint).
- Where the rendered files live: `$KB/<id>_<title-slug>.md`.

## Common mistakes

| Mistake | Fix |
| --- | --- |
| Passing a relative `--kb` | Always use an absolute path. The helpers don't `cd`, but figures are written via a `pymupdf4llm` call that does — relative paths get tricky. |
| Forgetting `--download-arxiv-pdfs` in Step 4 | Without it, only metadata is fetched and every entry renders `full_text: no`. |
| Editing the rendered `.md` by hand and losing it on re-render | The renderer overwrites without warning. Edit the `.raw/` source or the renderer logic if you need persistent changes. |
| Leaving `vN` on arXiv IDs in the manifest | `bibtex_to_manifest.py` strips it; if you edit the manifest by hand, strip it yourself. |
| Re-running on a partial registry | Helpers are idempotent — they skip entries whose `.raw/` already exists. Safe to re-run. |

## Done checklist

- [ ] `.raw/{arxiv,doi}/<id>.json` exists for every requested id
- [ ] `.raw/{arxiv,doi}/<id>.pdf` exists where the source allows (else recorded as miss)
- [ ] One new `<id>_<slug>.md` per ref at `$KB/` root, with frontmatter
- [ ] User told the rendered file count, `full_text` yes/no split, and any paywall misses
