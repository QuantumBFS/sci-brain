#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge
#set page(width: auto, height: auto, margin: (top: 8pt, bottom: 8pt, left: 8pt, right: 8pt))

#diagram(
  node-stroke: 0.8pt,
  edge-stroke: 1pt,
  spacing: (16mm, 14mm),
  mark-scale: 60%,

  let s = 11pt,
  let sm = 9.5pt,
  let survey-fill = rgb("#e0f2fe"),
  let survey-stroke = rgb("#0284c7"),
  let ideas-fill = rgb("#f3e8ff"),
  let ideas-stroke = rgb("#7c3aed"),
  let review-fill = rgb("#fef3c7"),
  let review-stroke = rgb("#d97706"),

  // --- Nodes ---

  node((0, 0), text(size: s)[*Topic*],
    fill: white, stroke: 1pt + black, corner-radius: 4pt, inset: 6pt, name: <topic>),

  node((1, 0), box(width: 110pt, align(center, text(size: s)[*Survey*\ #text(size: sm)[parallel search strategies]])),
    fill: survey-fill, stroke: 1pt + survey-stroke, corner-radius: 4pt, inset: 6pt, name: <survey>),

  node((2, 0), box(width: 110pt, align(center, text(size: s)[*Brainstorm*\ #text(size: sm)[propose, question, refine]])),
    fill: ideas-fill, stroke: 1pt + ideas-stroke, corner-radius: 4pt, inset: 6pt, name: <ideas>),

  node((3, 0), box(width: 110pt, align(center, text(size: s)[*Review*\ #text(size: sm)[critique, kill or rank]])),
    fill: review-fill, stroke: 1pt + review-stroke, corner-radius: 4pt, inset: 6pt, name: <review>),

  node((4, 0), text(size: s)[*Report*],
    fill: white, stroke: 1pt + black, corner-radius: 4pt, inset: 6pt, name: <report>),

  // --- Edges ---

  edge(<topic>, <survey>, "-|>"),
  edge(<survey>, <ideas>, "-|>"),
  edge(<ideas>, <review>, "-|>"),
  edge(<review>, <report>, "-|>"),

  // Loop: brainstorm self-loop
  edge(<ideas>, <ideas>, "-|>", bend: -130deg,
    stroke: (paint: ideas-stroke, thickness: 1pt, dash: "dashed"),
    label: text(fill: ideas-stroke, size: sm)[user steers], label-side: right),

  // Loop: dive into papers (review → brainstorm)
  edge(<review>, <ideas>, "-|>", bend: -40deg,
    stroke: (paint: review-stroke, thickness: 1pt, dash: "dashed"),
    label: text(fill: review-stroke, size: sm)[dive into papers], label-side: right),
)
