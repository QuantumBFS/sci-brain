---
name: ideas
description: Use when generating research ideas — runs three-agent concurrent conversation (Ideator proposes, Critic challenges, main agent mediates), then formal adversarial review, AI judge ranking, and user decision
---

## Step 2 — Ideas

Three-agent concurrent ideation: the Ideator proposes, the Critic challenges, and the main agent mediates the conversation with the human. After the conversation, formal adversarial review kills or ranks ideas, then the user decides.

### Agents

| Agent | Role | Mode |
|-------|------|------|
| **Main agent** | Mediator — presents proposals and challenges, asks for user feedback | Foreground |
| **Ideator** | Brainstorms questions, proposes new ideas, develops directions | Background subagent |
| **Critic** | Reads literature, challenges ideas adversarially | Background subagent |

The main agent does NOT generate ideas or critique. It relays, summarizes, and asks.

### Phase 0 — Load context

**Survey registries:** Check for existing survey registries in both global and project paths (e.g., `~/.claude/survey/` and `.claude/survey/`). If registries exist, list them and ask the user which ones to load:

> "I found these survey registries. Which ones should I use for ideation? Pick one or more."

Read the selected `summary.md` and `references.bib` files to ground the ideas in prior survey work. If no registries exist, skip this.

**Personal registry:** Check for an existing personal registry at the global registry path (e.g., `~/.claude/survey/personal/`). Also check `CLAUDE.md`/`AGENTS.md` for a configured registry path. If found, read `summary.md` to understand the user's research background and calibrate suggestions. If not found, offer:

> "I can build a personal registry from your Zotero/PDF folder/Google Scholar to calibrate suggestions. Want to do that now, or skip?"

### Phase 1 — Open

Present the survey highlights and suggest 2-3 promising directions. Then ask:

> `>>> Based on what we found, what directions interest you? Even a vague hunch is fine.`

Launch the **Ideator** as a background subagent with the survey context. The Ideator may optionally use **creative lenses** when they fit the topic:

| Lens | Strategy | Search focus |
|------|----------|-------------|
| **Combiner** | Combine two distant findings into a novel approach | Search for prior attempts at this combination |
| **Inverter** | Invert a key assumption — what if the opposite is true? | Search for evidence supporting the inverted assumption |
| **Transplanter** | Apply a method from field A to problem B | Search field A for concrete methods and their results |
| **Bottleneck-breaker** | Directly attack the identified bottleneck | Search for recent tools, techniques, or compute advances that could break it |

The Ideator adapts its strategy to the topic — lenses are tools, not requirements. Each lens produces 0-2 concrete ideas with a paragraph summary grounded in survey findings.

### Phase 2 — Concurrent conversation

When the user mentions a direction or gives feedback:

1. **Ideator** (background) develops it:
   - Search for related methods and recent advances
   - Connect to survey findings
   - Propose concrete approaches and combinations
   - Ask probing questions that open new angles
   - Report ideas to main agent

2. **Critic** (background) challenges it:
   - Check novelty against the survey (has this been tried?)
   - Search for prior art and negative results
   - Identify risks and prior failures
   - Report challenges with evidence to main agent

3. **Main agent** relays to the user:
   - Present Ideator's proposals: "The Ideator suggests [idea] — it connects to [survey finding] because [reason]."
   - Present Critic's challenges: "The Critic found [paper X] tried something similar and hit [problem]. What's different about your angle?"
   - Ask for the user's opinion: "Given this critique, do you want to refine this idea, pivot, or move on?"

The conversation continues until the user settles on 1-3 directions or says they're done.

### Phase 3 — Develop

Collect all surviving ideas (human-seeded, Ideator-proposed, lens outputs). The Ideator fills in **Polya criteria** for each:

- **What's new?** — verify novelty claim against survey
- **Why now?** — identify recent enablers (new data, methods, compute, theory)
- **Methodology** — outline approach, connect to known methods
- **Minimal experiment** — smallest test that validates the core claim
- **Key risk** — weakest assumption

Present all developed ideas as a single numbered list with Polya analysis filled in.

Save to `articles/iteration-N/ideas/`.

### Phase 4 — Formal critique

The Critic runs a full adversarial review on each developed idea. Try to kill each idea with evidence — Ideator ideas and human ideas alike. Whatever survives is worth pursuing.

**Each idea is paired with a devil's advocate analysis that:**

- Searches for prior art via **Semantic Scholar MCP** (citation chains) + **arxiv MCP** (novelty, negative results) + **paper-search-mcp** (cross-database) + **WebSearch** (blog posts, workshop papers)
- **Verifies key references** — identify load-bearing references (not every citation). Fetch the full PDF if needed. Check that papers exist and cited claims match actual content. Flag misrepresentations
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

Present critiques to the user and ask for their opinion before proceeding to judgment.

**Output:** Each idea has a report + counter-report pair. Save to `articles/iteration-N/critique/`.

### Phase 5 — AI Judge

Read all report/counter-report pairs from Phase 4 and make hard calls.

- **Kill** ideas that did not survive critique — write a one-line epitaph explaining why each died. If all ideas are killed, report what was learned, suggest new angles, and ask the user whether to loop back to survey with adjusted strategies
- **Rank** survivors by: novelty, impact, viability
- **Present** a ranked table to the user

| # | Idea | Novelty | Impact | Viability | Key risk | Status |
|---|------|---------|--------|-----------|----------|--------|
| 1 | ... | High | High | Medium | Needs X | Alive |
| 2 | ... | High | Medium | High | Prior art Y | Alive |
| 3 | ... | Medium | High | Low | Killed by Z | Dead |

Save synthesis to `articles/iteration-N/SUMMARY.md`.

### Phase 6 — User Judge

Present the ranked results. Ask **one question:**

"Which direction interests you?"

- **(a)** Pick one and write the proposal — exit loop, proceed to Refine
- **(b)** Pick one and go deeper — loop back to Survey with narrowed scope
- **(c)** None of these, explore differently — loop back to Survey with new angle from user

Analyze the user's feedback to understand their reasoning before proceeding.

### Loop Handoff (between iterations)

When the user chooses to go deeper or explore a new angle (options b/c), run this before starting the next iteration:

**1. Save iteration summary** to `articles/iteration-N/ITERATION-SUMMARY.md`:

- Research question as understood at this point
- Key findings from the survey (with file references to saved reports)
- Ideas generated — which survived, which were killed and why
- User feedback and chosen direction
- What to explore next and why

**2. Compact the conversation** if it is getting long: summarize the conversation so far, then compact or trim context to free space for the next iteration (e.g., `/compact` in Claude Code). The saved files in `articles/iteration-N/` serve as the durable record — re-read them as needed in the next iteration rather than relying on conversation history.
