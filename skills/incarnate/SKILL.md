---
name: incarnate
description: Use when onboarding a contributor as an advisor — guides them through providing their background and conversation history, runs conversation-dump and soul-extraction, then synthesizes a named advisor profile for the ideas skill's advisor library
---

## Advisor Profile Generation

Onboard a contributor and create a named advisor profile. The profile captures how a real person thinks — their cognitive style, attention patterns, reasoning strengths, and conversation dynamics — so the ideas skill can launch them as a subagent collaborator rather than a thin inline persona.

### Step 1 — Personal Profile

Ask the contributor to provide their academic/professional background:

- **(a)** Tell me yourself (field, experience, what you've worked on)
- **(b)** Zotero library — follow the `researchstyle` skill instructions (`skills/researchstyle/SKILL.md`) to index publications
- **(c)** Google Scholar profile — follow the `researchstyle` skill instructions to index publications

From the response, extract:
- **Name** (ask if not provided)
- **Field and subfields**
- **Key research themes**
- **Technical skills**
- **Notable contributions**
- **Publication sources** if available (homepage, Google Scholar, ORCID, DBLP, arXiv author page)
- **Voice preference** if available (spoken language, accent, or preferred `edge-tts` voice)

Hold this information for Step 4.

### Step 2 — Conversation Analysis

Ask the contributor to specify their conversation source:

- **(a)** Claude Code / Codex CLI (JSONL session logs)
- **(b)** Exported `.md` dialog files (Claude.ai web exports, custom markdown conversations)
- **(c)** Both — import `.md` files first, then scan JSONL logs, merge all data

Run the analysis pipeline based on the chosen source:

**If (a) — JSONL sessions:**

**Step 2a — conversation-dump.** Read `skills/conversation-dump/SKILL.md` and follow Phases 1–4. This extracts all sessions, classifies them by topic, performs deep 6-dimension analysis, and outputs tagged JSON reports. At the end of Phase 2, the contributor selects which topics to analyze in depth.

**If (b) — .md dialog files:**

**Step 2a — parse .md files.** Ask the contributor for the file path(s). Run the markdown parser:

```bash
python3 skills/conversation-dump/parse_md_dialog.py parse <file.md>
```

For multiple files in a directory:

```bash
python3 skills/conversation-dump/parse_md_dialog.py batch <directory> --outdir docs/dialog/md-import/raw/
```

Save JSON outputs to `docs/dialog/md-import/raw/`. Then follow conversation-dump Phases 2–3 (classify by topic, deep 6-dimension analysis) on the parsed JSON files.

**If (c) — both sources:**

Run the .md import first (Step 2a for option b), then the JSONL extraction (Step 2a for option a). Merge all classified sessions before presenting topic counts. Sessions from different sources in the same topic are analyzed together.

**Step 2b — soul-extraction (per topic).** For each topic the contributor selected, read `skills/soul-extraction/SKILL.md` and follow Phases 1–4. Skip soul-extraction's Phase 1 source/topic prompt — you already know both from conversation-dump. Pass the source and topic directly. The contributor participates in the logic jump confirmation gate. Do not skip or rush it.

After soul-extraction finishes for all selected topics, note which topics had enough data to produce patterns (2+ patterns = sufficient).

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
- **Derived from:** absent or rare tags across patterns, plus per-turn `presup` tags from the conversation-dump JSON files

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
3. Replace or add topic sections based on new soul-extraction output
4. Keep existing topic sections that weren't re-analyzed
5. Update the index row
6. Preserve or refresh `Publication Sources` and `Voice` if the contributor provided new information
