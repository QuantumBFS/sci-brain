---
name: how-to-technical-writing
description: Agentic trigger. Use when writing or polishing scientific prose at the sentence and paragraph level, in a manuscript, report, or review.
---

## Installed resources

Keep the working directory at the user's project. Resolve this `SKILL.md` with
`Path(path).resolve()` to follow symlinks. Bare `helpers/`, `references/`, and
template paths are relative to that real directory. `skills/<name>/...` refers
to the installed skill found by public name in the agent's catalog, not the
user's project. Dependencies need not be siblings; report and install missing
skills before the dependent step. Shared writing files are bundled in
`how-to-write-ideas-report/references/`.

# Writing style guide

These sentence and paragraph rules guide `write-paper` drafts, `review-paper` findings and proposed fixes, and `how-to-write-ideas-report` and `survey` report prose.

Related resources:

- Checkable form of these rules: `checklist.md`.
- Notation Rulebook and Figure Rulebook: `skills/write-paper/SKILL.md`.
- Reasons behind every rule: `skills/write-paper/references.md`.
- Model paper: `skills/write-paper/sources/1807.01815_Ho2019_quantum-scars.md`.

The rules come from Martinis, von Delft, and a language-polish checklist for teaching material. The guardrails prevent mechanical edits from changing manuscript content.

## Rules

Clarity outranks these rules. When they conflict, keep the clearer sentence.

### Conceptual clarity and semantic coherence

- **Explain concepts with existing concepts.** Do not use concepts never explained, or that are not a common sense to explain a new idea.
- **Define at the point of need.** Introduce a term or symbol only when the argument needs it. Every definition is used later in the paper.
- **Set up before calculating.** Before a derivation, state the system, the assumptions or boundary conditions, the symbols, and the quantity being computed. Use a labelled setup figure when geometry matters.
- **One job per paragraph.** Each paragraph has its own mission. Start with a topic sentence, support it with detail, and end with a transition or emphasis. Do not mix different jobs in the same paragraph.
- **Locality rule.** Keep each paragraph on one object and each section on its job. Avoid connecting to concepts not within current scope, previewing later sections, or adding unused interpretations. Keep cross-references only when the current step depends on them, and say why: "by the linearity of Eq. (3)". In paper writing, abstracts, introduction, and conclusions are exempt.
- **Do not repeat yourself.** Cut sentences that do not carry new information or new examples. A second appearance of a fact is a pointer, never a restatement. A number, count, or list stated in two places can drift, so state it once and point to it.
- **The delete test.** A sentence stays only if removing it leaves a gap that something later in the section depends on. Run the test against the whole section, not the next sentence, so a setup for a later payoff survives.
- **Trust the structure.** Do not re-describe in words what an equation, table, or figure already shows. At most one clause points at what to look at. The text says what a feature means, not what shape it has.
- **Pay every promise.** Every "we will show", "surprisingly", or "the key link" has a later line that pays it with a result, theorem, or figure. A promise paid only by a hint is cut or paid.

### Narrative and wording choices

- **Cut long sentences.** Use length as a review signal, not a target. Split overloaded clauses into separate sentences, retaining logical links such as "so" or "because". Keep sentences that wrap a display equation or bind a hypothesis to its conclusion whole.
- **State the point directly.** Place key information near the beginning of the sentence.
- **Simple words; preserve technical words.** Explain ideas with simple words rather than fancy ones. Prefer "so" to "hence" or "thus", "also" to "likewise", "use" to "utilize", "show" to "demonstrate", and "start" to "commence". Replace only everyday words, connectives, and filler without mathematical meaning. Never replace verbs, quantifiers, or adjectives in mathematical statements, including "arbitrary", "determined by", "identify with", and "the converse". Keep field terms such as "decoherence", "ansatz", and "thermalize". Textbook and referee vocabulary stays.
- **No metaphor.**
- **Active voice for actions.** Prefer "We measured" to "measurements were performed." Reserve passive for things without an agent. Put the verb early with a concrete subject.
- **Concrete verbs over nominalizations.** Prefer "We adopt the new notation" to "Adoption of the new notation is undertaken."
- **Prose carries ideas; calculations go to displays.** Body sentences state ideas, intuitions, or logical steps. Combine two or more inline computations in a paragraph into one display, followed by one sentence explaining it.
- **Parallel grammar for parallel ideas.** Give comparisons, contrasts, and existing list items the same grammatical shape. Preserve prose layout; do not turn paragraphs into bullets or add lists a journal would not print. Papers develop arguments, and lists interrupt their flow.
- **Signposting.** Mark main results and transitions with "This is our main result," "We now turn to," or "In summary,". The model paper marks every turn with phrases such as "Specifically," "Conversely," and "Most surprisingly," to signal narrowing, contrast, or escalation.

