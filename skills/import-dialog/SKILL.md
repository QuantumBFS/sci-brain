---
name: import-dialog
description: Import .md dialog files (Claude.ai exports, custom markdown conversations) to create or update advisor profiles. Use when the user wants to import a conversation file, update an advisor with new dialog data, or add .md chat history to the advisor library. Invoked with /import-dialog.
---

# Import Dialog

Import exported markdown dialog files, convert them to the standard dialog JSON format, then hand off to the existing advisor-profile pipeline. This skill is intentionally a thin wrapper around `conversation-dump`, `soul-extraction`, and `incarnate` so their taxonomies and profile rules stay single-sourced.

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

Follow `conversation-dump` Phases 2–3 on `docs/dialog/md-import/raw/`:
- Use the topic taxonomy from `conversation-dump` only.
- Move classified sessions to `docs/dialog/md-import/<topic>/`.
- Present topic counts and ask which topics to analyze deeply.
- Save enriched JSON back to `docs/dialog/md-import/<topic>/`.

## Phase 4 — Soul Extraction

For each selected topic, follow `soul-extraction` Phases 2–4 and write `thinking-pattern.md` + `master-thinking.md` to `docs/dialog/md-import/<topic>/`.

## Phase 5 — Update Advisor Profile

Use `incarnate` Step 3–4 to synthesize or update `advisors/<slug>/profile.md` from the new `soul-extraction` outputs. Preserve existing topic sections that were not re-analyzed, and update `advisors/index.md`.

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
