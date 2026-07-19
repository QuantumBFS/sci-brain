---
name: autoresearch-topics
description: Use when choosing research topics within a domain that suit autoresearch and defining their score metrics — brainstorms candidates, scores each on machine-checkable success, cheap per-attempt evaluation, iteration headroom, and publishability, lets the user pick, then derives primary/guard metrics (with computation cost and gaming risks) for each chosen topic and writes everything to topics.md. Stage 1 of the autoresearch pipeline; invoked via the autoresearch dispatcher or directly with a domain.
---

# Autoresearch Topics

Input: a domain from the user. Output: `<project>/topics.md` — chosen topics
*with* their metrics — plus a STATE.md stage advance. A good autoresearch
topic is one where a validator — not a human — can tell whether an attempt
succeeded; the metrics defined here become that validator's score function in
the validator stage, so gaming risks identified here turn into negative
controls there.

## Procedure

1. **Clarify the domain** with at most one question, only if it is too broad
   to enumerate concrete topics (e.g. "quantum computing" yes, "exact
   distance computation for CSS codes" no).
2. **Generate 5–10 candidates.** Ground each with WebSearch and any available
   paper MCP servers; every candidate needs at least one recent reference
   showing the problem is open. No candidate from memory alone.
3. **Score each candidate 1–5** on the four suitability criteria, one-line
   justification each:
   - **Checkable** — success is machine-checkable; a validator can score an
     attempt with no human judgment.
   - **Cheap** — one attempt evaluates in minutes on local hardware, not days.
   - **Headroom** — the search space supports tens-to-hundreds of genuinely
     distinct attempts, not three obvious ones.
   - **Publishable** — a clearly stated bar exists whose crossing is a
     publishable result.
   Present the scored table; flag any candidate scoring ≤2 on Checkable or
   Cheap as unsuitable and say why.
4. **User picks** topics via `AskUserQuestion` (multi-select) from the table.
5. **Derive metrics** for each chosen topic, one at a time. Propose 2–5
   candidate metrics; for each, state:
   - **Definition** — the quantity, precisely enough to implement.
   - **Computation** — how it is computed and the per-attempt cost (must fit
     inside the topic's Cheap budget).
   - **Gaming risks** — how a candidate could score well while being wrong,
     trivial, or a lookup table; and what check would catch it.
   Classify each as **primary** (enters the score function — usually one per
   topic, e.g. wall-clock speedup at verified-exact output) or **guard**
   (anti-gaming side condition, e.g. exactness on unseen instances, no
   hard-coded answers). The user approves the metric set per topic
   (`AskUserQuestion`; amendments welcome).
6. **Write `topics.md`.** One `## <topic title>` section per chosen topic:
   problem statement, why autoresearch fits (the four scores), key references
   (title + arXiv ID/DOI), and a `### Metrics` block — one bullet per
   approved metric: `**<name>** (primary|guard): definition; computation +
   cost; gaming risks`.
7. **Advance state.** When every chosen topic has an approved metrics block,
   set `stage: db` in `research/STATE.md` (create it from
   `skills/autoresearch/references/state-schema.md` if the dispatcher has
   not already).
