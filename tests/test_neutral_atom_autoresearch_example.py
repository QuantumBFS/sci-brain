import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOPICS = ROOT / "examples" / "neutral-atom-autoresearch-topics.md"


def test_topic_reserve_has_ten_validator_ready_topics():
    text = TOPICS.read_text()
    matches = list(re.finditer(r"^## Topic (\d{2})", text, re.MULTILINE))
    assert [match.group(1) for match in matches] == [
        "{:02d}".format(index) for index in range(1, 11)
    ]
    required_sections = [
        "### Research question",
        "### Evidence that the gap is open",
        "### Suitability",
        "### Metrics",
        "### Cost and resources",
        "### Gaming risk and negative control",
        "### Undergraduate prerequisites",
    ]
    required_markers = [
        "**Checkable:**",
        "**Cheap:**",
        "**Headroom:**",
        "**Publishable:**",
        "**Primary metric**",
        "**Guard metric**",
    ]
    boundaries = [match.start() for match in matches] + [len(text)]
    for index in range(10):
        section = text[boundaries[index] : boundaries[index + 1]]
        for marker in required_sections + required_markers:
            assert marker in section
        checkable = int(re.search(r"\*\*Checkable:\*\*\s*(\d)/5", section).group(1))
        cheap = int(re.search(r"\*\*Cheap:\*\*\s*(\d)/5", section).group(1))
        assert checkable >= 3
        assert cheap >= 3
