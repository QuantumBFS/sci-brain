#!/usr/bin/env python3
"""Validate sci-brain skills against the Agent Skills specification.

Checks (mirrors what pi / Claude Code / Codex enforce at load time):
  1. Every skills/<dir>/SKILL.md has frontmatter with `name` and `description`.
  2. `name` follows the spec: 1-64 chars, lowercase a-z / 0-9 / hyphens,
     no leading/trailing/double hyphens.
  3. The containing directory matches the public `name` (spec requirement;
     required for Claude Code and Codex discovery).
  4. `description` is non-empty and <= 1024 chars.
  5. Manifests (package.json, .claude-plugin/*.json) parse as JSON.

Non-skill directories such as skills/_shared/ (helper docs, no SKILL.md)
are intentionally skipped.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_NAME_LEN = 64
MAX_DESC_LEN = 1024

MANIFESTS = [
    ROOT / "package.json",
    ROOT / ".claude-plugin" / "plugin.json",
    ROOT / ".claude-plugin" / "marketplace.json",
]


def parse_frontmatter(path: Path) -> dict:
    """Parse the frontmatter block of a SKILL.md (between leading `---` lines)."""
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fields = {}
    for line in text[3:end].splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


def main() -> int:
    errors = []

    skill_dirs = sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir())
    if not skill_dirs:
        errors.append(f"no skill directories found under {SKILLS_DIR}")

    for d in skill_dirs:
        skill_md = d / "SKILL.md"
        if not skill_md.exists():
            continue  # data dir (e.g. _shared) — not a skill
        fm = parse_frontmatter(skill_md)

        name = fm.get("name", "")
        desc = fm.get("description", "")

        if not name:
            errors.append(f"{skill_md}: missing frontmatter `name`")
        elif d.name != name:
            errors.append(
                f"{skill_md}: directory '{d.name}' != public name '{name}' "
                "(required by the Agent Skills spec)"
            )
        elif not NAME_RE.match(name) or len(name) > MAX_NAME_LEN:
            errors.append(
                f"{skill_md}: invalid name '{name}' — 1-{MAX_NAME_LEN} chars, "
                "lowercase a-z / 0-9 / single hyphens"
            )

        if not desc:
            errors.append(f"{skill_md}: missing frontmatter `description`")
        elif len(desc) > MAX_DESC_LEN:
            errors.append(
                f"{skill_md}: description {len(desc)} chars > {MAX_DESC_LEN}"
            )

    for manifest in MANIFESTS:
        if not manifest.exists():
            errors.append(f"{manifest}: missing (npm/plugin packaging requires it)")
            continue
        try:
            json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{manifest}: invalid JSON — {exc}")

    if errors:
        print(f"FAIL: {len(errors)} problem(s) found:")
        for err in errors:
            print(f"  - {err}")
        return 1

    n = len([d for d in skill_dirs if (d / "SKILL.md").exists()])
    print(f"OK: {n} skills validated against the Agent Skills spec")
    return 0


if __name__ == "__main__":
    sys.exit(main())
