# sci-brainstorm

A structured scientific research brainstorming workflow for AI coding assistants. Conducts deep literature surveys, discovers cross-field connections, then challenges ideas through Socratic and adversarial discussion.

This brainstorming style is from [Lei Wang](https://github.com/wangleiphy) and [Jin-Guo Liu](https://github.com/GiggleLiu), incorporating strategic research questioning and problem-solving wisdom from Polya's *How to Solve It*. The skill format is inspired by [superpowers](https://github.com/obra/superpowers).

## Workflow

1. **Survey** — autonomous literature search (arxiv, Semantic Scholar, PubMed, etc.)
2. **Expand** — cross-field and adjacent subfield exploration
3. **Crystallize** — Socratic questioning to sharpen the research angle
4. **Stress-test** — adversarial challenge with evidence on novelty, rigor, and impact
5. **Refine** — produce a structured research direction document

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

## Optional: MCP Servers

For the best literature search experience, configure these MCP servers:

- [arxiv-mcp-server](https://github.com/blazickjp/arxiv-mcp-server) — arxiv paper search
- [paper-search-mcp](https://github.com/langrocks/paper-search-mcp) — PubMed, bioRxiv, CrossRef
- [Semantic Scholar MCP](https://github.com/YUZongmin/semantic-scholar-mcp) — citation graphs

If unavailable, the workflow falls back to web search.

## Output

Research direction documents are saved to `docs/plans/YYYY-MM-DD-<topic>-research-direction.md`.

## License

MIT
