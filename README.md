# sci-brain

An AI-powered research brainstorming partner. Tell it a research topic — it surveys the literature, generates ideas, stress-tests them with Polya-style questioning, and produces a report with the survivors.

Works with [Claude Code](https://claude.ai/claude-code), [Codex](https://github.com/openai/codex), and [OpenCode](https://github.com/opencode-ai/opencode). Skill format inspired by [superpowers](https://github.com/obra/superpowers).

## Quick Start

**Claude Code:**
```
/plugin marketplace add QuantumBFS/sci-brain
/plugin install sci-brain@sci-brain
```

Then in any session:
- `/survey` — survey a research topic
- `/ideas` — brainstorm research ideas (works best after a survey)
- `/writer` — write up ideas as a polished document
- `/researchstyle` — index your personal paper collection

## What It Does

![Flowchart](images/flowchart.svg)

### 1. Survey a topic

You name a research area. The AI searches in parallel using 7 strategies (landscape mapping, adjacent subfields, cross-vocabulary, cross-method, historical lineage, negative results, benchmarks). You pick which directions look interesting, and it builds a **survey registry** — `summary.md` + `references.bib` with verified BibTeX.

### 2. Brainstorm ideas

An AI Ideator proposes ideas grounded in your survey, optionally using creative strategies like combining distant findings, inverting assumptions, transplanting methods across fields, or reframing the problem entirely.

You're presented with the ideas and offered targeted questions to dig into — things like *"What's the minimal experiment that would validate this?"* or *"Has this been tried before?"*. You pick the questions that matter to you, and the conversation continues.

When you're ready, a formal adversarial review stress-tests each idea against the literature. Ideas that don't survive get killed with an epitaph. Survivors are ranked. You pick a direction.

### 3. Write it up

The writer skill takes the full reasoning trail — survey, ideas, critique, ranking — and produces a structured document (Typst, LaTeX, or Markdown) with BibTeX references.

## Get Better Results

**Index your papers.** Run `/researchstyle` first to index your Zotero library, PDF folder, or Google Scholar profile. This calibrates the AI to your research taste and lets it search your collection during brainstorming.

**Add your context to CLAUDE.md** (or `AGENTS.md` for other platforms):

```markdown
# Research context
My Google Scholar: https://scholar.google.com/citations?user=XXXX
My research interests: quantum computing, tensor networks
I prefer rigorous theoretical work over empirical benchmarks.
```

**Configure MCP servers** for deeper literature search and Zotero integration:

| MCP server | When it helps |
|------------|---------------|
| [arxiv-mcp-server](https://github.com/blazickjp/arxiv-mcp-server) | **Survey**: search arxiv by topic. **Ideas**: download full papers to verify claims during critique |
| [paper-search-mcp](https://github.com/langrocks/paper-search-mcp) | **Survey**: search PubMed, bioRxiv, CrossRef — essential for biomedical and life science topics |
| [Semantic Scholar MCP](https://github.com/YUZongmin/semantic-scholar-mcp) | **Survey**: follow citation chains to find related work. **Ideas**: check novelty by finding similar papers |
| [Zotero MCP](https://github.com/kujenga/zotero-mcp) | **Survey + Ideas**: search your existing library, read full text of PDFs you already have. Avoids re-downloading papers you own |
| [hybridkris/zotero-mcp](https://lobehub.com/mcp/hybridkris-zotero-mcp) or [add-to-zotero-mcp](https://lobehub.com/mcp/upascal-add-to-zotero-mcp) | **After survey**: export discovered papers back to your Zotero library (requires Zotero API key) |

Without MCP servers, the workflow falls back to web search — still works, just less thorough.

**Point to your Zotero.** Auto-detected at `~/Zotero/`. If yours is elsewhere:

```markdown
# PDF library
My Zotero library is at ~/custom/path/Zotero/
```

## Installation (Other Platforms)

### Codex

Tell Codex:

```
Fetch and follow instructions from https://raw.githubusercontent.com/QuantumBFS/sci-brain/refs/heads/main/.codex/INSTALL.md
```

### OpenCode

Tell OpenCode:

```
Fetch and follow instructions from https://raw.githubusercontent.com/QuantumBFS/sci-brain/refs/heads/main/.opencode/INSTALL.md
```

### Updating

```bash
# Codex
cd ~/.codex/sci-brain && git pull

# OpenCode
cd ~/.config/opencode/sci-brain && git pull
```

For Claude Code, use the plugin marketplace update workflow.

## Output

**Survey registry** (global or project-scoped, persists across sessions):

```
~/.claude/survey/<topic>/
  summary.md        # Papers by sub-theme, open problems, bottlenecks
  references.bib    # BibTeX with abstract + doi/url per entry
```

**Ideas report** (project-scoped):

```
articles/
  YYYY-MM-DD-<topic>-ideas-report.md      # Full reasoning trail
  YYYY-MM-DD-<topic>-ideas-report.typ      # Polished document (Typst/LaTeX)
  YYYY-MM-DD-<topic>-references.bib        # BibTeX references
```

## Contributors

**Initiator**: [Lei Wang](https://github.com/wangleiphy) and [Jin-Guo Liu](https://github.com/GiggleLiu)

## License

MIT
