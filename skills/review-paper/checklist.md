# Paper-reviewer process checklist

The review-only items behind `review-paper/SKILL.md`: scope and context (6), fact and reference verification (8), journal fit (9), and delivery. The writing items (1–5, 7) live in `skills/how-to-technical-writing/checklist.md`, the single source of truth for the writing guide.

---

## 6 — Scope and scientific context

- [ ] Scope and revision authorization were taken from the request; clarification was limited to missing information that changes the review.
- [ ] A full scientific review read the whole manuscript and bibliography; a local pass read the target and necessary dependencies.
- [ ] A full review includes the story, question, contributions, results tied to evidence, and section missions. Local wording checks do not require a story brief.
- [ ] The existing story was reused; only a material unresolved interpretation prompted a question.
- [ ] When option 1 was selected, high-level comments were made on each of the items below.
  - The significance of the problem: who is blocked, what it unlocks, and the strongest prior attempt. `survey` is suggested when the manuscript or KB cannot justify it.
  - The significance of each contribution. It is stated as a verifiable property, verified by a result, and better than the strongest baseline on an axis the audience names.
  - The story. The contribution matches the results and the gap is supported.
  - The abstract. Its moves are mapped to the brief. Unbacked or missing claims are named.
  - The main figure. It carries the central claim alone, or no such figure exists.
  - The supporting data. Claims without data, missing controls, baselines, and error bars are named. The evidence is strong enough for the claim as worded. General claims span systems or seeds. Improvements are separated from the baseline by error bars or a test. Scaling laws span enough decades. State-of-the-art claims are measured against the strongest baseline under the same conditions.
  - How the contributions are highlighted. They are named in the abstract, listed in the introduction, and each tied to its proving figure or equation. A better main figure, summary table, title sentence, or ordering is proposed when one exists.
- [ ] The selected passes were completed before delivering the report, unless missing scientific input prevented an assessment.

## 8 — Fact & reference verification (new)

- [ ] Skipped entirely, with a note in the report, when the user did not select option 3 in Phase 0. Otherwise:
- [ ] For a full review or bibliography audit, `verify_bib.py` screened every entry, including uncited entries. For a targeted check, only requested claims and their supporting entries were verified directly, and the limited scope was reported.
- [ ] Metadata fields in the checked scope were verified; full screening compares title, authors, year, venue or journal, volume, pages, and DOI against cached and batched Semantic Scholar metadata.
- [ ] Every `unverifiable` record was confirmed by hand before reporting. So was every `mismatch` with a high or medium finding. The chain is CrossRef → Semantic Scholar → MCP → web fetch. Low-severity missing fields remain completion suggestions.
- [ ] Every `\cite` key in the checked scope resolves to an entry in the bibliography that was actually used.
- [ ] Broken, missing, or mismatched citations are flagged. Repair is offered via the `how-to-download-ref` skill.
- [ ] Key claims attached to a citation are sanity-checked against the cited work. Uncertain ones are flagged, not asserted.
- [ ] Standalone checkable factual or numerical claims in scope are verified via web search. Uncertain ones are flagged.
- [ ] Relevant URLs and DOI links were checked for a targeted request; every manuscript/bibliography link was checked for a full review. Dead links, wrong redirects, and unresolvable DOIs are flagged.
- [ ] **No BibTeX invented from memory. No claim silently "corrected". No citation fabricated.**

## 9 — Journal fit (new)

- [ ] Skipped, with a note in the report, when the user did not select option 4 or chose "no target yet". Otherwise:
- [ ] The target journal was taken from the manuscript's declared venue or `template/README.md`. Otherwise it was recommended per `write-paper` Phase 1.5 and confirmed by the user.
- [ ] The official author guidelines were fetched this session or reused from `template/README.md`. The source URL and access date are recorded.
- [ ] Constraints were extracted into a table. It covers limits on body, abstract, and title, the figure, table, and reference maxima, the required sections and their order, the required statements, the formatting rules, and the journal's own writing guidance. Required statements include data and code availability, author contributions, competing interests, funding, ethics, keywords, and significance.
- [ ] Each constraint was measured against the manuscript. Word counts come from compiled text, counts from source, and sections from headings. Each has a status of ok, over, missing, or unverifiable.
- [ ] The abstract, opening paragraph, and significance framing were reviewed against the journal's stated audience and writing guidance.
- [ ] **No limit or rule is quoted from memory. Unfetchable guidelines are marked unverifiable with the URL.**

---

## Language-pass hunt table (guidelines 1, 3, 4, 5)

The checkable items live in `skills/how-to-technical-writing/checklist.md`. The hunt-for / fix table lives in `skills/how-to-technical-writing/SKILL.md`, shared with `write-paper`. Each finding cites its row. Rows marked **comment only** stay comments within a language pass; a separately requested substantive revision needs supporting evidence.

## Delivery & application

- [ ] Full-review findings are saved to the requested path or `articles/<slug>/review-YYYY-MM-DD.md`; a small excerpt review can be delivered inline. Findings are located and ranked by severity.
- [ ] A reference and fact-check table is included when that pass applies.
- [ ] A journal fit table (constraint → required → measured → status) with the guideline source is included. Otherwise a line says the pass was skipped.
- [ ] A prioritized "top fixes" list is included.
- [ ] The chosen direct/diff mode was reused. Already requested edits continued without asking for the same authorization; a proposal beyond that scope was prepared before requesting a decision.
- [ ] In marked-diff mode, edits went to a `*.proposed.*` copy. `latexdiff` produced the marked version, or `git diff --word-diff` for Typst and Markdown. A numbered legend was handed over. Only the accepted numbers were merged. The proposed and diff files were deleted afterwards.
- [ ] Applied edits stayed within the existing user authorization; a review-only request did not modify the original.
- [ ] LaTeX, Typst, and Markdown structure and macros are preserved. Author-judgment fixes are left as `% [reviewer]` comments.
- [ ] Language edits changed how sentences are written, never what they say. No definition, theorem, claim, or field term was altered. Numbers and qualifiers were rechecked after every rewrite.
- [ ] Fixes touching a quantifier, hedge, missing justification, paragraph deletion, or "not X but Y" contrast were left as `[reviewer]` comments, not applied.
- [ ] Changed document source was compiled and the result reported. Inline-text checks did not claim a document build.
- [ ] A changelog was appended to the top of the review report.
