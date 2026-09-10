---
name: how-to-technical-writing
description: Agentic trigger. Use when writing or polishing scientific prose at the sentence and paragraph level, in a manuscript, report, or review.
---

## Installed resources

Keep the working directory at the user's project. Resolve this loaded `SKILL.md`
with `Path(path).resolve()` before locating resources; follow symlinks. Bare
`helpers/`, `references/`, and template paths are relative to that real skill
directory. A path written as `skills/<name>/...` means the installed `<name>`
skill's directory from the agent's skill catalog, not a path in the user's project.
Locate each dependency by its public skill name; copied skills need not be siblings.
If a dependency is absent, report the missing skill and install it before that step.
Shared writing files are bundled in `how-to-write-ideas-report/references/`.


# Writing Style Guide

The sentence- and paragraph-level rules shared by every skill that produces or reviews scientific prose: `write-paper` applies them while drafting, `review-paper` hunts for their violations and proposes fixes, and `how-to-write-ideas-report` and `survey` report mode follow them for report prose. Notation and figure rules stay in `skills/write-paper/SKILL.md` (Notation Rulebook, Figure Rulebook); the reasons behind every rule are in `skills/write-paper/references.md`, and the model paper that executes them is `skills/write-paper/sources/1807.01815_Ho2019_quantum-scars.md`.

The rules were distilled from Martinis, von Delft, and a language-polish checklist for teaching material. The guardrails at the end exist because several rules are dangerous when applied mechanically to a research manuscript.

---

## Rules

Clarity outranks every rule below; when two collide, keep the clearer sentence.

- **One concept per sentence, about 20 words.** Twenty is a target, not a ceiling. A sentence with a semicolon, a colon-plus-clause, and a trailing "so …" is three sentences; keep the logical word ("so", "because") at the head of the next one. Do not split a sentence that wraps a display equation or binds a hypothesis to its conclusion. If two concepts must coexist, make sure both are already familiar to the reader.
- **Direct to the point.** Say the thing. No content-free opener ("In this section we discuss several aspects of …"), no "Notice that" / "As one can see" / "Interestingly,", and no meta-talk that adds nothing ("as promised above"). A sentence that names the section's job or points the reader to a result is signposting, not warm-up, and stays.
- **Name the earlier context instead of "obviously".** A claim that rests on something earlier names it: "Because Eq. (3) is linear in $t$, …", not "Clearly, …". Never tell the reader a step is obvious or trivial. The reason must already exist in the manuscript; if it does not, ask the author instead of writing one from general knowledge.
- **Plain connectives, but keep every technical word.** "so" over "hence" and "thus"; "also" over "likewise"; "use" over "utilize". Swap only connectives and filler that have no mathematical reading. Never swap a verb, quantifier, or adjective inside a mathematical statement: "arbitrary", "determined by", "identify with", and "the converse" are technical. Never replace a term the field uses ("decoherence", "ansatz", "thermalize") with a simpler word: if it is in the textbook or a referee's vocabulary, it stays.
- **No metaphor the paper does not draw.** "in disguise", "the clue", "recipe", "cashes in" go; use the plain word ("in different notation", "start from", "formula"). Replace only when a plain word carries the identical meaning; field idioms such as "the gap survives disorder" are technical usage and stay. A physical intuition in prose stays when the sentence itself makes it precise; it never requires a new figure, and it never requires an existing figure to depict it.
- **Active voice for actions.** "We measured" beats "measurements were performed." Reserve passive only for things genuinely without an agent. Put the verb early and give it a concrete subject.
- **Concrete verbs over nominalizations.** "We adopt the new notation" beats "Adoption of the new notation is undertaken."
- **No stacked asides, no idle adverbs.** At most one parenthesis or dash aside per paragraph; make the rest sentences. Delete intensifiers and empty evaluatives only: "very", "quite", "rather", "interestingly", "importantly", "notably". Hedges of magnitude or certainty are content and stay: "approximately", "nearly", "at most", "typically", "numerically", "only", "exactly". Drop a "not X but Y" frame only when X appears nowhere else in the argument; when the contrast with X is the result, the frame stays.
- **Prose carries ideas; calculations go to displays.** A body sentence states an idea, an intuition, or a logical step. Two or more inline computations in one paragraph become one display followed by one sentence saying what it shows. Whether that display earns its place is the Notation Rulebook's call. Never inline or cut an equation whose label is referenced elsewhere; in a letter, move algebra to the supplement rather than deleting a step the reader needs to reproduce the result.
- **Locality (Theory, Methods, Results, Analysis).** A paragraph stays on one object; a section stays on its job. Do not connect two concepts, preview a later section, or add a second interpretation the argument never uses. A cross-reference is fine when the current step depends on it, and the sentence says why ("by the linearity of Eq. (3)"). The Introduction and Conclusions are exempt: prior-work context, cross-field connections, and implications live there by design.
- **Say it once (within the body).** If the main-result sentence states it, the paragraph after the equation does not restate it. If a paragraph's last sentence repeats its first, cut one. Restatement across the abstract, introduction, and conclusions is deliberate (Iron Rule 2), and so is naming a main result more than once.
- **No overclaim smuggled in by prose.** A rewritten sentence keeps every count, number, and qualifier right ("the three approximations" when four were made is a bug). "Always", "only", and "never" stay only if nothing later in the paper contradicts them.
- **Match grammar where ideas already run in parallel.** When a sentence compares or contrasts two things, or a list already exists, give the items the same grammatical shape. This is a rule about wording, not layout: prose stays prose. Do not turn a paragraph into a bulleted list, and do not add a list a journal would not print; a paper reads as an argument, and lists break its flow.
- **Signposting.** Use phrases like *"This is our main result," "We now turn to," "In summary,"* to orient the reader. The reader cannot tell which sentence carries the punchline unless you say so. The model paper signposts every turn — *"Specifically," "Conversely," "Most surprisingly,"* — so the reader always knows whether a sentence narrows, contrasts, or escalates.
- **Each paragraph: one job.** Topic sentence at the top, supporting detail in the middle, transition or stress at the end.

