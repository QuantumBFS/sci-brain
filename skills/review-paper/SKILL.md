---
name: review-paper
description: User trigger. Use when reviewing, commenting on, or fact-checking an existing manuscript, including its references.
---

## Installed resources

Keep the working directory at the user's project. Resolve this `SKILL.md` to its
real path before locating bundled resources. `skills/<name>/...` refers to the
installed skill found by public name, not the user's project; dependencies need
not be siblings. Load only resources needed for the current task. If a required
dependency is missing, report it before that dependent step.

Before running the examples, set `DOWNLOAD_REF_DIR` to the absolute directory of `how-to-download-ref`. Quote these variables as shown.


# Paper Reviewer

Run a structured **review-and-enhance** pass over an *existing* scientific manuscript. The skill reads the context needed for the selected scope, delivers **location-anchored findings**, and applies requested edits with appropriate verification.

**Scope note.** This is the *reviewing/revising* counterpart to `write-paper` (which *drafts* a manuscript figures-first). It is **not** `survey` report mode, which writes technology/field-assessment reports from a literature survey. Use `review-paper` when a manuscript already exists and the user wants comments, a referee-style critique, reference/fact verification, or guideline-driven polish. If no manuscript exists yet, redirect to `write-paper`.

Guidelines 1–8 below come from a manuscript-quality rubric, and guideline 9 checks the manuscript against its target journal's own rules; the writing checklist lives in `skills/how-to-technical-writing/checklist.md` and the review-process checklist in `skills/review-paper/checklist.md`. Sentence- and paragraph-level rules live in the `how-to-technical-writing` skill (`skills/how-to-technical-writing/SKILL.md`); notation and figure discipline live in `write-paper/SKILL.md`. This skill **references** both rather than restating them. Consult `skills/write-paper/references.md` for the *why* behind a rule.

Use `skills/how-to-write-ideas-report/references/writing-workflow.md` for KB/context loading, citation handling, the BibTeX lookup chain, and output mechanics.

---

## Operating principle

**Choose the application mode before changing a manuscript file.** Use the
user's current instructions and prior decisions:

| Request or existing decision | Application mode |
|---|---|
| Review, critique, comments, or fact check | Findings only; leave the original unchanged. |
| Polish or revise a whole manuscript, with no direct-edit decision | Marked proposal in a separate copy; leave the original unchanged until the user accepts changes. |
| Explicitly edit the original directly, apply accepted findings, or continue an established direct-edit mode | Apply within that authorization and verify; do not ask again. |
| A specific local replacement or edit to a named passage | Complete that local edit without reopening whole-paper approval. |
| Rewrite an excerpt supplied in chat | Return revised text inline. |

Naming `main.md` or limiting a whole-paper polish to English/grammar does not
select direct mode. Prepare the marked proposal and numbered changes before
asking which to apply; do not ask permission to begin the work. A user-requested
preview takes precedence over the local-edit default. For wording-only work,
preserve scientific meaning. Unresolved scientific
judgment calls remain comments, while a separately requested substantive revision
may be proposed from the supplied evidence. Never invent a result or justification.

---

## The nine guidelines → where each is handled

| # | Guideline | Phase | Source |
|---|-----------|-------|--------|
| 1 | Break long sentences; one concept per sentence | 1 | `how-to-technical-writing` |
| 2 | Define every concept/symbol before use | 1 | `write-paper` Notation Rulebook |
| 3 | Each paragraph has one well-defined job | 1 | `how-to-technical-writing` |
| 4 | **DRY** — avoid repeated explanations/definitions | 1 | new to this skill |
| 5 | Display math reserved for emphasis only | 1 | `write-paper` Notation Rulebook |
| 6 | Match context to scope; brief the story and section missions for a full review | 0 | scope and context selection |
| 7 | Every figure referenced ≥1× and its striking features discussed | 1 | `write-paper` Figure Rulebook |
| 8 | Verify factual claims & references; flag the uncertain | 2 | new — the standout capability |
| 9 | Fit the target journal: limits, required parts, and its writing guidance | 2.5 | new — venue discussion reused from `write-paper` Phase 1.5 |

---

## Severity rubric

Rank every finding so the user can triage:

- **high** — wrong or misleading: undefined-but-used symbol, broken/missing citation, a factual or numerical claim that fails verification, an orphan figure central to a result, a claim the cited work does not support, a hard journal limit exceeded or a required statement missing.
- **med** — hurts clarity but not correctness: overlong multi-concept sentences, a purposeless paragraph, a repeated explanation (DRY), display math that doesn't earn emphasis.
- **low** — polish: minor signposting, parallelism, caption tightening, a striking figure feature left undiscussed.

---

## Phase 0 — Scope, load & understand (guideline #6)

1. **Resolve scope and mode.** Use the supplied manuscript, excerpt, requested
   checks, and existing authorization. For an unspecified full review, cover
   story, writing, facts/references, and journal fit when a target is known.
   A local wording or caption request runs only the relevant writing checks.
   Ask only when the target or substantive scope cannot be inferred. On a
   repeat pass, inspect changed passages and affected dependencies; rerun
   reference or journal checks only when relevant inputs or unresolved findings
   changed. State any limits of the review.
2. **Read enough context.** For a full scientific review, read the whole manuscript
   and its bibliography. For a local pass, read the target plus nearby definitions,
   referenced equations/figures, and the context needed to preserve meaning.
   Expand only if a concrete dependency requires it; do not require the entire
   KB, user profile, or history for a local grammar check.
3. **Resolve references when needed.** Use the manuscript's own bibliography
   (`\bibliography`, `\addbibresource`, embedded entries, or Typst bibliography)
   before falling back to `$KB/references.bib`. For fact checks, follow the
   relevant context/citation sections of
   `skills/how-to-write-ideas-report/references/writing-workflow.md`. Load only
   source entries relevant to the review, except in a requested full-bibliography
   audit (Phase 2).
4. **Understand the story for a full review.** Write a brief covering the question,
   significance, claimed contributions, key results tied to figures/equations,
   and each section's mission. Include it with the completed report. Pause for
   clarification only if competing interpretations would materially change the
   critique. A local wording pass does not need a story-approval gate.
5. **Select passes.** The requested scope selects Phase 1 (writing), Phase 2
   (facts/references), and Phase 2.5 (journal fit). These correspond to options
   2, 3, and 4 below; option 1 means high-level scientific review.
6. **Comment on the high-level aspects** (option 1). Severity-ranked, same finding shape as Phase 1, guideline 6:
   - **Significance of the problem** — Justify, from the manuscript and the loaded KB, why the problem is worth solving: who is blocked by it, what becomes possible once it is solved, and what the strongest prior attempt achieved. If the manuscript does not supply this, or the KB is too thin to judge whether the gap is real, mark that assessment unresolved and suggest a focused literature check; continue other selected checks without inventing support from general knowledge.
   - **Significance of each contribution** — Take the numbered contributions one at a time. For each, ask: is it stated as a verifiable property (a bound, a measured improvement, a new capability with a demonstrated case) rather than an activity ("we study", "we explore")? Does a result in the paper verify it? Would a reader in the target audience pay for it: is it better than the strongest baseline on an axis that audience cares about, and is that axis named? A contribution that fails any of these is a finding; the fix names the property that would make it buyable.
   - **Story** — Does the claimed contribution match what the results actually show? Is the gap statement supported by the cited prior work, or asserted?
   - **Abstract** — Map its moves (system, method, finding, implication) onto the story brief. Flag any abstract claim no result backs, and any key result the abstract omits.
   - **Main figure** — If one figure clearly carries the central claim, judge whether it does so alone: is the striking feature the result, is the comparison the right one, are the axes and baselines the ones a skeptic would ask for? If no figure can be pointed to as "the result", say so; that is itself a finding.
   - **Supporting data** — For each key result, is the evidence strong enough for the claim as worded? Check the match between claim strength and evidence: a general claim needs more than one system, size, or seed; a "significant" improvement needs error bars or a statistical test that separates it from the baseline; a scaling claim needs enough decades to distinguish the fitted law from its neighbours; a "state of the art" claim needs the strongest current baseline, run under the same conditions. Flag claims with no data behind them, missing controls, baselines, or error bars, and claims worded stronger than the data. The fix either names the extra evidence needed or rewords the claim down to what the data shows.
   - **Highlighting the contributions** — Are the contributions where a skimming reader looks: named as such in the abstract, listed in the introduction's "in this paper" paragraph, and each tied to the figure or equation that proves it? Propose a better way to surface them when one exists: a main figure that puts the contribution and the strongest baseline on the same axes, a summary table of results versus prior work, a sharper title or abstract sentence that states the property rather than the activity, or reordering so the strongest result comes first. Keep to what the data already supports; do not invent a comparison.

