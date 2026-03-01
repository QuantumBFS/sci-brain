#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge
#set page(width: auto, height: auto, margin: (top: 8pt, bottom: 8pt, left: 8pt, right: 8pt))

#diagram(
  node-stroke: 0.8pt,
  edge-stroke: 1pt,
  spacing: (14mm, 12mm),
  mark-scale: 60%,

  // Colors
  let bk = black,
  let bk-fill = white,
  let bk-stroke = black,
  let survey-fill = rgb("#e0f2fe"),
  let survey-stroke = rgb("#0284c7"),
  let ideas-fill = rgb("#f3e8ff"),
  let ideas-stroke = rgb("#7c3aed"),
  let arrow = black,
  let loop-color = rgb("#4a5568"),
  let w = 140pt,
  let s = 12pt,
  let sm = 10pt,

  // Row 0 (left to right): Idea → Background → Clarify → Survey
  node((0, 0), box(width: w, align(center, text(fill: bk, size: s)[*User states idea*])),
    fill: bk-fill, stroke: 1pt + bk-stroke, corner-radius: 4pt, inset: 5pt, name: <idea>),

  node((1, 0), box(width: w, align(center, text(fill: bk, size: s)[*Step 0: Background*\ #text(size: sm)[Zotero / Scholar lookup]])),
    fill: bk-fill, stroke: 1pt + bk-stroke, corner-radius: 4pt, inset: 5pt, name: <background>),

  node((2, 0), box(width: w, align(center, text(fill: bk, size: s)[*Clarify*\ multiple choice Q])),
    fill: bk-fill, stroke: 1pt + bk-stroke, corner-radius: 4pt, inset: 5pt, name: <clarify>),

  node((3, 0), box(width: w, align(left, text(fill: bk, size: s)[
    *Step 1: Survey*\
    #text(size: sm)[#sym.bullet Landscape #sym.bullet Adjacent\
    #sym.bullet Cross-vocabulary\
    #sym.bullet Cross-method\
    #sym.bullet Historical #sym.bullet Negative\
    #sym.bullet Benchmarks & datasets]
  ])),
    fill: survey-fill, stroke: 1pt + survey-stroke, corner-radius: 4pt, inset: 5pt, name: <survey>),

  // Row 1: Step 2 — Ideas (expanded, spans columns 1-3)
  node((1.5, 1), box(width: 320pt, align(left, text(fill: bk, size: s)[
    *Step 2: Ideas*\
    #text(size: sm)[
      *Ideator* (background): proposals, lenses, Polya development\
      *Critic* (background): novelty check, source verification, formal review\
      *Main agent*: mediates conversation with user\
      #sym.arrow.r AI Judge: kill, rank, present\
      #sym.arrow.r User Judge: proposal / deeper / new angle
    ]
  ])),
    fill: ideas-fill, stroke: 1pt + ideas-stroke, corner-radius: 4pt, inset: 5pt, name: <ideas>),

  // Row 2: Refine → Doc
  node((0, 2), box(width: w, align(center, text(fill: bk, size: s)[*Refine*\ ideas report])),
    fill: bk-fill, stroke: 1pt + bk-stroke, corner-radius: 4pt, inset: 5pt, name: <refine>),

  node((1, 2), box(width: w, align(center, text(fill: bk, size: s)[*Ideas Report*\ + BibTeX])),
    fill: bk-fill, stroke: 1pt + bk-stroke, corner-radius: 4pt, inset: 5pt, name: <doc>),

  // Row 0 forward (left to right)
  edge(<idea>, <background>, "-|>", stroke: 1pt + arrow),
  edge(<background>, <clarify>, "-|>", stroke: 1pt + arrow),
  edge(<clarify>, <survey>, "-|>", stroke: 1pt + arrow),

  // Survey down to Ideas
  edge(<survey>, <ideas>, "-|>", stroke: 1pt + arrow),

  // Exit: Ideas down to Refine
  edge(<ideas>, <refine>, "-|>", stroke: 1pt + arrow,
    label: text(fill: bk, size: sm)[write proposal], label-side: left),
  edge(<refine>, <doc>, "-|>", stroke: 1pt + arrow),

  // Loop: Ideas back up to Survey
  edge(<ideas>, <survey>, "-|>", bend: 0deg,
    stroke: (paint: loop-color, thickness: 1pt, dash: "dashed"),
    label: text(fill: loop-color, size: sm, weight: "medium")[go deeper / new angle], label-side: center),
)
