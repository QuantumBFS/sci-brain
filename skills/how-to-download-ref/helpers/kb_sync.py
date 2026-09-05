#!/usr/bin/env python3
"""Restore .raw/ and .figures/ from tracked KB entries without rewriting text."""
from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path
from urllib.parse import unquote

from fetch_metadata import fetch_doi_pdf, fetch_pdf, lookup_metadata, save, valid_pdf
from kb_identity import cache_path, identities, normalize, papers
from tex_source import fetch_arxiv_source
from verify_bib import extract_arxiv, extract_doi, parse_bib


def restore_pdf_figures(kb: Path, pdf: Path, subdir: str, text: str) -> str:
    """Use the original renderer so restored filenames match tracked image links."""
    from render import extract_pdf_text
    expected = [kb / unquote(link) for link in re.findall(r"(?:\]\(|[\"{])([.]figures/[^\s)\"}]+)", text)]
    for path in expected:
        if not path.resolve().is_relative_to((kb / ".figures").resolve()):
            raise ValueError(f"figure link escapes .figures/: {path}")
    dest = kb / ".figures" / subdir
    stamp = dest / ".complete.json"
    if stamp.exists():
        generated = json.loads(stamp.read_text())
        if all((dest / name).is_file() for name in generated) and all(path.is_file() for path in expected):
            return "cached"
    # A text-only fallback cannot restore images. Make missing dependencies visible.
    import pymupdf4llm  # noqa: F401
    if not extract_pdf_text(pdf, kb=kb, fig_subdir=subdir):
        return "failed to extract PDF figures"
    if any(not path.is_file() for path in expected):
        return "figure filenames differ from tracked links; use the original pymupdf4llm version"
    dest.mkdir(parents=True, exist_ok=True)
    generated = [str(path.relative_to(dest)) for path in dest.rglob("*") if path.is_file() and path != stamp]
    stamp.write_text(json.dumps(generated))
    return "ok"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--kb", required=True, type=Path)
    p.add_argument("--email", default=os.environ.get("SCIBRAIN_CONTACT_EMAIL", ""))
    args = p.parse_args(argv)
    kb = args.kb.resolve()
    bib = kb / "references.bib"
    try:
        records = [(path, meta) for path, meta in papers(kb) if meta.get("type") in ("arxiv", "doi")]
        if not bib.is_file() or not records:
            p.error("references.bib and rendered arXiv/DOI Markdown entries are required")
        entries = parse_bib(bib.read_text())
        known = set()
        work = []
        for path, meta in records:
            kind = meta["type"]
            value = normalize(kind, meta.get("canonical_id", ""))
            known |= identities(meta)
            work.append((path, kind, value, meta))
        # A bib-only entry can recover caches, but cannot recreate tracked prose.
        for entry in entries:
            fields = entry["fields"]
            meta = {"doi": extract_doi(fields), "arxiv_id": extract_arxiv(fields), "full_text": "no"}
            keys = identities(meta)
            if keys and not keys & known:
                kind, value = ("doi", meta["doi"]) if meta["doi"] else ("arxiv", meta["arxiv_id"])
                work.append((None, kind, normalize(kind, value), meta))
                known |= keys
        pending, metadata = [], {}
        for _, kind, value, _ in work:
            dest = cache_path(kb, kind, value)
            if dest.exists():
                metadata[kind, value] = json.loads(dest.read_text())
            else:
                pending.append((kind, value))
        metadata.update(zip(pending, lookup_metadata(pending, args.email)))
    except (OSError, ValueError, TypeError) as e:
        p.exit(2, f"kb_sync: {e}\n")
    failures = 0
    for path, kind, value, fm in work:
        warnings, assets = [], []
        all_cached = (kind, value) not in pending
        try:
            meta = metadata[kind, value]
            if meta is None:
                raise ValueError("metadata unavailable; retry acquisition")
            meta_path = cache_path(kb, kind, value)
            safe = meta_path.stem
            base = kb / ".raw" / kind / safe
            if not meta_path.exists():
                save(meta_path, meta)
            assets.append("json")
            pdf = cache_path(kb, kind, value, ".pdf")
            cached = valid_pdf(pdf)
            all_cached &= cached
            status = ("cached" if cached else "ok" if fetch_pdf(f"https://arxiv.org/pdf/{value}.pdf", pdf) else "miss") if kind == "arxiv" else fetch_doi_pdf(value, meta, pdf, args.email)
            if status == "miss":
                warnings.append("PDF unavailable; try scihub_download.py")
            else:
                assets.append("pdf")
            if not cached:
                time.sleep(2)
            arxiv = value if kind == "arxiv" else fm.get("arxiv_id") or (meta.get("externalIds") or {}).get("ArXiv")
            subdir = f"{kind}__{safe}"
            if arxiv:
                status = fetch_arxiv_source(arxiv, kb, out_tex=base.with_name(safe + ".tex"),
                                            fig_subdir=subdir, restore_figures=fm.get("full_text") == "latex")
                all_cached &= status == "cached"
                if status in ("ok", "cached"):
                    assets.append("tex")
                elif fm.get("full_text") == "latex":
                    warnings.append(f"LaTeX source/figures unavailable ({status})")
                if status != "cached":
                    time.sleep(2)
            if fm.get("full_text") == "jats":
                from aps_harvest import fetch_jats
                status = fetch_jats(value, base.with_name(safe + ".jats.xml"))
                all_cached &= status == "cached"
                if status not in ("ok", "cached"):
                    warnings.append(f"JATS unavailable ({status})")
                else:
                    assets.append("jats")
            if fm.get("full_text") == "yes" and valid_pdf(pdf):
                status = restore_pdf_figures(kb, pdf, subdir, path.read_text() if path else "")
                all_cached &= status == "cached"
                if status not in ("ok", "cached"):
                    warnings.append(status)
            if path is None:
                warnings.append("no rendered entry; run kb_doctor.py")
            figs = sum(1 for f in (kb / ".figures" / subdir).rglob("*") if f.is_file() and not f.name.startswith("."))
            print(f"{'WARN' if warnings else 'PASS'} {kind}:{value} ({'cached; ' if all_cached else ''}{', '.join(assets)}, {figs} figs)" +
                  ("; " + "; ".join(warnings) if warnings else ""))
        except (OSError, ValueError, ImportError) as e:
            failures += 1
            print(f"FAIL {kind}:{value}: {e}")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
