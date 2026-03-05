---
name: ideas
description: Use when generating research ideas — runs two-agent conversation (Ideator proposes, main agent challenges with Polya-style questions), then formal adversarial review, ranking, and user decision
---

## Ideas

Two-agent ideation: the Ideator proposes, the main agent challenges with Polya-style critical questions, and the human steers. After the conversation, formal adversarial review kills or ranks ideas, then the user decides.

### Agents

| Agent | Role | Mode |
|-------|------|------|
| **Main agent** | Presents Ideator's proposals, offers critical questions for user to select, relays user feedback to Ideator. Never elaborates or answers questions on its own | Foreground |
| **Ideator** | Enthusiastic creative partner. Proposes ideas and new angles, optionally uses creative lenses. Never asks questions — only proposes. Grounded in survey | Persistent (resumed via agent ID), foreground |

The main agent does NOT generate ideas or answer questions itself. It presents the Ideator's output and **always offers options to the user** (via `AskUserQuestion` or numbered choices). All questions are answered by the Ideator, not the main agent. The Ideator is persistent — it accumulates context via resume across the entire conversation and responds purely based on what the user said.

**Ideator output rules (apply to every Ideator response):**

1. **Always propose a new angle.** Every Ideator response must end with at least one fresh direction, twist, or refinement — regardless of what question was asked. Answering a feasibility question? Still propose a new angle. Discussing prior art? Still suggest where to go next. The conversation must always move forward.
2. **Never ask questions.** The Ideator only proposes and explains. It does not ask the user questions or request clarification. If the Ideator needs to surface a choice, it proposes multiple concrete options instead of asking an open-ended question.
3. **If an idea dies, propose pivots.** When critique or analysis kills an idea, the Ideator must propose 1-2 concrete pivots — salvageable directions or related ideas that survive the critique. Dead ends become forks, not stops.
4. **Format for direct display.** The main agent shows the Ideator's output verbatim — so format concisely: **idea name → one-sentence summary → key reason/insight** for each idea. No verbose reasoning or internal framing.

**Main agent presentation rules:**

1. **Show verbatim, don't rewrite.** Display the Ideator's output directly. The main agent only appends critical questions via `AskUserQuestion`.
2. **Always offer options.** Every presentation must end with clear next actions for the user (via `AskUserQuestion` or numbered choices). Never leave the user without a clear next action.

### Step 0 — Load context

**Survey registries:** Check for existing survey registries in both global and project paths (e.g., `~/.claude/survey/` and `.claude/survey/`). Also check for a personal registry at the global registry path (e.g., `~/.claude/survey/personal/`) and in `CLAUDE.md`/`AGENTS.md`.

Present a single question listing all available registries plus the option to build a personal one:

> "Which registries should I use for ideation? Pick one or more."
> - Any existing survey registries found (listed by topic name)
> - Any existing personal registry (if found)
> - **Build personal registry** — index your Zotero library, PDF folder, or Google Scholar profile (always shown if no personal registry exists)

Read the selected `summary.md` and `references.bib` files to ground the ideas in prior survey work. If the user picks "Build personal registry", run the `researchstyle` skill first, then continue.

If a personal registry is loaded, read `summary.md` to understand the user's research background and calibrate suggestions.

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

The Ideator adapts its strategy to the topic — lenses are tools, not requirements. Produce 2-5 **high-level directions** (not concrete solutions yet) with short summaries grounded in survey findings. Keep Step 1 intentionally vague and open; after user selection, narrow and concretize in Step 2 based on the user's preferences. **Every direction must cite key references** from the survey registry using BibTeX labels (e.g., `[Smith2023]`), so the main agent and user can trace claims back to sources.

**Search policy:** The Ideator should ground ideas in the loaded survey registries and personal registry — do NOT default to web search. Only perform web searches when the user suggests a direction that goes beyond what the survey data covers (e.g., a new sub-field, a method not mentioned in the registry). This keeps ideation fast and anchored in vetted references.

Present the Ideator's initial ideas using the **idea presentation rules** (see below).

