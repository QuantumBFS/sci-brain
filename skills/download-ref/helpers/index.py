#!/usr/bin/env python3
"""Generate INDEX.md for a harness by reading frontmatter from rendered .md files.

Groups entries by `type` (arxiv|doi|github|web|stub). Within each group, sorts by
year descending (None → bottom), then by title ascending. Failed/excluded entries
can optionally be supplied via --excluded for an "Excluded" section.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
from pathlib import Path

TITLES = {"arxiv": "arXiv", "doi": "DOI", "github": "GitHub", "web": "Web", "stub": "Bib stubs (no source)"}


def yaml_strip_quotes(s: str) -> str:
    return s.strip().strip('"')


def parse_frontmatter(path: Path) -> dict:
    text = path.read_text()
    m = re.search(r"^---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    out: dict = {}
    in_list = None
    for raw in m.group(1).splitlines():
        if raw.startswith("  - ") and in_list is not None:
            out[in_list].append(yaml_strip_quotes(raw[4:]))
            continue
        in_list = None
        if ":" not in raw:
            continue
        k, _, v = raw.partition(":")
        v = v.strip()
        if v == "":
            out[k.strip()] = []
            in_list = k.strip()
            continue
        out[k.strip()] = yaml_strip_quotes(v)
    return out


def year_key(s: str) -> int:
    """Sort key: real years high→low, missing/empty → -inf (so they go last in desc sort)."""
    try:
        return int(s)
    except (ValueError, TypeError):
        return -10**9


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--kb", required=True, type=Path)
    p.add_argument("--title", required=True,
                   help="Heading for the INDEX (e.g. 'attention-solids knowledge base')")
    p.add_argument("--source-note", default=None,
                   help="Optional one-line description shown under the title")
    p.add_argument("--excluded", type=Path, default=None,
                   help="Optional JSON file: [[url, reason], ...] for an Excluded section")
    args = p.parse_args()

    today = datetime.date.today().isoformat()
    rows: dict[str, list[dict]] = {}
    for md in sorted(args.kb.glob("*.md")):
        if md.name == "INDEX.md":
            continue
        fm = parse_frontmatter(md)
        if not fm:
            continue
        t = fm.get("type", "stub")
        rows.setdefault(t, []).append({
            "file": md.name,
            "title": fm.get("title", ""),
            "authors": fm.get("authors", ""),
            "year": fm.get("year", ""),
            "venue": fm.get("venue", ""),
            "full_text": fm.get("full_text", "no"),
        })

    # Sort: year desc, then title asc (within each type bucket).
    for t in rows:
        rows[t].sort(key=lambda r: (r["title"] or "").lower())
        rows[t].sort(key=lambda r: year_key(r["year"]), reverse=True)

    out = []
    out.append(f"# {args.title}")
    out.append("")
    note = f" {args.source_note}" if args.source_note else ""
    out.append(f"Generated {today}.{note}")
    out.append("")
    out.append("Search inside this dir with `rg --hidden -g '!.raw' \"term\" .knowledge/` "
               "(or `rg` from inside `.knowledge/` itself). "
               "The `.raw/` subdir holds the original PDFs / clones / HTML and is gitignored.")
    out.append("")

    for t in ("arxiv", "doi", "github", "web", "stub"):
        if not rows.get(t):
            continue
        out.append(f"## {TITLES[t]} ({len(rows[t])} entries)")
        out.append("")
        out.append("| File | Title | Authors | Year | Venue | Full text |")
        out.append("|---|---|---|---|---|:---:|")
        for r in rows[t]:
            ttl = r["title"].replace("|", "\\|")
            au = (r["authors"] or "").replace("|", "\\|")
            # Truncate long author lists
            if len(au) > 60:
                au = au.split(",")[0] + " et al."
            ven = (r["venue"] or "").replace("|", "\\|")
            ft = "✅" if r["full_text"] == "yes" else "—"
            out.append(
                f"| [{r['file']}]({r['file']}) | {ttl} | {au} | {r['year']} | {ven} | {ft} |"
            )
        out.append("")

    if args.excluded and args.excluded.exists():
        excluded = json.loads(args.excluded.read_text())
        if excluded:
            out.append("## Excluded / abstract-only")
            out.append("")
            out.append("| URL | Reason |")
            out.append("|---|---|")
            for u, reason in excluded:
                out.append(f"| {u} | {reason} |")
            out.append("")

    (args.kb / "INDEX.md").write_text("\n".join(out) + "\n")
    print("INDEX.md written:", args.kb / "INDEX.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
