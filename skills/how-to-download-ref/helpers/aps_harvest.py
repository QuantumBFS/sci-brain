#!/usr/bin/env python3
"""Fetch APS published full text (JATS XML) via the APS Harvest API.

The APS Harvest server (https://harvest.aps.org/docs/harvest-api) serves the
*publisher's own* JATS XML — sections, MathML3 equations, structured reference
list — for every open-access APS article, with no API key and no institutional
IP. This is ground truth: no OCR, no two-column layout guessing, no formula
mangling. It strictly dominates PDF parsing whenever it returns 200.

Coverage is per-article, not per-journal. 200 is returned for gold-OA titles
(PRX, PRX Quantum, PRResearch, PRAB, PRPER), SCOAP3 titles (PRC, PRD), and any
individually CC-licensed article in an otherwise closed journal (a large and
growing share of PRL/PRA/PRB under transformative agreements). Closed articles
return 401 — that is also the cheapest possible open-access probe, since the
same request that tests access also delivers the full text.

Usage:
    aps_harvest.py --kb /abs/path/.knowledge --doi 10.1103/PhysRevLett.130.036401
    aps_harvest.py --kb /abs/path/.knowledge --all          # every 10.1103 DOI in .raw/doi/
    aps_harvest.py --kb /abs/path/.knowledge --all --bagit  # + figures & supplemental
    aps_harvest.py --check 10.1103/PhysRevB.108.045101      # probe only, no write

Writes:
    .raw/doi/<safe>.jats.xml          publisher JATS (safe = doi with / -> -)
    .raw/doi/<safe>.aps.pdf           published PDF        (--bagit only)
    .raw/doi/<safe>-suppl/            supplemental material (--bagit only)
    .figures/doi__<safe>/             figure files          (--bagit only)
"""
from __future__ import annotations

import argparse
import gzip
import html
import io
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

HARVEST = "https://harvest.aps.org/v2/journals/articles/{doi}"
UA = "sci-brain-download-ref/1.0 (+https://github.com/QuantumBFS/sci-brain)"
APS_PREFIX = "10.1103/"


def safe_name(doi: str) -> str:
    return doi.replace("/", "-")


