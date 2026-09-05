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
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from kb_identity import cache_path, find_match, identities, identity_index, normalize, same_record

S2_FIELDS = "title,abstract,authors,year,venue,publicationVenue,journal,externalIds,citationStyles,openAccessPdf"
S2_BATCH_URL = f"https://api.semanticscholar.org/graph/v1/paper/batch?fields={S2_FIELDS}"

S2_API_KEY = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")


def post_batch(ids: list[str]) -> list[dict | None]:
    """Submit IDs (with ARXIV: or DOI: prefix) to S2's batch endpoint."""
    body = json.dumps({"ids": ids}).encode("utf-8")
    headers = {"Content-Type": "application/json", "User-Agent": "build-harness/1.0"}
    if S2_API_KEY:
        headers["x-api-key"] = S2_API_KEY
    req = urllib.request.Request(
        S2_BATCH_URL, data=body, method="POST", headers=headers,
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


def valid_pdf(path: Path) -> bool:
    if not path.is_file():
        return False
    body = path.read_bytes()
    return len(body) > 1024 and body.startswith(b"%PDF") and b"%%EOF" in body[-32:]


def fetch_pdf(url: str, out: Path, ua: str = "Mozilla/5.0") -> bool:
    if valid_pdf(out):
        return True
    try:
        req = urllib.request.Request(url, headers={"User-Agent": ua})
        with urllib.request.urlopen(req, timeout=120) as r:
            body = r.read()
        if len(body) <= 1024 or body[:4] != b"%PDF":
            return False
        if b"%%EOF" not in body[-32:]:
            print(f"  {out.name}: downloaded file missing %%EOF (truncated?), skipping", file=sys.stderr)
            return False
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(body)
        return True
    except Exception as e:
        print(f"  pdf fail {out.name}: {e}", file=sys.stderr)
        return False


def save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def get_json(url: str, email: str = "") -> dict:
    ua = "sci-brain/0.5 (https://github.com/QuantumBFS/sci-brain)"
    if email:
        ua += f" mailto:{email}"
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read())


def crossref_metadata(doi: str, email: str = "") -> dict | None:
    """Normalize deposited Crossref fields, including a usable BibTeX entry."""
    try:
        url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
        if email:
            url += "?" + urllib.parse.urlencode({"mailto": email})
        m = get_json(url, email)["message"]
        title = " ".join(html.unescape(re.sub(r"<[^>]+>", "", (m.get("title") or [""])[0])).split())
        if not title or normalize("doi", m["DOI"]) != doi:
            return None
        authors = [" ".join(filter(None, (a.get("given"), a.get("family")))) or a.get("name", "")
                   for a in m.get("author", [])]
        year = next((m[k]["date-parts"][0][0] for k in ("published", "issued", "published-print", "published-online")
                     if m.get(k, {}).get("date-parts") and m[k]["date-parts"][0]), None)
        venue = html.unescape((m.get("container-title") or [""])[0])
        entry_type = {"journal-article": "article", "book": "book", "monograph": "book",
                      "book-chapter": "incollection", "proceedings-article": "inproceedings"}.get(m.get("type"), "misc")
        fields = {"title": title, "author": " and ".join(authors), "year": year,
                  "doi": doi, "publisher": m.get("publisher"), "volume": m.get("volume"),
                  "number": m.get("issue"), "pages": m.get("page")}
        fields["journal" if entry_type == "article" else "booktitle"] = venue
        def escape(value):
            return re.sub(r"[\\{}%&#_$]", lambda match: "\\" + match[0], str(value))
        bib = "@" + entry_type + "{crossref,\n" + "\n".join(
            f"  {key} = {{{value if key == 'doi' else escape(value)}}}," for key, value in fields.items() if value) + "\n}"
        return {"title": title, "authors": [{"name": a} for a in authors], "year": year,
                "venue": venue, "journal": {"name": venue, "volume": m.get("volume"), "pages": m.get("page")},
                "externalIds": {"DOI": doi}, "abstract": html.unescape(re.sub(r"<[^>]+>", "", m.get("abstract", ""))),
                "citationStyles": {"bibtex": bib}, "metadata_source": "crossref"}
    except (OSError, ValueError, KeyError, TypeError, IndexError) as e:
        print(f"  Crossref miss {doi}: {e}", file=sys.stderr)
        return None


