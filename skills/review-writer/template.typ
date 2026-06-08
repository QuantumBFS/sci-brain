// review-writer Typst template — copy to articles/YYYY-MM-DD-<topic>-review.typ
// and replace the placeholder content. Compile with: typst compile <file>.typ
// Citations use a sibling bib (see the bibliography() call at the bottom);
// copy the project's ref.bib beside the document, or adapt template.bib.

#set page(margin: 1.6cm)
#set text(size: 10pt)
#set par(justify: true, leading: 0.62em)
#set heading(numbering: "1.")

#let title = [TODO: Review Title]
#let authors = [TODO: author / "review draft"]

#show link: set text(fill: blue.darken(30%))

// ---- reusable helpers ---------------------------------------------------

#let section_box(title, body, fill: rgb("f7f8fc"), stroke: rgb("d9deeb")) = rect(
  width: 100%, inset: 10pt, radius: 6pt, fill: fill, stroke: stroke,
  [#strong[#title] #v(0.3em) #body],
)

// horizontal strip cell (use in a grid for a flow/era/landscape diagram)
#let stage(name, body, fill) = rect(
  width: 100%, inset: 7pt, radius: 5pt, fill: fill, stroke: rgb("c7cfe0"),
  align(center)[#text(weight: "semibold", size: 9pt)[#name] #v(0.2em) #text(size: 8pt)[#body]],
)

// per-approach strengths / limitations (two UNPAIRED bullet lists)
#let proscons(pros, cons) = grid(
  columns: (1fr, 1fr), gutter: 0.6em,
  rect(width: 100%, inset: 7pt, radius: 5pt, fill: rgb("eef6ef"), stroke: rgb("bcd9c4"))[
    #text(weight: "semibold", fill: green.darken(30%))[Strengths]
    #pros
  ],
  rect(width: 100%, inset: 7pt, radius: 5pt, fill: rgb("fbecec"), stroke: rgb("e3c6c6"))[
    #text(weight: "semibold", fill: red.darken(20%))[Limitations]
    #cons
  ],
)

// optional cross-approach comparison matrix
#let compare_table(rows) = table(
  columns: (20%, 18%, 22%, 16%, 24%),
  stroke: (x, y) => if y == 0 { 0.8pt + black } else { 0.4pt + rgb("d7dbe6") },
  inset: 6pt,
  table.header(
    [#strong[Approach]], [#strong[Scalability]], [#strong[Verifiability / cost]], [#strong[Maturity]], [#strong[Best-fit use case]],
  ),
  ..rows,
)

#let problem_table(rows) = table(
  columns: (5%, 27%, 38%, 20%, 10%),
  stroke: (x, y) => if y == 0 { 0.8pt + black } else { 0.4pt + rgb("d7dbe6") },
  inset: 6pt,
  table.header(
    [#strong[No.]], [#strong[Problem]], [#strong[Why it matters]], [#strong[Who could solve it]], [#strong[Urgency]],
  ),
  ..rows,
)

// ---- title --------------------------------------------------------------

#heading(numbering: none)[#title]

#align(center)[
  #text(size: 12pt, weight: "semibold")[State-of-the-Art Review]
  #v(0.25em)
  #text(fill: gray.darken(20%))[#authors]
  #v(0.25em)
  #text(fill: gray.darken(10%))[TODO: Generated YYYY-MM-DD from the knowledge base.]
]

#v(0.9em)

#section_box(
  [Scope],
  [TODO: one paragraph — what this report assesses, who it is for, and what it deliberately excludes. State that the review is organized #emph[by technical approach].],
)

= What and Why

// TODO: 2–3 paragraphs. (1) What it is + the problem it solves.
// (2) Why it matters now — the motivation/stakes. (3) How it differs from the
// dominant or prior approach. Cite real claims with @citekey.

TODO: define the topic for a reader who has never heard of it @Example2024.

#v(0.5em)
#figure(
  grid(
    columns: (30%, 5%, 30%, 5%, 30%),
    align: center + horizon,
    stage([Concept A], [one-line role], rgb("eef3ff")),
    align(center + horizon)[#text(size: 14pt)[→]],
    stage([Concept B], [one-line role], rgb("e9f7ee")),
    align(center + horizon)[#text(size: 14pt)[→]],
    stage([Concept C], [one-line role], rgb("fdf2e9")),
  ),
  caption: [TODO: a concept / architecture / problem-framing diagram.],
)

= Technical Approaches

// Identify the main approaches / method families (typically 3–6) and give one
// subsection each. Optionally open with a short field-wide timeline/landscape.

#figure(
  grid(
    columns: (30%, 5%, 30%, 5%, 30%),
    align: center + horizon,
    stage([Era 1 (years)], [what defined it], rgb("eef3ff")),
    align(center + horizon)[#text(size: 13pt)[→]],
    stage([Era 2 (years)], [what defined it], rgb("eef6ef")),
    align(center + horizon)[#text(size: 13pt)[→]],
    stage([Era 3 (years)], [what defined it], rgb("fdf2e9")),
  ),
  caption: [Optional field landscape / timeline.],
)

== TODO: Approach One

*What it is.* TODO: the mechanism at one level of detail — the representation, objective, or trick that defines it.

*State of the art.* TODO: the strongest current results, leading groups, maturity — lead with the best result, each cited @Example2024 @Example2025.

#proscons(
  list([TODO strength @Example2024.], [TODO strength @Example2025.]),
  list([TODO limitation @Example2024.], [TODO limitation @Example2025.]),
)

== TODO: Approach Two

*What it is.* TODO.

*State of the art.* TODO @Example2025.

#proscons(
  list([TODO strength @Example2025.]),
  list([TODO limitation @Example2025.], [TODO limitation @Example2024.]),
)

// ... repeat one == subsection per approach (3–6 total). Optionally add a final
// cross-cutting subsection (e.g. shared infrastructure) that is not itself an
// approach but every approach depends on.

== At-a-glance comparison

// Optional: include when the field has several comparable approaches; drop for a
// single-approach topic.
#compare_table((
  [Approach One], [TODO @Example2024], [TODO], [TODO], [TODO],
  [Approach Two], [TODO @Example2025], [TODO], [TODO], [TODO],
))

= Open Problems

#problem_table((
  [1], [TODO problem], [TODO why it matters @Example2024], [TODO who], [#text(fill: red.darken(10%))[Critical]],
  [2], [TODO problem], [TODO why it matters @Example2025], [TODO who], [#text(fill: orange.darken(20%))[High]],
  [3], [TODO problem], [TODO why it matters], [TODO who], [#text(fill: olive.darken(10%))[Medium]],
))

#v(0.8em)

#section_box(
  [Bottom line],
  [TODO: one tight paragraph — the synthesis / recommendation the reader should leave with @Example2024.],
  fill: rgb("eef6ef"), stroke: rgb("bcd9c4"),
)

// ---- optional: Business Relevance (only if business context is available) ---
// = Business Relevance
//   - Strategic fit (numbered points)
//   - Product-level impact table
//   - Customer map table
//   - Recommended actions (highlighted box)
//   - What we should NOT do (guardrails)

#v(0.6em)

#bibliography("template.bib", title: "References", style: "ieee")
