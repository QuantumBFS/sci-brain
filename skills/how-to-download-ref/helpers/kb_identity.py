"""DOI/arXiv identity shared by KB acquisition, rendering, and maintenance."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote

from index import parse_frontmatter


def normalize(kind: str, value: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{kind} identifier must be a string")
    value = value.strip()
    if kind == "doi":
        value = re.sub(r"^https?://(?:dx\.)?doi\.org/|^doi:\s*", "", value, flags=re.I).lower()
        if not re.fullmatch(r"10\.\d{4,9}/\S+", value) or "\\" in value:
            raise ValueError(f"invalid DOI: {value!r}")
    elif kind == "arxiv":
        value = re.sub(r"^https?://arxiv\.org/(?:abs|pdf)/|^arxiv:\s*", "", value, flags=re.I)
        value = re.sub(r"(?:v\d+)?(?:\.pdf)?$", "", value).lower()
        if not re.fullmatch(r"\d{4}\.\d{4,5}|[a-z][a-z.\-]+/\d{7}", value):
            raise ValueError(f"invalid arXiv ID: {value!r}")
    else:
        raise ValueError(f"unknown identifier type: {kind}")
    return value


def identities(meta: dict) -> set[tuple[str, str]]:
    ext = meta.get("externalIds") or {}
    values = [("doi", meta.get("doi") or ext.get("DOI")),
              ("arxiv", meta.get("arxiv_id") or meta.get("eprint") or ext.get("ArXiv"))]
    if meta.get("type") in ("arxiv", "doi"):
        values.append((meta["type"], meta.get("canonical_id")))
    return {(kind, normalize(kind, value)) for kind, value in values if value}


def papers(kb: Path) -> list[tuple[Path, dict]]:
    return [(path, parse_frontmatter(path)) for path in sorted(kb.glob("*.md"))
            if path.name not in ("INDEX.md", "NOTES.md")]


def identity_index(kb: Path, include_raw: bool = True) -> dict[tuple[str, str], Path]:
    found = {}
    for path, meta in papers(kb):
        for key in identities(meta):
            found.setdefault(key, path)
    if include_raw:
        for kind in ("arxiv", "doi"):
            for path in sorted((kb / ".raw" / kind).glob("*.json")):
                meta = json.loads(path.read_text())
                keys = identities(meta)
                if kind == "arxiv" and not any(k == "arxiv" for k, _ in keys):
                    value = "/".join(path.stem.rsplit("-", 1)) if "-" in path.stem else path.stem
                    keys.add((kind, normalize(kind, value)))
                # Prefer the rendered record for *all* aliases of a cached paper.
                owner = next((found[k] for k in sorted(keys) if k in found), path)
                for key in keys:
                    found.setdefault(key, owner)
    return found


def find_match(index: dict, keys: set) -> tuple[Path, str] | None:
    return next(((index[key], key[0]) for key in sorted(keys) if key in index), None)


def same_record(path: Path, kind: str, value: str) -> bool:
    """An existing namespace can acquire missing assets without adding an alias."""
    if path.suffix == ".json":
        return path.parent.name == kind and path.stem.lower() == value.replace("/", "-").lower()
    meta = parse_frontmatter(path)
    return meta.get("type") == kind and normalize(kind, meta.get("canonical_id", "")) == value


def cache_path(kb: Path, kind: str, value: str, suffix: str = ".json") -> Path:
    """Compare canonical identities, but retain legacy case in cache/figure names."""
    canonical = normalize(kind, value)
    stem = canonical.replace("/", "-")
    directory = kb / ".raw" / kind
    if (directory / (stem + suffix)).exists():
        return directory / (stem + suffix)
    # ponytail: scan small KBs for legacy spelling; preindex paths if bulk imports become slow.
    for path in sorted(directory.glob("*")):
        if path.name.lower() == stem + suffix:
            return path
    for path in sorted(directory.glob("*.json")):
        if path.stem.lower() == stem:
            return directory / (path.stem + suffix)
    for path, meta in papers(kb):
        if meta.get("type") == kind and normalize(kind, meta.get("canonical_id", "")) == canonical:
            # Preserve the spelling used by tracked image links on cache-free clones.
            for linked in re.findall(r"\.figures/" + kind + r"__([^/\s)\"}]+)/", path.read_text()):
                linked = unquote(linked)
                if linked.lower() == stem:
                    return directory / (linked + suffix)
            original = meta["canonical_id"]
            if kind == "doi" and original.lower().startswith("10."):
                stem = original.replace("/", "-")
            break
    return directory / (stem + suffix)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--kb", required=True, type=Path)
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--arxiv")
    group.add_argument("--doi")
    args = p.parse_args()
    kind = "doi" if args.doi else "arxiv"
    try:
        value = normalize(kind, args.doi or args.arxiv)
        index = identity_index(args.kb)
        keys = {(kind, value)}
        match = find_match(index, keys)
        if not match:
            from fetch_metadata import lookup_metadata
            meta = lookup_metadata([(kind, value)])[0]
            keys |= identities(meta or {})
            match = find_match(index, keys)
        if match:
            print(f"present {match[0]} (matched via {match[1]})")
            return 0
        print("missing")
        return 1
    except (OSError, ValueError) as e:
        p.exit(2, f"identity check: {e}\n")


if __name__ == "__main__":
    raise SystemExit(main())
