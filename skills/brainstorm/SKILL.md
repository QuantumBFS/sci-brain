---
name: brainstorm
description: Use when brainstorming research ideas from a survey report — runs a concurrent conversation where the main agent suggests directions while background agents analyze and develop ideas
---

## Step 2 — Brainstorm

A concurrent conversation: the main agent brainstorms with the human while background agents do real-time research. The human provides creative direction; the AI does the analytical heavy lifting.

**Phase 1 — Open.**

Present the survey highlights and suggest 2-3 promising directions from the findings. Then ask:

> `>>> Based on what we found, what directions interest you? Even a vague hunch is fine.`

At the same time, launch the **creative lenses** as background subagents (they only need the survey, not the human's input):

| Lens | Strategy | Search focus |
|------|----------|-------------|
| **Combiner** | Combine two distant findings into a novel approach | Search for prior attempts at this combination |
| **Inverter** | Invert a key assumption — what if the opposite is true? | Search for evidence supporting the inverted assumption |
| **Transplanter** | Apply a method from field A to problem B | Search field A for concrete methods and their results |
| **Bottleneck-breaker** | Directly attack the identified bottleneck | Search for recent tools, techniques, or compute advances that could break it |

Each lens produces 0-2 concrete ideas with a paragraph summary explaining why it is interesting and why it might work, grounded in survey findings.

**Phase 2 — Concurrent conversation.**

As soon as the human mentions a direction:

1. **Launch background subagents** to analyze what the human said:
   - Check novelty against the survey (has this been tried?)
   - Search for related methods and recent advances
   - Identify what would make this tractable now
   - Find potential risks or prior failures

2. **Main agent keeps the conversation going** — don't wait for background results. Instead of drilling the human with questions, **actively suggest directions**:
   - Connect human instincts to survey findings: "That connects to [paper X] which found [Y] — could that method apply here?"
   - Propose angles: "The survey showed [bottleneck Z] is the main obstacle. What if we attacked it with [method from field A]?"
   - Challenge gently when needed: "That's interesting, but [paper X] tried something similar and hit [problem]. What would be different this time?"

3. **When background results arrive**, integrate them naturally:
   - "I just checked — [paper] tried something similar but [key difference]. That actually supports your angle because [reason]."
   - "Novelty check: I couldn't find prior work combining [X] and [Y] — that's genuinely new territory."
   - "One risk: [paper] showed that [assumption] breaks down when [condition]. Worth keeping in mind."

The conversation continues until the human settles on 1-3 directions or says they're done. The main agent should be an active collaborator — suggesting, connecting, challenging — not an interviewer drilling questions.

**Phase 3 — Develop and present.**

Once the human is done, collect all ideas (human-seeded, AI-suggested during conversation, and creative lens outputs). Run subagents to fill in **Polya criteria** for each idea:

- **What's new?** — verify novelty claim against survey
- **Why now?** — identify recent enablers (new data, methods, compute, theory)
- **Methodology** — outline approach, connect to known methods
- **Minimal experiment** — smallest test that validates the core claim
- **Key risk** — weakest assumption

Present all developed ideas as a single numbered list. Each idea should have its Polya analysis filled in so the human can compare them on substance, not just vibes.

Save brainstorm reports to `articles/iteration-N/brainstorm/`.