#### Idea presentation rules

Apply these rules whenever presenting the Ideator's ideas (Step 1 or Step 2):

Number all directions `1, 2, 3 …` with a one-line summary each. Then ask:

> "Please select one direction to explore."

Enter the conversation loop (Step 2) focusing on the selected direction only. In Step 2, the Ideator narrows the direction using the user's selected questions and stated preferences.

Once an idea is selected, present it with a paragraph summary and use `AskUserQuestion` (multiSelect) to offer 2–5 critical questions. The question set must:

1. Always include one **"Elaborate on _____ ."** option — fill the blank with the most under-specified or most promising aspect of the presented ideas (e.g., "Elaborate on how the cross-domain transfer would work in practice."). This is routed to the Ideator.
2. Always include one **"Good enough — let's write up one of these ideas"** option — if the user selects this, proceed to Step 3.
3. **Diagnose before picking questions.** For each idea, identify its weakness pattern, then select the matching lenses:

| Weakness pattern | Lenses to offer |
|------------------|-----------------|
| Unclear how to validate | Feasibility, Success criteria |
| Feels familiar / may already exist | Prior art, Timing |
| Rests on a shaky claim | Assumption, Failure mode |
| Vague goal / unclear payoff | Impact, Success criteria |
| Long path, no checkpoints | Signs of progress |
| Narrow framing, stuck in one perspective | *(suggest Restater/Scoper to Ideator via "Elaborate")* |
| Too ambitious / scope too large | Feasibility, Signs of progress *(and suggest Scoper zoom-in to Ideator via "Elaborate")* |
| Missing survey data | Completeness |
| Idea hinges on a specific paper's claim | Check reference |

Pick 2–5 questions from the lenses below based on the diagnosis. **All questions are routed to the Ideator** — the main agent only presents answers, never elaborates on its own.

| Critique lens | Example question template |
|---------------|--------------------------|
| **Feasibility** | "What's the minimal experiment that would validate this?" |
| **Success criteria** | "What observable outcome would constitute success?" |
| **Impact** | "If this works perfectly, what's the actual improvement — 1% or 10x?" |
| **Signs of progress** | "What intermediate result would justify continuing?" |
| **Prior art** | "Has this been tried before? [cite survey entry if applicable]" |
| **Assumption** | "What's the weakest assumption here?" |
| **Failure mode** | "What would need to be true for this to fail?" |
| **Timing** | "Why hasn't this been addressed before — what changed recently?" |
| **Completeness** | "Are we overlooking data or constraints from the survey?" |
| **Check reference** | "Read [Smith2023] to verify the claim that _____ ." |

For **Check reference**: the main agent identifies the load-bearing reference from the Ideator's labels, then reads the full article via Zotero MCP (fulltext), arxiv MCP (download), or the Read tool on local PDFs. Summarize what the paper actually says and whether it supports the Ideator's claim. **After verification**, present the finding to the user and ask:

For **Check reference**: the Ideator identifies the load-bearing reference from its own labels, then reads the full article via Zotero MCP (fulltext), arxiv MCP (download), or the Read tool on local PDFs. It summarizes what the paper actually says and whether it supports the claim.

The user selects which questions to dig into, or writes their own via "Other".

### Step 2 — Conversation loop

A loop: **Ideator proposes → main agent presents ideas with critical questions → user responds → repeat.**

