"""Grep-based structural tests for the rewritten SKILL.md files.

These don't validate prose quality — they verify the rewrites actually
landed (presence of new layout markers, absence of old layout markers).
"""
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


def _read(skill: str) -> str:
    return (SKILLS / skill / "SKILL.md").read_text()


# ---- download-ref ----

def test_download_ref_targets_dot_knowledge():
    text = _read("download-ref")
    assert "<project>/.knowledge" in text or "$KB" in text
    # No more references to <registry-root>/<slug>/
    assert "<registry-root>" not in text
    assert "references.bib" not in text  # the inside-KB bib path is gone
    assert "summary.md" not in text       # superseded by NOTES.md + INDEX.md


def test_download_ref_writes_index_md_via_helper():
    text = _read("download-ref")
    assert "INDEX.md" in text
    assert "index.py" in text


def test_download_ref_appends_to_ref_bib_at_repo_root():
    text = _read("download-ref")
    # ref.bib is the new bib filename, at $(dirname $KB)
    assert "ref.bib" in text


def test_download_ref_has_scihub_fallback_step():
    text = _read("download-ref")
    assert "sci-hub-server" in text.lower() or "scihub" in text.lower()


def test_download_ref_supports_from_bib_mode():
    text = _read("download-ref")
    assert "--from-bib" in text
    assert "bibtex_to_manifest.py" in text


def test_download_ref_mentions_notes_md_belongs_to_humans():
    text = _read("download-ref")
    assert "NOTES.md" in text


def test_download_ref_uses_vendored_helpers_path():
    text = _read("download-ref")
    # All four helpers should be invoked from skills/download-ref/helpers/
    for helper in ("fetch_metadata.py", "render.py", "index.py", "append_bibtex.py"):
        assert helper in text
    # No more cross-skill reference into fetch-papers/helpers/
    assert "fetch-papers/helpers" not in text


def test_download_ref_uses_resolve_kb():
    text = _read("download-ref")
    assert "resolve_kb" in text


# ---- survey ----

def test_survey_targets_dot_knowledge():
    text = _read("survey")
    assert ".knowledge" in text
    assert "<registry-root>" not in text
    assert "registry-location picker" not in text.lower()


def test_survey_writes_notes_md_not_summary_md():
    text = _read("survey")
    assert "NOTES.md" in text
    assert "summary.md" not in text


def test_survey_uses_dot_raw_json_path():
    text = _read("survey")
    assert ".raw/" in text or ".raw/arxiv" in text


def test_survey_invokes_append_bibtex_for_dedup():
    text = _read("survey")
    assert "append_bibtex.py" in text


def test_survey_regenerates_index_at_end():
    text = _read("survey")
    assert "index.py" in text
    assert "INDEX.md" in text


def test_survey_no_step_zero_registry_picker():
    text = _read("survey")
    assert "Step 0" not in text
    assert "Where should I store the survey registry" not in text


def test_survey_transition_uses_download_ref_from_bib():
    text = _read("survey")
    assert "download-ref" in text
    assert "--from-bib" in text


# ---- researchstyle ----

def test_researchstyle_targets_dot_knowledge():
    text = _read("researchstyle")
    assert ".knowledge" in text
    assert "<registry-root>" not in text


def test_researchstyle_writes_notes_md_not_summary_md():
    text = _read("researchstyle")
    assert "NOTES.md" in text
    assert "summary.md" not in text


def test_researchstyle_writes_dot_raw_json():
    text = _read("researchstyle")
    assert ".raw/" in text


def test_researchstyle_invokes_append_bibtex():
    text = _read("researchstyle")
    assert "append_bibtex.py" in text


def test_researchstyle_regenerates_index():
    text = _read("researchstyle")
    assert "index.py" in text

# ---- ideas, incarnate — added in later tasks ----
