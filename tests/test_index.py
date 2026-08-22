"""Tests for skills/download-ref/helpers/index.py."""
import importlib.util
import sys
from pathlib import Path


HELPER = Path(__file__).resolve().parents[1] / "skills" / "download-ref" / "helpers" / "index.py"


def _load():
    spec = importlib.util.spec_from_file_location("index_helper", HELPER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_generated_index_uses_actual_kb_dirname(tmp_path, monkeypatch):
    kb = tmp_path / "proj" / "kb"
    kb.mkdir(parents=True)
    (kb / "paper.md").write_text("""---
type: arxiv
title: Test Paper
authors: Example Author
year: 2026
full_text: yes
---

body
""")
    monkeypatch.setattr(sys, "argv", ["index.py", "--kb", str(kb), "--title", "test refs"])
    mod = _load()

    assert mod.main() == 0

    text = (kb / "INDEX.md").read_text()
    assert "kb/" in text
    assert ".knowledge/" not in text


def test_index_counts_latex_as_full_text(tmp_path, monkeypatch):
    kb = tmp_path / "kb"
    kb.mkdir(parents=True)
    (kb / "paper.md").write_text("""---
type: arxiv
title: Tex Paper
authors: Example Author
year: 2026
full_text: latex
---

body
""")
    monkeypatch.setattr(sys, "argv", ["index.py", "--kb", str(kb), "--title", "test refs"])
    _load().main()
    index = (kb / "INDEX.md").read_text()
    row = next(line for line in index.splitlines() if "Tex Paper" in line)
    assert "✅" in row
