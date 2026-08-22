# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

sci-brain is a skill-based plugin for AI coding assistants (Claude Code, Codex, OpenCode) that provides a structured scientific research brainstorming workflow. It is not a traditional code project — it consists of skill definition files (SKILL.md) that define agent interaction protocols.

## Skills

Twelve skills in `skills/`, each defined by a `SKILL.md` with YAML frontmatter + instructions:

- **brainstorm-ideas** — The main entry point. Socratic research mentor that understands user background, finds attackable problems, and encourages deeper thinking. When an advisor is selected, `/brainstorm-ideas` launches that advisor as a subagent and loads literature from `advisors/<slug>/.knowledge/`. The project's shared knowledge base is `<project>/.knowledge/`. Auto-calls `know-me-better` (Phase 0, if user chooses Zotero/Scholar) and `idea-writer` (Phase 3, if user wants a report).
- **survey** — Parallel literature search via 7 strategies, populates `<project>/.knowledge/` with `.raw/` JSON, appends to `<project>/.knowledge/references.bib` via `download-ref`'s helpers, regenerates `INDEX.md`, writes curated `NOTES.md` (sub-themes, open problems, bottlenecks). Run before `/brainstorm-ideas` for deeper literature grounding.
- **idea-writer** — Produces a structured ideas report (Typst/LaTeX/Markdown) with full reasoning trail. Auto-called from `/brainstorm-ideas` at wrap-up, or run standalone on a past session's log.
- **survey-writer** — Produces a structured technology assessment from a populated KB (what it is, pros/cons, state of the art, key problems, optional business relevance). The write-up stage of the `survey` → `download-ref` → `survey-writer` pipeline.
- **paper-writer** — Use when drafting or revising an actual scientific manuscript. Encodes the von Delft / Martinis workflow: figures first → telegram outline → body → polish abstract+intro+conclusions last. Distinct from `idea-writer` — for real manuscripts with results.
- **paper-reviewer** — The *review/enhance an existing manuscript* counterpart to `paper-writer`'s *drafting*. Reads the whole paper, emits location-anchored comments against eight writing guidelines (one-concept sentences, define-before-use, one-job paragraphs, DRY, display-math discipline, figure integration) plus reference & fact verification (CrossRef → Semantic Scholar → MCP → WebFetch, repairs via `download-ref`). Comment-first and non-destructive: applies only approved edits, then re-runs the compile-check. Distinct from `survey-writer` (which assesses a field, not a manuscript).
- **slide-writer** — Builds PDF slide decks in Typst + Touying for scientific talks, lectures, and briefings. Ships a browsable **zoo** under `skills/slide-writer/zoo/`: five color themes (academic/dark/minimal/vibrant/brand), nine layout templates (spread, twocol, hero, cards, punch …), and ~25 palette-aware gadgets (rail_pull, callout, figbox, stat_row, spec_list, theorem/definition/lemma/proof boxes, data_table, conclusion_grid, codebox, toc, pacing), plus optional CeTZ diagram helpers (tensor, automaton-state, flowbox) and pinit pin annotations. Compile `gallery.typ` to browse it (`--input theme=<name>` to retheme). The *technical* (Typst/Touying) companion to the `slide-writing` skill's *logical* (outline sign-off, brand) layer; borrows that workflow and enriches it. Phase 5 hands figure-heavy slides to `figure-taste`.
- **figure-taste** — Reviews the *visual design quality* of a figure, plot, or diagram and prints a scorecard. Source-aware (renders the figure to a raster to look at it via `helpers/render.py`, reads matplotlib/Typst/SVG source so fixes can cite a line), report-only, terminal-first. Scores against an 18-rule rubric (11 general — alignment, proximity, color, hierarchy, contrast, colorblind-safety, …; plus 7 scientific-plot rules — text size, line weight, space use, chartjunk, legend, cross-panel consistency, resolution). Distinct from `paper-reviewer` (which checks whether a figure is cited/discussed in the text, not how it looks) and `paper-writer` (which authors figures). Full rubric in `skills/figure-taste/checklist.md`.
- **autoresearch** — The autoresearch pipeline, one skill with four stage files under `references/stages/`. Reads `research/STATE.md`, verifies stage gate artifacts, and follows the current stage: **topics** (brainstorms topics scored on Checkable/Cheap/Headroom/Publishable; user picks; primary/guard score metrics with gaming risks; red-teamed, user-confirmed acceptance gate per topic → `topics.md`), **db** (insight-coverage-driven reference downloads via `download-ref`, distillation into user-selected `research/INSIGHTS.md`, domain database, pinned reference implementations, `research/CATALOG.md`; owns the survey gate), **validator** (publishable bar in `GOAL.md`, user-confirmed validation method, sealed gitignored holdout, Docker-canonical `validate` CLI with rich JSON errors, negative-control strictness self-test; owns the validator gate), and **run** (the loop: batches of attempts in worktrees with `LOG.md`, validator-scored under a hard time limit; every draft hypothesis must state a *mechanism* against the gap to the bar and its *prior art*, ranked on expected gap closure with cost as a constraint, filtered for novelty and triviality; when stuck it refreshes insights via `survey` into `## Candidate`; reflection reports in `docs/discussion/`; first batch plan confirmed with the user; soft-gated by `authorized_attempts` — at each gate the skill proposes 2–4 lesson-grounded directions and the user authorizes a number of attempts). Each attempt commits code + `LOG.md` + `report.json` on its `attempt-NNN` branch; a cycle-end sync pushes those branches plus main.
- **flow** — Autonomous deep-thinker that conquers one hard goal via a CDCL/DPLL-style search loop: a **preflight gate** (is the goal testable? are all context/KB facts loaded?), then iterate *decide* (**what-if**: assume a condition, test "closer to goal?" + "easier to achieve?") → *propagate* (**simulate**: run consequences forward, reflect; may fan out 2–3 subagents on wide forks) → *learn* (note a reusable clause after **every** trial) → *backjump* (non-chronological, to the real cause) → *pivot* (meta-restart: re-aim to an equally-valuable easier goal when stuck, keeping all notes). Domain-agnostic and KB-optional. Writes a per-trial journal to `docs/flow/<goal-slug>.md` (template in `skills/flow/journal-template.md`). Terminates SOLVED / PIVOTED-SOLVED / EXHAUSTED (≤3 pivots). Distinct from `brainstorm-ideas` (open-ended, collaborative) — `flow` is goal-locked and autonomous.
- **know-me-better** — Indexes a paper collection (Zotero / PDF folder / Google Scholar) into the active KB. Default target is `<project>/.knowledge/`; when invoked from `/incarnate` targets `advisors/<slug>/.knowledge/`. Writes `.raw/` JSON, delegates `references.bib` writes via `download-ref` helpers.
- **download-ref** — Adds one or many new arXiv IDs / DOIs to a knowledge base (`<project>/.knowledge/` by default; `advisors/<slug>/.knowledge/` when invoked from advisor flows). Fetches Semantic Scholar metadata, downloads PDFs (with SciHub fallback), renders to markdown via `pymupdf4llm`, regenerates `INDEX.md`, appends to the KB's `references.bib`. Supports `--from-bib` for bulk operations on an existing BibTeX.
- **conversation-dump** — Extracts dialog from Claude Code or Codex CLI session logs, classifies user messages across 6 academic dimensions, outputs tagged dialog reports to `docs/dialog/`.
- **import-dialog** — Imports `.md` dialog files (Claude.ai exports, custom markdown conversations) to create or update advisor profiles. Adjunct to `incarnate` for users whose conversation history isn't in JSONL form.
- **soul-extraction** — Reads `/conversation-dump` output, clusters trigger→reaction pairs into `thinking-pattern.md`, detects logic jumps for `master-thinking.md`. Feeds into `incarnate`.
- **incarnate** — Onboards a contributor as a named advisor. Guides them through background, runs conversation-dump and soul-extraction, synthesizes `advisors/<slug>/profile.md`. The advisor's literature cache lives at `advisors/<slug>/.knowledge/` (populated via `/know-me-better` or `/download-ref` against that KB).

