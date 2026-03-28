import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "analyze"))
from extract_dialog import extract_claude_turns


def test_extract_claude_text_content():
    """String message.content is extracted as-is."""
    lines = [
        json.dumps({
            "type": "user",
            "message": {"role": "user", "content": "What is TDD?"},
            "timestamp": "2026-03-28T10:00:00Z",
        }),
        json.dumps({
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "thinking", "thinking": "Let me think..."},
                    {"type": "text", "text": "TDD stands for Test-Driven Development."},
                ],
            },
            "timestamp": "2026-03-28T10:00:05Z",
        }),
    ]
    turns = extract_claude_turns(lines)
    assert len(turns) == 1
    assert turns[0]["index"] == 1
    assert turns[0]["user"] == "What is TDD?"
    assert turns[0]["assistant"] == "TDD stands for Test-Driven Development."


def test_claude_skips_non_conversational():
    """Progress, file-history-snapshot, tool_use-only records are ignored."""
    lines = [
        json.dumps({"type": "progress", "data": {"type": "hook_progress"}}),
        json.dumps({"type": "file-history-snapshot", "snapshot": {}}),
        json.dumps({
            "type": "user",
            "message": {"role": "user", "content": "Hello"},
            "timestamp": "2026-03-28T10:00:00Z",
        }),
        json.dumps({
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [{"type": "tool_use", "id": "t1", "name": "Read", "input": {}}],
            },
            "timestamp": "2026-03-28T10:00:01Z",
        }),
        json.dumps({
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [{"type": "text", "text": "Hi there!"}],
            },
            "timestamp": "2026-03-28T10:00:02Z",
        }),
    ]
    turns = extract_claude_turns(lines)
    assert len(turns) == 1
    assert turns[0]["user"] == "Hello"
    assert turns[0]["assistant"] == "Hi there!"


def test_claude_skips_system_preamble():
    """User messages that are only system-reminder tags are skipped."""
    lines = [
        json.dumps({
            "type": "user",
            "message": {"role": "user", "content": "<system-reminder>SessionStart hook</system-reminder>"},
            "timestamp": "2026-03-28T10:00:00Z",
        }),
        json.dumps({
            "type": "user",
            "message": {"role": "user", "content": "Real question here"},
            "timestamp": "2026-03-28T10:01:00Z",
        }),
        json.dumps({
            "type": "assistant",
            "message": {"role": "assistant", "content": "Real answer"},
            "timestamp": "2026-03-28T10:01:05Z",
        }),
    ]
    turns = extract_claude_turns(lines)
    assert len(turns) == 1
    assert turns[0]["user"] == "Real question here"


def test_claude_merges_consecutive_assistant():
    """Multiple assistant records before next user are merged."""
    lines = [
        json.dumps({
            "type": "user",
            "message": {"role": "user", "content": "Explain X"},
            "timestamp": "2026-03-28T10:00:00Z",
        }),
        json.dumps({
            "type": "assistant",
            "message": {"role": "assistant", "content": "Part 1."},
            "timestamp": "2026-03-28T10:00:01Z",
        }),
        json.dumps({
            "type": "assistant",
            "message": {"role": "assistant", "content": "Part 2."},
            "timestamp": "2026-03-28T10:00:02Z",
        }),
    ]
    turns = extract_claude_turns(lines)
    assert len(turns) == 1
    assert "Part 1." in turns[0]["assistant"]
    assert "Part 2." in turns[0]["assistant"]


def test_claude_empty_input():
    """Empty input returns empty list."""
    assert extract_claude_turns([]) == []


def test_claude_malformed_json():
    """Malformed JSON lines are silently skipped."""
    lines = [
        "not valid json",
        json.dumps({
            "type": "user",
            "message": {"role": "user", "content": "Valid"},
            "timestamp": "2026-03-28T10:00:00Z",
        }),
        json.dumps({
            "type": "assistant",
            "message": {"role": "assistant", "content": "Response"},
            "timestamp": "2026-03-28T10:00:01Z",
        }),
    ]
    turns = extract_claude_turns(lines)
    assert len(turns) == 1
    assert turns[0]["user"] == "Valid"


def test_claude_trailing_user_no_response():
    """User message with no following assistant gets '[no response]'."""
    lines = [
        json.dumps({
            "type": "user",
            "message": {"role": "user", "content": "Last question"},
            "timestamp": "2026-03-28T10:00:00Z",
        }),
    ]
    turns = extract_claude_turns(lines)
    assert len(turns) == 1
    assert turns[0]["assistant"] == "[no response]"


def test_claude_truncates_long_assistant():
    """Assistant responses longer than 500 chars are truncated."""
    long_text = "x" * 600
    lines = [
        json.dumps({
            "type": "user",
            "message": {"role": "user", "content": "Tell me everything"},
            "timestamp": "2026-03-28T10:00:00Z",
        }),
        json.dumps({
            "type": "assistant",
            "message": {"role": "assistant", "content": long_text},
            "timestamp": "2026-03-28T10:00:01Z",
        }),
    ]
    turns = extract_claude_turns(lines)
    assert len(turns) == 1
    assert len(turns[0]["assistant"]) == 503  # 500 + "..."
    assert turns[0]["assistant"].endswith("...")
