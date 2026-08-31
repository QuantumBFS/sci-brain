// Minimal theme — black ink on white, no progress bar, generous margin.
// The handout/lecture-note deck: decoration is the enemy.
#import "@preview/touying:0.6.1": *
#import themes.metropolis: *
#import "../palettes/minimal.typ": palette, fonts

#let theme(..args, body) = {
  set text(font: fonts.sans, lang: "en")
  show math.equation: set text(font: fonts.math)
  show: metropolis-theme.with(
    aspect-ratio: "16-9",
    footer-progress: false,
    config-page(margin: (top: 3.2em, bottom: 2em, x: 3em)),
    config-colors(
      primary: palette.primary,
      primary-light: palette.primary_light,
      secondary: palette.secondary,
      neutral-lightest: palette.neutral_lightest,
      neutral-dark: palette.neutral_dark,
      neutral-darkest: palette.neutral_darkest,
    ),
    ..args,
  )
  body
}
