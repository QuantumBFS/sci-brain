# sci-brainstorm

A structured scientific research brainstorming workflow for AI coding assistants. Iterates through survey, verification, brainstorming, and adversarial critique in a loop until the user picks a direction, then produces a research plan.

This brainstorming style is initiated by [Lei Wang](https://github.com/wangleiphy) and [Jin-Guo Liu](https://github.com/GiggleLiu), incorporating strategic research questioning and problem-solving wisdom from Polya's *How to Solve It*. The skill format is inspired by [superpowers](https://github.com/obra/superpowers).

## Workflow

![Flowchart](images/flowchart.svg)

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

```bash
cd ~/.sci-brainstorm && git pull
```

Skills update instantly through the symlinks.

## Optional: Strategies to Improve the Brainstorm

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

Each loop iteration saves intermediate artifacts. The final document is produced when the user exits the loop.

```
articles/
  iteration-1/
    survey/          # Step 1 — paper PDFs + survey reports
    brainstorm/      # Step 3 — idea reports per lens
    critique/        # Step 4 — report + counter-report pairs
    SUMMARY.md       # Step 5 — ranked ideas table, epitaphs for killed ideas
  iteration-2/
    ...
docs/plans/
  YYYY-MM-DD-<topic>-research-plan.md   # Refine — final output
```

## License

MIT
