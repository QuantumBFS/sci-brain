#!/usr/bin/env python3
"""Batch-fetch paper metadata from Semantic Scholar for a harness.

The Semantic Scholar /paper/batch endpoint accepts up to 500 IDs in one POST and
returns title/authors/abstract/venue/externalIds/citationStyles/openAccessPdf for
each. That's MUCH faster and more reliable than per-paper calls (which 429 fast).

Usage:
    fetch_metadata.py --kb /abs/path/.knowledge --manifest manifest.json

The manifest is JSON: {"arxiv": ["2401.12345", ...], "doi": ["10.xxx/yyy", ...]}
Output: .raw/arxiv/<id>.json and .raw/doi/<safe>.json (where safe = doi with /→-)

If --download-arxiv-pdfs is passed, also fetches the arXiv preprint PDFs into the
same directory. For DOI entries with an `externalIds.ArXiv` preprint (very common
even for paywalled journal papers), the arXiv PDF is fetched into .raw/doi/<safe>.pdf
as a paywall-bypass fallback.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

S2_FIELDS = "title,abstract,authors,year,venue,journal,externalIds,citationStyles,openAccessPdf"
S2_BATCH_URL = f"https://api.semanticscholar.org/graph/v1/paper/batch?fields={S2_FIELDS}"


def post_batch(ids: list[str]) -> list[dict | None]:
    """Submit IDs (with ARXIV: or DOI: prefix) to S2's batch endpoint."""
    body = json.dumps({"ids": ids}).encode("utf-8")
    req = urllib.request.Request(
        S2_BATCH_URL, data=body, method="POST",
        headers={"Content-Type": "application/json", "User-Agent": "build-harness/1.0"},
    )
    backoff = 5
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < 5:
                print(f"  HTTP {e.code}, sleep {backoff}s", file=sys.stderr)
                time.sleep(backoff)
                backoff *= 2
                continue
            raise
    return [None] * len(ids)


def fetch_pdf(url: str, out: Path, ua: str = "Mozilla/5.0") -> bool:
    if out.exists() and out.stat().st_size > 1024:
        return True
    try:
        req = urllib.request.Request(url, headers={"User-Agent": ua})
        with urllib.request.urlopen(req, timeout=120) as r:
            body = r.read()
        if body[:4] != b"%PDF":
            return False
        out.write_bytes(body)
        return True
    except Exception as e:
        print(f"  pdf fail {out.name}: {e}", file=sys.stderr)
        return False


def save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def summarize(prefix: str, key: str, data: dict | None) -> None:
    if data is None:
        print(f"miss {prefix}:{key}", file=sys.stderr)
        return
    venue = data.get("venue") or (data.get("journal") or {}).get("name", "?")
    abs_ = "yes" if data.get("abstract") else "no"
    oa = "yes" if (data.get("openAccessPdf") or {}).get("url") else "no"
    print(f"ok  {prefix}:{key:40s} | {venue} {data.get('year', '?')} | abs={abs_} oa={oa}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--kb", required=True, type=Path,
                   help="Absolute path to <stream>/.knowledge/")
    p.add_argument("--manifest", required=True, type=Path,
                   help="JSON file with {arxiv: [ids], doi: [dois]}")
    p.add_argument("--download-arxiv-pdfs", action="store_true",
                   help="Also fetch arXiv preprint PDFs (incl. preprints of paywalled DOIs)")
    args = p.parse_args()

    raw = args.kb / ".raw"
    manifest = json.loads(args.manifest.read_text())
    arxiv_ids = manifest.get("arxiv", [])
    dois = manifest.get("doi", [])

    ids = [f"ARXIV:{a}" for a in arxiv_ids] + [f"DOI:{d}" for d in dois]
    if not ids:
        print("nothing to fetch")
        return 0
    print(f"batch fetching {len(ids)} papers via Semantic Scholar...")
    results = post_batch(ids)

    # Save metadata
    for k, r in zip(arxiv_ids, results[:len(arxiv_ids)]):
        if r is not None:
            save(raw / "arxiv" / f"{k}.json", r)
        summarize("arxiv", k, r)
    for k, r in zip(dois, results[len(arxiv_ids):]):
        if r is not None:
            safe = k.replace("/", "-")
            save(raw / "doi" / f"{safe}.json", r)
        summarize("doi", k, r)

    if args.download_arxiv_pdfs:
        print("\nfetching PDFs...")
        # arXiv preprints
        for aid in arxiv_ids:
            out = raw / "arxiv" / f"{aid}.pdf"
            if fetch_pdf(f"https://arxiv.org/pdf/{aid}.pdf", out):
                print(f"  ok arxiv:{aid}")
            else:
                print(f"  FAIL arxiv:{aid}")
        # DOI papers — try arXiv preprint via externalIds.ArXiv
        for doi, r in zip(dois, results[len(arxiv_ids):]):
            if r is None:
                continue
            ext = r.get("externalIds") or {}
            arxiv_pre = ext.get("ArXiv")
            safe = doi.replace("/", "-")
            out = raw / "doi" / f"{safe}.pdf"
            ok = False
            # First try S2's openAccessPdf if it points to a non-publisher host
            oa_url = (r.get("openAccessPdf") or {}).get("url") or ""
            if oa_url and not any(h in oa_url for h in ("link.aps.org", "iopscience", "nature.com", "science.org")):
                ok = fetch_pdf(oa_url, out)
            # Then arXiv preprint (paywall bypass)
            if not ok and arxiv_pre:
                ok = fetch_pdf(f"https://arxiv.org/pdf/{arxiv_pre}.pdf", out)
            print(f"  {'ok  ' if ok else 'miss'} doi:{doi} (arxiv={arxiv_pre or '-'})")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
