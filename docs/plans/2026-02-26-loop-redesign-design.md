# Loop Redesign: Survey-Brainstorm-Critique

Replace the current 5-phase pipeline (Survey → Expand → Crystallize → Stress-test → Refine) with a simpler structure: **Entry → Loop → Refine**.

## Overall structure

```
Entry (clarify) → Loop [Survey → Verify → Brainstorm → Critique → AI Judge → User Judge] → Refine → Doc
                  ↑___________________________________|
                        (user says: go deeper)
```

The loop runs until the user is satisfied with a direction, then exits to Refine.

## Entry (unchanged)

Ask one clarification question to narrow the research question. Multiple choice when possible. Focus on what the user wants to explore, not background or logistics.

## The Loop

### Step 1: Survey (parallel exploration)

Launch N subagents in parallel. The AI selects exploration strategies dynamically based on what is known vs. unknown. First iteration is broad; later iterations focus on gaps identified in previous iterations.

Strategy menu (AI picks from these):
- **Landscape mapping** — first iteration default, broad field overview
- **Adjacent subfield** — deep-dive into a neighboring cluster
- **Cross-vocabulary** — abstract away jargon, search other fields for the same structural problem
- **Cross-method** — same problem, different computational or experimental approaches
- **Historical lineage** — who tried before, what failed, what changed since
- **Negative results** — search for papers showing what does not work
- **Benchmarks and datasets** — what evaluation infrastructure exists

Each subagent produces a structured report with inline citations. Reports saved to `articles/iteration-N/survey/`.

### Step 2: Verify (fact-check)

Launch reviewer subagents — one per survey report. Each reviewer:
- Checks that cited papers exist (search for them)
- Verifies claims match cited abstracts
- Flags unsupported assertions
- Rates confidence per claim: high / medium / low

Output: annotated reports with confidence ratings. Main agent synthesizes a verified survey summary.

### Step 3: Brainstorm (parallel ideation)

Launch subagents with fixed creative lenses, each receiving the verified survey:

| Lens | Strategy |
|------|----------|
| **Combiner** | Combine two distant findings into a novel approach |
| **Inverter** | Invert a key assumption — what if the opposite is true? |
| **Transplanter** | Apply a method from field A to problem B |
| **Bottleneck-breaker** | Directly attack the identified bottleneck |

Each subagent produces: a concrete idea (1 paragraph), why it might work, and what would be needed to test it.

### Step 4: Critique (adversarial review)

Each brainstorm idea is paired with a devil's advocate subagent that:
- Searches for prior art (has this been tried?)
- Identifies the weakest assumption
- Estimates feasibility (what would it actually take?)
- Rates on three axes: novelty, rigor, impact

Output: each idea has a report + counter-report pair.

### Step 5: AI Judge (synthesis and ranking)

Main agent reads all report/counter-report pairs and:
- Kills ideas that did not survive critique (with one-line epitaphs explaining why)
- Ranks survivors by: novelty, impact, viability
- Presents a ranked table to the user

| # | Idea | Novelty | Impact | Viability | Key risk | Status |
|---|------|---------|--------|-----------|----------|--------|
| 1 | ... | High | High | Medium | Needs X | Alive |
| 2 | ... | High | Medium | High | Prior art Y | Alive |
| 3 | ... | Medium | High | Low | Killed by Z | Dead |

### Step 6: User Judge (human decision)

Present the ranked results. Ask one question:

"Which direction interests you?"
- **(a)** Pick one and write the proposal → exit loop, proceed to Refine
- **(b)** Pick one and go deeper → loop back to Step 1 with narrowed scope
- **(c)** None of these, explore differently → loop back to Step 1 with new angle from user

Analyze user's feedback to understand their reasoning before proceeding.

## Refine (mostly unchanged)

Produce a structured research direction document incorporating all accumulated survey findings, ideas, and critique from loop iterations.

Output saved to `docs/plans/YYYY-MM-DD-<topic>-research-direction.md`.

Structure:
- Field Landscape
- Key Bottleneck
- Research Question
- Novelty Claim (survived critique)
- Why Now, Why You
- Key References
- Cross-field Connections
- Proposed Approach
- Minimum Viable Experiment
- Success Criteria
- Warning Signs (from critique)
- Open Risks
- Target Venue

## File organization

```
articles/
  iteration-1/
    survey/        # Step 1 reports
    brainstorm/    # Step 3 ideas
    critique/      # Step 4 counter-reports
    SUMMARY.md     # Step 5 synthesis
  iteration-2/
    ...
docs/plans/
  YYYY-MM-DD-<topic>-research-direction.md
```

## Design decisions

- **Flat loop, no phase numbers.** Each iteration runs the same 6 steps. The AI adapts strategies per iteration rather than using distinct named phases.
- **Dynamic survey strategies.** AI selects from a menu based on knowledge gaps, rather than always running the same 4 subagents.
- **Fixed brainstorming lenses.** Four creative strategies that complement each other: combine, invert, transplant, break bottleneck.
- **Adversarial pairs for critique.** Every idea gets a devil's advocate. No ideas skip review.
- **Two-stage judgement.** AI filters and ranks first, then human decides. Human always has the option to loop, exit, or redirect.
