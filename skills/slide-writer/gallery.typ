// slide-writer zoo — gallery
// ===========================
// A browsable visual index of every theme, layout, and gadget in the zoo.
// Compile it to see the whole catalogue rendered:
//
//   typst compile gallery.typ                         # default = academic theme
//   typst compile --input theme=dark   gallery.typ    # preview the dark theme
//   typst compile --input theme=minimal gallery.typ
//
// The "Color themes" section renders all five palettes as swatch cards (each
// sample sits on its own palette's paper, so dark palettes stay readable in a
// light gallery and vice versa). The surrounding chrome (header, footer,
// progress bar, section pages) reflects whichever theme `theme` selects.

#import "zoo/lib.typ": *

#let theme-name = sys.inputs.at("theme", default: "academic")
#let pal = palettes.at(theme-name)

// Active-theme gadgets/layouts, destructured for ergonomic calls below.
#let (rail_pull, callout, codebox, quote_pull, figbox, portrait, clip_image,
      stat, stat_row, spec_list, theorem, definition, lemma, example, proof_box,
      badge, tag, time_badge, data_table, conclusion_grid, key_links, toc,
      pacing, kicker, progress_dots) = gadgets(pal)
#let (spread, twocol, threecol, hero, band, cards, card, punch, centered_figure) = layouts(pal)

// Swatch helpers (work with any palette, not just the active one).
#let chip = (c, label) => block(width: 100%, inset: (x: 4pt, y: 4pt))[
  #block(width: 100%, height: 26pt, fill: c, radius: 2pt, stroke: 0.5pt + pal.hairline)
  #text(sizes.normal, fill: pal.text_soft)[#label]
  #linebreak()
  #text(sizes.normal, font: ("DejaVu Sans Mono", "Noto Sans Mono"), fill: pal.text_soft)[#c.to-hex()]
]
#let chip-row = (p) => grid(
  columns: (1fr,) * 6, column-gutter: 5pt,
  ..((("primary", p.primary), ("accent", p.accent), ("accent_deep", p.accent_deep),
      ("ink", p.ink), ("text_soft", p.text_soft), ("hairline", p.hairline))
    .map(((l, c)) => chip(c, l))),
)
// Render each palette's sample ON ITS OWN PAPER — a dark palette's light ink
// would vanish on the light gallery page (and vice versa).
#let palette-sample = (p) => {
  let g = gadgets(p)
  block(width: 100%, fill: p.paper, stroke: 0.5pt + p.hairline, radius: 4pt,
    inset: (x: 14pt, y: 10pt))[
    #(g.stat_row)(
      (value: [13], unit: [weeks], label: [to full adoption]),
      (value: [56%], label: [daily use]),
      (value: [3], label: [modules]),
    )
    #v(6pt)
    #(g.rail_pull)[The model is the coupling, not the artifact.]
  ]
}
// Placeholder “photo” for the portrait/clip demos (the zoo ships no images).
#let head-shot = (c1, c2, w: 48pt, h: 48pt) => rect(
  width: w, height: h, fill: gradient.linear(c1, c2, angle: 45deg))

#show: themes.at(theme-name).with(
  config-info(
    title: [slide-writer · the zoo],
    subtitle: [themes · layouts · gadgets],
    author: [sci-brain skill],
    date: datetime.today(),
    institution: [compile with #raw("--input theme=<name>") to retheme],
  ),
)

#title-slide()

== Outline
#toc(columns: 2)

= Color themes

== academic
#chip-row(palettes.academic)
#v(6pt)
#palette-sample(palettes.academic)
Restrained navy on white — the conference-talk default.

== dark
#chip-row(palettes.dark)
#v(6pt)
#palette-sample(palettes.dark)
Light text on deep slate — for dim rooms and glare-fatiguing projectors.

== minimal
#chip-row(palettes.minimal)
#v(6pt)
#palette-sample(palettes.minimal)
Black ink on white, single grey rule — the handout / lecture-note deck.

== vibrant
#chip-row(palettes.vibrant)
#v(6pt)
#palette-sample(palettes.vibrant)
Saturated teal + magenta — for teaching and outreach where energy beats gravitas.

== brand
#chip-row(palettes.brand)
#v(6pt)
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
#hero[#punch([56%], [of users adopt it daily], label: [survey, n=128])]

== band + cards
#band(align(center, badge([A])), align(center, badge([long B])), align(center, badge([C])), gutter: 8pt)
#v(10pt)
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
  callout([Key], [The deep-accent remark for the claim that matters.], kind: "accent"),
)

