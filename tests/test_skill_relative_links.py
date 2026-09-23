"""Every relative Markdown link inside a skill resolves within that skill's own directory.

Skills are installed one at a time (symlinked or copied), so a SKILL.md or any
reference it links to must not point outside the skill.
"""

import re
import shutil
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SKILLS = sorted(p.parent.name for p in (ROOT / "skills").glob("*/SKILL.md"))


@pytest.mark.parametrize("skill", SKILLS)
def test_relative_links_resolve_inside_the_installed_skill(tmp_path, skill):
    installed = (tmp_path / skill).resolve()
    shutil.copytree(ROOT / "skills" / skill, installed)
    pending = [installed / "SKILL.md"]
    visited = set()
    while pending:
        source = pending.pop()
        if source in visited:
            continue
        visited.add(source)
        for link in re.findall(r"\]\(([^)\s]+)\)", source.read_text()):
            if "://" in link or link.startswith("#") or link.startswith("mailto:"):
                continue
            target = (source.parent / link.split("#", 1)[0]).resolve()
            assert target.is_relative_to(installed), (source, link)
            assert target.exists(), (source, link)
            if target.suffix == ".md":
                pending.append(target)
