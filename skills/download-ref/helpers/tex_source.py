#!/usr/bin/env python3
"""Fetch and flatten arXiv e-print LaTeX sources for a knowledge base.

Used by fetch_metadata.py (--download-arxiv-source). Downloads
https://arxiv.org/e-print/<id>, detects the payload (tar / gzip / PDF-only),
extracts to .raw/arxiv/<id>-src/, finds the main .tex, and flattens
\\input/\\include into .raw/arxiv/<id>.tex. Figure files from the source
tree are copied into .figures/arxiv__<id>/.

Flattening uses latexpand when on PATH, else a small built-in inliner.
Stdlib-only; failures degrade to the PDF render path (see SKILL.md Step 5).
"""
from __future__ import annotations

import gzip
import io
import re
import shutil
import subprocess
import tarfile
import urllib.request
from pathlib import Path

FIG_EXTS = {".png", ".jpg", ".jpeg", ".pdf"}
COMMENT_LINE = re.compile(r"^\s*%")
INPUT_CMD = re.compile(r"\\(?:input|include)\{([^}]+)\}")


def detect_payload(data: bytes) -> str:
    """Classify an e-print response: 'pdf', 'source', or 'unknown'.

    HTML error pages (withdrawn papers) land in 'unknown'.
    """
    if data[:5] == b"%PDF-":
        return "pdf"
    if data[:2] == b"\x1f\x8b":
        return "source"
    if len(data) > 262 and data[257:262] == b"ustar":
        return "source"
    return "unknown"


def _safe_members(tf: tarfile.TarFile, src_dir: Path):
    base = src_dir.resolve()
    for m in tf.getmembers():
        if not (m.isreg() or m.isdir()):
            continue
        dest = (src_dir / m.name).resolve()
        if dest == base or base in dest.parents:
            yield m


def extract_source(data: bytes, src_dir: Path) -> bool:
    """Extract an e-print payload (gzip, gzipped tar, or plain tar) into src_dir."""
    if data[:2] == b"\x1f\x8b":
        try:
            data = gzip.decompress(data)
        except OSError:
            return False
    try:
        src_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        return False
    try:
        with tarfile.open(fileobj=io.BytesIO(data)) as tf:
            members = list(_safe_members(tf, src_dir))
            try:
                tf.extractall(src_dir, members=members, filter="data")
            except TypeError:  # Python < 3.12: no filter kwarg
                tf.extractall(src_dir, members=members)
        return True
    except (tarfile.TarError, OSError):
        pass
    # Single-file source: a bare .tex document.
    text = data.decode("utf-8", errors="replace")
    if "\\documentclass" not in text and "\\begin{document}" not in text:
        return False
    try:
        (src_dir / "main.tex").write_bytes(data)
        return True
    except OSError:
        return False


def read_tex(path: Path) -> str:
    data = path.read_bytes()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1")


def find_main_tex(src_dir: Path) -> Path | None:
    """The .tex containing \\documentclass; prefer one that also has \\begin{document}."""
    cands = []
    for p in sorted(src_dir.rglob("*.tex")):
        try:
            if "\\documentclass" in read_tex(p):
                cands.append(p)
        except (OSError, UnicodeDecodeError):
            continue
    if not cands:
        return None
    with_begin = []
    for p in cands:
        try:
            if "\\begin{document}" in read_tex(p):
                with_begin.append(p)
        except (OSError, UnicodeDecodeError):
            continue
    return (with_begin or cands)[0]


def flatten_python(main: Path, src_dir: Path, depth: int = 0, max_depth: int = 10) -> str:
    """Inline \\input/\\include relative to src_dir; strip full-line comments.

    Unresolvable references are left verbatim; recursion is depth-bounded.
    """
    if depth > max_depth:
        return read_tex(main)
    out_lines = []
    for line in read_tex(main).splitlines():
        if COMMENT_LINE.match(line):
            continue

        def repl(m: re.Match) -> str:
            name = m.group(1)
            for cand in (src_dir / name, src_dir / f"{name}.tex"):
                if cand.is_file() and cand.resolve() != main.resolve():
                    return flatten_python(cand, src_dir, depth + 1, max_depth)
            return m.group(0)

        out_lines.append(INPUT_CMD.sub(repl, line))
    return "\n".join(out_lines)


def flatten(main: Path, src_dir: Path) -> str:
    """latexpand when available, else the built-in inliner."""
    exe = shutil.which("latexpand")
    if exe:
        try:
            r = subprocess.run(
                [exe, str(main.relative_to(src_dir))],
                cwd=src_dir, capture_output=True, text=True,
                errors="replace", timeout=120,
            )
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout
        except Exception:
            pass
    return flatten_python(main, src_dir)


def copy_figures(src_dir: Path, fig_dir: Path) -> int:
    """Copy raster/PDF figure files, preserving relative paths. Returns count."""
    n = 0
    for p in sorted(src_dir.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in FIG_EXTS:
            continue
        dest = fig_dir / p.relative_to(src_dir)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest)
        n += 1
    return n


def fetch_arxiv_source(arxiv_id: str, kb: Path, ua: str = "Mozilla/5.0") -> str:
    """Fetch + flatten one paper's e-print source.

    Returns 'ok', 'cached', 'pdf-only' (PDF-only submission), or 'miss'.
    On anything but 'ok'/'cached' the caller's PDF path stays in charge.
    """
    raw_dir = kb / ".raw" / "arxiv"
    out_tex = raw_dir / f"{arxiv_id}.tex"
    if out_tex.exists() and out_tex.stat().st_size > 100:
        return "cached"
    try:
        req = urllib.request.Request(
            f"https://arxiv.org/e-print/{arxiv_id}",
            headers={"User-Agent": ua})
        with urllib.request.urlopen(req, timeout=120) as r:
            data = r.read()
        kind = detect_payload(data)
        if kind == "pdf":
            return "pdf-only"
        if kind != "source":
            return "miss"
        src_dir = raw_dir / f"{arxiv_id}-src"
        if not extract_source(data, src_dir):
            return "miss"
        main = find_main_tex(src_dir)
        if main is None:
            return "miss"
        tex = flatten(main, src_dir)
        if not tex.strip():
            return "miss"
        raw_dir.mkdir(parents=True, exist_ok=True)
        out_tex.write_text(tex, encoding="utf-8")
        copy_figures(src_dir, kb / ".figures" / f"arxiv__{arxiv_id}")
        return "ok"
    except Exception:
        return "miss"
