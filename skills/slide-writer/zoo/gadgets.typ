// slide-writer zoo — gadgets
// ============================
// Pure-Typst content components (no CeTZ/pinit dependency). Every gadget is
// palette-aware: call `make(palette)` once and get back a dict `G` of functions
// that already know the active theme's colours.
//
//   #import "zoo/gadgets.typ": make
//   #let G = make(palette)
//   #G.rail_pull[The key insight in one sentence.]
//
// Keys are snake_case so they work as Typst field selectors: `G.stat_row(...)`.
//
// Two invariants keep gadgets legible under EVERY palette (incl. dark):
//   1. Soft fills are never `c.lighten(...)` (that walks toward white and
//      produces white-on-white under the dark theme). They mix the accent
//      into `pal.paper` instead — `_tint` below.
//   2. Gadgets bold via `text(weight: "bold")`, never `*...*` markup: touying
//      show-rules `strong` as an alert and would repaint it in theme primary.

// Running pacing counter, shared across all gadget dicts in this document.
#let _clock = state("slide-writer-clock", 0)

// Soft fill: mix `k` of colour `c` into the palette's paper. Works on light
// and dark grounds alike (a lighten() would not).
#let _tint(pal, c, k) = color.mix((c, k), (pal.paper, 100% - k))

// Theory-box factory shared by theorem / definition / lemma / example / proof_box.
#let _thm(label, border, pal) = (title: none, body) => block(
  width: 100%, radius: 3pt, inset: (x: 12pt, y: 9pt),
  stroke: (left: 3pt + border), fill: _tint(pal, border, 10%),
)[
  #text(11pt, weight: "bold", fill: border)[#upper(label)#if title != none [ · #title]]
  #v(3pt)
  #text(13pt, fill: pal.text)[#body]
]

