---
name: paper-writer
description: Use when drafting or revising a scientific manuscript with real results, including journal articles, letters, and arXiv preprints
---

# Paper Writer

A working-rules guide for writing scientific papers, distilled from John Martinis's *Notes on Writing a Scientific Paper* and Jan von Delft's *Style Guide*. Both source documents are preserved at `skills/paper-writer/references.md` and `skills/paper-writer/sources/` — consult them when this SKILL.md leaves a question open.

**Scope note.** This skill is for *real manuscripts* — papers reporting completed (or near-complete) experimental, theoretical, or computational results. It is **not** for the upstream ideas/plan report produced by `idea-writer`. If the user has not yet finished the work, push back: a paper requires results.

Use `skills/_shared/writing-workflow.md` for KB loading, citation handling, missing references, output formats, and Typst/diagram mechanics. The manuscript-specific rules below override shared defaults when venue templates or figure-first sequencing require it.

---

## The Iron Rules

These seven override everything else.

1. **Figures first, then prose.** Plot every figure you intend to publish *before* writing a single section. Figures are the backbone; the text serves them. If you cannot draw the story in 4–8 figures, you do not yet know the story.
2. **Polish what readers actually read.** 95% of readers read only the title, abstract, introduction, figures + captions, and conclusions. These five elements deserve disproportionate iteration. Write them last — *but iterate them most*.
3. **State main results explicitly.** Use at least one sentence per main result that names it as such: *"This figure / equation / observation is our (first / second / Nth) main result."* Do not assume the reader will identify which sentence is the punchline.
4. **One concept per sentence.** If you must break this rule, both concepts must be simple. Long compound sentences with three new ideas are how readers drop out.
5. **Never plot anything in arbitrary units.** If you find yourself reaching for "a.u." on an axis, the axis is wrong — find the right normalization (dimensionless ratio, calibrated scale, or experimental control). This is non-negotiable; "a.u." plots are a known integrity red flag.
6. **Target journal before story.** Before proposing story lines, discuss the target journal or venue with the user and download the official author template; if the user deliberately has no target yet, record that choice. Venue constraints shape the narrative, figure count, length, and format.
7. **Iterate the story with the user.** Once the figures or figure plan are available and the target venue is known, propose 1–3 plausible story lines for the user to choose, reject, or combine. Do not draft prose until the user has selected the paper's narrative.

---

## Workflow Phases

A correct ordering of effort that defeats writer's block. Do not reorder — the sequence is the point.

### Phase 0 — Load context

Before drafting, gather the materials that should inform the paper. Cheap to do once; expensive to skip.

1. **Shared writing context.** Follow `skills/_shared/writing-workflow.md`. Use `$KB/NOTES.md` as the spine for prior work, gap statement, motivation, and conclusions.
2. **Ideas / brainstorming log.** Look for `docs/discussion/*-brainstorm-ideas-log.md` from a prior `/brainstorm-ideas` session. If present, read it for: the original motivation, what cross-field connections were surfaced, what minimum viable experiment was planned, and what the success/hope/pivot signals were. This is the *why* behind the paper and feeds the introduction's contribution claim.
3. **Personal publication context.** Read `docs/discussion/user-profile.md` and any `researchstyle` notes in `$KB/NOTES.md`. Use them to position the new paper in the user's own arc and to avoid re-citing the user's own work incorrectly.
4. **Existing draft.** If a partial manuscript already exists under `articles/`, read it before proposing new prose — pick up where the user left off rather than starting from a blank slate.

If none of these exist, name what's missing and ask the user to either point at the files or run `/survey` first. A paper without a literature foundation will read like one.

### Phase 1 — Set up the figures (before writing any prose)

- List the figures the paper needs. Aim for 4–6 in a letter, 6–10 in a regular article.
- Order them so they *tell a story*: simple data first → progressively complex analysis → flagship comparison with theory.
- Draft each figure. Apply the **Figure Rulebook** (below). Do not move on until line weights, axes, colors, and dimensionless choices are right — going back later is more expensive than getting it right now.
- For each figure, write a one-sentence caption-summary: what the figure *shows* in plain words. These become the spine of the captions and the Results section.

### Phase 1.5 — Target journal and template checkpoint

