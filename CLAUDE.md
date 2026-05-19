# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

sci-brain is a skill-based plugin for AI coding assistants (Claude Code, Codex, OpenCode) that provides a structured scientific research brainstorming workflow. It is not a traditional code project — it consists of skill definition files (SKILL.md) that define agent interaction protocols.

## Skills

Eleven skills in `skills/`, each defined by a `SKILL.md` with YAML frontmatter + instructions:

- **ideas** — The main entry point. Socratic research mentor that understands user background, finds attackable problems, and encourages deeper thinking. When an advisor is selected, `/ideas` launches that advisor as a subagent and loads literature from `advisors/<slug>/.knowledge/`. The project's shared knowledge base is `<project>/.knowledge/`. Auto-calls `researchstyle` (Phase 0, if user chooses Zotero/Scholar) and `writer` (Phase 3, if user wants a report).
- **survey** — Parallel literature search via 7 strategies, populates `<project>/.knowledge/` with `.raw/` JSON, appends to `<project>/ref.bib` via `download-ref`'s helpers, regenerates `INDEX.md`, writes curated `NOTES.md` (sub-themes, open problems, bottlenecks). Run before `/ideas` for deeper literature grounding.
- **writer** — Produces a structured ideas report (Typst/LaTeX/Markdown) with full reasoning trail. Auto-called from `/ideas` at wrap-up, or run standalone on a past session's log.
- **paperwrite** — Use when drafting or revising an actual scientific manuscript. Encodes the von Delft / Martinis workflow: figures first → telegram outline → body → polish abstract+intro+conclusions last. Distinct from `writer` — for real manuscripts with results.
- **researchstyle** — Indexes a paper collection (Zotero / PDF folder / Google Scholar) into the active KB. Default target is `<project>/.knowledge/`; when invoked from `/incarnate` targets `advisors/<slug>/.knowledge/`. Writes `.raw/` JSON, delegates `ref.bib` writes via `download-ref` helpers.
- **download-ref** — Adds one or many new arXiv IDs / DOIs to a knowledge base (`<project>/.knowledge/` by default; `advisors/<slug>/.knowledge/` when invoked from advisor flows). Fetches Semantic Scholar metadata, downloads PDFs (with SciHub fallback), renders to markdown via `pymupdf4llm`, regenerates `INDEX.md`, appends to `ref.bib`. Supports `--from-bib` for bulk operations on an existing BibTeX.
- **quicknote** — Captures the last substantive Q&A exchange, saves to `docs/discussion/notes/`, copies to clipboard.
- **conversation-dump** — Extracts dialog from Claude Code or Codex CLI session logs, classifies user messages across 6 academic dimensions, outputs tagged dialog reports to `docs/dialog/`.
- **import-dialog** — Imports `.md` dialog files (Claude.ai exports, custom markdown conversations) to create or update advisor profiles. Adjunct to `incarnate` for users whose conversation history isn't in JSONL form.
- **soul-extraction** — Reads `/conversation-dump` output, clusters trigger→reaction pairs into `thinking-pattern.md`, detects logic jumps for `master-thinking.md`. Feeds into `incarnate`.
- **incarnate** — Onboards a contributor as a named advisor. Guides them through background, runs conversation-dump and soul-extraction, synthesizes `advisors/<slug>/profile.md`. The advisor's literature cache lives at `advisors/<slug>/.knowledge/` (populated via `/researchstyle` or `/download-ref` against that KB).

## Architecture

**Entry point:** `/ideas` — most users only need this. Other skills are auto-called or can run independently.

**Ideas skill uses a primary Socratic mentor plus an optional advisor subagent:**
- Understands user background (self-intro, Zotero, or Google Scholar)
- Loads project literature from `<project>/.knowledge/INDEX.md` + `NOTES.md`
- When an advisor is selected, also loads `advisors/<slug>/.knowledge/INDEX.md` + `NOTES.md` and pre-fetches representative papers into the advisor subagent context
- Six principles: clarify motivation, encourage thinking (humbly), flag uncertainty, surface related facts, empower based on skills, inspire with deep theory
- Phases: Get to Know You → Find Good Problems → Dive Into the Topic → Wrap Up

**Knowledge base layout** (used by every skill that touches papers):