## Architecture

**Entry point:** `/brainstorm-ideas` — most users only need this. Other skills are auto-called or can run independently.

**brainstorm-ideas skill uses a primary Socratic mentor plus an optional advisor subagent:**
- Understands user background (self-intro, Zotero, or Google Scholar)
- Loads project literature from `<project>/.knowledge/INDEX.md` + `NOTES.md`
- When an advisor is selected, also loads `advisors/<slug>/.knowledge/INDEX.md` + `NOTES.md` and pre-fetches representative papers into the advisor subagent context. The advisor subagent is launched with `Read`/`Grep`/`Glob` over its `.knowledge/` KB plus `WebSearch`/`WebFetch`, and is instructed to consult its KB and the web before making comments (grounding each comment in a cited source or marking it as opinion)
- Six principles: clarify motivation, encourage thinking (humbly), flag uncertainty, surface related facts, empower based on skills, inspire with deep theory
- Phases: Get to Know You → Find Good Problems → Dive Into the Topic → Wrap Up

**Knowledge base layout** (used by every skill that touches papers):

```
<project>/
  .knowledge/
    references.bib              # cite-key namespace for this KB (download-ref appends here)
    INDEX.md                    # auto-regenerated table of contents (download-ref/helpers/index.py)
    NOTES.md                    # human-curated: sub-themes, open problems, bottlenecks
    .raw/{arxiv,doi}/<id>.{json,pdf}
    .figures/{arxiv__<id>,doi__<safe>}/...
    <id>_<slug>.md              # rendered papers at root, with YAML frontmatter

advisors/<slug>/
  profile.md                    # thinking style (committed)
  .knowledge/                   # same shape as project KB; text tracked, .raw/.figures gitignored
    references.bib              # advisor's private BibTeX namespace (created on first append)
    INDEX.md
    NOTES.md
    .raw/...
    .figures/...
    <id>_<slug>.md
```