Before the story checkpoint, stop and discuss the target journal or venue with the user. If the user has not chosen one, propose 2–3 plausible venues with tradeoffs: article type, audience, length pressure, figure limits, novelty bar, and format requirements. Ask the user to pick one target or explicitly choose "no target yet." If they choose no target yet, record that no official template can be selected and continue only after they confirm this tradeoff.

Once a target is chosen:

1. Find the official author instructions and template from the journal or publisher website. Prefer official publisher pages over mirrors, GitHub copies, Overleaf community templates, or lab handouts.
2. Download the template package into the active manuscript directory, usually `articles/YYYY-MM-DD-<paper-slug>/template/`. If no manuscript directory exists yet, create the article directory first.
3. Record the template source URL, access date, journal name, article type, and key constraints in a short `template/README.md` or manuscript note.
4. If the official template cannot be downloaded, explain why, save the author-instruction URL, and ask the user whether to continue with a generic draft format.
5. Do not propose story lines until the target venue and template status are clear.

### Phase 1.6 — Story checkpoint with the user

Before the telegram outline, stop and discuss the paper's narrative with the user. Base this only on the provided figures, caption-summaries, existing draft, loaded literature context, and target-journal constraints.

1. Propose **1–3 candidate story lines** for the user to pick from. If there is only one defensible story, present one strong option and say why alternatives would be forced.
2. For each story line, include:
   - the central claim in one sentence,
   - the figure order and what each figure contributes,
   - the hierarchy of main results,
   - the audience or venue fit,
   - what the story deliberately de-emphasizes.
3. Ask the user to choose one, combine pieces, or reject them. If they push back, revise the story lines and ask again.
4. Only after the user selects or synthesizes a story, continue to the telegram outline. Treat the selected story as the contract for the draft.

### Phase 2 — Telegram outline

- Write a telegram-style outline from the selected story line: section headings → bullet points → which figures and equations land where.
- Mark which sentence in each section names a main result.
- Show the outline to a collaborator/advisor before you write prose. Cost of revision is lowest now.

### Phase 3 — Draft the body in this order

1. **Methods / Theory** — easiest to write; gets you over the activation barrier.
2. **Results** — walk the reader through the figures in order. For each figure: state what was varied (x-axis), what was measured (y-axis), what trend appears, where errors come from. Data is obvious to you, not the reader.
3. **Analysis** — explain how the data matches (or stretches) the theory. Plot data as points, theory as lines, on the same axes; arrange so theory lies on straight lines whenever possible. Discuss deviations larger than error bars *and* deviations much smaller than them (both are problems).
4. **Introduction (rough draft).** Do not perfect it yet. Hit four beats: (a) field-level question and why it matters, (b) prior work and what was missing, (c) what *this* paper does, (d) where the main results live (figure / equation pointers). Move on even if it feels weak.
5. **Conclusions.** Often a re-statement of the introduction in newly technical language — the reader now has the apparatus to absorb it. Add one paragraph on implications, applications, and follow-up directions. Acknowledgments and funding here.

### Phase 4 — Iterate the body

- Revise the body many times before touching abstract/intro polish.
- Each pass: check the **One Concept Per Sentence** rule, check notation consistency, check that every striking feature in every figure is *explained in text*.

### Phase 5 — Polish the high-leverage sections last

- **Abstract:** one paragraph, 5–10 lines, ~one sentence per body section. Write it last, when you finally understand what the paper says.
- **Title:** descriptive, specific, scannable. Rewrite several times.
- **Introduction:** sharpen the opening hook, the gap statement, the contribution claim, and the forward-pointers to figures.
- **Conclusions:** make the take-home messages crisp and quotable.

### Phase 6 — External feedback

- Send to a friend / officemate who is *not* a co-author.
- Solicit comments from a known expert in the area. Most will oblige if you mention a deadline. Consider sending to known competitors as a goodwill gesture — they catch what reviewers will catch.
- Take every comment seriously. "Confusing to a friend" → "confusing to a reviewer."

---

## The Seven-Section Template (Martinis structure)

Most physics-style papers fit this. Short letters (PRL, Nature, Science) drop the section headers but the reader still parses these seven roles.

