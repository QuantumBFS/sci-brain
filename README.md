# sci-brain

An AI-powered research brainstorming partner. Tell it a research topic — it helps you find good problems, think them through, and shape concrete research ideas together with you.

Works with [Claude Code](https://claude.ai/claude-code), [Codex](https://github.com/openai/codex), and [OpenCode](https://github.com/opencode-ai/opencode). Skill question styles inspired by [superpowers](https://github.com/obra/superpowers).

## Quick Start

**Claude Code**/**Codex**/**OpenCode**:

```
Install the plugin/skills from https://github.com/QuantumBFS/sci-brain
Then invoke `ideas` skill to start talking.
```

## What `/ideas` Is Like

You start a conversation. The mentor asks about your background — you can describe yourself, or point it at your Zotero library or Google Scholar profile so it can learn from your papers directly.

Then you talk about what interests you. The mentor listens, makes connections, searches the literature, and presents a few directions tailored to your skills. Not as a menu — as a conversation. You pick what resonates, push back on what doesn't, combine things.

Once a direction clicks, the mentor helps you sharpen it — narrowing from "I'm interested in X" to a concrete, attackable research problem. It asks one question at a time, checks for prior art, flags risks honestly, and brings in references. You think, it fetches.

When you're done, it reflects on the conversation, recommends a reading, and offers to generate a structured write-up with full BibTeX references. Sessions are logged — the next time you run `/ideas`, it remembers where you left off.

## Want Deeper Literature First?

`/ideas` searches the web as you talk, but if you want a thorough literature map before brainstorming, run `/survey` first. It searches in parallel across seven strategies — landscape mapping, adjacent fields, cross-vocabulary, cross-method, historical lineage, negative results, and benchmarks — and builds a registry with verified BibTeX.

When you run `/ideas` afterward, it automatically picks up the survey results and uses them to ground the conversation.

```
/survey              ← build a literature map
/ideas               ← brainstorm with that literature loaded
```

## Want It to Know Your Work?

The fastest way is to add a few lines to `CLAUDE.md` (or `AGENTS.md` on other platforms):

```markdown
# Research context
My Google Scholar: https://scholar.google.com/citations?user=XXXX
My research interests: quantum computing, tensor networks
I prefer rigorous theoretical work over empirical benchmarks.
```

If your Zotero isn't at the default `~/Zotero/`:

```markdown
# PDF library
My Zotero library is at ~/custom/path/Zotero/
```

You can also run `/researchstyle` to index your full paper collection (Zotero, PDF folder, or Google Scholar) into a registry the mentor can search during brainstorming. This happens automatically inside `/ideas` if you choose the Zotero or Scholar option — `/researchstyle` is only needed standalone if you want to set it up ahead of time.

## MCP Servers (Optional, Recommended)

These make literature search significantly deeper:

| MCP server | What it adds |
|------------|--------------|
| [arxiv-mcp-server](https://github.com/blazickjp/arxiv-mcp-server) | Search arxiv by topic, download full papers |
| [paper-search-mcp](https://github.com/langrocks/paper-search-mcp) | PubMed, bioRxiv, CrossRef — essential for biomedical topics |
| [Semantic Scholar MCP](https://github.com/YUZongmin/semantic-scholar-mcp) | Citation chains, related work, novelty checking |
| [Zotero MCP](https://github.com/kujenga/zotero-mcp) | Search your existing library, read PDFs you already have |

Without them, everything falls back to web search — still works, just less thorough.

## Where Things Are Saved

- **Survey registries** — `~/.claude/survey/<topic>/` — persist across sessions, automatically loaded by `/ideas`
- **Conversation logs** — `docs/discussion/` — each session is a timestamped file; the next session picks up where you left off
- **Quick notes** — `docs/discussion/notes/` — individual Q&A snapshots from `/quicknote`
- **Ideas reports** — `articles/` in your current directory, with a matching `.bib` file

## Want to Become an Advisor?

If you've used Claude Code or Codex for research conversations and want your thinking style captured as a reusable advisor profile, just run:

```
clone https://github.com/QuantumBFS/sci-brain,
invoke incarnate skill in the cloned repo to create my profile,
then submit a pr,
include all relevant chat history, interview output and the generated profile.
```

The whole process is interactive — you review everything before it's published, and you can decide to include the raw conversation data (for research purposes) in the pr or not.

## Contributors

**Initiator**: [Lei Wang](https://github.com/wangleiphy) and [Jin-Guo Liu](https://github.com/GiggleLiu)

## License

MIT. Feel free to adapt from the current codebase, BUT please acknowledge this package properly, thank you.
