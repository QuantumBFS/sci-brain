---
name: create-advisor
description: User trigger. Use when creating or updating a named advisor profile from a researcher's conversation history.
---

## Installed resources

Keep the working directory at the user's project. Resolve this loaded `SKILL.md`
with `Path(path).resolve()` before locating resources; follow symlinks. Bare
`helpers/`, `references/`, and template paths are relative to that real skill
directory. A path written as `skills/<name>/...` means the installed `<name>`
skill's directory from the agent's skill catalog, not a path in the user's project.
Locate each dependency by its public skill name; copied skills need not be siblings.
If a dependency is absent, report the missing skill and install it before that step.
Shared writing files are bundled in `how-to-write-ideas-report/references/`.

Before running the examples, set `DOWNLOAD_REF_DIR` to the absolute directory of `how-to-download-ref`, `DUMP_DIALOG_DIR` to the absolute directory of `how-to-dump-dialog`. Quote these variables as shown.


## Advisor Profile Generation

Onboard a contributor and create a named advisor profile. The profile captures how a real person thinks — their cognitive style, attention patterns, reasoning strengths, and conversation dynamics — so the brainstorm-ideas skill can launch them as a subagent collaborator rather than a thin inline persona.

## Choose the mode

- **Create an advisor:** start at Step 1 and run the complete workflow.
- **Update an advisor from new conversations:** read the existing `advisors/<slug>/profile.md`, preserve its background, then start at Step 2 with the new JSONL or Markdown sources.
- **Import Markdown dialogs:** ask for the file paths and target advisor, then use the Markdown path in Step 2. For a new advisor, collect the Step 1 background first.
- **Analyze thinking patterns only:** run Conversation Pattern Extraction and stop after writing `thinking-pattern.md` and `master-thinking.md`; do not synthesize an advisor profile unless the user asks.

### Step 1 — Personal Profile

Ask the contributor to provide their academic/professional background:

- **(a)** Tell me yourself (field, experience, what you've worked on)
- **(b)** Zotero library — follow the `know-me-better` skill instructions (`skills/know-me-better/SKILL.md`) to index publications
- **(c)** Google Scholar profile — follow the `know-me-better` skill instructions to index publications

From the response, extract:
- **Name** (ask if not provided)
- **Field and subfields**
- **Key research themes**
- **Technical skills**
- **Notable contributions**
- **Publication sources** if available (homepage, Google Scholar, ORCID, DBLP, arXiv author page)
- **Voice preference** if available (spoken language, accent, or preferred `edge-tts` voice)

Hold this information for Step 4.

**Advisor KB.** Each advisor gets a private knowledge base at `advisors/<slug>/.knowledge/` (shape identical to the project KB: `INDEX.md`, `NOTES.md`, `.raw/`, `.figures/`, rendered `<id>_<slug>.md` files). The advisor's BibTeX namespace lives at `advisors/<slug>/.knowledge/references.bib` (i.e. `$KB/references.bib` for the resolved advisor KB). When `know-me-better` or `how-to-download-ref` is invoked from this skill, resolve the advisor KB path via `python3 "$DOWNLOAD_REF_DIR/helpers/resolve_kb.py" --advisor <slug>` and pass it as `--kb "$KB"` so writes land in the advisor KB rather than the project KB. (Users who set `$SCIBRAIN_KB_DIRNAME` get the right directory name automatically.)

### Step 2 — Conversation Analysis

Ask the contributor to specify their conversation source:

- **(a)** Claude Code / Codex CLI (JSONL session logs)
- **(b)** Exported `.md` dialog files (Claude.ai web exports, custom markdown conversations)
- **(c)** Both — import `.md` files first, then scan JSONL logs, merge all data

Run the analysis pipeline based on the chosen source:

**If (a) — JSONL sessions:**

**Step 2a — how-to-dump-dialog.** Read `skills/how-to-dump-dialog/SKILL.md` and follow Phases 1–4. This extracts all sessions, classifies them by topic, performs deep 6-dimension analysis, and outputs tagged JSON reports. At the end of Phase 2, the contributor selects which topics to analyze in depth.

**If (b) — .md dialog files:**

**Step 2a — parse .md files.** Ask the contributor for one or more file paths (globs are acceptable). Create `docs/dialog/md-import/raw/`, then parse and persist a single file:

```bash
python3 "$DUMP_DIALOG_DIR/parse_md_dialog.py" parse <file.md> \
  > docs/dialog/md-import/raw/<session-id>.json
```

The `parse` subcommand accepts exactly one file. For a glob, resolve it to individual paths and run the command once per file with a unique `<session-id>` output; do not pass multiple expanded paths to one `parse` call. For all Markdown files in one directory, use batch mode:

```bash
python3 "$DUMP_DIALOG_DIR/parse_md_dialog.py" batch <directory> --outdir docs/dialog/md-import/raw/
```

Then follow the adapted how-to-dump-dialog Phases 2–4 on these files: classify them into `docs/dialog/md-import/<topic>/`, deeply tag all six dimensions, and persist the enriched JSON reports in those topic folders before pattern extraction begins.

Verify every parsed file contains at least one turn before continuing. The parser auto-detects these role markers:

| Format | Human marker | Assistant marker |
|--------|--------------|-----------------|
| Claude.ai export | `## **Human**` | `## **Claude**` |
| Bold variant | `## **User**` | `## **Assistant**` |
| Plain heading | `## Human` | `## Claude` or `## Assistant` |
| Colon format | `**Human:**` | `**Claude:**` or `**Assistant:**` |

Separator lines are ignored and nested Markdown headings inside assistant messages are preserved.

**If (c) — both sources:**

Run the .md import first (Step 2a for option b), then the JSONL extraction (Step 2a for option a). Merge all classified sessions before presenting topic counts. Sessions from different sources in the same topic are analyzed together.

**Step 2b — pattern extraction (per topic).** For each selected topic, follow Conversation Pattern Extraction below. Skip its source/topic prompt because Step 2 already established both. The contributor participates in the logic-jump confirmation gate; do not skip or rush it.

After pattern extraction finishes for all selected topics, note which topics had enough data to produce patterns (2+ patterns = sufficient).

### Conversation Pattern Extraction

This workflow consumes the tagged JSON reports produced by `how-to-dump-dialog` (including parsed Markdown imports) and writes two intermediate artifacts: recurring trigger→reaction patterns and user-confirmed logic jumps.

#### 1. Scan

For standalone analysis, ask for the source (`claude`, `codex`, or `md-import`) and a topic folder or `all`. Read report JSON files under `docs/dialog/<source>/<topic>/`; skip `topics.md`, `summary.md`, and other non-report files.

For every turn, load the user message, preceding assistant response, turn index, classification note, and all six tags (`bloom`, `depth`, `probe`, `presup`, `discourse`, `mechanism`). Treat classifier notes as evidence when a tag's intent is not obvious.

#### 2. Extract recurring patterns

A pattern is a **trigger signature → reaction pattern** pair. Triggers include starting questions and assistant outputs, choices, errors, or results that provoke the next user turn. Reactions combine the six-dimensional tag profile, action taken, and a natural-language summary.

Cluster turns across sessions when at least 3 of these 4 discriminating dimensions match: `bloom`, depth level (ignore the subcategory), `discourse`, and `mechanism`. Record only patterns appearing in at least two sessions. Name each with a descriptive verb phrase and include:

```markdown
### Pattern: <name>
**Trigger:** <what provokes it>
**Reaction:** <what the user does>
**Tag profile:** `bloom:X` `depth:Y/Z` `discourse:X` `mechanism:X`
**Frequency:** N occurrences across M sessions
**Examples:** <session/turn, user message, and one-line outcome>
```

#### 3. Detect and confirm logic jumps

A logic jump is not a direct response to the preceding assistant message: it introduces a new angle, catches a hidden gap, or connects distant concepts. Candidate signals include an uninvited assumption/evidence probe, exploration/debugging without an error prompt, a sudden jump to analyze/evaluate/create, a new constraint, or an unusually cross-domain starting question.

Curate only the 5–12 most valuable candidates relative to the topic: those that improved the outcome, expose a transferable insight, or reveal genuinely non-obvious reasoning. Discard routine scope corrections and obvious next steps.

Present one candidate at a time. On the first candidate from a session, summarize that session. Then show the preceding assistant context, the user's full message, why it is surprising, and three substantively different hypotheses plus Skip and a write-in option. Express hypotheses as causality chains using `+` for combined observations and `=>` for inference, for example:

```text
fixed a bug + responsibilities are tangled => root cause is architectural => separate them
```

Record the selected chain or the user's own explanation. Never batch the confirmation gate.

#### 4. Write analysis artifacts

Write to `docs/dialog/<source>/<topic>/` (or `<source>/all/`):

- `thinking-pattern.md` — source/topic, sessions analyzed, pattern count, patterns grouped by category, examples, and distribution summary.
- `master-thinking.md` — each confirmed jump's context, user question, confirmed causal chain, and a self-interview prompt asking what connected the context to the question.

Do not delete or move the underlying session JSON. Step 3 reads its `presup` tags directly for blind-spot analysis.

### Step 3 — Synthesize Portrait

For each topic with sufficient data, generate the thinking style sections of the profile.

**For each topic section, produce these 5 subsections:**

#### Cognitive Style
What bloom levels dominate? How quickly does depth escalate?
- **Derived from:** bloom + depth distributions across patterns

#### Attention Patterns
What does this person notice and react to?
- **Derived from:** high-frequency trigger-reaction patterns

#### Reasoning Strengths
Where does this person's thinking shine?
- **Derived from:** logic jumps (causality chains reveal reasoning style)

#### Conversation Dynamics
How does this person steer conversations?
- **Derived from:** discourse + mechanism distributions across patterns

#### Potential Blind Spots
What does this person *not* do? Frame constructively — these are tendencies, not flaws.
- **Derived from:** absent or rare tags across patterns, plus per-turn `presup` tags from the how-to-dump-dialog JSON files

For presup-derived blind spots: read the per-turn `presup` tags directly from the session JSON files in `docs/dialog/<source>/<topic>/`. Count non-sound presuppositions. If a specific presup issue appears 3+ times across sessions, generate a directive about it.

**Directive rules:**

Each subsection contains a narrative paragraph followed by directives:

```markdown
**As this advisor:** <how to behave when role-playing this person>
**Evidence:** <pattern or jump reference>
```

- **5–15 directives per topic section.** Fewer than 5 = data too thin (warn contributor).
- Every directive must be grounded in at least one pattern or logic jump. No speculative directives.
- Directives describe how the advisor **would behave**, not what a mentor should do:
  - Good: "As this advisor, challenge naming inconsistencies immediately."
  - Bad: "Be precise with terminology around this user."
- Blind spot directives describe tendencies authentically:
  - Good: "As this advisor, you tend to follow reasoning chains without pausing for empirical evidence. Role-play this authentically — but if asked for evidence, be honest about what you're inferring vs. what's established."

### Step 4 — Output

**Compute the advisor slug:** lowercase, hyphenated name (e.g., `jin-guo-liu`).

**Write the profile** to `advisors/<slug>/profile.md`:

```markdown
# <Full Name>

## Background

- **Field:** <field and subfields>
- **Key themes:** <research themes>
- **Technical skills:** <skills>
- **Notable contributions:** <contributions>
- **Generated:** <date>

## Publication Sources

- **Homepage:** <url or omit section if unknown>
- **Scholar/ORCID/DBLP/arXiv:** <url list or omit section if unknown>

## Voice

- **Language:** <language or omit section if unknown>
- **edge-tts:** <voice id or omit section if unknown>

## Thinking Style: <topic>

### Cognitive Style
<narrative>
**As this advisor:** <directive>
**Evidence:** <reference>

### Attention Patterns
...

### Reasoning Strengths
...

### Conversation Dynamics
...

### Potential Blind Spots
...
```

**Update the advisor index** at `advisors/index.md` — add or update a row for this contributor:

```markdown
| <Name> | <Field> | <Top 2-3 strengths> | <topic1, topic2, ...> |
```

If `advisors/index.md` does not exist, create it with header:
```markdown
# Advisor Library

| Name | Field | Strengths | Topics |
|------|-------|-----------|--------|
```

**Present to contributor for review** after writing:
> Your advisor profile is ready at `advisors/<slug>/profile.md`. Please review it — you can edit anything before it's shared. The raw conversation data stays in `docs/dialog/` (gitignored) and is never included in the profile.

### Updating an Existing Profile

When run on a contributor who already has a profile:

1. Read the existing profile
2. Preserve the Background section (unless the contributor provides updated info)
3. Replace or add topic sections based on new pattern-extraction output
4. Keep existing topic sections that weren't re-analyzed
5. Update the index row
6. Preserve or refresh `Publication Sources` and `Voice` if the contributor provided new information
