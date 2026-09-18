"""Render checks for report content that crosses page boundaries."""

import json
import re
import shutil
import sys
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "skills/dump-chat-history/helpers/history.py"
pytestmark = pytest.mark.skipif(
    not shutil.which("typst") or not shutil.which("pdftotext"),
    reason="PDF toolchain not installed",
)


BUNDLED = ["--ignore-system-fonts", "--input", "heading-font=Libertinus Serif"]


def compile_pdf(source, pdf, *extra):
    compiled = subprocess.run(
        ["typst", "compile", *BUNDLED, *extra, str(source), str(pdf)],
        capture_output=True, text=True,
    )
    assert compiled.returncode == 0, compiled.stderr
    assert "warning:" not in compiled.stderr, compiled.stderr
    return subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)


def test_survey_tables_paginate_with_repeated_headers_and_complete_rows(tmp_path):
    for name in ("template.typ", "template.bib"):
        shutil.copy(ROOT / "skills/survey" / name, tmp_path / name)
    source = tmp_path / "template.typ"
    with source.open("a") as stream:
        stream.write('''
#pagebreak()
#problem_table(range(45).map(i => (
  [#i], [Row-#i],
  [Evidence-#i: the result depends on the evaluation protocol and input distribution.],
  [Evaluation team], [Critical],
)))
#pagebreak()
#compare_table(
  (([Method A], [Evidence A]), ([Method B], [Evidence B])),
  columns: (1fr, 2fr), headers: ([Method], [Evidence]),
)
#stage([Custom stage], [Named fill override], fill: rgb("eef3ff"))
#stage([Default stage], [Fill omitted])
''')
    extracted = compile_pdf(source, tmp_path / "report.pdf")
    table_pages = [page for page in extracted.split("\f") if "Row-" in page]
    assert len(table_pages) >= 2
    for page in table_pages:
        for header in ("Problem", "Why it matters", "Who can act", "Urgency"):
            assert header in page
    assert re.findall(r"Row-(\d+)", extracted) == [str(i) for i in range(45)]
    assert re.findall(r"Evidence-(\d+)", extracted) == [str(i) for i in range(45)]
    for text in ("Method A", "Evidence A", "Method B", "Evidence B",
                 "Custom stage", "Named fill override", "Default stage", "Fill omitted"):
        assert text in extracted


@pytest.mark.parametrize("call, message", [
    ("compare_table((([A], [B]),), columns: (1fr, 2fr), headers: ([H1], [H2], [H3]))", "3 headers but 2 columns"),
    ("problem_table((([1], [P], [Why], [Who], [High]), ([2], [P], [Why], [Who])))", "row 2 has 4 cells but the table has 5 columns"),
])
def test_survey_table_shape_mismatch_fails_with_named_location(tmp_path, call, message):
    for name in ("template.typ", "template.bib"):
        shutil.copy(ROOT / "skills/survey" / name, tmp_path / name)
    source = tmp_path / "template.typ"
    with source.open("a") as stream:
        stream.write("\n#" + call + "\n")
    compiled = subprocess.run(
        ["typst", "compile", *BUNDLED, str(source), str(tmp_path / "bad.pdf")],
        capture_output=True, text=True,
    )
    assert compiled.returncode != 0
    assert message in compiled.stderr


def test_chat_history_pdf_opens_with_first_prompt_and_closes_with_sources(tmp_path):
    def entry(identifier, text, **extra):
        return {"id": identifier, "source": "codex", "session_id": "s1", "timestamp": "2026-09-07T00:00:00+08:00",
                "role": "user", "kind": "prompt", "text": text, "source_id": "S1",
                "provenance": "S1, record " + identifier, **extra}
    data = {
        "title": "A Long Topic Title That Should Not Collide With The Page Number In The Footer",
        "subtitle": "Where the plan changed",
        "window": {"start": "2026-09-03T00:00:00+08:00", "end": "2026-09-10T00:00:00+08:00", "timezone": "Asia/Shanghai"},
        "scope": "SCOPE-SENTINEL synthetic sessions.",
        "coverage": "COVERAGE-SENTINEL fixtures only.",
        "sources": [{"id": "S1", "location": "fixture.jsonl", "note": "Synthetic source."}],
        "entries": [entry("P1", "FIRST-PROMPT-SENTINEL design the site.", phase="Phase 1: Scoping"),
                    entry("P2", "\n".join(f"Line {i:03}" for i in range(120)))],
    }
    source = tmp_path / "source.json"
    source.write_text(json.dumps(data))
    out = tmp_path / "report"
    subprocess.run([sys.executable, str(HISTORY), "render", str(source), "--outdir", str(out)], check=True)
    extracted = compile_pdf(out / "report.typ", out / "report.pdf", "--input", "body-font=Libertinus Serif")
    pages = extracted.split("\f")
    assert len(pages) >= 2
    assert "FIRST-PROMPT-SENTINEL" in pages[0]
    assert "Phase 1: Scoping" in pages[0]
    assert "SCOPE-SENTINEL" not in pages[0] and "COVERAGE-SENTINEL" not in pages[0]
    tail = extracted[extracted.index("Sources and limits"):]
    assert "SCOPE-SENTINEL" in tail and "COVERAGE-SENTINEL" in tail
    assert extracted.rindex("Line 119") < extracted.index("Sources and limits")
    assert re.search(r"Page Number In The Footer\s+1\s*$", pages[0], re.M)
