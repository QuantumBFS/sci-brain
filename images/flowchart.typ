#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge
#set page(width: auto, height: auto, margin: (top: 10pt, bottom: 10pt, left: 10pt, right: 10pt))

#diagram(
  node-stroke: 1pt,
  edge-stroke: 1.2pt,
  spacing: (28mm, 16mm),
  mark-scale: 70%,

  // Colors
  let navy = rgb("#1e3a5f"),
  let entry-fill = rgb("#fef3c7"),
  let entry-stroke = rgb("#d97706"),
  let survey-fill = rgb("#e0f2fe"),
  let survey-stroke = rgb("#0284c7"),
  let expand-fill = rgb("#f3e8ff"),
  let expand-stroke = rgb("#7c3aed"),
  let crystal-fill = rgb("#dcfce7"),
  let crystal-stroke = rgb("#16a34a"),
  let stress-fill = rgb("#fee2e2"),
  let stress-stroke = rgb("#dc2626"),
  let refine-fill = rgb("#e0f2fe"),
  let refine-stroke = rgb("#0284c7"),
  let decision-fill = rgb("#fef9c3"),
  let decision-stroke = rgb("#a16207"),
  let arrow = rgb("#4a5568"),
  let loop-color = rgb("#0284c7"),
  let pivot-color = rgb("#dc2626"),

  // Entry
  node((0, 0), text(fill: navy, size: 9pt)[*User states*\ *idea*],
    fill: entry-fill, stroke: 1.5pt + entry-stroke, shape: "circle", inset: 8pt, name: <idea>),

  node((1, 0), align(center, text(fill: navy, size: 9pt)[*Clarify*\ multiple choice Q]),
    fill: entry-fill, stroke: 1.5pt + entry-stroke, corner-radius: 5pt, inset: 8pt, name: <clarify>),

  // Phase 1
  node((2, 0), align(center, text(fill: navy, size: 9pt)[*Phase 1: Survey*\ landscape, problems,\ bottlenecks]),
    fill: survey-fill, stroke: 1.5pt + survey-stroke, corner-radius: 5pt, inset: 8pt, name: <survey>),

  // Phase 2
  node((2, 1), align(center, text(fill: navy, size: 9pt)[*Phase 2: Expand*\ 4 parallel subagents]),
    fill: expand-fill, stroke: 1.5pt + expand-stroke, corner-radius: 5pt, inset: 8pt, name: <expand>),

  // Subagent labels
  node((0.3, 1), box(width: 110pt,
    align(left, text(fill: expand-stroke, size: 7pt)[
      #sym.bullet Adjacent subfield\
      #sym.bullet Cross-vocabulary\
      #sym.bullet Cross-method\
      #sym.bullet Historical
    ])),
    stroke: 0.8pt + expand-stroke, fill: rgb("#faf5ff"), corner-radius: 4pt, inset: 6pt, name: <agents>),

  // Go deeper decision
  node((2, 2), text(fill: navy, size: 9pt)[*Go deeper?*],
    fill: decision-fill, stroke: 1.5pt + decision-stroke, shape: fletcher.shapes.diamond, inset: 10pt, name: <deeper>),

  // Phase 3
  node((2, 3), align(center, text(fill: navy, size: 9pt)[*Phase 3: Crystallize*\ Socratic + Polya]),
    fill: crystal-fill, stroke: 1.5pt + crystal-stroke, corner-radius: 5pt, inset: 8pt, name: <crystal>),

  // Phase 4
  node((2, 4), align(center, text(fill: navy, size: 9pt)[*Phase 4: Stress-test*\ novelty, rigor, impact]),
    fill: stress-fill, stroke: 1.5pt + stress-stroke, corner-radius: 5pt, inset: 8pt, name: <stress>),

  // Survives decision
  node((2, 5), text(fill: navy, size: 9pt)[*Survives?*],
    fill: decision-fill, stroke: 1.5pt + decision-stroke, shape: fletcher.shapes.diamond, inset: 10pt, name: <survives>),

  // Phase 5
  node((2, 6), align(center, text(fill: navy, size: 9pt)[*Phase 5: Refine*\ direction document]),
    fill: refine-fill, stroke: 1.5pt + refine-stroke, corner-radius: 5pt, inset: 8pt, name: <refine>),

  // Output
  node((2, 7.2), text(fill: navy, size: 9pt)[*Research*\ *Direction Doc*],
    fill: entry-fill, stroke: 1.5pt + entry-stroke, shape: "circle", inset: 8pt, name: <doc>),

  // Forward edges
  edge(<idea>, <clarify>, "-|>", stroke: 1.5pt + arrow),
  edge(<clarify>, <survey>, "-|>", stroke: 1.5pt + arrow),
  edge(<survey>, <expand>, "-|>", stroke: 1.5pt + arrow),
  edge(<expand>, <deeper>, "-|>", stroke: 1.5pt + arrow),
  edge(<deeper>, <crystal>, "-|>", stroke: 1.5pt + arrow,
    label: text(fill: navy, size: 8pt)[ready], label-side: right),
  edge(<crystal>, <stress>, "-|>", stroke: 1.5pt + arrow),
  edge(<stress>, <survives>, "-|>", stroke: 1.5pt + arrow),
  edge(<survives>, <refine>, "-|>", stroke: 1.5pt + arrow,
    label: text(fill: crystal-stroke, size: 8pt)[yes], label-side: right),
  edge(<refine>, <doc>, "-|>", stroke: 1.5pt + arrow),

  // Subagent connection
  edge(<agents>, <expand>, "-|>", stroke: 1pt + expand-stroke),

  // Loop: go deeper -> survey
  edge(<deeper>, <survey>, "-|>", bend: 40deg,
    stroke: (paint: loop-color, thickness: 1.2pt, dash: "dashed"),
    label: text(fill: loop-color, size: 8pt, weight: "medium")[deeper], label-side: center),

  // Loop: survives no -> crystal (pivot)
  edge(<survives>, <crystal>, "-|>", bend: 40deg,
    stroke: (paint: pivot-color, thickness: 1.2pt, dash: "dashed"),
    label: text(fill: pivot-color, size: 8pt, weight: "medium")[pivot], label-side: center),
)
