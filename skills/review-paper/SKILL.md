---
name: review-paper
description: User trigger. Use when reviewing, commenting on, or fact-checking an existing manuscript, including its references.
---

# Paper Reviewer

Run a structured **review-and-enhance** pass over an *existing* scientific manuscript. The skill reads the whole paper, produces **location-anchored comments first**, then applies only the edits the user approves and re-checks that the manuscript still compiles.

**Scope note.** This is the *reviewing/revising* counterpart to `write-paper` (which *drafts* a manuscript figures-first). It is **not** `survey` report mode, which writes technology/field-assessment reports from a literature survey. Use `review-paper` when a manuscript already exists and the user wants comments, a referee-style critique, reference/fact verification, or guideline-driven polish. If no manuscript exists yet, redirect to `write-paper`.

The eight guidelines below come from a manuscript-quality rubric; the full rubric lives in `skills/review-paper/checklist.md`. Where `write-paper/SKILL.md` already defines a rule (sentence/notation/figure discipline), this skill **references** it rather than restating it. Consult `skills/write-paper/references.md` for the *why* behind a rule.

Use `skills/_shared/writing-workflow.md` for KB/context loading, citation handling, the BibTeX lookup chain, and output mechanics.

---

## Operating principle

**Comment-first, non-destructive.** Never edit the manuscript before the user has seen and approved the findings. Read the whole paper, deliver the comments, let the user choose what to apply, *then* edit. This mirrors `write-paper`'s "iterate the story with the user" philosophy: the author keeps control of judgment calls.

---

## The eight guidelines → where each is handled

| # | Guideline | Phase | Source |
|---|-----------|-------|--------|
| 1 | Break long sentences; one concept per sentence | 1 | `write-paper` Sentence-Level Rules |
| 2 | Define every concept/symbol before use | 1 | `write-paper` Notation Rulebook |
| 3 | Each paragraph has one well-defined job | 1 | `write-paper` Sentence-Level Rules |
| 4 | **DRY** — avoid repeated explanations/definitions | 1 | new to this skill |
| 5 | Display math reserved for emphasis only | 1 | `write-paper` Notation Rulebook |
| 6 | Read the whole paper first; grasp the story, then each section's mission | 0 | new — the gate before critique |
| 7 | Every figure referenced ≥1× and its striking features discussed | 1 | `write-paper` Figure Rulebook |
| 8 | Verify factual claims & references; flag the uncertain | 2 | new — the standout capability |

---

## Severity rubric

Rank every finding so the user can triage:

- **high** — wrong or misleading: undefined-but-used symbol, broken/missing citation, a factual or numerical claim that fails verification, an orphan figure central to a result, a claim the cited work does not support.
- **med** — hurts clarity but not correctness: overlong multi-concept sentences, a purposeless paragraph, a repeated explanation (DRY), display math that doesn't earn emphasis.
- **low** — polish: minor signposting, parallelism, caption tightening, a striking figure feature left undiscussed.

---

## Phase 0 — Load & understand (guideline #6)

1. **Resolve the manuscript.** Accept an explicit path; else auto-detect from `articles/<slug>/` or the working directory. Detect format from the extension: **LaTeX (`.tex`) is primary**; Typst (`.typ`) and Markdown (`.md`) are supported.
2. **Read the whole manuscript** end to end — and its bibliography. Resolve the bibliography in this order: the manuscript's own `\bibliography{…}` / `\addbibresource{…}` target (or embedded `thebibliography` / Typst `bibliography(…)`), then fall back to `$KB/references.bib`. Handle both; note which one you used.
3. **Load shared context.** Follow `skills/_shared/writing-workflow.md`: resolve `KB=$(python3 skills/how-to-download-ref/helpers/resolve_kb.py)`, read `$KB/INDEX.md`, `$KB/NOTES.md`, `$KB/references.bib`, and `docs/discussion/user-profile.md` if present. This is the literature backdrop for fact-checking.
4. **Write the story summary + per-section missions.** One paragraph capturing the paper's story, plus a one-line "mission" for each section. This gate prevents local nitpicks that fight the global narrative: if you misread the story, fix that before producing any finding.

Do not proceed to Phase 1 until the user confirms (or corrects) the story summary.

---

## Phase 1 — Structured review (guidelines #1–5, #7)

Walk the manuscript and produce findings. Each finding has this shape:

```
{ guideline: 1–8,
  location:  section + line/anchor (and the offending snippet),
  severity:  high | med | low,
  problem:   what's wrong, in one sentence,
  fix:       a concrete suggested edit }
```

Calibrate every `fix` against the model paper: Ho et al., PRL 122, 040603 (2019), at `skills/write-paper/sources/1807.01815_Ho2019_quantum-scars.md`, with a move-by-move walkthrough in `skills/write-paper/references.md` §C. A good rewrite reads like that letter: one concept per sentence, symbols defined at first use, each section opening with its job, main results named as such. When unsure whether a sentence deserves a finding, ask whether it could appear in the model paper unchanged.

Checks:

1. **Sentence length / one concept per sentence.** Flag overlong or triple-idea sentences; propose splits. (`write-paper` Sentence-Level Rules.)
2. **Define before use.** Build a symbol/notation table *as you read*. Flag any symbol or concept used before its definition, any symbol never defined, and definitions out of logical order. (`write-paper` Notation Rulebook.)
3. **Paragraph purpose.** Flag purposeless or double-duty paragraphs; suggest a topic sentence and a single job per paragraph.
4. **DRY / anti-repetition.** Detect explanations or definitions repeated across sections; suggest consolidate-and-cross-reference. (New — keep one canonical statement, reference it elsewhere.)
5. **Display-math discipline.** Flag display equations that don't earn emphasis; suggest inlining or cutting. Reserve display math for key/flagship results, non-obvious steps, or figure-referenced equations. (`write-paper` Notation Rulebook.)
7. **Figure integration.** Flag **orphan** figures (never referenced in the main text) and figures whose striking features (peaks, kinks, jumps) aren't discussed. (`write-paper` Figure Rulebook.)

Also run a per-section **"did this section deliver its Phase-0 mission?"** check (guideline #6 carried into the body).

---

## Phase 2 — Fact & reference verification (guideline #8)

The standout capability. Follow the repo discipline: **never invent BibTeX from memory**. Bibliography metadata gets a complete automated screening pass; claim verification stays focused on what supports the main claims (see `skills/_shared/writing-workflow.md`).

- **Screen every bibliography entry.** Run `python3 skills/how-to-download-ref/helpers/verify_bib.py --bib "$BIB" --kb "$KB" --json` against the bibliography resolved in Phase 0. This checks uncited entries too and compares title, authors, year, venue/journal, volume, pages, and DOI using cached metadata plus Semantic Scholar's batch API.
- **Confirm actionable records.** Use the helper's severity-ranked output as the starting point for the reference / fact-check table. Before reporting any `unverifiable` entry, or any `mismatch` with a high- or medium-severity finding, confirm it manually through **CrossRef → Semantic Scholar → MCP → web fetch**; Semantic Scholar screens, it is not the final authority. Keep low-severity missing-field findings as metadata-completion suggestions — they do not need the full lookup chain. Flag broken, missing, or confirmed-mismatched entries and offer repair via the `how-to-download-ref` skill (it owns `references.bib` appends and metadata fetching).
- **Citation resolution.** For each `\cite` key, confirm that an entry exists in the resolved bibliography. Uncited entries remain in the metadata scan; cited keys additionally participate in the claim-support check below.
- **Claim ↔ citation support.** For key claims attached to a citation, best-effort sanity-check that the cited work actually supports the claim. **Flag uncertain — do not assert.**
- **Standalone factual claims.** Identify checkable factual/numerical claims *not* tied to a citation; verify via web search. **Flag** the uncertain or unsupported — never silently "correct" a claim, and never fabricate a citation to prop one up.

---

## Phase 3 — Deliver the review report

Write a timestamped report to `articles/<slug>/review-YYYY-MM-DD.md` (the repo's dated-output convention). Structure:

1. **Story summary + per-section missions** (from Phase 0).
2. **Findings grouped by guideline, severity-ranked** (high → low).
3. **Reference / fact-check table** — cite key → status (ok / broken / missing / mismatch / unverifiable) → note.
4. **Top fixes** — a prioritized list of the highest-leverage changes.

Then present a short summary to the user and ask which findings to apply.

---

## Phase 4 — Apply approved edits

1. **User selects scope:** all / by-severity (e.g. "apply all high") / individually. Do not edit anything the user didn't approve.
2. **Apply edits to the manuscript**, preserving macros, environments, labels, and document structure in every format. Where a fix genuinely needs author judgment, insert a `% [reviewer] …` margin comment instead of rewriting silently (`// [reviewer]` in Typst, an HTML comment in Markdown).
3. **Verify it still compiles** — `latexmk` (or `pdflatex`) for `.tex`, `typst compile` for `.typ`; for `.md`, confirm it still renders. Report pass/fail with the actual command output (per verification-before-completion: evidence before assertions). If it breaks, fix or revert the offending edit before claiming done.
4. **Append a changelog** to the top of the review report: what was applied, what was skipped, and the compile result.

---

## Reused vs. new

**Reused (no duplication):** `skills/_shared/writing-workflow.md` (context, citations, output mechanics); the BibTeX lookup chain (CrossRef → Semantic Scholar → MCP → web fetch); `how-to-download-ref` for reference repair; `write-paper`'s sentence/notation/figure rule *definitions* (referenced).

**New here:** the read-whole-first review protocol (Phase 0), DRY/anti-repetition detection (#4), fact & reference verification (#8), and the comment-then-apply loop plus compile-check (Phases 3–4).

---

## Common mistakes

| Mistake | Instead |
|---|---|
| Editing before the user approves | Comment-first. Phase 3 → user picks → Phase 4. |
| Nitpicking sentences before confirming the story | Phase 0 gate: confirm the story summary first. |
| Inventing a BibTeX entry to "fix" a citation | Never. Use the lookup chain / the `how-to-download-ref` skill, or flag as unverifiable. |
| Silently "correcting" a factual claim | Flag uncertain claims; the author decides. |
| Claiming done without compiling | Run `latexmk` / `typst compile` and paste the result. |
| Chasing completeness on fact-checks | Verify only what supports the main claims. |

---

## Integrations

- **Context, citations, output mechanics:** `skills/_shared/writing-workflow.md`.
- **Rule definitions (sentence/notation/figure):** `skills/write-paper/SKILL.md` + `skills/write-paper/references.md`.
- **Model paper (style calibration for fixes):** `skills/write-paper/sources/1807.01815_Ho2019_quantum-scars.md`, distilled in `skills/write-paper/references.md` §C.
- **Reference repair / adding a missing paper:** the `how-to-download-ref` skill.
- **Full rubric checklist:** `skills/review-paper/checklist.md`.
