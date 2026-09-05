#!/usr/bin/env python3
"""Check a KB offline. --fix repairs only INDEX.md, preserving its heading/notes."""
from __future__ import annotations

import argparse
from collections import Counter
import re
from pathlib import Path

from index import TITLES, main as index_main
from kb_identity import identities, papers
from verify_bib import extract_arxiv, extract_doi, normalize_text, parse_bib

CHECKS = ("bib-md-sync", "duplicate-identity", "frontmatter-required", "frontmatter-types",
          "bib-required-keys", "index-sync", "raw-orphans")


def check_kb(kb: Path) -> list[tuple[str, str, str]]:
    findings = []
    def add(check, message, level="FAIL"):
        findings.append((level, check, message))
    records = papers(kb)
    owners = {}
    md_keys = {}
    for path, meta in records:
        missing = [key for key in ("source", "type", "canonical_id", "title") if not meta.get(key)]
        if meta.get("type") in ("arxiv", "doi") and meta.get("full_text") not in ("yes", "no", "latex", "jats"):
            missing.append("full_text (yes/no/latex/jats)")
        if missing:
            add("frontmatter-required", f"{path.name}: missing/invalid {', '.join(missing)}")
        if not isinstance(meta.get("type"), str) or meta["type"] not in TITLES:
            add("frontmatter-types", f"{path.name}: unknown type {meta.get('type')!r}")
        for key in ("source", "canonical_id", "title", "authors", "venue", "doi", "arxiv_id", "full_text"):
            if key in meta and not isinstance(meta[key], str):
                add("frontmatter-types", f"{path.name}: {key} must be a string")
        if "year" in meta:
            try:
                int(meta["year"])
            except (TypeError, ValueError):
                add("frontmatter-types", f"{path.name}: year must be an integer")
        try:
            keys = identities(meta)
        except (ValueError, TypeError, AttributeError) as e:
            add("frontmatter-types", f"{path.name}: {e}")
            keys = set()
        md_keys[path] = keys
        for key in keys:
            if key in owners:
                add("duplicate-identity", f"{key[0]}:{key[1]}: {owners[key].name}, {path.name}")
            owners[key] = path
    bib = kb / "references.bib"
    try:
        entries = parse_bib(bib.read_text())
    except (OSError, ValueError) as e:
        add("bib-md-sync", f"references.bib: {e}")
        entries = []
    matched = set()
    cite_keys = set()
    required = {"article": ("author", "title", "journal", "year"),
                "book": ("title", "publisher", "year"),
                "incollection": ("author", "title", "booktitle", "publisher", "year"),
                "inproceedings": ("author", "title", "booktitle", "year"),
                "phdthesis": ("author", "title", "school", "year"),
                "techreport": ("author", "title", "institution", "year")}
    for entry in entries:
        fields, key = entry["fields"], entry["key"]
        if key in cite_keys:
            add("bib-md-sync", f"{key}: duplicate cite key")
        cite_keys.add(key)
        missing = [f for f in required.get(entry["type"], ("title",)) if not fields.get(f)]
        if entry["type"] == "book" and not (fields.get("author") or fields.get("editor")):
            missing.append("author or editor")
        if missing:
            add("bib-required-keys", f"{key}: missing {', '.join(missing)}")
        try:
            keys = identities({"doi": extract_doi(fields), "arxiv_id": extract_arxiv(fields)})
        except ValueError as e:
            add("bib-md-sync", f"{key}: {e}")
            keys = set()
        paths = {path for path, meta in records if keys & md_keys[path] or
                 (not keys and meta.get("type") == "stub" and fields.get("title") and
                  normalize_text(fields["title"]) == normalize_text(meta.get("title")))}
        matched |= paths
        if not paths:
            add("bib-md-sync", f"{key}: no rendered entry")
    for path, meta in records:
        if meta.get("type") in ("arxiv", "doi", "stub") and path not in matched:
            add("bib-md-sync", f"{path.name}: no bibliography entry")
    index = kb / "INDEX.md"
    actual = Counter(re.findall(r"^\| \[[^\]]+\]\(([^)]+\.md)\)", index.read_text(), re.M)) if index.exists() else Counter()
    expected = Counter(path.name for path, _ in records)
    if not index.exists() or actual != expected:
        add("index-sync", f"INDEX.md: missing {list((expected - actual).elements())}; extra {list((actual - expected).elements())}")
    for kind in ("arxiv", "doi"):
        for raw in sorted((kb / ".raw" / kind).iterdir()) if (kb / ".raw" / kind).exists() else []:
            if not any(raw.name.lower().startswith(value.replace("/", "-") + ".")
                       or raw.name.lower() == value.replace("/", "-") + "-src"
                       for namespace, value in owners if namespace == kind):
                add("raw-orphans", f"{raw.relative_to(kb)}: no rendered paper", "WARN")
    return findings


def repair_index(kb: Path) -> None:
    path = kb / "INDEX.md"
    old = path.read_text() if path.exists() else ""
    title = re.search(r"^# (.+)$", old, re.M)
    note = re.search(r"^Generated \d{4}-\d{2}-\d{2}\.\s*(.*)$", old, re.M)
    index_main(["--kb", str(kb), "--title", title[1] if title else f"{kb.name} references",
                "--source-note", note[1] if note else ""])
    if "\n## Excluded / abstract-only\n" in old:
        path.write_text(path.read_text() + "## Excluded / abstract-only\n" + old.split("\n## Excluded / abstract-only\n", 1)[1])


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--kb", required=True, type=Path)
    p.add_argument("--checks", default=",".join(CHECKS), help=", ".join(CHECKS))
    p.add_argument("--fix", action="store_true")
    args = p.parse_args(argv)
    checks = set(args.checks.split(","))
    if checks - set(CHECKS):
        p.error(f"unknown checks: {', '.join(sorted(checks - set(CHECKS)))}")
    if not args.kb.is_dir():
        p.error(f"KB directory does not exist: {args.kb}")
    try:
        findings = check_kb(args.kb)
        invalid = any(check in ("frontmatter-types", "frontmatter-required") for _, check, _ in findings)
        if args.fix and not invalid and "index-sync" in checks and any(check == "index-sync" for _, check, _ in findings):
            repair_index(args.kb)
            findings = check_kb(args.kb)
    except (OSError, ValueError) as e:
        p.exit(2, f"kb_doctor: {e}\n")
    findings = [f for f in findings if f[1] in checks]
    for level, check, message in findings:
        print(f"{level} {check} {message}")
    failures = sum(level == "FAIL" for level, _, _ in findings)
    print(f"{failures} FAIL, {len(findings) - failures} WARN")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
