#!/usr/bin/env python3
"""Verify every BibTeX entry against Semantic Scholar metadata.

The helper is a deterministic screening pass for ``paper-reviewer``. It reads
all entries in a bibliography (including uncited entries), resolves metadata
by DOI, arXiv ID, or title, and compares the fields most likely to drift between
preprint and published records.

Usage:
    python3 verify_bib.py --bib /path/to/references.bib [--kb /path/.knowledge]
    python3 verify_bib.py --bib /path/to/references.bib --json

The default output is a severity-ranked table. ``--json`` emits the same report
as structured JSON. Metadata mismatches are findings, so a completed scan exits
0; malformed input or an operational lookup failure exits 2.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from fetch_metadata import S2_API_KEY, S2_FIELDS, post_batch, save


S2_TITLE_URL = "https://api.semanticscholar.org/graph/v1/paper/search/match"
SEVERITY_ORDER = {"high": 0, "med": 1, "low": 2, "none": 3}
MISMATCH_SEVERITY = {
    "title": "high",
    "authors": "high",
    "year": "high",
    "doi": "high",
    "venue": "med",
    "volume": "med",
    "pages": "med",
}
MISSING_SEVERITY = {
    "title": "high",
    "authors": "high",
    "year": "high",
    "venue": "med",
    "volume": "low",
    "pages": "low",
    "doi": "low",
}
ARXIV_RE = re.compile(
    r"^(?:\d{4}\.\d{4,5}|[a-z][a-z.\-]+/\d{7})(?:v\d+)?$",
    re.IGNORECASE,
)


class BibParseError(ValueError):
    """Raised when a BibTeX entry cannot be parsed reliably."""


def _balanced_end(text: str, start: int, opening: str, closing: str) -> int:
    depth = 1
    quoted = False
    escaped = False
    for i in range(start + 1, len(text)):
        char = text[i]
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"':
            quoted = not quoted
            continue
        if quoted:
            continue
        if char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return i
    raise BibParseError(f"unclosed BibTeX block starting at character {start}")


def _skip_separators(body: str, pos: int) -> int:
    while pos < len(body):
        if body[pos].isspace() or body[pos] == ",":
            pos += 1
            continue
        if body[pos] == "%":
            newline = body.find("\n", pos)
            return len(body) if newline < 0 else _skip_separators(body, newline + 1)
        break
    return pos


def _read_value_part(
    body: str, pos: int, macros: dict[str, str],
) -> tuple[str, int]:
    if pos >= len(body):
        raise BibParseError("missing BibTeX field value")
    if body[pos] == "{":
        end = _balanced_end(body, pos, "{", "}")
        return body[pos + 1:end], end + 1
    if body[pos] == '"':
        escaped = False
        braces = 0
        for i in range(pos + 1, len(body)):
            char = body[i]
            if escaped:
                escaped = False
                continue
            if char == "\\":
                escaped = True
                continue
            if char == "{":
                braces += 1
            elif char == "}" and braces:
                braces -= 1
            elif char == '"' and braces == 0:
                return body[pos + 1:i], i + 1
        raise BibParseError("unclosed quoted BibTeX field value")
    end = pos
    while end < len(body) and body[end] not in ",#\n\r":
        end += 1
    value = body[pos:end].strip()
    if not value:
        raise BibParseError("empty BibTeX field value")
    return macros.get(value.casefold(), value), end


def _read_value(
    body: str, pos: int, macros: dict[str, str],
) -> tuple[str, int]:
    parts: list[str] = []
    while True:
        while pos < len(body) and body[pos].isspace():
            pos += 1
        part, pos = _read_value_part(body, pos, macros)
        parts.append(part)
        while pos < len(body) and body[pos].isspace():
            pos += 1
        if pos >= len(body) or body[pos] != "#":
            return "".join(parts).strip(), pos
        pos += 1


def _parse_fields(
    body: str, key: str, macros: dict[str, str] | None = None,
) -> dict[str, str]:
    fields: dict[str, str] = {}
    macros = macros or {}
    pos = 0
    while True:
        pos = _skip_separators(body, pos)
        if pos >= len(body):
            return fields
        match = re.match(r"[A-Za-z][A-Za-z0-9_\-]*", body[pos:])
        if not match:
            raise BibParseError(f"invalid field in entry {key!r} near {body[pos:pos + 20]!r}")
        name = match.group(0).lower()
        pos += len(match.group(0))
        while pos < len(body) and body[pos].isspace():
            pos += 1
        if pos >= len(body) or body[pos] != "=":
            raise BibParseError(f"missing '=' after field {name!r} in entry {key!r}")
        value, pos = _read_value(body, pos + 1, macros)
        fields[name] = value
        while pos < len(body) and body[pos].isspace():
            pos += 1
        if pos < len(body) and body[pos] not in ",%":
            raise BibParseError(f"unexpected text after field {name!r} in entry {key!r}")


def _next_declaration(text: str, pos: int) -> int:
    """Find the next declaration, ignoring top-level percent comments."""
    while True:
        at = text.find("@", pos)
        if at < 0:
            return -1
        line_start = text.rfind("\n", 0, at) + 1
        if text[line_start:at].lstrip().startswith("%"):
            newline = text.find("\n", at)
            pos = len(text) if newline < 0 else newline + 1
            continue
        return at


def parse_bib(text: str) -> list[dict[str, Any]]:
    """Parse real entries from BibTeX while preserving nested braced values."""
    entries: list[dict[str, Any]] = []
    macros: dict[str, str] = {}
    saw_directive = False
    pos = 0
    while True:
        at = _next_declaration(text, pos)
        if at < 0:
            uncommented = "\n".join(
                line for line in text.splitlines()
                if not line.lstrip().startswith("%")
            ).strip()
            if not entries and not saw_directive and uncommented:
                raise BibParseError("bibliography contains no valid BibTeX entries")
            return entries
        match = re.match(r"@([A-Za-z]+)\s*([({])", text[at:])
        if not match:
            raise BibParseError(f"malformed BibTeX declaration at character {at}")
        entry_type = match.group(1).lower()
        opening = match.group(2)
        block_start = at + match.end() - 1
        closing = "}" if opening == "{" else ")"
        block_end = _balanced_end(text, block_start, opening, closing)
        content = text[block_start + 1:block_end]
        pos = block_end + 1
        if entry_type == "string":
            macros.update(_parse_fields(content, "@string", macros))
            saw_directive = True
            continue
        if entry_type in {"comment", "preamble"}:
            saw_directive = True
            continue
        comma = content.find(",")
        if comma < 0:
            raise BibParseError(f"entry at character {at} has no cite key separator")
        key = content[:comma].strip()
        if not key:
            raise BibParseError(f"entry at character {at} has an empty cite key")
        entries.append({
            "key": key,
            "type": entry_type,
            "fields": _parse_fields(content[comma + 1:], key, macros),
        })


def normalize_doi(value: str | None) -> str | None:
    if not value:
        return None
    doi = value.strip().strip("{}")
    doi = re.sub(r"^(?:doi:\s*|https?://(?:dx\.)?doi\.org/)", "", doi,
                 flags=re.IGNORECASE)
    doi = doi.rstrip(".,; ").lower()
    return doi if doi.startswith("10.") else None


def extract_doi(fields: dict[str, str]) -> str | None:
    return normalize_doi(fields.get("doi")) or normalize_doi(fields.get("url"))


def extract_arxiv(fields: dict[str, str]) -> str | None:
    eprint = (fields.get("eprint") or "").strip()
    archive = (fields.get("archiveprefix") or fields.get("eprinttype") or "").lower()
    if eprint and (not archive or "arxiv" in archive) and ARXIV_RE.match(eprint):
        return re.sub(r"v\d+$", "", eprint, flags=re.IGNORECASE)
    url = fields.get("url") or ""
    match = re.search(r"arxiv\.org/(?:abs|pdf)/([^?#\s]+?)(?:\.pdf)?$", url,
                      flags=re.IGNORECASE)
    if match and ARXIV_RE.match(match.group(1)):
        return re.sub(r"v\d+$", "", match.group(1), flags=re.IGNORECASE)
    return None


def entry_identifier(entry: dict[str, Any]) -> tuple[str, str] | None:
    fields = entry["fields"]
    doi = extract_doi(fields)
    if doi:
        return "doi", doi
    arxiv = extract_arxiv(fields)
    if arxiv:
        return "arxiv", arxiv
    return None


def _strip_latex(value: str) -> str:
    value = re.sub(r"\\[`'\"^~=.uvHckbdtr]\s*\{?([A-Za-z])\}?", r"\1", value)
    for _ in range(3):
        value = re.sub(r"\\[A-Za-z]+\*?\s*\{([^{}]*)\}", r"\1", value)
    value = re.sub(r"\\[A-Za-z]+", " ", value)
    value = re.sub(r"\\.", " ", value)
    return value.replace("{", "").replace("}", "")


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    value = unicodedata.normalize("NFKD", _strip_latex(str(value)))
    value = "".join(char for char in value if not unicodedata.combining(char))
    return " ".join(re.findall(r"[a-z0-9]+", value.casefold()))


def normalize_pages(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"[-–—]+", "-", str(value).replace(" ", "")).casefold()


def _split_authors(value: str) -> list[str]:
    authors: list[str] = []
    start = 0
    depth = 0
    for match in re.finditer(r"\s+and\s+", value, flags=re.IGNORECASE):
        depth += value[start:match.start()].count("{") - value[start:match.start()].count("}")
        if depth == 0:
            authors.append(value[start:match.start()].strip())
            start = match.end()
    authors.append(value[start:].strip())
    return [author for author in authors if author]


def normalize_author(name: str) -> str:
    plain = _strip_latex(name)
    comma_parts = [part.strip() for part in plain.split(",") if part.strip()]
    if len(comma_parts) == 2:
        plain = f"{comma_parts[1]} {comma_parts[0]}"
    elif len(comma_parts) == 3:
        plain = f"{comma_parts[2]} {comma_parts[0]} {comma_parts[1]}"
    tokens = re.findall(r"[a-z0-9]+", normalize_text(plain))
    if len(tokens) < 2:
        return " ".join(tokens)
    return f"{tokens[-1]} {''.join(token[0] for token in tokens[:-1])}"


def normalize_authors(value: str | list[dict[str, Any]] | None) -> list[str]:
    if not value:
        return []
    if isinstance(value, str):
        names = _split_authors(value)
    else:
        names = [str(author.get("name") or "") for author in value]
    normalized = [normalize_author(name) for name in names]
    return [name for name in normalized if name]


def _cache_path(kb: Path, kind: str, value: str) -> Path:
    if kind == "title":
        safe = hashlib.sha256(normalize_text(value).encode("utf-8")).hexdigest()
    else:
        safe = value.replace("/", "-") if kind == "doi" else value
    return kb / ".raw" / kind / f"{safe}.json"


def _load_cache(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict) or not data.get("paperId") or not data.get("title"):
        return None
    return data


def search_title(title: str) -> dict[str, Any] | None:
    """Return Semantic Scholar's closest title match, with bounded retries."""
    query = urllib.parse.urlencode({"query": title.replace("-", " "), "fields": S2_FIELDS})
    headers = {"User-Agent": "sci-brain-verify-bib/1.0"}
    if S2_API_KEY:
        headers["x-api-key"] = S2_API_KEY
    request = urllib.request.Request(f"{S2_TITLE_URL}?{query}", headers=headers)
    backoff = 5
    for attempt in range(6):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                data = json.loads(response.read())
            return data if isinstance(data, dict) and data.get("paperId") else None
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return None
            if error.code in (429, 500, 502, 503) and attempt < 5:
                print(f"  HTTP {error.code}, sleep {backoff}s", file=sys.stderr)
                time.sleep(backoff)
                backoff *= 2
                continue
            raise
    return None


