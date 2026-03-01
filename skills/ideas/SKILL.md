---
name: ideas
description: Use when generating research ideas — runs two-agent conversation (Ideator proposes, main agent challenges with Polya-style questions), then formal adversarial review, ranking, and user decision
---

## Ideas

Two-agent ideation: the Ideator proposes, the main agent challenges with Polya-style critical questions, and the human steers. After the conversation, formal adversarial review kills or ranks ideas, then the user decides.

### Agents

| Agent | Role | Mode |
|-------|------|------|
| **Main agent** | Presents Ideator's proposals, raises Polya-style critical questions, asks for user feedback, encourages deeper input | Foreground |
| **Ideator** | Enthusiastic creative partner. Proposes ideas, asks probing questions, optionally uses creative lenses. Grounded in survey | Persistent (resumed via agent ID), foreground |

The main agent does NOT generate ideas itself. It presents the Ideator's output, raises critical questions for the user to consider, and relays the user's feedback back to the Ideator. The Ideator is persistent — it accumulates context via resume across the entire conversation.

### Step 0 — Load context

**Survey registries:** Check for existing survey registries in both global and project paths (e.g., `~/.claude/survey/` and `.claude/survey/`). If registries exist, list them and ask the user which ones to load:

> "I found these survey registries. Which ones should I use for ideation? Pick one or more."

Read the selected `summary.md` and `references.bib` files to ground the ideas in prior survey work. If no registries exist, skip this.

**Personal registry:** Check for an existing personal registry at the global registry path (e.g., `~/.claude/survey/personal/`). Also check `CLAUDE.md`/`AGENTS.md` for a configured registry path. If found, read `summary.md` to understand the user's research background and calibrate suggestions. If not found, offer:

> "I can build a personal registry from your Zotero/PDF folder/Google Scholar to calibrate suggestions. Want to do that now, or skip?"

**Collect registry paths** for the Ideator. When launching or resuming the Ideator, include the file paths so it can read the files directly:
- Survey registry paths: `<registry-root>/<topic>/summary.md` and `references.bib`
- Personal registry path (if available): `<global-registry-root>/personal/summary.md`

### Step 1 — Open

Present the survey highlights. Launch the **Ideator** (foreground) with the registry file paths so it can read the survey context and generate initial ideas. The Ideator may optionally use **creative lenses** when they fit the topic:

| Lens | Strategy |
|------|----------|
| **Combiner** | Combine two distant findings into a novel approach |
| **Inverter** | Invert a key assumption — what if the opposite is true? |
| **Transplanter** | Apply a method from field A to problem B |
| **Bottleneck-breaker** | Directly attack the identified bottleneck |

The Ideator adapts its strategy to the topic — lenses are tools, not requirements. Each lens produces 0-2 concrete ideas with a paragraph summary grounded in survey findings.

**Search policy:** The Ideator should ground ideas in the loaded survey registries and personal registry — do NOT default to web search. Only perform web searches when the user suggests a direction that goes beyond what the survey data covers (e.g., a new sub-field, a method not mentioned in the registry). This keeps ideation fast and anchored in vetted references.

Present the Ideator's initial ideas to the user and ask:

> `>>> Based on what we found, what directions interest you? Even a vague hunch is fine.`

### Step 2 — Conversation loop

A loop: **Ideator proposes → main agent presents ideas with critical questions → user responds → repeat.**

The Ideator is persistent — resumed with its agent ID on each turn, accumulating full context. On each resume, the main agent sends:
- Latest user feedback/reaction
- Which critical questions the user engaged with or ignored
- Directive for what to do next

**The loop:**

1. **Resume Ideator** (foreground) with all context (user feedback, current direction).
   - Grounds ideas in survey findings and personal registry — no web search by default
   - Only searches the web when the user's direction goes beyond the loaded survey data
   - Proposes concrete approaches and combinations
   - Asks probing questions that open new angles

2. **Present ideas, then let the user pick critical questions.** The main agent presents the Ideator's ideas, then uses `AskUserQuestion` (multiSelect) to offer 3-4 idea-specific Polya-style critical questions for the user to choose from. The user selects which questions they want to dig into (or writes their own via "Other"). Example question bank (adapt to the specific ideas — never use these verbatim):
   - "This is not a new problem — why hasn't it been addressed?"
   - "Has this been tried before? [cite relevant survey entry if applicable]"
   - "What's the weakest assumption here?"
   - "If this works perfectly, what's the actual improvement — 1% or 10x?"
   - "What would need to be true for this to fail?"

   Generate questions specific to the ideas presented — reference survey entries where relevant. The user's selections (and any custom question) determine which challenges the main agent elaborates on and relays to the Ideator.

3. **Main agent elaborates on selected questions** — provide a substantive response to each question the user picked, grounded in the survey. Then relay the user's selections and any custom question back to the Ideator.

4. **Loop to 1** with full accumulated context.

The conversation continues until the user is ready to move on. When presenting multiple ideas, always offer these choices:

> "What would you like to do?"
> - **(a)** Explore a specific direction further — tell me which one
> - **(b)** Evaluate these ideas — run formal critique and ranking on the current set
> - **(c)** Something else — new angle, combine ideas, etc.

If the user picks **(b)**, proceed to Step 3 (Develop) → Step 4 (Formal critique).

### Step 3 — Develop

Collect all surviving ideas (human-seeded, Ideator-proposed, lens outputs). The Ideator fills in **Polya criteria** for each:

- **What's new?** — verify novelty claim against survey
- **Why now?** — identify recent enablers (new data, methods, compute, theory)
- **Methodology** — outline approach, connect to known methods
- **Minimal experiment** — smallest test that validates the core claim
- **Key risk** — weakest assumption

Present all developed ideas as a single numbered list with Polya analysis filled in.

### Step 4 — Formal critique and ranking

The main agent runs a full adversarial review on each developed idea. Try to kill each idea with evidence — Ideator ideas and human ideas alike. Whatever survives is worth pursuing.

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

**Recommend a resource (once, at the very end).** After the user makes their final choice and the report is written, recommend exactly one book, article, blog post, or video that connects to their chosen direction and matches their taste (inferred from their research background and conversation style). The recommendation must be a real, verified resource — search the web to confirm it exists. Only do this once per session, not on every loop iteration. Frame it casually:

> "You might enjoy: [title] by [author] — [one sentence on why it's relevant and why they'd like it]."

### Loop Handoff (between iterations)

When the user chooses to go deeper or explore a new angle (options b/c), save an iteration report to `articles/iteration-N/report.md` with the same structure as above. Then clear the conversation context (e.g., `/compact` in Claude Code) and re-read the iteration report before starting the next iteration.
