#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "playwright",
#     "tomli; python_version < '3.11'",
# ]
# ///
"""Browser-based Sci-Hub fallback for paywalled PDFs.

Replaces the old `sci-hub-server` MCP. A real (headless) browser is required
because the mirrors serve their PDFs from behind a DDoS-Guard JavaScript
challenge that plain HTTP clients (curl / urllib) cannot solve.

For each DOI it tries every mirror in `scihub_domains.toml` (in order) until one
yields a PDF:
  1. GET https://<mirror>/<doi>  and read the <meta name="citation_pdf_url">.
     (Absent  -> that mirror does not have the paper; try the next one.)
  2. Navigate the browser to the PDF URL so DDoS-Guard's JS challenge runs and
     sets the clearance cookie in the browser context.
  3. Re-fetch the PDF URL through the same context (cookies shared) and save the
     bytes if they start with %PDF-.

Saves to  $KB/.raw/doi/<safe>.pdf   (safe = DOI with '/' -> '-'), the same place
fetch_metadata.py writes DOI blobs, so render.py picks the PDF up automatically.

Usage:
  python3 scihub_download.py --kb /abs/kb --doi 10.1111/j.1467-9280.2006.01693.x
  python3 scihub_download.py --kb /abs/kb --doi 10.x/a --doi 10.y/b
  python3 scihub_download.py --kb /abs/kb --dois-file misses.txt   # one DOI per line

Always exits 0; prints one OK / MISS / SKIP line per DOI. Requires Playwright
(see the skill preflight): pip install playwright && python3 -m playwright install chromium
"""
import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
MIN_PDF_BYTES = 20_000


def load_domains():
    """Read the ordered domain list from scihub_domains.toml.

    Uses tomllib (Python >= 3.11) when available, else falls back to a tiny
    regex so the helper has no hard third-party TOML dependency.
    """
    path = HERE / "scihub_domains.toml"
    text = path.read_text(encoding="utf-8")
    try:
        import tomllib  # Python >= 3.11
        return tomllib.loads(text).get("domains", [])
    except ModuleNotFoundError:
        pass
    try:
        import tomli  # type: ignore
        return tomli.loads(text).get("domains", [])
    except ModuleNotFoundError:
        pass
    # Minimal fallback: pull quoted strings out of the `domains = [ ... ]` array.
    m = re.search(r"domains\s*=\s*\[(.*?)\]", text, re.S)
    if not m:
        return []
    return re.findall(r'"([^"]+)"', m.group(1))


def is_pdf(buf):
    return bool(buf) and len(buf) > MIN_PDF_BYTES and buf[:5] == b"%PDF-"


def fetch_one(page, ctx, doi, domains, timeout_ms):
    """Try each mirror for one DOI. Return PDF bytes or None."""
    for dom in domains:
        base = f"https://{dom}"
        try:
            page.goto(f"{base}/{doi}", wait_until="domcontentloaded", timeout=timeout_ms)
            page.wait_for_timeout(2500)
        except Exception:
            continue  # mirror unreachable / blocked — next domain
        el = page.query_selector('meta[name="citation_pdf_url"]')
        pdf_path = el.get_attribute("content") if el else None
        if not pdf_path:
            continue  # paper not on this mirror
        if pdf_path.startswith("http"):
            pdf_url = pdf_path
        elif pdf_path.startswith("//"):
            pdf_url = "https:" + pdf_path
        else:
            pdf_url = base + pdf_path

        def try_get():
            try:
                r = ctx.request.get(
                    pdf_url,
                    headers={"referer": f"{base}/{doi}", "accept": "application/pdf,*/*"},
                    timeout=timeout_ms,
                )
                return r.body()
            except Exception:
                return None

        buf = try_get()
        if not is_pdf(buf):
            # Solve the DDoS-Guard challenge by navigating the page to the PDF,
            # which sets the clearance cookie in the shared context, then retry.
            try:
                page.goto(pdf_url, wait_until="domcontentloaded", timeout=timeout_ms)
            except Exception:
                pass  # inline PDF render can abort the navigation — that's fine
            page.wait_for_timeout(7000)
            buf = try_get()
        if is_pdf(buf):
            return buf, dom
    return None, None


def main():
    ap = argparse.ArgumentParser(description="Browser-based Sci-Hub PDF fallback.")
    ap.add_argument("--kb", required=True, help="absolute KB path")
    ap.add_argument("--doi", action="append", default=[], help="DOI (repeatable)")
    ap.add_argument("--dois-file", help="file with one DOI per line")
    ap.add_argument("--timeout", type=int, default=60, help="per-request timeout (s)")
    ap.add_argument("--headed", action="store_true",
                    help="run a visible browser (sometimes clears stricter challenges)")
    args = ap.parse_args()

    dois = list(args.doi)
    if args.dois_file:
        dois += [ln.strip() for ln in Path(args.dois_file).read_text().splitlines() if ln.strip()]
    if not dois:
        print("no DOIs given (use --doi or --dois-file)", file=sys.stderr)
        sys.exit(2)

    try:
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError:
        print("ERROR: Playwright not installed. Run:\n"
              "  pip install playwright && python3 -m playwright install chromium",
              file=sys.stderr)
        sys.exit(3)

    domains = load_domains()
    if not domains:
        print("ERROR: no domains in scihub_domains.toml", file=sys.stderr)
        sys.exit(4)

    out_dir = Path(args.kb) / ".raw" / "doi"
    out_dir.mkdir(parents=True, exist_ok=True)
    timeout_ms = args.timeout * 1000

    with sync_playwright() as p:
        # channel="chrome" reuses an installed Google Chrome; fall back to the
        # Playwright-bundled Chromium if that channel is unavailable.
        launch = dict(headless=not args.headed,
                      args=["--disable-blink-features=AutomationControlled"])
        try:
            browser = p.chromium.launch(channel="chrome", **launch)
        except Exception:
            browser = p.chromium.launch(**launch)
        ctx = browser.new_context(user_agent=UA, accept_downloads=True)
        ctx.add_init_script(
            "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
        page = ctx.new_page()

        for doi in dois:
            safe = doi.replace("/", "-")
            dest = out_dir / f"{safe}.pdf"
            if dest.exists() and dest.stat().st_size > MIN_PDF_BYTES:
                print(f"SKIP  {doi}  (already present)")
                continue
            try:
                buf, dom = fetch_one(page, ctx, doi, domains, timeout_ms)
            except Exception as e:
                print(f"MISS  {doi}  (error: {str(e).splitlines()[0][:80]})")
                continue
            if buf:
                dest.write_bytes(buf)
                print(f"OK    {doi}  {len(buf)} bytes  via {dom}")
            else:
                print(f"MISS  {doi}  (no mirror served a PDF)")

        browser.close()


if __name__ == "__main__":
    main()