#let make(pal) = {
  let tint = _tint.with(pal)
  let mono = ("DejaVu Sans Mono", "Noto Sans Mono", "Noto Mono")
  let on-primary = pal.at("on_primary", default: rgb("#ffffff"))

  let kind-color = (
    info: pal.accent,
    success: pal.success,
    warning: pal.warning,
    danger: pal.warning.darken(18%),
    accent: pal.accent_deep,
  )

  return (
    // ── Callouts ──────────────────────────────────────────────
    "rail_pull": (body) => block(
      width: 100%, inset: (left: 12pt, y: 6pt),
      stroke: (left: 3pt + pal.accent),
    )[#text(17pt, style: "italic", fill: pal.ink)[#body]],

    "callout": (label, body, kind: "info") => {
      let c = kind-color.at(kind, default: pal.accent)
      block(width: 100%, radius: 3pt, inset: 10pt,
        stroke: (left: 3pt + c), fill: tint(c, 12%))[
        // Label pulls toward ink so pale accents stay legible at small sizes.
        #text(11pt, weight: "bold", fill: color.mix((c, 65%), (pal.ink, 35%)))[#upper(label)]
        #v(2pt)
        #text(13pt, fill: pal.text)[#body]
      ]
    },

    "codebox": (body, size: 14pt) => block(
      width: 100%, radius: 4pt, inset: 12pt,
      fill: tint(pal.primary, 7%),
      stroke: 0.5pt + pal.hairline,
    )[#text(font: mono, size: size, fill: pal.text)[#body]],

    "quote_pull": (body, source: none) => block(width: 100%, inset: (left: 16pt, y: 8pt))[
      #text(18pt, style: "italic", fill: pal.ink)[#quote[#body]]
      #if source != none [#linebreak() #text(12pt, fill: pal.text_soft)[— #source]]
    ],

    // ── Figure ────────────────────────────────────────────────
    "figbox": (title, body, caption: none) => block(width: 100%, inset: 0pt)[
      #block(width: 100%, stroke: (bottom: 0.5pt + pal.hairline), inset: (bottom: 6pt))[
        #text(12pt, weight: "bold", fill: pal.ink)[#title]
      ]
      #v(6pt)
      #body
      #if caption != none [
        #v(4pt)
        #text(11pt, fill: pal.text_soft, style: "italic")[#caption]
      ]
    ],

    // `src` is an image path, or any ready-made content (a drawn placeholder).
    "portrait": (src, name, size: 48pt) => box(width: size + 6pt)[
      #align(center)[
        #box(width: size, height: size, clip: true, stroke: 0.5pt + pal.hairline,
          radius: 3pt,
          if type(src) == str { image(src, width: size, height: size, fit: "cover") }
          else { src })
        #v(4pt)
        #text(11pt, fill: pal.text)[#name]
      ]
    ],

    "clip_image": (src, top: 0pt, bottom: 0pt, left: 0pt, right: 0pt, width: auto) => {
      let body = if type(src) == str { image(src, width: width) } else { src }
      box(clip: true, width: width,
        inset: (top: -top, bottom: -bottom, left: -left, right: -right), body)
    },

    // ── Stats ─────────────────────────────────────────────────
    // Pass plain values ([13], not [*13*]) — the gadget bolds and colours.
    "stat": (value, label) => align(center)[
      #text(32pt, weight: "bold", fill: pal.accent_deep)[#value]
      #v(2pt)
      #text(12pt, fill: pal.text_soft)[#label]
    ],

    "stat_row": (..items) => grid(
      columns: (1fr,) * items.pos().len(), column-gutter: 12pt,
      ..items.pos().map(it => align(center)[
        #text(30pt, weight: "bold", fill: pal.accent_deep)[#it.value]
        #v(2pt)
        #text(12pt, fill: pal.text_soft)[#it.label]
      ]),
    ),

    "spec_list": (..items) => {
      let rows = items.pos().enumerate().map(((i, it)) => block(inset: (bottom: 7pt))[
        #text(13pt, weight: "bold", fill: pal.accent_deep)[#(i + 1).] #h(4pt)
        #text(weight: "bold", fill: pal.text)[#it.term] #h(4pt)
        #text(fill: pal.text_soft)[#it.desc]
        #if "tag" in it [
          #h(4pt) #box(fill: tint(pal.primary, 10%), inset: (x: 5pt, y: 2pt), radius: 2pt)[
            #text(10pt, fill: pal.primary)[→ #it.tag]
          ]
        ]
      ])
      rows.join()
    },

    // ── Theory boxes (hand-rolled, no extra packages) ─────────
    "theorem": _thm("Theorem", pal.primary, pal),
    "definition": _thm("Definition", pal.accent, pal),
    "lemma": _thm("Lemma", pal.secondary, pal),
    "example": _thm("Example", pal.text_soft, pal),
    "proof_box": _thm("Proof", pal.success, pal),

    // ── Badges ────────────────────────────────────────────────
    "badge": (label, fill: pal.primary, fg: auto) => box(
      fill: fill, inset: (x: 7pt, y: 2.5pt), radius: 2pt,
      text(10pt, weight: "bold",
        fill: if fg == auto { on-primary } else { fg })[#upper(label)],
    ),

    "tag": (label) => box(
      fill: tint(pal.primary, 10%), inset: (x: 7pt, y: 2.5pt), radius: 8pt,
      stroke: 0.5pt + tint(pal.primary, 35%),
      text(10pt, fill: pal.primary)[#label],
    ),

    "time_badge": (label) => box(
      fill: tint(pal.warning, 13%), inset: (x: 7pt, y: 2.5pt), radius: 2pt,
      text(font: mono, size: 10pt, weight: "bold", fill: pal.warning)[#label],
    ),

    // ── Structure ─────────────────────────────────────────────
    // data_table: positional rows; the FIRST row is the header. The first
    // column is the row label (sans, left); value columns are mono, centred.
    //   #data_table(("Metric","Before","After"), ("Lat","340","52"), highlight: (0,))
    "data_table": (..rows, highlight: ()) => {
      let all = rows.pos()
      let head = all.first()
      let body = all.slice(1)
      let ncols = head.len()
      let hcell = (h) => text(11pt, weight: "bold", fill: pal.text_soft,
        if type(h) == str { upper(h) } else { h })
      let cell = (j, it, emph) => {
        let body = text(
          size: if j == 0 { 15pt } else { 14pt },
          weight: if emph { "bold" } else { "regular" },
          fill: if emph { pal.accent_deep } else { pal.text },
        )[#it]
        if j == 0 { body } else { text(font: mono, body) }
      }
      table(
        columns: (auto,) + (1fr,) * calc.max(ncols - 1, 0),
        align: (left + horizon,) + (center + horizon,) * calc.max(ncols - 1, 0),
        stroke: (x: none, y: 0.5pt + pal.hairline),
        inset: (x: 8pt, y: 7pt),
        table.header(..head.map(hcell)),
        ..body.enumerate().map(((i, r)) => {
          let emph = i in highlight
          r.enumerate().map(((j, c)) => cell(j, c, emph))
        }).flatten(),
      )
    },

    "conclusion_grid": (..cards) => {
      let items = cards.pos()
      grid(
        columns: (1fr, 1fr), column-gutter: 8pt, row-gutter: 8pt,
        ..items.enumerate().map(((i, c)) => {
          let is-dark = i == items.len() - 1
          let bg = if is-dark { pal.primary } else { pal.paper_bg }
          let fg = if is-dark { on-primary } else { pal.ink }
          let fg-sub = if is-dark { color.mix((on-primary, 70%), (pal.primary, 30%)) }
            else { pal.text_soft }
          block(fill: bg, inset: 12pt, radius: 3pt, width: 100%)[
            #text(10pt, weight: "bold", fill: fg-sub)[#upper(c.label)]
            #v(4pt)
            #text(15pt, weight: "bold", fill: fg)[#c.title]
            #v(4pt)
            #text(12pt, fill: fg-sub)[#c.body]
          ]
        }),
      )
    },

    "key_links": (..pairs) => block(width: 100%)[
      #grid(
        columns: 1, row-gutter: 5pt,
        ..pairs.pos().map(((lab, link)) => grid(columns: (auto, 1fr), column-gutter: 10pt,
          text(11pt, weight: "bold", fill: pal.text_soft)[#upper(lab)],
          text(12pt, fill: pal.primary)[#link])),
      )
    ],

    // ── Deck chrome / pacing ──────────────────────────────────
    // Section outline for the `== Outline` slide (Typst's #outline() renders a
    // paper-style dotted TOC — wrong register for a deck). Lists level-1
    // headings, column-major, numbered in the accent.
    "toc": (columns: 1, size: 17pt) => context {
      let secs = query(heading.where(level: 1)).filter(h => h.outlined)
      let per = calc.max(calc.ceil(secs.len() / columns), 1)
      let entry = (i, h) => grid(columns: (auto, 1fr), column-gutter: 10pt, align: top,
        text(size, weight: "bold", fill: pal.accent_deep)[#(i + 1)],
        text(size, fill: pal.ink)[#h.body])
      grid(
        columns: (1fr,) * columns, column-gutter: 28pt, align: top,
        ..range(columns).map(k => grid(
          columns: 1, row-gutter: 14pt,
          ..secs.enumerate().slice(k * per, calc.min((k + 1) * per, secs.len()))
            .map(((i, h)) => entry(i, h)),
        )),
      )
    },

    "pacing": (minutes) => [
      #_clock.update(t => t + minutes)
      #context {
        place(top + right,
          text(11pt, fill: pal.text_soft)[#_clock.get() min])
      }
    ],

    "kicker": (label) => text(11pt, weight: "bold", tracking: 1.2pt, fill: pal.accent_deep)[#upper(label)],

    "progress_dots": (n, current) => {
      let dots = range(n).map(i => {
        let on = i <= current
        box(inset: (x: 1pt))[
          #box(width: 7pt, height: 7pt, radius: 50%,
            fill: if on { pal.primary } else { pal.hairline })[]
        ]
      })
      dots.join()
    },
  )
}
