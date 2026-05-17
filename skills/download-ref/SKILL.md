---
name: download-ref
description: Use when adding one or a few new references (arXiv ID or DOI) to an existing survey registry — fetches metadata, downloads/renders the arXiv PDF, proposes a cite key (with confirmation), appends BibTeX to `references.bib`, and inserts a row under `summary.md`. Single-shot counterpart to `fetch-papers`.
---

# download-ref

## When to use

- Mid-discussion (typically inside `/ideas`) a paper surfaces that should be added to the active registry.
- The user says "add this DOI to my survey", "pull this arXiv preprint", "save this ref to the topic registry".
- At the end of `/ideas` / `/survey` / `/researchstyle`, when the wrap-up prompts the user to enrich the registry with newly mentioned papers.

Do NOT use:
- For bulk operations on an already-populated `references.bib` whose PDFs are not yet rendered — that's `/fetch-papers`.
- To create a registry from scratch — that's `/survey` or `/researchstyle`.
- For non-arXiv-non-DOI sources (GitHub repos, blog posts, books). The pipeline only handles arXiv and DOI.

## Inputs

- One or more **arXiv IDs** (e.g., `1806.08734`, `2006.10739`). Strip any `arXiv:` prefix and `vN` suffix.
- One or more **DOIs** (e.g., `10.1103/PhysRevLett.130.036401`). Lowercase preferred but the renderer normalizes.
- A **target registry** directory: `<registry-root>/<slug>/` containing `summary.md` + `references.bib`. Both **personal** (e.g., `~/.claude/survey/personal/`) and **topic** registries (e.g., `~/.claude/survey/topological-orders/`) are valid targets.

## Workflow

### 1. Pick the target registry

Default to the registry active in the current session if known (e.g., the topic registry from `/survey`, or the personal registry from `/researchstyle`). Otherwise ask:

> "Which registry should the new ref join?"

List candidates by globbing `<registry-root>/*/references.bib` (check `~/.claude/survey/`, `~/.codex/survey/`, `~/.config/opencode/survey/`, and `.claude/survey/` per the configured platform). Let the user pick via `AskUserQuestion`.

```sh
KB="<registry-root>/<slug>"   # absolute path
```

### 2. Confirm the refs aren't already present

```sh
for id in 1806.08734 2006.10739; do
  [ -f "$KB/.raw/arxiv/$id.json" ] && echo "$id present" || echo "$id missing"
done
for doi in 10.1103/PhysRevLett.130.036401; do
  safe=$(echo "$doi" | tr '/' '-')
  [ -f "$KB/.raw/doi/$safe.json" ] && echo "$doi present" || echo "$doi missing"
done
grep -F "10.1103/PhysRevLett.130.036401" "$KB/references.bib" >/dev/null && echo "doi already in bib"
```

POSIX `[ -f … ]` is zsh-safe; `ls "$KB/.raw/arxiv/$id".*` triggers `no matches found` errors in zsh under `extended_glob`. Helpers are idempotent — re-running with an already-present id is a no-op — so this check is for human-readable status, not gating.

### 3. Build a one-shot manifest

```sh
TMP=/tmp/download-ref-manifest.json
cat > "$TMP" <<'EOF'
{"arxiv": ["1806.08734", "2006.10739"], "doi": []}
EOF
```

For DOIs, drop them into the `doi` list verbatim. Both lists may be present.

### 4. Fetch metadata + arXiv PDFs

Reuses `fetch-papers`' helper — do not re-vendor:

```sh
python3 <skill-base-dir>/../fetch-papers/helpers/fetch_metadata.py \
  --kb "$KB" \
  --manifest "$TMP" \
  --download-arxiv-pdfs
```

This populates `$KB/.raw/{arxiv,doi}/<id>.{json,pdf}` idempotently — re-running won't re-fetch what's already there.

For DOIs whose publisher gates the PDF (APS / Nature / IOP / AAAS), the helper falls back to the arXiv preprint via `externalIds.ArXiv` when present. If even that fails, you'll see a `miss` line in the output and the entry will render with `full_text: no`.

### 5. Propose + confirm cite key (per ref)

For each new id, propose first:

```sh
python3 <skill-base-dir>/helpers/append_bibtex.py propose \
  --kb "$KB" --id 1806.08734 --type arxiv
```

Output is JSON with `proposed_key` (form `lastname_year_firstkeyword`, e.g. `rahaman_2018_spectral`), `title`, `authors`, `year`, `venue`, and `bibtex_with_proposed_key`. Show the user the proposed key together with the title and ask via `AskUserQuestion`:

