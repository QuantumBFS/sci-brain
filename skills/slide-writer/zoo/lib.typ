// slide-writer zoo — library aggregator
// =======================================
// The single import surface for a deck. Pulls in the five palettes, five themes,
// the gadget/layout factories, and the touying slide primitives a deck needs.
//
//   #import "zoo/lib.typ": *
//   #let pal = palettes.academic
//   #let G = gadgets(pal)
//   #let L = layouts(pal)
//   #show: themes.academic.with(config-info(title: [...], author: [...], date: datetime.today()))
//   #title-slide()
//
// CeTZ/pinit gadget sets are intentionally NOT imported here, so a deck that does
// not diagram pays no extra-package cost. Import them directly when needed:
//   #import "zoo/gadgets_cetz.typ": make as make-cetz
//   #import "zoo/gadgets_pin.typ":  make as make-pin

#import "@preview/touying:0.6.1": *
#import themes.metropolis: title-slide, focus-slide, new-section-slide

#import "palettes/academic.typ" as _pal-academic
#import "palettes/dark.typ" as _pal-dark
#import "palettes/minimal.typ" as _pal-minimal
#import "palettes/vibrant.typ" as _pal-vibrant
#import "palettes/brand.typ" as _pal-brand

#import "themes/academic.typ": theme as _theme-academic
#import "themes/dark.typ": theme as _theme-dark
#import "themes/minimal.typ": theme as _theme-minimal
#import "themes/vibrant.typ": theme as _theme-vibrant
#import "themes/brand.typ": theme as _theme-brand

#import "gadgets.typ": make as make-gadgets
#import "layouts.typ": make as make-layouts

// Palettes: pure colour data. Pick one and bind gadgets/layouts to it.
#let palettes = (
  academic: _pal-academic.palette,
  dark: _pal-dark.palette,
  minimal: _pal-minimal.palette,
  vibrant: _pal-vibrant.palette,
  brand: _pal-brand.palette,
)

// Fonts per theme (sans/serif/mono stacks).
#let fonts = (
  academic: _pal-academic.fonts,
  dark: _pal-dark.fonts,
  minimal: _pal-minimal.fonts,
  vibrant: _pal-vibrant.fonts,
  brand: _pal-brand.fonts,
)

// Themes: touying show-rules. `themes.<name>.with(config-info(...))`.
#let themes = (
  academic: _theme-academic,
  dark: _theme-dark,
  minimal: _theme-minimal,
  vibrant: _theme-vibrant,
  brand: _theme-brand,
)

// Factories: call with the chosen palette to get bound gadget/layout dicts.
#let gadgets = make-gadgets
#let layouts = make-layouts