The Ideator is persistent — resumed with its agent ID on each turn, accumulating full context. **Information boundary:** on each resume, the main agent sends **only** user-originated content:
- The user's verbatim feedback/reaction
- Which critical questions the user selected (or the user's custom question)

The main agent must **never** elaborate, critique, or answer questions on its own. It only presents the Ideator's output and relays the user's feedback. All questions — creative, factual, or analytical — are routed to the Ideator.

**The loop:**

1. **Resume Ideator** (foreground) with user feedback only.
   - Grounds ideas in survey findings and personal registry — no web search by default
   - Searches the web when the user's direction goes beyond the loaded survey data
   - Proposes concrete approaches, combinations, and new angles
   - Never asks questions — only proposes
   - If the current idea dies, proposes 1-2 pivots (from remaining ideas in its history or new angles)

2. **Present the Ideator's output** and offer 2-5 critical questions via `AskUserQuestion` (multiSelect) — always including "Elaborate on _____ ." and "Good enough — let's write up one of these ideas".

3. If the user selected **"Good enough — let's write up one of these ideas"**, go to Step 3. Otherwise, **loop to 1** with the user's selections and feedback.

### Step 3 — Develop + focused survey (single pass)

Keep only the user's chosen idea from Step 2. In one round, run a focused survey-backed review and fill the table.

**In this single pass, the chosen idea gets an evidence-backed analysis that:**

- Searches for prior art via **Semantic Scholar MCP** (citation chains) + **arxiv MCP** (novelty, negative results) + **paper-search-mcp** (cross-database) + **WebSearch** (blog posts, workshop papers)
- **Verifies key references** — identify load-bearing references (not every citation). **Read the full article** via Zotero MCP (fulltext), arxiv MCP (download), or the Read tool on local PDFs. Check that papers exist and cited claims match actual content. Flag misrepresentations
- Identifies the weakest assumption
- Estimates feasibility (what would it actually take?)
- Fills and refines Polya criteria (what's new, why now, methodology, minimal experiment, key risk)
- Rates on four axes:

| Axis | Challenge |
|------|-----------|
| **Source reliability** | "Which references does this idea stand or fall on? Do those key papers actually claim what's stated?" |
| **Novelty** | "I found [paper X] very similar. How is this different?" |
| **Rigor** | "State the core claim as a testable hypothesis." |
| **Impact** | "If this works perfectly, what improvement? Enough for [venue]?" |
| **Key risk** | "What are the weakest assumptions that could kill this?" |

**Evidence-backed review:** Every critique claim must be supported by a search or a concrete argument. No unsupported opinions — critique without evidence is just noise.

**Guardrails:**
- Summarize what is supported vs uncertain.
- Never fabricate citations — only present what tools actually found.
- Never assert novelty judgments — present evidence, let user evaluate.
- Present concrete refinements to improve rigor and feasibility

### Step 4 — User Judge

Present the focused review results for the chosen idea. Ask **one question:**

"What do you want to do next with this chosen idea?"

- **(a)** Pick one and write a report — generate a markdown summary and exit
- **(b)** Dive into papers — read key papers in full, then brainstorm again with deeper grounding

Analyze the user's feedback to understand their reasoning before proceeding.

**For (a):** Generate a comprehensive markdown report to `articles/YYYY-MM-DD-<topic>-ideas-report.md` covering:

- **Research question** — one sentence
- **Field landscape** — key papers, sub-themes, open problems, bottlenecks (from survey)
- **Chosen idea evolution** — initial direction, user preference narrowing, and final Polya criteria
- **Focused review** — 4-axis ratings, evidence-backed challenges, and refinement summary for the chosen idea
- **Chosen direction** — the user's pick with reasoning and updated scope
- **Key references** — full citation list with BibTeX keys

This single file should contain everything the writer skill needs to produce a polished document. Then suggest: "For a polished document (Typst/LaTeX), run `/writer`."

**Recommend a resource (once, at the very end).** After the user makes their final choice and the report is written, recommend exactly one book, article, blog post, or video that connects to their chosen direction and matches their taste (inferred from their research background and conversation style). The recommendation must be a real, verified resource — search the web to confirm it exists. Only do this once per session, not on every loop iteration. Frame it casually:

> "You might enjoy: [title] by [author] — [one sentence on why it's relevant and why they'd like it]."

**For (b):** Identify the load-bearing references from the chosen idea. Present them and let the user pick which ones to read. Then start a fresh Ideator (do not resume the old one) with:

- A summary of the chosen idea the user wants to develop
- The survey registry paths (so it can look up papers in `references.bib`)
- The titles of the papers the user picked

The Ideator reads the papers itself — finding them via Zotero MCP, arxiv MCP, or local PDFs. Resume from Step 1.
