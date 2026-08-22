# sci-brain

Research skills for [Claude Code](https://claude.ai/claude-code), [Codex](https://github.com/openai/codex), and [OpenCode](https://github.com/opencode-ai/opencode). Point it at a research topic — it surveys the literature, builds a citable knowledge base on your disk, writes grounded reports, and brainstorms research ideas with you.

Skill question styles inspired by [superpowers](https://github.com/obra/superpowers).

## Install

**Claude Code:**

```
/plugin marketplace add QuantumBFS/sci-brain
```

**Codex / OpenCode:** clone this repo and symlink it as a skill folder — see [`.codex/INSTALL.md`](.codex/INSTALL.md) or [`.opencode/INSTALL.md`](.opencode/INSTALL.md). Or simply tell your agent:

```
Install the plugin/skills from https://github.com/QuantumBFS/sci-brain
```

## Start Here: Survey a Field

The core of sci-brain is a three-skill pipeline — **search → fetch → write**:

```
/survey            search the literature, pick directions, get verified BibTeX
/download-ref      download the PDFs, render full text into the knowledge base
/survey-writer     write a structured review from what was collected
```

**`/survey`** asks one question to narrow your topic, then searches in parallel with up to seven strategies — landscape mapping, adjacent subfields, cross-vocabulary, cross-method, historical lineage, negative results, and benchmarks. You pick which directions are worth keeping; only those go into the knowledge base. Every BibTeX entry is verified against CrossRef or Semantic Scholar — never invented from memory.

**`/download-ref`** fetches the papers behind those entries: metadata from Semantic Scholar, PDFs from arXiv (with a Sci-Hub fallback for paywalled DOIs), each rendered to markdown so later skills can read and quote the full text. It also works standalone — just say "add arXiv:2401.12345 to the KB".

**`/survey-writer`** turns the populated knowledge base into a structured assessment: what the technology is and why it matters, the main approaches with state of the art and trade-offs per approach, and the key open problems. Output in Markdown, Typst, or LaTeX.

Everything lands in one folder inside your project:

```
<project>/.knowledge/
  references.bib      verified BibTeX — point your LaTeX/Typst bibliography here
  INDEX.md            auto-generated table of contents
  NOTES.md            curated sub-themes, open problems, bottlenecks
  <id>_<slug>.md      full-text papers rendered to markdown
  .raw/               original PDFs + metadata (gitignored)
```

> **One-time setup** for PDF rendering: `python3 -m pip install --user pymupdf4llm`. Add `playwright` (`python3 -m playwright install chromium`) only if you need the Sci-Hub fallback for paywalled DOIs.

## Then: Brainstorm Ideas

```
/brainstorm-ideas
```

A Socratic research mentor. It first asks about your background — describe yourself, or point it at your Zotero library or Google Scholar profile so it can learn from your own papers. The better it knows you, the better its recommendations.

You can also pick a domain expert **advisor** (distilled from *real* scientists' conversations with AI — see the [advisor list](advisors/)) who joins the session as a subagent and challenges your thinking.

If you ran `/survey` first, the brainstorm automatically picks up the knowledge base and grounds the conversation in it. At wrap-up it can write a structured ideas report with the full reasoning trail.

## More Skills

| Skill | What it does |
|-------|--------------|
| `/paper-writer` | Draft a real manuscript: figures first → telegram outline → body → polish |
| `/paper-reviewer` | Review an existing manuscript against writing guidelines; verifies references |
| `/slide-writer` | Build Typst + Touying slide decks from a browsable theme/layout/gadget zoo |
| `/figure-taste` | Score a figure's visual design against an 18-rule rubric |
| `/flow` | Autonomous deep-thinker that attacks one hard goal via a search loop |
| `/know-me-better` | Index your Zotero / PDF folder / Google Scholar collection into the KB |
| `/incarnate` | Capture your thinking style as a reusable advisor profile |

## Where Things Are Saved

- **Project knowledge base** — `<project>/.knowledge/` (see layout above). Populated by `/survey`, `/download-ref`, `/know-me-better`.
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

## Contributors

**Initiators**: [Lei Wang](https://github.com/wangleiphy) and [Jin-Guo Liu](https://github.com/GiggleLiu)

## License

MIT. Feel free to adapt from the current codebase, BUT please acknowledge this package properly, thank you.
