---
name: how-to-build-kb
description: Agentic trigger. Use when turning a list of picked papers into verified knowledge-base entries — references.bib, INDEX.md, and NOTES.md.
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


# Build a knowledge base from picked papers

Non-interactive. The caller has already chosen the papers; this skill verifies them, writes the KB, and returns.

**Input.** A list of papers (title, plus DOI / arXiv ID when known, plus a one-line description and sub-theme) and a target KB. Callers: `survey` Step 3 picks, `know-me-better` collections, `autoresearch` db stage. Generate the BibTeX for exactly these papers. **Never generate BibTeX from memory** — always verify against an authoritative source.

**KB resolution.** The target KB is the project KB by default — `<project>/.knowledge/` unless the user overrides the directory name via `$SCIBRAIN_KB_DIRNAME`:

```sh
KB=$(python3 "$DOWNLOAD_REF_DIR/helpers/resolve_kb.py")
```

If `KB` is empty (resolve_kb printed `unresolvable from ...`), ask the user in chat for an explicit path. When the caller names an advisor, override via `KB=$(python3 "$DOWNLOAD_REF_DIR/helpers/resolve_kb.py" --advisor <slug>)` so the path follows `$SCIBRAIN_KB_DIRNAME` too.

Ensure `$KB/.raw/arxiv/` and `$KB/.raw/doi/` exist (`mkdir -p`).

**Pre-sort the input.** Split papers into:

- **ID-known papers** — DOI or arXiv ID was supplied
- **ID-unknown papers** — neither was found

**arxiv MCP fast path.** If an arxiv MCP with `export_papers` is configured, batch-export papers with arXiv IDs via `export_papers(arxiv_ids, format="bibtex", include_abstract=True)` and remove them from the lists below.

**Lookup path A — ID-known papers (batch lookup).**

Create a manifest `{"arxiv": [...], "doi": [...]}` and run:

```sh
python3 "$DOWNLOAD_REF_DIR/helpers/fetch_metadata.py" --kb "$KB" --manifest "$TMP"
```

This checks DOI/arXiv identities across tracked entries and cached metadata,
skips existing papers, batches S2 lookups, and falls back to Crossref for missing
DOIs. Do not bypass this check by writing a second namespace manually. For
MCP/title-based results, check both external identifiers with `kb_identity.py`
before saving metadata. After acquisition, render new entries:

```sh
python3 "$DOWNLOAD_REF_DIR/helpers/render.py" --kb "$KB" --only-missing
```

**Lookup path B — ID-unknown papers (title-based lookup).**

For each paper, pick the single most effective method (Semantic Scholar title match, CrossRef, MCP servers, fetching the publisher page). On success, write the result to `$KB/.raw/{arxiv,doi}/<id>.json` in the same shape as lookup path A.

**Finalize — bib + INDEX.**

After both lookup paths complete, for each new ref:

```sh
# Get the auto-proposed key from the JSON.
KEY=$(python3 "$DOWNLOAD_REF_DIR/helpers/append_bibtex.py" propose \
        --kb "$KB" --id "$ID" --type "$TYPE" | python3 -c 'import sys,json; print(json.load(sys.stdin)["proposed_key"])')
# Append to the KB's references.bib (dedup is free — refuses duplicates).
python3 "$DOWNLOAD_REF_DIR/helpers/append_bibtex.py" append \
  --kb "$KB" --id "$ID" --type "$TYPE" --key "$KEY" \
  --bib "$KB/references.bib"
```

Skip per-ref user confirmation — at KB scale (30+ refs) it's unworkable; this skill is the authority for its own cite keys.

Finally, regenerate `INDEX.md`:

```sh
python3 "$DOWNLOAD_REF_DIR/helpers/index.py" \
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
