from pathlib import Path


BRAINSTORM_IDEAS_SKILL = Path(__file__).resolve().parents[1] / "skills" / "brainstorm-ideas" / "SKILL.md"


def test_brainstorm_ideas_skill_requires_advisor_subagent_workflow():
    text = BRAINSTORM_IDEAS_SKILL.read_text()

    required_phrases = [
        "launch a dedicated advisor subagent",
        "advisors/<slug>/.knowledge",
        "seed context loaded into the advisor subagent",
        "edge-tts",
    ]

    for phrase in required_phrases:
        assert phrase in text, f"missing required phrase: {phrase!r}"


def test_brainstorm_ideas_skill_drops_old_advisor_cache_terms():
    text = BRAINSTORM_IDEAS_SKILL.read_text()
    forbidden = [
        "10 representative publications",
        "advisor survey index",
        "publications.yml",
    ]
    for phrase in forbidden:
        assert phrase not in text, f"stale phrase still present: {phrase!r}"
