// Dark theme — light text on deep slate. For dim rooms and glare-fatiguing projectors.
// Page fill (neutral-lightest) is the dark paper; body text (neutral-darkest) is light.
#import "@preview/touying:0.6.1": *
#import themes.metropolis: *
#import "../palettes/dark.typ": palette, fonts

#let theme(..args, body) = {
  set text(font: fonts.sans, lang: "en")
  show math.equation: set text(font: fonts.serif)
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
