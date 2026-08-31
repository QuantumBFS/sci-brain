#!/usr/bin/env python3
"""Scope a survey/review to the cite keys it should cover, and verify them.

The source set for a write-up is *defined* by the `[@cite-key]` anchors that
`/survey` wrote into `NOTES.md`. This helper extracts those keys, deduplicates
them, and checks that each one resolves to an entry in the bib — so the
write-up stage knows exactly which references are in scope and fails loudly if
any anchor is dangling.

CLI:
    python3 scope_refs.py --notes $KB/NOTES.md [--bib $KB/references.bib]
        --bib defaults to `references.bib` next to the notes file.
        Prints one resolved cite key per line to stdout (sorted).
        Writes a summary + any missing/unused keys to stderr.
        Exit 0 if every anchor resolves; exit 2 if any anchor is dangling.

    Add --json to emit {"scoped": [...], "missing": [...], "unused": [...]}
    on stdout instead of the plain list.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# `[@key]`, `[@a; @b]`, or bare `@key` (pandoc style). Keys are letters/digits
# with `_ : -` inside; trailing punctuation is stripped by the character class.
_ANCHOR = re.compile(r"@([A-Za-z][A-Za-z0-9_:.\-]*)")
_BIB_ENTRY = re.compile(r"@\w+\{([^,\s]+)\s*,")


def extract_anchors(notes_text: str) -> list[str]:
    """Cite keys referenced in the notes, in first-seen order, deduplicated."""
    seen: dict[str, None] = {}
    for key in _ANCHOR.findall(notes_text):
        seen.setdefault(key.rstrip(".:-"), None)
    return list(seen)


def bib_keys(bib_text: str) -> set[str]:
    return set(_BIB_ENTRY.findall(bib_text))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--notes", type=Path, required=True,
                        help="Path to NOTES.md (or any markdown with [@key] anchors).")
    parser.add_argument("--bib", type=Path, default=None,
                        help="Path to the bib (default: references.bib beside --notes).")
    parser.add_argument("--json", action="store_true",
                        help="Emit a JSON object instead of a plain key list.")
    args = parser.parse_args(argv)

    if not args.notes.is_file():
        print(f"notes not found: {args.notes}", file=sys.stderr)
        return 2
    bib_path = args.bib or args.notes.parent / "references.bib"
    if not bib_path.is_file():
        print(f"bib not found: {bib_path}", file=sys.stderr)
        return 2

    scoped = extract_anchors(args.notes.read_text(encoding="utf-8"))
    available = bib_keys(bib_path.read_text(encoding="utf-8"))
    missing = [k for k in scoped if k not in available]
    resolved = [k for k in scoped if k in available]
    unused = sorted(available - set(scoped))

    print(
        f"scoped {len(scoped)} anchors from {args.notes.name}: "
        f"{len(resolved)} resolve, {len(missing)} dangling "
        f"({len(unused)} bib entries out of scope)",
        file=sys.stderr,
    )
    if missing:
        print("DANGLING (anchor with no bib entry): " + ", ".join(missing), file=sys.stderr)

    if args.json:
        json.dump({"scoped": resolved, "missing": missing, "unused": unused},
                  sys.stdout)
        sys.stdout.write("\n")
    else:
        for k in sorted(resolved):
            print(k)

    return 2 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
