#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pymupdf4llm"]
# ///
"""Render the .raw/ assets into .knowledge/ markdown.

Reads:
- .raw/{arxiv,doi}/<id>.json — Semantic Scholar metadata (from fetch_metadata.py)
- .raw/{arxiv,doi}/<id>.pdf — original PDFs (optional; rendered as full-text section)
- .raw/doi/<safe>.jats.xml — publisher JATS from the APS Harvest API (optional;
  ALWAYS preferred as the full-text body when present — it is the published
  version, with exact TeX from MathML and a structured reference list)
- .raw/{arxiv,doi}/<id>.tex — flattened arXiv LaTeX source (optional; used as the
  full-text body ONLY with --tex-source; otherwise PDF->markdown is the default)
- .raw/repos/<owner>-<repo>/ — shallow clones (rendered as README + ls-tree)
- .raw/web/<slug>.html or .raw/web/<slug>/ subdir — web page or local source dir
- A manifest JSON describing web entries and bib stubs (titles/sources/notes)

Manifest schema (web/stub only — arxiv/doi/github are auto-discovered from .raw/):
  {
    "web":  {"<slug>": {"source_url": "...", "title": "...", "note": "..."}},
    "stub": [{"slug": ..., "title": ..., "authors": ..., "note": ...}, ...]
  }

Usage:
    render.py --kb /abs/path/.knowledge --manifest manifest.json
    render.py --kb /abs/path/.knowledge --tex-source   # prefer LaTeX bodies when .tex exists
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SLUG_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def slugify(s: str, max_len: int = 60) -> str:
    s = SLUG_NON_ALNUM.sub("-", s.lower()).strip("-")
    return s[:max_len].rstrip("-")


def yaml_escape(s: str) -> str:
    s = (s or "").replace('"', '\\"').replace("\n", " ").strip()
    return f'"{s}"'


def render_frontmatter(meta: dict) -> str:
    lines = ["---"]
    for k in ("source", "type", "canonical_id", "title", "authors",
              "year", "venue", "arxiv_id", "doi"):
        v = meta.get(k)
        if v not in (None, ""):
            lines.append(f"{k}: {yaml_escape(str(v))}")
    if meta.get("full_text"):
        lines.append(f"full_text: {meta['full_text']}")
    if meta.get("note"):
        lines.append(f"note: {yaml_escape(meta['note'])}")
    lines.append("---")
    return "\n".join(lines)


def authors_str(s2: dict) -> str:
    return ", ".join(a.get("name", "?") for a in (s2.get("authors") or []))


def venue_line(s2: dict) -> str:
    venue = s2.get("venue") or (s2.get("journal") or {}).get("name") or "preprint"
    j = s2.get("journal") or {}
    parts = [venue]
    if j.get("volume"):
        parts.append(f"vol. {j['volume']}")
    if j.get("pages"):
        parts.append(f"pp. {j['pages']}")
    parts.append(str(s2.get("year", "?")))
    return ", ".join(parts)


def extract_pdf_text(pdf: Path, kb: Path | None = None, fig_subdir: str | None = None) -> str:
    """Render a PDF to markdown.

    Priority: pymupdf4llm (preserves images) → markitdown → pdftotext -layout.
    pymupdf4llm produces markdown with image references; images are written to
    ``kb/.figures/<fig_subdir>/`` and links in the returned markdown are relative
    to ``kb/`` (so they resolve from the rendered ``kb/<slug>.md``).
    """
    text = ""
    if kb is not None and fig_subdir:
        try:
            import pymupdf4llm  # type: ignore
            try:
                from pymupdf4llm.ocr import OCRMode  # pymupdf4llm >= 1.28
            except ImportError:
                OCRMode = None
            fig_abs = kb / ".figures" / fig_subdir
            fig_abs.mkdir(parents=True, exist_ok=True)
            rel_path = f".figures/{fig_subdir}"
            def _to_md(**extra):
                old_cwd = os.getcwd()
                try:
                    os.chdir(kb)
                    return pymupdf4llm.to_markdown(
                        str(pdf),
                        write_images=True,
                        image_path=rel_path,
                        image_format="png",
                        **extra,
                    )
                finally:
                    os.chdir(old_cwd)

            # Papers from arXiv/APS are born-digital: the text layer is already
            # there, so OCR buys nothing, costs a lot of time, and drags in a
            # hard tessdata dependency. Worse, pymupdf4llm's default
            # (select-keep) OCRs pages it judges sparse, and a single page whose
            # OCR cannot initialise raises and discards the WHOLE document.
            # Skip it, and only reach for OCR if the text layer really is empty
            # -- a scanned old paper, typically via the Sci-Hub tier.
            md = _to_md(use_ocr=OCRMode.NEVER) if OCRMode else _to_md()
            if OCRMode and (not md or len(md.strip()) <= 100):
                print(f"  {pdf.name}: no text layer, retrying with OCR", file=sys.stderr)
                md = _to_md()
            if md and len(md.strip()) > 100:
                text = md
        except ImportError:
            print("  pymupdf4llm not installed; falling back to markitdown/pdftotext", file=sys.stderr)
        except Exception as e:
            print(f"  pymupdf4llm {pdf.name}: {e}", file=sys.stderr)
            if "esseract" in str(e):
                print("  ^ This PDF has no text layer, so it needs OCR, and the English "
                      "Tesseract pack is missing. Install it (tesseract-data-eng on Arch "
                      "-- note any tesseract-data-* satisfies the `tessdata` dependency "
                      "there, so `eng` is easy to end up without; tesseract-ocr-eng on "
                      "Debian/Ubuntu; `brew install tesseract-lang` on macOS). "
                      "Born-digital papers do not reach this path.",
                      file=sys.stderr)

    tmp_md = Path("/tmp") / (pdf.stem + ".md")
    tmp_txt = Path("/tmp") / (pdf.stem + ".txt")
    if not text:
        try:
            r = subprocess.run(["markitdown", str(pdf), "-o", str(tmp_md)],
                               capture_output=True, text=True, timeout=300)
            if r.returncode == 0 and tmp_md.exists() and tmp_md.stat().st_size > 100:
                text = tmp_md.read_text(errors="replace")
        except Exception as e:
            print(f"  markitdown {pdf.name}: {e}", file=sys.stderr)
    if not text:
        try:
            r = subprocess.run(["pdftotext", "-layout", str(pdf), str(tmp_txt)],
                               capture_output=True, text=True, timeout=120)
            if r.returncode == 0 and tmp_txt.exists():
                text = tmp_txt.read_text(errors="replace")
                print(f"  WARNING {pdf.name}: fell through to pdftotext. Equations and "
                      f"two-column layout will be mangled; treat the body as unreliable. "
                      f"Prefer JATS (aps_harvest.py) or arXiv LaTeX source.", file=sys.stderr)
        except Exception:
            pass
    for p in (tmp_md, tmp_txt):
        try:
            p.unlink()
        except FileNotFoundError:
            pass
    return text.strip()


def render_arxiv(kb: Path, raw: Path, only_missing: bool = False, use_tex: bool = False) -> int:
    n = 0
    arx_dir = raw / "arxiv"
    if not arx_dir.exists():
        return 0
    for json_path in sorted(arx_dir.glob("*.json")):
        arxiv_id = json_path.stem
        s2 = json.loads(json_path.read_text())
        title = s2.get("title", "(untitled)")
        slug = f"{arxiv_id}_{slugify(title)}"
        out_path = kb / f"{slug}.md"
        if only_missing and out_path.exists() and out_path.stat().st_size > 500:
            n += 1
            continue
        meta = {
            "source": f"https://arxiv.org/abs/{arxiv_id}",
            "type": "arxiv",
            "canonical_id": arxiv_id,
            "title": title,
            "authors": authors_str(s2),
            "year": s2.get("year"),
            "venue": s2.get("venue") or (s2.get("journal") or {}).get("name"),
            "arxiv_id": arxiv_id,
            "doi": (s2.get("externalIds") or {}).get("DOI"),
        }
        body = [render_frontmatter(meta), "", f"# {title}", "",
                f"**Authors:** {meta['authors']}", "",
                f"**Citation:** {venue_line(s2)}", "",
                f"**arXiv:** [{arxiv_id}](https://arxiv.org/abs/{arxiv_id})"]
        if meta.get("doi"):
            body += ["", f"**DOI:** [{meta['doi']}](https://doi.org/{meta['doi']})"]
        body += ["", "## Abstract", "", s2.get("abstract") or "_(abstract unavailable)_"]
        pdf = arx_dir / f"{arxiv_id}.pdf"
        tex = arx_dir / f"{arxiv_id}.tex"
        if use_tex and tex.exists() and tex.stat().st_size > 100:
            meta["full_text"] = "latex"
            body[0] = render_frontmatter(meta)
            body += ["", "## Full Text (LaTeX source)", "",
                     tex.read_text(encoding="utf-8", errors="replace").strip()]
        else:
            full = extract_pdf_text(pdf, kb=kb, fig_subdir=f"arxiv__{arxiv_id}") if pdf.exists() else ""
            if full:
                meta["full_text"] = "yes"
                body[0] = render_frontmatter(meta)
                body += ["", "## Full Text", "", full]
            else:
                meta["full_text"] = "no"
                body[0] = render_frontmatter(meta)
        (kb / f"{slug}.md").write_text("\n".join(body) + "\n")
        n += 1
    return n


def render_doi(kb: Path, raw: Path, only_missing: bool = False, use_tex: bool = False) -> int:
    n = 0
    doi_dir = raw / "doi"
    if not doi_dir.exists():
        return 0
    for json_path in sorted(doi_dir.glob("*.json")):
        safe = json_path.stem
        s2 = json.loads(json_path.read_text())
        doi_canon = (s2.get("externalIds") or {}).get("DOI") or safe.replace("-", "/", 1)
        title = s2.get("title", "(untitled)")
        slug = slugify(safe)
        out_path = kb / f"{slug}.md"
        if only_missing and out_path.exists() and out_path.stat().st_size > 500:
            n += 1
            continue
        ext = s2.get("externalIds") or {}
        meta = {
            "source": f"https://doi.org/{doi_canon}",
            "type": "doi",
            "canonical_id": doi_canon,
            "title": title,
            "authors": authors_str(s2),
            "year": s2.get("year"),
            "venue": s2.get("venue") or (s2.get("journal") or {}).get("name"),
            "doi": doi_canon,
            "arxiv_id": ext.get("ArXiv"),
        }
        body = [render_frontmatter(meta), "", f"# {title}", "",
                f"**Authors:** {meta['authors']}", "",
                f"**Citation:** {venue_line(s2)}", "",
                f"**DOI:** [{doi_canon}](https://doi.org/{doi_canon})"]
        if meta.get("arxiv_id"):
            body += ["", f"**arXiv preprint:** [{meta['arxiv_id']}](https://arxiv.org/abs/{meta['arxiv_id']})"]
        body += ["", "## Abstract", "", s2.get("abstract") or "_(abstract unavailable)_"]
        pdf = doi_dir / f"{safe}.pdf"
        tex = doi_dir / f"{safe}.tex"
        jats = doi_dir / f"{safe}.jats.xml"
        jats_md, jats_refs = "", []
        if jats.exists() and jats.stat().st_size > 2048:
            # Publisher JATS beats both LaTeX preprint and PDF: it is the
            # published version, its MathML carries exact TeX, and its
            # reference list is fully structured. See aps_harvest.py.
            try:
                from aps_harvest import extract_refs, jats_to_markdown, render_refs_md
                jats_md = jats_to_markdown(jats)
                jats_refs = extract_refs(jats)
            except Exception as e:
                print(f"  jats {safe}: {e}", file=sys.stderr)
        if jats_md:
            meta["full_text"] = "jats"
            body[0] = render_frontmatter(meta)
            body += ["", "## Full Text (publisher JATS)", "", jats_md]
            if jats_refs:
                body += ["", "## References", "", render_refs_md(jats_refs)]
        elif use_tex and tex.exists() and tex.stat().st_size > 100:
            meta["full_text"] = "latex"
            body[0] = render_frontmatter(meta)
            body += ["", "## Full Text (LaTeX source)", "",
                     tex.read_text(encoding="utf-8", errors="replace").strip()]
        else:
            full = extract_pdf_text(pdf, kb=kb, fig_subdir=f"doi__{safe}") if pdf.exists() else ""
            if full:
                meta["full_text"] = "yes"
                body[0] = render_frontmatter(meta)
                body += ["", "## Full Text", "", full]
            else:
                meta["full_text"] = "no"
                body[0] = render_frontmatter(meta)
                body += ["", "_Full text not retrieved — abstract-only entry._"]
        (kb / f"{slug}.md").write_text("\n".join(body) + "\n")
        n += 1
    return n


def render_github(kb: Path, raw: Path) -> int:
    n = 0
    repos_dir = raw / "repos"
    if not repos_dir.exists():
        return 0
    for repo_dir in sorted(repos_dir.iterdir()):
        if not repo_dir.is_dir():
            continue
        owner, _, repo = repo_dir.name.partition("-")
        if not repo:
            continue
        canonical = f"{owner}/{repo}"
        meta = {
            "source": f"https://github.com/{canonical}",
            "type": "github",
            "canonical_id": canonical,
            "title": canonical,
        }
        body = [render_frontmatter(meta), "", f"# {canonical}", "",
                f"**Source:** https://github.com/{canonical}"]
        for cand in ("README.md", "Readme.md", "readme.md", "README.rst"):
            p = repo_dir / cand
            if p.exists():
                content = p.read_text(errors="replace")
                if p.suffix.lower() == ".rst":
                    try:
                        r = subprocess.run(["pandoc", "-f", "rst", "-t", "gfm"],
                                           input=content, capture_output=True, text=True, timeout=60)
                        if r.returncode == 0:
                            content = r.stdout
                    except Exception:
                        pass
                body += ["", "## README", "", content.strip()]
                break
        try:
            r = subprocess.run(["git", "-C", str(repo_dir), "ls-tree", "-r", "--name-only", "HEAD"],
                               capture_output=True, text=True, timeout=30)
            tree = r.stdout.splitlines()[:200]
        except Exception:
            tree = []
        if tree:
            body += ["", "## File tree (top 200)", "", "```"]
            body += tree
            body.append("```")
        (kb / f"{repo_dir.name}.md").write_text("\n".join(body) + "\n")
        n += 1
    return n


def render_web(kb: Path, raw: Path, manifest: dict) -> int:
    n = 0
    web_dir = raw / "web"
    cite_idx = manifest.get("web", {})
    if not web_dir.exists():
        return 0
    for slug, info in cite_idx.items():
        meta = {
            "source": info.get("source_url", ""),
            "type": "web",
            "canonical_id": slug,
            "title": info.get("title", slug),
            "year": info.get("year"),
            "note": info.get("note"),
        }
        body = [render_frontmatter(meta), "", f"# {meta['title']}", "",
                f"**Source:** {meta['source']}"]
        html = web_dir / f"{slug}.html"
        local_dir = web_dir / slug
        if html.exists():
            try:
                r = subprocess.run(["pandoc", "-f", "html", "-t", "gfm", str(html)],
                                   capture_output=True, text=True, timeout=60)
                content = r.stdout if r.returncode == 0 else html.read_text(errors="replace")
            except Exception:
                content = html.read_text(errors="replace")
            body += ["", "## Body", "", content.strip()]
        elif local_dir.is_dir():
            for f in sorted(local_dir.iterdir()):
                if f.suffix.lower() in (".tex", ".bib", ".md", ".txt"):
                    body += ["", f"## {f.name}", "", f"```{f.suffix.lstrip('.')}",
                             f.read_text(errors="replace").strip(), "```"]
        (kb / f"{slug}.md").write_text("\n".join(body) + "\n")
        n += 1
    return n


def render_stubs(kb: Path, manifest: dict) -> int:
    n = 0
    for st in manifest.get("stub", []):
        slug = st["slug"]
        meta = {
            "source": "(none — bib stub)",
            "type": "stub",
            "canonical_id": slug,
            "title": st["title"],
            "authors": st.get("authors", "unknown"),
            "year": st.get("year"),
            "note": st.get("note"),
        }
        body = [render_frontmatter(meta), "", f"# {st['title']}", "",
                f"**Authors:** {meta['authors']}"]
        if meta.get("note"):
            body += ["", f"**Note:** {meta['note']}"]
        (kb / f"{slug}.md").write_text("\n".join(body) + "\n")
        n += 1
    return n


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--kb", required=True, type=Path)
    p.add_argument("--manifest", type=Path, default=None,
                   help="Optional JSON manifest for web entries and bib stubs")
    p.add_argument("--only-missing", action="store_true",
                   help="Skip rendering papers that already have a non-trivial .md file (>500 bytes)")
    p.add_argument("--tex-source", action="store_true",
                   help="Render from flattened arXiv LaTeX source (.raw/*/<id>.tex) when available; "
                        "default is PDF->markdown for every ref")
    args = p.parse_args()
    raw = args.kb / ".raw"
    m = json.loads(args.manifest.read_text()) if args.manifest else {}
    om = args.only_missing
    print(f"arxiv:  {render_arxiv(args.kb, raw, only_missing=om, use_tex=args.tex_source)}")
    print(f"doi:    {render_doi(args.kb, raw, only_missing=om, use_tex=args.tex_source)}")
    print(f"github: {render_github(args.kb, raw)}")
    print(f"web:    {render_web(args.kb, raw, m)}")
    print(f"stub:   {render_stubs(args.kb, m)}")
    if om:
        print("(--only-missing: skipped already-rendered papers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
