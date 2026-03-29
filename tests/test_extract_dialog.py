import json
import subprocess
import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "conversation-dump"))
from extract_dialog import extract_claude_turns, extract_codex_turns, list_claude_sessions


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


def test_extract_codex_turns():
    """Codex response_item records with role user/assistant are extracted."""
    lines = [
        json.dumps({"type": "session_meta", "timestamp": "2026-03-28T10:00:00Z", "payload": {"model": "gpt-5.4"}}),
        json.dumps({"type": "response_item", "timestamp": "2026-03-28T10:00:01Z", "payload": {"role": "user", "content": [{"type": "input_text", "text": "What is Rust?"}]}}),
        json.dumps({"type": "event_msg", "timestamp": "2026-03-28T10:00:02Z", "payload": {"event": "task_started"}}),
        json.dumps({"type": "response_item", "timestamp": "2026-03-28T10:00:03Z", "payload": {"role": "assistant", "content": [{"type": "output_text", "text": "Rust is a systems language."}]}}),
    ]
    turns = extract_codex_turns(lines)
    assert len(turns) == 1
    assert turns[0]["user"] == "What is Rust?"
    assert turns[0]["assistant"] == "Rust is a systems language."


def test_codex_skips_developer_and_no_role():
    """Developer (system) messages and role=N/A items are skipped."""
    lines = [
        json.dumps({"type": "response_item", "timestamp": "2026-03-28T10:00:00Z", "payload": {"role": "developer", "content": [{"type": "input_text", "text": "System instructions here"}]}}),
        json.dumps({"type": "response_item", "timestamp": "2026-03-28T10:00:01Z", "payload": {"role": "user", "content": [{"type": "input_text", "text": "Hello"}]}}),
        json.dumps({"type": "response_item", "timestamp": "2026-03-28T10:00:02Z", "payload": {"content": "some string without role"}}),
        json.dumps({"type": "response_item", "timestamp": "2026-03-28T10:00:03Z", "payload": {"role": "assistant", "content": [{"type": "output_text", "text": "Hi!"}]}}),
    ]
    turns = extract_codex_turns(lines)
    assert len(turns) == 1
    assert turns[0]["user"] == "Hello"
    assert turns[0]["assistant"] == "Hi!"


def test_list_claude_sessions(tmp_path):
    """Lists sessions from a project directory, showing timestamp and first user message."""
    project_dir = tmp_path / "projects" / "-home-leo-test"
    project_dir.mkdir(parents=True)
    session_file = project_dir / "abc-123.jsonl"
    session_file.write_text(
        json.dumps({
            "type": "user",
            "message": {"role": "user", "content": "First real question"},
            "timestamp": "2026-03-28T10:00:00Z",
        }) + "\n"
    )
    sub_dir = project_dir / "abc-123" / "subagents"
    sub_dir.mkdir(parents=True)
    (sub_dir / "agent-x.jsonl").write_text('{"type":"user","message":{"role":"user","content":"sub"}}\n')

    sessions = list_claude_sessions(str(tmp_path / "projects"), project_filter="-home-leo-test")
    assert len(sessions) == 1
    assert sessions[0]["session_id"] == "abc-123"
    assert "First real question" in sessions[0]["preview"]


def test_cli_extract_claude(tmp_path):
    """CLI extract command outputs valid JSON to stdout."""
    project_dir = tmp_path / "projects" / "-test"
    project_dir.mkdir(parents=True)
    session_file = project_dir / "sess-1.jsonl"
    session_file.write_text(
        json.dumps({
            "type": "user",
            "message": {"role": "user", "content": "What is X?"},
            "timestamp": "2026-03-28T10:00:00Z",
        })
        + "\n"
        + json.dumps({
            "type": "assistant",
            "message": {"role": "assistant", "content": "X is Y."},
            "timestamp": "2026-03-28T10:00:01Z",
        })
        + "\n"
    )
    script = str(Path(__file__).parent.parent / "skills" / "conversation-dump" / "extract_dialog.py")
    result = subprocess.run(
        [sys.executable, script, "extract", "--source", "claude", "--session", "sess-1",
         "--projects-root", str(tmp_path / "projects")],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["source"] == "claude"
    assert data["session_id"] == "sess-1"
    assert len(data["turns"]) == 1
    assert data["turns"][0]["user"] == "What is X?"
