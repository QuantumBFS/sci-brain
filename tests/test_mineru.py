"""mineru_parse.py caching and render.py --mineru body selection (offline)."""
import importlib.util
import io
import json
import sys
import zipfile
from pathlib import Path

HELPERS = Path(__file__).resolve().parents[1] / "skills" / "how-to-download-ref" / "helpers"


def _load(name):
    sys.path.insert(0, str(HELPERS))
    spec = importlib.util.spec_from_file_location(f"{name}_helper", HELPERS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


S2 = {"title": "Test Paper", "authors": [{"name": "A. Author"}], "year": 2026,
      "venue": "TestConf", "abstract": "An abstract.", "externalIds": {}}
BODY = "MINERU-BODY-MARKER with $x^2$ inline math. " + "x" * 100


def _kb(tmp_path):
    kb = tmp_path / "kb"
    (kb / ".raw" / "arxiv").mkdir(parents=True)
    (kb / ".raw" / "arxiv" / "2401.00001.json").write_text(json.dumps(S2))
    return kb


def test_mineru_body_with_flag(tmp_path):
    mod = _load("render")
    kb = _kb(tmp_path)
    (kb / ".raw" / "arxiv" / "2401.00001.mineru.md").write_text(BODY)
    assert mod.render_arxiv(kb, kb / ".raw", use_mineru=True) == 1
    md = (kb / "2401.00001_test-paper.md").read_text()
    assert "full_text: mineru" in md
    assert "## Full Text (MinerU)" in md
    assert "MINERU-BODY-MARKER" in md


def test_mineru_ignored_without_flag(tmp_path):
    mod = _load("render")
    kb = _kb(tmp_path)
    (kb / ".raw" / "arxiv" / "2401.00001.mineru.md").write_text(BODY)
    mod.render_arxiv(kb, kb / ".raw")
    md = (kb / "2401.00001_test-paper.md").read_text()
    assert "full_text: no" in md
    assert "MINERU-BODY-MARKER" not in md


def test_tex_beats_mineru(tmp_path):
    mod = _load("render")
    kb = _kb(tmp_path)
    (kb / ".raw" / "arxiv" / "2401.00001.mineru.md").write_text(BODY)
    (kb / ".raw" / "arxiv" / "2401.00001.tex").write_text("TEX-BODY-MARKER " + "x" * 100)
    mod.render_arxiv(kb, kb / ".raw", use_tex=True, use_mineru=True)
    md = (kb / "2401.00001_test-paper.md").read_text()
    assert "full_text: latex" in md
    assert "MINERU-BODY-MARKER" not in md


def test_postprocess_relinks_images_and_fixes_ff():
    mod = _load("mineru_parse")
    md, used = mod.postprocess(
        "The efect is Efective, a cutoff, an of-diagonal term.\n"
        "![](images/a.jpg)\n<td><img src=\"images/b.jpg\"></td>\n", ".figures/arxiv__x")
    assert "The effect is Effective, a cutoff, an off-diagonal term." in md
    assert "![](.figures/arxiv__x/a.jpg)" in md
    assert 'src=".figures/arxiv__x/b.jpg"' in md
    assert used == {"a.jpg", "b.jpg"}


def test_save_result_copies_only_linked_images(tmp_path):
    mod = _load("mineru_parse")
    kb = _kb(tmp_path)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("full.md", "Fig. ![](images/fig.jpg)\n")
        z.writestr("images/fig.jpg", b"JPEG")
        z.writestr("images/equation-crop.jpg", b"JPEG")
    assert mod.save_result(kb, "arxiv", "2401.00001", buf.getvalue()) == 1
    assert (kb / ".raw" / "arxiv" / "2401.00001.mineru.md").read_text() == \
        "Fig. ![](.figures/arxiv__2401.00001/fig.jpg)\n"
    assert sorted(p.name for p in (kb / ".figures" / "arxiv__2401.00001").iterdir()) == ["fig.jpg"]


def test_discover_skips_cached_and_maps_old_style_ids(tmp_path):
    mod = _load("mineru_parse")
    kb = _kb(tmp_path)
    raw = kb / ".raw" / "arxiv"
    (raw / "2401.00001.pdf").write_bytes(b"%PDF-")
    (raw / "hep-th-9901001.json").write_text(json.dumps(S2))
    (raw / "hep-th-9901001.pdf").write_bytes(b"%PDF-")
    todo = mod.discover(kb, set(), force=False)
    assert [(k, s, i) for k, s, i, _ in todo] == [
        ("arxiv", "2401.00001", "2401.00001"), ("arxiv", "hep-th-9901001", "hep-th/9901001")]
    (raw / "2401.00001.mineru.md").write_text(BODY)
    assert [s for _, s, _, _ in mod.discover(kb, set(), force=False)] == ["hep-th-9901001"]
    assert len(mod.discover(kb, set(), force=True)) == 2
