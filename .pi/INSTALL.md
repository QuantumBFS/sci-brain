# Installing sci-brain for pi

Enable all sci-brain skills through pi's native skill discovery. Pi loads skills
from `~/.agents/skills/` (a global location it shares with Codex), expects one
directory containing `SKILL.md` per discovered skill, and supports symlinked
skill folders.

## Prerequisites

- Git

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/QuantumBFS/sci-brain.git ~/.pi/sci-brain
   ```

2. **Symlink each skill directory:**
   ```bash
   mkdir -p ~/.agents/skills
   SCI_BRAIN_DIR="$HOME/.pi/sci-brain"
   for skill_dir in "$SCI_BRAIN_DIR"/skills/*; do
     [ -f "$skill_dir/SKILL.md" ] || continue
     skill_link="$HOME/.agents/skills/$(basename "$skill_dir")"
     if [ -e "$skill_link" ] || [ -L "$skill_link" ]; then
       echo "skip existing: $skill_link"
     else
       ln -s "$skill_dir" "$skill_link"
     fi
   done
   ```

   Existing paths are skipped so the installer never overwrites another local
   skill. Review any reported name collisions manually.

3. **Restart pi** (quit and relaunch the CLI) to discover the skill.

## Verify

```bash
find -L ~/.agents/skills -mindepth 2 -maxdepth 2 -name SKILL.md -print | sort
```

You should see the sci-brain skill entry points, including
`brainstorm-ideas/SKILL.md`, `autoresearch/SKILL.md`, and
`know-me-better/SKILL.md`.

## Updating

```bash
cd ~/.pi/sci-brain && git pull
```

Skills update instantly through the symlink.

## Alternative: install via the npm package

If you use pi's package manager instead of a git checkout:

```bash
pi install npm:sci-brain
```

This installs the same `skills/` tree through the package's `pi.skills`
manifest entry; the npm-published version may lag the git `main` branch.

## Uninstalling

```bash
SCI_BRAIN_DIR="$HOME/.pi/sci-brain"
for skill_dir in "$SCI_BRAIN_DIR"/skills/*; do
  [ -f "$skill_dir/SKILL.md" ] || continue
  skill_link="$HOME/.agents/skills/$(basename "$skill_dir")"
  [ -L "$skill_link" ] && [ "$(readlink "$skill_link")" = "$skill_dir" ] && rm "$skill_link"
done
```

Optionally delete the clone: `rm -rf ~/.pi/sci-brain`.

See pi's [skills documentation](https://github.com/earendil-works/pi) for discovery locations.
