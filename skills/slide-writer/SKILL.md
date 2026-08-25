---
name: slide-writer
description: Use when building a slide deck in Typst + Touying for a scientific talk, lecture, or project briefing — ships a browsable zoo of color themes, layout templates, and gadgets (callouts, theory boxes, CeTZ diagrams, pin annotations) that compose into projector-safe slides. Distinct from slide-writing (HTML, QudeLeap brand) and paper-writer (full manuscripts).
---

# Slide Writer (Typst + Touying)

A technical skill for building PDF slide decks in Typst with the Touying slide
engine. It ships a **zoo** — five color themes, nine layout templates, and two
dozen gadgets — that compose into projector-safe slides for scientific talks. The
zoo is the deliverable; this file teaches how to drive it.

**Scope note.** This skill is the *technical* companion to `slide-writing`.
`slide-writing` owns the *logical* layer (the logic-flow sign-off, the per-page
design discipline, the house rules for figure-vs-commentary rhythm) and outputs
HTML in a fixed brand. This skill owns the *Typst/Touying* layer: which theme,
which layout, which gadget, and how to compile. When a deck is for an external
brand or must be HTML, use `slide-writing`. When it is a PDF research talk,
lecture, or briefing, use this skill.

## When to use

- A research talk, conference presentation, seminar, or lecture as a PDF deck.
- A project briefing or internal report that should read as deliberate slides.
- Any deck where Touying's `#pause` animations, math, CeTZ diagrams, or Typst's
  typesetting are worth more than a browser deck.

## When NOT to use

- A brand-locked or investor-facing deck — use `slide-writing` (HTML, brand).
- A one-page handout or status update — write Markdown.
- An in-paper figure — use Typst directly, or `paper-writer` + `figure-taste`.
- A real manuscript with results — use `paper-writer`.

---

## The zoo at a glance

Everything lives under `skills/slide-writer/zoo/`. Compile `gallery.typ` to see
the whole catalogue rendered (`typst compile gallery.typ`, or
`--input theme=dark` to preview any theme).

| Axis | Count | Where | Examples |
|---|---|---|---|
| **Color themes** | 5 | `zoo/themes/` | academic, dark, minimal, vibrant, brand |
| **Layouts** (slide-body composers) | 9 | `zoo/layouts.typ` | spread, twocol, threecol, hero, band, cards, punch |
| **Gadgets** (content components) | ~25 | `zoo/gadgets.typ` | rail_pull, callout, figbox, stat_row, spec_list, theorem, data_table, conclusion_grid, codebox, toc, pacing |
| **CeTZ diagrams** (optional) | 4 | `zoo/gadgets_cetz.typ` | tensor, automaton-state, edge, flowbox |
| **Pin annotations** (optional) | 3 | `zoo/gadgets_pin.typ` | pin, highlight, note |
| **Touying primitives** | — | re-exported by `zoo/lib.typ` | `title-slide`, `focus-slide`, `#pause` |

Palettes (pure color data) live in `zoo/palettes/`; each theme maps its palette
onto Touying's `config-colors` slots. The single import surface is `zoo/lib.typ`.

---

## Workflow

Borrow the logical discipline from `slide-writing` (agree the outline before
drawing), then enrich it with the Typst technical layer. Do not reorder — the
sequence is the point.

### Phase 0 — Load context

- Read any `docs/discussion/*-brainstorm-ideas-log.md` for the talk's *why*.
- Pull figures the deck will reuse from `$KB/.figures/`, the paper's `figs/`,
  or a prior talk — do not redraw a figure the author already drew.
- If the talk presents a manuscript, read `articles/<paper>/main.typ` so the
  deck's claims match the paper's.

### Phase 1 — Logic flow (sign-off gate)

Capture **topic**, **audience**, **key claim** in three lines. Propose a
section outline of 5–8 sections (12 is the ceiling), one line each:

```
§N · <section name> — <main claim, 1 sentence> — <figure idea, ≤8 words>
```

Show the outline and **wait for sign-off**. A deck whose outline is wrong is
wrong on every page; do not touch Typst until the user approves.

### Phase 2 — Pick the theme (before any slide)

Choose one theme up front and commit. The decision is audience + room:

| Situation | Theme |
|---|---|
| Conference talk, default, projector-safe | `academic` |
| Dim room, projector glare | `dark` |
| Lecture notes printed as slides, handout | `minimal` |
| Teaching, outreach, back-row energy | `vibrant` |
| Your lab/product has a house color | `brand` (pass `build(rgb("#…"))`) |

Theme-hopping mid-deck reads as inconsistent. Pick once.

### Phase 3 — Compose slides from the zoo (one at a time)

For each section in the approved outline, pick a layout/gadget by the slide's
job — the router is `references/layout-patterns.md`. Write the slide, then show
the user (compiled page or markdown form) before moving on.

### Phase 4 — Assemble and verify

1. Scaffold a self-contained deck (copies the zoo next to the `.typ`):
   ```bash
   python3 skills/slide-writer/scripts/scaffold.py <target> --name <deck> --theme <theme>
   ```
2. Paste the approved slides into `<deck>.typ`.
3. Compile and walk it:
   ```bash
   typst compile <deck>.typ          # the compile IS the lint
   ```
   - Every `==` heading is a slide; every `=` is a section divider.
   - Check: titles carry one italic accent, no slide overflows, every figure is
     cited in the rail, the outline (`#toc()`) lists the real sections, and no
     text sits below ~11 pt.

### Phase 5 — Figure-taste pass

Hand any figure-heavy slide to the `figure-taste` skill (line weight, color
discipline, text size, chartjunk). Slides are the harshest viewing context for a
figure; a figure that survives `figure-taste` survives a projector.

---

## The preamble (copy once per deck)

```typst
#import "zoo/lib.typ": *

#let pal = palettes.academic
#show: themes.academic.with(config-info(
  title: [Deck Title], subtitle: [one-line],
  author: [Name], date: datetime.today(), institution: [Org],
))

#let (rail_pull, callout, codebox, quote_pull, figbox, portrait, clip_image,
      stat, stat_row, spec_list, theorem, definition, lemma, example, proof_box,
      badge, tag, time_badge, data_table, conclusion_grid, key_links, toc,
      pacing, kicker, progress_dots) = gadgets(pal)
#let (spread, twocol, threecol, hero, band, cards, card, punch,
      centered_figure) = layouts(pal)

#title-slide()

== Outline
#toc()          // deck-register section list; #outline() is a paper TOC
```

The two `#let` lines destructure the gadget/layout factories bound to `pal`, so
every gadget already knows the active theme's colors. To switch theme, change
`palettes.academic` → `palettes.dark` and `themes.academic` → `themes.dark` in
those three spots — nothing else moves. Full router + copyable snippets in
`references/layout-patterns.md`; palette vocabulary in
`references/style-tokens.md`.

### Optional: diagrams and pin annotations

CeTZ and pinit are imported per-section (not in the preamble) so a text-only deck
pays no extra-package cost:

```typst
#import "zoo/gadgets_cetz.typ": make as make-cetz
#import "@preview/cetz:0.4.2": canvas
#let (tensor, automaton-state, edge, flowbox) = make-cetz(pal)
```

---

## House rules

- **One figure per slide.** A second figure means two slides conflated.
- **One accent for emphasis.** Numerals and `rail_pull` use `accent_deep`; do
  not repaint gadgets by hand — read `pal.X` so a theme switch repaints all.
- **Tabular numbers in mono.** `data_table` value columns and `time_badge` set
  it themselves; emphasised quantities (`stat`, `punch`) stay in the theme sans.
- **A number is emphasised as a statement, not a dashboard numeral.** `stat`,
  `stat_row`, and `punch` set the full quantity ("13 weeks", via `unit:`) in
  bold accent at the same scale as its meaning — never a giant bare "13" over
  a small caption.
- **Three text sizes, deck-wide.** The whole zoo draws from `sizes` in
  `zoo/scale.typ` — `xlarge` (30 pt, the one hero statement; also the title,
  section, and focus slides), `large` (24 pt,
  emphasised statements and slogans), `normal` (20 pt, everything else —
  bodies, labels, captions, table cells, chrome). Hierarchy comes from weight,
  colour, and case, never from smaller type. Use `sizes.X` (exported by
  `zoo/lib.typ`) for hand-rolled text; if content only fits smaller, the slide
  holds two slides' worth.
- **Pass plain values to gadgets** (`[13]`, not `[*13*]`): touying show-rules
  `strong` as an alert and would repaint your bold in theme primary. Gadgets
  bold and colour their own numerals.
