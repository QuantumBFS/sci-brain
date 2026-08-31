---
name: how-to-review-figure
description: Agentic trigger. Use when judging the visual design of a figure, plot, or diagram against a scientific-plot rubric.
---

# Figure Taste

Run a structured **visual-design review** over one or more figures and print a scorecard. The skill **renders the figure to a raster so it can see it**, reads the source (matplotlib `.py`, Typst `.typ`, SVG) so suggestions can name the exact line or parameter to change, scores it against an 18-rule rubric, and delivers severity-ranked findings with concrete fixes.

**Scope note.** This judges *how a figure looks* — the artifact itself. It is **not** `review-paper`, which checks whether figures are *referenced and discussed in the manuscript* (orphan figures, undiscussed features, caption sufficiency). It is **not** `write-paper`, which *authors* figures figures-first. Use `how-to-review-figure` when a figure already exists and the user wants its visual quality assessed. For the *why* behind a plotting convention, consult `write-paper`'s Figure Rulebook rather than restating it here.

The full rubric — each rule's "good looks like" and "flag when" — lives in `skills/how-to-review-figure/checklist.md`.

---

## Operating principle

**Source-aware, report-only, terminal-first.**

- **Source-aware** — always look at a rendered raster before scoring (never judge a figure you have not seen); when source exists, read it too so a fix can cite a line or parameter.
- **Report-only** — never edit the figure or its source. Suggest concrete changes; the user applies them.
- **Terminal-first** — print the scorecard to the chat by default. Write a file only when the user asks.

---

## The rubric — 18 rules

All **11 general rules** apply to every figure. The **7 scientific rules** add on when the figure is a scientific plot (quantitative axes / data series). Numbering is stable: scientific IDs skip S4/S6/S10 (axes-with-units, honest-axes, show-uncertainty were considered and not selected — keep the gaps if added later).

| ID | Rule | Applies to |
|----|------|-----------|
| G1 | **Alignment** — contents align to a shared grid / baselines, not eyeballed | all |
| G2 | **Proximity** — related elements are physically close; unrelated ones separated | all |
| G3 | **Edge padding** — text and content have breathing room from the boundaries | all |
| G4 | **Unified color** — a limited, coherent palette; not too colorful | all |
| G5 | **Clear focus** — the main message stands out; not too many competing highlights | all |
| G6 | **Reading order / hierarchy** — the eye knows where to start and go next; the key element reads first | all |
| G7 | **Consistent sizing & spacing** — same-type elements share size; gutters/margins are uniform | all |
| G8 | **Contrast & legibility** — text and lines stand out from their background | all |
| G9 | **Colorblind / grayscale-safe** — no meaning carried by red-vs-green alone; survives B&W | all |
| G10 | **No overlap / clipping / occlusion** — nothing collides, covers data, or is cut off at edges | all |
| G11 | **Consistent typography** — one or two font families; a small set of sizes as a hierarchy | all |
| S1 | **Text large enough** — readable at the intended display size | plots |
| S2 | **Lines strong enough** — data lines/markers have enough weight to read | plots |
| S3 | **Efficient use of space** — no large empty regions; data fills the frame | plots |
| S5 | **Minimize chartjunk** — drop 3D effects, heavy gridlines, redundant borders, decorative fills | plots |
| S7 | **Legend & direct labeling** — legend unambiguous and not occluding; prefer direct labels for few series | plots |
| S8 | **Cross-panel consistency** — comparable subpanels share scales/axes/colors; consistent (a)(b)(c) labels | plots |
| S9 | **Resolution / format adequate** — vector where possible; no pixelation or blur at display size | plots |

---

## Severity rubric

Rank every non-pass finding so the user can triage:

- **high** — breaks readability or meaning: illegible text at display size, clipped/cut-off content, meaning lost in grayscale (G9), data occluded by a legend, pixelated-to-unreadable.
- **med** — hurts clarity but not correctness: too colorful (G4), weak hierarchy/focus (G5/G6), inconsistent spacing (G7), chartjunk (S5), weak lines (S2), large blank areas (S3).
- **low** — polish: minor edge padding (G3), marker/typography inconsistency, an ambiguous-but-survivable legend.

---

## Phase 0 — Scope & render

