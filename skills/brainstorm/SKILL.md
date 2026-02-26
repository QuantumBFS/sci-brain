---
name: brainstorm
description: Use when brainstorming research ideas from a survey report — runs a harsh-but-constructive human interview in parallel with AI creative lenses (Combiner, Inverter, Transplanter, Bottleneck-breaker), then merges all ideas
---

## Step 2 — Brainstorm (human first, then AI)

Human and AI brainstorm independently and in parallel — neither side sees the other's ideas, so there is no anchoring in either direction. All ideas enter critique on equal footing.

**Step 2a — Human brainstorm + AI brainstorm (launched simultaneously):**

Present the survey report, then start the human brainstorm conversation while launching AI subagents in the background.

**AI subagents run in parallel with the human conversation.** Each receives only the survey report from Step 1 — **not** the human's ideas. This keeps both sides independent.

**Human brainstorm conversation (5+ questions, one at a time):**

A harsh but constructive interview. Push the human from vague to concrete, from weak to strong. Be direct — demand specifics, push back on hand-waving. Stop only when the human says stop.

**Formatting:** Prefix every brainstorm question with `>>>` so it stands out in the CLI. Example: `>>> What specifically is new here?`

**Phase 1 — Open.** Get the human talking:

> `>>> Based on what we've found, what directions interest you? Even a vague hunch is fine — we'll sharpen it together.`

**Phase 2 — Explore.** Dig into whatever the human gravitates toward. Connect their instincts to the survey:

- `>>> You mentioned X — what specifically about that excites you?`
- `>>> That connects to [paper Y] which found [Z] — does that change your thinking?`
- If stuck, throw survey findings to provoke a reaction: `>>> The survey found [method X] failed because [Y] — does that suggest an angle?`

**Phase 3 — Sharpen.** Once a direction emerges, pressure-test it. Use Polya and Lei Wang criteria to force clarity:

- *What's new?* — `>>> What specifically is new here? What is the unknown, the data, the conditions?` (Polya)
- *Why now?* — `>>> Why can this be solved now? What changed — new data, methods, compute, theory?` (Lei Wang)
- *Why you?* — `>>> Why hasn't anyone done this before? What's your unique advantage?` (Lei Wang)
- *What's the plan?* — `>>> Do you know a related problem with a known solution? Can you adapt it?` (Polya)
- *What's the test?* — `>>> What's the minimal experiment? What would you measure?` (Polya)
- *What could go wrong?* — `>>> What has to be true for this to work? Which assumption worries you most?`

**Phase 4 — Pivot if needed.** If an idea is weak, don't kill it — redirect: `>>> What if instead of [weak version], you tried [stronger version] inspired by [survey finding]?`

By the end, the human should have at least one idea that is concrete enough to enter critique.

**Creative lenses (one subagent per lens):**

| Lens | Strategy | Search focus |
|------|----------|-------------|
| **Combiner** | Combine two distant findings into a novel approach | Search for prior attempts at this combination |
| **Inverter** | Invert a key assumption — what if the opposite is true? | Search for evidence supporting the inverted assumption |
| **Transplanter** | Apply a method from field A to problem B | Search field A for concrete methods and their results |
| **Bottleneck-breaker** | Directly attack the identified bottleneck | Search for recent tools, techniques, or compute advances that could break it |

**Each subagent produces:**
0-2 Concrete ideas, each with a paragraph summary, explain why it is interesting or practically important, and why it might work, refer to the relevant survey findings

**Step 2b — Merge and present all ideas:**

Combine human ideas + AI ideas into a single numbered list. Apply the sharpening criteria (Polya + Lei Wang, from the questioning strategy above) to each AI idea as well — fill in any gaps. Present to the user before moving to critique.

Save brainstorm reports to `articles/iteration-N/brainstorm/`.
