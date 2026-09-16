// Copy beside template.bib, then replace the example content and bibliography.
// The canonical source bibliography remains .knowledge/references.bib.
// Compile: typst compile review.typ review.pdf
// Optional: --input heading-font="Your installed sans-serif font"

#let title = [TODO: Review title]
#let authors = "TODO: author / review draft"
#let review_date = [TODO: YYYY-MM-DD]
#let short_title = [Research review] // Short running title; keep to one line.
#let serif = "Libertinus Serif"
#let sans = (sys.inputs.at("heading-font", default: "Avenir Next"), serif)
#let ink = rgb("24282b")
#let muted = rgb("53616b")
#let accent = rgb("245b65")
#let tint = rgb("f2f6f6")
#let rule = rgb("cbd4d7")

#set document(title: title, author: authors)
#set page(
  paper: "a4", margin: (x: 18mm, y: 18mm),
  footer: context {
    set text(font: sans, size: 8pt, fill: muted)
    grid(columns: (1fr, auto), gutter: 12pt, short_title, counter(page).display())
  },
)
#set text(font: serif, size: 10pt, fill: ink)
#set par(justify: true, leading: 0.55em, spacing: 0.65em)
#set heading(numbering: "1.1")
#set list(indent: 1em, body-indent: 0.5em, spacing: 0.35em)
#show heading: set text(font: sans, weight: "bold")
#show heading.where(level: 1): set text(size: 13pt)
#show heading.where(level: 2): set text(size: 11pt)
#show heading.where(level: 1): set block(above: 1.3em, below: 0.55em)
#show heading.where(level: 2): set block(above: 1em, below: 0.45em)
#show link: set text(fill: accent)
#show figure.caption: set text(size: 9pt, fill: muted)
#set figure(gap: 6pt)

// Short assessments only. Ordinary prose needs no container.
#let section_box(title, body, fill: tint, stroke: accent) = block(
  width: 100%, inset: 9pt, fill: fill,
  stroke: (left: 2pt + stroke), breakable: true,
)[
  #block(sticky: true, below: 4pt)[
    #text(font: sans, size: 9.5pt, weight: "bold", title)
  ]
  #body
]

// Cell for a flow, architecture, or timeline grid. Use arrows only for an
// actual sequence or dependency. Names and descriptions must carry the
// relationship on their own; `fill` is optional emphasis.
#let stage(name, body, fill: tint) = block(
  width: 100%, inset: 7pt, fill: fill, stroke: 0.5pt + rule,
)[
  #align(center)[
    #text(font: sans, size: 9pt, weight: "bold", name)
    #v(3pt)
    #text(size: 8.5pt, body)
  ]
]

// Two independent lists, only for competing solutions to the same problem.
// Complementary capabilities need a prose assessment instead.
#let proscons(pros, cons) = grid(
  columns: (1fr, 1fr), gutter: 12pt,
  ..(([Strengths], pros), ([Limitations], cons)).map(((label, body)) => block(
    width: 100%, inset: (top: 5pt), stroke: (top: 0.5pt + rule),
    breakable: true,
  )[
    #block(sticky: true, below: 3pt)[
      #text(font: sans, size: 9pt, weight: "bold", label)
    ]
    #body
  ]),
)

// Rows are arrays of cells; a row whose length differs from `columns` fails
// with a message naming the row. Keep text brief; explain qualifications in
// prose. Horizontal rules separate records without boxing in every cell.
// Headers repeat when a table continues onto another page.
#let report_table(columns, headers, rows) = {
  assert(headers.len() == columns.len(), message: "report_table: "
    + str(headers.len()) + " headers but " + str(columns.len()) + " columns")
  for (i, row) in rows.enumerate() {
    assert(row.len() == columns.len(), message: "report_table: row " + str(i + 1)
      + " has " + str(row.len()) + " cells but the table has " + str(columns.len()) + " columns")
  }
  set text(size: 9pt)
  set par(justify: false, leading: 0.45em)
  table(
    columns: columns, align: left + top,
    inset: (x: 5pt, y: 5pt),
    stroke: (x, y) => (bottom: if y == 0 { 0.8pt + accent } else { 0.4pt + rule }),
    fill: (x, y) => if y == 0 { tint },
    table.header(repeat: true, ..headers.map(h => text(weight: "bold", h))),
    ..rows.flatten(),
  )
}

