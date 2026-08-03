---
name: download-ref
description: Use when adding one or many new references (arXiv ID or DOI) to a sci-brain knowledge base — `<project>/.knowledge/` by default, or `advisors/<slug>/.knowledge/` when invoked from an advisor flow. Fetches metadata via Semantic Scholar, downloads PDFs (with SciHub fallback), renders to markdown, regenerates `INDEX.md`, and appends to the KB's `references.bib`. Handles both single refs and bulk-from-bib batches.
---

# download-ref

## When to use

- A discussion / draft surfaces a paper not yet in the project KB, and you want it indexed for future search.
- The user says "add this ref to the KB", "download arXiv:XXXX", "pull this DOI".
- Bulk-importing a reading list from issue threads / chat history / a `references.bib`.

Do NOT use:
- For GitHub repos / web pages — those are too varied for a single-shot helper.

## Preflight (run once per machine)

The renderer uses **pymupdf4llm** for highest-fidelity output (preserves figures). Fallbacks (`markitdown` → `pdftotext`) are text-only — *figures silently missing*. Verify before fetching:

```sh
python3 -c "import pymupdf4llm; print('ok', pymupdf4llm.__version__)"
```

If that errors, install for the **same** `python3` the helpers will use:

```sh
# macOS / Homebrew Python
/opt/homebrew/bin/python3 -m pip install --user --break-system-packages pymupdf4llm

# Linux / system Python
python3 -m pip install --user pymupdf4llm
```

The Sci-Hub fallback (Step 4b) drives a real browser to clear the mirrors'
DDoS-Guard challenge, so it needs **Playwright** with a Chromium. Only required
if you expect to hit paywalled DOIs:

```sh
python3 -m pip install --user playwright && python3 -m playwright install chromium
```

For arXiv LaTeX sources (Step 4), `latexpand` (ships with TeX Live) gives the
cleanest flattening; if absent, a built-in Python inliner is used — no action
needed either way.

## Inputs

- **One or more arXiv IDs** (e.g. `1806.08734`, `2006.10739`) — strip the `vN` suffix.
- **One or more DOIs** (e.g. `10.1103/PhysRevLett.130.036401`) — lowercase preferred; renderer normalizes.
- **KB path** — see Step 1.

## Files this skill owns vs. doesn't

`download-ref` writes:
- `$KB/.raw/{arxiv,doi}/<id>.{json,pdf}`
- `$KB/.raw/arxiv/<id>-src/` (extracted e-print source tree)
- `$KB/.raw/arxiv/<id>.tex` (flattened LaTeX)
- `$KB/.figures/{arxiv__<id>,doi__<safe>}/...`
- `$KB/<id>_<slug>.md` (rendered paper, one per ref)
- `$KB/INDEX.md` (regenerated each run)
- Appends entries to `$KB/references.bib`

`download-ref` **never touches**:
- `$KB/NOTES.md` — owned by `survey` / `researchstyle` / humans (sub-themes, open problems, bottlenecks).

The canonical bib is `$KB/references.bib` — it lives inside the KB, beside `INDEX.md` and `NOTES.md`. (Older notes may say `$(dirname $KB)/ref.bib`; that project-root path is retired.)

## Workflow

### 1. Resolve the KB

If the caller passes `--kb <abs-path>`, use that. Otherwise:

```sh
KB=$(python3 skills/download-ref/helpers/resolve_kb.py)
if [ -z "$KB" ]; then
  # resolve_kb printed "unresolvable from ..." to stderr and exited 2.
  # Ask the user via AskUserQuestion where the KB should live.
  exit 1
fi
```

For advisor flows (`/incarnate`, `/brainstorm-ideas` with a selected advisor), resolve the advisor KB instead: `KB=$(python3 skills/download-ref/helpers/resolve_kb.py --advisor <slug>)`. This honors `$SCIBRAIN_KB_DIRNAME` the same way the project-KB form does.

### 2. Confirm the refs aren't already present

```sh
for id in 1806.08734 2006.10739; do
  [ -f "$KB/.raw/arxiv/$id.json" ] && echo "$id present" || echo "$id missing"
done
for doi in 10.1103/PhysRevLett.130.036401; do
  safe=$(echo "$doi" | tr '/' '-')
  [ -f "$KB/.raw/doi/$safe.json" ] && echo "$doi present" || echo "$doi missing"
done
```

Helpers are idempotent — this check is for human-readable status, not gating.

### 3. Build a manifest

**3a. Direct input** (single-shot mode):

```sh
TMP=/tmp/download-ref-manifest.json
cat > "$TMP" <<'EOF'
{"arxiv": ["1806.08734", "2006.10739"], "doi": []}
EOF
```

**3b. From an existing `references.bib`** (bulk mode, `--from-bib`):

```sh
TMP=/tmp/download-ref-manifest.json
python3 skills/download-ref/helpers/bibtex_to_manifest.py "$KB/references.bib" > "$TMP"
```

