# Acquisition and rendering troubleshooting

Read the matching row when a helper fails or gives unexpected output. Resource
paths use the installed `DOWNLOAD_REF_DIR` from SKILL.md.

## Common mistakes

| Mistake | Fix |
| --- | --- |
| Passing a relative `--kb` | Always absolute. Helpers don't `cd`; figures depend on absolute paths. |
| Forgetting `--download-arxiv-pdfs` in Step 4 | Without it, refs with no LaTeX source render `full_text: no` — the PDF is the only body for DOIs and PDF-only arXiv submissions. |
| Using `arXiv:XXXX` with prefix or `vN` suffix | Strip both — manifest takes bare ids: `1806.08734`. |
| Editing generated body text and losing it on re-render | Keep prose in NOTES.md. Human frontmatter `note`, `tags`, and `rating` survives re-rendering. |
| Cite-key collision with different content | `append` skips silently. Propose with `--bib` so the key is disambiguated up front (next content word of the title). |
| Drifting `--title` / `--source-note` between runs | `INDEX.md` regenerates wholesale; first-run values are canonical. Copy verbatim from existing `INDEX.md`. |
| Expecting `.figures/` images for `full_text: latex` refs to come from the PDF | They come from the source tarball; PDF image extraction runs only on the PDF path. |
| Rendered from PDF despite a `.tex` in `.raw/` | PDF is the default. To use LaTeX bodies, pass `--tex-source` in Step 5 (and `--download-arxiv-source` in Step 4). |
| APS paper rendered from PDF, math mangled | `pandoc` is missing, or the article is genuinely `closed`. Check with `aps_harvest.py --check <doi>`. |
| Reaching for MinerU/Marker on an APS DOI | Try Harvest first — a 401 is the only thing that justifies parsing a PDF at all. |
| APS DOI reported `notfound` | Harvest matches the DOI suffix case-sensitively; `aps_harvest.canonical_doi` restores APS's capitalisation before the request. Add the journal to `APS_JOURNAL_TOKENS` if a new title 404s. |
