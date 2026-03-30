---
name: soul-extraction
description: Use when extracting conversation patterns and logic jumps from tagged dialog reports — reads /conversation-dump output, clusters trigger→reaction pairs into thinking-pattern.md, detects logic jumps with user confirmation for master-thinking.md
---

## Soul Extraction

Extract conversation patterns and logic jumps from tagged dialog reports, producing a thinking profile and a self-interview document.

### Phase 1 — Scan

Ask the user to specify:
- **Source:** claude or codex
- **Topic:** a specific topic folder name (e.g., `skill-design`), or `all`

Read all `.json` report files in `docs/dialog/<source>/<topic>/` (or all topic folders if "all"). Skip non-report files (`topics.md`, `summary.md`).

Each JSON file follows the conversation-dump output schema:

```json
{
  "turns": [
    {
      "index": 1,
      "user": "...",
      "assistant": "...",
      "tags": { "bloom": "...", "depth": "...", "probe": "...", "presup": "...", "discourse": "...", "mechanism": "..." },
      "note": "..."
    }
  ]
}
```

For each turn, extract:
- User message text (`user`)
- 6-dimension tags from `tags` object
- Assistant response (`assistant` — preceding context)
- Turn position (`index` — Turn 1 = starting question)
- Classification note (`note`) — if present, use it to understand non-obvious tag assignments. Notes explain why the classifier chose a tag that might seem wrong at face value (e.g., why a statement was tagged `probe:assumption-probe`). Factor notes into clustering and jump detection when they clarify intent.

### Phase 2 — Extract Patterns

A "pattern" is a pair: **trigger signature → reaction pattern**.

**Trigger signatures include:**
- **Starting questions** — Turn 1 messages (what the user brings unprompted)
- **Mid-conversation triggers** — assistant output, presented options, errors, or results that provoke the next user message

**Reaction pattern** is characterized by:
- The 6-dimension tag profile
- The action taken (select, command, evaluate, redirect, etc.)
- A natural-language summary

**Clustering:** Group turns with similar trigger→reaction profiles across sessions. Two turns are "similar" when **at least 3 of 4** discriminating dimensions match: `bloom`, `depth` (level only, ignoring sub-category), `discourse`, `mechanism`. A pattern must appear in 2+ sessions to be recorded.

Name each pattern with a descriptive verb phrase (e.g., "Fail-safe to human", "Redirect scope", "Challenge naming inconsistency").

**Pattern format:**

```markdown
### Pattern: <name>

**Trigger:** <description of what provokes this reaction>
**Reaction:** <what the user does>
**Tag profile:** `bloom:X` `depth:Y/Z` `discourse:X` `mechanism:X`
**Frequency:** N occurrences across M sessions
**Examples:**
- Session <id>, Turn N: "<user message>" → <one-line summary>
- Session <id>, Turn N: "<user message>" → <one-line summary>
```

### Phase 3 — Detect Logic Jumps

A "logic jump" is a user message that is NOT a direct response to what the assistant just said — it introduces a new angle, catches a hidden gap, or connects distant concepts.

**Detection heuristics (any suggest a candidate):**
- Tags show `probe:assumption-probe` or `probe:evidence-probe` when the assistant didn't invite scrutiny
- `mechanism` is `exploration` or `debugging` but the assistant didn't present an error or prompt
- `bloom` jumps from shallow (confirmations) to `analyze`/`evaluate`/`create` without the assistant asking a question
- User introduces a topic or constraint not mentioned in the prior assistant turn
- A starting question (Turn 1) that connects multiple domains or frames a problem unusually

**Curation:** Not every candidate is worth presenting. From all candidates, select the **5-12 most valuable** logic jumps. Value is judged **relative to the topic being analyzed** — e.g., if the topic is `skill-design`, evaluate jumps by how they improved skill writing; if `debugging`, by how they led to root-cause discovery.

Selection criteria:
- **Brought good outcomes for the topic** — the jump led to a better result in the domain being studied (e.g., better skill design, better code, better paper)
- **Introduced a transferable insight** — the reasoning pattern could improve future work in the same topic area
- **Revealed non-obvious reasoning** — the connection between context and question is genuinely surprising

Discard jumps that are routine (e.g., simple scope corrections, obvious next steps, bloom jumps that are just resuming after confirmations).

**User confirmation gate:** Present ONE curated candidate at a time with full context. When moving to a new session for the first time, start with a session summary:

> **Session:** <id> — <1-2 sentence summary of what this session was about>

Then present the candidate:

**Candidate logic jump** (Turn N)

> *Assistant:* <full or near-full text of what the assistant said before this turn>

> *You:* "<the user's full message>"

**Why this is a jump:** <explain what gap you detected — what about the prior context makes this message surprising or non-obvious as a next step>

**(A)** `<causality chain>`

**(B)** `<causality chain>`

**(C)** `<causality chain>`

**(D)** None of these — I'll explain

**(E)** Skip

The 3 guesses should be substantively different hypotheses about what the user was *actually thinking* — not surface restatements. Consider: hidden analogies, pattern recognition from other domains, latent dissatisfaction, architectural instincts, or unstated goals.

Express each guess in **causality form** using `+` (logical AND of observations/principles) and `=>` (implies). The `+` terms can appear anywhere in the chain — beginning, middle, or end. Keep it flexible and natural.
Examples:
- `"simple is good" principle + complex code => not good => should consider simpler approach`
- `fixed a bug => why did it exist? + responsibilities are tangled => orthogonalize`
- `design looks complete => dry-run in head + subagent is stateless => missing dependency`

If the user picks A/B/C, record that guess as the chain of thought. If D, the user provides their own explanation. If E, discard the candidate. Process candidates one at a time — do NOT batch.

### Phase 4 — Output

Write both files to `docs/dialog/<source>/<topic>/` (or `docs/dialog/<source>/all/` when topic is "all"):

**`thinking-pattern.md`:**

```markdown
# Thinking Patterns

- **Source:** <source>
- **Topic:** <topic or "all">
- **Sessions analyzed:** N
- **Patterns extracted:** M

## Category: <group name>

### Pattern: <name>
**Trigger:** ...
**Reaction:** ...
**Tag profile:** ...
**Frequency:** N across M sessions
**Examples:** ...

---

## Summary

- Total patterns: N
- Most frequent patterns: ...
- Dominant bloom levels: ...
- Dominant mechanisms: ...
```

**`master-thinking.md`:**

```markdown
# Master Thinking: Logic Jumps

- **Source:** <source>
- **Topic:** <topic or "all">
- **Logic jumps confirmed:** N

## Jump 1: <short title>

**Context:** <what the assistant just said, truncated>
**Your question:** <the actual user message>
**Chain of thought:** `<principle/observation> + <context> => <inference> => <action>`

> **Interview prompt:** "You were looking at [context]. Then you asked [question]. Walk me through what connected those — what were you actually thinking?"
```

If the user confirmed a guess (A/B/C) or provided their own explanation (D), fill the `Chain of thought:` field with it. The interview prompt is always generated — it serves as a self-interview anchor even when the chain is already filled.

### Note: Incarnate Integration

When soul-extraction is invoked as part of the `incarnate` skill's contributor onboarding (Step 2), control returns to incarnate after Phase 4 completes. Incarnate Step 3 then uses the outputs written here to synthesize an advisor profile. Do not invoke incarnate from here — incarnate drives the flow.

**Important:** Do not delete or move the session JSON files in `docs/dialog/<source>/<topic>/` after Phase 4. Incarnate reads them directly for presup-based blind spot analysis.
