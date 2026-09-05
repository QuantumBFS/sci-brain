# Repository Guide

This is the canonical project guide for agents working in this repository. Claude Code reads it directly; `AGENTS.md` routes Codex, OpenCode, and pi here so the project description stays in one place.

## Project Overview

sci-brain is a skill-based plugin for AI coding assistants (Claude Code, Codex, OpenCode, pi) that provides structured literature, ideation, writing, review, and autonomous-research workflows. It is not a traditional application — its main product is the set of `SKILL.md` interaction protocols and their supporting scripts and references.

## Skills

The 14 skills in `skills/` are each defined by a `SKILL.md` with YAML frontmatter and instructions. Each description is one sentence starting with its trigger kind, mirroring the `qude-software-skills` convention:

- `Agentic trigger. Use when …` — `how-to-*` skills the agent invokes automatically while serving a need (a user may still type them).
- `User trigger. Use when …` — skills a user invokes by need (everything else).

`scripts/validate_skills.py` enforces the prefix; `tests/test_repository_consistency.py` enforces `how-to-*` ⇔ agentic and keeps the README tables identical to the descriptions.

**User trigger:**

- **brainstorm-ideas** — The main ideation entry point. Socratic research mentor that understands user background, finds attackable problems, and encourages deeper thinking. When an advisor is selected, it launches that advisor as a subagent and loads literature from `advisors/<slug>/.knowledge/`. At Phase 3 wrap-up (or on a past session log) it hands off to `how-to-write-ideas-report`.
- **survey** — Parallel literature search via 7 strategies; the user picks directions, then `how-to-build-kb` populates `<project>/.knowledge/`. It also owns the report mode that produces a grounded technology/field assessment from a populated KB; `how-to-download-ref` fetches and renders full text between discovery and writing.
- **write-paper** — Use when drafting or revising an actual scientific manuscript. Encodes the von Delft / Martinis workflow: figures first → telegram outline → body → polish abstract+intro+conclusions last. Distinct from the upstream ideas report in `brainstorm-ideas` — this skill requires real results.
- **review-paper** — The *review/enhance an existing manuscript* counterpart to `write-paper`'s *drafting*. Reads the whole paper, emits location-anchored comments against eight writing guidelines (one-concept sentences, define-before-use, one-job paragraphs, DRY, display-math discipline, figure integration) plus reference & fact verification (CrossRef → Semantic Scholar → MCP → web fetch, repairs via `how-to-download-ref`). Comment-first and non-destructive: applies only approved edits, then re-runs the compile-check. Distinct from `survey` report mode, which assesses a field rather than a manuscript.
- **write-slides** — Builds PDF decks for scientific talks, lectures, and briefings using [GiggleLiu/sci-brain-slides](https://github.com/GiggleLiu/sci-brain-slides), pinned to v0.1.0. The upstream repository owns templates, layouts, themes, and style documentation; this skill guides outline approval, package setup, composition, compilation, and figure review. It uses Typst's native package mechanism with an explicit local package directory until that version is available in the public registry.
- **autoresearch** — The autoresearch pipeline, one skill with four stage files under `references/stages/`. Reads `research/STATE.md`, verifies stage gate artifacts, and follows the current stage: **topics** (brainstorms topics scored on Checkable/Cheap/Headroom/Publishable; user picks; primary/guard score metrics with gaming risks; red-teamed, user-confirmed acceptance gate per topic → `topics.md`), **db** (insight-coverage-driven reference downloads via `how-to-download-ref`, distillation into user-selected `research/INSIGHTS.md`, domain database, pinned reference implementations, `research/CATALOG.md`; owns the survey gate), **validator** (publishable bar in `GOAL.md`, user-confirmed validation method, sealed gitignored holdout, Docker-canonical `validate` CLI with rich JSON errors, negative-control strictness self-test; owns the validator gate), and **run** (the loop: attempts in worktrees with `LOG.md`, validator-scored under a hard time limit; the user chooses a recommended cycle size during initial setup, while the agent may adjust each actual cycle by need within the authorized attempt budget; every draft hypothesis must state a *mechanism* against the gap to the bar and its *prior art*, ranked on expected gap closure with cost as a constraint, filtered for novelty and triviality; when stuck it refreshes insights via `survey` into `## Candidate`; each cycle report plots every scored attempt's raw primary score with no cumulative headline KPIs, the index and campaign retain cross-cycle summaries, and each reflection thinks through 4–6 candidates before ranking the best 2–4 evidence-grounded next directions with explicit reasons and a top recommendation; the first plan of each authorization is user-confirmed; each soft gate asks which direction and how many attempts to authorize). Each attempt commits code + `LOG.md` + `report.json` on its `attempt-NNN` branch; a cycle-end sync pushes those branches plus main.
- **know-me-better** — Lets the agent learn the user's research style so it speaks their language; the mechanism is indexing a paper collection (Zotero / PDF folder / Google Scholar) into the active KB. Default target is `<project>/.knowledge/`; when invoked from `/create-advisor` targets `advisors/<slug>/.knowledge/`. Writes `.raw/` JSON, delegates `references.bib` writes via `how-to-download-ref` helpers.
- **create-advisor** — Creates or updates a named advisor from JSONL histories or imported Markdown dialogs. It classifies conversations, extracts recurring trigger→reaction patterns, confirms logic jumps with the user, and synthesizes `advisors/<slug>/profile.md`; it can also stop after analysis-only artifacts. The advisor's literature cache lives at `advisors/<slug>/.knowledge/`.

**Agentic trigger (`how-to-*`):**

- **how-to-build-kb** — Turns a list of picked papers (from `survey`, `know-me-better`, or `autoresearch`) into verified KB entries: Semantic Scholar / CrossRef lookup, `.raw/` JSON, `references.bib` append via `append_bibtex.py`, `INDEX.md` regeneration, and `NOTES.md` (landscape, open problems, bottlenecks). Non-interactive; never generates BibTeX from memory.
- **how-to-write-ideas-report** — Writes the proposal-style ideas report (research question, novelty, MVE, success/hope/pivot signals, risks, venue, verified references) from a finished `brainstorm-ideas` log. Follows `skills/how-to-write-ideas-report/references/writing-workflow.md`.
- **how-to-review-figure** — Reviews the *visual design quality* of a figure, plot, or diagram and prints a scorecard. Source-aware (renders the figure to a raster to look at it via `helpers/render.py`, reads matplotlib/Typst/SVG source so fixes can cite a line), report-only, terminal-first. Scores against an 18-rule rubric (11 general — alignment, proximity, color, hierarchy, contrast, colorblind-safety, …; plus 7 scientific-plot rules — text size, line weight, space use, chartjunk, legend, cross-panel consistency, resolution). Distinct from `review-paper` (which checks whether a figure is cited/discussed in the text, not how it looks) and `write-paper` (which authors figures). Full rubric in `skills/how-to-review-figure/checklist.md`.
- **how-to-flow** — Autonomous deep-thinker that conquers one hard goal via a CDCL/DPLL-style search loop: a **preflight gate** (is the goal testable? are all context/KB facts loaded?), then iterate *decide* (**what-if**: assume a condition, test "closer to goal?" + "easier to achieve?") → *propagate* (**simulate**: run consequences forward, reflect; may fan out 2–3 subagents on wide forks) → *learn* (note a reusable clause after **every** trial) → *backjump* (non-chronological, to the real cause) → *pivot* (meta-restart: re-aim to an equally-valuable easier goal when stuck, keeping all notes). Domain-agnostic and KB-optional. Writes a per-trial journal to `docs/flow/<goal-slug>.md` (template in `skills/how-to-flow/journal-template.md`). Terminates SOLVED / PIVOTED-SOLVED / EXHAUSTED (≤3 pivots). Distinct from `brainstorm-ideas` (open-ended, collaborative) — `how-to-flow` is goal-locked and autonomous.
- **how-to-download-ref** — Adds one or many new arXiv IDs / DOIs to a knowledge base (`<project>/.knowledge/` by default; `advisors/<slug>/.knowledge/` when invoked from advisor flows). Fetches Semantic Scholar metadata, downloads PDFs (with SciHub fallback); when the user opts in, also fetches arXiv LaTeX sources and renders those refs (incl. DOI entries with an arXiv preprint) from flattened LaTeX (`full_text: latex`) via `--tex-source`, otherwise all refs render via `pymupdf4llm`. Regenerates `INDEX.md`, appends to the KB's `references.bib`. Supports `--from-bib` for bulk operations on an existing BibTeX.
- **how-to-dump-dialog** — Extracts dialog from Claude Code or Codex CLI session logs, classifies user messages across 6 academic dimensions, outputs tagged dialog reports to `docs/dialog/`.

The directory name must match the skill's frontmatter `name`. In particular, the public `know-me-better` skill lives at `skills/know-me-better/`.

## Architecture

**Entry point:** `/brainstorm-ideas` — most users only need this. Other skills are auto-called or can run independently.

**brainstorm-ideas skill uses a primary Socratic mentor plus an optional advisor subagent:**
- Understands user background (self-intro, Zotero, or Google Scholar)
- Loads project literature from `<project>/.knowledge/INDEX.md` + `NOTES.md`
- When an advisor is selected, also loads `advisors/<slug>/.knowledge/INDEX.md` + `NOTES.md` and pre-fetches representative papers into the advisor subagent context. The advisor subagent is launched with file search/read over its `.knowledge/` KB plus web search/fetch, and is instructed to consult its KB and the web before making comments (grounding each comment in a cited source or marking it as opinion)
- Six principles: clarify motivation, encourage thinking (humbly), flag uncertainty, surface related facts, empower based on skills, inspire with deep theory
- Phases: Get to Know You → Find Good Problems → Dive Into the Topic → Wrap Up

**Knowledge base layout** (used by every skill that touches papers):

```
<project>/
  .knowledge/
    references.bib              # cite-key namespace for this KB (how-to-download-ref appends here)
    INDEX.md                    # auto-regenerated table of contents (how-to-download-ref/helpers/index.py)
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

`how-to-download-ref` owns `INDEX.md`, `references.bib` (via append), `.raw/`, `.figures/`, and the rendered `<id>_<slug>.md` files. `survey` / `know-me-better` / humans own `NOTES.md`.

Acquisition checks DOI/arXiv identity across namespaces, falls back from Semantic Scholar to Crossref for DOI metadata, and optionally uses Unpaywall for PDFs when `SCIBRAIN_CONTACT_EMAIL` is set. Rendered frontmatter `note`, `tags`, and `rating` are human-owned and survive re-renders. `how-to-download-ref/helpers/kb_sync.py` restores clone-local caches without changing tracked text; `kb_doctor.py` checks KB consistency offline and can repair only INDEX.md with `--fix`. Full-text values include `jats`, `latex`, `yes`, and `no`.

Each SKILL.md defines installed-resource resolution. Run helpers by their absolute installed paths while keeping the working directory at the user's project. Shared writing resources live inside the installable `how-to-write-ideas-report/references/` directory.

**Advisor library** (`advisors/`): Named advisor profiles generated by `create-advisor`. Each profile captures cognitive patterns, attention patterns, reasoning strengths, and conversation dynamics, and may include publication-source links and `edge-tts` voice hints. The brainstorm-ideas skill launches a selected advisor as a subagent and loads their `advisors/<slug>/.knowledge/` literature during brainstorming.

**BibTeX lookup chain** (never from memory): CrossRef API → Semantic Scholar API → MCP servers → web fetch fallback

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
python3 skills/how-to-download-ref/helpers/index.py \
  --kb "$PROJ/.knowledge" \
  --title "topological-orders — references" \
  --source-note "Migrated from ~/.claude/survey/topological-orders on $(date -u +%Y-%m-%d)."

# Remove the old registry:
rmdir "$OLD"
```

For advisor caches built by the abandoned 0.2-era `publications.yml` flow: that layout was never populated; nothing to migrate. The new flow builds `advisors/<slug>/.knowledge/` via `/know-me-better` or `/how-to-download-ref` invoked from `/create-advisor`.

Multiple old registries can be merged into one project KB (run the `mv` block per topic; `references.bib` accepts appends; `NOTES.md` accepts merges as separate top-level headings).

## Installation

- **Claude Code:** `/plugin marketplace add QuantumBFS/sci-brain`
- **Codex:** Clone → symlink each skill directory into `~/.agents/skills/` (see `.codex/INSTALL.md`)
- **OpenCode:** Clone → symlink each skill directory into `~/.config/opencode/skills/` (see `.opencode/INSTALL.md`)
- **pi:** `pi install npm:sci-brain`, or clone → symlink each skill directory into `~/.agents/skills/` (see `.pi/INSTALL.md`)

## Key Files

- `.claude-plugin/plugin.json` / `.claude-plugin/marketplace.json` — Plugin metadata for Claude Code marketplace
- `package.json` — npm/pi package metadata; matching `v<version>` release tags publish through `.github/workflows/publish.yml` after all three manifest versions are validated as synchronized
- `AGENTS.md` / `CLAUDE.md` — Agent entry point and canonical repository guide
- `skills/*/SKILL.md` — Skill entry points; supporting scripts and references live beside them
- `scripts/validate_skills.py` — Validates every `skills/*/SKILL.md` frontmatter against the Agent Skills spec; run by `.github/workflows/ci.yml` together with `pytest -q`
- `tests/` — Structural and helper tests; run with `pytest -q`
