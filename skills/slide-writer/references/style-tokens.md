# slide-writer zoo — Style Tokens

The palette vocabulary every theme speaks, the touying slots each maps onto, and
the per-theme values. All values live in `zoo/palettes/<name>.typ`; this file is
the human-readable mirror. When a gadget reads `pal.accent` or a theme feeds
`config-colors`, these are the values in play.

## Palette keys (the vocabulary)

Every palette exports these keys. Gadgets and layouts read them by name, so a
gadget written against `academic` works unchanged under `dark`.

| Key | Role | Read by |
|---|---|---|
| `primary` | The theme's signature colour — headings, header fill, section accents | theme, badges, theory borders |
| `primary_light` | A 85–90% tint of primary — soft fills, tag backgrounds | theme (touying `primary-light`) |
| `secondary` | A darker shade of primary — secondary chrome | theme (touying `secondary`) |
| `on_primary` | Text on a primary-filled surface (dark theme: dark text on light-blue primary) | badge, conclusion_grid's dark card |
| `accent` | The complement — `rail_pull` bar, callout borders, pin notes | rail_pull, callout, tag |
| `accent_deep` | A deeper accent — big numerals, punch, highlighted table cells | stat, punch, data_table highlight |
| `ink` | Heading / title colour | rail_pull, quote_pull, figbox title |
| `text` | Body copy on light surfaces | most gadgets |
| `text_soft` | Captions, meta labels, sub-copy | captions, kicker, key_links |
| `paper` | The pure page surface | (backgrounds) |
| `paper_bg` | A faint tint for callout / card fills | cards, callout bg |
| `hairline` | 0.5pt rules between rows, figure frames | figbox, data_table, cards |
| `success` | "success"/"proof" semantic colour | callout(kind:"success"), proof_box |
| `warning` | "warning"/"danger" semantic colour | callout(kind:"warning"), time_badge |
| `neutral_lightest` | touying page fill (white, or dark on the dark theme) | theme (touying `neutral-lightest`) |
| `neutral_dark` | touying secondary text | theme (touying `neutral-dark`) |
| `neutral_darkest` | touying body text (light on the dark theme) | theme (touying `neutral-darkest`) |

### Touying slot mapping (metropolis base)

The five themes all wrap `metropolis-theme` and feed it these slots:

```
config-colors(
  primary:           pal.primary,
  primary-light:     pal.primary_light,
  secondary:         pal.secondary,
  neutral-lightest:  pal.neutral_lightest,   // page fill
  neutral-dark:      pal.neutral_dark,
  neutral-darkest:   pal.neutral_darkest,    // body text
)
```

So to retheme touying, you retheme the palette — the theme file is a thin
adapter.

### Derived fills (the dark-theme invariant)

Gadgets never compute soft fills with `c.lighten(...)` — that walks toward
white and turns into white-on-white under the dark palette. They mix the accent
into the palette's own paper instead:

```typst
fill: color.mix((c, 12%), (pal.paper, 88%))   // ≈ pastel on white, deep tint on slate
```

Follow the same rule in any new gadget, and read `pal.on_primary` for text
sitting on a `pal.primary` fill.

## Typography

| Use | Family | Notes |
|---|---|---|
| Sans (default body + headings) | DejaVu Sans → Noto Sans | metropolis is a sans theme |
| Math | New Computer Modern Math → Libertinus Math | bound via `show math.equation: set text(font: fonts.math)`; must be a font with an OpenType MATH table, or operators collapse to letter height |
| Serif (reserved) | New Computer Modern → Libertinus Serif | unused by the stock themes; available for venue overrides |
| Mono (code, numerals) | DejaVu Sans Mono → Noto Mono | `codebox`, `data_table`, `time_badge` |

