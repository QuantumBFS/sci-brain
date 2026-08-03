# arXiv LaTeX source in the knowledge base — design

Date: 2026-08-03
Status: approved scope — LaTeX-source upgrade only (papis integration considered and deferred, see Non-goals)

## Problem

`download-ref` renders every reference from its PDF via pymupdf4llm. For arXiv
papers we can fetch the LaTeX source (`arxiv.org/e-print/<id>`), which is the
ground truth for equations and structure. PDF→Markdown mangles math badly;
raw LaTeX is read natively by LLM agents. The KB should store LaTeX as the
full-text body for arXiv papers whenever source is available.

## Constraints

- The rendered-file contract is shared beyond this repo: quantum.harness /
  init-harness vendor the same helpers and commit rendered `.md` files as
  agent-facing cite targets. Filenames (`<id>_<slug>.md`), YAML frontmatter
  keys, `INDEX.md` regeneration, `references.bib` append flow, and the
  `.raw/` / `.figures/` layout must not change shape.
- No new hard dependencies. The flattener is pure Python; `latexpand` (TeX
  Live) is used opportunistically when installed.
- PDF→Markdown remains the path for DOI refs, PDF-only arXiv submissions,
  and any source-fetch failure.

## Design

### Fetch (extend `fetch_metadata.py`)

New flag `--download-arxiv-source`, used alongside the existing
`--download-arxiv-pdfs` (PDFs are still fetched — they remain the fallback
and the `.figures/` source for the PDF path):

1. Download `https://arxiv.org/e-print/<id>` with the same sequential 2 s
   rate-limit loop as PDF downloads. Idempotent: skip when
   `.raw/arxiv/<id>.tex` already exists.
2. Detect payload by magic bytes: gzipped tar (typical), single gzipped
   `.tex`, or PDF (PDF-only submission → record, fall back to PDF path).
3. Extract tarballs to `.raw/arxiv/<id>-src/` (guard against path traversal;
   members must resolve inside the target dir).
4. Find the main file: the `.tex` containing `\documentclass`; if several,
   prefer the one containing `\begin{document}`.
5. Flatten to `.raw/arxiv/<id>.tex`: use `latexpand` when on `PATH`;
   otherwise a small built-in Python inliner that recursively resolves
   `\input{...}` / `\include{...}` (bounded depth, missing files left as-is)
   and strips full-line `%` comments. Imperfect flattening is acceptable —
   the consumer is an LLM, and unresolved macros are left untouched.
6. Copy raster/PDF figure files (`.png .jpg .jpeg .pdf`) from the source
   tree into `.figures/arxiv__<id>/`, preserving relative names, so agents
   can locate the files that `\includegraphics{...}` references name.
7. Keep the extracted `<id>-src/` dir (it is inside gitignored `.raw/`).

Failure at any step (404, corrupt tarball, no `\documentclass` found) prints
a `src-miss` status line and leaves the PDF path in charge. Withdrawn papers
serve an HTML error page — the magic-byte check catches this.

### Render (`render.py`)

For an arXiv entry, if `.raw/arxiv/<id>.tex` exists, the body of
`<id>_<slug>.md` is the raw flattened LaTeX (after the usual frontmatter and
metadata header), and frontmatter gets `full_text: latex`. Otherwise the
pymupdf4llm PDF path runs unchanged with `full_text: yes` as today.

- Truthiness contract: any consumer treating `full_text` as yes/no must
  treat `latex` as yes. Audit `index.py` (and quantum.harness's
  `md_to_bibtex.py` convention, which reads frontmatter) during
  implementation; `yes`/`latex` both count as full text.
- The LaTeX body is embedded raw, not fenced — fencing adds noise and the
  files are consumed by Read/Grep, not by Markdown renderers.
- Read source with UTF-8, falling back to Latin-1.

### Documentation

- `skills/download-ref/SKILL.md`: add the flag to Step 4, describe the
  latex-vs-pdf render behavior in Step 5, update the done checklist and the
  final report (`full_text: latex|yes|no` per ref).
- `CLAUDE.md` (project): one-line update to the download-ref description.
- `skills/survey/SKILL.md` / `skills/researchstyle/SKILL.md`: add the flag to
  their fetch invocations.

## Migration / rollout

Nothing breaks for existing KBs; `full_text: yes` entries stay valid. To
upgrade an existing arXiv paper, re-run fetch with `--download-arxiv-source`
and re-render (renderer overwrites, as documented today). No bulk migration
step — upgrades happen opportunistically or on demand via the existing
`--from-bib` bulk mode.

## Error handling summary

| Case | Behavior |
| --- | --- |
| e-print 404 / HTML error page | `src-miss`, PDF path renders |
| PDF-only submission | `src-miss (pdf-only)`, PDF path renders |
| No `\documentclass` in tarball | `src-miss`, PDF path renders |
| `latexpand` absent | Python inliner fallback |
| Unresolvable `\input` | left verbatim in the flattened output |

## Testing

- Real-paper smoke test on a scratch KB: one normal arXiv id (tarball), one
  PDF-only submission, one DOI ref. Verify: `.raw/arxiv/<id>.tex` produced,
  `full_text: latex` frontmatter, figures copied, `INDEX.md` lists all
  entries, DOI ref unchanged.
- Inliner unit check: nested `\input`, missing file, comment stripping.
- Idempotency: second fetch+render run is a no-op apart from overwrite.

## Non-goals

- papis integration (backend, fetcher, or sync) — evaluated 2026-08-03 and
  deferred: its advantages (human query CLI, papis-ask RAG, Zotero interop)
  are complementary rather than a better version of this pipeline, and a
  backend swap would diverge the `.raw/` spec shared with
  quantum.harness/init-harness. Revisit as an optional export/sync if wanted.
- pandoc tex→Markdown conversion (mangles macro-heavy papers).
- LaTeX source for non-arXiv refs.
