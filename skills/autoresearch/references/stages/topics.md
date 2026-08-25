# Stage 1: Topics

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
   - **Diverse strategies** — many genuinely different *kinds* of approach
     could plausibly work (different mechanisms, not different parameter
     settings of one method), and it is not known in advance which one
     will. A topic whose only freedom is a parameter sweep or a fixed,
     enumerable search space scores low here even if that space is large.
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
6. **Define the acceptance gate** for each chosen topic — mandatory, never
   skipped or deferred to a later stage. The **user must state** the
   condition under which a result counts as *a solid research output that
   meets the bar of publication*: primary metric, threshold, the instance
   families it must hold on, and the baseline it must beat. A vague gate
   ("significantly better", "state of the art-ish") is not acceptable —
   every term must be checkable by the future validator.

   Then **red-team the gate before accepting it**: list the concrete ways
   an attempt could satisfy it while being wrong, trivial, or
   unpublishable. Check at least: overfitting to visible dev instances;
   lookup tables / hard-coded answers; a baseline too weak to be a
   publishable comparison; a threshold at or below already-published
   results (verify against the step-2 references); an instance family
   narrow or easy enough that the claim doesn't generalize; the metric
   diverging from the quantity the paper would actually claim; and the
   topic's own gaming risks from step 5. For each hack, name the
   strengthening that closes it (holdout family, stronger baseline, raised
   threshold, added guard metric, wider instances).

   If any hack survives, the gate is **not strict enough**: present the
   surviving hacks with their strengthenings and ask the user to strengthen
   the gate (`AskUserQuestion` — the options are the strengthenings, never
   an "accept as is"). Iterate until no listed hack survives, then get the
   user's **explicit confirmation** of the final gate (`AskUserQuestion`) —
   the gate is never inferred, defaulted, or assumed.
7. **Write `topics.md`.** One `## <topic title>` section per chosen topic:
   problem statement, why autoresearch fits (the four scores), key references
   (title + arXiv ID/DOI), a `### Metrics` block — one bullet per
   approved metric: `**<name>** (primary|guard): definition; computation +
   cost; gaming risks` — and a `### Acceptance gate` block: the
   user-confirmed condition verbatim, followed by one bullet per considered
   hack: `**<hack>** — closed by <strengthening>`. These hacks become
   topic-specific negative controls at the validator stage.
8. **Advance state.** When every chosen topic has an approved metrics block
   and a user-confirmed acceptance gate, set `stage: db` in
   `research/STATE.md` (create it from
   `../state-schema.md` if the dispatcher has
   not already).
