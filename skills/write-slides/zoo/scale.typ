// write-slides zoo — type scale
// ==============================
// Exactly three text sizes, deck-wide. `normal` equals the touying/metropolis
// body size (20pt), so every glyph on a slide lands on one of three steps —
// hierarchy comes from weight, colour, and case, not from ever-smaller type.
//
//   xlarge — the one hero statement a slide carries (punch, title, section
//            and focus slides; 1.5 × body, matching metropolis's 1.5em)
//   large  — emphasised statements and slogans (stat, rail_pull, quote_pull, toc)
//   normal — everything else: bodies, labels, captions, table cells, chrome
#let sizes = (
  xlarge: 30pt,
  large: 24pt,
  normal: 20pt,
)