## Hunt table

Use for reviews and final language passes. Each finding cites its row; leave passages that match none untouched. **Comment only** fixes remain comments even after approval; the author writes the replacement.

| Hunt for | Fix |
|---|---|
| An overloaded sentence or stacked clauses | Split, retaining logical links such as "so" or "because". Use length as a review signal, not a target. Keep sentences wrapping display equations or binding hypotheses to conclusions whole. |
| Restatement of the main-result sentence, equation, or paragraph opening | Delete the restatement; keep the canonical statement. |
| A sentence whose removal leaves no gap anywhere later in the section | Delete it, or fold its one useful clause into a neighbour. Test against the whole section. |
| Prose that re-describes what a nearby equation, table, or figure shows | Cut it to one clause pointing at what to look at. Keep the sentence that says what the feature means. |
| A promise ("we will show", "surprisingly", "the key link") with no line that pays it | **Comment only.** Name the promise and ask for the payoff or the cut. |
| A term or symbol defined before the argument needs it, or never used after its definition | **Comment only.** Propose moving the definition to its first use, or cutting it. |
| A number, count, or list stated in two places | Keep one statement and point to it from the other. Abstract and conclusions are exempt. |
| "Notice that", "As one can see", "It is worth noting" | State the fact directly. |
| Metaphor or idiom: "in disguise", "clue", "recipe", "cashes in" | Use plain wording with identical meaning: "in different notation", "start from", "formula". Keep field idioms such as "the gap survives disorder". |
| Fancy words where simple ones explain the idea: "hence", "thus", "likewise", "utilize", "demonstrate", "commence" | Use "so", "also", "use", "show", "start". Preserve mathematical verbs, quantifiers, and adjectives as required by the technical-words rule. |
| Wrong count or qualifier, such as "three approximations" when there are four | Correct it or drop the number. |
| A derivation that starts before the system, assumptions, symbols, and target quantity are stated | **Comment only.** Ask for the setup, and a labelled figure when geometry matters. |
| "Always", "only", "never" contradicted later | Qualify or cut the claim. |
| Two or more inline computations in a paragraph | Combine into one display and one explanatory sentence. Cut algebra that earns no display, subject to the equation and derivation guardrails. |
| Multiple asides in a paragraph, intensifiers, or empty evaluatives | Cut the aside or make it a sentence; delete intensifiers. Preserve magnitude and certainty hedges listed above. |
| "Not X but Y" with X absent elsewhere in the argument | Propose stating Y. **Comment only.** Keep the frame when the contrast is the result. |
| Empty meta-talk: "this answers the question posed above", "as promised" | Delete. Keep signposts naming the section's job or pointing to a result. |
| In Theory, Methods, Results, or Analysis: a second object, preview, or unused interpretation | **Comment only.** Propose cutting or moving the digression to where its object is the subject. Retain only necessary cross-references and explain the dependency. Introduction and Conclusions are exempt. |

## Guardrails

- **Change wording, never meaning.** Preserve definitions, theorems, claims, and field terms. Never add or remove a claim, figure, or derivation step as a language fix.
- **Recheck every number, count, and qualifier** in each rewritten sentence before continuing.
- **Comment on content changes; do not apply them.** This includes changing quantifiers or hedges, adding missing justifications, deleting paragraphs as digressions, or removing "not X but Y" contrasts. Use `[reviewer]` comments: `% [reviewer]` in LaTeX, `// [reviewer]` in Typst, or HTML comments in Markdown. The author writes the replacement.
- **Leave passing passages alone.** Every proposed rewrite names its rule; never rewrite merely to produce a diff.
- **Prose rules never require figure detail.** Conceptual and overview figures may omit implementation and timing details. Use the Figure Rulebook in `write-paper` to judge figures against their stated purpose. Flag omissions only if they materially misrepresent the central mechanism or contradict a claim attributed to the figure. Prefer clarifying labels, captions, or nearby prose; weigh added graphics against readability. Diagrams need not depict every mechanism discussed in the text.
