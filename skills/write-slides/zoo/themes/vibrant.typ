// Vibrant theme — saturated teal + magenta. For teaching and outreach decks
// where energy beats gravitas and slides must read from the back row.
#import "@preview/touying:0.6.1": *
#import themes.metropolis: *
#import "../palettes/vibrant.typ": palette, fonts

#let theme(..args, body) = {
  set text(font: fonts.sans, lang: "en")
  show math.equation: set text(font: fonts.math)
  show: metropolis-theme.with(
    aspect-ratio: "16-9",
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