def lookup_metadata(refs: list[tuple[str, str]], email: str = "") -> list[dict | None]:
    results = []
    for start in range(0, len(refs), 500):
        batch = refs[start:start + 500]
        try:
            found = post_batch([f"{kind.upper()}:{value}" for kind, value in batch])
            if len(found) != len(batch):
                raise ValueError("Semantic Scholar returned an incomplete batch")
        except (OSError, ValueError) as e:
            print(f"  Semantic Scholar unavailable: {e}", file=sys.stderr)
            found = [None] * len(batch)
        for (kind, value), meta in zip(batch, found):
            if meta is None and kind == "doi":
                meta = crossref_metadata(value, email)
                time.sleep(2)
            results.append(meta)
    return results


def unpaywall_urls(doi: str, email: str) -> list[str]:
    if not email:
        return []
    try:
        url = "https://api.unpaywall.org/v2/" + urllib.parse.quote(doi, safe="")
        data = get_json(url + "?" + urllib.parse.urlencode({"email": email}), email)
        locations = [data.get("best_oa_location"), *(data.get("oa_locations") or [])]
        return list(dict.fromkeys(loc["url_for_pdf"] for loc in locations if loc and loc.get("url_for_pdf")))
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(f"  Unpaywall miss {doi}: {e}", file=sys.stderr)
        return []