---

## Hunt table (for reviewing and for the final language pass)

What to hunt for at the sentence level, with the fix. Each finding cites its row. A passage that trips no row stays untouched. Rows marked **comment only** are never applied as edits, even after approval: the author writes those words.

| Hunt for | Fix |
|---|---|
| A sentence over ~25 words, or two clauses joined by a semicolon or "and … so …" | Split. Keep the logical word ("so", "because") at the start of the second sentence. Leave whole a sentence that wraps a display equation or binds a hypothesis to its conclusion. |
| A paragraph that restates the main-result sentence, the equation, or its own opening | Delete the restatement; keep the canonical statement. |
| "Notice that", "As one can see", "Interestingly," "It is worth noting" | Rewrite as a declarative statement of the fact. |
| "Obviously", "clearly", "trivially", or an assertion with no visible reason | Name the earlier context in one clause: which equation, figure, or section gives it. **Comment only** when that reason is not already in the manuscript. |
| A metaphor or idiom ("in disguise", "clue", "recipe", "cashes in") | The plain word ("in different notation", "start from", "formula"), only when it carries the identical meaning. Field idioms ("the gap survives disorder") stay. |
| A Latinate connective where an everyday one exists ("hence", "thus", "likewise", "utilize") | "so", "also", "use". Connectives and filler only. Never swap a verb, quantifier, or adjective in a mathematical statement: "arbitrary", "determined by", "identify with", "the converse" are technical. |
| A count or qualifier the prose gets wrong ("the three approximations" when four were made) | Correct it or drop the number. |
| "Always", "only", "never" that a later section contradicts | Add the qualifier, or cut the claim. |
| Two or more inline computations in one paragraph | One display; one sentence names what it shows. Cut the algebra if it earns no display. |
| More than one aside per paragraph; an intensifier or empty evaluative ("very", "quite", "interestingly", "notably") | Cut the aside or make it a sentence; delete the intensifier. Hedges of magnitude or certainty ("approximately", "at most", "typically", "only", "exactly") are content and stay. |
| A "not X but Y" frame where X appears nowhere else in the argument | State Y. **Comment only**; when the contrast with X is the result, the frame stays. |
| Empty meta-talk ("this answers the question posed above", "as promised") | Delete. A signpost that names the section's job or points to a result is not meta-talk. |
| In Theory, Methods, Results, or Analysis: a paragraph that drifts to a second object, previews a later section, or adds an interpretation the argument never uses | **Comment only.** Propose cutting the digression or moving it to where that object is the subject. Keep a cross-reference only when the step depends on it, and say why. Introduction and Conclusions exempt. |

---

## Guardrails when applying

- **Change how a sentence is written, never what it says.** Never alter the content of a definition, theorem, or claim while rewording it; never add or remove a claim, figure, or derivation step under a language fix; never replace a field term with a simpler word.
- **Recheck every number, count, and qualifier** a rewritten sentence mentions before moving on.
- **Comment, do not apply, when a fix touches content.** An edit that would change a quantifier or hedge, add a justification the manuscript does not already contain, delete a paragraph as a digression, or remove a "not X but Y" contrast is left as a `[reviewer]` comment (`% [reviewer]` in LaTeX, `// [reviewer]` in Typst, an HTML comment in Markdown). The author writes those words.
- **Leave passing passages alone.** A rewrite is never proposed for the sake of a diff. Every finding names the rule it serves.
- **These are prose rules; they never add figure detail.** Conceptual and overview figures may intentionally omit implementation and timing detail. Judge a figure against its stated explanatory purpose (the Figure Rulebook in `write-paper`), and flag an omission only when it materially misleads the reader about the central mechanism or contradicts a claim the text attributes to the figure. Prefer clarifying a label, a caption, or the nearby sentence over adding graphical detail, and weigh any added detail against readability. Nothing here requires every mechanism discussed in the text to appear in a diagram.