```
<project>/
  ref.bib                       # cite-key namespace, shared with any LaTeX in this project
  .knowledge/
    INDEX.md                    # auto-regenerated table of contents (download-ref/helpers/index.py)
    NOTES.md                    # human-curated: sub-themes, open problems, bottlenecks
    .raw/{arxiv,doi}/<id>.{json,pdf}
    .figures/{arxiv__<id>,doi__<safe>}/...
    <id>_<slug>.md              # rendered papers at root, with YAML frontmatter

advisors/<slug>/
  profile.md                    # thinking style (committed)
  ref.bib                       # advisor's private BibTeX namespace (created on first append)
  .knowledge/                   # gitignored cache; same shape as project KB
    INDEX.md
    NOTES.md
    .raw/...
    .figures/...
    <id>_<slug>.md
```

`download-ref` owns `INDEX.md`, `ref.bib` (via append), `.raw/`, `.figures/`, and the rendered `<id>_<slug>.md` files. `survey` / `researchstyle` / humans own `NOTES.md`.

**Advisor library** (`advisors/`): Named advisor profiles generated by `incarnate`. Each profile captures cognitive patterns, attention patterns, reasoning strengths, and conversation dynamics, and may include publication-source links and `edge-tts` voice hints. The ideas skill launches a selected advisor as a subagent and loads their `advisors/<slug>/.knowledge/` literature during brainstorming.

**BibTeX lookup chain** (never from memory): CrossRef API → Semantic Scholar API → MCP servers → WebFetch fallback

## Regenerating the Flowchart

```bash
typst compile images/flowchart.typ images/flowchart.svg
typst compile images/flowchart.typ images/flowchart.png
```

## Migrating from the pre-0.3 `<registry-root>/<slug>/` layout

Old sci-brain (≤ 0.2.x) stored surveys under `~/.claude/survey/<topic>/` (or `.codex/survey/`, `.config/opencode/survey/`, `.claude/survey/`) with `summary.md` + `references.bib` per topic. 0.3 moves to one `<project>/.knowledge/` per project (plus per-advisor caches). Migrate by hand:

```sh
# Pick your project root (where you want .knowledge/ to live):
PROJ=/path/to/your/project
mkdir -p "$PROJ/.knowledge"

# Move a single old registry into the project KB:
OLD=~/.claude/survey/topological-orders     # adapt path
mv "$OLD/references.bib" "$PROJ/ref.bib"    # or merge into existing ref.bib
mv "$OLD/summary.md"     "$PROJ/.knowledge/NOTES.md"
mv "$OLD"/*.md           "$PROJ/.knowledge/"   2>/dev/null  # rendered papers
mv "$OLD/.raw"           "$PROJ/.knowledge/.raw"
mv "$OLD/.figures"       "$PROJ/.knowledge/.figures"

# Regenerate INDEX.md (use a stable title — re-runs must use the same string):
python3 skills/download-ref/helpers/index.py \
  --kb "$PROJ/.knowledge" \
  --title "topological-orders — references" \
  --source-note "Migrated from ~/.claude/survey/topological-orders on $(date -u +%Y-%m-%d)."

# Remove the old registry:
rmdir "$OLD"
```

For advisor caches built by the abandoned 0.2-era `publications.yml` flow: that layout was never populated; nothing to migrate. The new flow builds `advisors/<slug>/.knowledge/` via `/researchstyle` or `/download-ref` invoked from `/incarnate`.

Multiple old registries can be merged into one project KB (run the `mv` block per topic; `ref.bib` accepts appends; `NOTES.md` accepts merges as separate top-level headings).

## Installation

- **Claude Code:** `/plugin marketplace add QuantumBFS/sci-brain`
- **Codex:** Clone → symlink to `~/.agents/skills/sci-brain` (see `.codex/INSTALL.md`)
- **OpenCode:** Clone → symlink to `~/.config/opencode/skills/sci-brain` (see `.opencode/INSTALL.md`)

## Key Files

- `.claude-plugin/plugin.json` / `.claude-plugin/marketplace.json` — Plugin metadata for Claude Code marketplace
- `.claude/settings.local.json` — Allowed permissions (WebSearch, academic domain WebFetch, curl, git, typst)
- `docs/plans/` — Design documents for interaction protocols
- `images/flowchart.typ` — Workflow diagram source (Typst + Fletcher package)
