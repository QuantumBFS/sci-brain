# Installing sci-brain for Codex

Enable the sci-brain skill in Codex via native skill discovery. Just clone and symlink.

## Prerequisites

- Git

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/QuantumBFS/sci-brain.git ~/.codex/sci-brain
   ```

2. **Create the skills symlink:**
   ```bash
   mkdir -p ~/.agents/skills
   ln -s ~/.codex/sci-brain/skills/sci-brain ~/.agents/skills/sci-brain
   ```

3. **Restart Codex** (quit and relaunch the CLI) to discover the skill.

## Verify

```bash
ls -la ~/.agents/skills/sci-brain
```

You should see a symlink pointing to the sci-brain skills directory.

## Updating

```bash
cd ~/.codex/sci-brain && git pull
```

Skills update instantly through the symlink.

## Uninstalling

```bash
rm ~/.agents/skills/sci-brain
```

Optionally delete the clone: `rm -rf ~/.codex/sci-brain`.
