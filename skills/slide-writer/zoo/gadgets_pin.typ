// slide-writer zoo — pinit gadgets (optional, requires @preview/pinit)
// ======================================================================
// Pin annotations onto figures or text: drop inline pin markers, then attach
// highlights and pointing notes that float to the right place on the slide.
//
//   #import "zoo/gadgets_pin.typ": make
//   #let P = make(palette)
//   A simple #P.pin(1)highlighted phrase#P.pin(2).
//   #P.highlight(1, 2)
//   #P.note(2)[And a note pointing at it.]

#import "@preview/pinit:0.2.2": pin, pinit-highlight, pinit-point-from

#let make(pal) = (
  // Drop an inline pin marker. Wrap content between two pins to highlight a span.
  "pin": (id) => pin(id),

  // Highlight the span between two (or more) pin ids.
  "highlight": (..ids) => pinit-highlight(..ids),

  // A pointing note attached to a pin, set in the slide's text colour.
  "note": (id, body, dx: 35pt, dy: 35pt) => pinit-point-from(id, offset-dx: dx, offset-dy: dy)[
    #block(radius: 3pt, inset: 6pt,
      fill: pal.accent.lighten(85%),
      stroke: 0.5pt + pal.accent,
      text(10pt, fill: pal.text)[#body])
  ],
)
