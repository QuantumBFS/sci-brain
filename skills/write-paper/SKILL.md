---
name: write-paper
description: User trigger. Use when drafting or revising a scientific manuscript with real results.
---

## Installed resources

Keep the working directory at the user's project. Resolve this `SKILL.md` to its
real path before locating bundled resources. `skills/<name>/...` refers to the
installed skill found by public name, not the user's project; dependencies need
not be siblings. Load only resources needed for the current task. If a required
dependency is missing, report it before that dependent step.


# Paper Writer

A working-rules guide for writing scientific papers, distilled from John Martinis's *Notes on Writing a Scientific Paper* and Jan von Delft's *Style Guide*. The source documents live in `references.md` and `sources/`; consult them when this SKILL.md leaves a question open. Beside them sits a model letter that executes these rules — Ho et al., PRL 122, 040603 (2019), see Source material. Use its relevant examples when a style judgment is unresolved, adapting to the manuscript and venue.

**Scope note.** This skill is for *real manuscripts* — papers reporting completed (or near-complete) experimental, theoretical, or computational results. It is **not** for the upstream ideas/plan report produced by `brainstorm-ideas` report mode. If the user has not yet finished the work, push back: a paper requires results.

Use `skills/how-to-write-ideas-report/references/writing-workflow.md` for KB loading, citation handling, missing references, output formats, and Typst/diagram mechanics. Venue requirements take precedence over formatting defaults; the shared guide remains the source of sentence-level rules.

---

## Choose the scope

- **New manuscript:** default to the guided phases below, including unresolved
  venue, story, and outline decisions with the user before full prose. The
  supplied result, figure plan, or proof provides the evidence for those choices.
- **Continue an existing draft:** reuse its story, venue, outline, and figures.
  Enter at the unfinished part and verify affected dependencies.
- **Broad revision or polish of an existing manuscript:** use `review-paper`
  and carry forward the requested scope and application mode. With no mode
  established, prepare a marked proposal before changing the original; reuse
  direct-edit instructions or accepted findings without another approval.
- **Local revision:** change only the requested section, abstract, caption, or
  passage, using its necessary context. Do not restart figure production,
  venue selection, or story approval. For a critique rather than revision, use
  `review-paper`.
- **Submission preparation:** apply the target venue's current requirements
  and the relevant final checks.

Carry forward choices and authorization from the conversation. A generic
"help me write a paper" uses the guided workflow; it does not by itself waive
the initial checkpoints. A supplied or previously approved venue, narrative,
or outline satisfies the corresponding checkpoint. If the user delegates the
remaining writing choices and asks for a complete draft without checkpoints,
state the choices you make and proceed, asking only for missing scientific
input that cannot be inferred. Never manufacture results,
references, or an unsupported claim. A writing request ends with the requested
text/source and appropriate checks; external feedback is optional.

## Writing priorities

Use figures, evidence, or a proof outline to organize the story. State each main
result clearly and connect it to its evidence. Give the title, abstract,
introduction, captions, and conclusions careful attention because readers use
them to judge the paper. Follow the shared style guide rather than imposing a
fixed sentence length or a template from a different scientific genre.

## Workflow for a new manuscript

Use the phases that the work still needs. For a theoretical result, a proof and
its key statements can serve the role of figures; a fixed figure count is not an
entry requirement.

### Phase 0 — Load context

Before drafting, gather the materials that should inform the paper. Cheap to do once; expensive to skip.

1. **Shared writing context.** Follow `skills/how-to-write-ideas-report/references/writing-workflow.md`. Use `$KB/NOTES.md` as the spine for prior work, gap statement, motivation, and conclusions.
2. **Ideas / brainstorming log.** Look for `docs/discussion/*-brainstorm-ideas-log.md` from a prior `brainstorm-ideas` session. Read only logs relevant to this manuscript, starting with their summaries, for motivation, planned experiments, and success/hope/pivot signals. This is the *why* behind the paper and feeds the introduction's contribution claim.
3. **Personal publication context.** When positioning or self-citation requires it, read the relevant parts of `docs/discussion/user-profile.md` and `know-me-better` notes in `$KB/NOTES.md`. Use them to position the new paper in the user's own arc and to cite the user's earlier work correctly.
4. **Existing draft.** If a partial manuscript already exists under `articles/`, read it before proposing new prose; pick up where the user left off.

Use supplied source material even without a sci-brain KB. Research citation gaps needed by the draft; ask for missing results or assumptions that cannot be established from the available evidence.

### Phase 1 — Establish the evidence and figure plan

