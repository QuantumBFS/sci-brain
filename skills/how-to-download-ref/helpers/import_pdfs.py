#!/usr/bin/env python3
"""Import chemistry-publisher PDFs that a person downloaded by hand.

AIP (10.1063), ACS (10.1021) and RSC (10.1039) serve article PDFs only after a
Cloudflare human check, even on a subscribed network, so fetch_metadata.py lists
those misses as links. Open each link, save the PDF anywhere under --from, then:

    import_pdfs.py --kb /abs/path/.knowledge [--from ~/Downloads] [--days 14]

Each recent PDF is matched to a pending DOI (a KB DOI under those prefixes with
no PDF yet) by a DOI printed in it, or else by the exact title on its first
pages, and copied to .raw/doi/<safe>.pdf. Files matching no pending DOI, or more
than one, are left alone. Re-render afterwards with render.py --kb <kb>.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from fetch_metadata import BOT_CHECKED_PREFIXES, valid_pdf
from kb_identity import cache_path, normalize

def title_key(value: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value.lower()).split())


def pending(kb: Path) -> dict[str, str]:
    """Chemistry-publisher DOIs in the KB without a PDF, mapped to their titles."""
    out = {}
    for path in sorted((kb / ".raw" / "doi").glob("*.json")):
        try:
            meta = json.loads(path.read_text())
            doi = normalize("doi", (meta.get("externalIds") or {}).get("DOI") or "")
        except (OSError, ValueError, AttributeError):
            continue
        if doi.startswith(BOT_CHECKED_PREFIXES) and not valid_pdf(cache_path(kb, "doi", doi, ".pdf")):
            out[doi] = meta.get("title") or ""
    return out


def first_pages_text(pdf: Path) -> bytes:
    """Text of pages 1-2 (pdftotext, else PyMuPDF) plus the raw bytes, which hold XMP metadata."""
    text = b""
    try:
        text = subprocess.run(["pdftotext", "-f", "1", "-l", "2", str(pdf), "-"],
                              capture_output=True, timeout=60).stdout
    except (OSError, subprocess.TimeoutExpired):
        try:
            import pymupdf  # type: ignore
            with pymupdf.open(pdf) as doc:
                text = "".join(doc[i].get_text() for i in range(min(2, len(doc)))).encode()
        except Exception:
            pass
    return text + b"\n" + pdf.read_bytes()


def match(pdf: Path, wanted: dict[str, str]) -> str | None:
    blob = first_pages_text(pdf)
    lower = blob.lower()
    # The DOI must end there: 10.1063/1.49440 must not match inside 10.1063/1.4944087.
    hits = [doi for doi in wanted
            if re.search(re.escape(doi.encode()) + rb"(?![a-z0-9]|[./-][a-z0-9])", lower)]
    if len(hits) == 1:
        return hits[0]
    text = title_key(blob.split(b"\n%PDF", 1)[0].decode("utf-8", "replace"))
    hits = [doi for doi, title in wanted.items() if len(title_key(title)) > 20 and title_key(title) in text]
    return hits[0] if len(hits) == 1 else None


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--kb", required=True, type=Path, help="Absolute path to <stream>/.knowledge/")
    p.add_argument("--from", dest="source", type=Path, default=Path.home() / "Downloads",
                   help="Folder holding the downloaded PDFs (default ~/Downloads)")
    p.add_argument("--days", type=float, default=14, help="Only look at PDFs modified in the last N days")
    args = p.parse_args()

    wanted = pending(args.kb)
    if not wanted:
        print("no chemistry-publisher DOI in this KB is waiting for a PDF")
        return 0
    cutoff = time.time() - args.days * 86400
    pdfs = sorted(f for f in args.source.expanduser().rglob("*.pdf")
                  if f.is_file() and f.stat().st_mtime >= cutoff)
    imported = 0
    for pdf in pdfs:
        if not wanted or not valid_pdf(pdf):
            continue
        doi = match(pdf, wanted)
        if doi is None:
            continue
        dest = cache_path(args.kb, "doi", doi, ".pdf")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(pdf, dest)
        print(f"  ok   doi:{doi} <- {pdf}")
        del wanted[doi]
        imported += 1
    for doi in wanted:
        print(f"  miss doi:{doi} (no matching PDF in {args.source})")
    if imported:
        print(f"\n{imported} imported; re-render with: render.py --kb {args.kb}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
