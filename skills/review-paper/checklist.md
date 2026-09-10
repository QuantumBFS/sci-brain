# Paper-reviewer rubric

The eight-guideline review rubric backing `review-paper/SKILL.md`, expanded into checkable items. Use it as the per-pass checklist when reviewing a manuscript. Guidelines 1–3, 5, and 7 restate the `how-to-technical-writing` skill (`skills/how-to-technical-writing/SKILL.md`) and `write-paper` authoring rules as *review* checks — consult `skills/write-paper/references.md` for the reasoning. Guidelines 4, 6, and 8 are specific to reviewing.

---

## 1 — One concept per sentence

- [ ] No sentence introduces three new ideas at once; long compound sentences are split.
- [ ] Where two concepts share a sentence, both are already familiar to the reader.
- [ ] Active voice for actions; concrete verbs over nominalizations.
- [ ] Parallel grammar only where ideas already run in parallel; no prose converted into lists.
- [ ] Sentences run about 20 words; no semicolon-chained or "and … so …" triple clauses. Sentences wrapping a display equation or binding hypothesis to conclusion are left whole.
- [ ] No content-free openers, "Notice that", or empty meta-talk; signposts that name a section's job or point to a result stay.
- [ ] No "obviously" / "clearly"; each asserted step names the earlier equation, figure, or section it rests on, and that reason already exists in the manuscript.
- [ ] Plain connectives, every technical word kept; no verb, quantifier, or adjective swapped inside a mathematical statement; no metaphor the paper does not draw.
- [ ] At most one aside per paragraph; no intensifiers; hedges of magnitude or certainty untouched; "not X but Y" kept where the contrast is the result.
- [ ] Runs of inline computation moved to one display with one sentence naming what it shows.

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
- [ ] In Theory, Methods, Results, and Analysis, each paragraph stays on one object; no sideways digression, preview, or unused second interpretation. Introduction and Conclusions exempt.
- [ ] Each cross-reference is needed by the current step, and the sentence says why.

## 4 — DRY / anti-repetition (new)

- [ ] No explanation or definition is repeated across body sections; abstract, introduction, conclusions, and main-result sentences are exempt.
- [ ] Each concept is stated canonically once and cross-referenced elsewhere.
- [ ] Repetition that *is* deliberate emphasis is intentional, not accidental drift.

## 5 — Display-math discipline

- [ ] Display equations are reserved for flagship results, non-obvious steps, key intermediates, or figure-referenced equations.
- [ ] Routine or inline-able algebra is not promoted to a display equation.
- [ ] No equation with a referenced label is proposed for inlining or cutting; letters move algebra to the supplement rather than deleting a reproducibility step.

## 6 — Read the whole paper first (the gate)

- [ ] The whole manuscript and its bibliography were read before any critique.
- [ ] A story brief was produced: story paragraph, scientific question and its significance, numbered key contributions, key results each tied to a figure, table, or equation.
- [ ] A one-line mission per section was produced.
- [ ] High-level comments were made on the story (question worth asking, contribution matches results, gap supported), the abstract (moves mapped to the brief, unbacked or missing claims), the main figure (carries the central claim alone, or no such figure exists), and the supporting data (claims without data, missing controls, baselines, error bars).
- [ ] **The story brief and high-level comments were confirmed with the user before findings were generated.**
- [ ] The user chose which passes to run (writing / references and facts / both); on a repeat review the previous report was named and the default was writing only.

## 7 — Figure integration

- [ ] Every figure is referenced at least once in the main text (no orphan figures).
- [ ] Every striking feature (peak, dip, kink, jump) is discussed in the text.
- [ ] Captions are self-sufficient: every plotted quantity defined, trend summarized.

## 8 — Fact & reference verification (new)

- [ ] Skipped entirely, with a note in the report, when the user did not select this pass in Phase 0. Otherwise:
- [ ] `verify_bib.py` was run against the resolved bibliography; **every entry**, including uncited entries, appears in its report.
- [ ] Title / authors / year / venue or journal / volume / pages / DOI were screened against cached and batched Semantic Scholar metadata.
- [ ] Every `unverifiable` record and every `mismatch` with a high/medium finding was manually confirmed through CrossRef → Semantic Scholar → MCP → web fetch before reporting it; low-severity missing fields remain completion suggestions.
- [ ] Every `\cite` key resolves to an entry in the bibliography that was actually used.
- [ ] Broken / missing / mismatched citations flagged; repair offered via the `how-to-download-ref` skill.
- [ ] Key claims attached to a citation sanity-checked against the cited work; uncertain ones flagged, not asserted.
- [ ] Standalone checkable factual/numerical claims verified via web search; uncertain ones flagged.
- [ ] **No BibTeX invented from memory; no claim silently "corrected"; no citation fabricated.**

---

## Language-pass hunt table (guidelines 1, 3, 4, 5)

The hunt-for / fix table lives in `skills/how-to-technical-writing/SKILL.md`, shared with `write-paper`. Each finding cites its row. Rows marked **comment only** are never applied as edits, even after approval.

## Delivery & application

- [ ] Findings written to `articles/<slug>/review-YYYY-MM-DD.md`, grouped by guideline and severity-ranked.
- [ ] A reference/fact-check table (cite key → status → note) is included.
- [ ] A prioritized "top fixes" list is included.
- [ ] The user was asked whether to see a marked diff first or apply directly; marked diff is the default.
- [ ] In marked-diff mode: edits went to a `*.proposed.*` copy, `latexdiff` (or `git diff --word-diff` for Typst/Markdown) produced the marked version, a numbered legend was handed over, and only the accepted numbers were merged; proposed and diff files deleted afterwards.
- [ ] Edits applied only after user approval (all / by-severity / individual).
- [ ] LaTeX/Typst/Markdown structure and macros preserved; author-judgment fixes left as `% [reviewer]` comments.
- [ ] Language edits changed how sentences are written, never what they say; no definition, theorem, claim, or field term altered; numbers and qualifiers rechecked after every rewrite.
- [ ] Fixes touching a quantifier, hedge, missing justification, paragraph deletion, or "not X but Y" contrast were left as `[reviewer]` comments, not applied.
- [ ] Manuscript re-compiled (`latexmk` / `pdflatex` / `typst compile`) and the result reported.
- [ ] A changelog appended to the top of the review report.