- List the figures or proof results needed to support the main claim; use the venue and argument to determine their number.
- Order them so they *tell a story*: simple data first → progressively complex analysis → flagship comparison with theory.
- Draft needed figures using the **Figure Rulebook** below. Resolve issues affecting interpretation before writing claims around them; visual polish can proceed alongside the draft.
- For each figure, write a one-sentence caption-summary: what the figure *shows* in plain words. These become the spine of the captions and the Results section.

### Phase 1.5 — Target journal and template checkpoint

Reuse a selected venue and installed template, including an existing decision
to draft without a target. For a new guided manuscript with no venue decision,
discuss plausible venues with audience, article type, length, novelty, and
format tradeoffs; let the user choose a target or "no target yet". For a local
revision, or when the user has delegated those choices and requested a draft,
do not reopen venue selection. If drafting without a target, record that status
and use the requested or existing format.

Once a target is chosen:

1. Find the official author instructions and template from the journal or publisher website. Prefer official publisher pages over mirrors, GitHub copies, Overleaf community templates, or lab handouts.
2. Download the template package into the active manuscript directory, usually `articles/YYYY-MM-DD-<paper-slug>/template/`. If no manuscript directory exists yet, create the article directory first.
3. Record the template source URL, access date, journal name, article type, and key constraints in a short `template/README.md` or manuscript note.
4. If the official template cannot be downloaded, record the limitation and source URL. Continue a content draft in the existing format; ask only if the requested deliverable requires a template choice that cannot be inferred.
5. Apply known venue constraints to the story and figures; identify requirements that remain unverified.

### Phase 1.6 — Story checkpoint with the user

Reuse a narrative supplied or already selected by the user. In a new guided
manuscript, present the proposed story for the user's decision before full
prose, even if only one story is defensible. When the user has delegated the
narrative choice, state the evidence-based story you select and proceed. Base
the story on the provided results, figures, existing draft, literature, and
venue constraints; missing results cannot be replaced by a writing choice.

When a narrative choice is still needed:

1. Propose **1–3 candidate story lines** for the user to pick from. If there is only one defensible story, present one strong option and say why alternatives would be forced.
2. For each story line, include:
   - the central claim in one sentence,
   - the figure order and what each figure contributes,
   - the hierarchy of main results,
   - the audience or venue fit,
   - what the story deliberately de-emphasizes.
3. Ask the user to choose one, combine pieces, or reject them. If they push back, revise the story lines and ask again.
4. Once the story is established, continue to the outline. Reopen that story only if new evidence changes the main claim.

### Phase 2 — Telegram outline

- Write a telegram-style outline from the selected story line: section headings → bullet points → which figures and equations land where.
- Mark which sentence in each section names a main result.
- Reuse a supplied or approved outline. In a new guided manuscript, show the outline before drafting full prose; it may accompany the story proposal so the user can approve both together. If the user delegated outline decisions or authorized drafting from the established plan, use it as a working note and continue. Do not require a separate external advisor to approve it.

### Phase 3 — Draft the body (a useful default order)

1. **Methods / Theory** — easiest to write; gets you over the activation barrier.
2. **Results** — walk the reader through the figures in order. For each figure: state what was varied (x-axis), what was measured (y-axis), what trend appears, where errors come from. Data is obvious to you, not the reader.
3. **Analysis** — compare data and theory under the stated uncertainty model. Investigate unexpected residuals rather than declaring large or small deviations an error by themselves; use the relevant Figure Rulebook guidance.
4. **Introduction (rough draft).** Do not perfect it yet. Hit four beats: (a) field-level question and why it matters, (b) prior work and what was missing, (c) what *this* paper does, (d) where the main results live (figure / equation pointers). The model letter executes all four in as many paragraphs, closing with "In this Letter, we develop…" — see `references.md` §C. Move on even if it feels weak.
5. **Conclusions.** Often a re-statement of the introduction in newly technical language — the reader now has the apparatus to absorb it. Add one paragraph on implications, applications, and follow-up directions. Acknowledgments and funding here.

### Phase 4 — Iterate the body

- Revise until the argument, notation, and evidence support the requested draft. Repeat a pass only for a changed section, a failed check, or an unresolved finding.
- Each pass: check the **One Concept Per Sentence** rule, check notation consistency, check that every striking feature in every figure is *explained in text*.
- Last pass before Phase 5 is a **language pass**: walk the style guide's hunt table and change *how* sentences are written, never *what* they say. Do not add or remove a claim, figure, or derivation step in that pass; recheck every number and qualifier a rewritten sentence mentions; leave passages that already pass untouched.

### Phase 5 — Polish the high-leverage sections last

