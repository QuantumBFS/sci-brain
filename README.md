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

## Skills

Two kinds, told apart by the first words of each skill's description. **User trigger** skills are the needs you type (`/survey`, `/write-paper`). **Agentic trigger** skills (`how-to-*`) are procedures the agent reaches for while serving one of those needs; you can still invoke them directly. Each table row is the skill's frontmatter description (test-enforced).

### User trigger — invoke by need

| Skill | Use when |
|---|---|
| [`survey`](skills/survey/) | surveying a research topic into a knowledge base or writing a grounded literature, technology, or field assessment. |
| [`brainstorm-ideas`](skills/brainstorm-ideas/) | brainstorming research ideas with a Socratic collaborator who learns your background and helps find a problem worth attacking. |
| [`know-me-better`](skills/know-me-better/) | you want the agent to learn your research style from your papers (Zotero, PDF folder, or Google Scholar) so it speaks your language. |
| [`autoresearch`](skills/autoresearch/) | starting, resuming, or checking an autoresearch campaign — topics, evidence base, sealed validator, then validator-scored attempt loops. |
| [`write-paper`](skills/write-paper/) | drafting or revising a scientific manuscript with real results. |
| [`review-paper`](skills/review-paper/) | reviewing, commenting on, or fact-checking an existing manuscript, including its references. |
| [`write-slides`](skills/write-slides/) | building a Typst + Touying slide deck for a scientific talk, lecture, or briefing. |
| [`create-advisor`](skills/create-advisor/) | creating or updating a named advisor profile from a researcher's conversation history. |

A typical path: `/survey` a field → `/brainstorm-ideas` with an optional [advisor](advisors/) → `/autoresearch` to run validator-scored attempts → `/write-paper` and `/write-slides`.

Slide templates are maintained in [GiggleLiu/sci-brain-slides](https://github.com/GiggleLiu/sci-brain-slides). The `write-slides` skill uses its v0.1.0 release and documents the local Typst package setup.

> **One-time setup** for PDF rendering: `python3 -m pip install --user pymupdf4llm`.

### Agentic trigger — `how-to-*`, invoked automatically

| Skill | Use when |
|---|---|
| [`how-to-build-kb`](skills/how-to-build-kb/) | turning a list of picked papers into verified knowledge-base entries — references.bib, INDEX.md, and NOTES.md. |
| [`how-to-download-ref`](skills/how-to-download-ref/) | adding arXiv IDs or DOIs to a knowledge base — fetches metadata, PDFs, and full text, then updates references.bib and INDEX.md. |
| [`how-to-write-ideas-report`](skills/how-to-write-ideas-report/) | writing a proposal-style ideas report from a finished brainstorm-ideas session or a chosen research direction. |
| [`how-to-review-figure`](skills/how-to-review-figure/) | judging the visual design of a figure, plot, or diagram against a scientific-plot rubric. |
| [`how-to-flow`](skills/how-to-flow/) | one hard, testable goal resists a direct solution and needs an autonomous decide–simulate–learn–backjump search. |
| [`how-to-dump-dialog`](skills/how-to-dump-dialog/) | extracting and classifying research dialog from Claude Code or Codex session logs. |

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

- **Project knowledge base** — `<project>/.knowledge/` (layout above). Populated by `/survey`, `/how-to-download-ref`, `/know-me-better`.
- **Advisor knowledge bases** — `advisors/<slug>/.knowledge/` — each advisor's private literature cache, same layout.
- **Conversation logs** — `docs/discussion/` — timestamped per session; the next session picks up where you left off.
- **Ideas reports** — `articles/` in your current directory, with a matching `.bib` file.

## Want to Become an Advisor?

If you've used Claude Code or Codex for research conversations and want your thinking style captured as a reusable advisor profile, just tell your agent:

```
clone https://github.com/QuantumBFS/sci-brain,
invoke create-advisor skill in the cloned repo to create my profile,
then submit a pr,
include all relevant chat history, interview output and the generated profile.
```

The whole process is interactive — you review everything before it's published, and you decide whether to include the raw conversation data (for research purposes) in the PR.

## Upgrading

> ⚠️ **Breaking change in v0.5.** Skills are renamed by trigger kind. Update slash commands:

| Previous command | Current entry point |
|------------------|---------------------|
| `/download-ref` | `/how-to-download-ref` |
| `/conversation-dump` | `/how-to-dump-dialog` |
| `/figure-taste` | `/how-to-review-figure` |
| `/flow` | `/how-to-flow` |
| `/paper-writer` | `/write-paper` |
| `/paper-reviewer` | `/review-paper` |
| `/slide-writer` | `/write-slides` |
| `/incarnate` | `/create-advisor` |
| `/survey` (KB-building step) | `/how-to-build-kb`, invoked by `/survey` |
| `/brainstorm-ideas` (report mode) | `/how-to-write-ideas-report`, invoked by `/brainstorm-ideas` |

> ⚠️ **Breaking change in v0.3.** Knowledge bases moved from per-topic registries (`~/.claude/survey/<topic>/` with `summary.md` + `references.bib`) to one `<project>/.knowledge/` per project, with `references.bib` living *inside* the KB. The `fetch-papers` skill was folded into `download-ref --from-bib`. See [`CLAUDE.md`](./CLAUDE.md) § "Migrating from the pre-0.3 layout" for `mv` commands.

Four internal stages became modes of their goal-level skill in v0.3:

| Previous command | Current entry point |
|------------------|---------------------|
| `/survey-writer` | `/survey` in Survey Report mode |
| `/idea-writer` | `/how-to-write-ideas-report` |
| `/import-dialog` | `/create-advisor` with Markdown dialog input |
| `/soul-extraction` | `/create-advisor` in analysis-only mode |

## Contributors

**Initiators**: [Lei Wang](https://github.com/wangleiphy) and [Jin-Guo Liu](https://github.com/GiggleLiu)

## License

MIT. Feel free to adapt from the current codebase, BUT please acknowledge this package properly, thank you.