// Adapt both headers and widths to criteria that discriminate this field.
#let compare_table(
  rows,
  columns: (1.1fr, 1fr, 1.25fr, 0.85fr, 1.4fr),
  headers: ([Approach], [Scalability], [Verification / cost], [Maturity], [Best use]),
) = report_table(columns, headers, rows)

// Rank and urgency get enough room for their labels, not a fixed tiny fraction.
#let problem_table(
  rows,
  columns: (auto, 1.2fr, 1.6fr, 1fr, auto),
  headers: ([No.], [Problem], [Why it matters], [Who can act], [Urgency]),
) = report_table(columns, headers, rows)

// Title is not a numbered section or an outline entry.
#block(breakable: false, below: 10pt)[
  #text(font: sans, size: 18pt, weight: "bold", title)
  #v(5pt)
  #text(font: sans, size: 9pt, fill: muted)[#authors #h(1em) #review_date]
]

*Scope.* TODO: what this report assesses, who it is for, and what it excludes.
State the evidence cutoff. Organize by technical approach.

#section_box(
  [Assessment in brief],
  [TODO: the principal finding, the evidence supporting it, and the main unresolved constraint. Give the reader a reason to continue @Example2024.],
)

= Overview

// 2–3 paragraphs: define the topic and problem, explain the stakes, then
// distinguish it from the prior approach. Cite claims, not filler.
TODO: define the topic for a new reader @Example2024.

#figure(
  grid(
    columns: (1fr, auto, 1fr, auto, 1fr), gutter: 6pt,
    align: center + horizon,
    stage([Concept A], [one-line role]),
    [→],
    stage([Concept B], [one-line role]),
    [→],
    stage([Concept C], [one-line role]),
  ),
  caption: [TODO: explain the relationship shown and the point it establishes.],
)

= Key questions

// One subsection per subtopic or open question the field is trying to settle,
// typically 2–5. A question earns its place by what answering it gives:
// deeper understanding, practical value, or both. Do not list strengths and
// limitations here; those belong to techniques.

== TODO: Key question one

*The question.* TODO: state it in one sentence.

*Why it matters.* Understanding: TODO what an answer would settle or unify.
Value: TODO what it would enable in practice @Example2024.

*Where it stands.* TODO: the best partial answer and its limits @Example2025.

== TODO: Key question two

*The question.* TODO.

*Why it matters.* Understanding: TODO. Value: TODO @Example2025.

*Where it stands.* TODO @Example2024.

= Technical approaches

// Give each method family a subsection, typically 3–6 in total. Strengths and
// limitations apply here, to techniques, not to questions. Add a timeline
// (a `stage` grid of eras) only if chronology explains a technical change.

== TODO: Approach one

*Mechanism.* TODO: the representation, objective, or operation that defines it.

*Best evidence.* TODO: the strongest supported result and its conditions @Example2024 @Example2025.

#proscons(
  list([TODO strength @Example2024.], [TODO strength @Example2025.]),
  list([TODO limitation @Example2024.], [TODO limitation @Example2025.]),
)

== TODO: Approach two

*Mechanism.* TODO.

*Best evidence.* TODO @Example2025.

#proscons(
  list([TODO strength @Example2025.]),
  list([TODO limitation @Example2025.], [TODO limitation @Example2024.]),
)

== Comparison

// Optional. Compare only approaches with shared assumptions and criteria.
// Keep these native tables in the page flow so long tables can paginate.
#compare_table((
  ([Approach one], [TODO @Example2024], [TODO], [TODO], [TODO]),
  ([Approach two], [TODO @Example2025], [TODO], [TODO], [TODO]),
))

= Open problems

// Rank 4–8 evidence-backed problems in a completed review. Priority is written
// explicitly, so neither color nor a legend is needed to read it.
#problem_table((
  ([1], [TODO problem], [TODO why it matters @Example2024], [TODO who], [Critical]),
  ([2], [TODO problem], [TODO why it matters @Example2025], [TODO who], [High]),
  ([3], [TODO problem], [TODO why it matters @Example2024], [TODO who], [Medium]),
))

#v(6pt)
*Next step.* TODO: the measurement or result that would resolve the most
consequential uncertainty. Do not repeat the opening assessment.

#bibliography("template.bib", title: "References", style: "ieee")
