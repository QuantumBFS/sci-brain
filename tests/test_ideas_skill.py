from pathlib import Path


IDEAS_SKILL = Path(__file__).resolve().parents[1] / "skills" / "ideas" / "SKILL.md"


def test_ideas_skill_requires_advisor_subagent_workflow():
    text = IDEAS_SKILL.read_text()

    required_phrases = [
        "launch a dedicated advisor subagent",
        "advisors/<slug>/.knowledge",
        "loaded into the advisor subagent context",
        "edge-tts",
    ]

    for phrase in required_phrases:
        assert phrase in text, f"missing required phrase: {phrase!r}"


def test_ideas_skill_drops_old_advisor_cache_terms():
    text = IDEAS_SKILL.read_text()
    forbidden = [
        "10 representative publications",
        "advisor survey index",
        "publications.yml",
    ]
    for phrase in forbidden:
        assert phrase not in text, f"stale phrase still present: {phrase!r}"
