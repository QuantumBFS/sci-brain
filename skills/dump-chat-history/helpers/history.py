"""Validate a reconciled history export and write reading or analysis artifacts."""
import argparse
import copy
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def instant(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.utcoffset() is None:
        raise ValueError(f"timestamp needs a UTC offset: {value}")
    return parsed


def required_text(record, field):
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a nonempty string")
    return value


def validate(data):
    """Validate declared provenance/bounds without changing original strings."""
    data = copy.deepcopy(data)
    for field in ("title", "scope", "coverage"):
        required_text(data, field)
    window = data["window"]
    ZoneInfo(window["timezone"])
    start = instant(window["start"]) if window["start"] is not None else None
    end = instant(window["end"])
    if start is not None and start >= end:
        raise ValueError("window start must precede end")
    source_ids = set()
    for source in data["sources"]:
        identifier = required_text(source, "id")
        required_text(source, "location")
        if identifier in source_ids:
            raise ValueError(f"duplicate source ID: {identifier}")
        source_ids.add(identifier)
    seen = set()
    previous_time = None
    reached_undated = False
    for entry in data["entries"]:
        for field in ("id", "source", "session_id", "kind", "provenance", "source_id"):
            required_text(entry, field)
        if entry["id"] in seen:
            raise ValueError(f"duplicate entry ID: {entry['id']}")
        seen.add(entry["id"])
        if entry["source_id"] not in source_ids:
            raise ValueError(f"unknown source ID: {entry['source_id']}")
        if entry["role"] not in ("user", "assistant"):
            raise ValueError("only user/assistant text belongs in the transcript")
        if not isinstance(entry["text"], str):
            raise ValueError("text must be a string")
        if entry["timestamp"] is None:
            if entry.get("undated") is not True:
                raise ValueError("missing timestamp requires undated: true")
            reached_undated = True
        else:
            current = instant(entry["timestamp"])
            if reached_undated or (previous_time is not None and current < previous_time):
                raise ValueError("dated entries must be chronological, before undated entries")
            previous_time = current
            within = (start is None or current >= start) and current < end
            if not within and entry.get("outside_window") is not True:
                raise ValueError(f"entry {entry['id']} is outside the selected window")
        digest = hashlib.sha256(entry["text"].encode("utf-8")).hexdigest()
        if "text_sha256" in entry and entry["text_sha256"] != digest:
            raise ValueError(f"text digest mismatch: {entry['id']}")
        entry["text_sha256"] = digest
    return data


def literal(text):
    """Fence arbitrary text without treating its Markdown as document structure."""
    fence = "`" * max(3, 1 + max((len(m.group()) for m in re.finditer(r"`+", text)), default=0))
    return f"{fence}text\n{text}\n{fence}\n"


def markdown(data):
    parts = [f"# {data['title']}\n\n{data['scope']}\n\n{data['coverage']}\n"]
    for entry in data["entries"]:
        parts.append(f"\n## {entry['id']} · {entry['source']} · {entry['session_id']} · {entry['role']}\n")
        parts.append(f"\nTime: {entry['timestamp'] or 'unavailable'}; source: {entry['provenance']}\n\n")
        if "question" in entry:
            parts.append("Question:\n\n" + literal(entry["question"]) + "\nAnswer:\n\n")
        parts.append(literal(entry["text"]))
    return "".join(parts)


def analysis_sessions(data, archive):
    """Create analysis views per session/branch, preserving multipart message IDs."""
    groups = {}
    for entry in data["entries"]:
        key = (entry["source"], entry["session_id"], entry.get("branch_id"))
        groups.setdefault(key, []).append(entry)
    result = {}
    for key, entries in groups.items():
        turns = []
        current = None
        for entry in entries:
            if entry["role"] == "user":
                same_message = (current is not None and entry.get("message_id") is not None
                                and entry["message_id"] == current.get("message_id")
                                and not current["assistant_entry_ids"])
                if same_message:
                    # Original block boundaries stay explicit; joining is a derived view.
                    current["user_blocks"].append(entry["text"])
                    current["user"] = "\n".join(current["user_blocks"])
                    current["user_entry_ids"].append(entry["id"])
                    continue
                current = {"index": len(turns) + 1, "user": entry["text"],
                           "user_blocks": [entry["text"]], "assistant": "", "assistant_blocks": [],
                           "user_entry_ids": [entry["id"]], "assistant_entry_ids": [],
                           "timestamp": entry["timestamp"], "message_id": entry.get("message_id"),
                           "kind": entry["kind"], "provenance": entry["provenance"]}
                for field in ("question", "turn_id", "outside_window", "undated", "attachment_note"):
                    if field in entry:
                        current[field] = entry[field]
                turns.append(current)
            elif current is not None:
                current["assistant_blocks"].append(entry["text"])
                current["assistant"] = "\n".join(current["assistant_blocks"])
                current["assistant_entry_ids"].append(entry["id"])
        if not turns:
            continue
        name = hashlib.sha256(json.dumps(key).encode()).hexdigest()[:20]
        result[name + ".json"] = {"source": key[0], "session_id": key[1], "branch_id": key[2],
                                  "archive": str(archive), "timestamp": turns[0]["timestamp"],
                                  "grouping": "Transcript order, not causal attribution; missing replies are empty strings.",
                                  "turns": turns}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("render", "analysis", "validate"))
    parser.add_argument("history", type=Path)
    parser.add_argument("--outdir", type=Path)
    args = parser.parse_args()
    try:
        data = validate(json.loads(args.history.read_text(encoding="utf-8")))
        if args.command == "validate":
            print(f"Validated {len(data['entries'])} entries")
            return
        if args.outdir is None:
            parser.error("--outdir is required for render/analysis")
        # A fresh destination protects raw exports and previous analysis results.
        args.outdir.mkdir(parents=True, exist_ok=False)
        if args.command == "render":
            (args.outdir / "history.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            (args.outdir / "transcript.md").write_text(markdown(data), encoding="utf-8")
            template = Path(__file__).resolve().parents[1] / "assets" / "report.typ"
            (args.outdir / "report.typ").write_text(template.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            for name, session in analysis_sessions(data, args.history.resolve()).items():
                (args.outdir / name).write_text(json.dumps(session, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(args.outdir)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.exit(1, f"History export failed: {exc}\n")


if __name__ == "__main__":
    main()