def _cache_metadata(kb: Path, kind: str, value: str, metadata: dict[str, Any]) -> None:
    save(_cache_path(kb, kind, value), metadata)


def resolve_metadata(
    entries: list[dict[str, Any]], kb: Path,
) -> list[tuple[dict[str, Any] | None, dict[str, Any]]]:
    """Resolve metadata for entries, batching every uncached identifier."""
    resolved: dict[tuple[str, str], tuple[dict[str, Any] | None, str]] = {}
    identifiers = [identifier for entry in entries if (identifier := entry_identifier(entry))]
    for identifier in dict.fromkeys(identifiers):
        kind, value = identifier
        cached = _load_cache(_cache_path(kb, kind, value))
        if cached is not None:
            resolved[identifier] = (cached, "cache")

    pending = [identifier for identifier in dict.fromkeys(identifiers) if identifier not in resolved]
    for start in range(0, len(pending), 500):
        chunk = pending[start:start + 500]
        ids = [f"{kind.upper()}:{value}" for kind, value in chunk]
        results = post_batch(ids)
        if len(results) != len(chunk):
            raise RuntimeError("Semantic Scholar batch response length did not match request")
        for identifier, metadata in zip(chunk, results):
            if metadata is not None:
                _cache_metadata(kb, *identifier, metadata)
            resolved[identifier] = (metadata, "batch")

    title_queries: dict[str, str] = {}
    for entry in entries:
        title = entry["fields"].get("title")
        if not entry_identifier(entry) and title:
            title_queries.setdefault(normalize_text(title), title)
    resolved_titles: dict[str, tuple[dict[str, Any] | None, str | None]] = {}
    for normalized, title in title_queries.items():
        cached = _load_cache(_cache_path(kb, "title", title))
        if cached is not None:
            resolved_titles[normalized] = (cached, "cache")
            continue
        metadata = search_title(title)
        resolved_titles[normalized] = (metadata, "title" if metadata else None)
        if metadata:
            _cache_metadata(kb, "title", title, metadata)
            external = metadata.get("externalIds") or {}
            doi = normalize_doi(external.get("DOI"))
            arxiv = external.get("ArXiv")
            if doi:
                _cache_metadata(kb, "doi", doi, metadata)
            elif arxiv:
                _cache_metadata(kb, "arxiv", str(arxiv), metadata)

    output: list[tuple[dict[str, Any] | None, dict[str, Any]]] = []
    for entry in entries:
        identifier = entry_identifier(entry)
        if identifier:
            metadata, source = resolved[identifier]
            lookup = {"type": identifier[0], "value": identifier[1], "source": source}
        else:
            title = entry["fields"].get("title")
            metadata, source = resolved_titles.get(normalize_text(title), (None, None)) if title else (None, None)
            lookup = {"type": "title" if title else "none", "value": title, "source": source}
        output.append((metadata, lookup))
    return output


