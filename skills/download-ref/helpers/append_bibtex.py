#!/usr/bin/env python3
"""
Append BibTeX entry to ref.bib for a fetched ref.

Reads citationStyles.bibtex from .raw/{arxiv,doi}/<id>.json, proposes a cite
key in `lastname_year_firstword` form, prints both for the caller to confirm
(via AskUserQuestion in the skill harness), then on confirmation rewrites the
cite key and appends to ref.bib if not already present.

Usage:
  # Step A — propose
  python3 append_bibtex.py propose --kb /abs/.knowledge --id 1806.08734 --type arxiv

  # Step B — append (after user confirms key)
  python3 append_bibtex.py append --kb /abs/.knowledge --id 1806.08734 --type arxiv \\
                                  --key rahaman_2018_spectral --bib /abs/ref.bib
"""
import argparse
import json
import re
import sys
from pathlib import Path


def load_meta(kb: Path, idtype: str, ref_id: str) -> dict:
    safe = ref_id.replace("/", "-")
    p = kb / ".raw" / idtype / f"{safe}.json"
    if not p.exists():
        sys.exit(f"missing metadata: {p}")
    return json.loads(p.read_text())


def extract_bibtex(meta: dict) -> str:
    bib = (meta.get("citationStyles") or {}).get("bibtex")
    if not bib:
        sys.exit("no citationStyles.bibtex in metadata")
    return bib.strip()


def propose_key(meta: dict) -> str:
    authors = meta.get("authors") or []
    last = "anon"
    if authors:
        name = (authors[0].get("name") or "").strip()
        if name:
            last = name.split()[-1].lower()
            last = re.sub(r"[^a-z]", "", last) or "anon"
    year = str(meta.get("year") or "0000")
    title = (meta.get("title") or "").lower()
    stop = {"a", "an", "the", "of", "on", "for", "and", "to", "is", "in", "with"}
    words = [w for w in re.findall(r"[a-z]+", title) if w not in stop]
    kw = words[0] if words else "ref"
    return f"{last}_{year}_{kw}"


def replace_key(bibtex: str, new_key: str) -> str:
    return re.sub(r"^(@\w+\{)[^,]+,", rf"\g<1>{new_key},", bibtex, count=1)


def already_in_bib(bib_path: Path, key: str) -> bool:
    if not bib_path.exists():
        return False
    return bool(re.search(rf"^\s*@\w+\{{\s*{re.escape(key)}\s*,", bib_path.read_text(), re.M))


def cmd_propose(args):
    meta = load_meta(Path(args.kb), args.type, args.id)
    bib = extract_bibtex(meta)
    key = propose_key(meta)
    out = {
        "id": args.id,
        "type": args.type,
        "title": meta.get("title", ""),
        "authors": ", ".join(a.get("name", "") for a in (meta.get("authors") or [])[:4]),
        "year": meta.get("year"),
        "venue": meta.get("venue", ""),
        "proposed_key": key,
        "bibtex_with_proposed_key": replace_key(bib, key),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


def cmd_append(args):
    meta = load_meta(Path(args.kb), args.type, args.id)
    bib = extract_bibtex(meta)
    bib = replace_key(bib, args.key)
    bib_path = Path(args.bib)
    if already_in_bib(bib_path, args.key):
        print(f"skip: {args.key} already present in {bib_path}")
        return
    with bib_path.open("a") as f:
        f.write("\n" + bib + "\n")
    print(f"appended: {args.key} -> {bib_path}")


def main():
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(dest="cmd", required=True)
    pr = sp.add_parser("propose")
    pr.add_argument("--kb", required=True)
    pr.add_argument("--id", required=True)
    pr.add_argument("--type", required=True, choices=["arxiv", "doi"])
    pr.set_defaults(func=cmd_propose)
    ap = sp.add_parser("append")
    ap.add_argument("--kb", required=True)
    ap.add_argument("--id", required=True)
    ap.add_argument("--type", required=True, choices=["arxiv", "doi"])
    ap.add_argument("--key", required=True)
    ap.add_argument("--bib", required=True)
    ap.set_defaults(func=cmd_append)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
