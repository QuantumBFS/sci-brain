// Brand palette — a generator. Derives a coherent palette from one primary color
// so a lab or product can drop in its house color and get a matching deck.
//
//   #import "zoo/palettes/brand.typ": build
//   #let palette = build(rgb("#aa1e2b"))   // your house color
//
// Derivation rules (kept simple and predictable, using only color.mix):
//   - primary       = the given color
//   - primary_light = primary mixed 85% toward white
//   - secondary     = primary mixed 15% toward black
//   - accent        = primary mixed 55% toward a lavender complement
//   - ink / text    = a very dark shade of primary (12% primary into near-black)
//   - neutrals      = white paper + the dark ink
#let build(primary) = {
  let mix2 = (a, wa, b, wb) => color.mix((a, wa), (b, wb))
  let pl = primary.lighten(85%)
  let sec = primary.darken(15%)
  let ink-c = mix2(primary, 88%, rgb("#10101a"), 12%)
  let text-c = mix2(primary, 92%, rgb("#16161e"), 8%)
  let soft = text-c.lighten(45%)
  let accent-c = mix2(primary, 45%, rgb("#9b83ec"), 55%)
  return (
    primary: primary,
    primary_light: pl,
    secondary: sec,
    // Text on a primary-filled surface. House colors are assumed dark enough
    // for white; pass a dark override into gadgets manually if yours is pastel.
    on_primary: rgb("#ffffff"),
    accent: accent-c,
    accent_deep: accent-c.darken(18%),
    ink: ink-c,
    text: text-c,
    text_soft: soft,
    paper: rgb("#ffffff"),
    paper_bg: pl.lighten(55%),
    hairline: mix2(pl, 60%, rgb("#cccccc"), 40%),
    success: rgb("#2e7d32"),
    warning: rgb("#c62828"),
    neutral_lightest: rgb("#ffffff"),
    neutral_dark: soft,
    neutral_darkest: text-c,
  )
}

// Default brand palette, so it can be listed alongside the others.
#let palette = build(rgb("#2f2f7f"))

// Ordered fallback chains — Typst can't query the OS, so the chain IS the
// OS switch: Linux picks DejaVu/Noto, macOS falls through to Helvetica Neue.
#let fonts = (
  sans: ("DejaVu Sans", "Noto Sans", "Helvetica Neue", "Arial", "Liberation Sans"),
  serif: ("New Computer Modern", "Libertinus Serif"),
  math: ("New Computer Modern Math", "Libertinus Math"),
  mono: ("DejaVu Sans Mono", "Noto Mono", "Menlo"),
)
