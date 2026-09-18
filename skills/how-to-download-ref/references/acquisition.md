# Optional acquisition paths

Use the installed `DOWNLOAD_REF_DIR` and resolved `KB` from SKILL.md.
Read the relevant section when handling APS/JATS details, arXiv source output,
missed DOI PDFs, or supplemental material. Dependency setup is in
[dependencies.md](dependencies.md).

**APS DOIs are handled automatically.** For any `10.1103/*` DOI the helper first
calls the [APS Harvest API](https://harvest.aps.org/docs/harvest-api), which serves
the *publisher's own* JATS XML — real sections, MathML3 equations, a structured
reference list — with **no API key and no institutional IP**. This is ground truth
and strictly beats parsing the PDF. Coverage is per *article*, not per journal: you
get `ok` for gold-OA titles (PRX, PRX Quantum, PRResearch, PRAB, PRPER), SCOAP3
titles (PRC, PRD), and any individually CC-licensed article in PRL/PRA/PRB;
`closed` (HTTP 401) falls through to the arXiv and PDF tiers below. Pass `--no-aps`
to skip. The same request both tests access and delivers the text, so there is no
separate open-access lookup to do.

Metadata uses cached JSON, then Semantic Scholar batches of at most 500,
then Crossref for missing DOIs, including deposited metadata normalized to usable
BibTeX. PDF acquisition tries S2's OA URL, Unpaywall repository copies, then the
arXiv preprint. Pass `--email <contact-address>` or set `SCIBRAIN_CONTACT_EMAIL`
to enable Unpaywall and Crossref's polite pool; without an email, Unpaywall is
skipped. API errors and HTML landing pages fall through to the next source.
PDFs must have both a `%PDF` header and `%%EOF` trailer. A DOI miss continues to
the DOI fallback below. Service contracts: [Crossref](https://www.crossref.org/documentation/retrieve-metadata/rest-api/),
[Unpaywall](https://unpaywall.org/products/api).


`--download-arxiv-source` additionally fetches each arXiv paper's e-print
LaTeX source, extracts it to `.raw/arxiv/<id>-src/`, flattens
`\input`/`\include` into `.raw/arxiv/<id>.tex`, and copies the source tree's
figure files into `.figures/arxiv__<id>/`. `src-miss` lines (PDF-only
submissions, withdrawn papers, fetch failures) are fine — those refs fall
back to PDF rendering in the rendering step. DOI entries whose Semantic Scholar record
names an arXiv preprint (`externalIds.ArXiv`) get the same treatment, into
`.raw/doi/<safe>.tex` and `.figures/doi__<safe>/`.

**Tip:** Set `SEMANTIC_SCHOLAR_API_KEY` in your environment to raise the Semantic Scholar rate limit from ~1 req/s to 100 req/s. Get a free key at https://www.semanticscholar.org/product/api#api-key-form.

## Sci-Hub fallback for paywalled PDFs (script)

If the fetch reports `miss` for any DOI (no open-access PDF and no arXiv preprint),
run the browser-based Sci-Hub helper. Pass the missed DOIs:

```sh
python3 "$DOWNLOAD_REF_DIR/helpers/scihub_download.py" --kb "$KB" \
  --doi 10.1111/j.1467-9280.2006.01693.x \
  --doi 10.3102/0034654316689306
```

It tries each mirror in `helpers/scihub_domains.toml` (in order) until one
serves the PDF, solving the mirrors' DDoS-Guard JavaScript challenge with a
headless browser, and saves to `$KB/.raw/doi/<safe>.pdf` (`<safe>` = DOI with
`/` → `-`) — the same place the fetch writes, so render.py picks it up. It
prints one `OK` / `MISS` / `SKIP` line per DOI.

- **Requires Playwright** (see dependencies.md). curl/urllib cannot pass DDoS-Guard.
- **Mirrors rotate.** If every DOI returns `MISS`, the domain list is likely
  stale: web-search "working sci-hub mirror domains <year>" and edit
  `helpers/scihub_domains.toml` (see its header), then re-run.
- If a stricter challenge blocks the headless browser, retry with `--headed`.

Skip this fallback when the requested full text is already available.

## APS extras (optional)

`aps_harvest.py` also runs standalone — useful for backfilling a KB built before
this path existed, or for pulling figures and supplemental material:

```sh
# probe one DOI without writing anything -> prints open | closed | notfound
python3 "$DOWNLOAD_REF_DIR/helpers/aps_harvest.py" --check 10.1103/PhysRevB.108.045101

# backfill JATS for every APS DOI already in the KB
python3 "$DOWNLOAD_REF_DIR/helpers/aps_harvest.py" --kb "$KB" --all

# ...and pull the BagIt package too: published PDF, figures, supplemental material
python3 "$DOWNLOAD_REF_DIR/helpers/aps_harvest.py" --kb "$KB" --all --bagit
```

`--bagit` is the only way to get **supplemental material**, which the arXiv
preprint route cannot provide. It is much heavier (tens of MB per article), so
use it per-DOI rather than across a whole KB.
