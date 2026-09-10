# Writing checklist

The checkable form of the rules in `SKILL.md`. Use it as the checklist for a `write-paper` language pass or a `review-paper` writing pass. Guidelines 2, 5, and 7 apply the `write-paper` Notation and Figure Rulebooks. See `skills/write-paper/references.md` for the reasoning. Guideline numbers match `review-paper/SKILL.md`; guidelines 6, 8, and 9 are review process and live in `skills/review-paper/checklist.md`.

---

## 1 — One concept per sentence

- [ ] No sentence introduces three new ideas at once. Long compound sentences are split.
- [ ] When two concepts share a sentence, the reader already knows both.
- [ ] Actions use the active voice. Concrete verbs replace nominalizations.
- [ ] Parallel grammar appears only where the ideas already run in parallel. No prose is turned into lists.
- [ ] Sentences run about 20 words. No sentence chains clauses with semicolons or "and … so …". A sentence that wraps a display equation or binds a hypothesis to its conclusion stays whole.
- [ ] No content-free openers, "Notice that", or empty meta-talk. Signposts that name a section's job or point to a result stay.
- [ ] No "obviously" or "clearly". Each asserted step names the earlier equation, figure, or section it rests on. That reason already exists in the manuscript.
- [ ] Simple words are used and every technical word is kept. No verb, quantifier, or adjective is swapped inside a mathematical statement. No metaphor stands in for a precise statement. No finding on this rule asks a conceptual figure for more detail.
- [ ] At most one aside per paragraph. No intensifiers. Hedges of magnitude or certainty are untouched. "Not X but Y" stays where the contrast is the result.
- [ ] Runs of inline computation are moved to one display. One sentence names what the display shows.
- [ ] No sentence re-describes what a nearby equation, table, or figure shows. At most one clause points at it.
- [ ] Every promise ("we will show", "surprisingly", "the key link") is paid by a later result, theorem, or figure.

## 2 — Define every concept/symbol before use

- [ ] A symbol and notation table was built while reading.
- [ ] No symbol or concept is used before it is defined. No forward references.
- [ ] No symbol is left never defined.
- [ ] No term or symbol is defined before the argument needs it. Every definition is used later.
- [ ] Each derivation is preceded by the system, the assumptions or boundary conditions, the symbols, and the quantity being computed.
- [ ] Symbols are introduced in logical order. Earlier symbols define later ones.
- [ ] No symbol is reused for two meanings within a few pages. Any deliberate change is signalled with "henceforth …".

## 3 — One job per paragraph

- [ ] Each paragraph has one identifiable purpose.
- [ ] A topic sentence opens each paragraph. No paragraph does double duty.
- [ ] Each section delivers the mission stated for it in Phase 0.
- [ ] In Theory, Methods, Results, and Analysis, each paragraph stays on one object. No sideways digression, preview, or unused second interpretation. Introduction and Conclusions are exempt.
- [ ] Each cross-reference is needed by the current step. The sentence says why.

## 4 — DRY / anti-repetition (new)

- [ ] No explanation or definition is repeated across body sections. The abstract, introduction, conclusions, and main-result sentences are exempt.
- [ ] Each concept is stated once in canonical form and cross-referenced elsewhere.
- [ ] Any repetition kept for emphasis is deliberate, not accidental drift.
- [ ] A second appearance of a fact is a pointer, never a restatement.
- [ ] No number, count, or list is stated in two places that can drift. Abstract and conclusions are exempt.
- [ ] Every sentence passes the delete test: removing it leaves a gap something later in the section depends on.

## 5 — Display-math discipline

- [ ] Display equations are reserved for flagship results, non-obvious steps, key intermediates, or equations referenced by a figure.
- [ ] Routine algebra that fits inline is not promoted to a display equation.
- [ ] No equation with a referenced label is proposed for inlining or cutting. In a letter, algebra moves to the supplement rather than losing a reproducibility step.

## 7 — Figure integration

- [ ] Every figure is referenced at least once in the main text. No orphan figures.
- [ ] Every striking feature, such as a peak, dip, kink, or jump, is discussed in the text.
- [ ] Captions stand alone. Every plotted quantity is defined and the trend is summarized.
