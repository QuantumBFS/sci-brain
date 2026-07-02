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

// Running pacing counter, shared across all gadget dicts in this document.
#let _clock = state("slide-writer-clock", 0)

// Theory-box factory shared by theorem / definition / lemma / example / proof_box.
#let _thm(label, border, fill, pal) = (title: none, body) => block(
  width: 100%, radius: 3pt, inset: (x: 12pt, y: 8pt),
  stroke: (left: 3pt + border), fill: fill,
)[
  #text(9pt, weight: "bold", fill: border)[#upper(label)#if title != none [ · #title]]
  #v(3pt)
  #text(11pt, fill: pal.text)[#body]
]

#let make(pal) = {
  let tint = pal.primary.lighten(90%)
  let tint-deep = pal.primary.lighten(80%)
      let mono = ("DejaVu Sans Mono", "Noto Mono")

  let kind-color = (
    info: pal.accent,
    success: pal.success,
    warning: pal.warning,
    danger: pal.warning,
    accent: pal.accent_deep,
  )

  return (
    // ── Callouts ──────────────────────────────────────────────
    "rail_pull": (body) => block(
      width: 100%, inset: (left: 12pt, y: 6pt),
      stroke: (left: 3pt + pal.accent),
    )[#text(15pt, style: "italic", fill: pal.ink)[#body]],

    "callout": (label, body, kind: "info") => {
      let c = kind-color.at(kind, default: pal.accent)
      block(width: 100%, radius: 3pt, inset: 10pt,
        stroke: (left: 3pt + c), fill: c.lighten(88%))[
        #text(9pt, weight: "bold", fill: c)[#upper(label)]
        #v(2pt)
        #text(11pt, fill: pal.text)[#body]
      ]
    },

    "codebox": (body) => block(
      width: 100%, radius: 4pt, inset: 10pt,
      fill: pal.primary.lighten(93%),
      stroke: 0.5pt + pal.hairline,
    )[#text(font: mono, 10pt)[#body]],

    "quote_pull": (body, source: none) => block(width: 100%, inset: (left: 16pt, y: 8pt))[
      #text(16pt, style: "italic", fill: pal.ink)[#quote[#body]]
      #if source != none [#linebreak() #text(10pt, fill: pal.text_soft)[— #source]]
    ],

    // ── Figure ────────────────────────────────────────────────
    "figbox": (title, body, caption: none) => block(width: 100%, inset: 0pt)[
      #block(width: 100%, stroke: (bottom: 0.5pt + pal.hairline), inset: (bottom: 6pt))[
        #text(9pt, weight: "bold", fill: pal.ink)[#title]
      ]
      #v(6pt)
      #body
      #if caption != none [
        #v(4pt)
        #text(9pt, fill: pal.text_soft, style: "italic")[#caption]
      ]
    ],

    "portrait": (path, name, size: 48pt) => box(width: size + 6pt)[
      #align(center)[
        #box(width: size, height: size, clip: true, stroke: 0.5pt + pal.hairline,
          radius: 2pt, image(path, width: size, height: size, fit: "cover"))
        #v(4pt)
        #text(9pt, fill: pal.text)[#name]
      ]
    ],

    "clip_image": (path, top: 0pt, bottom: 0pt, left: 0pt, right: 0pt, width: none) => {
      box(clip: true, width: width,
        inset: (top: -top, bottom: -bottom, left: -left, right: -right),
        image(path, width: width))
    },

    // ── Stats ─────────────────────────────────────────────────
    "stat": (value, label) => align(center)[
      #text(28pt, weight: "bold", fill: pal.accent_deep)[#value]
      #v(2pt)
      #text(10pt, fill: pal.text_soft)[#label]
    ],

    "stat_row": (..items) => grid(
      columns: (1fr,) * items.pos().len(), column-gutter: 12pt,
      ..items.pos().map(it => align(center)[
        #text(24pt, weight: "bold", fill: pal.accent_deep)[#it.value]
        #v(2pt)
        #text(9pt, fill: pal.text_soft)[#it.label]
      ]),
    ),

    "spec_list": (..items) => {
      let rows = items.pos().enumerate().map(((i, it)) => block(inset: (bottom: 6pt))[
        #text(12pt, weight: "bold", fill: pal.accent_deep)[#(i + 1).] #h(4pt)
        *#it.term* #h(4pt) #text(fill: pal.text_soft)[#it.desc]
        #if "tag" in it [
          #h(4pt) #box(fill: tint, inset: (x: 5pt, y: 2pt), radius: 2pt)[
            #text(8pt, fill: pal.primary)[→ #it.tag]
          ]
        ]
      ])
      rows.join()
    },

    // ── Theory boxes (hand-rolled, no extra packages) ─────────
    "theorem": _thm("Theorem", pal.primary, tint, pal),
    "definition": _thm("Definition", pal.accent, pal.accent.lighten(90%), pal),
    "lemma": _thm("Lemma", pal.secondary, tint, pal),
    "example": _thm("Example", pal.text_soft, pal.text_soft.lighten(90%), pal),
    "proof_box": _thm("Proof", pal.success, pal.success.lighten(90%), pal),

    // ── Badges ────────────────────────────────────────────────
    "badge": (label, fill: pal.primary) => box(
      fill: fill, inset: (x: 7pt, y: 2pt), radius: 2pt,
      text(8pt, weight: "bold", fill: white)[#upper(label)],
    ),

    "tag": (label) => box(
      fill: tint, inset: (x: 6pt, y: 2pt), radius: 8pt,
      stroke: 0.5pt + tint-deep,
      text(8pt, fill: pal.primary)[#label],
    ),

    "time_badge": (label) => box(
      fill: pal.warning.lighten(85%), inset: (x: 6pt, y: 2pt), radius: 2pt,
      text(8pt, weight: "bold", fill: pal.warning)[⏱ #label],
    ),

    // ── Structure ─────────────────────────────────────────────
    // data_table: positional rows; the FIRST row is the header.
    //   #data_table(("Metric","Before","After"), ("Lat","340","52"), highlight: (0,))
    "data_table": (..rows, highlight: ()) => {
      let all = rows.pos()
      let head = all.first()
      let body = all.slice(1)
      let ncols = head.len()
  let mono = ("DejaVu Sans Mono", "Noto Mono")
      let cell = (it, emph: false) => if emph {
        text(font: mono, fill: pal.accent_deep)[*#it*]
      } else {
        text(fill: pal.text)[#it]
      }
      table(
        columns: (auto,) + (1fr,) * calc.max(ncols - 1, 0),
        align: (left,) + (center,) * calc.max(ncols - 1, 0),
        stroke: (x: none, y: 0.5pt + pal.hairline),
        inset: 6pt,
        table.header(..head.map(h => text(8pt, weight: "bold", fill: pal.text_soft)[#upper(str(h))])),
        ..body.enumerate().map(((i, r)) => {
          let emph = i in highlight
          r.map(c => cell(c, emph: emph))
        }).flatten(),
      )
    },

    "conclusion_grid": (..cards) => {
      let items = cards.pos()
      grid(
        columns: (1fr, 1fr), rows: (auto, auto), column-gutter: 8pt, row-gutter: 8pt,
        ..items.enumerate().map(((i, c)) => {
          let is-dark = i == items.len() - 1
          let bg = if is-dark { pal.primary } else { pal.paper_bg }
          let fg = if is-dark { rgb("#ffffff") } else { pal.ink }
          let fg-sub = if is-dark { pal.primary.lighten(35%) } else { pal.text_soft }
          block(fill: bg, inset: 12pt, radius: 3pt, width: 100%)[
            #text(7pt, weight: "bold", fill: fg-sub)[#upper(c.label)]
            #v(4pt)
            #text(12pt, weight: "bold", fill: fg)[#c.title]
            #v(4pt)
            #text(9pt, fill: fg-sub)[#c.body]
          ]
        }),
      )
    },

    "key_links": (..pairs) => block(width: 100%)[
      #grid(
        columns: 1, row-gutter: 4pt,
        ..pairs.pos().map(((lab, link)) => grid(columns: (auto, 1fr), column-gutter: 10pt,
          text(8pt, weight: "bold", fill: pal.text_soft)[#upper(lab)],
          text(9pt, fill: pal.primary)[#link])),
      )
    ],

    // ── Chrome / pacing ───────────────────────────────────────
    "pacing": (minutes) => [
      #_clock.update(t => t + minutes)
      #context {
        place(top + right, dy: -1.4em,
          text(9pt, fill: pal.text_soft)[#_clock.get() min])
      }
    ],

    "kicker": (label) => text(9pt, weight: "bold", tracking: 1.2pt, fill: pal.accent)[#upper(label)],

    "progress_dots": (n, current) => {
      let dots = range(n).map(i => {
        let on = i <= current
        box(inset: (x: 1pt))[
          #if on [
            #box(width: 7pt, height: 7pt, fill: pal.primary, radius: 50%)[]
          ] else [
            #box(width: 7pt, height: 7pt, fill: pal.hairline, radius: 50%)[]
          ]
        ]
      })
      dots.join()
    },
  )
}
