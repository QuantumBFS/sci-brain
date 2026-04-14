---
name: import-dialog
description: Import .md dialog files (Claude.ai exports, custom markdown conversations) to create or update advisor profiles. Use when the user wants to import a conversation file, update an advisor with new dialog data, or add .md chat history to the advisor library. Invoked with /import-dialog.
---

# Import Dialog — Update Advisor from .md Files

Import exported markdown dialog files and use them to create or update an advisor profile through the conversation-dump and soul-extraction pipeline.

## Phase 1 — Specify Inputs

Ask the user for:

1. **File path(s):** One or more `.md` dialog files to import. Accept glob patterns (e.g., `docs/*.md`).
2. **Target advisor:** An existing advisor slug (from `advisors/index.md`) or a new advisor name. If new, also gather background info (field, themes, skills) for the profile header.

## Phase 2 — Parse and Store

Run the bundled parser to convert `.md` files into standard JSON turns:

```bash
python3 <skill-base-dir>/../conversation-dump/parse_md_dialog.py parse <file.md>
```

For multiple files:

```bash
python3 <skill-base-dir>/../conversation-dump/parse_md_dialog.py batch <directory> --outdir docs/dialog/md-import/raw/
```

Save JSON outputs to `docs/dialog/md-import/raw/`. Verify each file parsed correctly (non-zero turns).

## Phase 3 — Classify and Analyze

Follow `conversation-dump` Phases 2–3:

1. **Classify** each session into a topic using the standard taxonomy: `skill-design`, `debugging`, `documentation`, `refactoring`, `feature-implementation`, `paper-review`, `research-brainstorming`, `data-analysis`, `system-design`, `testing`, `code-review`, `literature-survey`, `writing`, `automated`, `other`.

2. Move classified sessions to `docs/dialog/md-import/<topic>/`.

3. Present topic counts to the user. Ask which topics to analyze in depth.

4. **Deep analysis:** For each selected topic, tag every user message across the six dimensions (`bloom`, `depth`, `probe`, `presup`, `discourse`, `mechanism`). Save enriched JSON to `docs/dialog/md-import/<topic>/`.

## Phase 4 — Soul Extraction

For each selected topic, follow `soul-extraction` Phases 2–4:

1. **Extract patterns:** Identify trigger→reaction pairs. Cluster similar turns (3-of-4 dimension match). Record patterns with frequency and examples.

2. **Detect logic jumps:** Find user messages that are not direct responses to the assistant's prior turn. Curate the 5–12 most valuable. Present each candidate to the user for confirmation with causality chain options.

3. **Output:** Write `thinking-pattern.md` and `master-thinking.md` to `docs/dialog/md-import/<topic>/`.

## Phase 5 — Update Advisor Profile

Read the target advisor's existing `advisors/<slug>/profile.md`.

**If advisor exists:**
- Preserve the Background section (unless user provides updates).
- For each topic with sufficient data (2+ patterns), generate the five thinking-style subsections: Cognitive Style, Attention Patterns, Reasoning Strengths, Conversation Dynamics, Potential Blind Spots.
- Add new topic sections or replace existing ones that were re-analyzed.
- Keep existing topic sections that were not re-analyzed.

**If advisor is new:**
- Create `advisors/<slug>/profile.md` with Background + topic sections.
- Create `advisors/<slug>/` directory.

**Update `advisors/index.md`** — add or update the row for this advisor.

Present the updated profile to the user for review:
> Your advisor profile has been updated at `advisors/<slug>/profile.md`. The new analysis added/updated the following topic sections: [list]. Please review — raw dialog data stays in `docs/dialog/md-import/` and is not included in the profile.

## Supported .md Formats

The parser (`parse_md_dialog.py`) auto-detects these role marker patterns:

| Format | Human marker | Assistant marker |
|--------|-------------|-----------------|
| Claude.ai export | `## **Human**` | `## **Claude**` |
| Bold variant | `## **User**` | `## **Assistant**` |
| Plain heading | `## Human` | `## Claude` or `## Assistant` |
| Colon format | `**Human:**` | `**Claude:**` or `**Assistant:**` |

Messages are separated by `---` lines (ignored during parsing). Nested markdown headings within assistant responses are preserved as content.