| § | Section | Purpose | Length cue |
|---|---|---|---|
| 1 | **Title & Abstract** | Advertisement: get the reader to open the paper. | One paragraph, 5–10 lines. |
| 2 | **Introduction** | Why the field cares, prior work, what's new here. Hardest section; most important for acceptance. | 0.5–1.5 pages. |
| 3 | **Theory / Background** | Minimum theory needed to interpret the experiment. State assumptions, give formulas without long derivations (assume expert reader). | As short as possible. |
| 4 | **Experimental Methods** | Document what was done so the experiment is reproducible. Be concise — state, don't explain — *except* for tricky, unusual, surprising steps, which should be written out fully. | Compact. |
| 5 | **Results** | A sequence of figures telling a story, simple → complex. Walk the reader through each plot's axes, trends, and error sources. | Bulk of the paper, with Analysis. |
| 6 | **Analysis** | Compare data to theory. Discuss where deviations come from. Introduce check experiments and any extra theory needed. Often merged with Results. | Bulk of the paper, with Results. |
| 7 | **Conclusions** | What was learned. Implications and future directions. Acknowledgments and funding. | Short — one to two paragraphs plus acks. |

**Cross-cutting:** Use references aggressively — citing a prior result is cheaper than re-deriving it, and a reference is the politest way to credit prior work.

---

## Figure Rulebook

Figures are what readers remember; design them to survive the harshest viewing context.

**Design for three uses simultaneously.** Each figure must work as: (a) inline figure in the paper, (b) slide in a beamer talk, (c) greyscale photocopy. Optimize at draft time, not as a post-hoc retrofit.

**Line weight.** Minimum thickness 2 for every curve (or at least the main-result curves). Thin lines vanish on a projector.

**Color discipline.**
- Use saturated, robust colors: black, blue, red, dark orange, magenta, violet, dark brown.
- Avoid light yellow, light green, light grey — invisible when projected.
- Encode the distinction with a *line style* (solid / dashed / dash-dot) in addition to color, so the figure survives greyscale printing.
- In the caption, refer to features by line style, not color: "the dashed curve" not "the red curve". Add "(Color online)" if color matters.

**Text size.** Axis labels, numbers, and legend text should not be much smaller than the surrounding paper text — at most 2/3 of body size. Tiny text wrecks the figure for talks.

**Parameter labels.** Place key parameters (e.g., `T = 0`, `V = 0`, `Γ = 1`) directly inside the plot in small boxes. Saves caption length and makes the figure self-contained for talks.

**Dimensionless axes.** Use dimensionless quantities (`G/G₀`, `T/Γ`, `V_g/Γ`, etc.) whenever possible — they generalize the result, clarify the relevant scale, and travel across systems. Choose the combination that maximizes message clarity; if you find a better one after plotting, replot. Exception: comparison with dimensional experimental data.

**Data vs. theory.** Plot data as points (with error bars) and theory as lines, on the same axes. Arrange so theory lines are *straight* whenever possible — anyone can then check agreement at a glance. Use curved-theory plots only with a deliberate reason.

**Error-bar reasoning.** Theory should pass through error bars on most points. Patterns to *discuss in text*:
- Many points deviating by more than an error bar → likely systematic error, must be addressed.
- Error bars dwarfing the deviations → uncertainties likely overestimated, also addressed.

**Captions.** Concise but self-sufficient. Define every plotted quantity, summarize the trend, identify line styles. A reader who reads only the title, abstract, and figures+captions should get the paper.

**Explain every striking feature.** Every peak, dip, kink, or jump that catches the eye must be discussed in the main text — ideally with a back-of-envelope reason. Unexplained features are either an honesty problem or a missed opportunity. If you genuinely don't understand a feature, say so in print and flag it for follow-up.

---

## Notation Rulebook

Notation is the reader's interface to the math. Treat it with the same care as a public API.

- **No symbol reuse in nearby sections.** Same letter must not mean two different things within a few pages.
- **If notation must change, signal it explicitly.** "Henceforth we use X to denote..." — never silent reuse.
- **Define every variable before using it.** And define them in a logical order — symbols introduced earlier should be used to define symbols introduced later, not the other way around.
- **If a better notation appears mid-project, switch and rewrite earlier sections.** The reader's cost of decoding bad notation is far higher than your cost of rewriting.
- **Compact vs. explicit formulas:**
  - *Compact* when summarizing strategy, manipulating reader's high-level model, or when an expert could fill in the steps.
  - *Explicit* when: highlighting a non-obvious step, presenting a trick that took real effort, showing a key intermediate result other work depends on, presenting a flagship result, or matching a plotted figure (cite the figure in the equation).

