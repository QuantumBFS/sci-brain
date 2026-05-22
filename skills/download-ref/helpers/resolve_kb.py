#!/usr/bin/env python3
"""Resolve a project's or advisor's knowledge-base directory.

For project KBs: walks up from `start` looking for a `.git/` directory.
If found, returns `<git-root>/<KB-name>`. If not found and `start` is at
or above $HOME, returns None (the caller should prompt the user).
Otherwise falls back to `start/<KB-name>`.

For advisor KBs: pass `--advisor <slug>` and the path is rooted at the
plugin checkout — `<plugin-root>/advisors/<slug>/<KB-name>`. `--start`
is ignored when `--advisor` is set.

The KB directory name defaults to `.knowledge` and can be overridden via
the `SCIBRAIN_KB_DIRNAME` environment variable (e.g. `kb`, `papers`).

This is the single source of truth for "where does the KB live" across
download-ref, survey, researchstyle, ideas, and incarnate.

CLI:
    python3 resolve_kb.py [--start DIR] [--advisor SLUG]
        --start defaults to $PWD. Prints the resolved KB path to stdout,
        or writes "unresolvable from <start>" to stderr and exits 2.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

DEFAULT_KB_DIRNAME = ".knowledge"


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
    raw = os.environ.get("SCIBRAIN_KB_DIRNAME")
    if raw is None or raw == "":
        return DEFAULT_KB_DIRNAME
    if Path(raw).is_absolute() or raw in {".", ".."} or "/" in raw or "\\" in raw:
        raise ValueError(
            "SCIBRAIN_KB_DIRNAME must be a single directory name, "
            f"not an absolute or nested path: {raw!r}"
        )
    return raw


def _plugin_root() -> Path:
    """Plugin root (the sci-brain checkout). Used to locate advisors/."""
    return Path(__file__).resolve().parents[3]


def resolve_kb(start: Optional[Path] = None, advisor: Optional[str] = None) -> Optional[Path]:
    """Return the resolved KB path, or None if the caller should prompt.

    When `advisor` is given, returns `<plugin-root>/advisors/<slug>/<kb-name>`
    and ignores `start`. Otherwise resolves the project KB by walking up
    from `start` looking for a git root.
    """
    name = _kb_dirname()
    if advisor:
        return _plugin_root() / "advisors" / advisor / name
    start = (start or Path.cwd()).resolve()
    git_root = _find_git_root(start)
    if git_root is not None:
        return git_root / name
    if _is_at_or_above_home(start):
        return None
    return start / name


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=Path, default=None,
                        help="Starting directory for project-KB resolution (default: $PWD)")
    parser.add_argument("--advisor", default=None,
                        help="Advisor slug (lowercase hyphenated). When set, returns the "
                             "advisor KB path under <plugin-root>/advisors/<slug>/.")
    args = parser.parse_args(argv)
    try:
        kb = resolve_kb(start=args.start, advisor=args.advisor)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if kb is None:
        print(f"unresolvable from {args.start or Path.cwd()}", file=sys.stderr)
        return 2
    print(str(kb))
    return 0


if __name__ == "__main__":
    sys.exit(main())
