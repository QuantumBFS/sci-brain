# Figure-taste rubric

The 18-rule rubric backing `figure-taste/SKILL.md`, expanded into checkable items. Use it as the per-figure checklist while scoring. **G-rules apply to every figure; S-rules add on only for scientific plots.** Numbering is stable — scientific IDs skip S4/S6/S10 (axes-with-units, honest-axes, show-uncertainty were considered and not selected; keep the gaps if added later).

Each rule lists what a **pass** looks like, then a **Flag when** line for what to catch. Score every applicable rule `pass` / `warn` / `fail` and attach a severity (high / med / low) to anything that is not a pass.

---

## General rules — apply to every figure

### G1 — Alignment

- [ ] Elements line up on a shared grid; edges and baselines agree.
- [ ] Labels align with the things they label; columns/rows of items share an axis.
- [ ] Nothing sits at a slightly-off offset that reads as a mistake.

**Flag when:** items are eyeballed rather than gridded; text baselines or box edges are a few pixels out of true.

### G2 — Proximity

- [ ] Conceptually related elements are physically close; a label sits nearest the thing it names.
- [ ] Unrelated groups are separated by clearly larger gaps than within-group spacing.
- [ ] Whitespace encodes grouping (the eye reads clusters correctly without a legend).

**Flag when:** a label is closer to the wrong element; related items are scattered; group gaps and item gaps are indistinguishable.

### G3 — Edge padding

- [ ] Text and content keep a consistent margin from the figure boundary.
- [ ] No glyph, arrowhead, or marker kisses or crosses the frame.
- [ ] Padding is even on opposing sides unless asymmetry is intentional.

**Flag when:** text crowds an edge; content is clipped; one side is tight while the opposite is loose.

### G4 — Unified color

- [ ] A limited, coherent palette (a small set of hues plus neutrals).
- [ ] Color is used to mean something, not for decoration.
- [ ] Hues are harmonious; no clashing or fully saturated rainbow.

**Flag when:** too many competing colors; default rainbow/categorical palette used where a sequential or 2–3-color set would do; saturation is uniformly maxed.

### G5 — Clear focus

- [ ] The single most important element is the most salient.
- [ ] Highlights (bold color, heavy weight, callouts) are few and reserved for what matters.
- [ ] Secondary/context elements are visually demoted (muted, thinner, smaller).

**Flag when:** everything is highlighted (so nothing is); the key result competes with decoration; no clear visual entry point.

### G6 — Reading order / hierarchy

- [ ] There is an obvious place for the eye to start and a clear path onward.
- [ ] Size/weight/position encode importance consistently (a real hierarchy).
- [ ] Flow follows a sensible order (left→right, top→down, or guided by arrows).

**Flag when:** the eye does not know where to begin; equal weight on unequal-importance items; the intended sequence is ambiguous.

### G7 — Consistent sizing & spacing

- [ ] Same-type elements share a size (all subpanels, all icons, all boxes).
- [ ] Gutters and margins between repeated elements are uniform.
- [ ] Stroke widths and corner radii are consistent across like elements.

**Flag when:** sibling panels differ in size; gaps vary without reason; mixed stroke weights/radii on the same class of element.

### G8 — Contrast & legibility

- [ ] Text contrasts strongly with its background; lines stand out from the canvas.
- [ ] No light-gray-on-white or color-on-similar-color that is hard to read.
- [ ] Important marks are not lost against a busy or dark background.

**Flag when:** low text/background contrast; data lines blend into gridlines or fill; labels disappear over an image/heatmap.

### G9 — Colorblind / grayscale-safe

- [ ] No distinction depends on red-vs-green (or other CVD-confusable pairs) alone.
- [ ] Categories are also separable by shape, linestyle, or position (redundant encoding).
- [ ] Converted to grayscale, the meaning survives.

**Flag when:** red/green is the only differentiator; series distinguished by hue alone; everything collapses to similar grays in B&W.

