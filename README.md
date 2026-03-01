# sci-brain

A structured scientific research brainstorming workflow for AI coding assistants. Iterates through survey and ideation (with Polya-style critique and question routing) in a loop until the user picks a direction, then produces a research plan.

This brainstorming style incorporates strategic research questioning and problem-solving wisdom from Polya's *How to Solve It*. The skill format is inspired by [superpowers](https://github.com/obra/superpowers).

## Workflow

![Flowchart](images/flowchart.svg)
Source: [images/flowchart.typ](images/flowchart.typ)

### Skills

| Skill | Purpose |
|-------|---------|
| **survey** | Parallel literature search via 7 strategies, builds a registry with verified BibTeX |
| **ideas** | Two-agent ideation with Polya-style critique, adversarial review, kill/rank |
| **writer** | Produces a structured ideas report (Typst/LaTeX/Markdown) with full reasoning trail |
| **researchstyle** | Indexes a personal paper collection (Zotero/PDF folder/Google Scholar) into the registry format |

### How Ideas Works

The ideas skill runs a **3-party conversation** — the Ideator generates, the main agent critiques, and the user steers:

1. **Ideator** (persistent subagent) proposes ideas, optionally through creative lenses:

| Lens | Strategy |
|------|----------|
| Combiner | Merge two distant findings into a novel approach |
| Inverter | Flip a key assumption — what if the opposite is true? |
| Transplanter | Apply a method from field A to problem B |
| Bottleneck-breaker | Directly attack the identified bottleneck |
| Restater | Reframe the problem statement itself |
| Scoper | Zoom in (specialize) or zoom out (generalize — Polya's Inventor's paradox) |

2. **Main agent** diagnoses each idea's weakness, then offers targeted critique questions:

| Weakness pattern | Questions to offer |
|------------------|--------------------|
| Unclear how to validate | Feasibility, Success criteria |
| Feels familiar | Prior art, Timing |
| Rests on a shaky claim | Assumption, Failure mode |
| Vague goal | Impact, Success criteria |
| Long path, no checkpoints | Signs of progress |
| Narrow framing | Restater/Scoper via "Elaborate" |
| Missing survey data | Completeness |

Questions are routed by type: creative questions (Feasibility, Impact, Success criteria, Signs of progress) go to the Ideator; factual questions (Prior art, Assumption, Failure mode, Timing, Completeness) are answered by the main agent. The main agent's elaboration is shown only to the user — never relayed to the Ideator.

3. **User** selects ideas to explore and questions to dig into. Only user feedback reaches the Ideator.

After the conversation, a formal adversarial review kills or ranks ideas, then the user picks a direction.

## Installation

Installation differs by platform. Claude Code has a built-in plugin marketplace. Codex and OpenCode require manual setup.

### Claude Code (via Plugin Marketplace)

```
/plugin marketplace add QuantumBFS/sci-brain
/plugin install sci-brain@sci-brain
```

Then use `/sci-brain` in any session.

### Codex

Tell Codex:

```
Fetch and follow instructions from https://raw.githubusercontent.com/QuantumBFS/sci-brain/refs/heads/main/.codex/INSTALL.md
```

**Detailed docs:** [.codex/INSTALL.md](.codex/INSTALL.md)

### OpenCode

Tell OpenCode:

```
Fetch and follow instructions from https://raw.githubusercontent.com/QuantumBFS/sci-brain/refs/heads/main/.opencode/INSTALL.md
```

**Detailed docs:** [.opencode/INSTALL.md](.opencode/INSTALL.md)

### Updating

Pull latest changes from the install location you used:

```bash
# Codex
cd ~/.codex/sci-brain && git pull

# OpenCode
cd ~/.config/opencode/sci-brain && git pull
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
    report.md                                          # Ideas — comprehensive iteration report
  iteration-2/
    ...
  YYYY-MM-DD-<topic>-ideas-report.md                   # Ideas — final report (input for writer)
  YYYY-MM-DD-<topic>-ideas-report.{typ,tex}            # Writer — polished document
  YYYY-MM-DD-<topic>-references.bib                    # BibTeX references
```

## Contributors
**Initiator**: [Lei Wang](https://github.com/wangleiphy) and [Jin-Guo Liu](https://github.com/GiggleLiu)
**Reviewers**: empty

## License

MIT
