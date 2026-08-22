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
    # Operational helpers should be invoked from skills/download-ref/helpers/.
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

# ---- ideas ----

def test_ideas_uses_dot_knowledge_paths():
    text = _read("ideas")
    assert "<project>/.knowledge" in text or ".knowledge" in text
    assert "advisors/<slug>/.knowledge" in text
    # Old paths gone
    assert "advisors/<slug>/survey" not in text
    assert ".claude/survey/" not in text
    assert "<registry-root>" not in text


def test_ideas_still_launches_advisor_subagent():
    text = _read("ideas")
    assert "launch a dedicated advisor subagent" in text


def test_ideas_loads_advisor_kb_from_dot_knowledge():
    text = _read("ideas")
    # The advisor's literature comes from .knowledge/, no longer publications.yml
    assert "publications.yml" not in text
    assert "papers/*.md" not in text


def test_ideas_operational_instructions_use_resolved_kb_variables():
    text = _read("ideas")
    assert "Resolve the project KB via `KB=$(python3 skills/download-ref/helpers/resolve_kb.py)`" in text
    assert "ADVISOR_KB=$(python3 skills/download-ref/helpers/resolve_kb.py --advisor <slug>)" in text
    assert "project knowledge base at `<project>/.knowledge/`" not in text
    assert "Ground ideas in loaded knowledge bases (`<project>/.knowledge/` and `advisors/<slug>/.knowledge/`)" not in text

# ---- incarnate ----

def test_incarnate_targets_advisor_dot_knowledge():
    text = _read("incarnate")
    assert "advisors/<slug>/.knowledge" in text or "advisors/<name>/.knowledge" in text
    assert "advisors/<slug>/survey" not in text


def test_incarnate_keeps_profile_md_unchanged():
    text = _read("incarnate")
    # profile.md should still be the deliverable
    assert "profile.md" in text


def test_incarnate_invokes_researchstyle_or_download_ref():
    text = _read("incarnate")
    # The advisor KB is populated by /researchstyle or /download-ref
    assert "researchstyle" in text or "download-ref" in text


# ---- paper-reviewer ----

def test_paper_reviewer_has_frontmatter():
    text = _read("paper-reviewer")
    assert "name: paper-reviewer" in text
    assert "description:" in text


def test_paper_reviewer_uses_shared_writing_workflow():
    text = _read("paper-reviewer")
    assert "skills/_shared/writing-workflow.md" in text


def test_paper_reviewer_mentions_verification_chain():
    # Guideline #8: never invent BibTeX; use the lookup chain.
    text = _read("paper-reviewer")
    assert "CrossRef" in text
    assert "Semantic Scholar" in text


def test_paper_reviewer_verifies_every_bib_entry_with_helper():
    text = _read("paper-reviewer")
    assert "verify_bib.py" in text
    assert "every bibliography entry" in text.lower()
    for field in ("title", "authors", "year", "venue", "volume", "pages", "DOI"):
        assert field in text


def test_paper_reviewer_is_comment_first_then_apply():
    # Operating principle: non-destructive, approve before edit.
    text = _read("paper-reviewer").lower()
    assert "comment" in text
    assert "approve" in text or "approval" in text


def test_paper_reviewer_covers_the_eight_checks():
    text = _read("paper-reviewer").lower()
    # #1 sentence length / one concept
    assert "one concept" in text or "sentence length" in text
    # #2 define before use
    assert "before use" in text or "forward reference" in text or "forward-reference" in text
    # #3 paragraph purpose / one job
    assert "paragraph" in text
    # #4 DRY / anti-repetition (new)
    assert "dry" in text or "repetition" in text or "repeated" in text
    # #5 display math discipline
    assert "display math" in text or "display equation" in text
    # #6 read the whole paper first
    assert "whole" in text
    # #7 figure integration / orphan figures
    assert "figure" in text and "orphan" in text


def test_paper_reviewer_repairs_refs_via_download_ref():
    # Never invent BibTeX from memory; repair via download-ref.
    text = _read("paper-reviewer")
    assert "download-ref" in text


def test_paper_reviewer_has_compile_check():
    text = _read("paper-reviewer").lower()
    assert "latexmk" in text or "pdflatex" in text
    assert "typst compile" in text


def test_paper_reviewer_references_paper_writer_rules():
    # Reuse paper-writer's rule definitions rather than duplicating them.
    text = _read("paper-reviewer")
    assert "paper-writer" in text


def test_paper_reviewer_does_not_collide_with_writer_description():
    # The trigger must be about reviewing an EXISTING manuscript, distinct
    # from paper-writer (drafting) and survey-writer (field assessment).
    text = _read("paper-reviewer")
    front = text.split("---", 2)[1].lower()
    assert "review" in front
    assert "manuscript" in front or "paper" in front


# ---- survey-writer (renamed from review-writer, issue #20) ----

def test_survey_writer_replaces_review_writer():
    # The skill directory was renamed review-writer -> survey-writer.
    assert (SKILLS / "survey-writer" / "SKILL.md").exists()
    assert not (SKILLS / "review-writer").exists()


def test_survey_writer_has_renamed_frontmatter():
    text = _read("survey-writer")
    assert "name: survey-writer" in text
    assert "name: review-writer" not in text


def test_no_lingering_review_writer_references():
    # Every tracked skill file, template, and CLAUDE.md must reference the new
    # name. Catches stale cross-references after the rename.
    scanned = (
        list(SKILLS.rglob("*.md"))
        + list(SKILLS.rglob("*.typ"))
        + [ROOT / "CLAUDE.md"]
    )
    offenders = [
        str(p.relative_to(ROOT)) for p in scanned if "review-writer" in p.read_text()
    ]
    assert offenders == [], f"stale review-writer references: {offenders}"
