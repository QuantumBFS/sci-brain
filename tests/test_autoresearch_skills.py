"""Grep-based structural tests for the autoresearch skill family.

Like test_skill_structure.py, these verify the skills' load-bearing
markers exist — not prose quality.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"

STAGE_SKILLS = [
    "autoresearch-topics",
    "autoresearch-metrics",
    "autoresearch-db",
    "autoresearch-validator",
    "autoresearch-run",
]


def _read(skill: str) -> str:
    return (SKILLS / skill / "SKILL.md").read_text()


def _ref(skill: str, name: str) -> str:
    return (SKILLS / skill / "references" / name).read_text()


# ---- autoresearch (dispatcher) ----

def test_dispatcher_has_frontmatter():
    text = _read("autoresearch")
    assert text.startswith("---\nname: autoresearch\n")
    assert "description: Use when" in text


def test_dispatcher_reads_state_and_routes_to_all_stages():
    text = _read("autoresearch")
    assert "research/STATE.md" in text
    for stage_skill in STAGE_SKILLS:
        assert stage_skill in text


def test_dispatcher_recovers_from_missing_or_corrupt_state():
    text = _read("autoresearch")
    # missing STATE.md -> initialize; corrupt -> re-derive from artifacts,
    # confirm with user before overwriting
    assert "state-schema.md" in text
    assert "re-derive" in text.lower()
    assert "confirm" in text.lower()


def test_dispatcher_verifies_gate_artifacts_before_routing():
    text = _read("autoresearch")
    for artifact in ["topics.md", "research/CATALOG.md",
                     "research/INSIGHTS.md", "research/validator/manifest.json"]:
        assert artifact in text


def test_state_schema_defines_all_fields():
    text = _ref("autoresearch", "state-schema.md")
    for field in ["stage:", "topic:", "batch_size:", "time_limit_seconds:",
                  "authorized_rounds:", "next_attempt:", "next_cycle:",
                  "survey_gate:", "validator_gate:", "validator_env:",
                  "overrides:"]:
        assert field in text
    for stage in ["topics", "metrics", "db", "validator", "run", "done"]:
        assert stage in text


# ---- autoresearch-topics ----

def test_topics_has_frontmatter():
    text = _read("autoresearch-topics")
    assert text.startswith("---\nname: autoresearch-topics\n")
    assert "description: Use when" in text


def test_topics_scores_four_suitability_criteria():
    text = _read("autoresearch-topics")
    for criterion in ["Checkable", "Cheap", "Headroom", "Publishable"]:
        assert criterion in text


def test_topics_writes_topics_md_with_metrics_placeholder():
    text = _read("autoresearch-topics")
    assert "topics.md" in text
    assert "### Metrics" in text


def test_topics_lets_user_pick_and_advances_stage():
    text = _read("autoresearch-topics")
    assert "AskUserQuestion" in text
    assert "stage: metrics" in text


# ---- autoresearch-metrics ----

def test_metrics_has_frontmatter():
    text = _read("autoresearch-metrics")
    assert text.startswith("---\nname: autoresearch-metrics\n")
    assert "description: Use when" in text


def test_metrics_fills_topics_md_in_place():
    text = _read("autoresearch-metrics")
    assert "topics.md" in text
    assert "### Metrics" in text


def test_metrics_distinguishes_primary_and_guard():
    text = _read("autoresearch-metrics")
    assert "primary" in text
    assert "guard" in text
    assert "gaming" in text.lower()


def test_metrics_advances_stage_to_db():
    text = _read("autoresearch-metrics")
    assert "stage: db" in text


# ---- autoresearch-db ----

def test_db_has_frontmatter():
    text = _read("autoresearch-db")
    assert text.startswith("---\nname: autoresearch-db\n")
    assert "description: Use when" in text


def test_db_delegates_paper_acquisition_to_download_ref():
    text = _read("autoresearch-db")
    assert "download-ref" in text
    assert ".knowledge" in text


def test_db_checks_insight_coverage_before_distilling():
    text = _read("autoresearch-db")
    assert "insight area" in text.lower()
    assert "coverage" in text.lower()


def test_db_distills_and_lets_user_select_insights():
    text = _read("autoresearch-db")
    assert "research/INSIGHTS.md" in text
    assert "AskUserQuestion" in text
    assert "Shelved" in text


def test_db_builds_catalog_with_status_vocabulary():
    text = _read("autoresearch-db")
    assert "research/CATALOG.md" in text
    for status in ["reproduced", "pinned", "paper-only"]:
        assert status in text


def test_db_owns_survey_gate():
    text = _read("autoresearch-db")
    assert "survey_gate" in text
    assert "stage: validator" in text


def test_insights_template_defines_entry_fields():
    text = _ref("autoresearch-db", "insights-template.md")
    for marker in ["## Selected", "## Shelved", "**Technique**",
                   "**Applies when**", "**Limits**", "**Sources**"]:
        assert marker in text
