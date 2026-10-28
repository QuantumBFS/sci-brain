#!/usr/bin/env python3
"""Parse KB PDFs with MinerU's v1 parse API into cached markdown bodies.

For every .raw/{arxiv,doi}/<id>.pdf that sits beside its <id>.json, writes
.raw/<kind>/<id>.mineru.md and copies the images that markdown links into
.figures/<kind>__<id>/. ``render.py --mineru`` then uses the cache as the body
(``full_text: mineru``). MinerU emits display and inline math as LaTeX, tables
as HTML, and keeps the reading order of two-column layouts, which the default
pymupdf4llm path flattens.

arXiv papers are submitted as https://arxiv.org/pdf/<id> URL sources, so the
service fetches them itself and nothing is uploaded. DOI PDFs must be uploaded,
which is slow far from the service. All files go into batched jobs that the
service parses in parallel.

Service: the remote https://mineru.net/api by default, so no local GPU or
models are needed; anonymous access works and MINERU_API_KEY raises the quota.
MINERU_API_URL or --api-url points at a self-hosted ``mineru-api`` instead,
which reads local paths directly when it allows that.

Stdlib-only.

Usage:
    mineru_parse.py --kb /abs/path/.knowledge
    mineru_parse.py --kb ... --only 1106.3375 --force
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

DEFAULT_API_URL = "https://mineru.net/api"
TERMINAL = {"completed", "partial", "failed", "canceled"}
IMAGE_LINK = re.compile(r"""(\]\(|src=["'])images/([^)"'\s]+)""")
# MinerU drops the U+FB00 "ff" ligature glyph ("efect"); fi/fl survive.
FF_STEMS = ("effect", "effici", "effort", "differ", "diffus", "diffract", "suffic",
            "suffer", "coeffic", "affect", "offer", "offset", "off-diag", "cutoff",
            "tradeoff", "stiffness")
FF_FIXES = [(re.compile(r"\b" + re.escape(s.replace("ff", "f", 1)) + r"(?!f)", re.I), s)
            for s in FF_STEMS]


class APIError(RuntimeError):
    pass


class Client:
    def __init__(self, api_url: str, api_key: str | None):
        self.base = api_url.rstrip("/")
        self.key = api_key
        host = urllib.parse.urlparse(self.base).hostname or ""
        self.local = host in ("localhost", "127.0.0.1", "::1")
        self._sources: set[str] | None = None

    def _headers(self, extra: dict | None = None) -> dict:
        h = {"User-Agent": "sci-brain/mineru_parse"}
        if self.key:
            h["Authorization"] = f"Bearer {self.key}"
        h.update(extra or {})
        return h

    def request(self, method: str, path: str, body: dict | None = None, timeout: int = 60) -> dict:
        data = json.dumps(body).encode() if body is not None else None
        headers = self._headers({"Content-Type": "application/json"} if data else None)
        req = urllib.request.Request(self.base + path, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read() or b"{}")
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:500]
            raise APIError(f"{method} {path}: HTTP {e.code} {detail}") from None

    def download(self, file_id: str) -> bytes:
        req = urllib.request.Request(f"{self.base}/v1/files/{file_id}/content", headers=self._headers())
        with urllib.request.urlopen(req, timeout=300) as r:
            return r.read()

    def sources(self) -> set[str]:
        if self._sources is None:
            health = self.request("GET", "/v1/health")
            self._sources = set((health.get("features") or {}).get("sources") or [])
        return self._sources

    def upload(self, pdf: Path) -> str:
        data = pdf.read_bytes()
        resp = self.request("POST", "/v1/uploads", {
            "filename": pdf.name, "bytes": len(data), "mime_type": "application/pdf",
            "purpose": "parse", "sha256sum": hashlib.sha256(data).hexdigest()})
        if resp.get("status") == "completed":
            return resp["file"]["id"]
        url = resp["upload_url"]
        if url.startswith("/"):
            url = self.base + url
        headers = dict(resp.get("upload_headers") or {})
        same_origin = urllib.parse.urlparse(url)[:2] == urllib.parse.urlparse(self.base)[:2]
        if same_origin and self.key:
            # Presigned storage URLs carry their own auth; never leak the key there.
            headers["Authorization"] = f"Bearer {self.key}"
        req = urllib.request.Request(url, data=data, method="PUT", headers=headers)
        # Upstream bandwidth to the service can be a few tens of KB/s.
        with urllib.request.urlopen(req, timeout=max(120, len(data) // 20_000)):
            pass
        return self.request("POST", f"/v1/uploads/{resp['id']}/complete")["file"]["id"]

    def source_for(self, kind: str, ident: str, pdf: Path) -> dict:
        if self.local and "local" in self.sources():
            return {"type": "local", "path": str(pdf.resolve())}
        if kind == "arxiv" and "url" in self.sources():
            return {"type": "url", "url": f"https://arxiv.org/pdf/{ident}"}
        return {"type": "file_id", "file_id": self.upload(pdf)}


def postprocess(md: str, fig_rel: str) -> tuple[str, set[str]]:
    """Repoint image links at fig_rel/ and repair lost ff ligatures.

    Returns the markdown and the set of image names it references.
    """
    used: set[str] = set()

    def relink(m: re.Match) -> str:
        used.add(m[2])
        return f"{m[1]}{fig_rel}/{m[2]}"

    md = IMAGE_LINK.sub(relink, md)
    for pat, word in FF_FIXES:
        md = pat.sub(lambda m, w=word: w[0].upper() + w[1:] if m[0][0].isupper() else w, md)
    return md.strip() + "\n", used


def save_result(kb: Path, kind: str, stem: str, blob: bytes) -> int:
    fig_sub = f"{kind}__{stem}"
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        md, used = postprocess(z.read("full.md").decode("utf-8", errors="replace"), f".figures/{fig_sub}")
        if used:
            fig_dir = kb / ".figures" / fig_sub
            fig_dir.mkdir(parents=True, exist_ok=True)
            for name in used:
                try:
                    (fig_dir / name).write_bytes(z.read(f"images/{name}"))
                except KeyError:
                    print(f"  {kind}:{stem}: image {name} missing from result", file=sys.stderr)
    (kb / ".raw" / kind / f"{stem}.mineru.md").write_text(md)
    return len(used)


def discover(kb: Path, only: set[str], force: bool) -> list[tuple[str, str, str, Path]]:
    """Return (kind, stem, ident, pdf) for every PDF that needs parsing."""
    todo = []
    for kind in ("arxiv", "doi"):
        for json_path in sorted((kb / ".raw" / kind).glob("*.json")):
            stem = json_path.stem
            pdf = json_path.with_suffix(".pdf")
            if not pdf.exists() or (only and stem not in only):
                continue
            if not force and json_path.with_suffix(".mineru.md").exists():
                continue
            ident = stem
            if kind == "arxiv":
                meta = json.loads(json_path.read_text())
                ident = (meta.get("externalIds") or {}).get("ArXiv") or stem
                if "-" in ident and "/" not in ident:
                    ident = "/".join(ident.rsplit("-", 1))
            todo.append((kind, stem, ident, pdf))
    return todo


def run_batch(client: Client, kb: Path, batch: list, tier: str | None, timeout: int) -> int:
    files, entries = [], []
    for kind, stem, ident, pdf in batch:
        try:
            files.append({"source": client.source_for(kind, ident, pdf)})
            entries.append((kind, stem))
        except (OSError, APIError, KeyError) as e:
            print(f"FAIL {kind}:{stem}: upload: {e}")
    if not files:
        return len(batch)
    body = {"files": files, "output_formats": ["zip"]}
    if tier:
        body["tier"] = tier
    job = client.request("POST", "/v1/parse/jobs", body, timeout=120)
    deadline = time.time() + timeout
    while job.get("status") not in TERMINAL:
        if time.time() > deadline:
            raise APIError(f"job {job.get('job_id')} still {job.get('status')} after {timeout}s")
        time.sleep(3)
        job = client.request("GET", f"/v1/parse/jobs/{job['job_id']}")
    failures = len(batch) - len(files)
    for (kind, stem), result in zip(entries, job.get("files") or []):
        zip_ref = (result.get("output_files") or {}).get("zip") or {}
        if result.get("status") != "completed" or not zip_ref.get("file_id"):
            failures += 1
            print(f"FAIL {kind}:{stem}: {result.get('status')} {result.get('error') or ''}".rstrip())
            continue
        try:
            n_figs = save_result(kb, kind, stem, client.download(zip_ref["file_id"]))
            parse = result.get("parse") or {}
            print(f"ok   {kind}:{stem} ({result.get('page_range', '?')} pages, "
                  f"{parse.get('model_used', '?')}, {n_figs} figs)")
        except (OSError, KeyError, zipfile.BadZipFile, urllib.error.URLError) as e:
            failures += 1
            print(f"FAIL {kind}:{stem}: download: {e}")
    return failures


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--kb", required=True, type=Path)
    p.add_argument("--only", action="append", default=[],
                   help="Parse only this .raw stem (e.g. 1106.3375); repeatable")
    p.add_argument("--force", action="store_true", help="Re-parse PDFs that already have a .mineru.md")
    p.add_argument("--tier", choices=("flash", "basic", "standard"),
                   help="Parse tier (default: server decides; mineru.net picks its VLM model)")
    p.add_argument("--api-url", default=os.environ.get("MINERU_API_URL") or DEFAULT_API_URL)
    p.add_argument("--batch", type=int, default=20, help="Files per parse job (service max 200)")
    p.add_argument("--timeout", type=int, default=1800, help="Seconds to wait for each job")
    args = p.parse_args()

    todo = discover(args.kb, set(args.only), args.force)
    if not todo:
        print("nothing to parse (every PDF already has a .mineru.md; use --force to redo)")
        return 0
    client = Client(args.api_url, os.environ.get("MINERU_API_KEY"))
    print(f"parsing {len(todo)} PDF(s) via {client.base}")
    failures = 0
    for i in range(0, len(todo), args.batch):
        batch = todo[i:i + args.batch]
        try:
            failures += run_batch(client, args.kb, batch, args.tier, args.timeout)
        except (APIError, urllib.error.URLError, TimeoutError) as e:
            failures += len(batch)
            print(f"FAIL batch of {len(batch)}: {e}")
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
