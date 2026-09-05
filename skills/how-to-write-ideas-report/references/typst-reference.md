---
description: Use when editing Typst files — covers general patterns, CeTZ drawing, plotting, and utility functions
globs: ["*.typ"]
---
# Typst Editing Reference

Reference files: ~/Documents/private-note/notes/typst-learn/ (typst-tricks.typ, typst-drawing.typ, typst-my-utils.typ)

## General Typst Patterns

### Page Setup
- Standalone figures: `#set page(width: auto, height: auto, margin: 5pt)`
- Standard notes: `#set page(margin: 2cm)` + `#set text(size: 10pt)` + `#set heading(numbering: "1.1.")`
- Numbered equations: `#set math.equation(numbering: "(1)")`

### Common Packages
- CeTZ: `@preview/cetz:0.4.0`, `@preview/cetz-plot:0.1.2`
- Algorithms: `@preview/algorithmic:1.0.3` — `Function`, `For`, `While`, `If`, `ElseIf`, `Else`, `Assign`, `Return`, `Comment`
- Math: `@preview/physica:0.9.3` (physics notation), `@preview/ouset:0.2.0` (over/under sets)
- Theorems: `@preview/ctheorems:1.1.2` or `@preview/unequivocal-ams:0.1.2`
- Random: `@preview/suiji:0.3.0` — `gen-rng(seed)`, `uniform(rng, size: n)`, `shuffle(rng, arr)`

### Math Notation
- Bra-ket: `$|psi chevron.r$`, `$chevron.l phi|$`
- Blackboard bold: `$bb(I)$`, calligraphic: `$cal(E)$`
- Accents: `$hat(N)$`, `$tilde(H)$`, `$overline(X)$`
- Cases: `$ f(x) = cases(x^2 &"if" x > 0, 0 &"otherwise") $`
- Matrices with ellipses: `$mat(a, dots; dots.v, dots.down;)$`

### Citations
- Inline: `@Author2024`, with locator: `@Author2024[Ch. 4]`
- Prose: `#cite(<Author2024>, form: "prose")`
- Compact slides style: `#set cite(style: "author-journal-year.csl")`

### Functional Idioms
- `range(n).map(_ => 0)` — zeros array
- `a.zip(b).map(((x, y)) => ...)` — pairwise ops
- `for (k, (i, j)) in pts.enumerate() { ... }` — destructuring enumerate
- `dict.at(key, default: 0)` — dict with default

### Content Helpers
- Infobox: `rect(stroke: color, inset: 8pt, radius: 4pt, width: 100%, [*Title:*\ body])`
- Inline image alignment: `box(image(...), baseline: (size - 20pt) / 2 + offset)`
- Image clipping: `box(clip: true, img, inset: (top: -top, bottom: -bottom, ...))`
- Two columns: `grid(columns: (1fr, 1fr), gutter: 20pt, left, right)`

## CeTZ Drawing

### Core Rules
1. **Name all objects** that will be referenced later: `circle(..., name: "c")`, `line(..., name: "edge")`
2. **Connect objects by name + anchor**, never by raw coordinates: `line("a.east", "b.west")`, not `line((2, 0), (5, 0))`
3. **Use `set-origin`** for sub-figures instead of manual coordinate offsets
4. **Use `on-layer`** for layering: -1 for backgrounds, 0 for main content, 1 for labels
5. **Use `content()` with `frame: "rect"`** for labeled boxes; use `fill: white, stroke: none` for edge labels
6. **Inside CeTZ functions**, always `import draw: *` for unqualified access

### Gotchas
- **`arc`**: first parameter is the **start point** of the arc, not the center of the circle
- **`bezier`**: first two args are **start and end points**; remaining args are control points
- **Arrows**: prefer `mark: (end: "straight")` style — do NOT use `">"`
- **Stroke dict**: use `(paint: color, thickness: 1pt, dash: "dashed")` — NOT `stroke(...)` constructor

### Quick Reference
- Shapes: `circle`, `rect`, `line`, `arc`, `bezier`, `hobby`, `catmull`, `merge-path`, `grid`
- Anchors: `"name.north"`, `.south`, `.east`, `.west`, `.center`, `.start`, `.mid`, `.end`
- Coordinates: `(x, y)`, `(rel: (dx, dy), to: "name")`, `("a", 50%, "b")`, `("a", "|-", "b")`
- Marks (arrows): `"straight"`, `">"`, `"stealth"`, `"|"`, `"o"`, `"<>"`, `"hook"`, `"]"`
- Strokes: `(dash: "dashed")`, `(dash: "dotted")`, `(dash: "dash-dotted")`, `2pt + red`
- Colors: `blue.lighten(60%)`, `green.darken(20%)`, `rgb("#f0f0fe")`
- Decorations: `decorations.brace`, `.flat-brace`, `.zigzag`, `.wave`, `.coil`
- Trees: `tree.tree((...), direction: "down", grow: 1.5, spread: 1.8)`

### Drawing Patterns
- **Graph rendering**: name vertices as `str(k)`, connect with `line(str(k), str(l))`
- **Circular layout**: use `vrotate(v, theta)` helper to place vertices on a circle
- **Edge labels**: `content("edge.mid", label, fill: white, frame: "rect", padding: 0.08, stroke: none)`
- **Data-driven diagrams**: store layout as list of tuples, iterate with `for` loops
- **Tensor networks**: `tensor` (circle + label), `deltatensor` (small filled dot), `labeledge` (line + midpoint label)
- **Intersections**: `intersections("ix", { ...shapes... })` then reference `"ix.0"`, `"ix.1"`

## CeTZ Plotting
- `plot.plot(size: (w, h), axis-style: "scientific", x-tick-step: 1, y-tick-step: 2, { ... })`
- Line: `plot.add(domain: (a, b), x => f(x), label: $f$, style: (stroke: blue))`
- Data: `plot.add(data, mark: "o", line: "spline")` — line types: `"linear"`, `"spline"`, `"vh"`, `"hv"`
- Scatter marks: `"*"`, `"o"`, `"square"`, `"triangle"`, `"+"`, `"|"`, `"-"`, `"<>"`
- Fill between: `plot.add-fill-between(f, g, domain: (a, b))`
- Reference lines: `plot.add-hline(y)`, `plot.add-vline(x)`
- Annotations: `plot.add-anchor("name", (x, y))`, `plot.annotate({ ... })`
- Bar chart: `chart.barchart(data, size: ..., mode: "clustered", labels: (...))`
- Pie chart: `chart.piechart(data, inner-radius: 0.5, outer-label: (content: auto, radius: 130%))`
