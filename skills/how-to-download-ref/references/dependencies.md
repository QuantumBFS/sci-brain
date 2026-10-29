# Dependencies and rendering backends

Every helper runs under plain `python3`. Two of them want third-party packages:
`render.py` needs **pymupdf4llm** (highest-fidelity output, preserves figures) and
`scihub_download.py` needs **playwright**. Without them the renderer degrades to
`markitdown` → `pdftotext`, which is text-only — *figures missing, equations
mangled*. Check the backend needed for the current render before running it:

```sh
python3 -c "import pymupdf4llm; print('ok', pymupdf4llm.__version__)"
```

If that errors, install it for the **same** `python3` the helpers will use:

```sh
python3 -m pip install --user pymupdf4llm
# macOS / Homebrew, or any PEP 668 "externally managed" Python:
python3 -m pip install --user --break-system-packages pymupdf4llm
```

Both scripts also carry [PEP 723](https://peps.python.org/pep-0723/) inline
dependency metadata, so if you happen to have [uv](https://docs.astral.sh/uv/),
`uv run "$DOWNLOAD_REF_DIR/helpers/render.py" ...` resolves those deps on its own and you can skip the
install step entirely. That is an option, not a requirement — the metadata is
inert comments to a plain interpreter.

**Tesseract is not needed for normal papers.** arXiv and APS PDFs are born-digital,
so `render.py` runs `pymupdf4llm` with `use_ocr=NEVER` and only retries with OCR
when a PDF turns out to have no text layer at all — a scanned old paper, usually
from the Sci-Hub tier. Install a language pack only if you hit that:
`tesseract-data-eng` (Arch), `tesseract-ocr-eng` (Debian/Ubuntu), or
`brew install tesseract-lang` (macOS).

On Arch in particular, *any* `tesseract-data-*` satisfies the `tessdata`
dependency, so it is easy to have `tesseract` installed with `eng` absent.

The Sci-Hub fallback (the DOI fallback) additionally needs a Chromium for Playwright to
clear the mirrors' DDoS-Guard challenge. Only required if you expect to hit
paywalled DOIs:

```sh
python3 -m pip install --user playwright && python3 -m playwright install chromium
```

APS DOIs (`10.1103/*`) render from publisher JATS XML, which needs **pandoc**:

```sh
pandoc --version | head -1   # any 2.x/3.x works
```

If missing: `paru -S pandoc-cli` (Arch) / `apt install pandoc` / `brew install pandoc`.
Without it, APS refs silently fall back to the arXiv/PDF tiers.

For arXiv LaTeX sources (optional, when LaTeX sources are requested), `latexpand`
(ships with TeX Live) gives the cleanest flattening; if absent, a built-in Python
inliner is used — no action needed either way.

## MinerU

`mineru_parse.py` is stdlib-only: it talks to MinerU's v1 parse API over HTTPS,
so nothing needs installing and no local GPU is used. By default it calls the
hosted service at `https://mineru.net/api`, which accepts anonymous jobs
(about 200 pages per file; results are kept 30 days on the service). A key
from <https://mineru.net/apiManage/token> raises the quota; the user exports it
themselves, and it must never be written into the KB or the repo:

```sh
export MINERU_API_KEY=...   # optional
```

arXiv papers are submitted as `https://arxiv.org/pdf/<id>` URLs, so the service
fetches them itself and the job returns in about a minute for a 60-page paper.
DOI PDFs have to be uploaded to the service's storage, whose upstream bandwidth
can be a few tens of KB/s from outside China, so a large DOI PDF can take minutes.

`--tier flash|basic|standard` picks the parse model (default: the service
decides, which on mineru.net is its VLM). To run MinerU on your own hardware
instead, start `mineru-api --allow-local-source` (from `uv tool install mineru`)
and point the helper at it with `--api-url http://127.0.0.1:8000` or
`MINERU_API_URL`; it then reads the PDFs straight from `.raw/`.
