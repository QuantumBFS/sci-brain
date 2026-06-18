#!/usr/bin/env python3
"""Normalize a figure input to a viewable PNG for `figure-taste`.

Given one figure path, emit raster image path(s) the caller can read with an
image-reading tool, printing each produced/passthrough path to stdout (one
per line). The goal is "always end up with something you can look at" — never
score a figure you have not seen.

Per input type:
  - raster (.png/.jpg/.jpeg/.gif/.bmp/.webp) and .pdf  -> passthrough (printed
    as-is; image/PDF readers handle these directly).
  - .typ  -> compiled to PNG via `typst compile ... --ppi <dpi>`.
  - .svg  -> converted to PNG via the first available of
             rsvg-convert / inkscape / cairosvg.
  - .py   -> treated as a matplotlib script; rendered ONLY with --allow-exec,
             which runs it under the Agg backend and saves every open figure.
             Without --allow-exec it refuses (arbitrary code execution).

On failure it writes a clear reason to stderr and exits non-zero, so the
caller knows to ask the user to export a PNG instead of scoring blind.

CLI:
    python3 render.py FIGURE [--dpi 200] [--allow-exec] [--outdir DIR]
        --dpi      raster resolution for typst/svg/py rendering (default 200).
        --allow-exec  permit executing a matplotlib .py (off by default).
        --outdir   where to write rendered PNGs (default: alongside a temp dir
                   next to the input). Passthrough inputs ignore this.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Optional

RASTER_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
PASSTHROUGH_EXTS = RASTER_EXTS | {".pdf"}


def _fail(msg: str) -> int:
    print(f"render.py: {msg}", file=sys.stderr)
    print(
        "render.py: could not produce a viewable raster — "
        "ask the user to export a PNG.",
        file=sys.stderr,
    )
    return 1


def _outdir(fig: Path, outdir: Optional[Path]) -> Path:
    if outdir is not None:
        outdir.mkdir(parents=True, exist_ok=True)
        return outdir
    d = Path(tempfile.mkdtemp(prefix=f"figtaste_{fig.stem}_"))
    return d


def _render_typst(fig: Path, dpi: int, out: Path) -> List[Path]:
    if shutil.which("typst") is None:
        raise RuntimeError("typst not found on PATH")
    # `{p}` expands to the page number, so multi-page docs do not error.
    template = out / f"{fig.stem}_{{p}}.png"
    subprocess.run(
        ["typst", "compile", "--ppi", str(dpi), str(fig), str(template)],
        check=True,
        capture_output=True,
        text=True,
    )
    produced = sorted(out.glob(f"{fig.stem}_*.png"))
    if not produced:
        raise RuntimeError("typst produced no PNG output")
    return produced


def _render_svg(fig: Path, dpi: int, out: Path) -> List[Path]:
    target = out / f"{fig.stem}.png"
    if shutil.which("rsvg-convert"):
        cmd = ["rsvg-convert", "--dpi-x", str(dpi), "--dpi-y", str(dpi),
               "-o", str(target), str(fig)]
    elif shutil.which("inkscape"):
        cmd = ["inkscape", str(fig), "--export-type=png",
               f"--export-filename={target}", f"--export-dpi={dpi}"]
    elif shutil.which("cairosvg"):
        cmd = ["cairosvg", str(fig), "-o", str(target), "-d", str(dpi)]
    else:
        raise RuntimeError(
            "no SVG renderer found (need rsvg-convert, inkscape, or cairosvg)"
        )
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    if not target.exists():
        raise RuntimeError("SVG conversion produced no PNG output")
    return [target]


# Runs the user's matplotlib script under Agg and saves every open figure.
_MPL_WRAPPER = r"""
import sys, runpy
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
user_file, out_prefix, dpi = sys.argv[1], sys.argv[2], int(sys.argv[3])
runpy.run_path(user_file, run_name="__main__")
nums = plt.get_fignums()
if not nums:
    sys.stderr.write("no matplotlib figures were open after running the script\n")
    sys.exit(3)
for i, n in enumerate(nums):
    p = f"{out_prefix}_{i}.png"
    plt.figure(n).savefig(p, dpi=dpi, bbox_inches="tight")
    print(p)
"""


def _render_py(fig: Path, dpi: int, out: Path, allow_exec: bool) -> List[Path]:
    if not allow_exec:
        raise RuntimeError(
            "refusing to execute a .py figure script without --allow-exec "
            "(confirm with the user first, or supply a rendered PNG)"
        )
    out_prefix = out / fig.stem
    proc = subprocess.run(
        [sys.executable, "-c", _MPL_WRAPPER, str(fig), str(out_prefix), str(dpi)],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            "matplotlib render failed: "
            + (proc.stderr.strip() or f"exit {proc.returncode}")
        )
    produced = [Path(line) for line in proc.stdout.splitlines() if line.strip()]
    produced = [p for p in produced if p.exists()]
    if not produced:
        raise RuntimeError("matplotlib render produced no PNG output")
    return produced


def render(fig: Path, dpi: int, allow_exec: bool,
           outdir: Optional[Path]) -> List[Path]:
    ext = fig.suffix.lower()
    if ext in PASSTHROUGH_EXTS:
        return [fig]  # image/PDF readers handle these directly
    out = _outdir(fig, outdir)
    if ext == ".typ":
        return _render_typst(fig, dpi, out)
    if ext == ".svg":
        return _render_svg(fig, dpi, out)
    if ext == ".py":
        return _render_py(fig, dpi, out, allow_exec)
    raise RuntimeError(f"unsupported figure type {ext!r} (export a PNG instead)")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("figure", type=Path, help="path to the figure to render")
    parser.add_argument("--dpi", type=int, default=200,
                        help="raster resolution for typst/svg/py (default 200)")
    parser.add_argument("--allow-exec", action="store_true",
                        help="permit executing a matplotlib .py script")
    parser.add_argument("--outdir", type=Path, default=None,
                        help="directory for rendered PNGs (default: a temp dir)")
    args = parser.parse_args(argv)

    fig = args.figure
    if not fig.exists():
        return _fail(f"no such file: {fig}")
    try:
        produced = render(fig, args.dpi, args.allow_exec, args.outdir)
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        detail = exc.stderr.strip() if isinstance(exc, subprocess.CalledProcessError) and exc.stderr else str(exc)
        return _fail(detail)
    for p in produced:
        print(str(p))
    return 0


if __name__ == "__main__":
    sys.exit(main())