def _source_fields(metadata: dict[str, Any]) -> dict[str, Any]:
    journal = metadata.get("journal") or {}
    external = metadata.get("externalIds") or {}
    return {
        "title": metadata.get("title"),
        "authors": metadata.get("authors") or [],
        "year": str(metadata.get("year")) if metadata.get("year") is not None else None,
        "venue": journal.get("name") or metadata.get("venue"),
        "volume": journal.get("volume"),
        "pages": journal.get("pages"),
        "doi": external.get("DOI"),
    }


def _bib_fields(entry: dict[str, Any]) -> dict[str, Any]:
    fields = entry["fields"]
    return {
        "title": fields.get("title"),
        "authors": fields.get("author"),
        "year": fields.get("year"),
        "venue": fields.get("journal") or fields.get("booktitle"),
        "volume": fields.get("volume"),
        "pages": fields.get("pages"),
        "doi": extract_doi(fields),
    }


def _normalized(field: str, value: Any) -> Any:
    if field == "authors":
        return normalize_authors(value)
    if field == "pages":
        return normalize_pages(value)
    if field == "doi":
        return normalize_doi(value)
    return normalize_text(value)


def compare_entry(
    entry: dict[str, Any], metadata: dict[str, Any] | None, lookup: dict[str, Any],
) -> dict[str, Any]:
    if metadata is None:
        return {
            "key": entry["key"],
            "status": "unverifiable",
            "severity": "med",
            "lookup": lookup,
            "findings": [{
                "field": "record",
                "kind": "unverifiable",
                "severity": "med",
                "bib": entry["fields"].get("title"),
                "semantic_scholar": None,
            }],
            "compared_fields": [],
            "unverified_fields": ["title", "authors", "year", "venue", "volume", "pages", "doi"],
        }

    bib = _bib_fields(entry)
    source = _source_fields(metadata)
    findings: list[dict[str, Any]] = []
    compared: list[str] = []
    unverified: list[str] = []
    for field in ("title", "authors", "year", "venue", "volume", "pages", "doi"):
        bib_value = bib[field]
        source_value = source[field]
        if not source_value:
            if bib_value:
                unverified.append(field)
                findings.append({
                    "field": field,
                    "kind": "unverifiable",
                    "severity": MISSING_SEVERITY[field],
                    "bib": bib_value,
                    "semantic_scholar": None,
                })
            continue
        if not bib_value:
            findings.append({
                "field": field,
                "kind": "missing",
                "severity": MISSING_SEVERITY[field],
                "bib": None,
                "semantic_scholar": source_value,
            })
            continue
        compared.append(field)
        if _normalized(field, bib_value) != _normalized(field, source_value):
            findings.append({
                "field": field,
                "kind": "mismatch",
                "severity": MISMATCH_SEVERITY[field],
                "bib": bib_value,
                "semantic_scholar": source_value,
            })

    findings.sort(key=lambda finding: (SEVERITY_ORDER[finding["severity"]], finding["field"]))
    severity = findings[0]["severity"] if findings else "none"
    has_discrepancy = any(finding["kind"] != "unverifiable" for finding in findings)
    return {
        "key": entry["key"],
        "status": "mismatch" if has_discrepancy else "unverifiable" if unverified else "ok",
        "severity": severity,
        "lookup": lookup,
        "findings": findings,
        "compared_fields": compared,
        "unverified_fields": unverified,
    }


