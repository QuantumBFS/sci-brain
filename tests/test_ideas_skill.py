from pathlib import Path


IDEAS_SKILL = Path(__file__).resolve().parents[1] / "skills" / "ideas" / "SKILL.md"


def test_ideas_skill_requires_advisor_subagent_workflow():
    text = IDEAS_SKILL.read_text()

    required_phrases = [
        "launch a dedicated advisor subagent",
        "advisor survey index",
        "10 representative publications",
        "rendered into markdown",
        "loaded into the advisor subagent context",
        "edge-tts",
    ]

    for phrase in required_phrases:
        assert phrase in text