---

## Sentence-Level Rules

- **One concept per sentence.** Break long sentences. If two concepts must coexist, make sure both are already familiar to the reader.
- **Active voice for actions.** "We measured" beats "measurements were performed." Reserve passive only for things genuinely without an agent.
- **Concrete verbs over nominalizations.** "We adopt the new notation" beats "Adoption of the new notation is undertaken."
- **Parallel structure for parallel ideas.** Lists, comparisons, and contrasts read 2× faster when grammatically parallel.
- **Signposting.** Use phrases like *"This is our main result," "We now turn to," "In summary,"* to orient the reader. The reader cannot tell which sentence carries the punchline unless you say so.
- **Each paragraph: one job.** Topic sentence at the top, supporting detail in the middle, transition or stress at the end.

---

## Pre-Submission Checklist

Run this before clicking submit. Each item is cheap to check; missing any of them is expensive to fix in proof.

**High-leverage text (read by 95%):**
- [ ] Title is descriptive, specific, scannable.
- [ ] Abstract reads as a one-paragraph summary, one sentence per body section.
- [ ] Introduction has all four beats (field interest, prior work, what's new, where main results live).
- [ ] Every figure has a caption that stands alone.
- [ ] Conclusions name the contribution and at least one implication.

**Main-result labeling:**
- [ ] Target journal or "no target yet" was discussed with the user before story selection.
- [ ] Official template was downloaded, or the failed/blocked/not-applicable template status was recorded.
- [ ] The user selected or synthesized a story line before prose drafting began.
- [ ] Each major result has a sentence explicitly tagging it as a main result.
- [ ] Each main result has a corresponding figure or equation.

**Figures:**
- [ ] All curves are line-weight ≥ 2.
- [ ] All colors are saturated; no faint yellow/green/grey.
- [ ] Each figure is identifiable in greyscale (line styles distinguish, not just color).
- [ ] Axis numbers and legend text are readable from a slide.
- [ ] No axis labeled in arbitrary units.
- [ ] Every striking feature is explained in text.
- [ ] Data as points + theory as lines, plotted together, with straight theory lines where possible.

**Notation and equations:**
- [ ] No symbol reuse for different meanings.
- [ ] Every symbol defined before use, in logical order.
- [ ] Explicit equations only for non-obvious steps, key intermediates, flagship results, or figure references.

**Sentence-level:**
- [ ] No paragraph contains more than one new concept per sentence.
- [ ] Active voice dominates.
- [ ] Topic sentences open each paragraph.

**External feedback:**
- [ ] At least one friend / officemate has read the full draft.
- [ ] At least one expert outside the author list has commented (when feasible).
- [ ] Comments have been addressed, not deflected.

---

## When stuck

| Symptom | Action |
|---|---|
| Cannot start writing introduction | Skip it. Write Methods or Theory first; loop back later. |
| Notation feels awkward | Stop. Redesign notation now. Cost grows linearly with pages written. |
| Figure looks "fine" but feels off | Test it: project on a screen + print in greyscale. The problem will reveal itself. |
| Cannot decide what the "main result" is | You don't have a paper yet. Go back to brainstorming (`/brainstorm-ideas`) or surveying (`/survey`). |
| Co-authors keep proposing reorganizations | Lock the figure list first; the body follows the figures. |

---

## Integrations

- **Citations and missing references:** Follow `skills/_shared/writing-workflow.md`.
- **Manuscript format:** Use the target journal's official template when available. Default to Typst (`.typ`) only when no target venue or required template exists; use LaTeX (`.tex`) or Word when the journal requires it; use Markdown only for arXiv-style preprints where the journal accepts it.
- **Storing the draft:** `articles/YYYY-MM-DD-<paper-slug>/` with `main.typ` (or `.tex`), a bibliography copied from `ref.bib`, and `figures/`.

---

## Source material

- `references.md` — distilled rule lists from Martinis (2012) and von Delft (style guide).
- `sources/NotesOnWritingPaper12.pdf` — the original Martinis notes.
- von Delft's *Style Guide* online: <https://homepages.physik.uni-muenchen.de/~vondelft/JansStyleGuide.html>

Consult the references when this SKILL.md leaves a judgment call open. The point of the references is to preserve the *reasons* behind the rules.
