// slide-writer zoo — gallery
// ===========================
// A browsable visual index of every theme, layout, and gadget in the zoo.
// Compile it to see the whole catalogue rendered:
//
//   typst compile gallery.typ                         # default = academic theme
//   typst compile --input theme=dark   gallery.typ    # preview the dark theme
//   typst compile --input theme=minimal gallery.typ
//
// The "Color themes" section renders all five palettes as swatch cards, so a
// single compile shows every palette. The surrounding chrome (header, footer,
// progress bar, section pages) reflects whichever theme `theme` selects.

#import "zoo/lib.typ": *

#let theme-name = sys.inputs.at("theme", default: "academic")
#let pal = palettes.at(theme-name)

// Active-theme gadgets/layouts, destructured for ergonomic calls below.
#let (rail_pull, callout, codebox, quote_pull, figbox, portrait, clip_image,
      stat, stat_row, spec_list, theorem, definition, lemma, example, proof_box,
      badge, tag, time_badge, data_table, conclusion_grid, key_links, pacing,
      kicker, progress_dots) = gadgets(pal)
#let (spread, twocol, threecol, hero, band, cards, card, punch, centered_figure) = layouts(pal)

// Swatch helpers (work with any palette, not just the active one).
#let chip = (c, label) => block(width: 100%, inset: (x: 4pt, y: 4pt))[
  #block(width: 100%, height: 30pt, fill: c, radius: 2pt, stroke: 0.5pt + pal.hairline)[]
  #text(6pt, fill: pal.text_soft)[#label]
]
#let chip-row = (p) => grid(
  columns: (1fr,) * 6, column-gutter: 5pt,
  ..((("primary", p.primary), ("accent", p.accent), ("accent_deep", p.accent_deep),
      ("ink", p.ink), ("text_soft", p.text_soft), ("hairline", p.hairline))
    .map(((l, c)) => chip(c, l))),
)
#let palette-sample = (p) => {
  let g = gadgets(p)
  grid(columns: 1, row-gutter: 8pt)[
    #(g.stat_row)(
      (value: [*13*], label: [weeks]),
      (value: [*56%*], label: [daily use]),
      (value: [*3*], label: [modules]),
    )
  ][
    #(g.rail_pull)[The model is the coupling, not the artifact.]
  ]
}

#show: themes.at(theme-name).with(
  config-info(
    title: [slide-writer · the zoo],
    subtitle: [themes · layouts · gadgets],
    author: [sci-brain skill],
    date: datetime.today(),
    institution: [compile with --input theme=<name> to retheme],
  ),
)

#title-slide()

== Outline
#outline()

= Color themes

== academic
#chip-row(palettes.academic)
#v(8pt)
#palette-sample(palettes.academic)
Restrained navy on white — the conference-talk default.

== dark
#chip-row(palettes.dark)
#v(8pt)
#palette-sample(palettes.dark)
Light text on deep slate — for dim rooms and glare-fatiguing projectors.

== minimal
#chip-row(palettes.minimal)
#v(8pt)
#palette-sample(palettes.minimal)
Black ink on white, single grey rule — the handout / lecture-note deck.

== vibrant
#chip-row(palettes.vibrant)
#v(8pt)
#palette-sample(palettes.vibrant)
Saturated teal + magenta — for teaching and outreach where energy beats gravitas.

== brand
#chip-row(palettes.brand)
#v(8pt)
#palette-sample(palettes.brand)
Derived from a single house colour via `palettes/brand.typ`'s `build(primary)`.

= Layouts

== spread — figure + commentary
#spread(
  figbox([Fig · overview], rect(width: 100%, height: 120pt, fill: pal.paper_bg, stroke: pal.hairline)[your figure], caption: [how to read it]),
  [Lead sentence. The default 2fr/1fr ratio makes the figure primary.],
)