- **Abstract:** one paragraph, 5–10 lines, ~one sentence per body section. The model paper does it in four moves — system, method, finding, implication — one move per sentence. Write it last, when you finally understand what the paper says.
- **Title:** descriptive, specific, scannable. Refine it when it misstates or obscures the main claim.
- **Introduction:** sharpen the opening hook, the gap statement, the contribution claim, and the forward-pointers to figures.
- **Conclusions:** make the take-home messages crisp and quotable.

### Optional external feedback

- When useful, suggest feedback from a reader outside the author list. External sharing is a separate user decision, not a completion gate for drafting.
- If the user requests expert feedback, help prepare the material and questions; contact others only when explicitly authorized.
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

For figure creation or review, read the Figure Rulebook in
[figures-and-notation.md](references/figures-and-notation.md). Use intended display
size and scientifically meaningful axes; explain any normalization, including
arbitrary units when the measurement legitimately requires them.

## Notation Rulebook

For mathematical writing, read the Notation Rulebook in
[figures-and-notation.md](references/figures-and-notation.md). Local prose edits
need only the definitions and notation used by the affected passage.

## Sentence-Level Rules

Follow `skills/how-to-technical-writing/SKILL.md`: one concept per sentence, direct to the point, name the earlier context instead of "obviously", simple words with every technical word kept, no undrawn metaphors, active voice, one aside per paragraph, calculations in displays, locality within body sections, say it once within the body, signposting, and one job per paragraph. The guide's `checklist.md` and hunt table are the checklist for the Phase 4 language pass, and its guardrails say which fixes are never applied mechanically.

---

## Finish the requested deliverable

- Verify the requested sections say what the supplied results support and that
  citations resolve. For new or changed figures, inspect the render at its
  intended size using the Figure Rulebook. Check affected symbols and labels.
- For language changes, use `skills/how-to-technical-writing/checklist.md`;
  preserve logical connectives and mathematical meaning. Sentence length is a
  signal for overloaded clauses, not a word-count target.
- Compile changed source and resolve failures introduced by the change using
  the shared writing workflow. For an inline excerpt, check the text and state
  that no document build was run. Do not require a bibliography for a passage
  that contains no citations.
- For submission preparation, also check current venue limits, statements,
  template requirements, and unresolved author decisions. Do not submit or
  distribute the manuscript without authorization.
- Deliver the draft/source or revised excerpt, relevant verification, and any
  unresolved scientific questions. External reviews are not required to finish
  a writing task.

---

## When stuck

| Symptom | Action |
|---|---|
| Cannot start writing introduction | Skip it. Write Methods or Theory first; loop back later. |
| Notation feels awkward | Stop. Redesign notation now. Cost grows linearly with pages written. |
| Figure looks "fine" but feels off | Test it: project on a screen + print in greyscale. The problem will reveal itself. |
| Cannot decide what the "main result" is | You don't have a paper yet. Go back to brainstorming (`brainstorm-ideas`) or surveying (`survey`). |
| Co-authors keep proposing reorganizations | Lock the figure list first; the body follows the figures. |

---

## Integrations

- **Citations and missing references:** Follow `skills/how-to-write-ideas-report/references/writing-workflow.md`.
- **Manuscript format:** Preserve the requested or existing format. Use the target journal's required format for submission preparation; a content draft can remain in Markdown, Typst, or LaTeX until a venue is chosen.
- **Storing the draft:** `articles/YYYY-MM-DD-<paper-slug>/` with `main.typ` (or `.tex`), a bibliography copied from `$KB/references.bib`, and `figures/`.

---

## Source material

- `skills/how-to-technical-writing/SKILL.md` — the `how-to-technical-writing` skill: sentence- and paragraph-level rules shared with `review-paper`, with the hunt table and application guardrails.
- `references.md` — distilled rule lists from Martinis (2012) and von Delft (style guide), plus a walkthrough of the model paper (§C).
- `sources/NotesOnWritingPaper12.pdf` — the original Martinis notes.
- `sources/1807.01815_Ho2019_quantum-scars.md` — the model paper: Ho, Choi, Pichler & Lukin, *Periodic orbits, entanglement and quantum many-body scars in constrained models*, PRL 122, 040603 (2019), rendered from arXiv:1807.01815. This letter practices what the rules preach: one move per abstract sentence, the four introduction beats in order, run-in headers whose first sentence names the section's job, symbols defined at first use and then read back in plain words, figures that carry the story from page one. Read a relevant excerpt only when the distilled guidance leaves a style question open. `references.md` §C maps each move to its location in the paper.
- von Delft's *Style Guide* online: <https://homepages.physik.uni-muenchen.de/~vondelft/JansStyleGuide.html>

The references preserve the *reasons* behind the rules; the model paper shows the rules executed.
