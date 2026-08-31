"""render.py: arXiv entries with .raw/arxiv/<id>.tex get a LaTeX body (with --tex-source)."""
import importlib.util
import json
import sys
from pathlib import Path

HELPER = Path(__file__).resolve().parents[1] / "skills" / "how-to-download-ref" / "helpers" / "render.py"


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
    n = mod.render_arxiv(kb, kb / ".raw", use_tex=True)
    assert n == 1
    md = (kb / "2401.00001_test-paper.md").read_text()
    assert "full_text: latex" in md
    assert "TEX-BODY-MARKER" in md
    assert "## Full Text (LaTeX source)" in md


def test_tex_ignored_without_flag_pdf_default(tmp_path):
    """Without --tex-source, a present .tex must NOT change the body (PDF default)."""
    mod = _load()
    kb = _kb(tmp_path)
    (kb / ".raw" / "arxiv" / "2401.00001.tex").write_text(
        "\\documentclass{article}\n\\begin{document}\nTEX-BODY-MARKER\n\\end{document}\n" + "x" * 100)
    n = mod.render_arxiv(kb, kb / ".raw")  # no use_tex
    assert n == 1
    md = (kb / "2401.00001_test-paper.md").read_text()
    assert "full_text: no" in md  # no PDF present either -> abstract-only
    assert "TEX-BODY-MARKER" not in md
    assert "## Full Text (LaTeX source)" not in md


def test_no_tex_no_pdf_stays_abstract_only(tmp_path):
    mod = _load()
    kb = _kb(tmp_path)
    mod.render_arxiv(kb, kb / ".raw")
    md = (kb / "2401.00001_test-paper.md").read_text()
    assert "full_text: no" in md


DOI_S2 = {"title": "Doi Paper", "authors": [{"name": "B. Author"}], "year": 2026,
          "venue": "J. Test", "abstract": "An abstract.",
          "externalIds": {"DOI": "10.1000/xyz", "ArXiv": "2401.00001"}}


def test_doi_tex_body(tmp_path):
    mod = _load()
    kb = tmp_path / "kb"
    (kb / ".raw" / "doi").mkdir(parents=True)
    (kb / ".raw" / "doi" / "10.1000-xyz.json").write_text(json.dumps(DOI_S2))
    (kb / ".raw" / "doi" / "10.1000-xyz.tex").write_text(
        "\\documentclass{article}\n\\begin{document}\nDOI-TEX-MARKER\n\\end{document}\n" + "x" * 100)
    n = mod.render_doi(kb, kb / ".raw", use_tex=True)
    assert n == 1
    md = (kb / "10-1000-xyz.md").read_text()
    assert "full_text: latex" in md
    assert "DOI-TEX-MARKER" in md
    assert "## Full Text (LaTeX source)" in md


def test_doi_no_tex_no_pdf_stays_abstract_only(tmp_path):
    mod = _load()
    kb = tmp_path / "kb"
    (kb / ".raw" / "doi").mkdir(parents=True)
    (kb / ".raw" / "doi" / "10.1000-xyz.json").write_text(json.dumps(DOI_S2))
    mod.render_doi(kb, kb / ".raw")
    md = (kb / "10-1000-xyz.md").read_text()
    assert "full_text: no" in md
    assert "abstract-only entry" in md