def _get(doi: str, accept: str, timeout: int = 120) -> tuple[int, bytes]:
    req = urllib.request.Request(
        HARVEST.format(doi=doi), headers={"Accept": accept, "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception as e:  # network / DNS / timeout
        print(f"  harvest error {doi}: {e}", file=sys.stderr)
        return 0, b""


def fetch_jats(doi: str, out: Path) -> str:
    """-> ok | cached | closed | notfound | error"""
    if out.exists() and out.stat().st_size > 2048:
        return "cached"
    code, body = _get(doi, "text/xml")
    if code == 200 and body.lstrip().startswith(b"<?xml"):
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(body)
        return "ok"
    if code == 401:
        return "closed"
    if code == 404:
        return "notfound"
    return "error"


def fetch_bagit(doi: str, kb: Path, safe: str) -> str:
    """Pull the BagIt package: published PDF, figures, supplemental material."""
    code, body = _get(doi, "application/zip", timeout=600)
    if code != 200 or not body:
        return "closed" if code == 401 else "error"
    try:
        z = zipfile.ZipFile(io.BytesIO(body))
    except zipfile.BadZipFile:
        return "error"
    figdir = kb / ".figures" / f"doi__{safe}"
    suppl = kb / ".raw" / "doi" / f"{safe}-suppl"
    got = []
    for name in z.namelist():
        base = Path(name).name
        if not base:
            continue
        if base == "online.pdf":
            target = kb / ".raw" / "doi" / f"{safe}.aps.pdf"
        elif "/supplemental_files/" in name:
            target = suppl / base
        elif base.startswith("figure_"):
            # figure_f1.eps.gz -> .figures/doi__<safe>/f1.eps
            target = figdir / re.sub(r"^figure_", "", base)
        else:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        data = z.read(name)
        if target.name.endswith(".gz"):
            try:
                data = gzip.decompress(data)
                target = target.with_suffix("")
            except OSError:
                pass
        target.write_bytes(data)
        got.append(target.name)
    return f"ok ({len(got)} files)" if got else "empty"


# ---------------------------------------------------------------- markdown --

_MATH = re.compile(
    r'<math\b[^>]*?display="(?P<disp>inline|block)".*?'
    r'<annotation encoding="application/x-tex">(?P<tex>.*?)</annotation>.*?</math>',
    re.S)
_FIGURE = re.compile(
    r'<figure\b(?P<attrs>[^>]*)>(?P<inner>.*?)</figure>', re.S)
_FIG_ID = re.compile(r'id="(?P<fid>[^"]*)"')
_FIGCAPTION = re.compile(r'<figcaption>(?P<cap>.*?)</figcaption>', re.S)
_TAG = re.compile(r'<[^>]+>')


def _demath(s: str) -> str:
    """MathML -> $tex$, using APS's x-tex annotation (always present)."""
    def sub(m):
        tex = html.unescape(m.group("tex")).strip()
        return f"$${tex}$$" if m.group("disp") == "block" else f"${tex}$"
    return _MATH.sub(sub, s)


def _defigure(md: str) -> str:
    """Collapse pandoc's raw <figure> passthrough into a caption line.

    Figure *files* are only available with --bagit; without them an image link
    would dangle, so the caption text (which carries the physics) is kept and
    the <embed> dropped.
    """
    def sub(m):
        inner = m.group("inner")
        cap = _FIGCAPTION.search(inner)
        cap = _demath(cap.group("cap")) if cap else ""
        cap = html.unescape(_TAG.sub("", cap)).strip()
        cap = re.sub(r"\s+", " ", cap)
        fid = _FIG_ID.search(m.group("attrs") or "")
        num = re.sub(r"^f", "", fid.group("fid")) if fid else ""
        label = f"Figure {num}" if num else "Figure"
        return f"\n**{label}.** {cap}\n" if cap else ""
    return _FIGURE.sub(sub, md)


def jats_to_markdown(xml_path: Path) -> str:
    """pandoc JATS -> markdown with LaTeX math, then clean up passthrough HTML."""
    if not shutil.which("pandoc"):
        raise RuntimeError("pandoc not found; required for JATS rendering "
                           "(install: paru -S pandoc-cli / apt install pandoc)")
    r = subprocess.run(
        ["pandoc", "-f", "jats", "-t", "markdown+tex_math_dollars",
         "--wrap=preserve", str(xml_path)],
        capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise RuntimeError(f"pandoc failed on {xml_path.name}: {r.stderr[:300]}")
    md = _defigure(r.stdout)
    md = _demath(md)
    md = _TAG.sub("", md) if "<embed" in md else md
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip()


# -------------------------------------------------------------- references --

def _txt(el) -> str:
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip()


def extract_refs(xml_path: Path) -> list[dict]:
    """Structured reference list. APS tags every cited DOI / arXiv id."""
    root = ET.parse(xml_path).getroot()
    out = []
    for ref in root.findall(".//ref"):
        cit = ref.find("mixed-citation")
        if cit is None:
            cit = ref.find("element-citation")
        if cit is None:
            continue
        d = {"id": ref.get("id") or ""}
        lbl = ref.find("label")
        d["label"] = _txt(lbl).strip("[]") if lbl is not None else ""
        d["authors"] = [_txt(n) for n in cit.findall(".//string-name")]
        for tag, key in (("article-title", "title"), ("source", "source"),
                         ("volume", "volume"), ("page-range", "pages"),
                         ("fpage", "pages"), ("year", "year")):
            el = cit.find(tag)
            if el is not None and not d.get(key):
                d[key] = _txt(el)
        link = cit.find("ext-link")
        if link is not None:
            d["url"] = (link.get("{http://www.w3.org/1999/xlink}href")
                        or _txt(link))
        oid = cit.find("object-id")
        raw = _txt(cit)
        if oid is not None:
            raw = raw.replace(_txt(oid), "", 1).strip()
        d["raw"] = raw
        for pid in cit.findall("pub-id"):
            t = pid.get("pub-id-type")
            if t == "doi":
                d["doi"] = _txt(pid)
            elif t == "arxiv":
                d["arxiv"] = _txt(pid).replace("arXiv:", "")
        out.append(d)
    return out


def render_refs_md(refs: list[dict]) -> str:
    lines = []
    for r in refs:
        au = ", ".join(r.get("authors") or [])
        if len(r.get("authors") or []) > 4:
            au = f"{r['authors'][0]} et al."
        bits = [b for b in (au, r.get("title")) if b]
        cite = " ".join(x for x in (
            r.get("source"), r.get("volume"),
            r.get("pages"), f"({r['year']})" if r.get("year") else "") if x)
        if cite:
            bits.append(cite)
        links = []
        if r.get("doi"):
            links.append(f"[doi:{r['doi']}](https://doi.org/{r['doi']})")
        if r.get("arxiv"):
            links.append(f"[arXiv:{r['arxiv']}](https://arxiv.org/abs/{r['arxiv']})")
        if r.get("url") and not links:
            links.append(f"<{r['url']}>")
        tail = "  " + " ".join(links) if links else ""
        body = ". ".join(b.rstrip(". ") for b in bits if b.strip())
        if not body:
            # misc/unstructured citation (a bare URL, a software note, ...)
            body = r.get("raw", "").rstrip(". ")
        lines.append(f"{r.get('label') or r.get('id')}. {body}." + tail)
    return "\n".join(lines)


# --------------------------------------------------------------------- cli --

def aps_dois_in_kb(kb: Path) -> list[str]:
    doi_dir = kb / ".raw" / "doi"
    if not doi_dir.exists():
        return []
    found = []
    for j in sorted(doi_dir.glob("*.json")):
        try:
            s2 = json.loads(j.read_text())
        except Exception:
            continue
        doi = (s2.get("externalIds") or {}).get("DOI") or ""
        if doi.lower().startswith(APS_PREFIX):
            found.append(doi)
    return found


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--kb", type=Path, help="Absolute path to <stream>/.knowledge/")
    p.add_argument("--doi", action="append", default=[], help="APS DOI (repeatable)")
    p.add_argument("--all", action="store_true",
                   help="Process every 10.1103/* DOI already in .raw/doi/")
    p.add_argument("--bagit", action="store_true",
                   help="Also pull the BagIt package (published PDF, figures, supplemental)")
    p.add_argument("--check", metavar="DOI",
                   help="Probe open-access status only; print open/closed and exit")
    args = p.parse_args()

    if args.check:
        code, _ = _get(args.check, "text/xml", timeout=30)
        print({200: "open", 401: "closed", 404: "notfound"}.get(code, f"error({code})"))
        return 0 if code == 200 else 1

    if not args.kb:
        p.error("--kb is required unless --check is used")
    dois = list(args.doi)
    if args.all:
        dois += [d for d in aps_dois_in_kb(args.kb) if d not in dois]
    dois = [d for d in dois if d.lower().startswith(APS_PREFIX)]
    if not dois:
        print("no APS (10.1103/*) DOIs to process")
        return 0

    raw_doi = args.kb / ".raw" / "doi"
    n_ok = n_closed = 0
    for i, doi in enumerate(dois):
        safe = safe_name(doi)
        status = fetch_jats(doi, raw_doi / f"{safe}.jats.xml")
        extra = ""
        if status in ("ok", "cached"):
            n_ok += 1
            if args.bagit:
                extra = f" bagit={fetch_bagit(doi, args.kb, safe)}"
        elif status == "closed":
            n_closed += 1
        print(f"  {status:8s} {doi}{extra}")
        if status not in ("cached",) and i < len(dois) - 1:
            time.sleep(1)
    print(f"\njats: {n_ok} open, {n_closed} closed (closed -> arXiv/PDF tiers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
