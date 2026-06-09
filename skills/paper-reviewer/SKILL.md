---
name: paper-reviewer
description: Use when reviewing, critiquing, commenting on, or fact-checking an existing scientific manuscript — "comment on my paper", "review my draft", "check my references", "verify my claims", or a referee-style read of a .tex/.typ/.md paper. Not for drafting from scratch (use paper-writer) or for technology/field assessments (use review-writer).
---

# Paper Reviewer

Run a structured **review-and-enhance** pass over an *existing* scientific manuscript. The skill reads the whole paper, produces **location-anchored comments first**, then applies only the edits the user approves and re-checks that the manuscript still compiles.

**Scope note.** This is the *reviewing/revising* counterpart to `paper-writer` (which *drafts* a manuscript figures-first). It is **not** `review-writer`, which writes technology/field-assessment reports. Use `paper-reviewer` when a manuscript already exists and the user wants comments, a referee-style critique, reference/fact verification, or guideline-driven polish. If no manuscript exists yet, redirect to `paper-writer`.

The eight guidelines below come from a manuscript-quality rubric. Where a rule is already defined as an *authoring* rule in `paper-writer/SKILL.md` (sentence/notation/figure discipline), this skill **references** it rather than restating it — consult `skills/paper-writer/SKILL.md` and `skills/paper-writer/references.md` for the *why* behind a rule. The full rubric lives in `skills/paper-reviewer/checklist.md`.

Use `skills/_shared/writing-workflow.md` for KB/context loading, citation handling, the BibTeX lookup chain, and output mechanics.

---

## Operating principle

**Comment-first, non-destructive.** Never edit the manuscript before the user has seen and approved the findings. Read the whole paper, deliver the comments, let the user choose what to apply, *then* edit. This mirrors `paper-writer`'s "iterate the story with the user" philosophy: the author keeps control of judgment calls.

---

## The eight guidelines → where each is handled

| # | Guideline | Phase | Source |
|---|-----------|-------|--------|
| 1 | Break long sentences; one concept per sentence | 1 | `paper-writer` Sentence-Level Rules |
| 2 | Define every concept/symbol before use | 1 | `paper-writer` Notation Rulebook |
| 3 | Each paragraph has one well-defined job | 1 | `paper-writer` Sentence-Level Rules |
| 4 | **DRY** — avoid repeated explanations/definitions | 1 | new to this skill |
| 5 | Display math reserved for emphasis only | 1 | `paper-writer` Notation Rulebook |
| 6 | Read the whole paper first; grasp the story, then each section's mission | 0 | new — the gate before critique |
| 7 | Every figure referenced ≥1× and its striking features discussed | 1 | `paper-writer` Figure Rulebook |
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
2. **Read the whole manuscript** end to end — and its bibliography. Resolve the bibliography in this order: the manuscript's own `\bibliography{…}` / `\addbibresource{…}` target (or embedded `thebibliography` / Typst `bibliography(…)`), then fall back to `$(dirname $KB)/ref.bib`. Handle both; note which one you used.
3. **Load shared context.** Follow `skills/_shared/writing-workflow.md`: resolve `KB=$(python3 skills/download-ref/helpers/resolve_kb.py)`, read `$KB/INDEX.md`, `$KB/NOTES.md`, `$(dirname $KB)/ref.bib`, and `docs/discussion/user-profile.md` if present. This is the literature backdrop for fact-checking.
4. **Emit the story summary + per-section missions.** One paragraph capturing the paper's story, plus a one-line "mission" for each section. **Confirm the story with the user before any critique.** This gate prevents local nitpicks that fight the global narrative — if the reviewer misread the story, fix that before producing findings.

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

Checks:

1. **Sentence length / one concept per sentence.** Flag overlong or triple-idea sentences; propose splits. (`paper-writer` Sentence-Level Rules.)
2. **Define before use.** Build a symbol/notation table *as you read*. Flag any symbol or concept used before its definition (a forward-reference), and any symbol never defined. Require that every symbol is defined before use, in logical order. (`paper-writer` Notation Rulebook.)
3. **Paragraph purpose.** Flag purposeless or double-duty paragraphs; suggest a topic sentence and a single job per paragraph.
4. **DRY / anti-repetition.** Detect explanations or definitions repeated across sections; suggest consolidate-and-cross-reference. (New — keep one canonical statement, reference it elsewhere.)
5. **Display-math discipline.** Flag display equations that don't earn emphasis; suggest inlining or cutting. Reserve display math for key/flagship results, non-obvious steps, or figure-referenced equations. (`paper-writer` Notation Rulebook.)
7. **Figure integration.** Flag **orphan** figures (never referenced in the main text) and figures whose striking features (peaks, kinks, jumps) aren't discussed. (`paper-writer` Figure Rulebook.)

Also run a per-section **"did this section deliver its Phase-0 mission?"** check (guideline #6 carried into the body).

---

## Phase 2 — Fact & reference verification (guideline #8)

The standout capability. Follow the repo discipline: **never invent BibTeX from memory**; use the lookup chain **CrossRef → Semantic Scholar → MCP → WebFetch**; verify only what supports the main claims (completeness is not the goal — see `skills/_shared/writing-workflow.md`).

- **References.** For each `\cite` key: confirm the entry exists in the resolved bibliography, then verify authors / year / title / venue against the lookup chain. Flag broken, missing, or mismatched citations. Offer to repair via `/download-ref` (it owns `ref.bib` appends and metadata fetching).
- **Claim ↔ citation support.** For key claims attached to a citation, best-effort sanity-check that the cited work actually supports the claim. **Flag uncertain — do not assert.**
- **Standalone factual claims.** Identify checkable factual/numerical claims *not* tied to a citation; verify via WebSearch. **Flag** the uncertain or unsupported — never silently "correct" a claim, and never fabricate a citation to prop one up.

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
2. **Apply edits to the manuscript**, preserving LaTeX macros, environments, labels, and structure (and Typst/Markdown structure for those formats). Where a fix genuinely needs author judgment, insert a `% [reviewer] …` margin comment instead of rewriting silently (use `// [reviewer]` for Typst, an HTML comment for Markdown).
3. **Verify it still compiles** — `latexmk` (or `pdflatex`) for `.tex`, `typst compile` for `.typ`; for `.md`, confirm it still renders. Report pass/fail with the actual command output (per verification-before-completion: evidence before assertions). If it breaks, fix or revert the offending edit before claiming done.
4. **Append a changelog** to the top of the review report: what was applied, what was skipped, and the compile result.

---

## Reused vs. new

**Reused (no duplication):** `skills/_shared/writing-workflow.md` (context, citations, output mechanics); the BibTeX lookup chain (CrossRef → Semantic Scholar → MCP → WebFetch); `download-ref` for reference repair; `paper-writer`'s sentence/notation/figure rule *definitions* (referenced).

**New here:** the read-whole-first review protocol (Phase 0), DRY/anti-repetition detection (#4), fact & reference verification (#8), and the comment-then-apply loop plus compile-check (Phases 3–4).

---

## Common mistakes

| Mistake | Instead |
|---|---|
| Editing before the user approves | Comment-first. Phase 3 → user picks → Phase 4. |
| Nitpicking sentences before confirming the story | Phase 0 gate: confirm the story summary first. |
| Inventing a BibTeX entry to "fix" a citation | Never. Use the lookup chain / `/download-ref`, or flag as unverifiable. |
| Silently "correcting" a factual claim | Flag uncertain claims; the author decides. |
| Claiming done without compiling | Run `latexmk` / `typst compile` and paste the result. |
| Chasing completeness on fact-checks | Verify only what supports the main claims. |

---

## Integrations

- **Context, citations, output mechanics:** `skills/_shared/writing-workflow.md`.
- **Rule definitions (sentence/notation/figure):** `skills/paper-writer/SKILL.md` + `skills/paper-writer/references.md`.
- **Reference repair / adding a missing paper:** `/download-ref`.
- **Full rubric checklist:** `skills/paper-reviewer/checklist.md`.
