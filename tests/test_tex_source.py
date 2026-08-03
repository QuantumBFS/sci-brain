"""Tests for skills/download-ref/helpers/tex_source.py."""
import gzip
import importlib.util
import io
import tarfile
from pathlib import Path

HELPER = Path(__file__).resolve().parents[1] / "skills" / "download-ref" / "helpers" / "tex_source.py"


def _load():
    spec = importlib.util.spec_from_file_location("tex_source", HELPER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _tar_bytes(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tf:
        for name, data in files.items():
            info = tarfile.TarInfo(name=name)
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    return buf.getvalue()


MAIN_TEX = b"\\documentclass{article}\n\\begin{document}\n\\input{sec1}\nhello\n\\end{document}\n"


def test_detect_payload_pdf():
    ts = _load()
    assert ts.detect_payload(b"%PDF-1.5 blah") == "pdf"


def test_detect_payload_gzip_and_tar():
    ts = _load()
    assert ts.detect_payload(gzip.compress(MAIN_TEX)) == "source"
    assert ts.detect_payload(_tar_bytes({"main.tex": MAIN_TEX})) == "source"


def test_detect_payload_html_error_page():
    ts = _load()
    assert ts.detect_payload(b"<!DOCTYPE html><html>withdrawn</html>") == "unknown"


def test_extract_source_gzipped_tar(tmp_path):
    ts = _load()
    data = gzip.compress(_tar_bytes({"main.tex": MAIN_TEX, "sec1.tex": b"world\n"}))
    assert ts.extract_source(data, tmp_path) is True
    assert (tmp_path / "main.tex").read_bytes() == MAIN_TEX
    assert (tmp_path / "sec1.tex").exists()


def test_extract_source_single_gzipped_tex(tmp_path):
    ts = _load()
    assert ts.extract_source(gzip.compress(MAIN_TEX), tmp_path) is True
    assert (tmp_path / "main.tex").read_bytes() == MAIN_TEX


def test_extract_source_rejects_path_traversal(tmp_path):
    ts = _load()
    evil = gzip.compress(_tar_bytes({"../evil.tex": b"x", "ok.tex": MAIN_TEX}))
    ts.extract_source(evil, tmp_path / "src")
    assert not (tmp_path / "evil.tex").exists()
    assert (tmp_path / "src" / "ok.tex").exists()


def test_extract_source_garbage_returns_false(tmp_path):
    ts = _load()
    assert ts.extract_source(b"<html>not a source</html>", tmp_path) is False


def test_find_main_tex_prefers_begin_document(tmp_path):
    ts = _load()
    (tmp_path / "style.tex").write_text("\\documentclass{article}\n")  # no \begin{document}
    (tmp_path / "paper.tex").write_text(MAIN_TEX.decode())
    (tmp_path / "sec1.tex").write_text("world\n")
    assert ts.find_main_tex(tmp_path).name == "paper.tex"


def test_find_main_tex_none(tmp_path):
    ts = _load()
    (tmp_path / "notes.txt").write_text("no tex here")
    assert ts.find_main_tex(tmp_path) is None


def test_read_tex_latin1_fallback(tmp_path):
    ts = _load()
    p = tmp_path / "a.tex"
    p.write_bytes(b"caf\xe9\n")  # invalid UTF-8, valid Latin-1
    assert "caf" in ts.read_tex(p)


def test_flatten_python_inlines_and_strips_comments(tmp_path):
    ts = _load()
    (tmp_path / "main.tex").write_text(
        "\\documentclass{article}\n% top comment\n\\begin{document}\n"
        "\\input{sec1}\n\\include{sec2}\n\\input{missing}\n\\end{document}\n")
    (tmp_path / "sec1.tex").write_text("SECTION-ONE\n% inner comment\n\\input{sub/deep}\n")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "deep.tex").write_text("DEEP\n")
    (tmp_path / "sec2.tex").write_text("SECTION-TWO\n")
    out = ts.flatten_python(tmp_path / "main.tex", tmp_path)
    assert "SECTION-ONE" in out
    assert "SECTION-TWO" in out
    assert "DEEP" in out
    assert "% top comment" not in out
    assert "% inner comment" not in out
    assert "\\input{missing}" in out  # unresolvable left verbatim


def test_flatten_python_depth_bound(tmp_path):
    ts = _load()
    (tmp_path / "main.tex").write_text("\\input{main}\n")  # self-recursive
    out = ts.flatten_python(tmp_path / "main.tex", tmp_path)  # must terminate
    assert isinstance(out, str)


def test_copy_figures(tmp_path):
    ts = _load()
    src = tmp_path / "src"
    (src / "figs").mkdir(parents=True)
    (src / "figs" / "plot.png").write_bytes(b"\x89PNG fake")
    (src / "figs" / "diag.pdf").write_bytes(b"%PDF fake")
    (src / "main.tex").write_text("x")
    (src / "refs.bib").write_text("x")
    fig_dir = tmp_path / "figures"
    n = ts.copy_figures(src, fig_dir)
    assert n == 2
    assert (fig_dir / "figs" / "plot.png").exists()
    assert (fig_dir / "figs" / "diag.pdf").exists()
    assert not (fig_dir / "refs.bib").exists()


def test_extract_source_mkdir_permission_denied(tmp_path, monkeypatch):
    ts = _load()
    # Simulate mkdir raising PermissionError by monkeypatching Path.mkdir
    original_mkdir = Path.mkdir

    def failing_mkdir(self, *args, **kwargs):
        if "src" in str(self):
            raise PermissionError("mock permission denied")
        return original_mkdir(self, *args, **kwargs)

    monkeypatch.setattr(Path, "mkdir", failing_mkdir)
    data = gzip.compress(_tar_bytes({"main.tex": MAIN_TEX}))
    assert ts.extract_source(data, tmp_path / "src") is False


def test_find_main_tex_skips_broken_symlink(tmp_path):
    ts = _load()
    # Create a valid .tex file with \documentclass
    (tmp_path / "good.tex").write_text("\\documentclass{article}\n\\begin{document}\nhello\n\\end{document}\n")
    # Create a broken symlink named .tex
    (tmp_path / "broken.tex").symlink_to("/nonexistent/path")
    # Should find good.tex and not raise on the broken symlink
    result = ts.find_main_tex(tmp_path)
    assert result is not None
    assert result.name == "good.tex"
