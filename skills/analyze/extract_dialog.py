"""Extract and normalize dialog from Claude Code and Codex CLI session logs."""
import json
import re


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
    """Check if text is entirely system-reminder tags or environment injection."""
    stripped = re.sub(r"<system-reminder>.*?</system-reminder>", "", text, flags=re.DOTALL).strip()
    return len(stripped) == 0


def _truncate(text, max_chars=500):
    """Truncate text to max_chars, appending '...' if truncated."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."


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
