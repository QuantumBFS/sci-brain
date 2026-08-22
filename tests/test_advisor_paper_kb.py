"""Structural tests for advisor knowledge bases.

The advisor KB layout mirrors the project KB:
    advisors/<slug>/
      profile.md           # always present (committed)
      .knowledge/          # gitignored cache (optional; populated by know-me-better/download-ref)
        references.bib     # advisor's BibTeX namespace (created on first append)
        INDEX.md
        NOTES.md
        .raw/{arxiv,doi}/...
        .figures/...
        <id>_<slug>.md

We only enforce: each advisor has profile.md, and the .knowledge cache
is gitignored if/when it exists.
"""
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADVISORS_DIR = ROOT / "advisors"


def _advisor_slugs():
    return [p.name for p in ADVISORS_DIR.iterdir() if p.is_dir() and (p / "profile.md").exists()]


def test_at_least_one_advisor_exists():
    assert _advisor_slugs(), "no advisor folders with profile.md found"


def test_each_advisor_has_profile_md():
    for slug in _advisor_slugs():
        profile = ADVISORS_DIR / slug / "profile.md"
        assert profile.exists(), f"missing profile.md for advisor {slug}"
        # Sanity: not empty
        assert profile.stat().st_size > 0, f"empty profile.md for advisor {slug}"


def test_advisor_knowledge_is_gitignored():
    """The per-advisor .knowledge cache must be excluded from git."""
    gi = (ROOT / ".gitignore").read_text()
    assert "advisors/*/.knowledge/" in gi or "advisors/**/.knowledge/" in gi, \
        ".gitignore must exclude advisors/*/.knowledge/"


def test_advisor_knowledge_when_present_has_expected_shape():
    """If an advisor has a populated .knowledge/, verify the canonical files exist."""
    for slug in _advisor_slugs():
        kb = ADVISORS_DIR / slug / ".knowledge"
        if not kb.exists():
            continue  # cache not built yet — fine
        # INDEX.md is the only file download-ref guarantees on populated KBs
        # (NOTES.md is optional human-curated content)
        index = kb / "INDEX.md"
        if any(kb.glob("*.md")):
            assert index.exists(), f"populated {kb} missing INDEX.md"
