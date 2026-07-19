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
