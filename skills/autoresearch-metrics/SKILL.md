---
name: autoresearch-metrics
description: Use when deriving score metrics for chosen autoresearch topics — for each topic in topics.md, identifies what "good" means as computable metrics, how each is computed and at what cost, and its gaming risks, then attaches an approved metrics block in-place. Stage 2 of the autoresearch pipeline.
---

# Autoresearch Metrics

Input: `<project>/topics.md` with `### Metrics` placeholders. Output: the
placeholders filled, per user approval. These metrics become the validator's
score function in stage 4, so gaming risks identified here turn into negative
controls there.

## Procedure

For each topic in `topics.md`, one at a time:

1. **Propose 2–5 candidate metrics.** For each, state:
   - **Definition** — the quantity, precisely enough to implement.
   - **Computation** — how it is computed and the per-attempt cost (must fit
     inside the topic's Cheap budget).
   - **Gaming risks** — how a candidate could score well while being wrong,
     trivial, or a lookup table; and what check would catch it.
2. **Classify** each as **primary** (enters the score function — usually one
   per topic, e.g. wall-clock speedup at verified-exact output) or **guard**
   (anti-gaming side condition, e.g. exactness on unseen instances, no
   hard-coded answers).
3. **User approves** the metric set per topic (`AskUserQuestion`; amendments
   welcome).
4. **Write in-place.** Fill the topic's `### Metrics` block: one bullet per
   metric — `**<name>** (primary|guard): definition; computation + cost;
   gaming risks`.
5. **Advance state.** When every chosen topic has an approved metrics block,
   set `stage: db` in `research/STATE.md`.
