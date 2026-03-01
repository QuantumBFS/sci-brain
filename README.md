# sci-brainstorm

A structured scientific research brainstorming workflow for AI coding assistants. Iterates through survey, ideation, and adversarial critique in a loop until the user picks a direction, then produces a research plan.

This brainstorming style incorporates strategic research questioning and problem-solving wisdom from Polya's *How to Solve It*. The skill format is inspired by [superpowers](https://github.com/obra/superpowers).

## Workflow

![Flowchart](images/flowchart.svg)
Source: [images/flowchart.typ](images/flowchart.typ)

## Installation

Installation differs by platform. Claude Code has a built-in plugin marketplace. Codex and OpenCode require manual setup.

### Claude Code (via Plugin Marketplace)

```
/plugin marketplace add QuantumBFS/sci-brainstorm
/plugin install sci-brainstorm@sci-brainstorm
```

Then use `/sci-brainstorm` in any session.

### Codex

Tell Codex:

```
Fetch and follow instructions from https://raw.githubusercontent.com/QuantumBFS/sci-brainstorm/refs/heads/main/.codex/INSTALL.md
```

**Detailed docs:** [.codex/INSTALL.md](.codex/INSTALL.md)

### OpenCode

Tell OpenCode:

```
Fetch and follow instructions from https://raw.githubusercontent.com/QuantumBFS/sci-brainstorm/refs/heads/main/.opencode/INSTALL.md
```

**Detailed docs:** [.opencode/INSTALL.md](.opencode/INSTALL.md)

### Updating

Pull latest changes from the install location you used:

```bash
# Codex
cd ~/.codex/sci-brainstorm && git pull

# OpenCode
cd ~/.config/opencode/sci-brainstorm && git pull
```

Skills update instantly through the symlinks.

For Claude Code marketplace installs, use the plugin marketplace update workflow.

### Regenerating the flowchart

Requires [Typst](https://typst.app/):

```bash
typst compile images/flowchart.typ images/flowchart.svg
typst compile images/flowchart.typ images/flowchart.png
```

## Optional: Strategies to Improve Ideation

### 1. Configure MCP Servers

For deeper literature search, configure these MCP servers:

- [arxiv-mcp-server](https://github.com/blazickjp/arxiv-mcp-server) — arxiv paper search
- [paper-search-mcp](https://github.com/langrocks/paper-search-mcp) — PubMed, bioRxiv, CrossRef
- [Semantic Scholar MCP](https://github.com/YUZongmin/semantic-scholar-mcp) — citation graphs

If unavailable, the workflow falls back to web search.

### 2. Use CLAUDE.md to Describe Your Research Style

Add your research context to `CLAUDE.md` (or `AGENTS.md` for other platforms) so the AI knows your background, taste, and interests:

```markdown
# Research context
My Google Scholar: https://scholar.google.com/citations?user=XXXX
My research interests: quantum computing, tensor networks
I prefer rigorous theoretical work over empirical benchmarks.
```

### 3. Setup Local PDF Registry

The skill auto-detects Zotero at standard paths (`~/Zotero/`). If your library is elsewhere, or you use a different PDF manager, add the path to `CLAUDE.md`:

```markdown
# PDF library
My Zotero library is at ~/Zotero/
My PDFs are in ~/Papers/
```

This lets the AI search your local paper collection during survey — before hitting external sources.

## Output

Each loop iteration saves intermediate artifacts. The final ideas report includes the full reasoning trail — what was explored, what was killed and why, and the surviving direction with justifications. All citations are in BibTeX format.

**Survey registry** (user chooses global or project-scoped at session start):

```
# Global (shared across projects)
~/.claude/survey/<topic>/          # Claude Code
~/.codex/survey/<topic>/           # Codex
~/.config/opencode/survey/<topic>/ # OpenCode

# Project-scoped
.claude/survey/<topic>/
```

**Per-session working files** (always project-scoped):

```
articles/
  iteration-1/
    ideas/           # Step 2 — idea reports per lens
    critique/        # Step 3 — report + counter-report pairs
    SUMMARY.md       # Step 4 — ranked ideas table, epitaphs for killed ideas
  iteration-2/
    ...
  YYYY-MM-DD-<topic>-ideas-report.{md,typ,tex}   # Refine — format chosen by user
  YYYY-MM-DD-<topic>-references.bib                   # BibTeX references
```

## Contributors
**Initiator**: [Lei Wang](https://github.com/wangleiphy) and [Jin-Guo Liu](https://github.com/GiggleLiu)
**Reviewers**: empty

## License

MIT
