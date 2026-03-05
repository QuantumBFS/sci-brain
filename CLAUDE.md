# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

sci-brain is a skill-based plugin for AI coding assistants (Claude Code, Codex, OpenCode) that provides a structured scientific research brainstorming workflow. It is not a traditional code project — it consists of skill definition files (SKILL.md) that define agent interaction protocols.

## Skills

Four skills in `skills/`, each defined by a `SKILL.md` with YAML frontmatter + instructions:

- **survey** — Parallel literature search via 7 strategies, builds a registry (`summary.md` + `references.bib`) with verified BibTeX
- **ideas** — Socratic research mentor (single agent) that understands user background, suggests attackable problems, encourages deeper thinking, and recommends readings
- **writer** — Produces a structured ideas report (Typst/LaTeX/Markdown) with full reasoning trail from ideation
- **researchstyle** — Indexes a personal paper collection (Zotero/PDF folder/Google Scholar) into the same registry format

## Architecture

**Workflow pipeline:** Survey → Ideas → Writer (each skill can run independently or chain)

**Ideas skill uses a single Socratic mentor:**
- Understands user background (self-intro, Zotero, or Google Scholar)
- Adapts to three motivations: understand a topic, generate ideas, evaluate risk
- Five principles: understand motivation, encourage thinking (humbly), flag uncertainty, surface related facts, empower based on skills
- Phases: Get to Know You → Find Good Problems → Conversation Loop → Topic Switch (snapshot) → Wrap Up

**Creative lenses** (used in ideation mode): Combiner, Inverter, Transplanter, Bottleneck-breaker, Restater, Scoper

**Survey registry format** (reused across survey, ideas, researchstyle, writer):
```
<registry-root>/<topic>/
  summary.md       # Papers by sub-theme, open problems, bottlenecks
  references.bib   # BibTeX with abstract + doi/url required per entry
```

**BibTeX lookup chain** (never from memory): CrossRef API → Semantic Scholar API → MCP servers → WebFetch fallback

## Regenerating the Flowchart

```bash
typst compile images/flowchart.typ images/flowchart.svg
typst compile images/flowchart.typ images/flowchart.png
```

## Installation

- **Claude Code:** `/plugin marketplace add QuantumBFS/sci-brain`
- **Codex:** Clone → symlink to `~/.agents/skills/sci-brain` (see `.codex/INSTALL.md`)
- **OpenCode:** Clone → symlink to `~/.config/opencode/skills/sci-brain` (see `.opencode/INSTALL.md`)

## Key Files

- `plugin.json` / `marketplace.json` — Plugin metadata for Claude Code marketplace
- `.claude/settings.local.json` — Allowed permissions (WebSearch, academic domain WebFetch, curl, git, typst)
- `docs/plans/` — Design documents for interaction protocols
- `images/flowchart.typ` — Workflow diagram source (Typst + Fletcher package)
