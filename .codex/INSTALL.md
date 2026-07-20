# Installing sci-brain for Codex

Enable the sci-brain skill in Codex via native skill discovery. Just clone and symlink.

## Prerequisites

- Git

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/QuantumBFS/sci-brain.git ~/.codex/sci-brain
   ```

2. **Create one symlink per skill:**
   ```bash
   mkdir -p "$HOME/.agents/skills"
   for skill in "$HOME/.codex/sci-brain/skills"/*; do
     [ -f "$skill/SKILL.md" ] || continue
     ln -sfn "$skill" "$HOME/.agents/skills/$(basename "$skill")"
   done
   ```

3. **Restart Codex** (quit and relaunch the CLI) to discover the skill.

## Verify

```bash
find "$HOME/.agents/skills" -maxdepth 1 -type l -print
```

You should see one symlink for each directory under `sci-brain/skills/` that
contains a `SKILL.md`.

## Updating

```bash
cd ~/.codex/sci-brain && git pull
```

Skills update instantly through the symlinks.

## Uninstalling

```bash
for skill in "$HOME/.codex/sci-brain/skills"/*; do
  [ -f "$skill/SKILL.md" ] || continue
  rm "$HOME/.agents/skills/$(basename "$skill")"
done
```

Optionally delete the clone: `rm -rf ~/.codex/sci-brain`.
