#!/usr/bin/env python3
"""Resolve a project's knowledge-base directory.

Walks up from `start` looking for a `.git/` directory. If found, returns
`<git-root>/<KB-name>`. If not found and `start` is at or above $HOME,
returns None (the caller should prompt the user). Otherwise falls back
to `start/<KB-name>`.

The KB directory name defaults to `.knowledge` and can be overridden via
the `SCIBRAIN_KB_DIRNAME` environment variable (e.g. `kb`, `papers`).

This is the single source of truth for "where does the project KB live"
across download-ref, survey, researchstyle, ideas, and incarnate.

CLI:
    python3 resolve_kb.py [--start DIR]
        DIR defaults to $PWD. Prints the resolved KB path to stdout,
        or writes "unresolvable from <start>" to stderr and exits 2.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Optional


def _find_git_root(start: Path) -> Optional[Path]:
    cur = start.resolve()
    while True:
        if (cur / ".git").exists():
            return cur
        if cur.parent == cur:
            return None
        cur = cur.parent


def _is_at_or_above_home(start: Path) -> bool:
    home = Path(os.environ.get("HOME", "")).resolve()
    s = start.resolve()
    return s == home or home.is_relative_to(s)


def _kb_dirname() -> str:
    """KB directory name. Override via $SCIBRAIN_KB_DIRNAME (default '.knowledge')."""
    return os.environ.get("SCIBRAIN_KB_DIRNAME", ".knowledge")


def resolve_kb(start: Optional[Path] = None) -> Optional[Path]:
    """Return the resolved KB path, or None if the caller should prompt."""
    start = (start or Path.cwd()).resolve()
    name = _kb_dirname()
    git_root = _find_git_root(start)
    if git_root is not None:
        return git_root / name
    if _is_at_or_above_home(start):
        return None
    return start / name


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=Path, default=None,
                        help="Starting directory (default: $PWD)")
    args = parser.parse_args(argv)
    kb = resolve_kb(start=args.start)
    if kb is None:
        print(f"unresolvable from {args.start or Path.cwd()}", file=sys.stderr)
        return 2
    print(str(kb))
    return 0


if __name__ == "__main__":
    sys.exit(main())