Body size is 20 pt (metropolis default). Gadget body copy sits at 13–14 pt,
captions and labels at 11–12 pt, badges/tags at 10 pt bold caps, big numerals at
30–54 pt. **Floor: nothing below 10 pt**, and nothing meant to be *read* below
~11 pt — if smaller is tempting, the slide is overfull. One caveat: touying
show-rules `strong` as an alert (theme primary), so gadgets bold via
`text(weight: "bold")` and callers pass plain values. Override fonts per-theme
in `zoo/themes/<name>.typ` if a venue demands it (the stacks above ship with
TeX Live / most Linux distros; Typst bundles only NCM, Libertinus, and DejaVu
Sans Mono — check `typst fonts`).

## Per-theme values

### academic — navy on white (default)

| primary | on_primary | accent | accent_deep | ink | text | paper_bg | hairline |
|---|---|---|---|---|---|---|---|
| `#2f2f7f` | `#ffffff` | `#9b83ec` | `#7c5fdc` | `#2f2f7f` | `#1c1c2e` | `#f7f7fb` | `#d4d4de` |

### dark — light on deep slate

| primary | on_primary | accent | accent_deep | ink | text | paper_bg | hairline |
|---|---|---|---|---|---|---|---|
| `#7c9cf0` | `#10142a` | `#e0b341` | `#c8a13a` | `#e8ecff` | `#e8ecff` | `#161a2e` | `#38406b` |

`neutral_lightest` is the dark paper `#1b2138`; `neutral_darkest` is the light
text `#e8ecff` — i.e. the light/dark roles are inverted from the light themes.

### minimal — black on white

| primary | on_primary | accent | accent_deep | ink | text | paper_bg | hairline |
|---|---|---|---|---|---|---|---|
| `#111111` | `#ffffff` | `#555555` | `#222222` | `#111111` | `#111111` | `#fafafa` | `#cccccc` |

The minimal theme also turns off the footer progress bar and widens the margin —
see `zoo/themes/minimal.typ`.

### vibrant — teal + magenta

| primary | on_primary | accent | accent_deep | ink | text | paper_bg | hairline |
|---|---|---|---|---|---|---|---|
| `#0d9488` | `#ffffff` | `#db2777` | `#be185d` | `#134e4a` | `#1c2b2a` | `#f0fdfa` | `#99f6e4` |

### brand — derived from one colour

`palettes/brand.typ` exports `build(primary)` which derives the full palette
from a single house colour:

```typst
#import "zoo/palettes/brand.typ": build
#let pal = build(rgb("#aa1e2b"))   // your lab / product colour
```

Derivation: `primary_light` = primary +85% toward white; `secondary` = primary
−15%; `accent` = primary mixed 55% toward a lavender complement; `ink`/`text` =
primary mixed ~12% into near-black; `on_primary` = white (house colours are
assumed dark — pass gadgets a custom palette if yours is pastel). Predictable,
always harmonious, no manual colour-picking.

## Adding a new theme

1. Add `zoo/palettes/<name>.typ` exporting `palette` and `fonts` (include every
   key in the vocabulary table — `on_primary` too).
2. Add `zoo/themes/<name>.typ` — copy `academic.typ`, swap the palette import,
   adjust any theme flags (e.g. `footer-progress`, margins).
3. Register both in `zoo/lib.typ` (`palettes`, `themes`, `fonts` dicts).
4. Add a swatch slide in `gallery.typ` under the `= Color themes` section.
5. Recompile `gallery.typ` to confirm the new theme renders.

## Don't

- **Don't hardcode hex colours in slides.** Read `pal.X` so a theme switch
  repaints the whole deck.
- **Don't mix themes in one deck.** Pick one; the chrome is part of the identity.
- **Don't reach for CeTZ/pinit in the preamble unless you diagram.** They are
  imported per-section in the gallery on purpose — a text-only deck pays no
  extra-package cost.
- **Don't `lighten()` a fill in a gadget.** Mix into `pal.paper` (see "Derived
  fills") or the dark theme goes white-on-white.
- **Don't pass `[*bold*]` values into gadgets.** Touying's strong-as-alert rule
  repaints them primary; gadgets bold their own numerals.
- **Don't set slide text below ~11 pt.** Split the slide instead.