When in bulk mode, optionally ask the user:

> "I see 59 refs in the manifest. Render all, topic-filtered, or specific IDs?"
> - **(a)** All — proceed with the full manifest
> - **(b)** Topic-filtered — name a heading from `NOTES.md` (skill greps for cite keys under it)
> - **(c)** Specific IDs — paste arXiv IDs / DOIs

For (b) and (c), edit `$TMP` accordingly before continuing.

### 4. Fetch metadata + arXiv PDFs/sources

```sh
python3 skills/download-ref/helpers/fetch_metadata.py \
  --kb "$KB" \
  --manifest "$TMP" \
  --download-arxiv-pdfs \
  --download-arxiv-source
```

Populates `$KB/.raw/{arxiv,doi}/<id>.{json,pdf}` idempotently. PDFs are downloaded sequentially with 2s sleep between requests to avoid arXiv rate limits. Each PDF is verified for a `%%EOF` trailer; truncated downloads are discarded and retried. For DOIs whose publisher gates the PDF (APS / Nature / IOP / AAAS / ACS), the helper falls back to the arXiv preprint via `externalIds.ArXiv` when present. If even that fails, you'll see a `miss` line — go to Step 4b.

`--download-arxiv-source` additionally fetches each arXiv paper's e-print
LaTeX source, extracts it to `.raw/arxiv/<id>-src/`, flattens
`\input`/`\include` into `.raw/arxiv/<id>.tex`, and copies the source tree's
figure files into `.figures/arxiv__<id>/`. `src-miss` lines (PDF-only
submissions, withdrawn papers, fetch failures) are fine — those refs fall
back to PDF rendering in Step 5.

**Tip:** Set `SEMANTIC_SCHOLAR_API_KEY` in your environment to raise the Semantic Scholar rate limit from ~1 req/s to 100 req/s. Get a free key at https://www.semanticscholar.org/product/api#api-key-form.

### 4b. Sci-Hub fallback for paywalled PDFs (script)

If Step 4 reports `miss` for any DOI (no open-access PDF and no arXiv preprint),
run the browser-based Sci-Hub helper. Pass the missed DOIs:

```sh
python3 skills/download-ref/helpers/scihub_download.py --kb "$KB" \
  --doi 10.1111/j.1467-9280.2006.01693.x \
  --doi 10.3102/0034654316689306
```

It tries each mirror in `helpers/scihub_domains.toml` (in order) until one
serves the PDF, solving the mirrors' DDoS-Guard JavaScript challenge with a
headless browser, and saves to `$KB/.raw/doi/<safe>.pdf` (`<safe>` = DOI with
`/` → `-`) — the same place Step 4 writes, so Step 5 (render) picks it up. It
prints one `OK` / `MISS` / `SKIP` line per DOI.

- **Requires Playwright** (see Preflight). curl/urllib cannot pass DDoS-Guard.
- **Mirrors rotate.** If every DOI returns `MISS`, the domain list is likely
  stale: web-search "working sci-hub mirror domains <year>" and edit
  `helpers/scihub_domains.toml` (see its header), then re-run.
- If a stricter challenge blocks the headless browser, retry with `--headed`.

Skip this step if all PDFs were fetched in Step 4.

### 5. Render PDF to markdown

```sh
python3 skills/download-ref/helpers/render.py --kb "$KB"
```

Add `--only-missing` to skip papers that already have a rendered `.md` file (>500 bytes). This is much faster when adding a few papers to a large KB:

```sh
python3 skills/download-ref/helpers/render.py --kb "$KB" --only-missing
```

No manifest needed — renderer auto-discovers `.raw/{arxiv,doi}/*.json`. Renders new entries; overwrites existing.

PDF backend priority:
1. **`pymupdf4llm`** — markdown + extracted images into `$KB/.figures/`.
2. `markitdown` — text-only fallback.
3. `pdftotext -layout` — last-resort fallback.

arXiv refs with a flattened `.raw/arxiv/<id>.tex` are rendered with the raw
LaTeX as the full-text body (`full_text: latex` in frontmatter) — ground
truth for equations, read natively by agents. The PDF backends above apply
only to refs without LaTeX source (DOIs, PDF-only arXiv submissions).

`.raw/` and `.figures/` should stay out of git. Append to `.gitignore` if missing.

### 6. Propose + confirm cite key (per ref, single-shot mode only)

In single-shot mode (Step 3a), ask the user to confirm each new cite key. In bulk mode (Step 3b), the keys come from `references.bib` directly — skip this step.

```sh
python3 skills/download-ref/helpers/append_bibtex.py propose \
  --kb "$KB" --id 1806.08734 --type arxiv
```

Output JSON has `proposed_key` (form `lastname_year_firstkeyword`), `title`, `authors`, `year`, `bibtex_with_proposed_key`. Show the user via `AskUserQuestion`:
- Accept the proposed key
- Use a custom key (free-text)
- Skip this entry