The canonical bib is `$KB/references.bib` — inside the KB, beside `INDEX.md`/`NOTES.md`. (Pre-0.3 notes placed it at the project root as `ref.bib`; that path is retired. To share with project LaTeX, point `\addbibresource`/`bibliography` at `.knowledge/references.bib` or copy it beside the document.)

`download-ref` owns `INDEX.md`, `references.bib` (via append), `.raw/`, `.figures/`, and the rendered `<id>_<slug>.md` files. `survey` / `know-me-better` / humans own `NOTES.md`.

**Advisor library** (`advisors/`): Named advisor profiles generated by `incarnate`. Each profile captures cognitive patterns, attention patterns, reasoning strengths, and conversation dynamics, and may include publication-source links and `edge-tts` voice hints. The brainstorm-ideas skill launches a selected advisor as a subagent and loads their `advisors/<slug>/.knowledge/` literature during brainstorming.

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
mv "$OLD/references.bib" "$PROJ/.knowledge/references.bib"   # or merge into existing references.bib
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

For advisor caches built by the abandoned 0.2-era `publications.yml` flow: that layout was never populated; nothing to migrate. The new flow builds `advisors/<slug>/.knowledge/` via `/know-me-better` or `/download-ref` invoked from `/incarnate`.

Multiple old registries can be merged into one project KB (run the `mv` block per topic; `references.bib` accepts appends; `NOTES.md` accepts merges as separate top-level headings).

## Installation

- **Claude Code:** `/plugin marketplace add QuantumBFS/sci-brain`
- **Codex:** Clone → symlink to `~/.agents/skills/sci-brain` (see `.codex/INSTALL.md`)
- **OpenCode:** Clone → symlink to `~/.config/opencode/skills/sci-brain` (see `.opencode/INSTALL.md`)

## Key Files

- `.claude-plugin/plugin.json` / `.claude-plugin/marketplace.json` — Plugin metadata for Claude Code marketplace
- `.claude/settings.local.json` — Allowed permissions (WebSearch, academic domain WebFetch, curl, git, typst)
- `docs/plans/` — Design documents for interaction protocols
- `images/flowchart.typ` — Workflow diagram source (Typst + Fletcher package)
