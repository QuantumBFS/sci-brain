# Installing sci-brain for OpenCode

## Prerequisites

- [OpenCode.ai](https://opencode.ai) installed
- Git installed

## Installation Steps

### 1. Clone sci-brain

```bash
git clone https://github.com/QuantumBFS/sci-brain.git ~/.config/opencode/sci-brain
```

### 2. Symlink Skills

Create a symlink so OpenCode's native skill tool discovers the skill:

```bash
mkdir -p ~/.config/opencode/skills
ln -s ~/.config/opencode/sci-brain/skills/sci-brain ~/.config/opencode/skills/sci-brain
```

### 3. Restart OpenCode

Restart OpenCode. The skill will be available via the native skill tool.

## Usage

### Loading the Skill

Use OpenCode's native `skill` tool to load the skill:

```
use skill tool to load sci-brain
```

### Project Skills

You can also place the skill in `.opencode/skills/` within your project for project-specific use.

## Updating

```bash
cd ~/.config/opencode/sci-brain && git pull
```

## Uninstalling

```bash
rm ~/.config/opencode/skills/sci-brain
```

Optionally delete the clone: `rm -rf ~/.config/opencode/sci-brain`.
