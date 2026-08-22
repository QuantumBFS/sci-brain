# Installing sci-brain for Codex

Enable all sci-brain skills through Codex's native skill discovery. Codex expects
one directory containing `SKILL.md` per discovered skill and supports symlinked
skill folders.

## Prerequisites

- Git

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/QuantumBFS/sci-brain.git ~/.codex/sci-brain
   ```

2. **Symlink each skill directory:**
   ```bash
   mkdir -p ~/.agents/skills
   SCI_BRAIN_DIR="$HOME/.codex/sci-brain"
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

3. **Restart Codex** (quit and relaunch the CLI) to discover the skill.

## Verify

```bash
find -L ~/.agents/skills -mindepth 2 -maxdepth 2 -name SKILL.md -print | sort
```

You should see the sci-brain skill entry points, including
`brainstorm-ideas/SKILL.md`, `autoresearch/SKILL.md`, and
`know-me-better/SKILL.md`.

## Updating

```bash
cd ~/.codex/sci-brain && git pull
```

Skills update instantly through the symlink.

## Uninstalling

```bash
SCI_BRAIN_DIR="$HOME/.codex/sci-brain"
for skill_dir in "$SCI_BRAIN_DIR"/skills/*; do
  [ -f "$skill_dir/SKILL.md" ] || continue
  skill_link="$HOME/.agents/skills/$(basename "$skill_dir")"
  [ -L "$skill_link" ] && [ "$(readlink "$skill_link")" = "$skill_dir" ] && rm "$skill_link"
done
```

Optionally delete the clone: `rm -rf ~/.codex/sci-brain`.

See the [official Codex skill-discovery documentation](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills) for supported locations.
