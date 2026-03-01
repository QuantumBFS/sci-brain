---
name: critique
description: Use when critiquing brainstorm ideas — runs adversarial devil's advocate review with source verification, then AI judge ranks and kills ideas, then user decides whether to loop or write proposal
---

## Step 3 — Critique (adversarial review + source verification)

Try to kill each idea with evidence — AI ideas and human ideas alike. Whatever survives is worth considering. This is also where source claims get fact-checked.

**Each brainstorm idea (AI or human) is paired with a devil's advocate subagent that:**

- Searches for prior art (has this been tried?) via **Semantic Scholar MCP** (citation chains) + **arxiv MCP** (novelty claim, negative results) + **paper-search-mcp** (cross-database) + **WebSearch** (blog posts, workshop papers)
- **Verifies key references** — for each idea, identify the small number of references that the idea's validity depends on (not every citation — just the load-bearing ones). Fetch the full PDF if needed (survey only collected abstracts). Check that these papers exist, that the cited claims match the actual content, and flag any misrepresentations
- Identifies the weakest assumption
- Estimates feasibility (what would it actually take?)
- Rates on four axes:

| Axis | Challenge |
|------|-----------|
| **Source reliability** | "Which references does this idea stand or fall on? Do those key papers actually claim what's stated?" |
| **Novelty** | "I found [paper X] very similar. How is this different?" |
| **Rigor** | "State the core claim as a testable hypothesis." |
| **Impact** | "If this works perfectly, what improvement? Enough for [venue]?" |

**Evidence-backed critique:** Every critique claim must be supported by a search or a concrete argument. No unsupported opinions — critique without evidence is just noise.

**Guardrails:**
- Never fabricate citations — only present what tools actually found.
- Never assert novelty judgments — present evidence, let user evaluate.
- Always preserve pivot path — show what's salvageable when critique kills an idea.

**Output:** Each idea has a report + counter-report pair. Save to `articles/iteration-N/critique/`.

## Step 4 — AI Judge (synthesis and ranking)

Read all report/counter-report pairs from Step 3 and make hard calls.

**Actions:**

- **Kill** ideas that did not survive critique — write a one-line epitaph explaining why each died. If all ideas are killed, report what was learned, suggest new angles, and ask the user whether to loop back to survey with adjusted strategies
- **Rank** survivors by: novelty, impact, viability
- **Present** a ranked table to the user

| # | Idea | Novelty | Impact | Viability | Key risk | Status |
|---|------|---------|--------|-----------|----------|--------|
| 1 | ... | High | High | Medium | Needs X | Alive |
| 2 | ... | High | Medium | High | Prior art Y | Alive |
| 3 | ... | Medium | High | Low | Killed by Z | Dead |

Save synthesis to `articles/iteration-N/SUMMARY.md`.

## Step 5 — User Judge (human decision)

Present the ranked results. Ask **one question:**

"Which direction interests you?"

- **(a)** Pick one and write the proposal → exit loop, proceed to Refine
- **(b)** Pick one and go deeper → loop back to Step 1 with narrowed scope
- **(c)** None of these, explore differently → loop back to Step 1 with new angle from user

Analyze the user's feedback to understand their reasoning before proceeding.

## Loop Handoff (between iterations)

When the user chooses to go deeper or explore a new angle (options b/c), run this before starting the next iteration:

**1. Save iteration summary** to `articles/iteration-N/ITERATION-SUMMARY.md`:

- Research question as understood at this point
- Key findings from the survey (with file references to saved reports)
- Ideas generated — which survived, which were killed and why
- User feedback and chosen direction
- What to explore next and why

**2. Compact the conversation** if it is getting long: summarize the conversation so far, then compact or trim context to free space for the next iteration (e.g., `/compact` in Claude Code). The saved files in `articles/iteration-N/` serve as the durable record — re-read them as needed in the next iteration rather than relying on conversation history.
