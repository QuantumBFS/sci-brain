"""Parse exported .md dialog files into the standard conversation-dump JSON format.

Supports:
- Claude.ai web export: ## **Human** / ## **Claude** with --- separators
- Generic markdown: ## Human / ## Assistant variants
- Auto-detection of role markers
"""
import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_ROLE_PATTERNS = [
    # Claude.ai bold format: ## **Human** / ## **Claude**
    (re.compile(r"^##\s+\*\*Human\*\*", re.IGNORECASE), "user"),
    (re.compile(r"^##\s+\*\*Claude\*\*", re.IGNORECASE), "assistant"),
    (re.compile(r"^##\s+\*\*Assistant\*\*", re.IGNORECASE), "assistant"),
    (re.compile(r"^##\s+\*\*User\*\*", re.IGNORECASE), "user"),
    # Plain format: ## Human / ## Claude / ## Assistant / ## User
    (re.compile(r"^##\s+Human\s*$", re.IGNORECASE), "user"),
    (re.compile(r"^##\s+Claude\s*$", re.IGNORECASE), "assistant"),
    (re.compile(r"^##\s+Assistant\s*$", re.IGNORECASE), "assistant"),
    (re.compile(r"^##\s+User\s*$", re.IGNORECASE), "user"),
    # Colon format: **Human:** / **Claude:**
    (re.compile(r"^\*\*Human\*\*\s*:", re.IGNORECASE), "user"),
    (re.compile(r"^\*\*Claude\*\*\s*:", re.IGNORECASE), "assistant"),
    (re.compile(r"^\*\*Assistant\*\*\s*:", re.IGNORECASE), "assistant"),
    (re.compile(r"^\*\*User\*\*\s*:", re.IGNORECASE), "user"),
]


def _detect_role(line):
    """Return 'user', 'assistant', or None for a line."""
    stripped = line.strip()
    for pattern, role in _ROLE_PATTERNS:
        if pattern.match(stripped):
            return role
    return None


def _truncate(text, max_chars=500):
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."


def parse_md_file(filepath):
    """Parse a markdown dialog file into a list of (role, text) segments.

    Strategy: scan line-by-line, detect role markers, and accumulate text
    between markers. This handles --- separators, blank lines, and nested
    markdown headings within assistant responses gracefully.
    """
    path = Path(filepath)
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")

    segments = []
    current_role = None
    current_lines = []

    for line in lines:
        role = _detect_role(line)
        if role is not None:
            if current_role is not None:
                body = "\n".join(current_lines).strip()
                if body:
                    segments.append({"role": current_role, "text": body})
            current_role = role
            current_lines = []
        elif current_role is not None:
            stripped = line.strip()
            if stripped == "---":
                continue
            current_lines.append(line)

    if current_role is not None:
        body = "\n".join(current_lines).strip()
        if body:
            segments.append({"role": current_role, "text": body})

    return segments


def segments_to_turns(segments):
    """Pair consecutive user+assistant segments into turns."""
    turns = []
    idx = 0
    i = 0
    while i < len(segments):
        seg = segments[i]
        if seg["role"] == "user":
            user_text = seg["text"]
            assistant_parts = []
            i += 1
            while i < len(segments) and segments[i]["role"] == "assistant":
                assistant_parts.append(segments[i]["text"])
                i += 1
            idx += 1
            assistant_text = "\n".join(assistant_parts) if assistant_parts else "[no response]"
            turns.append({
                "index": idx,
                "user": user_text,
                "assistant": _truncate(assistant_text),
            })
        else:
            i += 1

    return turns


def build_output(filepath, turns):
    """Build the standard conversation-dump JSON structure."""
    path = Path(filepath)
    try:
        mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        timestamp = mtime.isoformat()
    except OSError:
        timestamp = ""

    return {
        "source": "md-import",
        "session_id": path.stem,
        "timestamp": timestamp,
        "turns": turns,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Parse .md dialog files into conversation-dump JSON format"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # parse subcommand
    parse_p = sub.add_parser("parse", help="Parse a single .md file")
    parse_p.add_argument("file", help="Path to the .md dialog file")

    # list subcommand
    list_p = sub.add_parser("list", help="List .md dialog files in a directory")
    list_p.add_argument("directory", help="Directory to scan for .md files")

    # batch subcommand
    batch_p = sub.add_parser("batch", help="Parse all .md files in a directory")
    batch_p.add_argument("directory", help="Directory containing .md files")
    batch_p.add_argument("--outdir", help="Output directory for JSON files")

    args = parser.parse_args()

    if args.command == "parse":
        segments = parse_md_file(args.file)
        turns = segments_to_turns(segments)
        output = build_output(args.file, turns)
        json.dump(output, sys.stdout, indent=2, ensure_ascii=False)
        print()

    elif args.command == "list":
        directory = Path(args.directory)
        if not directory.is_dir():
            print(f"Not a directory: {directory}", file=sys.stderr)
            sys.exit(1)
        md_files = sorted(directory.glob("*.md"))
        for i, f in enumerate(md_files, 1):
            segments = parse_md_file(f)
            turns = segments_to_turns(segments)
            print(f"[{i}] {f.name} | {len(turns)} turns")

    elif args.command == "batch":
        directory = Path(args.directory)
        outdir = Path(args.outdir) if args.outdir else directory
        outdir.mkdir(parents=True, exist_ok=True)

        md_files = sorted(directory.glob("*.md"))
        for f in md_files:
            segments = parse_md_file(f)
            turns = segments_to_turns(segments)
            if not turns:
                continue
            output = build_output(f, turns)
            out_path = outdir / f"{f.stem}.json"
            out_path.write_text(
                json.dumps(output, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            print(f"Wrote {out_path} ({len(turns)} turns)")


if __name__ == "__main__":
    main()
