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

Before running the examples, set `DOWNLOAD_REF_DIR` to the absolute directory of `how-to-download-ref`. Quote these variables as shown.


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

**Step 2a — export, then analyze.** If the contributor already has classified
dialog JSON, use it directly. Otherwise invoke `dump-chat-history` to select
harnesses and the start date first, passing through any choices already given.
It supports local harness histories and supplied Markdown/JSON exports. Request
an analysis handoff; a PDF is optional and should not be generated solely for
advisor synthesis.

Then read `skills/how-to-analyze-dialog/SKILL.md` and follow Phases 1–4: load the
export, classify sessions by topic, let the contributor select topics for deep
analysis, and persist the enriched JSON reports in the analysis workspace.
The raw transcript remains separate and unchanged. Retain assistant context for
trigger→reaction analysis and flag sessions that lack it.

**Step 2b — pattern extraction (per topic).** For each selected topic, follow Conversation Pattern Extraction below. Skip its source/topic prompt because Step 2 already established both. The contributor participates in the logic-jump confirmation gate; do not skip or rush it.

After pattern extraction finishes for all selected topics, note which topics had enough data to produce patterns (2+ patterns = sufficient).

### Conversation Pattern Extraction

This workflow consumes the tagged JSON reports produced by `how-to-analyze-dialog` (including parsed Markdown imports) and writes two intermediate artifacts: recurring trigger→reaction patterns and user-confirmed logic jumps.

#### 1. Scan

For standalone analysis, ask for the existing analysis workspace and a topic folder or `all`. Read report JSON files under `docs/dialog/analysis/<run-slug>/<topic>/`; skip `topics.md`, `summary.md`, and other non-report files.

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
- **Derived from:** absent or rare tags across patterns, plus per-turn `presup` tags from the how-to-analyze-dialog JSON files

For presup-derived blind spots: read the per-turn `presup` tags directly from the session JSON files in `docs/dialog/analysis/<run-slug>/<topic>/`. Count non-sound presuppositions. If a specific presup issue appears 3+ times across sessions, generate a directive about it.

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