def verify_bibliography(bib: Path, kb: Path) -> dict[str, Any]:
    entries = parse_bib(bib.read_text(encoding="utf-8"))
    metadata = resolve_metadata(entries, kb)
    results = [compare_entry(entry, record, lookup)
               for entry, (record, lookup) in zip(entries, metadata)]
    results.sort(key=lambda result: (SEVERITY_ORDER[result["severity"]], result["key"].casefold()))
    status_counts = {status: sum(result["status"] == status for result in results)
                     for status in ("ok", "mismatch", "unverifiable")}
    severity_counts = {severity: sum(
        finding["severity"] == severity
        for result in results
        for finding in result["findings"]
    ) for severity in ("high", "med", "low")}
    return {
        "bib": str(bib),
        "summary": {
            "entries": len(results),
            **status_counts,
            "findings": severity_counts,
        },
        "entries": results,
    }


def _display(value: Any, limit: int = 52) -> str:
    if value is None:
        return "-"
    if isinstance(value, list):
        value = ", ".join(
            str(item.get("name") or "") if isinstance(item, dict) else str(item)
            for item in value
        )
    text = " ".join(str(value).split())
    return text if len(text) <= limit else text[:limit - 1] + "…"


def render_table(report: dict[str, Any]) -> str:
    headers = ("severity", "status", "key", "field", "bib", "semantic_scholar")
    rows: list[tuple[str, ...]] = []
    for entry in report["entries"]:
        if not entry["findings"]:
            rows.append(("-", entry["status"], entry["key"], "-", "-", "-"))
            continue
        for finding in entry["findings"]:
            rows.append((
                finding["severity"], entry["status"], entry["key"], finding["field"],
                _display(finding["bib"]), _display(finding["semantic_scholar"]),
            ))
    widths = [len(header) for header in headers]
    for row in rows:
        widths = [max(width, len(cell)) for width, cell in zip(widths, row)]
    lines = ["  ".join(header.ljust(width) for header, width in zip(headers, widths))]
    lines.append("  ".join("-" * width for width in widths))
    lines.extend("  ".join(cell.ljust(width) for cell, width in zip(row, widths)) for row in rows)
    summary = report["summary"]
    findings = summary["findings"]
    lines.append(
        f"\n{summary['entries']} entries: {summary['ok']} ok, "
        f"{summary['mismatch']} mismatch, {summary['unverifiable']} unverifiable; "
        f"findings: {findings['high']} high, {findings['med']} med, {findings['low']} low"
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--bib", required=True, type=Path,
                        help="Bibliography to verify.")
    parser.add_argument("--kb", type=Path,
                        help="Knowledge-base cache root (default: bibliography directory).")
    parser.add_argument("--json", action="store_true",
                        help="Emit structured JSON instead of the human-readable table.")
    args = parser.parse_args(argv)
    if not args.bib.is_file():
        print(f"bib not found: {args.bib}", file=sys.stderr)
        return 2
    kb = args.kb or args.bib.parent
    try:
        report = verify_bibliography(args.bib, kb)
    except (BibParseError, OSError, RuntimeError, urllib.error.URLError, json.JSONDecodeError) as error:
        print(f"verification failed: {error}", file=sys.stderr)
        return 2
    if args.json:
        json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
    else:
        print(render_table(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
