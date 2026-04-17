# sci-brain

An AI-powered research brainstorming partner. Tell it a research topic — it helps you find good problems, think them through, and shape concrete research ideas together with you.

Works with [Claude Code](https://claude.ai/claude-code), [Codex](https://github.com/openai/codex), and [OpenCode](https://github.com/opencode-ai/opencode). Skill question styles inspired by [superpowers](https://github.com/obra/superpowers).

## Quick Start

Open **Claude Code**/**Codex**/**OpenCode** and type:

```
Install the plugin/skills from https://github.com/QuantumBFS/sci-brain
Then invoke `ideas` skill to start talking.
```

## What does the `/ideas` skill do?

You start a conversation. The agent asks about your background — you can describe yourself, or point it at your Zotero library or Google Scholar profile so it can learn from your papers directly.
The better the agent understands you, the higher quality its recommendations are.

Then you pick a domain expert (distilled from **real** scientists's conversation with AI, see [list](advisors/)) to assist you. Their profile will be loaded to a subagent, to assist you "ask the right question".

## Want Deeper Literature First?

`/ideas` searches the web as you talk, but if you want a thorough literature map before brainstorming, run `/survey` first. It searches in parallel across seven strategies — landscape mapping, adjacent fields, cross-vocabulary, cross-method, historical lineage, negative results, and benchmarks — and builds a registry with verified BibTeX.

When you run `/ideas` afterward, it automatically picks up the survey results and uses them to ground the conversation.

```
/survey              ← build a literature map
/ideas               ← brainstorm with that literature loaded
```

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