Once confirmed:

```sh
python3 skills/download-ref/helpers/append_bibtex.py append \
  --kb "$KB" --id 1806.08734 --type arxiv \
  --key rahaman_2018_spectral \
  --bib "$KB/references.bib"
```

The helper rewrites the BibTeX cite key, refuses duplicates, appends with one blank-line separator.

### 7. Regenerate INDEX.md

```sh
python3 skills/download-ref/helpers/index.py \
  --kb "$KB" \
  --title "<project-or-advisor-slug> — references" \
  --source-note "Reading list and full-text harness."
```

Replace `<project-or-advisor-slug>` with this KB's name. **Once chosen, keep `--title` and `--source-note` byte-identical across runs** — `INDEX.md` is regenerated wholesale every time; drift causes noisy diffs.

### 8. Verify and report

```sh
# New md files appear at top level
ls -t "$KB"/*.md | head
# Frontmatter present
for f in "$KB"/*.md; do
  case "$(basename "$f")" in INDEX.md|NOTES.md) continue ;; esac
  head -1 "$f" | grep -q '^---$' || echo "MISSING FRONTMATTER: $f"
done
# Raw blobs gitignored
KB_NAME=$(basename "$KB")
git -C "$(dirname "$KB")" check-ignore "$KB_NAME/.raw/" 2>/dev/null \
  || echo "WARN: $KB_NAME/.raw/ not gitignored"
# INDEX picked up the new ids
for id in 1806.08734 2006.10739; do
  grep -q "$id" "$KB/INDEX.md" || echo "WARN: $id missing from INDEX.md"
done
```

Tell the user: new cite key(s), rendered file path(s), `full_text` latex/yes/no per ref.

## After download — hand off to survey-writer

After the done checklist passes, offer the pipeline's final stage:

> "Papers downloaded and rendered. Write the review?"
> - **(a)** Write a review — invokes `survey-writer` to produce a technology assessment from the rendered KB. This is the final stage of the `survey` → `download-ref` → `survey-writer` pipeline.
> - **(b)** Done — stop here.

## Integration with other skills

- **`/survey`** (upstream): writes/extends `$KB/NOTES.md`, appends to `$KB/references.bib`, regenerates `$KB/INDEX.md`, then hands off to `/download-ref` to fetch PDFs and render full text. The survey's transition checkpoint offers this directly.
- **`/survey-writer`** (downstream): consumes the rendered KB (full-text `.md` files + `$KB/references.bib`) to produce a structured technology assessment report.
- **`/survey` / `/researchstyle`**: write their own `.raw/` JSON via batched fetches and call `append_bibtex.py` directly (skipping the per-ref confirmation in Step 6). They invoke `index.py` at the end of their run.
- **`/brainstorm-ideas` end-of-session**: surfaces candidate IDs/DOIs from the conversation; for the user's selections, invokes `/download-ref` in single-shot mode.
- **`/incarnate`**: invokes `/download-ref` (or `/researchstyle`) targeting the advisor KB resolved by `python3 skills/download-ref/helpers/resolve_kb.py --advisor <slug>`.

## Common mistakes

| Mistake | Fix |
| --- | --- |
| Passing a relative `--kb` | Always absolute. Helpers don't `cd`; figures depend on absolute paths. |
| Forgetting `--download-arxiv-pdfs` in Step 4 | Without it, refs with no LaTeX source render `full_text: no` — the PDF is the only body for DOIs and PDF-only arXiv submissions. |
| Using `arXiv:XXXX` with prefix or `vN` suffix | Strip both — manifest takes bare ids: `1806.08734`. |
| Editing the rendered `.md` and losing it on re-render | Renderer overwrites without warning. Edit `.raw/` source or renderer logic. |
| Cite-key collision with different content | Helper skips silently — investigate, re-run propose with a different key. |
| Drifting `--title` / `--source-note` between runs | `INDEX.md` regenerates wholesale; first-run values are canonical. Copy verbatim from existing `INDEX.md`. |
| Expecting `.figures/` images for `full_text: latex` refs to come from the PDF | They come from the source tarball; PDF image extraction runs only on the PDF path. |

## Done checklist

- [ ] `.raw/{arxiv,doi}/<id>.json` exists for every requested id
- [ ] `.raw/{arxiv,doi}/<id>.pdf` exists where the source allows (else recorded as miss)
- [ ] One new `<id>_<slug>.md` per ref at `$KB/` root, with frontmatter
- [ ] `$KB/INDEX.md` regenerated, lists each new entry
- [ ] `$KB/references.bib` has the new cite key (no duplicate)
- [ ] User told cite keys, file names, and `full_text` latex/yes/no per ref
- [ ] `.raw/arxiv/<id>.tex` exists for every arXiv id (or its `src-miss` reported)
