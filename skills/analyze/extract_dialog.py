"""Extract and normalize dialog from Claude Code and Codex CLI session logs."""
import argparse
import json
import re
import sys
from pathlib import Path


def _extract_text(content):
    """Extract human-readable text from message.content (string or array)."""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
            elif isinstance(block, dict) and block.get("type") == "input_text":
                parts.append(block.get("text", ""))
            elif isinstance(block, dict) and block.get("type") == "output_text":
                parts.append(block.get("text", ""))
        return "\n".join(parts).strip()
    return ""


def _is_system_preamble(text):
    """Check if text is entirely system/environment tags with no real user content."""
    stripped = text
    # Remove XML-style system tags
    for tag in ("system-reminder", "environment_context", "command-message",
                "command-name", "INSTRUCTIONS", "instructions"):
        stripped = re.sub(rf"<{tag}>.*?</{tag}>", "", stripped, flags=re.DOTALL)
    stripped = stripped.strip()
    if len(stripped) == 0:
        return True
    # Detect AGENTS.md / CLAUDE.md preamble injections
    if stripped.startswith("# AGENTS.md") or stripped.startswith("# CLAUDE.md"):
        return True
    return False


def _truncate(text, max_chars=500):
    """Truncate text to max_chars, appending '...' if truncated."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."


def _cwd_to_project_key(cwd):
    """Convert a filesystem path to Claude's project directory key format.

    Replaces '/' with '-', keeping the leading '-'.
    Example: '/home/leo/myproject' -> '-home-leo-myproject'
    """
    return cwd.replace("/", "-")


def list_claude_sessions(projects_root, project_filter=None):
    """List sessions from Claude Code projects directory.

    Args:
        projects_root: path to ~/.claude/projects or equivalent
        project_filter: if given, only look in this project subdirectory name

    Returns:
        list of dicts with keys: session_id, project, timestamp, preview
        sorted by timestamp descending
    """
    root = Path(projects_root)
    if not root.exists():
        return []

    sessions = []
    if project_filter:
        project_dirs = [root / project_filter] if (root / project_filter).is_dir() else []
    else:
        project_dirs = [p for p in root.iterdir() if p.is_dir()]

    for project_dir in project_dirs:
        for jsonl_file in project_dir.glob("*.jsonl"):
            # Skip subagent files — they live under <session_id>/subagents/
            # (i.e. the parent's parent is not the project dir)
            if jsonl_file.parent != project_dir:
                continue

            session_id = jsonl_file.stem
            timestamp = None
            preview = ""

            try:
                with jsonl_file.open() as f:
                    for raw in f:
                        raw = raw.strip()
                        if not raw:
                            continue
                        try:
                            rec = json.loads(raw)
                        except json.JSONDecodeError:
                            continue
                        # Find first real user message
                        if rec.get("type") == "user":
                            msg = rec.get("message", {})
                            text = _extract_text(msg.get("content", ""))
                            if text and not _is_system_preamble(text):
                                if timestamp is None:
                                    timestamp = rec.get("timestamp", "")
                                preview = text[:80]
                                break
                        # Capture timestamp from any record if not yet set
                        if timestamp is None:
                            timestamp = rec.get("timestamp", "")
            except OSError:
                continue

            sessions.append({
                "session_id": session_id,
                "project": project_dir.name,
                "timestamp": timestamp or "",
                "preview": preview,
            })

    sessions.sort(key=lambda s: s["timestamp"], reverse=True)
    return sessions


def list_codex_sessions(sessions_root):
    """List Codex sessions from ~/.codex/sessions/ or equivalent.

    Args:
        sessions_root: path to the Codex sessions directory

    Returns:
        list of dicts with keys: session_id, timestamp, preview, path
        sorted by timestamp descending
    """
    root = Path(sessions_root)
    if not root.exists():
        return []

    sessions = []
    for jsonl_file in root.rglob("rollout-*.jsonl"):
        session_id = jsonl_file.stem
        timestamp = None
        preview = ""

        try:
            with jsonl_file.open() as f:
                for raw in f:
                    raw = raw.strip()
                    if not raw:
                        continue
                    try:
                        rec = json.loads(raw)
                    except json.JSONDecodeError:
                        continue
                    if timestamp is None:
                        timestamp = rec.get("timestamp", "")
                    if rec.get("type") == "response_item":
                        payload = rec.get("payload", {})
                        if payload.get("role") == "user":
                            text = _extract_text(payload.get("content", []))
                            if text and not _is_system_preamble(text):
                                preview = text[:80]
                                break
        except OSError:
            continue

        sessions.append({
            "session_id": session_id,
            "timestamp": timestamp or "",
            "preview": preview,
            "path": str(jsonl_file),
        })

    sessions.sort(key=lambda s: s["timestamp"], reverse=True)
    return sessions


def extract_codex_turns(lines):
    """Parse Codex CLI JSONL lines into normalized turns.

    Args:
        lines: iterable of JSONL string lines

    Returns:
        list of dicts with keys: index, user, assistant
    """
    records = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("type") != "response_item":
            continue
        payload = rec.get("payload", {})
        role = payload.get("role")
        if role not in ("user", "assistant"):
            continue
        content = payload.get("content", [])
        text = _extract_text(content)
        if not text:
            continue
        if role == "user" and _is_system_preamble(text):
            continue
        records.append({"role": role, "text": text})

    turns = []
    idx = 0
    i = 0
    while i < len(records):
        r = records[i]
        if r["role"] == "user":
            user_text = r["text"]
            assistant_parts = []
            i += 1
            while i < len(records) and records[i]["role"] == "assistant":
                assistant_parts.append(records[i]["text"])
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


def extract_claude_turns(lines):
    """Parse Claude Code JSONL lines into normalized turns.

    Args:
        lines: iterable of JSONL string lines

    Returns:
        list of dicts with keys: index, user, assistant
    """
    records = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        rec_type = rec.get("type")
        if rec_type not in ("user", "assistant"):
            continue
        msg = rec.get("message", {})
        if "content" not in msg:
            continue
        text = _extract_text(msg["content"])
        if not text:
            continue
        records.append({"role": rec_type, "text": text})

    turns = []
    idx = 0
    i = 0
    while i < len(records):
        r = records[i]
        if r["role"] == "user":
            if _is_system_preamble(r["text"]):
                i += 1
                continue
            user_text = r["text"]
            assistant_parts = []
            i += 1
            while i < len(records) and records[i]["role"] == "assistant":
                assistant_parts.append(records[i]["text"])
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


def main():
    """CLI entry point for listing and extracting dialog sessions."""
    parser = argparse.ArgumentParser(description="Extract dialog from Claude Code and Codex sessions")
    sub = parser.add_subparsers(dest="command", required=True)

    # list subcommand
    list_p = sub.add_parser("list", help="List available sessions")
    list_p.add_argument("--source", choices=["claude", "codex"], required=True)
    list_p.add_argument("--project", help="Project directory name to filter (Claude only)")
    list_p.add_argument(
        "--projects-root",
        default=str(Path.home() / ".claude" / "projects"),
        help="Root of Claude projects directory",
    )
    list_p.add_argument(
        "--sessions-root",
        default=str(Path.home() / ".codex" / "sessions"),
        help="Root of Codex sessions directory",
    )

    # extract subcommand
    ext_p = sub.add_parser("extract", help="Extract dialog from a session")
    ext_p.add_argument("--source", choices=["claude", "codex"], required=True)
    ext_p.add_argument("--session", required=True, help="Session ID to extract")
    ext_p.add_argument(
        "--projects-root",
        default=str(Path.home() / ".claude" / "projects"),
        help="Root of Claude projects directory",
    )
    ext_p.add_argument(
        "--sessions-root",
        default=str(Path.home() / ".codex" / "sessions"),
        help="Root of Codex sessions directory",
    )

    args = parser.parse_args()

    if args.command == "list":
        if args.source == "claude":
            project_filter = args.project or _cwd_to_project_key(str(Path.cwd()))
            sessions = list_claude_sessions(args.projects_root, project_filter=project_filter)
        else:
            sessions = list_codex_sessions(args.sessions_root)

        for i, s in enumerate(sessions, 1):
            ts = s["timestamp"][:16].replace("T", " ") if s.get("timestamp") else "unknown"
            session_id = s["session_id"]
            preview = s.get("preview", "")
            print(f'[{i}] {ts} | {session_id} | "{preview}"')

    elif args.command == "extract":
        session_file = None
        timestamp = None

        if args.source == "claude":
            claude_projects = Path(args.projects_root)
            for candidate in claude_projects.rglob(f"{args.session}.jsonl"):
                # Skip subagent files (they sit inside <session>/subagents/)
                if "subagents" in candidate.parts:
                    continue
                session_file = candidate
                break
        else:
            codex_root = Path(args.sessions_root)
            for candidate in codex_root.rglob("*.jsonl"):
                if args.session in candidate.stem:
                    session_file = candidate
                    break

        if session_file is None:
            print(f"Session '{args.session}' not found.", file=sys.stderr)
            sys.exit(1)

        with session_file.open() as f:
            lines = f.readlines()

        # Get timestamp from first parseable record
        for raw in lines:
            raw = raw.strip()
            if not raw:
                continue
            try:
                rec = json.loads(raw)
                timestamp = rec.get("timestamp", "")
                break
            except json.JSONDecodeError:
                continue

        if args.source == "claude":
            turns = extract_claude_turns(lines)
            project = session_file.parent.name if session_file else ""
        else:
            turns = extract_codex_turns(lines)
            project = ""

        output = {
            "source": args.source,
            "session_id": args.session,
            "project": project,
            "timestamp": timestamp or "",
            "turns": turns,
        }
        json.dump(output, sys.stdout, indent=2)
        print()


if __name__ == "__main__":
    main()
