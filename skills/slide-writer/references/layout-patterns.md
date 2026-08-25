# Layout Patterns — slide-writer zoo

How to compose a slide from the zoo. Pick the layout/gadget that fits the slide's
job, copy the snippet, fill in content. All snippets assume the deck preamble
below — the single import plus the two destructures that bind the active theme's
palette to every gadget and layout.

## Deck preamble (copy once per deck)

```typst
#import "zoo/lib.typ": *

// 1. pick a theme
#let pal = palettes.academic
#show: themes.academic.with(config-info(
  title: [Deck Title], subtitle: [one-line],
  author: [Your Name], date: datetime.today(), institution: [Org],
))

// 2. bind gadgets + layouts to that palette (names are stable across themes)
#let (rail_pull, callout, codebox, quote_pull, figbox, portrait, clip_image,
      stat, stat_row, spec_list, theorem, definition, lemma, example, proof_box,
      badge, tag, time_badge, data_table, conclusion_grid, key_links, toc,
      pacing, kicker, progress_dots) = gadgets(pal)
#let (spread, twocol, threecol, hero, band, cards, card, punch,
      centered_figure) = layouts(pal)

#title-slide()

== Outline
#toc()
```

To switch theme, change `palettes.academic` → `palettes.dark` and
`themes.academic` → `themes.dark` in three places. Nothing else moves.

---

## Router — match the slide's job to a pattern

| The slide does this | Use |
|---|---|
| Opens the deck | `#title-slide()` |
| Shows the table of contents | `== Outline` + `#toc()` (`#outline()` is a dotted paper TOC — wrong register) |
| Punches one sentence between sections | `#focus-slide[...]` |
| Reveals a slide stepwise | `#pause` between blocks (each step = one PDF page) |
| One figure + commentary (the default talk slide) | `spread` + `figbox` |
| Side-by-side compare/contrast | `twocol` |
| Three parallel concepts | `threecol` |
| One headline quantity-statement or slogan | `hero` + `punch` |
| Headlines 3–4 quantity-statements | `stat_row` |
| Names 3–4 parallel items (principles, failures) | `spec_list` |
| Compares before/after across rows | `data_table` |
| Carries a one-line slogan | `rail_pull` |
| Sidebar remark / single big number panel | `callout` |
| States a result, definition, lemma | `theorem` / `definition` / `lemma` |
| Shows code | `codebox` |
| Closes with audience-shaped takeaways | `conclusion_grid` (4 cards) |
| Closing links | `key_links` |
| Tensor / network diagram | CeTZ `tensor` + `edge` |
| Finite-automaton / flowchart | CeTZ `automaton-state` / `flowbox` |
| Annotates a figure or phrase in place | pinit `pin` + `highlight` + `note` |

Combine at most two patterns per slide; past that the eye loses its anchor.

---

## Pattern: figure + commentary (`spread` + `figbox`)

The default talk slide. Wide figure left, narrow commentary right.

```typst
== The system breaks in three _places_
#spread(
  figbox([Fig 1 · Overview], image("figures/system.pdf", width: 100%),
         caption: [how to read it]),
  [Lead sentence. #rail_pull[Key insight in one line.]],
)
```

- The figure is the evidence; the rail carries the claim. Don't recap the figure
  in the rail.
- Swap `image(...)` for a `rect(…)[…]` placeholder while drafting.
- Change the ratio with `spread(fig, rail, ratio: (1fr, 1fr))` for equal columns.

## Pattern: side-by-side (`twocol` / `threecol`)

```typst
== Before vs. after
#twocol(
  [#kicker[before] The old approach has three failure modes.],
  [#kicker[after]  The new approach collapses them into one.],
)
```

## Pattern: headline numbers (`stat_row`)

```typst
== Adoption at a glance
#stat_row(
  // Keep the unit inside the highlight ("13 weeks" is a quantity, a bare
  // highlighted "13" says nothing); the label states what the number means.
  (value: [13], unit: [weeks], label: [to full adoption]),
  (value: [56%], label: [daily use]),  // plain values — the gadget bolds and
  (value: [3], label: [modules]),      // colours them; [*13*] would be
)                                      // repainted primary by touying's alert
```

## Pattern: numbered parallel items (`spec_list`)

```typst
#spec_list(
  (term: [Failure A], desc: [latency collapses], tag: [cost]),
  (term: [Failure B], desc: [error rate climbs], tag: [scale]),
)
```

## Pattern: before/after table (`data_table`)

