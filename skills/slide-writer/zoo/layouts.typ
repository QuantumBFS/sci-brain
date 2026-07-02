// slide-writer zoo — layouts
// ============================
// Slide-body composers: where content goes on one slide. Each takes ready-made
// content (often gadgets from G) and arranges it within a touying slide body.
// A `== Heading` is still what creates the slide; these lay out its body.
//
//   #import "zoo/layouts.typ": make
//   #let L = make(palette)
//   == Some slide
//   #L.spread(G.figbox(...), [commentary])

#let make(pal) = {
  let card = (body) => block(
    width: 100%, inset: 12pt, radius: 3pt,
    fill: pal.paper_bg, stroke: 0.5pt + pal.hairline,
  )[#body]

  return (
    // Figure (wide) + commentary (narrow). The default talk slide.
    "spread": (fig, text, ratio: (2fr, 1fr)) => grid(
      columns: ratio, column-gutter: 24pt, align: top,
      fig, text,
    ),

    // Equal two-column split for side-by-side compare/contrast.
    "twocol": (left, right, gutter: 20pt) => grid(
      columns: (1fr, 1fr), column-gutter: gutter, align: top, left, right,
    ),

    // Three equal columns (three parallel concepts, three case studies).
    "threecol": (a, b, c, gutter: 16pt) => grid(
      columns: (1fr, 1fr, 1fr), column-gutter: gutter, align: top, a, b, c,
    ),

    // Centred single punch line / equation / figure. For the slide that carries one idea.
    "hero": (body) => align(center + horizon)[
      #block(width: 80%, inset: (x: 8pt))[#align(center)[#body]]
    ],

    // Horizontal band of equal items (badges, portraits, mini-cards).
    "band": (..items, gutter: 14pt) => grid(
      columns: (1fr,) * items.pos().len(), column-gutter: gutter, align: top,
      ..items.pos(),
    ),

    // Grid of N cards (cell content becomes a bordered card each).
    "cards": (..items, cols: 2, gutter: 8pt) => grid(
      columns: (1fr,) * cols, column-gutter: gutter, row-gutter: gutter, align: top,
      ..items.pos().map(card),
    ),

    // A bordered card around any content.
    "card": card,

    // Big number (left) + sentence (right). For headline-stat slides.
    "punch": (number, desc, label: none) => grid(
      columns: (auto, 1fr), column-gutter: 20pt, align: horizon,
      align(center)[
        #text(40pt, weight: "bold", fill: pal.accent_deep)[#number]
        #if label != none [#linebreak() #text(9pt, fill: pal.text_soft)[#label]]
      ],
      text(13pt, fill: pal.text)[#desc],
    ),

    // Captioned figure centred on its own (no commentary rail).
    "centered_figure": (body, caption: none) => align(center)[
      #body
      #if caption != none [#v(6pt) #text(9pt, fill: pal.text_soft, style: "italic")[#caption]]
    ],
  )
}