== codebox
#codebox[#raw(lang: "typst", "#let pal = palettes.dark\n#show: themes.dark.with(config-info(title: [Deck]))\n#let G = gadgets(pal)")]

= Stats and structure

== stat row + spec list
#stat_row((value: [13], unit: [weeks], label: [to full adoption]), (value: [56%], label: [daily use]), (value: [3], label: [modules]))
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
#example([For a 20-site chain, $Delta \/ Gamma approx 0.3$ at the transition.])

== lemma and proof
#lemma([A useful intermediate statement.])
#v(4pt)
#proof_box([The argument follows by expanding the sum and grouping terms. #h(8pt)$square$])

= Chrome, badges, portraits

== badges and pacing
#pacing(2)
#twocol(
  [
    #kicker[kicker · an eyebrow label] \
    #v(6pt)
    #badge([badge]) #h(6pt) #badge([success], fill: pal.success) #h(6pt)
    #tag([tag]) #h(6pt) #time_badge([12:00])
    #v(10pt)
    #key_links(
      ("code", [github.com/you/project]),
      ("paper", [arxiv.org/abs/2401.00000]),
    )
  ],
  [
    #stat([56%], [a single stat, centred])
    #v(8pt)
    #align(center)[#progress_dots(6, 2)]
    #v(4pt)
    #align(center)[#text(sizes.normal, fill: pal.text_soft)[progress_dots(6, 2) — and `pacing(2)` printed “2 min” top-right]]
  ],
)

== portraits and clipping
#band(
  align(center, portrait(head-shot(pal.accent, pal.primary), [A. Author])),
  align(center, portrait(head-shot(pal.primary, pal.accent_deep), [B. Builder])),
  align(center, portrait(head-shot(pal.accent_deep, pal.accent), [C. Curator])),
)
#v(10pt)
#centered_figure(
  clip_image(head-shot(pal.accent, pal.primary, w: 200pt, h: 90pt), top: 20pt, bottom: 20pt),
  caption: [clip_image trims 20pt off the top and bottom of a taller original (both accept an image path or ready content)],
)

= Touying moves

== reveal steps with pause
First, the claim.
#pause

Then the evidence — this line lands on the second step.
#pause

#rail_pull[The takeaway appears last; every step is one more page in the PDF.]

#focus-slide[One sentence that must land.]

= Diagrams (CeTZ)

#import "zoo/gadgets_cetz.typ": make as make-cetz
#let (tensor, automaton-state, edge, flowbox) = make-cetz(pal)
#import "@preview/cetz:0.4.2": canvas

== tensor network
#centered_figure(
  canvas(length: 0.9cm, {
    import "@preview/cetz:0.4.2": draw
    tensor((0, 0), "A", [$A$])
    tensor((2.2, 1.1), "B", [$B$])
    tensor((2.2, -1.1), "C", [$C$])
    tensor((4.4, 0), "D", [$D$])
    edge("A", "B"); edge("A", "C"); edge("B", "D"); edge("C", "D")
  }),
  caption: [tensor + edge — undirected legs by default],
)

== automaton + flowchart
#twocol(
  align(center, canvas(length: 0.9cm, {
    import "@preview/cetz:0.4.2": draw
    automaton-state((0, 0), "s0", [$q_0$])
    automaton-state((3, 0), "s1", [$q_1$], accept: true)
    edge("s0", "s1", mark: (end: "straight"))
  })),
  align(center, canvas(length: 0.9cm, {
    import "@preview/cetz:0.4.2": draw
    flowbox((0, 0), "in", [input])
    flowbox((4, 0), "proc", [process])
    edge("in.east", "proc.west", mark: (end: "straight"))
  })),
)

= Pin annotations (pinit)

#import "zoo/gadgets_pin.typ": make as make-pin
#let (pin, highlight, note) = make-pin(pal)

== pinning notes onto text
A #pin(1)key phrase#pin(2) in the prose, annotated after the fact.

#highlight(1, 2)
#note(2)[This is where the claim lives.]

= Closing

== browse and retheme
#hero[
  #text(sizes.normal, fill: pal.text_soft)[One compile per theme — chrome, gadgets, and diagrams all repaint.]
  #v(10pt)
  #codebox[#raw("typst compile --input theme=dark gallery.typ")]
  #v(12pt)
  #align(left)[#key_links(
    ("zoo", [skills/slide-writer/zoo/ — palettes, themes, gadgets, layouts]),
    ("router", [references/layout-patterns.md — which pattern for which slide]),
    ("tokens", [references/style-tokens.md — the palette vocabulary]),
  )]
]