First positional row is the header; `highlight:` is the set of body-row indices
to emphasise in the accent colour. The first column is the row label (sans,
left-aligned); value columns render in mono automatically.

```typst
#data_table(
  ("Metric", "Before", "After"),
  ("Latency", "340 ms", "52 ms"),
  ("Error rate", "12%", "1.3%"),
  highlight: (0,),
)
```

## Pattern: theory boxes

```typst
#theorem(title: [Main result], [Let $H = sum_i X_i$. Then the gap closes.])
#definition(title: [Gap], [The gap is $Delta = E_1 - E_0$.])
#example([For $N=20$, $Delta/Gamma approx 0.3$.])
#proof_box([Expand the sum and group terms. #h(8pt)$square$])
```

## Pattern: one punch (`hero` + `punch`)

One centred statement with the quantity emphasised inline (add `unit: [weeks]`
for unitful values so the emphasis reads "13 weeks", never a bare "13"):

```typst
#hero[#punch(56%, [of users adopt it daily], label: [survey, n=128])]
```

## Pattern: closing grid (`conclusion_grid`)

Always four cards; the last is dark and carries the call to action.

```typst
#conclusion_grid(
  (label: "Approach", title: [The method], body: [one sentence.]),
  (label: "Result",   title: [The outcome], body: [one sentence.]),
  (label: "Impact",   title: [Why it matters], body: [one sentence.]),
  (label: "Next",     title: [project URL], body: [the call to action.]),
)
```

## Pattern: outline, focus, and pause

```typst
== Outline
#toc()                    // level-1 sections, numbered; toc(columns: 2) for long decks

#focus-slide[One sentence that must land.]   // full-bleed, between sections

== Reveal stepwise
First the claim.
#pause
Then the evidence.       // each #pause step becomes one more PDF page
```

## Pattern: CeTZ diagrams (optional)

Node radii are in canvas units, so size follows `length`; keep nodes ≥ 2.5
units apart. Edges are undirected by default — pass `mark: (end: "straight")`
for arrows, and connect flowboxes via side anchors so lines stop at borders.

```typst
#import "zoo/gadgets_cetz.typ": make as make-cetz
#import "@preview/cetz:0.4.2": canvas
#let (tensor, automaton-state, edge, flowbox) = make-cetz(pal)

#canvas(length: 1cm, {
  import "@preview/cetz:0.4.2": draw
  tensor((0, 0), "A", [$A$])
  tensor((2.2, 1.1), "B", [$B$])
  edge("A", "B")                                  // undirected tensor leg
  flowbox((0, -2.5), "in", [input])
  flowbox((4, -2.5), "proc", [process])
  edge("in.east", "proc.west", mark: (end: "straight"))
})
```

## Pattern: pin annotations (optional)

```typst
#import "zoo/gadgets_pin.typ": make as make-pin
#let (pin, highlight, note) = make-pin(pal)

A #pin(1)key phrase#pin(2) in the prose.
#highlight(1, 2)
#note(2)[This is where the claim lives.]
```

---

## House rules

- **One figure per slide.** A second figure means you have conflated two slides.
- **One accent colour for emphasis.** Numbers and `rail_pull` use `accent_deep`;
  don't repaint gadgets by hand.
- **Tabular numbers in mono.** `data_table` value columns and `time_badge` do it
  themselves; emphasised quantities (`stat`, `punch`) stay in the theme sans.
- **A number is emphasised as a statement, not a dashboard numeral.** `stat`,
  `stat_row`, and `punch` set the full quantity ("13 weeks", via `unit:`) in
  bold accent at the same scale as its meaning — never a giant bare "13" over
  a small caption.
- **Three text sizes, deck-wide** (`sizes` from `zoo/scale.typ`, exported by
  `zoo/lib.typ`): `xlarge` 30 pt (the one hero statement; also title, section,
  and focus slides), `large` 24 pt
  (emphasised statements/slogans), `normal` 20 pt (everything else). Hierarchy
  comes from weight, colour, and case — never from smaller type. If content
  only fits smaller, split the slide.
- **Pass plain values** (`[13]`, not `[*13*]`) — touying repaints `strong` in
  theme primary; gadgets bold and colour their own numerals.
- **Captions describe how to *read* the figure**, not what it is.
- **Pick the theme up front.** Theme-hopping mid-deck reads as inconsistent.
- **Recompile the gallery** (`typst compile gallery.typ`) whenever you add a
  gadget or layout — it is the visual regression test for the zoo.
