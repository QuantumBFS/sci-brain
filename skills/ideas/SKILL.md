---
name: ideas
description: Use when generating research ideas — runs three-agent concurrent conversation (Ideator proposes, Critic challenges, main agent mediates), then formal adversarial review, AI judge ranking, and user decision
---

## Ideas

Three-agent concurrent ideation: the Ideator proposes, the Critic challenges, and the main agent mediates the conversation with the human. After the conversation, formal adversarial review kills or ranks ideas, then the user decides.

### Agents

| Agent | Role | Mode |
|-------|------|------|
| **Main agent** | Mediator — presents proposals and challenges, asks for user feedback, encourages deeper input | Foreground |
| **Ideator** | Enthusiastic creative partner. Proposes ideas, asks probing questions, optionally uses creative lenses. Grounded in survey | Persistent (resumed via agent ID), foreground |
| **Critic** | Harsh, professional, annoying. Pokes holes in everything with evidence. Does not hold back negative comments. User can address or ignore | Persistent (resumed via agent ID), foreground |

The main agent does NOT generate ideas or critique. It relays, summarizes, and asks. Both subagents are persistent — they accumulate context via resume across the entire conversation.

### Step 0 — Load context

**Survey registries:** Check for existing survey registries in both global and project paths (e.g., `~/.claude/survey/` and `.claude/survey/`). If registries exist, list them and ask the user which ones to load:

> "I found these survey registries. Which ones should I use for ideation? Pick one or more."

Read the selected `summary.md` and `references.bib` files to ground the ideas in prior survey work. If no registries exist, skip this.

**Personal registry:** Check for an existing personal registry at the global registry path (e.g., `~/.claude/survey/personal/`). Also check `CLAUDE.md`/`AGENTS.md` for a configured registry path. If found, read `summary.md` to understand the user's research background and calibrate suggestions. If not found, offer:

> "I can build a personal registry from your Zotero/PDF folder/Google Scholar to calibrate suggestions. Want to do that now, or skip?"

**Collect registry paths** for subagent launches. Both the Ideator and Critic need access to the survey data. When launching or resuming either subagent, include the file paths so they can read the files directly:
- Survey registry paths: `<registry-root>/<topic>/summary.md` and `references.bib`
- Personal registry path (if available): `<global-registry-root>/personal/summary.md`

### Step 1 — Open

Present the survey highlights. Launch the **Ideator** (foreground) with the registry file paths so it can read the survey context and generate initial ideas. The Ideator may optionally use **creative lenses** when they fit the topic:

| Lens | Strategy | Search focus |
|------|----------|-------------|
| **Combiner** | Combine two distant findings into a novel approach | Search for prior attempts at this combination |
| **Inverter** | Invert a key assumption — what if the opposite is true? | Search for evidence supporting the inverted assumption |
| **Transplanter** | Apply a method from field A to problem B | Search field A for concrete methods and their results |
| **Bottleneck-breaker** | Directly attack the identified bottleneck | Search for recent tools, techniques, or compute advances that could break it |

The Ideator adapts its strategy to the topic — lenses are tools, not requirements. Each lens produces 0-2 concrete ideas with a paragraph summary grounded in survey findings.

Present the Ideator's initial ideas to the user and ask:

> `>>> Based on what we found, what directions interest you? Even a vague hunch is fine.`

### Step 2 — Conversation loop

A sequential loop with a predictable rhythm: **ideas → user reacts → critique → user responds → repeat.**

Both subagents are persistent — resumed with their agent ID on each turn, accumulating full context across the conversation. On each resume, the main agent sends:
- Latest user feedback/reaction
- What the other subagent said (so they stay informed of each other)
- Any user decisions (e.g., "user ignored your critique of idea 3")
- Directive for what to do next

**The loop:**

1. **Resume Ideator** (foreground) with all context (user feedback, Critic's previous points, current direction).
   - Ideator searches for related methods and recent advances
   - Connects to survey findings
   - Proposes concrete approaches and combinations
   - Asks probing questions that open new angles
   - Main agent presents Ideator's ideas to user

2. **User reacts** — provides feedback, direction, or new thoughts. Main agent encourages deeper input: ask follow-up questions, invite the user to think more.

3. **Resume Critic** (foreground) with ideas + user's reaction.
   - Critic checks novelty against the survey (has this been tried?)
   - Searches for prior art and negative results
   - Identifies risks and prior failures
   - Delivers harsh but evidence-backed critique
   - Main agent presents Critic's challenges. User can address or ignore.

4. **User responds** to critique (or ignores it). Main agent notes the user's decision.

5. **Loop to 1** with full accumulated context.

The conversation continues until the user settles on 1-3 directions or says they're done.

### Step 3 — Develop

Collect all surviving ideas (human-seeded, Ideator-proposed, lens outputs). The Ideator fills in **Polya criteria** for each:

- **What's new?** — verify novelty claim against survey
- **Why now?** — identify recent enablers (new data, methods, compute, theory)
- **Methodology** — outline approach, connect to known methods
- **Minimal experiment** — smallest test that validates the core claim
- **Key risk** — weakest assumption

Present all developed ideas as a single numbered list with Polya analysis filled in.

### Step 4 — Formal critique and ranking

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

**After the review, make hard calls:**

- **Kill** ideas that did not survive critique — write a one-line epitaph explaining why each died. If all ideas are killed, report what was learned, suggest new angles, and ask the user whether to loop back to survey with adjusted strategies
- **Rank** survivors by: novelty, impact, viability
- **Present** a ranked table to the user

| # | Idea | Novelty | Impact | Viability | Key risk | Status |
|---|------|---------|--------|-----------|----------|--------|
| 1 | ... | High | High | Medium | Needs X | Alive |
| 2 | ... | High | Medium | High | Prior art Y | Alive |
| 3 | ... | Medium | High | Low | Killed by Z | Dead |


### Step 5 — User Judge

Present the ranked results. Ask **one question:**

"Which direction interests you?"

- **(a)** Pick one and write a report — generate a markdown summary and exit
- **(b)** Pick one and go deeper — loop back to Survey with narrowed scope
- **(c)** None of these, explore differently — loop back to Survey with new angle from user

Analyze the user's feedback to understand their reasoning before proceeding.

**For (a):** Generate a comprehensive markdown report to `articles/YYYY-MM-DD-<topic>-ideas-report.md` covering:

- **Research question** — one sentence
- **Field landscape** — key papers, sub-themes, open problems, bottlenecks (from survey)
- **All ideas explored** — each idea with its Polya criteria (what's new, why now, methodology, minimal experiment, key risk)
- **Critique and ranking** — 4-axis ratings, evidence-backed challenges, ranked table
- **Killed ideas** — epitaphs explaining why each died
- **Surviving ideas** — what survived and why
- **Chosen direction** — the user's pick with reasoning
- **Key references** — full citation list with BibTeX keys

This single file should contain everything the writer skill needs to produce a polished document. Then suggest: "For a polished document (Typst/LaTeX), run `/writer`."

### Loop Handoff (between iterations)

When the user chooses to go deeper or explore a new angle (options b/c), save an iteration report to `articles/iteration-N/report.md` with the same structure as above. Then clear the conversation context (e.g., `/compact` in Claude Code) and re-read the iteration report before starting the next iteration.