Continue through the selected passes and deliver one coherent report. Reuse a story the user already supplied or confirmed.

---

## Phase 1 — Structured review (guidelines #1–5, #7)

Run only when option 2 was selected in Phase 0. Walk the manuscript and produce findings. Each finding has this shape:

```
{ guideline: 1–8,
  location:  section + line/anchor (and the offending snippet),
  severity:  high | med | low,
  problem:   what's wrong, in one sentence,
  fix:       a concrete suggested edit }
```

When style calibration is needed, consult the relevant walkthrough in `skills/write-paper/references.md` §C; open only the corresponding excerpt of the model paper: Ho et al., PRL 122, 040603 (2019), at `skills/write-paper/sources/1807.01815_Ho2019_quantum-scars.md`, with a move-by-move walkthrough in `skills/write-paper/references.md` §C. A good rewrite reads like that letter: one concept per sentence, symbols defined at first use, each section opening with its job, main results named as such. When unsure whether a sentence deserves a finding, ask whether it could appear in the model paper unchanged.

Checks:

1. **Sentence length / one concept per sentence.** Flag overlong or triple-idea sentences; propose splits, except for sentences that wrap a display equation or bind a hypothesis to its conclusion. Also hunt the language-level faults listed in the hunt table of `skills/how-to-technical-writing/SKILL.md`: content-free openers and meta-talk, "obviously" / "clearly" where the earlier context should be named, Latinate connectives, metaphors the paper does not draw, intensifiers and stacked asides, and runs of inline computation that belong in one display. (Style guide.)
2. **Define before use.** Build a symbol/notation table *as you read*. Flag any symbol or concept used before its definition, any symbol never defined, and definitions out of logical order. (`write-paper` Notation Rulebook.)
3. **Paragraph purpose and locality.** Flag purposeless or double-duty paragraphs, and, in Theory, Methods, Results, and Analysis, paragraphs that drift to a second object or reach sideways to a concept the argument does not need (a preview of a later section, a second interpretation never used). The Introduction and Conclusions are exempt from the locality check. Suggest a topic sentence and a single job per paragraph; keep a cross-reference only when the current step depends on it, and say why in the same sentence.
4. **DRY / anti-repetition.** Detect explanations or definitions repeated across body sections; suggest consolidate-and-cross-reference. (New — keep one canonical statement, reference it elsewhere.) Exempt the abstract, introduction, and conclusions, which restate by design, and main-result sentences, which may be named more than once.
5. **Display-math discipline.** Flag display equations that don't earn emphasis; suggest inlining or cutting. Reserve display math for key/flagship results, non-obvious steps, or figure-referenced equations. Never propose inlining or cutting an equation whose label is referenced elsewhere; for a letter, propose moving algebra to the supplement rather than deleting a reproducibility step. (`write-paper` Notation Rulebook.)
7. **Figure integration.** Flag **orphan** figures (never referenced in the main text) and figures whose striking features (peaks, kinks, jumps) aren't discussed. (`write-paper` Figure Rulebook.)

