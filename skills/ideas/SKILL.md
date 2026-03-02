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

The main agent does NOT generate ideas itself. It presents the Ideator's output, raises critical questions for the user to consider, and relays **only the user's feedback** back to the Ideator — never the main agent's own elaboration, critique, or directives. The Ideator is persistent — it accumulates context via resume across the entire conversation and responds purely based on what the user said.

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
| **Restater** | Reframe the problem statement itself — a different formulation may unlock different solutions |
| **Scoper** | Zoom in (specialize to a concrete case) or zoom out (generalize to a broader class — Polya's Inventor's paradox: "the more ambitious plan may have more chances of success") |

The Ideator adapts its strategy to the topic — lenses are tools, not requirements. Each lens produces 0-2 concrete ideas with a paragraph summary grounded in survey findings. **Every idea must cite key references** from the survey registry using BibTeX labels (e.g., `[Smith2023]`), so the main agent and user can trace claims back to sources.

**Search policy:** The Ideator should ground ideas in the loaded survey registries and personal registry — do NOT default to web search. Only perform web searches when the user suggests a direction that goes beyond what the survey data covers (e.g., a new sub-field, a method not mentioned in the registry). This keeps ideation fast and anchored in vetted references.

Present the Ideator's initial ideas using the **idea presentation rules** (see below).

#### Idea presentation rules

Apply these rules whenever presenting the Ideator's ideas (Step 1 or Step 2):

**Long list (> 3 ideas):** Number them `1, 2, 3 …` with a one-line summary each. Then ask:

> "Type the numbers of the ideas you'd like to explore (e.g. `1, 3`), or describe a new direction."

Do NOT present critical questions yet — wait for the user to narrow down first.

**Short list (≤ 3 ideas):** Present each idea with a paragraph summary, then use `AskUserQuestion` (multiSelect) to offer 3–6 critical questions tailored to the ideas. The question set must:

1. Always include one **"Elaborate on _____ ."** option — fill the blank with the most under-specified or most promising aspect of the presented ideas (e.g., "Elaborate on how the cross-domain transfer would work in practice."). This is routed to the Ideator.
2. **Diagnose before picking questions.** For each idea, identify its weakness pattern, then select the matching lenses:

| Weakness pattern | Lenses to offer |
|------------------|-----------------|
| Unclear how to validate | Feasibility, Success criteria |
| Feels familiar / may already exist | Prior art, Timing |
| Rests on a shaky claim | Assumption, Failure mode |
| Vague goal / unclear payoff | Impact, Success criteria |
| Long path, no checkpoints | Signs of progress |
| Narrow framing, stuck in one perspective | *(suggest Restater/Scoper to Ideator via "Elaborate")* |
| Missing survey data | Completeness |
| Idea hinges on a specific paper's claim | Check reference |

Pick 2–5 questions from the lenses below based on the diagnosis. Each lens has a **routes to** indicator.

**Ideator-routed** — user selection is relayed to the Ideator (creative/generative questions):

| Critique lens | Example question template |
|---------------|--------------------------|
| **Feasibility** | "What's the minimal experiment that would validate this?" |
| **Success criteria** | "What observable outcome would constitute success?" |
| **Impact** | "If this works perfectly, what's the actual improvement — 1% or 10x?" |
| **Signs of progress** | "What intermediate result would justify continuing?" |

**Main-agent-routed** — main agent elaborates grounded in the survey (factual/analytical questions, shown only to user, not relayed to Ideator):

| Critique lens | Example question template |
|---------------|--------------------------|
| **Prior art** | "Has this been tried before? [cite survey entry if applicable]" |
| **Assumption** | "What's the weakest assumption here?" |
| **Failure mode** | "What would need to be true for this to fail?" |
| **Timing** | "Why hasn't this been addressed before — what changed recently?" |
| **Completeness** | "Are we overlooking data or constraints from the survey?" |
| **Check reference** | "Let me read [Smith2023] to verify the claim that _____ ." |

For **Check reference**: the main agent identifies the load-bearing reference from the Ideator's labels, then reads the full article via Zotero MCP (fulltext), arxiv MCP (download), or the Read tool on local PDFs. Summarize what the paper actually says and whether it supports the Ideator's claim.

The user selects which questions to dig into, or writes their own via "Other" (custom questions are always routed to the Ideator).

### Step 2 — Conversation loop

A loop: **Ideator proposes → main agent presents ideas with critical questions → user responds → repeat.**

The Ideator is persistent — resumed with its agent ID on each turn, accumulating full context. **Information boundary:** on each resume, the main agent sends **only** user-originated content:
- The user's verbatim feedback/reaction
- Which critical questions the user selected (or the user's custom question)

The main agent must **never** send its own elaboration, critique, or directives to the Ideator. The Ideator responds purely based on the user's input.

**The loop:**

1. **Resume Ideator** (foreground) with user feedback only.
   - Grounds ideas in survey findings and personal registry — no web search by default
   - Only searches the web when the user's direction goes beyond the loaded survey data
   - Proposes concrete approaches and combinations
   - Asks probing questions that open new angles

2. **Present ideas using the idea presentation rules** (defined in Step 1). If the Ideator returned > 3 ideas, list and let the user narrow down first. If ≤ 3, present with critical questions via `AskUserQuestion` (multiSelect) — always including one "Elaborate on _____ ." option.

3. **Route by question type:**
   - **Ideator-routed questions** ("Elaborate on _____", Feasibility, Success criteria, Impact, Signs of progress, custom "Other") → relay the user's selection to the Ideator. The Ideator responds creatively.
   - **Main-agent-routed questions** (Prior art, Assumption, Failure mode, Timing, Completeness) → the main agent elaborates, grounded in the survey. This elaboration is shown **only to the user**, not relayed to the Ideator.

4. **Loop to 1** — pass all user feedback (selections + verbatim reactions) to the Ideator. The Ideator receives everything the user said, nothing the main agent said.

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
- **Verifies key references** — identify load-bearing references (not every citation). **Read the full article** via Zotero MCP (fulltext), arxiv MCP (download), or the Read tool on local PDFs. Check that papers exist and cited claims match actual content. Flag misrepresentations. This is the most important step — an idea built on a misread paper is worthless
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

- **Kill** ideas that did not survive critique — write a one-line epitaph explaining why each died. If all ideas are killed, report what was learned, suggest new angles, and offer to dive into papers (Step 5b) for deeper grounding
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
- **(b)** Dive into papers — read key papers in full, then brainstorm again with deeper grounding

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

**For (b):** Identify the load-bearing references from the surviving ideas. Present them and let the user pick which ones to read. Then start a fresh Ideator (do not resume the old one) with:

- A summary of the surviving idea(s) the user wants to develop
- The survey registry paths (so it can look up papers in `references.bib`)
- The titles of the papers the user picked

The Ideator reads the papers itself — finding them via Zotero MCP, arxiv MCP, or local PDFs. Resume from Step 1.
