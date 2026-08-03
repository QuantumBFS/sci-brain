"""render.py: arXiv entries with .raw/arxiv/<id>.tex get a LaTeX body."""
import importlib.util
import json
import sys
from pathlib import Path

HELPER = Path(__file__).resolve().parents[1] / "skills" / "download-ref" / "helpers" / "render.py"


def _load():
    spec = importlib.util.spec_from_file_location("render_helper", HELPER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


S2 = {"title": "Test Paper", "authors": [{"name": "A. Author"}], "year": 2026,
      "venue": "TestConf", "abstract": "An abstract.", "externalIds": {}}


def _kb(tmp_path):
    kb = tmp_path / "kb"
    (kb / ".raw" / "arxiv").mkdir(parents=True)
    (kb / ".raw" / "arxiv" / "2401.00001.json").write_text(json.dumps(S2))
    return kb


def test_tex_body_wins_over_pdf(tmp_path):
    mod = _load()
    kb = _kb(tmp_path)
    (kb / ".raw" / "arxiv" / "2401.00001.tex").write_text(
        "\\documentclass{article}\n\\begin{document}\nTEX-BODY-MARKER\n\\end{document}\n" + "x" * 100)
    n = mod.render_arxiv(kb, kb / ".raw")
    assert n == 1
    md = (kb / "2401.00001_test-paper.md").read_text()
    assert "full_text: latex" in md
    assert "TEX-BODY-MARKER" in md
    assert "## Full Text (LaTeX source)" in md


def test_no_tex_no_pdf_stays_abstract_only(tmp_path):
    mod = _load()
    kb = _kb(tmp_path)
    mod.render_arxiv(kb, kb / ".raw")
    md = (kb / "2401.00001_test-paper.md").read_text()
    assert "full_text: no" in md