For full reviews, also run a per-section **"did this section deliver its Phase-0 mission?"** check (guideline #6 carried into the body), and check that each key result from the story brief is named as a main result where it appears.

Every finding names the rule it serves. Not every paragraph needs a finding: a passage that already passes stays untouched, and a rewrite is never proposed for the sake of a diff.

---

## Phase 2 — Fact & reference verification (guideline #8)

Run only when option 3 was selected in Phase 0. The standout capability. Follow the repo discipline: **never invent BibTeX from memory**. Keep this pass within the selected scope: a full review screens all bibliography metadata, while a targeted fact or reference check verifies only the requested claims and their supporting entries/links; claim verification stays focused on what supports those claims (see `skills/how-to-write-ideas-report/references/writing-workflow.md`).

- **Full review or bibliography audit: screen every bibliography entry.** Run `python3 "$DOWNLOAD_REF_DIR/helpers/verify_bib.py" --bib "$BIB" --kb "$KB" --json` against the bibliography resolved in Phase 0. This checks uncited entries too and compares title, authors, year, venue/journal, volume, pages, and DOI using cached metadata plus Semantic Scholar's batch API.
- **Targeted check.** Resolve the entries cited by the selected passage or named by the user and verify those records directly against authoritative metadata. Do not run `verify_bib.py` against the whole bibliography for this mode: its CLI has no key filter. Include additional entries only when they are dependencies of the requested claim. State the checked scope in the result.
- **Confirm actionable records.** Use the helper's severity-ranked output as the starting point for the reference / fact-check table. Before reporting any `unverifiable` entry, or any `mismatch` with a high- or medium-severity finding, confirm it manually through **CrossRef → Semantic Scholar → MCP → web fetch**; Semantic Scholar screens, it is not the final authority. Keep low-severity missing-field findings as metadata-completion suggestions — they do not need the full lookup chain. Flag broken, missing, or confirmed-mismatched entries and offer repair via the `how-to-download-ref` skill (it owns `references.bib` appends and metadata fetching).
- **Citation resolution.** For each `\cite` key in the selected scope, confirm that an entry exists in the resolved bibliography. In a full review, uncited entries remain in the metadata scan; cited keys additionally participate in the claim-support check below.
- **Claim ↔ citation support.** For key claims attached to a citation, best-effort sanity-check that the cited work actually supports the claim. **Flag uncertain — do not assert.**
- **Standalone factual claims.** Identify checkable factual/numerical claims in the selected scope *not* tied to a citation; verify via web search. **Flag** the uncertain or unsupported — never silently "correct" a claim, and never fabricate a citation to prop one up.
- **Link check.** Fetch relevant URLs and DOI links for a targeted check. In a full review, fetch every URL in the manuscript and bibliography (`\url`, `\href`, DOI links, code and data repositories) once; flag dead links, redirects to a different resource, and DOIs that do not resolve. A private or paywalled target that answers is ok.

---

## Phase 2.5 — Journal fit (guideline #9)

Run only when option 4 was selected in Phase 0. Never quote a limit or rule from memory: every constraint in this pass comes from a page fetched in this session or from a `template/README.md` that records its source.

1. **Decide the target journal.** Use the venue the manuscript already declares: a document class or template (`revtex4-2`, `iopart`, `elsarticle`, an `sn-jnl` class), journal macros, a cover letter, or a `template/README.md` written by `write-paper` Phase 1.5. If none, follow `write-paper` Phase 1.5: propose 2–3 venues with tradeoffs (article type, audience, length pressure, figure limits, novelty bar) grounded in the story brief, and ask the user to pick one or say "no target yet". With no target, skip the rest of this pass and record that choice in the report.
2. **Fetch the author guidelines.** Prefer the official publisher page over mirrors, Overleaf copies, or lab handouts. Reuse `template/README.md` when it already records the URL and access date; otherwise record both in the report. If the page cannot be fetched, mark every constraint `unverifiable`, give the URL, and stop that journal-constraint check while completing the other selected passes.
3. **Extract the checkable constraints into a table**: article type; word, page, or character limits for the body, abstract, and title; maximum figures, tables, and references; required sections and their order; required statements (data availability, code availability, author contributions, competing interests, funding, ethics or IRB, keywords, significance statement); formatting rules (citations in the abstract, footnotes, units, figure resolution and file types, reference style); and any writing guidance the journal itself gives (a first paragraph accessible to non-specialists, a summary-paragraph structure, a stated audience).
4. **Check each constraint against the manuscript.** Measure rather than estimate: word counts from the compiled text (`detex`, `pandoc --to plain`, or `typst query`), figure, table, and reference counts from the source, section presence from the headings. Status per row: ok / over / missing / unverifiable. Severity: high for a hard limit exceeded or a required statement missing, med for a formatting rule, low for cosmetic.
5. **Review against the journal's writing guidance.** Judge the abstract, the opening paragraph, and the framing of significance against what the journal says it wants for its audience. These are guideline-9 findings with the same shape as Phase 1; the fix cites the guideline sentence it serves.

---

## Phase 3 — Deliver the review report

For a full review, write `articles/<slug>/review-YYYY-MM-DD.md` (or the requested
path). For a local excerpt or small wording pass, deliver concise findings or
the revised text inline unless a file was requested. Include only applicable
parts of this structure:

1. **Story brief, high-level comments, and per-section missions** (from Phase 0).
2. **Findings grouped by guideline, severity-ranked** (high → low).
3. **Reference / fact-check table** — cite key or URL → status (ok / broken / missing / mismatch / unverifiable) → note. If Phase 2 was skipped, one line saying so and pointing at the last report that ran it.
4. **Journal fit table** — target journal and guideline source (URL, access date), then constraint → required → measured → status. If Phase 2.5 was skipped or no target was chosen, one line saying so.
5. **Top fixes** — a prioritized list of the highest-leverage changes.

For a review-only request, deliver the report; offer application as an optional
next step. If changes were already requested, continue to Phase 4 using that
scope and the application mode from the Operating principle. For broad polish
without an established mode, deliver the marked proposal and numbered changes
for acceptance before merging; a generic revision request alone does not select
direct mode. Reuse explicit direct-edit instructions or already accepted
findings without asking again. A requested inline excerpt rewrite can be
delivered directly as revised text.

---

## Phase 4 — Apply approved edits

**Marked-diff mode** (the default for broad revision/polish without an established
application mode, and whenever the user requests a preview). Prepare the
proposed changes before asking the user which to merge. Proposals outside the
authorized scientific scope remain separate suggestions, not applied edits.

1. **Edit a copy.** `cp main.tex main.proposed.tex` (same for `.typ` / `.md`). Apply the proposed fixes to the copy; when using scripted replacements, assert that each target matches exactly once. Comment-only fixes (style-guide guardrails) go in as `[reviewer]` comments in the copy too.
2. **Mark the diff.** LaTeX: `latexdiff main.tex main.proposed.tex > main.diff.tex`, then compile `main.diff.tex` (deletions red struck-through, additions blue underlined). Typst and Markdown have no latexdiff; write `git diff --no-index --word-diff main.typ main.proposed.typ` into `articles/<slug>/review-YYYY-MM-DD.diff` and, for Typst, also compile the proposed copy so the author can read the result. Check the page count did not change unexpectedly.
   If shell/diff/render tools are unavailable, still create the proposed copy
   with available file tools and provide numbered before/after changes. Report
   the unavailable checks; do not ask whether to prepare the already requested
   proposal. Acceptance concerns applying it to the original.
3. **Hand over a numbered legend.** Give the marked PDF (or diff file) path and one line per change: number, section and page, the finding it fixes, and the rule it serves. Pair up a removal and an addition that belong to one change. End with "reply with the numbers to merge, or all".
4. **Merge exactly the accepted numbers** into the original. If the user accepts "all except one wording", revert that wording in the copy first, then merge all. Delete `main.proposed.*` and `main.diff.*` afterwards.

**Direct mode** (when the user asked to edit the original directly, approved
specific findings, or already chose this mode). Apply changes within that
authorization and show the diff/result. An explicit request such as "replace
'We studies' with 'We study' in this paragraph" authorizes that local edit;
a general "polish my paper"
uses the marked proposal by default. Do not broaden the requested revision or
ask again to apply changes already accepted.

**Both modes.**

1. **Preserve structure.** Keep macros, environments, labels, and document structure in every format. Where a fix genuinely needs author judgment, insert a `% [reviewer] …` margin comment instead of rewriting silently (`// [reviewer]` in Typst, an HTML comment in Markdown).
2. **Language edits change how a sentence is written, never what it says.** Never alter the content of a definition, theorem, or claim while rewording it; never add or remove a claim, figure, or derivation step under a guideline 1–5 fix; never replace a field term with a simpler word. Recheck every number, count, and qualifier a rewritten sentence mentions before moving on.
3. **Comment, do not apply, when a language fix touches content.** An edit that would change a quantifier or hedge ("arbitrary", "approximately", "at most"), add a justification the manuscript does not already contain, delete a paragraph as a digression, or remove a "not X but Y" contrast goes in as a `[reviewer]` comment even when the user approved the finding. Do not treat approval of a language pass as approval to change scientific content; a substantive rewrite needs its own explicit scope and supporting evidence.
4. **Verify it still compiles** — `latexmk` (or `pdflatex`) for `.tex`, `typst compile` for `.typ`; for `.md`, confirm it still renders. Report pass/fail with the actual command output (per verification-before-completion: evidence before assertions). If it breaks, fix or revert the offending edit before claiming done.
5. **Append a changelog** to the top of the review report: what was applied, what was skipped, and the compile result.

---

## Reused vs. new

**Reused (no duplication):** `skills/how-to-write-ideas-report/references/writing-workflow.md` (context, citations, output mechanics); `skills/how-to-technical-writing/SKILL.md` (sentence/paragraph rules, hunt table, application guardrails); the BibTeX lookup chain (CrossRef → Semantic Scholar → MCP → web fetch); `how-to-download-ref` for reference repair; `write-paper`'s notation/figure rule *definitions* (referenced).

**New here:** scope selection and whole-paper context for full reviews (Phase 0), DRY/anti-repetition detection (#4), fact & reference verification (#8), journal fit (#9, venue discussion reused from `write-paper` Phase 1.5), and the comment-then-apply loop plus compile-check (Phases 3–4).

---

## Common mistakes

| Mistake | Instead |
|---|---|
| Treating a review request as permission to edit | Deliver findings; use existing revision authorization only for its stated scope. |
| Treating broad polish as an implicit direct-edit preference | Default to a marked proposal; reuse explicit direct-edit instructions or accepted changes without another approval. |
| Running a full story gate for a local wording fix | Read the target and its necessary context; reserve the story brief for full reviews. |
| Re-running reference verification on every pass | Inspect changed inputs and unresolved findings; rerun only affected checks. |
| Inventing a BibTeX entry to "fix" a citation | Never. Use the lookup chain / the `how-to-download-ref` skill, or flag as unverifiable. |
| Silently "correcting" a factual claim | Flag uncertain claims; the author decides. |
| Claiming a build passed without running it | Compile changed document source; distinguish inline-text checks from a document build. |
| Chasing completeness on fact-checks | Verify only what supports the main claims. |
| Quoting a journal's word limit or required sections from memory | Fetch the official author guidelines this session, or mark the row unverifiable with the URL. |
| Rewriting a passage that already passes | Leave it. A finding must name the rule it serves. |
| "Simplifying" a technical term | Keep the field's term; simplify only connectives, idioms, and asides. |
| A reworded sentence changed a count, qualifier, or claim | Language edits change how, never what. Recheck numbers after every rewrite. |
| Writing the reason behind a "clearly" from general knowledge | If the supporting equation, figure, or section is not in the manuscript, ask the author in a `[reviewer]` comment. |
| Applying DRY or locality to the abstract, introduction, or conclusions | Those sections restate and connect by design; check them only for the four introduction beats and the implications paragraph. |

---

## Integrations

- **Context, citations, output mechanics:** `skills/how-to-write-ideas-report/references/writing-workflow.md`.
- **Sentence/paragraph rules, hunt table, guardrails:** `skills/how-to-technical-writing/SKILL.md`; checkable form in `skills/how-to-technical-writing/checklist.md`.
- **Rule definitions (notation/figure):** `skills/write-paper/SKILL.md` + `skills/write-paper/references.md`.
- **Model paper (style calibration for fixes):** `skills/write-paper/sources/1807.01815_Ho2019_quantum-scars.md`, distilled in `skills/write-paper/references.md` §C.
- **Target venue and template discussion:** `write-paper` Phase 1.5 (`skills/write-paper/SKILL.md`).
- **Reference repair / adding a missing paper:** the `how-to-download-ref` skill.
- **Review-process checklist (gate, verification, journal fit, delivery):** `skills/review-paper/checklist.md`.
