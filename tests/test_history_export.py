"""Faithful text export and independent research-analysis views."""
import copy
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "skills/dump-chat-history/helpers/history.py"
spec = importlib.util.spec_from_file_location("history_export", HELPER)
history = importlib.util.module_from_spec(spec)
spec.loader.exec_module(history)


def corpus():
    return {
        "title": "Designing a Research Website",
        "window": {"start": "2026-09-03T00:00:00+08:00", "end": "2026-09-10T00:00:00+08:00", "timezone": "Asia/Shanghai"},
        "scope": "Synthetic website conversations; human prompts in the PDF.",
        "coverage": "Synthetic fixtures only; no private history.",
        "sources": [{"id": "S1", "location": "fixture.jsonl", "note": "Synthetic source."}],
        "entries": [entry("P1", "  keep \"quotes\", #headings, $math$ and ```code```\n  indents.\n")],
    }


def entry(identifier, text, role="user", **extra):
    return {"id": identifier, "source": "codex", "session_id": "s1", "timestamp": "2026-09-07T00:00:00+08:00",
            "role": role, "kind": "prompt" if role == "user" else "response", "text": text,
            "source_id": "S1", "provenance": "S1, record " + identifier, **extra}


def test_validation_preserves_original_and_rejects_changed_digest():
    data = corpus()
    before = copy.deepcopy(data)
    validated = history.validate(data)
    assert data == before
    assert validated["entries"][0]["text"] == data["entries"][0]["text"]
    validated["entries"][0]["text"] += "modified"
    with pytest.raises(ValueError, match="digest mismatch"):
        history.validate(validated)


def test_message_boundaries_not_session_creation_control_date_coverage():
    data = corpus()
    data["entries"][0]["timestamp"] = data["window"]["end"]
    with pytest.raises(ValueError, match="outside"):
        history.validate(data)
    data["entries"][0]["outside_window"] = True
    history.validate(data)
    data["entries"][0]["timestamp"] = None
    with pytest.raises(ValueError, match="undated"):
        history.validate(data)
    data["entries"][0]["undated"] = True
    history.validate(data)


def test_bad_timezone_order_and_provenance_are_not_silently_accepted():
    data = corpus()
    data["entries"][0]["timestamp"] = "2026-09-07T00:00:00"
    with pytest.raises(ValueError, match="offset"):
        history.validate(data)
    data = corpus()
    data["entries"].append(entry("P2", "earlier", timestamp="2026-09-06T00:00:00+08:00"))
    with pytest.raises(ValueError, match="chronological"):
        history.validate(data)
    data = corpus()
    data["entries"][0]["source_id"] = "missing"
    with pytest.raises(ValueError, match="unknown source"):
        history.validate(data)


def test_markdown_fences_preserve_arbitrary_prompt_contents():
    text = "\n```python\nprint('hi')\n```\n````\n  trailing spaces  \n"
    rendered = history.literal(text)
    fence = rendered.splitlines()[0].removesuffix("text")
    assert len(fence) == 5
    assert rendered == fence + "text\n" + text + "\n" + fence + "\n"


def test_analysis_keeps_distinct_repetitions_branches_and_full_answers():
    data = corpus()
    data["entries"] = [entry("P1", "yes"), entry("A1", "a" * 1200, "assistant"),
                       entry("P2", "yes", kind="answer", question="Which layout?"),
                       entry("P3", "yes", branch_id="other"), entry("A3", "branch reply", "assistant", branch_id="other")]
    before = copy.deepcopy(data)
    sessions = list(history.analysis_sessions(data, "history.json").values())
    assert data == before
    assert len(sessions) == 2
    main = next(s for s in sessions if s["branch_id"] is None)
    assert [t["user"] for t in main["turns"]] == ["yes", "yes"]
    assert main["turns"][0]["assistant"] == "a" * 1200
    assert main["turns"][1]["assistant"] == ""
    assert main["turns"][1]["question"] == "Which layout?"
    assert main["turns"][0]["assistant_entry_ids"] == ["A1"]


def test_analysis_preserves_multipart_blocks_and_never_uses_ids_as_paths():
    data = corpus()
    data["entries"] = [entry("b1", "part one", message_id="m1", session_id="../../escape"),
                       entry("b2", "  part two", message_id="m1", session_id="../../escape")]
    sessions = history.analysis_sessions(data, "history.json")
    name, session = next(iter(sessions.items()))
    assert re.fullmatch(r"[a-f0-9]{20}\.json", name)
    assert len(session["turns"]) == 1
    assert session["turns"][0]["user_blocks"] == ["part one", "  part two"]
    assert session["turns"][0]["user_entry_ids"] == ["b1", "b2"]


def test_cli_writes_fresh_bundle_and_analysis_without_mutating_archive(tmp_path):
    source = tmp_path / "input.json"
    source.write_text(json.dumps(corpus()))
    original = source.read_bytes()
    out = tmp_path / "render"
    result = subprocess.run([sys.executable, str(HELPER), "render", str(source), "--outdir", str(out)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert source.read_bytes() == original
    assert (out / "report.typ").is_file()
    assert corpus()["entries"][0]["text"] in (out / "transcript.md").read_text()
    repeated = subprocess.run([sys.executable, str(HELPER), "render", str(source), "--outdir", str(out)], capture_output=True, text=True)
    assert repeated.returncode != 0
    result = subprocess.run([sys.executable, str(HELPER), "analysis", str(out / "history.json"), "--outdir", str(tmp_path / "analysis")], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert len(list((tmp_path / "analysis").glob("*.json"))) == 1
    assert source.read_bytes() == original


@pytest.mark.skipif(not shutil.which("typst") or not shutil.which("pdftotext"), reason="PDF toolchain not installed")
def test_pdf_handles_long_original_text_and_structured_answers(tmp_path):
    data = corpus()
    long_text = "\n".join(f"Original line {i:03}: keep #markup, $literal$, `code` and punctuation." for i in range(140))
    data["entries"].extend([entry("P2", long_text), entry("D1", "Keep all original words.", kind="answer", question="Which content should remain?"),
                            entry("A1", "Assistant context stays in JSON.", "assistant")])
    source = tmp_path / "source.json"
    source.write_text(json.dumps(data))
    out = tmp_path / "report"
    subprocess.run([sys.executable, str(HELPER), "render", str(source), "--outdir", str(out)], check=True)
    subprocess.run(["typst", "compile", str(out / "report.typ"), str(out / "report.pdf")], check=True)
    extracted = subprocess.check_output(["pdftotext", "-layout", str(out / "report.pdf"), "-"], text=True)
    footer = re.compile(re.escape(data["title"]) + r"\s+\d+\s*$")
    extracted = "\n".join(line for line in extracted.splitlines() if not footer.fullmatch(line))
    normalize = lambda value: re.sub(r"\s+", "", value)
    for item in data["entries"]:
        if item["role"] == "user":
            assert normalize(item["text"]) in normalize(extracted)
    assert "Designing a Research Website" in extracted
    assert "Assistant context stays in JSON." not in extracted
