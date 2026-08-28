// Dark palette — light text on a deep slate ground.
// For dim rooms and projectors where a white background glare-fatigues the audience.
#let palette = (
  primary: rgb("#7c9cf0"),
  primary_light: rgb("#2a3358"),
  secondary: rgb("#9db4f5"),
  on_primary: rgb("#10142a"),
  accent: rgb("#e0b341"),
  accent_deep: rgb("#c8a13a"),
  ink: rgb("#e8ecff"),
  text: rgb("#e8ecff"),
  text_soft: rgb("#a6adcb"),
  paper: rgb("#1b2138"),
  paper_bg: rgb("#161a2e"),
  hairline: rgb("#38406b"),
  success: rgb("#5fd49a"),
  warning: rgb("#e09a4a"),
  neutral_lightest: rgb("#1b2138"),
  neutral_dark: rgb("#a6adcb"),
  neutral_darkest: rgb("#e8ecff"),
)

// Ordered fallback chains — Typst can't query the OS, so the chain IS the
// OS switch: Linux picks DejaVu/Noto, macOS falls through to Helvetica Neue.
#let fonts = (
  sans: ("DejaVu Sans", "Noto Sans", "Helvetica Neue", "Arial", "Liberation Sans"),
  serif: ("New Computer Modern", "Libertinus Serif"),
  mono: ("DejaVu Sans Mono", "Noto Mono", "Menlo"),
)
