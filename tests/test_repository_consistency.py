"""Cross-file invariants for skill discovery and public documentation."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


def _skills() -> dict[str, Path]:
    discovered = {}
    for skill_file in sorted(SKILLS.glob("*/SKILL.md")):
        text = skill_file.read_text()
        match = re.search(r"^name:\s*([a-z0-9-]+)\s*$", text, re.MULTILINE)
        assert match, f"missing valid frontmatter name: {skill_file}"
        name = match.group(1)
        assert name not in discovered, f"duplicate public skill name: {name}"
        discovered[name] = skill_file
    return discovered


def test_skill_directory_matches_public_name():
    for name, skill_file in _skills().items():
        assert skill_file.parent.name == name


def test_public_docs_cover_every_skill_and_current_count():
    skills = _skills()
    readme = (ROOT / "README.md").read_text()
    guide = (ROOT / "CLAUDE.md").read_text()

    assert f"The {len(skills)} skills" in guide
    for name in skills:
        assert f"/{name}" in readme, f"README missing /{name}"
        assert f"**{name}**" in guide, f"CLAUDE.md missing {name}"


def test_agent_entrypoint_routes_to_canonical_guide():
    agents = (ROOT / "AGENTS.md").read_text()
    assert "[CLAUDE.md](CLAUDE.md)" in agents
    assert "pytest -q" in agents


def test_install_guides_discover_individual_skill_folders():
    for path in (ROOT / ".codex" / "INSTALL.md", ROOT / ".opencode" / "INSTALL.md"):
        text = path.read_text()
        assert 'skill_dir in "$SCI_BRAIN_DIR"/skills/*' in text
        assert '[ -f "$skill_dir/SKILL.md" ]' in text
        assert "skills/sci-brain" not in text
    # The Codex verify step lists SKILL.md through symlinked skill folders, so
    # `find` must follow links or it prints nothing after a successful install.
    codex = (ROOT / ".codex" / "INSTALL.md").read_text()
    assert "find -L ~/.agents/skills" in codex


def test_retired_public_skill_names_do_not_reappear():
    current_files = [
        ROOT / ".gitignore",
        ROOT / "README.md",
        ROOT / "CLAUDE.md",
        *SKILLS.glob("*/SKILL.md"),
    ]
    for path in current_files:
        assert "researchstyle" not in path.read_text(), path


def test_report_templates_name_the_canonical_bibliography():
    for filename in ("template.typ", "template.bib"):
        text = (SKILLS / "survey-writer" / filename).read_text()
        assert ".knowledge/references.bib" in text
        assert "project's ref.bib" not in text
