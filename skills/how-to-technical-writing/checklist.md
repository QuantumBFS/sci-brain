# Writing checklist

The checkable form of the rules in `SKILL.md`. Use it as the checklist for a `write-paper` language pass or a `review-paper` writing pass. The five sections below group items by topic; their numbers are not the guideline numbers in `review-paper/SKILL.md`. Sentence structure and wording cover guideline 1; paragraph focus and information flow bring together items from guidelines 1, 3, and 4; definitions and notation cover guideline 2; equations and figures bring together items from guidelines 1, 5, and 7. Guidelines 2, 5, and 7 apply the `write-paper` Notation and Figure Rulebooks. See `skills/write-paper/references.md` for the reasoning. Guidelines 6, 8, and 9 are review process and live in `skills/review-paper/checklist.md`.

---

## 1 — Sentence structure

- [ ] No sentence introduces multiple new ideas at once. Long compound sentences are split.
- [ ] When two concepts share a sentence, the reader already knows both.
- [ ] Parallel grammar appears only where the ideas already run in parallel. No prose is turned into lists.
- [ ] Sentences run about 20 words. No semicolon chains, “and … so …” chains, paired em-dash asides, or paired-comma appositives.
- [ ] A sentence that wraps a display equation or binds a hypothesis to its conclusion stays whole.

## 2 — Wording and tone

- [ ] Prefer active voice. Concrete verbs replace nominalizations.
- [ ] No content-free openers, "Notice that", or empty meta-talk. Signposts that name a section's job or point to a result stay.
- [ ] Simple words are used and every technical word is kept. No verb, quantifier, or adjective is swapped inside a mathematical statement.
- [ ] No metaphor.
- [ ] Avoid “X, not Y”. State X directly.
- [ ] Replace vague abstract nouns (“property,” “system,” “structure,” ...) with the specific concept they refer to.
- [ ] Use literal verbs. Do not use metaphorical verbs (“unlock”, “bridge”, "open", ...).

## 3 — Paragraph focus and information flow

- [ ] Each paragraph has one identifiable purpose.
- [ ] A topic sentence opens each paragraph. No paragraph does double duty.
- [ ] In Theory, Methods, Results, and Analysis, each paragraph stays on one object. No sideways digression, preview, or unused second interpretation. Introduction and Conclusions are exempt.
- [ ] Use a cross-reference only when it supports the sentence. Explain the connection.
- [ ] No "obviously" or "clearly". Each asserted step names the earlier equation, figure, or section it rests on. That reason already exists in the manuscript.
- [ ] At most one aside per paragraph. No rhetorical intensifiers. Hedges of magnitude or certainty are untouched.
- [ ] No explanation or definition is repeated across body sections. The abstract, introduction, conclusions, and main-result sentences are exempt.
- [ ] Each concept is stated once in canonical form and cross-referenced elsewhere.
- [ ] Any repetition kept for emphasis is deliberate, not accidental drift.
- [ ] A second appearance of a fact is a pointer, never a restatement.
- [ ] No number, count, or list is stated in two places that can drift. Abstract and conclusions are exempt.
- [ ] Do not repeat information already visible in a nearby equation, table, or figure. State the relevant conclusion or implication.
- [ ] Every sentence passes the delete test: removing it leaves a gap something later in the section depends on.

## 4 — Definitions and notation

- [ ] A symbol and notation table was built while reading.
- [ ] No symbol or concept is used before it is defined. No forward references.
- [ ] No symbol is left never defined.
- [ ] No term or symbol is defined before the argument needs it. Every definition is used later.
- [ ] State the assumptions, define the symbols, and identify the target before a derivation.
- [ ] Symbols are introduced in logical order. Earlier symbols define later ones.
- [ ] Do not reuse a symbol for a different meaning in the same section or argument.

## 5 — Equations and figures

- [ ] Do not use inline calculations. Use a display instead.
- [ ] Display equations are reserved for flagship results, non-obvious steps, key intermediates, or equations referenced by a figure.
- [ ] Routine algebra that fits inline is not promoted to a display equation.
- [ ] No equation with a referenced label is proposed for inlining or cutting. In a letter, algebra moves to the supplement rather than losing a reproducibility step.
- [ ] Every figure is referenced at least once in the main text. No orphan figures.
- [ ] Every striking feature, such as a peak, dip, kink, or jump, is discussed in the text.
- [ ] Captions stand alone but stay concise. Every plotted quantity is defined and the trend is summarized. Keep experimental settings and procedural details in the main text.
