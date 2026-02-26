#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge
#set page(width: auto, height: auto, margin: (top: 8pt, bottom: 8pt, left: 8pt, right: 8pt))

#diagram(
  node-stroke: 0.8pt,
  edge-stroke: 1pt,
  spacing: (14mm, 12mm),
  mark-scale: 60%,

  // Colors — only 3 key steps get color
  let bk = black,
  let bk-fill = white,
  let bk-stroke = black,
  let survey-fill = rgb("#e0f2fe"),
  let survey-stroke = rgb("#0284c7"),
  let brainstorm-fill = rgb("#f3e8ff"),
  let brainstorm-stroke = rgb("#7c3aed"),
  let critique-fill = rgb("#fee2e2"),
  let critique-stroke = rgb("#dc2626"),
  let arrow = black,
  let loop-color = rgb("#4a5568"),
  let w = 140pt,
  let s = 12pt,
  let sm = 10pt,

  // Row 0 (left to right): Entry → Survey → Verify
  node((0, 0), box(width: w, align(center, text(fill: bk, size: s)[*User states idea*])),
    fill: bk-fill, stroke: 1pt + bk-stroke, corner-radius: 4pt, inset: 5pt, name: <idea>),

  node((1, 0), box(width: w, align(center, text(fill: bk, size: s)[*Clarify*\ multiple choice Q])),
    fill: bk-fill, stroke: 1pt + bk-stroke, corner-radius: 4pt, inset: 5pt, name: <clarify>),

  node((2, 0), box(width: w, align(left, text(fill: bk, size: s)[
    *Step 1: Survey*\
    #text(size: sm)[#sym.bullet Landscape #sym.bullet Adjacent\
    #sym.bullet Cross-vocabulary\
    #sym.bullet Cross-method\
    #sym.bullet Historical #sym.bullet Negative\
    #sym.bullet Benchmarks & datasets]
  ])),
    fill: survey-fill, stroke: 1pt + survey-stroke, corner-radius: 4pt, inset: 5pt, name: <survey>),

  node((3, 0), box(width: w, align(center, text(fill: bk, size: s)[*Step 2: Verify*\ fact-check citations])),
    fill: bk-fill, stroke: 1pt + bk-stroke, corner-radius: 4pt, inset: 5pt, name: <verify>),

  // Row 1 (right to left): Brainstorm → Critique → AI Judge → User Judge
  node((3, 1), box(width: w, align(left, text(fill: bk, size: s)[
    *Step 3: Brainstorm*\
    #text(size: sm)[#sym.bullet Combiner #sym.bullet Inverter\
    #sym.bullet Transplanter\
    #sym.bullet Bottleneck-breaker\
    #sym.bullet *Human ideas*]
  ])),
    fill: brainstorm-fill, stroke: 1pt + brainstorm-stroke, corner-radius: 4pt, inset: 5pt, name: <brainstorm>),

  node((2, 1), box(width: w, align(left, text(fill: bk, size: s)[
    *Step 4: Critique*\
    #text(size: sm)[#sym.bullet Prior art #sym.bullet Novelty\
    #sym.bullet Rigor #sym.bullet Impact\
    #sym.bullet Weakest assumption\
    #sym.bullet Feasibility]
  ])),
    fill: critique-fill, stroke: 1pt + critique-stroke, corner-radius: 4pt, inset: 5pt, name: <critique>),

  node((1, 1), box(width: w, align(center, text(fill: bk, size: s)[*Step 5: AI Judge*\ kill, rank, present])),
    fill: bk-fill, stroke: 1pt + bk-stroke, corner-radius: 4pt, inset: 5pt, name: <aijudge>),

  node((0, 1), box(width: w, align(center, text(fill: bk, size: s)[*Step 6: User Judge*\ #text(size: sm)[proposal / deeper / new angle]])),
    fill: bk-fill, stroke: 1pt + bk-stroke, corner-radius: 4pt, inset: 5pt, name: <userjudge>),

  // Row 2: Refine → Doc
  node((0, 2), box(width: w, align(center, text(fill: bk, size: s)[*Refine*\ brainstorm report])),
    fill: bk-fill, stroke: 1pt + bk-stroke, corner-radius: 4pt, inset: 5pt, name: <refine>),

  node((1, 2), box(width: w, align(center, text(fill: bk, size: s)[*Brainstorm Report*\ + BibTeX])),
    fill: bk-fill, stroke: 1pt + bk-stroke, corner-radius: 4pt, inset: 5pt, name: <doc>),

  // Row 0 forward (left to right)
  edge(<idea>, <clarify>, "-|>", stroke: 1pt + arrow),
  edge(<clarify>, <survey>, "-|>", stroke: 1pt + arrow),
  edge(<survey>, <verify>, "-|>", stroke: 1pt + arrow),

  // Corner: verify down to brainstorm
  edge(<verify>, <brainstorm>, "-|>", stroke: 1pt + arrow),

  // Row 1 forward (right to left)
  edge(<brainstorm>, <critique>, "-|>", stroke: 1pt + arrow),
  edge(<critique>, <aijudge>, "-|>", stroke: 1pt + arrow),
  edge(<aijudge>, <userjudge>, "-|>", stroke: 1pt + arrow),

  // Exit: user judge down to refine
  edge(<userjudge>, <refine>, "-|>", stroke: 1pt + arrow,
    label: text(fill: bk, size: sm)[write proposal], label-side: left),
  edge(<refine>, <doc>, "-|>", stroke: 1pt + arrow),

  // Loop: user judge back up to survey
  edge(<userjudge>, <survey>, "-|>", bend: 0deg,
    stroke: (paint: loop-color, thickness: 1pt, dash: "dashed"),
    label: text(fill: loop-color, size: sm, weight: "medium")[go deeper / new angle], label-side: center),
)
