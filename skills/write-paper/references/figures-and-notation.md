# Figures and notation

Use only the rulebook relevant to the current artifact. Venue requirements and
scientific meaning determine how these defaults apply.

## Figure Rulebook

Figures are what readers remember; design them to survive the harshest viewing context.

**Design for the intended display.** Use the target paper, slide, or print dimensions. Add grayscale-safe encodings when the venue or audience needs them.

**Line weight.** Judge curves at final display size, using explicit units or plotting-library parameters. A single numeric width is not portable across renderers.

**Color discipline.** Choose legible colors and redundant encodings at the intended size. The following are useful defaults, not a required palette.
- Use saturated, robust colors: black, blue, red, dark orange, magenta, violet, dark brown.
- Avoid light yellow, light green, light grey — invisible when projected.
- Encode the distinction with a *line style* (solid / dashed / dash-dot) in addition to color, so the figure survives greyscale printing.
- In the caption, refer to features by line style, not color: "the dashed curve" not "the red curve". Add "(Color online)" if color matters.

**Text size.** Axis labels, numbers, and legend text should not be much smaller than the surrounding paper text — at most 2/3 of body size. Tiny text wrecks the figure for talks.

**Parameter labels.** Place key parameters (e.g., `T = 0`, `V = 0`, `Γ = 1`) directly inside the plot in small boxes. Saves caption length and makes the figure self-contained for talks.

**Dimensionless axes.** Use dimensionless quantities (`G/G₀`, `T/Γ`, `V_g/Γ`, etc.) whenever possible — they generalize the result, clarify the relevant scale, and travel across systems. Choose the combination that maximizes message clarity; if you find a better one after plotting, replot. Exception: comparison with dimensional experimental data.

**Data vs. theory.** Plot data as points (with error bars) and theory as lines, on the same axes. A transformation that straightens a predicted relationship may help readers judge agreement. Keep transformations scientifically interpretable; straightening a theory curve is optional.

**Error-bar reasoning.** Compare residuals against the stated uncertainty model, accounting for what each interval represents and any correlations. Patterns to investigate:
- Unexpected residual patterns relative to the uncertainty model → investigate model mismatch or systematic error.
- Residuals unexpectedly small relative to the uncertainty model → investigate uncertainty estimates, correlations, or overfitting; this alone does not establish an error.

**Captions.** Concise but self-sufficient. Define every plotted quantity, summarize the trend, identify line styles. A reader who reads only the title, abstract, and figures+captions should get the paper.

**Explain every striking feature.** Every peak, dip, kink, or jump that catches the eye must be discussed in the main text — ideally with a back-of-envelope reason. Unexplained features are either an honesty problem or a missed opportunity. If you genuinely don't understand a feature, say so in print and flag it for follow-up.

---

## Notation Rulebook

Notation is the reader's interface to the math. Treat it with the same care as a public API.

- **No symbol reuse in nearby sections.** Same letter must not mean two different things within a few pages.
- **If notation must change, signal it explicitly.** "Henceforth we use X to denote..." — never silent reuse.
- **Define every variable before using it.** Define them in logical order: earlier symbols define later ones, never the reverse.
- **If a better notation appears mid-project, switch and rewrite earlier sections.** The reader's cost of decoding bad notation is far higher than your cost of rewriting.
- **Compact vs. explicit formulas:**
  - *Compact* when summarizing strategy, manipulating reader's high-level model, or when an expert could fill in the steps.
  - *Explicit* when: highlighting a non-obvious step, presenting a trick that took real effort, showing a key intermediate result other work depends on, presenting a flagship result, or matching a plotted figure (cite the figure in the equation).

---
