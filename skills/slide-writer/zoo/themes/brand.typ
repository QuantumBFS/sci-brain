// Brand theme — drop in your lab/product house colour and get a matching deck.
//
//   #show: brand-theme.with(primary: rgb("#aa1e2b"), config-info(...))
//
// The deck should build the *same* palette for gadgets via palettes/brand.typ:
//   #import "zoo/palettes/brand.typ": build
//   #let pal = build(rgb("#aa1e2b"))
//   #let G = make-gadgets(pal)
#import "@preview/touying:0.6.1": *
#import themes.metropolis: *
#import "../palettes/brand.typ": build, palette, fonts

#let theme(primary: rgb("#2f2f7f"), ..args, body) = {
  let pal = build(primary)
  set text(font: fonts.sans, lang: "en")
  show math.equation: set text(font: fonts.math)
  show: metropolis-theme.with(
    aspect-ratio: "16-9",
    config-colors(
      primary: pal.primary,
      primary-light: pal.primary_light,
      secondary: pal.secondary,
      neutral-lightest: pal.neutral_lightest,
      neutral-dark: pal.neutral_dark,
      neutral-darkest: pal.neutral_darkest,
    ),
    ..args,
  )
  body
}
