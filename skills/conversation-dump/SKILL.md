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

**Topic taxonomy (closed set):**

| Slug | Description |
|------|-------------|
| `skill-design` | Designing or refining skill definitions |
| `brainstorming` | Research ideation, /ideas sessions |
| `code-review` | Reviewing code or PRs |
| `debugging` | Fixing bugs, diagnosing failures |
| `documentation` | Writing or editing docs, READMEs |
| `ci-cd` | CI/CD pipelines, GitHub Actions, deployment |
| `refactoring` | Restructuring existing code |
| `research` | Literature search, paper discussion |
| `plugin-management` | Plugin install, config, marketplace |
| `slide-creation` | Presentations, Typst/LaTeX slides |
| `paper-review` | Reviewing or analyzing academic papers |
| `testing` | Writing or running tests |
| `configuration` | Settings, environment, permissions |
| `project-setup` | Scaffolding, init, dependencies |
| `automated` | No real human messages (system/skill invocations only) |
| `other` | Does not fit any above — agent must propose a slug |

**Topic classification rules:**
- Read the user messages in each session (first 3-5 turns are usually enough)
- Assign ONE slug from the taxonomy above
- Only use `other` when no existing slug fits; include a proposed new slug and one-line description
- After all agents return, review `other` entries: merge into existing slugs where possible, or promote a new slug if 3+ sessions share it

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

For full classification criteria, decision rules, tie-breaking rules, and examples, see `docs/plans/classification-criteria.md`.

**Quick classification guidelines:**
- When two `bloom` levels seem equally valid, pick the higher one (the message is *at least* that complex)
- `depth` always includes a Graesser sub-category after the slash (e.g., `deep/causal-antecedent`, `shallow/verification`)
- `probe:none` is the default for non-probing messages — do not force a probe type
- `presup:sound` is the default for well-formed messages — only flag issues when genuinely present
- When `mechanism` is ambiguous between `exploration` and `debugging`, check whether the user has a specific failure in mind (debugging) or is open-ended (exploration)

**Classifying non-question messages:** Commands, confirmations, and statements carry the same dimensions:
- A command like "fix the tests" → `bloom:apply`, `depth:deep/instrumental`, `probe:none`, `presup:sound`, `discourse:indirect-request`, `mechanism:action-coordination`
- A confirmation like "yes" or "option A" → `bloom:remember`, `depth:shallow/verification`, `probe:none`, `presup:sound`, `discourse:confirmation-check`, `mechanism:common-ground`
- Feedback like "no, not that approach" → `bloom:evaluate`, `depth:deep/judgmental`, `probe:none`, `presup:sound`, `discourse:referential`, `mechanism:conversation-control`

For any presupposition issue or non-obvious classification, add a brief **Note** explaining the reasoning.

### Phase 4 — Output

**Per-session reports:** Write one JSON file per session to `docs/dialog/<source>/<topic>/<session-id>.json`.

Schema:

```json
{
  "source": "<claude|codex>",
  "session_id": "<id>",
  "topic": "<topic slug>",
  "timestamp": "<ISO 8601>",
  "turns": [
    {
      "index": 1,
      "user": "<user message text>",
      "assistant": "<assistant response, truncated>",
      "tags": {
        "bloom": "analyze",
        "depth": "deep/causal-antecedent",
        "probe": "assumption-probe",
        "presup": "sound",
        "discourse": "referential",
        "mechanism": "exploration"
      },
      "note": "<explanation if non-obvious, otherwise null>"
    }
  ]
}
```

For any presupposition issue or non-obvious classification, populate the `note` field for that turn.

**Aggregate report:** After all sessions are processed, write `docs/dialog/<source>/summary.md` with:
- Total sessions analyzed (by topic, and how many were skipped as automated/empty)
- Combined message count across all sessions
- Aggregate distribution for each dimension (counts + percentages)
- Per-topic breakdown (which topics show which patterns)
- Presupposition issues found (session + turn numbers)
- Top patterns (2-3 sentences characterizing the user's overall conversation style across sessions)