== twocol — side by side
#twocol(
  [#kicker[before] #v(4pt) The old approach has three failure modes.],
  [#kicker[after] #v(4pt) The new approach collapses them into one.],
)

== threecol — three parallel ideas
#threecol(
  [#badge([one]) #v(4pt) idea A],
  [#badge([two]) #v(4pt) idea B],
  [#badge([three]) #v(4pt) idea C],
)

== hero — one punch
#hero[#punch(56%, [of users adopt it daily], label: [survey, n=128])]

== band + cards
#band(badge([A]), badge([long B]), badge([C]), gutter: 8pt)
#v(8pt)
#cards([Card one: a short claim.], [Card two: a short claim.], cols: 2)

== centered figure
#centered_figure(rect(width: 60%, height: 100pt, fill: pal.paper_bg, stroke: pal.hairline)[figure], caption: [a captioned figure with no commentary rail])

= Callout gadgets

== pull-quotes and callouts
#quote_pull([The cheapest way to credit prior work is a reference.], source: [von Delft])
#v(6pt)
#rail_pull[The model is not the artifact — it is the coupling.]
#v(8pt)
#grid(columns: (1fr, 1fr), column-gutter: 10pt, row-gutter: 10pt,
  callout([Note], [A neutral remark tied to the accent colour.]),
  callout([Tip], [A success-coloured note.], kind: "success"),
  callout([Watch], [A warning in the warning colour.], kind: "warning"),
  callout([Danger], [A red-flagged caveat.], kind: "danger"),
)

== codebox
#codebox[`#let f(x) = x + 1`]

= Stats and structure

== stat row + spec list
#stat_row((value: [*13*], label: [weeks]), (value: [*56%*], label: [daily]), (value: [*3*], label: [parts]))
#v(10pt)
#spec_list(
  (term: [Failure A], desc: [latency collapses], tag: [cost]),
  (term: [Failure B], desc: [error rate climbs], tag: [scale]),
  (term: [Failure C], desc: [recurs weekly], tag: [ops]),
)

== data table
#data_table(
  ("Metric", "Before", "After"),
  ("Latency", "340 ms", "52 ms"),
  ("Error rate", "12%", "1.3%"),
  highlight: (0,),
)

== conclusion grid
#conclusion_grid(
  (label: "Approach", title: [The method], body: [one sentence.]),
  (label: "Result", title: [The outcome], body: [one sentence.]),
  (label: "Impact", title: [Why it matters], body: [one sentence.]),
  (label: "Next", title: [project URL], body: [the call to action.]),
)

= Theory boxes

== theorem / definition / example
#theorem(title: [Main result], [Let $H = sum_i X_i$. Then the spectral gap closes.])
#v(4pt)
#definition(title: [Gap], [The gap is $Delta = E_1 - E_0$, dimensionless.])
#v(4pt)
#example([For a 20-site chain, $Delta / Gamma approx 0.3$ at the transition.])

== lemma and proof
#lemma([A useful intermediate statement.])
#v(4pt)
#proof_box([The argument follows by expanding the sum and grouping terms. #h(8pt)$square$])

= Diagrams (CeTZ)

#import "zoo/gadgets_cetz.typ": make as make-cetz
#let (tensor, automaton-state, edge, flowbox) = make-cetz(pal)
#import "@preview/cetz:0.4.2": canvas

== tensor network
#centered_figure(canvas(length: 0.6cm, {
  import "@preview/cetz:0.4.2": draw
  tensor((0, 0), "A", [$A$])
  tensor((2.4, 0.6), "B", [$B$])
  tensor((2.4, -0.6), "C", [$C$])
  tensor((4.8, 0), "D", [$D$])
  edge("A", "B"); edge("A", "C"); edge("B", "D"); edge("C", "D")
}))

== automaton + flowchart
#twocol(
  canvas(length: 0.7cm, {
    import "@preview/cetz:0.4.2": draw
    automaton-state((0, 0), "s0", [$q_0$])
    automaton-state((3, 0), "s1", [$q_1$], accept: true)
    edge("s0", "s1", mark: (end: ">"))
  }),
  canvas(length: 0.6cm, {
    import "@preview/cetz:0.4.2": draw
    flowbox((0, 0), "in", [input])
    flowbox((3, 0), "proc", [process])
    edge("in", "proc", mark: (end: ">"))
  }),
)

= Pin annotations (pinit)

#import "zoo/gadgets_pin.typ": make as make-pin
#let (pin, highlight, note) = make-pin(pal)

== pinning notes onto text
A #pin(1)key phrase#pin(2) in the prose, annotated after the fact.

#highlight(1, 2)
#note(2)[This is where the claim lives.]

= Closing

==
#hero[
  #text(18pt, fill: pal.text_soft)[Recompile with ]
  #badge([--input theme=dark])
  #text(18pt, fill: pal.text_soft)[ to preview any theme.]
]
