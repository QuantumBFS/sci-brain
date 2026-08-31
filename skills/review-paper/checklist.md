# Paper-reviewer rubric

The eight-guideline review rubric backing `review-paper/SKILL.md`, expanded into checkable items. Use it as the per-pass checklist when reviewing a manuscript. Guidelines 1–3, 5, and 7 restate `write-paper` authoring rules as *review* checks — consult `skills/write-paper/references.md` for the reasoning. Guidelines 4, 6, and 8 are specific to reviewing.

---

## 1 — One concept per sentence

- [ ] No sentence introduces three new ideas at once; long compound sentences are split.
- [ ] Where two concepts share a sentence, both are already familiar to the reader.
- [ ] Active voice for actions; concrete verbs over nominalizations.

## 2 — Define every concept/symbol before use

- [ ] A symbol/notation table was built while reading.
- [ ] No symbol or concept is used before it is defined (no forward references).
- [ ] No symbol is left never-defined.
- [ ] Symbols are introduced in logical order (earlier symbols define later ones).
- [ ] No symbol is reused for two different meanings within a few pages; any deliberate change is signalled ("henceforth …").

## 3 — One job per paragraph

- [ ] Each paragraph has a single, identifiable purpose.
- [ ] A topic sentence opens each paragraph; no double-duty paragraphs.
- [ ] Each section delivers the mission stated for it in Phase 0.

## 4 — DRY / anti-repetition (new)

- [ ] No explanation or definition is repeated across sections.
- [ ] Each concept is stated canonically once and cross-referenced elsewhere.
- [ ] Repetition that *is* deliberate emphasis is intentional, not accidental drift.

## 5 — Display-math discipline

- [ ] Display equations are reserved for flagship results, non-obvious steps, key intermediates, or figure-referenced equations.
- [ ] Routine or inline-able algebra is not promoted to a display equation.

## 6 — Read the whole paper first (the gate)

- [ ] The whole manuscript and its bibliography were read before any critique.
- [ ] A one-paragraph story summary and a one-line mission per section were produced.
- [ ] **The story summary was confirmed with the user before findings were generated.**

## 7 — Figure integration

- [ ] Every figure is referenced at least once in the main text (no orphan figures).
- [ ] Every striking feature (peak, dip, kink, jump) is discussed in the text.
- [ ] Captions are self-sufficient: every plotted quantity defined, trend summarized.

## 8 — Fact & reference verification (new)

- [ ] `verify_bib.py` was run against the resolved bibliography; **every entry**, including uncited entries, appears in its report.
- [ ] Title / authors / year / venue or journal / volume / pages / DOI were screened against cached and batched Semantic Scholar metadata.
- [ ] Every `unverifiable` record and every `mismatch` with a high/medium finding was manually confirmed through CrossRef → Semantic Scholar → MCP → web fetch before reporting it; low-severity missing fields remain completion suggestions.
- [ ] Every `\cite` key resolves to an entry in the bibliography that was actually used.
- [ ] Broken / missing / mismatched citations flagged; repair offered via the `how-to-download-ref` skill.
- [ ] Key claims attached to a citation sanity-checked against the cited work; uncertain ones flagged, not asserted.
- [ ] Standalone checkable factual/numerical claims verified via web search; uncertain ones flagged.
- [ ] **No BibTeX invented from memory; no claim silently "corrected"; no citation fabricated.**

---

## Delivery & application

- [ ] Findings written to `articles/<slug>/review-YYYY-MM-DD.md`, grouped by guideline and severity-ranked.
- [ ] A reference/fact-check table (cite key → status → note) is included.
- [ ] A prioritized "top fixes" list is included.
- [ ] Edits applied only after user approval (all / by-severity / individual).
- [ ] LaTeX/Typst/Markdown structure and macros preserved; author-judgment fixes left as `% [reviewer]` comments.
- [ ] Manuscript re-compiled (`latexmk` / `pdflatex` / `typst compile`) and the result reported.
- [ ] A changelog appended to the top of the review report.