- Accept the proposed key
- Use a custom key (free-text alternative)
- Skip this entry (don't touch `references.bib`)

Once the user confirms a key, append:

```sh
python3 <skill-base-dir>/helpers/append_bibtex.py append \
  --kb "$KB" --id 1806.08734 --type arxiv \
  --key rahaman_2018_spectral \
  --bib "$KB/references.bib"
```

The helper:
- Rewrites the BibTeX cite key to the confirmed value.
- Refuses to duplicate (greps for `@\w+\{<key>,` first; prints `skip: already present` if so).
- Appends with one blank-line separator.

If the cite key already exists with different content, the helper still skips — investigate manually, then re-run propose with a different key or fix the existing entry.

### 6. Render PDF to markdown

Reuses `fetch-papers`' helper:

```sh
python3 <skill-base-dir>/../fetch-papers/helpers/render.py --kb "$KB"
```

No manifest needed — the renderer auto-discovers `.raw/{arxiv,doi}/*.json` under `--kb`. Renders new entries to `$KB/<id>_<slug>.md` with frontmatter; existing files are overwritten.

PDF backend priority (first one that works wins):
1. **`pymupdf4llm`** (preferred) — markdown directly from the PDF + extracts embedded images. Figures land in `$KB/.figures/arxiv__<id>/` (or `doi__<safe>/`); the rendered `<id>_<slug>.md` references them via relative `.figures/...` paths.
2. `markitdown` — text-only fallback for table-heavy PDFs.
3. `pdftotext -layout` — last-resort plain-text fallback.

Install `pymupdf4llm` with `pip install pymupdf4llm`. If you see `pymupdf4llm not installed; falling back ...` in stderr, the rendered `.md` is still fine but **figures will be missing** — install and re-render.

`.raw/` and `.figures/` should stay out of git — append to `.gitignore` if not already excluded.

### 7. Update `summary.md`

Read `$KB/summary.md`, find the "Papers by sub-theme" section. For each new ref:

- Pick the sub-theme that fits the abstract. If none fits, ask the user via `AskUserQuestion` whether to add a new sub-theme or place the ref under "Misc".
- Insert a row under that sub-theme:
  ```
  - [@<cite-key>] <one-line description distilled from the abstract>
  ```

Keep existing sub-themes intact. Do not rewrite the "Open problems" or "Bottlenecks" sections — those are author-curated.

### 8. Verify and report

```sh
# New md files appear at top level
ls -t "$KB"/*.md | head
# Frontmatter present
for f in "$KB"/*.md; do
  case "$(basename "$f")" in summary.md) continue ;; esac
  head -1 "$f" | grep -q '^---$' || echo "MISSING FRONTMATTER: $f"
done
# Raw blobs gitignored
git -C "$KB" check-ignore .raw/ .figures/ 2>/dev/null \
  || echo "WARN: add .raw/ and .figures/ to .gitignore"
# New cite keys landed
for k in rahaman_2018_spectral; do
  grep -q "@\w*{$k," "$KB/references.bib" || echo "WARN: $k missing from references.bib"
  grep -q "@$k\b" "$KB/summary.md"          || echo "WARN: $k missing from summary.md"
done
```

Tell the user:
- New cite key(s) confirmed and appended to `references.bib`.
- Rendered file path(s) at `$KB/<id>_<slug>.md` and whether `full_text: yes` came through.
- Sub-theme(s) updated in `summary.md`.

## Integration with other skills

- **`/ideas` end-of-session hook**: After Phase 4 wrap-up, the mentor asks:
  > "We discussed N papers during this session. Want to add any to the registry now?"
  Then list candidate IDs/DOIs surfaced in the conversation. For the user's selections, hand off to `/download-ref`.
- **`/survey` and `/researchstyle` end-of-run**: Same prompt — after the registry is built or extended, ask whether any additional refs (mentioned but not searched) should be pulled in via `/download-ref`.
- **`/fetch-papers` relationship**: `download-ref` does the bibtex-add-and-render path for one ref at a time; `fetch-papers` does the bulk render path for an existing `references.bib`. They share helpers but never compete.

## Common mistakes

| Mistake | Fix |
| --- | --- |
| Passing a relative `--kb` | Always absolute. The helpers don't `cd`; figures rely on absolute paths. |
| Forgetting `--download-arxiv-pdfs` in Step 4 | Without it `full_text: no` and Step 6 has nothing to render. |
| Using `arXiv:XXXX` with the prefix or `vN` suffix | Strip both — manifest takes bare ids: `1806.08734`. |
| Editing the rendered `.md` by hand and losing it on re-render | The renderer overwrites without warning. Edit the `.raw/` source or the renderer logic if you need persistent changes. |
| Cite-key collision with different content | Helper skips silently — investigate the existing entry; re-run propose with a different proposed key. |
| Adding to a registry that doesn't exist yet | Run `/survey` or `/researchstyle` first to create `summary.md` + `references.bib`. |

## Done checklist

- [ ] `.raw/{arxiv,doi}/<id>.json` exists for every requested id
- [ ] `.raw/{arxiv,doi}/<id>.pdf` exists where the source allows (else recorded as miss)
- [ ] One new `<id>_<slug>.md` per ref at `$KB/` root, with frontmatter
- [ ] `$KB/references.bib` has the new cite key (no duplicate)
- [ ] `$KB/summary.md` has a row for each new ref under a sub-theme
- [ ] User told cite keys, file names, and `full_text` yes/no per ref
