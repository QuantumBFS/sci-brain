---
name: write-slides
description: User trigger. Use when building a Typst + Touying slide deck for a scientific talk, lecture, or briefing.
---

## Installed resources

Keep the working directory at the user's project. Resolve this loaded `SKILL.md`
with `Path(path).resolve()` before locating resources; follow symlinks. A path
written as `skills/<name>/...` means the installed `<name>` skill's directory from
the agent's skill catalog. Locate dependencies by public skill name.

The slide template, gallery, layouts, and style documentation come from
[GiggleLiu/sci-brain-slides](https://github.com/GiggleLiu/sci-brain-slides).
Use release **v0.1.0**, package **@preview/sci-brain-slides:0.1.0**, with Typst
**0.14.0 or newer**. Check `typst --version` and `typst fonts`; the upstream
starter uses DejaVu Sans, with math and monospace fonts bundled with Typst.

# Write scientific slides

Build a PDF talk from an agreed outline, using the upstream template's `setup()`
API. The upstream repository owns the slide components and their tests. This
skill owns the research context, presentation workflow, and final deck review.
For an actual manuscript, use `write-paper`; for an in-paper figure, use
`how-to-review-figure` with the figure's authoring tools.

## 1. Load context and agree the outline

Read the relevant manuscript or `docs/discussion/*-brainstorm-ideas-log.md`.
Resolve the project KB using `how-to-download-ref` when needed. Reuse figures
from `$KB/.figures/`, the manuscript, or earlier talks, and verify that claims
and citations match the source.

Capture the topic, audience, talk duration, and main claim. Propose sections with
one claim and a figure idea for each. Get outline approval before composing the
deck; an already approved outline can be reused.

## 2. Initialize the upstream template

The v0.1.0 GitHub release is available, but its public Typst registry package was
not available when this workflow was verified. Install the tagged repository in
an explicit local package directory. This uses Typst's native package mechanism:

```sh
SLIDE_PACKAGES="${XDG_CACHE_HOME:-$HOME/.cache}/sci-brain/typst-packages"
SLIDE_TEMPLATE="$SLIDE_PACKAGES/preview/sci-brain-slides/0.1.0"
git clone --branch v0.1.0 --depth 1 \
  https://github.com/GiggleLiu/sci-brain-slides.git "$SLIDE_TEMPLATE"
mkdir -p slides
typst init @preview/sci-brain-slides:0.1.0 slides/my-talk \
  --package-path "$SLIDE_PACKAGES"
```

Set `SLIDE_PACKAGES` again in each new shell that compiles the deck. If the
checkout already exists, verify its origin and revision before reusing it;
v0.1.0 was verified at `ba4085986c422249a4f0a550656c8f9e26de2565`. Use a new deck
directory rather than overwriting an existing talk. Record the package version
and compile command alongside the deck so collaborators can repeat the setup.
Once the same version is published in Typst's registry, the local checkout and
`--package-path` are optional.

Read `$SLIDE_TEMPLATE/docs/layout-patterns.md` and
`$SLIDE_TEMPLATE/docs/style-tokens.md` for the API and design examples matching
this release. Browse `$SLIDE_TEMPLATE/docs/gallery.pdf`, or compile the gallery:

```sh
typst compile "$SLIDE_TEMPLATE/gallery.typ" /tmp/sci-brain-slides-gallery.pdf \
  --package-path "$SLIDE_PACKAGES" --input theme=academic
```

## 3. Choose the theme and compose slides

Use `academic` by default; `dark` for a dark presentation background, `minimal`
for a restrained monochrome deck, `vibrant` for colorful teaching material, or
`brand` with an explicit primary color. Keep one theme throughout the talk.
The generated `main.typ` reads `theme` and `text-size` from CLI inputs.

The package binds colors, typography, layouts, and gadgets together:

```typst
#import "@preview/sci-brain-slides:0.1.0": *

#let deck = setup(theme: "academic", text-size: 22pt)
#let (twocol,) = deck.layouts
#show: deck.theme.with(config-info(
  title: [Talk title], author: [Your name], institution: [Your lab],
))
#title-slide()

== State the result in the slide title
#twocol([The evidence.], [What the evidence establishes.])

#focus-slide[The main takeaway.]
```

Bind only the layouts and gadgets used by the talk. `deck.palette` supplies
colors and `deck.sizes` supplies typography. For a custom brand, use
`setup(theme: "brand", primary: rgb("#aa1e2b"), text-size: 22pt)`.

| Slide purpose | Upstream layout or component |
|---|---|
| Figure with interpretation | `spread` and `figbox` |
| Comparison | `twocol` or `threecol` |
| Main equation or statement | `hero` |
| Related concepts | `cards` |
| Results table | `data_table` |
| Definition or theorem | `definition` or `theorem` |
| Closing statement | `focus-slide` |

`==` starts a content slide; `=` starts a section divider. Use `#pause` for
stepwise reveals. Pass image content such as `image("figures/result.svg")` to
image helpers so paths resolve relative to the talk. Optional diagrams and
annotations use the upstream `cetz-gadgets()` and `pin-gadgets()` APIs; consult
the release's layout guide before using them.

## 4. Compile and review

Compile from the project root so project figures and the canonical bibliography
remain accessible to the deck:

```sh
typst compile slides/my-talk/main.typ slides/my-talk/main.pdf \
  --root . --package-path "$SLIDE_PACKAGES" \
  --input theme=academic --input text-size=22
```

Inspect the rendered pages, including all reveals. Check that each title states
its slide's claim, figures and equations are legible, captions explain how to
read the evidence, and no content overflows. Split or shorten an overfull slide;
the template does not automatically shrink text. Keep emphasized quantities
with their units and use the source's own figures when available.

Run `how-to-review-figure` on figure-heavy slides. If the talk needs a
bibliography, use the resolved `$KB/references.bib`, with a path relative to the
`.typ` file. Report the source and PDF paths, package version, build command,
and any verification that could not be completed.

## Template changes and existing decks

Report template defects and propose component changes in
[the upstream repository](https://github.com/GiggleLiu/sci-brain-slides).
Keep template source and API documentation there rather than copying them into
this skill. Existing talks with their own `zoo/` copy can still compile; migrate
those talks individually to the package import and `setup()` API when requested.
