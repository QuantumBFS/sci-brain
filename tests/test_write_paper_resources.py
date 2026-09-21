"""Ensure moved paper-writing references work in an independent installation."""

import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_write_paper_relative_references_work_without_sibling_skills(tmp_path):
    installed = (tmp_path / "write-paper").resolve()
    shutil.copytree(ROOT / "skills" / "write-paper", installed)
    pending = [installed / "SKILL.md"]
    visited = set()

    while pending:
        source = pending.pop()
        if source in visited:
            continue
        visited.add(source)
        for link in re.findall(r"\]\(([^)]+)\)", source.read_text()):
            if "://" in link or link.startswith("#"):
                continue
            target = (source.parent / link.split("#", 1)[0]).resolve()
            assert target.is_relative_to(installed), (source, link)
            assert target.is_file(), (source, link)
            if target.suffix == ".md":
                pending.append(target)
