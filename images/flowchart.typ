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
  let critique-fill = rgb("#fef3c7"),
  let critique-stroke = rgb("#d97706"),
  let arrow = black,
  let loop-color = rgb("#4a5568"),
  let w = 140pt,
  let s = 12pt,
  let sm = 10pt,

  // Row 0: User idea → Background → Clarify → Survey
  node((0, 0), box(width: w, align(center, text(fill: bk, size: s)[*User states idea*])),
    fill: bk-fill, stroke: 1pt + bk-stroke, corner-radius: 4pt, inset: 5pt, name: <idea>),

  node((1, 0), box(width: w, align(center, text(fill: bk, size: s)[*Background*\ #text(size: sm)[Zotero / Scholar lookup]])),
    fill: bk-fill, stroke: 1pt + bk-stroke, corner-radius: 4pt, inset: 5pt, name: <background>),

  node((2, 0), box(width: w, align(center, text(fill: bk, size: s)[*Clarify*\ multiple choice Q])),
    fill: bk-fill, stroke: 1pt + bk-stroke, corner-radius: 4pt, inset: 5pt, name: <clarify>),

  node((3, 0), box(width: w, align(left, text(fill: bk, size: s)[
    *Survey*\
    #text(size: sm)[#sym.bullet Landscape #sym.bullet Adjacent\
    #sym.bullet Cross-vocabulary\
    #sym.bullet Cross-method\
    #sym.bullet Historical #sym.bullet Negative\
    #sym.bullet Benchmarks & datasets]
  ])),
    fill: survey-fill, stroke: 1pt + survey-stroke, corner-radius: 4pt, inset: 5pt, name: <survey>),

  // Row 1: Ideator (left) and Critique (right)
  node((0.5, 1), box(width: 180pt, align(left, text(fill: bk, size: s)[
    *Ideator* #text(size: sm)[(persistent)]\
    #text(size: sm)[
      Creative lenses:\
      Combiner · Inverter · Transplanter\
      Bottleneck-breaker · Restater · Scoper\
      #sym.arrow.r proposes ideas
    ]
  ])),
    fill: ideas-fill, stroke: 1pt + ideas-stroke, corner-radius: 4pt, inset: 5pt, name: <ideator>),

  node((2.5, 1), box(width: 180pt, align(left, text(fill: bk, size: s)[
    *Main agent* #text(size: sm)[(mediator)]\
    #text(size: sm)[
      Diagnose weakness → pick critique lens\
      Ideator-routed: Feasibility, Impact,\
      #h(1em)Success criteria, Signs of progress\
      Main-routed: Prior art, Assumption,\
      #h(1em)Failure mode, Timing, Completeness
    ]
  ])),
    fill: critique-fill, stroke: 1pt + critique-stroke, corner-radius: 4pt, inset: 5pt, name: <critique>),

  // Row 2: User in the middle
  node((1.5, 2), box(width: 200pt, align(center, text(fill: bk, size: s)[
    *User*\
    #text(size: sm)[selects ideas, picks questions, steers direction]
  ])),
    fill: bk-fill, stroke: 1pt + bk-stroke, corner-radius: 4pt, inset: 5pt, name: <user>),

  // Row 3: Formal critique → Rank → User Judge
  node((0.5, 3), box(width: 180pt, align(center, text(fill: bk, size: s)[*Formal critique*\ #text(size: sm)[adversarial review, kill or rank]])),
    fill: critique-fill, stroke: 1pt + critique-stroke, corner-radius: 4pt, inset: 5pt, name: <formal>),

  node((2.5, 3), box(width: 180pt, align(center, text(fill: bk, size: s)[*User Judge*\ #text(size: sm)[write report / go deeper / new angle]])),
    fill: bk-fill, stroke: 1pt + bk-stroke, corner-radius: 4pt, inset: 5pt, name: <judge>),

  // Row 4: Ideas Report
  node((1.5, 4), box(width: 200pt, align(center, text(fill: bk, size: s)[*Ideas Report*\ #text(size: sm)[+ BibTeX references]])),
    fill: bk-fill, stroke: 1pt + bk-stroke, corner-radius: 4pt, inset: 5pt, name: <doc>),

  // === Edges ===

  // Row 0 forward
  edge(<idea>, <background>, "-|>", stroke: 1pt + arrow),
  edge(<background>, <clarify>, "-|>", stroke: 1pt + arrow),
  edge(<clarify>, <survey>, "-|>", stroke: 1pt + arrow),

  // Survey down to Ideator
  edge(<survey>, <ideator>, "-|>", stroke: 1pt + arrow),

  // Ideator → Critique (presents ideas)
  edge(<ideator>, <critique>, "-|>", stroke: 1pt + arrow,
    label: text(fill: bk, size: sm)[ideas], label-side: left),

  // Critique → User (questions)
  edge(<critique>, <user>, "-|>", stroke: 1pt + arrow,
    label: text(fill: bk, size: sm)[questions], label-side: right),

  // User → Ideator (feedback, only user content)
  edge(<user>, <ideator>, "-|>", stroke: 1pt + arrow,
    label: text(fill: bk, size: sm)[feedback], label-side: left),

  // User → Formal critique (evaluate)
  edge(<user>, <formal>, "-|>", stroke: 1pt + arrow,
    label: text(fill: bk, size: sm)[evaluate], label-side: left),

  // Formal → Judge
  edge(<formal>, <judge>, "-|>", stroke: 1pt + arrow,
    label: text(fill: bk, size: sm)[ranked table], label-side: left),

  // Judge → Doc (write report)
  edge(<judge>, <doc>, "-|>", stroke: 1pt + arrow,
    label: text(fill: bk, size: sm)[write report], label-side: right),

  // Judge loop back to Survey (go deeper / new angle)
  edge(<judge>, <survey>, "-|>", bend: 0deg,
    stroke: (paint: loop-color, thickness: 1pt, dash: "dashed"),
    label: text(fill: loop-color, size: sm, weight: "medium")[go deeper / new angle], label-side: center),
)
