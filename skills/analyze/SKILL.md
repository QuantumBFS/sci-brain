---
name: analyze
description: Use when analyzing a conversation session's question patterns — extracts dialog from Claude Code or Codex CLI history, classifies each user question across 6 academic dimensions (Bloom's cognitive level, Graesser question depth, Paul & Elder reasoning probe, Walton presupposition quality, Long & Sato discourse function, Graesser generation mechanism), and outputs a tagged Q&A report
---

## Dialog Analysis

Analyze a conversation session to classify every user question across 6 academic dimensions and produce a tagged Q&A report.

### Phase 1 — Session Selection

Run the extraction script to list available sessions from both sources:

```bash
python skills/analyze/extract_dialog.py list --source claude
python skills/analyze/extract_dialog.py list --source codex
```

Present the combined results as a numbered menu. Ask the user to pick a session.

Once selected, extract it:

```bash
python skills/analyze/extract_dialog.py extract --source <source> --session <id>
```

Read the JSON output. It contains `turns[]` with `user` and `assistant` text for each exchange.

### Phase 2 — Question Analysis

For each turn, analyze the user message. If the message is not a question (e.g., "yes", "A", single-word confirmations, option selections), mark it `[non-question]` and skip tagging.

If a single message contains multiple distinct questions, tag each separately as sub-items (Q1a, Q1b, etc.).

For each question, classify across all 6 dimensions using the criteria in `docs/survey-question-classification.md` and the design spec at `docs/superpowers/specs/2026-03-28-analyze-dialog-design.md` (see "Classification Criteria" section for decision rules, tie-breaking rules, and examples).

**The 6 dimensions:**

| Prefix | Dimension | Tags |
|--------|-----------|------|
| `bloom:` | Cognitive Level | remember, understand, apply, analyze, evaluate, create |
| `depth:` | Question Depth | shallow/intermediate/deep + Graesser category (e.g., `deep/causal-antecedent`) |
| `probe:` | Reasoning Probe | clarification, assumption-probe, evidence-probe, perspective, implication, meta-question, none |
| `presup:` | Presupposition Quality | sound, existential-gap, factive-gap, loaded, complex, ambiguous, missing-context, leading |
| `discourse:` | Discourse Function | referential, display, rhetorical, confirmation-check, clarification-request, indirect-request |
| `mechanism:` | Generation Mechanism | knowledge-deficit, common-ground, action-coordination, conversation-control, exploration, debugging, undetermined |

For any presupposition issue or non-obvious classification, add a brief **Note** explaining the reasoning.

### Phase 3 — Output

Create the output directory if it doesn't exist:

```bash
mkdir -p docs/dialog
```

Write the analysis to `docs/dialog/YYYY-MM-DD-HHMMSS-<topic>.md` where:
- Timestamp is the current time
- Topic is a 2-3 word slug inferred from the conversation content

Format each turn as:

```markdown
## Turn N

**Q:** <user question text>

> **Tags:** `bloom:X` `depth:Y/Z` `probe:X` `presup:X` `discourse:X` `mechanism:X`
>
> **Note:** <explanation if non-obvious>

**A:** <assistant response, truncated>
```

For `[non-question]` turns:

```markdown
## Turn N `[non-question]`

**User:** "yes"

**A:** <assistant response, truncated>
```

End with a **Summary** section containing:
- Total questions analyzed (count per tagged question, sub-items count separately, non-questions excluded)
- Distribution for each dimension
- Presupposition issues found (list turn numbers)
- Key observation (1-2 sentence insight about the user's questioning pattern)
