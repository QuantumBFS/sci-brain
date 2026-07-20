import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOPICS = ROOT / "examples" / "neutral-atom-autoresearch-topics.md"
SMOKE = ROOT / "examples" / "neutral-atom-autoresearch-smoke"


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


def test_smoke_report_contains_public_reproduction_evidence_only():
    readme = (SMOKE / "README.md").read_text()
    summary = (SMOKE / "run-summary.md").read_text()
    for marker in [
        "topics",
        "survey gate",
        "validator gate",
        "attempt-001",
        "attempt-002",
        "attempt-003",
        "baseline score",
        "best development score",
        "holdout",
        "reflection",
    ]:
        assert marker in (readme + summary).lower()

    manifest = json.loads((SMOKE / "source-manifest.json").read_text())
    assert manifest["dataset_doi"] == "10.22002/4m9sp-yzr58"
    expected = {
        "fig4a_rabi_duration.npy": "93c6bd2d084f5c80075c75c8976fe765",
        "fig4a_rabi_pop_1.npy": "a0432de3d76551610e2a795803eb82dd",
        "fig4a_rabi_pop_1_std.npy": "7b95de05b41d1e05fdba72dc90b20334",
    }
    assert {item["filename"]: item["md5"] for item in manifest["files"]} == expected
    serialized = json.dumps(manifest).lower()
    for private_path in ["benchmark/private", "validator/private", ".worktrees"]:
        assert private_path not in serialized
