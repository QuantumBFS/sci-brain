---
name: how-to-download-ref
description: Agentic trigger. Use when adding arXiv IDs or DOIs to a knowledge base — fetches metadata, PDFs, and full text, then updates references.bib and INDEX.md.
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


# how-to-download-ref

## When to use

- A discussion / draft surfaces a paper not yet in the project KB, and you want it indexed for future search.
- The user says "add this ref to the KB", "download arXiv:XXXX", "pull this DOI".
- Bulk-importing a reading list from issue threads / chat history / a `references.bib`.

Do NOT use:
- For GitHub repos / web pages — those are too varied for a single-shot helper.

## Setup

Every helper runs under plain `python3`. Metadata fetching needs nothing else.
Rendering wants **pymupdf4llm** (without it the output is text-only: figures
missing, equations mangled), APS JATS needs **pandoc**, and the Sci-Hub fallback
needs **playwright**. Check the backend you are about to use:

```sh
python3 -c "import pymupdf4llm; print('ok', pymupdf4llm.__version__)"
```

Install commands, the text-only fallback chain, OCR, and `latexpand` are in
[dependencies.md](references/dependencies.md); read only the part you need.

## Inputs

- **One or more arXiv IDs** (e.g. `1806.08734`, `2006.10739`) — strip the `vN` suffix.
- **One or more DOIs** (e.g. `10.1103/PhysRevLett.130.036401`) — lowercase preferred; renderer normalizes.
- **KB path** — see Step 1.

## Files this skill owns vs. doesn't

`how-to-download-ref` writes:
- `$KB/.raw/{arxiv,doi}/<id>.{json,pdf}`
- `$KB/.raw/doi/<safe-doi>.jats.xml` (publisher JATS for APS DOIs)
- `$KB/.raw/doi/<safe-doi>.aps.pdf` and `<safe-doi>-suppl/` (only with `--bagit`)
- `$KB/.raw/{arxiv,doi}/<id>-src/` (extracted e-print source tree — only when LaTeX sources requested)
- `$KB/.raw/{arxiv,doi}/<id>.tex` (flattened LaTeX; <safe-doi> filenames for DOI entries — only when LaTeX sources requested)
- `$KB/.figures/{arxiv__<id>,doi__<safe>}/...`
- `$KB/<id>_<slug>.md` (rendered paper, one per ref)
- `$KB/INDEX.md` (regenerated each run)
- Appends entries to `$KB/references.bib`

`how-to-download-ref` **never touches**:
- `$KB/NOTES.md` — owned by `survey` / `know-me-better` / humans (sub-themes, open problems, bottlenecks).

The canonical bib is `$KB/references.bib` — it lives inside the KB, beside `INDEX.md` and `NOTES.md`. (Older notes may say `$(dirname $KB)/ref.bib`; that project-root path is retired.)

## Workflow

### 1. Resolve the KB

First distinguish adding references from restoring existing caches. For the
latter, resolve the KB and use Restore existing caches below without running the
acquisition/render/append sequence. If the caller passes `--kb <abs-path>`, use
that. Otherwise:

```sh
KB=$(python3 "$DOWNLOAD_REF_DIR/helpers/resolve_kb.py")
if [ -z "$KB" ]; then
  # resolve_kb printed "unresolvable from ..." to stderr and exited 2.
  # Ask the user in chat where the KB should live.
  exit 1
fi
```

For advisor flows (`create-advisor`, `brainstorm-ideas` with a selected advisor), resolve the advisor KB instead: `KB=$(python3 "$DOWNLOAD_REF_DIR/helpers/resolve_kb.py" --advisor <slug>)`. This honors `$SCIBRAIN_KB_DIRNAME` the same way the project-KB form does.

### 2. Confirm the refs aren't already present

```sh
python3 "$DOWNLOAD_REF_DIR/helpers/kb_identity.py" --kb "$KB" --arxiv 1806.08734
python3 "$DOWNLOAD_REF_DIR/helpers/kb_identity.py" --kb "$KB" --doi 10.1103/PhysRevLett.130.036401
```

