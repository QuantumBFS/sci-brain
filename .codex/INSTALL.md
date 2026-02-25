# Installing sci-brainstorm for Codex

Enable the sci-brainstorm skill in Codex via native skill discovery. Just clone and symlink.

## Prerequisites

- Git

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/QuantumBFS/sci-brainstorm.git ~/.codex/sci-brainstorm
   ```

2. **Create the skills symlink:**
   ```bash
   mkdir -p ~/.agents/skills
   ln -s ~/.codex/sci-brainstorm/skills/sci-brainstorm ~/.agents/skills/sci-brainstorm
   ```

3. **Restart Codex** (quit and relaunch the CLI) to discover the skill.

## Verify

```bash
ls -la ~/.agents/skills/sci-brainstorm
```

You should see a symlink pointing to the sci-brainstorm skills directory.

## Updating

```bash
cd ~/.codex/sci-brainstorm && git pull
```

Skills update instantly through the symlink.

## Uninstalling

```bash
rm ~/.agents/skills/sci-brainstorm
```

Optionally delete the clone: `rm -rf ~/.codex/sci-brainstorm`.
