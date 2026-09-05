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

OpenCode expects one directory per skill and requires its directory name to
match the skill name. Symlink each sci-brain skill directory:

```bash
mkdir -p ~/.config/opencode/skills
SCI_BRAIN_DIR="$HOME/.config/opencode/sci-brain"
for skill_dir in "$SCI_BRAIN_DIR"/skills/*; do
  [ -f "$skill_dir/SKILL.md" ] || continue
  skill_link="$HOME/.config/opencode/skills/$(basename "$skill_dir")"
  if [ -e "$skill_link" ] || [ -L "$skill_link" ]; then
    echo "skip existing: $skill_link"
  else
    ln -s "$skill_dir" "$skill_link"
  fi
done
```

Existing paths are skipped so the installer never overwrites another local
skill. Review any reported name collisions manually.

### 3. Restart OpenCode

Restart OpenCode. The skill will be available via the native skill tool.

## Usage

### Loading the Skill

Use OpenCode's native `skill` tool to load a skill, for example:

```
use skill tool to load brainstorm-ideas
```

### Project Skills

You can also place the skill in `.opencode/skills/` within your project for project-specific use.

## Updating

```bash
cd ~/.config/opencode/sci-brain && git pull
```

## Uninstalling

```bash
SCI_BRAIN_DIR="$HOME/.config/opencode/sci-brain"
for skill_dir in "$SCI_BRAIN_DIR"/skills/*; do
  [ -f "$skill_dir/SKILL.md" ] || continue
  skill_link="$HOME/.config/opencode/skills/$(basename "$skill_dir")"
  [ -L "$skill_link" ] && [ "$(readlink "$skill_link")" = "$skill_dir" ] && rm "$skill_link"
done
```

Optionally delete the clone: `rm -rf ~/.config/opencode/sci-brain`.

See the [official OpenCode skill documentation](https://opencode.ai/docs/skills/) for discovery locations and naming rules.

## Resource paths and per-skill installs

Run skills from your project directory. Agents locate helper scripts and templates
from each loaded SKILL.md's real directory, following symlinks. Shared writing
resources ship inside `how-to-write-ideas-report/references/`; include that skill
when installing survey or writing workflows with a per-skill manager. Cross-skill
dependencies are located by public skill name in the agent's catalog. Advisor
profiles still require the full checkout.
