---
name: how-to-build-kb
description: Agentic trigger. Use when turning a list of picked papers into verified knowledge-base entries — references.bib, INDEX.md, and NOTES.md.
---

# Build a knowledge base from picked papers

Non-interactive. The caller has already chosen the papers; this skill verifies them, writes the KB, and returns.

**Input.** A list of papers (title, plus DOI / arXiv ID when known, plus a one-line description and sub-theme) and a target KB. Callers: `survey` Step 3 picks, `know-me-better` collections, `autoresearch` db stage. Generate the BibTeX for exactly these papers. **Never generate BibTeX from memory** — always verify against an authoritative source.

**KB resolution.** The target KB is the project KB by default — `<project>/.knowledge/` unless the user overrides the directory name via `$SCIBRAIN_KB_DIRNAME`:

```sh
KB=$(python3 skills/how-to-download-ref/helpers/resolve_kb.py)
```

If `KB` is empty (resolve_kb printed `unresolvable from ...`), ask the user in chat for an explicit path. When the caller names an advisor, override via `KB=$(python3 skills/how-to-download-ref/helpers/resolve_kb.py --advisor <slug>)` so the path follows `$SCIBRAIN_KB_DIRNAME` too.

Ensure `$KB/.raw/arxiv/` and `$KB/.raw/doi/` exist (`mkdir -p`).

**Pre-sort the input.** Split papers into:

- **ID-known papers** — DOI or arXiv ID was supplied
- **ID-unknown papers** — neither was found

**arxiv MCP fast path.** If an arxiv MCP with `export_papers` is configured, batch-export papers with arXiv IDs via `export_papers(arxiv_ids, format="bibtex", include_abstract=True)` and remove them from the lists below.

**Lookup path A — ID-known papers (batch lookup).**

1. Single batch call to Semantic Scholar:
   ```
   POST https://api.semanticscholar.org/graph/v1/paper/batch?fields=title,authors,year,journal,abstract,externalIds,citationStyles
   Body: {"ids": ["DOI:10.xxxx/yyyy", "ARXIV:2401.12345", ...]}
   ```
   Up to 500 ids per call.
2. **For each returned paper:** write the full response to `$KB/.raw/{arxiv,doi}/<id>.json` in the exact JSON shape `fetch_metadata.py` produces (top-level keys: `title`, `authors`, `year`, `venue`, `abstract`, `externalIds`, `citationStyles`, `openAccessPdf`). Use `<safe-doi>` (DOI with `/` → `-`) for the filename in `.raw/doi/`.
3. For papers returning `null` from the batch, pick the single most effective fallback (CrossRef for DOI-only, title-match for others).

**Lookup path B — ID-unknown papers (title-based lookup).**

For each paper, pick the single most effective method (Semantic Scholar title match, CrossRef, MCP servers, fetching the publisher page). On success, write the result to `$KB/.raw/{arxiv,doi}/<id>.json` in the same shape as lookup path A.

**Finalize — bib + INDEX.**

After both lookup paths complete, for each new ref:

```sh
# Get the auto-proposed key from the JSON.
KEY=$(python3 skills/how-to-download-ref/helpers/append_bibtex.py propose \
        --kb "$KB" --id "$ID" --type "$TYPE" | python3 -c 'import sys,json; print(json.load(sys.stdin)["proposed_key"])')
# Append to the KB's references.bib (dedup is free — refuses duplicates).
python3 skills/how-to-download-ref/helpers/append_bibtex.py append \
  --kb "$KB" --id "$ID" --type "$TYPE" --key "$KEY" \
  --bib "$KB/references.bib"
```

Skip per-ref user confirmation — at KB scale (30+ refs) it's unworkable; this skill is the authority for its own cite keys.

Finally, regenerate `INDEX.md`:

```sh
python3 skills/how-to-download-ref/helpers/index.py \
  --kb "$KB" \
  --title "<topic-slug> — references" \
  --source-note "Built by how-to-build-kb on $(date -u +%Y-%m-%d)."
```

**Write NOTES.md.** Write or extend `$KB/NOTES.md` with three sections:

- **Field landscape** — key papers clustered by sub-theme with years, active groups, temporal trends. Reference papers as `[@<cite-key>]`.
- **Key open problems** — unsolved questions.
- **Key bottlenecks** — obstacles preventing progress.

If `NOTES.md` already exists, **extend** rather than overwrite: merge new findings into existing sections, preserve user edits.

**Extending an existing KB** (the KB already has entries): read `$KB/references.bib` first; skip papers already present (match by DOI or exact title); append only new entries.