Exit 0 means `present <path> (matched via doi|arxiv)`, 1 means `missing`, and 2
means an invalid input or operational error. Skip present refs by default.
The fetch helper repeats this identity check, including within a batch; it never
creates another namespace for the same paper unless `--allow-duplicate` is set.
Requests using an entry's existing namespace still acquire missing assets; this
supports the survey handoff from abstract-only metadata to full-text rendering.
Rendering and bibliography appends also avoid identity duplicates.
To restore missing caches for existing entries, use **Restore existing caches** below.

### 3. Build a manifest

**3a. Direct input** (single-shot mode):

```sh
TMP=$(mktemp "${TMPDIR:-/tmp}/sci-brain-refs.XXXXXX")
cat > "$TMP" <<'EOF'
{"arxiv": ["1806.08734", "2006.10739"], "doi": []}
EOF
```

**3b. From an existing `references.bib`** (bulk mode, `--from-bib`):

```sh
TMP=$(mktemp "${TMPDIR:-/tmp}/sci-brain-refs.XXXXXX")
python3 "$DOWNLOAD_REF_DIR/helpers/bibtex_to_manifest.py" "$KB/references.bib" > "$TMP"
```

If the requested bulk scope is unclear, ask the user:

> "I see 59 refs in the manifest. Render all, topic-filtered, or specific IDs?"
> - **(a)** All — proceed with the full manifest
> - **(b)** Topic-filtered — name a heading from `NOTES.md` (skill greps for cite keys under it)
> - **(c)** Specific IDs — paste arXiv IDs / DOIs

For (b) and (c), edit `$TMP` accordingly before continuing.

### 4. Fetch metadata and full text

Unless the user or the calling skill already said whether they want LaTeX
sources, ask once:

> "Fetch arXiv LaTeX sources as full text for these refs?"
> - **(a)** PDF only (default) — bodies come from the PDF in Step 5.
> - **(b)** Also fetch LaTeX sources — add `--download-arxiv-source` here and `--tex-source` in Step 5; refs with source render `full_text: latex`.

Default command (option **a**):

```sh
python3 "$DOWNLOAD_REF_DIR/helpers/fetch_metadata.py" \
  --kb "$KB" --manifest "$TMP" --download-arxiv-pdfs
```

Metadata comes from cached JSON, then Semantic Scholar, then Crossref; PDFs from
open-access sources, then the arXiv preprint. APS (`10.1103/*`) publisher JATS
is fetched automatically when the article is open. `--email` /
`SCIBRAIN_CONTACT_EMAIL` enables Unpaywall.

For source details, APS extras, or DOI misses requiring `scihub_download.py`,
read only the applicable section of [acquisition.md](references/acquisition.md).
Record unavailable assets and continue the remaining references.

### 5. Render PDF to markdown

```sh
python3 "$DOWNLOAD_REF_DIR/helpers/render.py" --kb "$KB"
```

Add `--only-missing` to skip papers that already have a rendered `.md` file (>500 bytes). This is much faster when adding a few papers to a large KB:

```sh
python3 "$DOWNLOAD_REF_DIR/helpers/render.py" --kb "$KB" --only-missing
```

When LaTeX sources were requested, add `--tex-source`:

```sh
python3 "$DOWNLOAD_REF_DIR/helpers/render.py" --kb "$KB" --tex-source
```

No manifest needed — renderer auto-discovers `.raw/{arxiv,doi}/*.json`. Renders new entries; overwrites existing.

