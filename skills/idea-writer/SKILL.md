---
name: idea-writer
description: Use when writing an ideas report after brainstorming or when turning a chosen research direction into a proposal-style research plan
---

# Idea Writer

Write a structured ideas report after `/ideas` has converged on a research direction. For technology assessments use `survey-writer`; for manuscripts with real results use `paper-writer`.

## Setup

Follow `skills/_shared/writing-workflow.md` for context loading, citation handling, gap-filling research, output format, diagrams, and finish checks.

- Primary source: `docs/discussion/*-ideas-log.md`; if multiple exist, ask which one to use.
- If no log exists, ask the user to run `/ideas` first or describe the direction.
- Save to `articles/YYYY-MM-DD-<topic>-ideas-report.{md,typ,tex}`.

## Report Structure

Draft each section, show, get feedback:

- **Research Question** — one sentence
- **Novelty Claim** — what's new and why it matters
- **Why Now, Why You** — what changed to make this tractable; unique advantage
- **Cross-field Connections** — unexpected links discovered during brainstorming
- **Proposed Approach** — method outline (Polya: what is the plan?)
- **Minimum Viable Experiment** — (Polya: can you solve a part of it?)
- **Success Signal** — what would it look like if this problem is truly solved?
- **Hope Signal** — what would indicate the problem isn't solved yet, but the approach still has hope?
- **Pivot Signal** — what would indicate this approach fundamentally doesn't work, and it's time to abandon or change direction?
- **Open Risks** — unresolved uncertainties
- **Target Venue**
- **Key References** — full BibTeX entries; save matching `.bib` file

## Diagrams

When a concept is abstract or structural — a reduction between problems, a relationship between methods, a data flow, an architecture — draw a diagram instead of (or alongside) explaining it in prose. A picture makes the idea concrete and shareable in ways that paragraphs of text cannot.

Common diagram types:
- **Reduction/connection diagrams** — boxes for concepts, arrows for relationships
- **Pipeline/flow diagrams** — stages of a method or data flow
- **Comparison layouts** — side-by-side before/after or method A vs. method B
- **Conceptual sketches** — any visual that makes an abstract idea graspable at a glance

*Polya's "Looking Back":* After drafting, review — can the result be derived differently? Can it be used for some other problem? Can you see the result at a glance?