1. **Resolve target(s).** Accept explicit path(s), a directory, or auto-detect (`images/`, `figures/`, then `*.png|jpg|jpeg|pdf|svg|typ` in the working directory). If several are found and the user did not name one, list them and ask which to review.
2. **Establish the display context.** Ask once (with a default): where will this figure appear — **paper single-column / paper double-column / slide / poster / web** — and the final width. This is what makes S1 (text size) and S9 (resolution) meaningful. **Default if unspecified:** paper double-column (~3.4 in wide).
3. **Render to a raster you can look at (source-aware).** Use the helper:

   ```bash
   python3 skills/how-to-review-figure/helpers/render.py <path> [--dpi 200] [--allow-exec]
   ```

   - raster (`.png`/`.jpg`) and `.pdf` → read directly (the helper passes them through).
   - `.typ` → compiled to PNG via `typst`.
   - `.svg` → converted to PNG via the first available of `rsvg-convert` / `inkscape` / `cairosvg`.
   - matplotlib `.py` → rendered **only** with `--allow-exec` (open figures captured to PNG). Confirm with the user before passing `--allow-exec`; otherwise prefer an already-rendered output, or ask for a PNG.
   - The helper prints the viewable PNG path(s) to stdout. If it fails (no renderer available), **ask the user to export a PNG** — do not score an unseen figure.

   Then **read the produced raster** with your image-reading ability. When the source exists, also read it as text so fixes can cite a line/parameter.
4. **Classify each figure** as **scientific plot** (quantitative axes / data series) or **general/schematic** (diagram, flowchart, conceptual art). State the classification so the user can override. General rules apply to all; scientific rules add on only for plots.

Do not score a figure before you have looked at its rendered raster.

---

## Phase 1 — Score against the rubric

For each figure, view the render (and source, if available) and rate every applicable rule. Each finding has this shape:

```
{ rule:      G1–G11 or S1–S9,
  rating:    pass | warn | fail,
  location:  where in the figure (panel, region, the offending element),
  observation: what you see, in one sentence,
  fix:       a concrete change — and the source line/parameter when source is available,
  severity:  high | med | low   (omit for pass) }
```

- Judge S1/S9 **against the Phase-0 display context**, not the on-screen render size.
- Ground each finding in something visible in the raster (or a line in the source). Where a call is subjective, say so rather than asserting.
- The per-rule "good looks like / flag when" detail is in `skills/how-to-review-figure/checklist.md` — walk it as you score.

---

## Phase 2 — Deliver

Print, per figure:

1. **Header** — file, classification (general / scientific), and the display context used.
2. **Scorecard table** — rule → rating (✓ / ⚠ / ✗) → one-line note.
3. **Severity-ranked findings** — high → low, each with its concrete fix.
4. **Top fixes** — a short prioritized list of the highest-leverage changes.

For a multi-figure run, add a brief cross-figure summary (shared problems, inconsistencies across the set).

Then **offer to save**: only on a yes, write `figure-review-YYYY-MM-DD.md` beside the reviewed figure(s) (or a path the user gives), using the same structure. This matches the repo's dated-output convention (cf. `review-paper`).

---

## Reused vs. new

**Reused:** the dated-output convention and severity-rubric shape from `review-paper`; `write-paper`'s Figure Rulebook for the *why* behind plotting conventions (referenced, not restated).

**New here:** the render-then-look protocol (Phase 0), the general/scientific classification gate, the 18-rule visual-design rubric, and `helpers/render.py` (normalize any figure input to a viewable PNG).

---

## Common mistakes

| Mistake | Instead |
|---|---|
| Scoring a figure you never rendered | Phase 0 step 3: render and look first; ask for a PNG if rendering fails. |
| Judging "text too small" with no context | Phase 0 step 2 fixes the intended display size before S1/S9. |
| Applying scientific rules to a schematic | Classify first; S-rules add on only for plots. |
| Editing the figure or its source | Report-only — suggest, never apply. |
| Running a matplotlib `.py` silently | Render `.py` only with `--allow-exec` after user confirmation; else use existing output or ask for a PNG. |
| Asserting a subjective taste call as fact | Mark subjective findings as opinion; ground the rest in the raster/source. |

---

## Integrations

- **Rendering / normalize-to-PNG:** `skills/how-to-review-figure/helpers/render.py`.
- **Full rubric checklist:** `skills/how-to-review-figure/checklist.md`.
- **Figure-text integration, captions, orphan figures:** `review-paper` (different concern).
- **Plotting-convention rationale:** `write-paper` Figure Rulebook.
