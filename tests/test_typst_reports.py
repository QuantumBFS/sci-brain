"""Render checks for report content that crosses page boundaries."""

import re
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.skipif(
    not shutil.which("typst") or not shutil.which("pdftotext"),
    reason="PDF toolchain not installed",
)


def test_survey_tables_paginate_with_repeated_headers_and_complete_rows(tmp_path):
    for name in ("template.typ", "template.bib"):
        shutil.copy(ROOT / "skills/survey" / name, tmp_path / name)
    source = tmp_path / "template.typ"
    with source.open("a") as stream:
        stream.write('''
#pagebreak()
#problem_table(range(45).map(i => (
  [#i], [Problem-#i],
  [Evidence-#i: the result depends on the evaluation protocol and input distribution.],
  [Evaluation team], [Critical],
)))
#pagebreak()
#compare_table(
  (([Method A], [Evidence A]), ([Method B], [Evidence B])),
  columns: (1fr, 2fr), headers: ([Method], [Evidence]),
)
#stage([Legacy stage], [Positional color remains supported], rgb("eef3ff"))
''')
    pdf = tmp_path / "report.pdf"
    compiled = subprocess.run(
        ["typst", "compile", "--ignore-system-fonts", "--input",
         "heading-font=Libertinus Serif", str(source), str(pdf)],
        capture_output=True, text=True,
    )
    assert compiled.returncode == 0, compiled.stderr
    assert "warning:" not in compiled.stderr, compiled.stderr
    extracted = subprocess.check_output(
        ["pdftotext", "-layout", str(pdf), "-"], text=True,
    )
    table_pages = [page for page in extracted.split("\f") if "Problem-" in page]
    assert len(table_pages) >= 2
    for page in table_pages:
        for header in ("Problem", "Why it matters", "Who can act", "Urgency"):
            assert header in page
    assert re.findall(r"Problem-(\d+)", extracted) == [str(i) for i in range(45)]
    assert re.findall(r"Evidence-(\d+)", extracted) == [str(i) for i in range(45)]
    for text in ("Method A", "Evidence A", "Method B", "Evidence B",
                 "Legacy stage", "Positional color remains supported"):
        assert text in extracted
