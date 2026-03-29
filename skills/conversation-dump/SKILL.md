---
name: conversation-dump
description: Use when analyzing conversation patterns — extracts dialog from Claude Code or Codex CLI history, classifies each user message across 6 academic dimensions (Bloom's cognitive level, Graesser question depth, Paul & Elder reasoning probe, Walton presupposition quality, Long & Sato discourse function, Graesser generation mechanism), and outputs tagged dialog reports
---

## Dialog Analysis

Analyze all conversation sessions from a chosen source (Claude Code or Codex CLI) in three phases: batch extraction, topic classification, and deep 6-dimension analysis.

### Phase 1 — Extract

Ask the user to choose a source: **claude** or **codex**.

List and extract ALL sessions in batch using the Python script:

```bash
python skills/conversation-dump/extract_dialog.py list --source claude --project all
python skills/conversation-dump/extract_dialog.py list --source codex
```

Extract every listed session and save the JSON output to a staging directory:

```bash
mkdir -p docs/dialog/<source>/extracted
python skills/conversation-dump/extract_dialog.py extract --source <source> --session <id> > docs/dialog/<source>/extracted/<session-id>.json
```

Run extractions in parallel (batch shell commands). Skip sessions that yield 0 user turns after filtering.

### Phase 2 — Classify by Topic

Dispatch fast subagents (model: haiku) in parallel to classify each extracted session by conversation topic. Each agent receives a batch of ~20 extracted JSON files and returns a topic label for each.

**Topic classification rules:**
- Read the user messages in each session (first 3-5 turns are usually enough)
- Assign ONE topic slug (2-3 words, lowercase, hyphenated) that captures the primary activity
- Common topics include but are not limited to: `skill-design`, `brainstorming`, `code-review`, `debugging`, `documentation`, `ci-cd`, `refactoring`, `research`, `plugin-management`, `slide-creation`, `paper-review`, `testing`
- If a session is purely automated (no real human messages, only skill invocations or system preambles), label it `automated`
- If the topic doesn't fit any common label, create a new descriptive slug

After all agents return, organize files into topic folders:

```bash
mkdir -p docs/dialog/<source>/<topic>
mv docs/dialog/<source>/extracted/<session-id>.json docs/dialog/<source>/<topic>/
```

Write a topic index to `docs/dialog/<source>/topics.md`:

```markdown
# Topic Index

| Topic | Sessions | Description |
|-------|----------|-------------|
| skill-design | 12 | Designing or refining skill definitions |
| brainstorming | 8 | Research ideation using /ideas |
| ... | ... | ... |
| **Total** | **N** | |
```

Present the topic index to the user and ask which topics to analyze in depth (or "all").

### Phase 3 — Deep Analysis

For each session in the selected topics, classify ALL user messages across 6 dimensions. Use parallel agents (batch ~5 sessions per agent).

**The 6 dimensions:**

| Prefix | Dimension | Tags |
|--------|-----------|------|
| `bloom:` | Cognitive Level | remember, understand, apply, analyze, evaluate, create |
| `depth:` | Question Depth | shallow/intermediate/deep + Graesser category (e.g., `deep/causal-antecedent`). For non-questions: use the depth of the cognitive task implied by the message. |
| `probe:` | Reasoning Probe | clarification, assumption-probe, evidence-probe, perspective, implication, meta-question, none |
| `presup:` | Presupposition Quality | sound, existential-gap, factive-gap, loaded, complex, ambiguous, missing-context, leading |
| `discourse:` | Discourse Function | referential, display, rhetorical, confirmation-check, clarification-request, indirect-request |
| `mechanism:` | Generation Mechanism | knowledge-deficit, common-ground, action-coordination, conversation-control, exploration, debugging, undetermined |

For classification criteria, decision rules, tie-breaking rules, and examples, see `docs/survey-question-classification.md` and `docs/superpowers/specs/2026-03-28-analyze-dialog-design.md` (Classification Criteria section).

**Classifying non-question messages:** Commands, confirmations, and statements carry the same dimensions:
- A command like "fix the tests" → `bloom:apply`, `depth:deep/instrumental`, `probe:none`, `presup:sound`, `discourse:indirect-request`, `mechanism:action-coordination`
- A confirmation like "yes" or "option A" → `bloom:remember`, `depth:shallow/verification`, `probe:none`, `presup:sound`, `discourse:confirmation-check`, `mechanism:common-ground`
- Feedback like "no, not that approach" → `bloom:evaluate`, `depth:deep/judgmental`, `probe:none`, `presup:sound`, `discourse:referential`, `mechanism:conversation-control`

For any presupposition issue or non-obvious classification, add a brief **Note** explaining the reasoning.

### Phase 4 — Output

**Per-session reports:** Write one file per session to `docs/dialog/<source>/<topic>/<session-id>.md`.

Format each turn as:

```markdown
## Turn N

**Q:** <user question text>

> **Tags:** `bloom:X` `depth:Y/Z` `probe:X` `presup:X` `discourse:X` `mechanism:X`
>
> **Note:** <explanation if non-obvious>

**A:** <assistant response, truncated>
```

End each per-session report with a **Summary** section containing:
- Total messages analyzed (sub-items count separately)
- Distribution for each dimension
- Presupposition issues found (list turn numbers)
- Key observation (1-2 sentence insight about the user's conversation pattern)

**Aggregate report:** After all sessions are processed, write `docs/dialog/<source>/summary.md` with:
- Total sessions analyzed (by topic, and how many were skipped as automated/empty)
- Combined message count across all sessions
- Aggregate distribution for each dimension (counts + percentages)
- Per-topic breakdown (which topics show which patterns)
- Presupposition issues found (session + turn numbers)
- Top patterns (2-3 sentences characterizing the user's overall conversation style across sessions)
