# sci-brain

Research skills for [Claude Code](https://claude.ai/claude-code), [Codex](https://github.com/openai/codex), [OpenCode](https://github.com/opencode-ai/opencode), and [pi](https://github.com/earendil-works/pi). Give it a research topic — it surveys the literature into a citable knowledge base on your disk, brainstorms ideas with you, and writes the paper.

## Install

**Claude Code:**

```
/plugin marketplace add QuantumBFS/sci-brain
```

**Codex / OpenCode:** clone this repo and symlink its skill directories into your agent's discovery path — see [`.codex/INSTALL.md`](.codex/INSTALL.md) or [`.opencode/INSTALL.md`](.opencode/INSTALL.md). Or simply tell your agent:

```
Install the plugin/skills from https://github.com/QuantumBFS/sci-brain
```

**pi:** install the npm package:

```
pi install npm:sci-brain
```

or clone the repo and symlink its skill directories into `~/.agents/skills/` (pi's global skill path, shared with Codex) — see [`.pi/INSTALL.md`](.pi/INSTALL.md).

## Start Here: Survey a Field

```
/survey
```

Asks one question to narrow your topic, then searches the literature with up to seven parallel strategies. You pick which directions to keep; every BibTeX entry is verified against CrossRef or Semantic Scholar — never invented from memory. Once full text is fetched, the same skill writes a structured assessment of the field: approaches, state of the art, trade-offs, open problems.

> **One-time setup** for PDF rendering: `python3 -m pip install --user pymupdf4llm`.

## Then: Brainstorm Ideas

```
/brainstorm-ideas
```

A Socratic research mentor. It learns your background (self-description, Zotero, or Google Scholar), picks up the knowledge base from `/survey`, and helps you find a problem worth attacking. Optionally invite an **advisor** — a domain expert distilled from [real scientists' conversations](advisors/) — who joins as a subagent and challenges your thinking. Ends with a structured ideas report.

## Then: Run Autonomous Research

```
/autoresearch
```

Turns an idea into a machine-checkable research campaign: choose topics with score metrics, build the evidence base, seal a Docker-canonical validator, then loop validator-scored attempts with reflection reports — you authorize each cycle.

## Finally: Write Papers & Slides

```
/paper-writer      figures first → outline → body → abstract last
/slide-writer      Typst + Touying decks from a browsable theme/layout zoo
```

## More Skills

| Skill | What it does |
|-------|--------------|
| `/download-ref` | Add arXiv IDs / DOIs to the KB — fetches metadata, PDFs, and renders full text |
| `/paper-reviewer` | Review an existing manuscript against writing guidelines; verifies references |
| `/figure-taste` | Score a figure's visual design against an 18-rule rubric |
| `/flow` | Autonomous deep-thinker that attacks one hard goal via a search loop |
| `/know-me-better` | Index your Zotero / PDF folder / Google Scholar collection into the KB |
| `/conversation-dump` | Extract and classify research conversations from Claude Code or Codex histories |
| `/incarnate` | Import JSONL or Markdown conversations, distill thinking patterns, and capture a reusable advisor profile |

## Where Things Are Saved

Everything lands in one folder inside your project:

```
<project>/.knowledge/
  references.bib      verified BibTeX — point your LaTeX/Typst bibliography here
  INDEX.md            auto-generated table of contents
  NOTES.md            curated sub-themes, open problems, bottlenecks
  <id>_<slug>.md      full-text papers rendered to markdown
  .raw/               original PDFs, metadata, and optional sources (gitignored)
  .figures/           extracted figures (gitignored)
```

- **Project knowledge base** — `<project>/.knowledge/` (layout above). Populated by `/survey`, `/download-ref`, `/know-me-better`.
- **Advisor knowledge bases** — `advisors/<slug>/.knowledge/` — each advisor's private literature cache, same layout.
- **Conversation logs** — `docs/discussion/` — timestamped per session; the next session picks up where you left off.
- **Ideas reports** — `articles/` in your current directory, with a matching `.bib` file.

## Want to Become an Advisor?

If you've used Claude Code or Codex for research conversations and want your thinking style captured as a reusable advisor profile, just tell your agent:

```
clone https://github.com/QuantumBFS/sci-brain,
invoke incarnate skill in the cloned repo to create my profile,
then submit a pr,
include all relevant chat history, interview output and the generated profile.
```

The whole process is interactive — you review everything before it's published, and you decide whether to include the raw conversation data (for research purposes) in the PR.

## Upgrading from ≤ 0.2

> ⚠️ **Breaking change in v0.3.** Knowledge bases moved from per-topic registries (`~/.claude/survey/<topic>/` with `summary.md` + `references.bib`) to one `<project>/.knowledge/` per project, with `references.bib` living *inside* the KB. The `fetch-papers` skill was folded into `download-ref --from-bib`. See [`CLAUDE.md`](./CLAUDE.md) § "Migrating from the pre-0.3 layout" for `mv` commands.

Four internal stages are now modes of their goal-level skill. Update explicit command references as follows:

| Previous command | Current entry point |
|------------------|---------------------|
| `/survey-writer` | `/survey` in Survey Report mode |
| `/idea-writer` | `/brainstorm-ideas` in Ideas Report mode |
| `/import-dialog` | `/incarnate` with Markdown dialog input |
| `/soul-extraction` | `/incarnate` in analysis-only mode |

## Contributors

**Initiators**: [Lei Wang](https://github.com/wangleiphy) and [Jin-Guo Liu](https://github.com/GiggleLiu)

## License

MIT. Feel free to adapt from the current codebase, BUT please acknowledge this package properly, thank you.