def fetch_doi_pdf(doi: str, meta: dict, out: Path, email: str = "") -> str:
    if valid_pdf(out):
        return "cached"
    oa = (meta.get("openAccessPdf") or {}).get("url")
    if oa and not any(h in oa for h in ("link.aps.org", "iopscience", "nature.com", "science.org", "pubs.acs.org")):
        if fetch_pdf(oa, out):
            return "s2"
    for url in unpaywall_urls(doi, email):
        if fetch_pdf(url, out):
            return "unpaywall"
    arxiv = (meta.get("externalIds") or {}).get("ArXiv")
    if arxiv and fetch_pdf(f"https://arxiv.org/pdf/{arxiv}.pdf", out):
        return "arxiv"
    return "miss"


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
    p.add_argument("--download-arxiv-source", action="store_true",
                   help="Also fetch arXiv e-print LaTeX sources, flattened to .raw/arxiv/<id>.tex")
    p.add_argument("--no-aps", action="store_true",
                   help="Skip the APS Harvest JATS fetch for 10.1103/* DOIs (on by default)")
    p.add_argument("--email", default=os.environ.get("SCIBRAIN_CONTACT_EMAIL", ""),
                   help="Contact email for Unpaywall and Crossref (or SCIBRAIN_CONTACT_EMAIL)")
    p.add_argument("--allow-duplicate", action="store_true", help="Allow a second identifier namespace for an existing paper")
    args = p.parse_args()

    raw = args.kb / ".raw"
    manifest = json.loads(args.manifest.read_text())
    try:
        refs = list(dict.fromkeys((kind, normalize(kind, value))
                    for kind in ("arxiv", "doi") for value in manifest.get(kind, [])))
        index = identity_index(args.kb)
    except (ValueError, OSError) as e:
        p.error(str(e))
    pending, accepted = [], []
    for kind, value in refs:
        out = cache_path(args.kb, kind, value)
        match = find_match(index, {(kind, value)})
        if match and not args.allow_duplicate and not same_record(match[0], kind, value):
            print(f"present {match[0]} (matched via {match[1]}); skipped {kind}:{value}")
            continue
        if out.exists():
            accepted.append((kind, value, json.loads(out.read_text())))
        else:
            pending.append((kind, value))
    results = lookup_metadata(pending, args.email)
    for (kind, value), meta in zip(pending, results):
        keys = identities(meta or {}) | {(kind, value)}
        match = find_match(index, keys)
        if match and not args.allow_duplicate and not same_record(match[0], kind, value):
            print(f"present {match[0]} (matched via {match[1]}); skipped {kind}:{value}")
            continue
        if meta is not None:
            out = cache_path(args.kb, kind, value)
            save(out, meta)
            index.update({key: out for key in keys})
        accepted.append((kind, value, meta))
    accepted.sort(key=lambda ref: ref[0] != "arxiv")
    for kind, value, meta in accepted:
        summarize(kind, value, meta)
        if meta and meta.get("metadata_source") == "crossref":
            print(f"ok {kind}:{value} (crossref)")
    arxiv_ids = [value for kind, value, _ in accepted if kind == "arxiv"]
    dois = [value for kind, value, _ in accepted if kind == "doi"]
    results = [meta for _, _, meta in accepted]

    if not args.no_aps and dois:
        from aps_harvest import APS_PREFIX, fetch_jats
        aps = [d for d in dois if d.lower().startswith(APS_PREFIX)]
        if aps:
            print(f"\nAPS Harvest: publisher JATS for {len(aps)} DOI(s) "
                  f"(no key needed; 401 = closed, falls through to arXiv/PDF)...")
            for i, d in enumerate(aps):
                st = fetch_jats(d, cache_path(args.kb, "doi", d, ".jats.xml"))
                print(f"  {st:8s} {d}")
                if st != "cached" and i < len(aps) - 1:
                    time.sleep(1)

    if args.download_arxiv_pdfs:
        print("\nfetching PDFs (sequential with 2s sleep to avoid arXiv rate limits)...")
        for aid in arxiv_ids:
            out = cache_path(args.kb, "arxiv", aid, ".pdf")
            if valid_pdf(out):
                print(f"  ok arxiv:{aid} (cached)")
                continue
            if fetch_pdf(f"https://arxiv.org/pdf/{aid}.pdf", out):
                print(f"  ok arxiv:{aid}")
            else:
                print(f"  FAIL arxiv:{aid}")
            time.sleep(2)
        for doi, r in zip(dois, results[len(arxiv_ids):]):
            if r is None:
                continue
            out = cache_path(args.kb, "doi", doi, ".pdf")
            status = fetch_doi_pdf(doi, r, out, args.email)
            print(f"  {'miss' if status == 'miss' else 'ok  '} doi:{doi} ({status})")
            time.sleep(2)

    if args.download_arxiv_source:
        from tex_source import fetch_arxiv_source
        print("\nfetching LaTeX sources (sequential with 2s sleep to avoid arXiv rate limits)...")
        for aid in arxiv_ids:
            status = fetch_arxiv_source(aid, args.kb)
            if status in ("ok", "cached"):
                print(f"  ok  arxiv:{aid}" + (" (cached)" if status == "cached" else ""))
            else:
                print(f"  src-miss arxiv:{aid} ({status})")
            if status != "cached":
                time.sleep(2)
        for doi, r in zip(dois, results[len(arxiv_ids):]):
            if r is None:
                continue
            arxiv_pre = (r.get("externalIds") or {}).get("ArXiv")
            if not arxiv_pre:
                continue
            out_tex = cache_path(args.kb, "doi", doi, ".tex")
            status = fetch_arxiv_source(
                arxiv_pre, args.kb,
                out_tex=out_tex,
                fig_subdir=f"doi__{out_tex.stem}")
            if status in ("ok", "cached"):
                print(f"  ok  doi:{doi} (arxiv={arxiv_pre})" + (" (cached)" if status == "cached" else ""))
            else:
                print(f"  src-miss doi:{doi} (arxiv={arxiv_pre}, {status})")
            if status != "cached":
                time.sleep(2)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