### G10 — No overlap / clipping / occlusion

- [ ] No text collides with lines, markers, or other text.
- [ ] Legend, labels, or annotations do not cover data.
- [ ] Nothing is cut off at the frame; tick labels are fully visible.

**Flag when:** overlapping labels; a legend sitting on top of the curves; truncated axis text or clipped panel content.

### G11 — Consistent typography

- [ ] One or two font families across the whole figure.
- [ ] A small set of sizes used as a deliberate hierarchy (title / label / annotation).
- [ ] Consistent casing, weight, and number formatting.

**Flag when:** mixed fonts; many arbitrary sizes; inconsistent capitalization or decimal formatting between labels.

---

## Scientific-plot rules — add on for plots (quantitative axes / data)

### S1 — Text large enough

- [ ] Axis labels, tick labels, and annotations are readable **at the intended display size** (from Phase 0).
- [ ] Text does not shrink below legibility when the figure is set to one column / one slide.
- [ ] Tick-label density does not force unreadably small type.

**Flag when:** at the target width, any text would be too small to read; default tiny matplotlib fonts on a column-width figure.

### S2 — Lines strong enough

- [ ] Data lines and marker edges have enough weight to read at display size.
- [ ] Primary curves are heavier than gridlines/axes, not thinner.
- [ ] Markers are large enough to distinguish.

**Flag when:** hairline data curves; gridlines heavier than data; markers too small to tell apart.

### S3 — Efficient use of space

- [ ] Data fills the frame; axis ranges are not far wider than the data.
- [ ] No large empty quadrants or wasted margins inside the axes.
- [ ] Subpanel layout uses the canvas without big dead zones.

**Flag when:** data huddles in one corner; padded-out axis limits leave broad blank areas; oversized inter-panel gaps.

### S5 — Minimize chartjunk

- [ ] No 3D effects, gradients, or decorative fills that carry no data.
- [ ] Gridlines are light and sparse (or absent); no redundant heavy borders.
- [ ] High data-ink ratio — ink mostly encodes data, not ornament.

**Flag when:** 3D bars/pies; dark dense gridlines; redundant frames/backgrounds; drop shadows and textures.

### S7 — Legend & direct labeling

- [ ] The legend is unambiguous and placed where it does not occlude data.
- [ ] With only a few series, lines are labeled directly instead of via a distant legend.
- [ ] Legend order matches the visual/used order of the series.

**Flag when:** legend covers the curves; many round-trips between legend and plot to decode colors; legend order scrambled vs. the data.

### S8 — Cross-panel consistency

- [ ] Comparable subpanels share axis ranges and scales (so they are visually comparable).
- [ ] The same quantity uses the same color/linestyle across panels.
- [ ] Panel labels (a)(b)(c) are present, consistently placed and styled.

**Flag when:** sibling panels use different y-ranges for the same quantity; a series changes color between panels; missing or inconsistent panel tags.

### S9 — Resolution / format adequate

- [ ] Vector format where the target allows; otherwise raster at sufficient DPI.
- [ ] No pixelation, blur, or JPEG artifacts at the intended display size.
- [ ] Line art stays crisp when scaled to the target width.

**Flag when:** a low-DPI raster used where vector was available; visible pixelation/blur at display size; compression artifacts around text/lines.

---

## Delivery

- [ ] Each figure was rendered and **looked at** before scoring (no unseen figures).
- [ ] Each figure classified general vs. scientific; S-rules applied only to plots.
- [ ] S1/S9 judged against the Phase-0 display context, not the on-screen size.
- [ ] A scorecard (rule → ✓/⚠/✗ → note), severity-ranked findings with concrete fixes, and a top-fixes list produced per figure.
- [ ] Subjective taste calls marked as opinion; the rest grounded in the raster or source.
- [ ] Nothing edited — suggestions only. File written only if the user asked (`figure-review-YYYY-MM-DD.md`).