**Body priority: JATS > LaTeX > PDF.** A `.jats.xml` in `.raw/doi/` always wins
(`full_text: jats`, plus a `## References` section from the publisher's list).
`--tex-source` is the only switch that prefers a flattened `.tex`
(`full_text: latex`); without it every ref renders from its PDF, even when a
`.tex` sits in `.raw/`. Human frontmatter `note`, `tags`, and `rating` survives
re-rendering; generated bodies refresh from source, so keep prose notes in
NOTES.md. PDF backends: [dependencies.md](references/dependencies.md).

`.raw/` and `.figures/` should stay out of git. Append to `.gitignore` if missing.

### 6. Propose + confirm cite key (per ref, single-shot mode only)

In single-shot mode (Step 3a), ask the user to confirm each new cite key. A
calling skill that passes explicit keys skips the question; in bulk mode (Step
3b) the keys come from `references.bib` directly, so skip this step entirely.

```sh
python3 "$DOWNLOAD_REF_DIR/helpers/append_bibtex.py" propose \
  --kb "$KB" --id 1806.08734 --type arxiv --bib "$KB/references.bib"
```

Output JSON has `proposed_key` (form `lastname_year_firstkeyword`), `title`, `authors`, `year`, `bibtex_with_proposed_key`. With `--bib`, a key already present in the bib is disambiguated by walking to the next content word of the title (existing keys are never renamed). Show the user the proposed key and ask in chat:
- Accept the proposed key
- Use a custom key (free-text)
- Skip this entry

Once confirmed (the key below is an example):

```sh
python3 "$DOWNLOAD_REF_DIR/helpers/append_bibtex.py" append \
  --kb "$KB" --id 1806.08734 --type arxiv \
  --key rahaman_2018_spectral \
  --bib "$KB/references.bib"
```

The helper rewrites the BibTeX cite key, refuses duplicates, appends with one blank-line separator.

### 7. Regenerate INDEX.md

```sh
python3 "$DOWNLOAD_REF_DIR/helpers/index.py" \
  --kb "$KB" \
  --title "<project-or-advisor-slug> — references" \
  --source-note "Reading list and full-text harness."
```

Replace `<project-or-advisor-slug>` with this KB's name. **Once chosen, keep `--title` and `--source-note` byte-identical across runs** — `INDEX.md` is regenerated wholesale every time; drift causes noisy diffs.

### 8. Verify and report

```sh
python3 "$DOWNLOAD_REF_DIR/helpers/kb_doctor.py" --kb "$KB"
```

The offline checker reports named FAIL/WARN findings and exits nonzero for any
FAIL. It checks bibliography/Markdown correspondence, duplicate identities,
required frontmatter and field types, BibTeX fields, index membership, and orphan
caches. `full_text` accepts `jats`, `latex`, `yes`, or `no`.
Use `--checks duplicate-identity,index-sync` to select checks. `--fix` only repairs
INDEX.md, preserving its title, source note, and exclusions. Fix other findings
explicitly; the checker never merges or deletes references.

Tell the user the new cite keys, rendered paths, full-text status, and remaining findings.

## Restore existing caches

For a fresh clone, or missing `.raw/` / `.figures/` assets on entries already
tracked in the KB, run the sync helper instead of the acquisition steps above:

```sh
python3 "$DOWNLOAD_REF_DIR/helpers/kb_sync.py" --kb "$KB"
```

It never rewrites Markdown, INDEX.md, or the bibliography. Requirements and
caveats are in [maintenance.md](references/maintenance.md).

## Human annotations

`note`, `tags`, and `rating` in existing frontmatter survive every render path,
including multiline values and lists. Generated metadata and body text refresh
from source. Keep other prose notes in NOTES.md.

## Completion and handoff

Return cite keys, rendered paths, full-text status (`jats`, `latex`, `yes`, or
`no`), and remaining findings. Remove the temporary manifest. If invoked by
`survey`, `know-me-better`, `create-advisor`, or `brainstorm-ideas`, return to that
workflow with its scope and authorization intact. Continue to a survey report
only when that report is already requested; standalone acquisition ends here.

For unexpected helper output, consult
[troubleshooting.md](references/troubleshooting.md).

## Done checklist

- [ ] `.raw/{arxiv,doi}/<id>.json` exists for every requested id
- [ ] `.raw/{arxiv,doi}/<id>.pdf` exists where the source allows (else recorded as miss)
- [ ] For every `10.1103/*` DOI: either publisher JATS exists (`full_text: jats`) or the actual access/fetch failure and fallback are reported
- [ ] One `<id>_<slug>.md` per distinct paper at `$KB/` root, with frontmatter
- [ ] `$KB/INDEX.md` regenerated, lists each new entry
- [ ] `$KB/references.bib` has the new cite key (no duplicate)
- [ ] User told cite keys, file names, and `full_text` jats/latex/yes/no per ref
- [ ] If the user requested LaTeX sources: `.raw/arxiv/<id>.tex` exists for every arXiv id, and `.raw/doi/<safe>.tex` for every DOI with an arXiv preprint (or the `src-miss` reported)
