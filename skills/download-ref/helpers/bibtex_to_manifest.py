#!/usr/bin/env python3
"""Extract arXiv IDs and DOIs from a references.bib into a manifest JSON.

The output schema matches what fetch_metadata.py expects:
    {"arxiv": ["2401.12345", ...], "doi": ["10.xxx/yyy", ...]}

Recognises:
- `eprint = {2401.12345}` (with optional `archivePrefix = {arXiv}` /
  `eprinttype = {arxiv}` — but treats any `eprint` as arXiv unless
  another archivePrefix is set)
- `doi = {10.xxx/yyy}`

If the same entry has both an arXiv ID and a DOI, the arXiv ID wins
(arXiv preprints are reliably downloadable; DOIs often paywalled).

Usage:
    python3 bibtex_to_manifest.py /abs/.knowledge/references.bib > manifest.json
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ENTRY_RE = re.compile(r"@\w+\{[^,]+,(.*?)\n\}\s*", re.DOTALL)
FIELD_RE = re.compile(r"^\s*(\w+)\s*=\s*[\{\"]([^\}\"]*)[\}\"]", re.MULTILINE)
ARXIV_RE = re.compile(r"^\s*\d{4}\.\d{4,5}(v\d+)?\s*$|^\s*[a-z\-]+/\d{7}(v\d+)?\s*$")


def parse_bib(text: str) -> list[dict[str, str]]:
    entries = []
    for body in ENTRY_RE.findall(text):
        fields: dict[str, str] = {}
        for k, v in FIELD_RE.findall(body):
            fields[k.lower()] = v.strip()
        entries.append(fields)
    return entries


def extract_arxiv(fields: dict[str, str]) -> str | None:
    eprint = fields.get("eprint")
    if not eprint:
        return None
    archive = (fields.get("archiveprefix") or fields.get("eprinttype") or "").lower()
    # If archive is set and it's not arxiv, skip.
    if archive and "arxiv" not in archive:
        return None
    eprint = eprint.strip()
    if not ARXIV_RE.match(eprint):
        return None
    # Strip vN suffix
    return re.sub(r"v\d+$", "", eprint)


def extract_doi(fields: dict[str, str]) -> str | None:
    doi = fields.get("doi")
    if not doi:
        return None
    doi = doi.strip()
    # Strip a leading https://doi.org/ if someone left one in
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi, flags=re.IGNORECASE)
    if not doi.startswith("10."):
        return None
    return doi


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    bib = Path(sys.argv[1])
    if not bib.exists():
        print(f"missing: {bib}", file=sys.stderr)
        return 1
    entries = parse_bib(bib.read_text())
    arxiv: list[str] = []
    doi: list[str] = []
    for f in entries:
        a = extract_arxiv(f)
        if a:
            arxiv.append(a)
            continue
        d = extract_doi(f)
        if d:
            doi.append(d)
    # Deduplicate, preserve order.
    seen: set[str] = set()
    arxiv = [x for x in arxiv if not (x in seen or seen.add(x))]
    seen.clear()
    doi = [x for x in doi if not (x in seen or seen.add(x))]
    json.dump({"arxiv": arxiv, "doi": doi}, sys.stdout, indent=2)
    sys.stdout.write("\n")
    print(f"extracted {len(arxiv)} arxiv ids, {len(doi)} dois "
          f"from {len(entries)} entries", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