- **Captions describe how to *read* the figure**, not what it is.
- **Use the source's own figures.** Pull from `figs/`, README, prior slides.
  Redrawing an author's figure as inline SVG produces a worse copy.
- **Pick the theme up front.** The chrome (header, footer, progress bar) is part
  of the deck's identity.
- **`==` is a slide, `=` is a section.** Don't nest slide content under the
  wrong heading level.
- **Recompile the gallery** when you add a gadget or layout — it is the visual
  regression test for the zoo.

## Common mistakes

| Mistake | Fix |
|---|---|
| Started composing slides before outline sign-off | Stop. Return to Phase 1. |
| Hardcoded a hex color in a slide | Read `pal.X` instead, so theme switches propagate. |
| Called a gadget as `G.figbox(...)` | Typst needs the destructure form (`figbox(...)`) or `(G.figbox)(...)`. Use the preamble's `#let` destructure. |
| Mixed two themes in one deck | Pick one; the chrome must stay consistent. |
| Used `//` inside markup `[...]` | `//` starts a line comment and eats the closing `]`. Drop it or use a raw block. |
| Wrapped a gadget value in `*...*` | Touying repaints `strong` in theme primary (alert). Pass plain content; the gadget bolds. |
| Typed a CLI string (`--input`, `<name>`) in prose | Markup turns `--` into – and eats `<name>` as a label. Put literal strings in backticks / `#raw`. |
| Inline-SVG'd a figure that exists in the source | Stop. Embed the source SVG/PDF instead. |
| Added CeTZ/pinit to the preamble of a text deck | Import them per-section; the preamble stays dependency-light. |
| Compile fails on a missing font | The palettes target DejaVu / Noto / New Computer Modern — stock on TeX Live and most Linux installs (Typst itself bundles only NCM, Libertinus, and DejaVu Sans Mono). Confirm with `typst fonts` before switching families. |

## Integrations

- **Logical workflow + brand decks:** `slide-writing` (HTML) is the sibling; this
  skill borrows its sign-off discipline.
- **Figures:** reuse figures from `paper-writer` manuscripts and the project KB;
  run `figure-taste` on figure-heavy slides (Phase 5).
- **Brainstorming:** a talk often follows a `/brainstorm-ideas` session — read its
  log for the deck's motivation and key claim.
- **Citations:** slides rarely need a bibliography page; if they do, point
  `\bibliography`/`#bibliography` at `$KB/.knowledge/references.bib`.

## What's in the bundle

| Path | Purpose |
|---|---|
| `gallery.typ` | Visual index of the whole zoo; compile to browse. `--input theme=<name>` rethemes. |
| `zoo/lib.typ` | Single import surface: palettes, themes, gadget/layout factories, `sizes` type scale, touying slide primitives. |
| `zoo/scale.typ` | The three deck-wide text sizes (`xlarge`/`large`/`normal`); every zoo text call uses one. |
| `zoo/palettes/` | Five pure-data color modules (+ `brand.typ`'s `build(primary)` generator). |
| `zoo/themes/` | Five thin metropolis overlays mapping palettes → touying `config-colors`. |
| `zoo/gadgets.typ` | ~24 palette-aware content components (callouts, stats, theory, structure, chrome). |
| `zoo/layouts.typ` | Nine slide-body composers (spread, twocol, hero, cards, …). |
| `zoo/gadgets_cetz.typ` | Optional CeTZ diagram helpers (tensor, automaton, flowbox). |
| `zoo/gadgets_pin.typ` | Optional pinit annotation helpers (pin, highlight, note). |
| `references/layout-patterns.md` | When-to-use router + copyable snippets. |
| `references/style-tokens.md` | Palette vocabulary, touying slot mapping, per-theme values. |
| `scripts/scaffold.py` | Scaffolds a self-contained deck (copies the zoo next to `<name>.typ`). |

## Extending the zoo

1. Add a gadget to `zoo/gadgets.typ` inside `make(pal)` — return it as a
   `"snake_case": (args) => …` entry so it destructures cleanly.
2. Add its swatch to `gallery.typ` under the matching section.
3. Recompile `gallery.typ`; if it renders, the gadget ships.
4. Document it in `references/layout-patterns.md`.

For a new theme, see "Adding a new theme" in `references/style-tokens.md`.
