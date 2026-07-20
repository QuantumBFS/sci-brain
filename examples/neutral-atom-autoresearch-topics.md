# Neutral-atom autoresearch topic reserve

These ten scoped projects were screened with the `autoresearch-topics`
rubric. “Publishable” means the project can produce a reusable benchmark or
carefully bounded method result; it does not promise a new physics discovery.
Primary data sources are the open CaltechDATA record
[`10.22002/4m9sp-yzr58`](https://doi.org/10.22002/4m9sp-yzr58), the open
Zenodo records [`10.5281/zenodo.15685795`](https://doi.org/10.5281/zenodo.15685795)
and [`10.5281/zenodo.19491381`](https://doi.org/10.5281/zenodo.19491381), and
the primary articles linked below.

## Topic 01 — Robust Rabi carrier and envelope recovery

### Research question

Which bounded envelope family best predicts unseen state-\(|1\rangle\)
populations while preserving a stable microwave Rabi carrier?

### Evidence that the gap is open

CaltechDATA publishes 80 durations, processed populations, and one-sigma
uncertainties for Fig. 4a. The article reports a 24.611 kHz carrier and
attributes late-time decay to spatially varying Rabi frequency, but does not
provide a reusable held-out model-selection benchmark.

### Suitability

- **Checkable:** 5/5 — deterministic sealed-duration prediction.
- **Cheap:** 5/5 — 2.3 kB and seconds per fit.
- **Headroom:** 4/5 — envelope, weighting, constraints, and search choices.
- **Publishable:** 3/5 — strongest as a benchmark/method note.

### Metrics

- **Primary metric** — uncertainty-normalized RMSE on sealed durations.
- **Guard metric** — complete finite populations in `[0,1]`, carrier in a
  frozen physical interval, and unseen jittered-duration checks.

### Cost and resources

Standard-library Python is sufficient; 30 seconds and one CPU per attempt.

### Gaming risk and negative control

A row lookup can memorize the public scan. Randomize IDs and include
perturbed durations unavailable as exact source rows.

### Undergraduate prerequisites

Driven two-level systems, least squares, basic Python, and train/test splits.

## Topic 02 — Ramsey dephasing-family discrimination

### Research question

Can Gaussian, exponential, stretched-exponential, and site-mixture models be
distinguished using unseen Ramsey evolution times and sites?

### Evidence that the gap is open

The same CaltechDATA record publishes evolution times and a 431.9 MB
iteration-by-time-by-image-by-site presence tensor for Fig. 4b. The paper
reports different array-averaged and site-resolved \(T_2^*\), leaving a clear
model-selection and hierarchical-compression exercise.

### Suitability

- **Checkable:** 5/5 — held-out Bernoulli log loss by time and site.
- **Cheap:** 3/5 — data are moderate, but minibatched scoring is simple.
- **Headroom:** 5/5 — hierarchical, mixture, and robust dephasing models.
- **Publishable:** 4/5 — reusable site-aware benchmark if splits are frozen.

### Metrics

- **Primary metric** — sealed-site-and-time Bernoulli negative log likelihood.
- **Guard metric** — calibrated probabilities, coverage on unseen sites, and
  no site-ID lookup.

### Cost and resources

About 432 MB storage; CPU streaming with a memory ceiling below 2 GB.

### Gaming risk and negative control

Site memorization can look predictive. Seal entire sites and late times, then
test a candidate that keys only on site index.

### Undergraduate prerequisites

Ramsey interferometry, Bernoulli likelihoods, vectorized array processing.

## Topic 03 — Dynamical-decoupling contrast model selection

### Research question

Which constrained contrast-decay law best extrapolates the two analyzer-phase
branches of the Fig. 4c dynamical-decoupling scan?

### Evidence that the gap is open

CaltechDATA provides time, population, and uncertainty arrays for both final
phases; the paper quotes \(T_2=12.6(1)\) s but does not benchmark competing
finite-contrast and drift-aware observation models.

### Suitability

- **Checkable:** 5/5 — tiny arrays with uncertainty-aware holdout.
- **Cheap:** 5/5 — less than 1 kB.
- **Headroom:** 4/5 — shared/asymmetric envelopes and nuisance offsets.
- **Publishable:** 3/5 — a compact reproducibility and identifiability study.

### Metrics

- **Primary metric** — normalized RMSE on sealed times and phases.
- **Guard metric** — positive \(T_2\), phase-consistent contrast, populations
  in `[0,1]`, and parameter stability under leave-one-time-out fits.

### Cost and resources

No GPU; exhaustive small-model search fits within seconds.

### Gaming risk and negative control

Independent interpolation of each phase can violate shared physics. Include a
control that fits each branch separately and reject inconsistent contrast.

### Undergraduate prerequisites

Spin echo/dynamical decoupling, exponential models, uncertainty propagation.

## Topic 04 — Global randomized-benchmarking decay inference

### Research question

Can hierarchical sequence-to-sequence variation improve prediction of unseen
Clifford lengths over a single averaged exponential decay?

### Evidence that the gap is open

Fig. 4d source arrays expose length, return probability, uncertainty, and
random-sequence axes. The paper reports an average Clifford fidelity but the
public data support a checkable comparison of pooled and hierarchical
observation models.

### Suitability

- **Checkable:** 5/5 — seal complete random sequences and lengths.
- **Cheap:** 5/5 — roughly 15 kB.
- **Headroom:** 4/5 — heterogeneity, robust likelihoods, and finite-SPAM fits.
- **Publishable:** 4/5 — useful small-data RB benchmark.

### Metrics

- **Primary metric** — held-out normalized RMSE or beta-likelihood deviance.
- **Guard metric** — decay parameter in `[0,1]`, finite SPAM parameters, and
  accuracy on unseen sequence identities.

### Cost and resources

CPU-only, under one minute per attempt.

### Gaming risk and negative control

Memorizing each random string defeats interpolation. Seal whole strings and
include a per-string lookup-table control.

### Undergraduate prerequisites

Randomized benchmarking, exponential decay, hierarchical regression.

## Topic 05 — Transport survival surface with confidence bounds

### Research question

Which monotone or shape-constrained surrogate best predicts straight and
diagonal atom-survival probability at unseen move durations?

### Evidence that the gap is open

CaltechDATA Fig. 5a provides duration plus central/lower/upper survival
estimates for both geometries. The article reports optimized operation points,
not a benchmark of uncertainty-aware surrogate families.

### Suitability

- **Checkable:** 5/5 — duration holdout with explicit confidence intervals.
- **Cheap:** 5/5 — about 2.2 kB.
- **Headroom:** 4/5 — splines, constrained kernels, and mechanistic losses.
- **Publishable:** 3/5 — reusable surrogate-selection exercise.

### Metrics

- **Primary metric** — interval-normalized RMSE on sealed durations.
- **Guard metric** — survival in `[0,1]`, correct geometry labels, and
  prespecified smoothness/shape constraints.

### Cost and resources

Seconds per attempt with standard numerical tools.

### Gaming risk and negative control

High-order interpolation can oscillate between rows. Add midpoint queries and
reject out-of-range or excessive-curvature predictions.

### Undergraduate prerequisites

Probability, confidence intervals, interpolation, constrained optimization.

## Topic 06 — Coherence loss under transport

### Research question

Can a shared-phase observation model separate contrast loss from phase shift
between static and transported Ramsey fringes?

### Evidence that the gap is open

CaltechDATA Fig. 5b publishes analyzer phase and confidence-bounded
populations for static and transported cases. A single quoted transport
fidelity does not determine whether contrast, offset, or phase is responsible.

### Suitability

- **Checkable:** 5/5 — held-out analyzer phases.
- **Cheap:** 5/5 — about 1.1 kB.
- **Headroom:** 4/5 — coupled sinusoidal and circular-statistics models.
- **Publishable:** 3/5 — bounded observation-model result.

### Metrics

- **Primary metric** — confidence-normalized prediction error on sealed phases.
- **Guard metric** — periodic continuity, populations in `[0,1]`, and a
  bootstrap interval for transported/static contrast ratio.

### Cost and resources

CPU-only; bootstrap capped at a frozen number of resamples.

### Gaming risk and negative control

Phase-index interpolation ignores periodicity. Seal across the \(0/2\pi\)
boundary and test a nonperiodic spline control.

### Undergraduate prerequisites

Ramsey fringes, trigonometric regression, bootstrap confidence intervals.

## Topic 07 — Survival versus coherent return in repeated transport

### Research question

Can a joint observation model separate atom loss from conditional coherent
return across move duration and number of repeated moves?

### Evidence that the gap is open

CaltechDATA Fig. 5d publishes a duration-by-move-count survival tensor and
static/transported return probabilities with uncertainties. These observables
constrain different processes, but a unique microscopic channel is not
directly identifiable.

### Suitability

- **Checkable:** 5/5 — two-output sealed grid prediction.
- **Cheap:** 5/5 — about 2 kB.
- **Headroom:** 5/5 — joint hazards, conditional returns, and change points.
- **Publishable:** 4/5 — explicit identifiability-aware benchmark.

### Metrics

- **Primary metric** — weighted joint RMSE for survival and return probability.
- **Guard metric** — both outputs in `[0,1]`, nonnegative loss hazard, and
  correct performance on unseen duration/count combinations.

### Cost and resources

Small-grid CPU fitting under 30 seconds.

### Gaming risk and negative control

Multiplying two independent fitted curves can misstate conditional coherence.
Include that factorized model as a negative control and seal grid rectangles.

### Undergraduate prerequisites

Conditional probability, survival models, two-output regression.

## Topic 08 — Hand-designed versus ML transport-transfer trajectories

### Research question

Can a low-parameter model predict survival and return-probability trade-offs
for hand-optimized and ML-optimized static/dynamic tweezer transfers?

### Evidence that the gap is open

CaltechDATA Fig. 6d provides survival and return-probability arrays across
trajectory/duration choices and repeated transfers, including an ML-optimized
0.4 ms case. The open comparison supports a blinded surrogate benchmark.

### Suitability

- **Checkable:** 5/5 — seal a trajectory-duration family.
- **Cheap:** 5/5 — about 1.2 kB.
- **Headroom:** 4/5 — partial pooling, interaction terms, monotone hazards.
- **Publishable:** 4/5 — transparent ML-versus-hand-designed comparison.

### Metrics

- **Primary metric** — held-out joint normalized RMSE across move counts.
- **Guard metric** — calibrated uncertainty, valid probabilities, and no
  trajectory-name lookup.

### Cost and resources

CPU-only; candidate source capped at a small dependency lock.

### Gaming risk and negative control

The label “ML optimized” leaks rank. Replace names with randomized IDs and
include a candidate that predicts solely from the label as a control.

### Undergraduate prerequisites

Regression interactions, survival probability, experimental controls.

## Topic 09 — Gate-speed error-budget response fitting

### Research question

Which constrained response model best predicts CZ fidelity across Rabi speed
while separating frequency noise, intensity noise, decay, and rise/fall
effects only to the extent supported by published observables?

### Evidence that the gap is open

Tsai et al., *PRX Quantum* **6**, 010331 (2025), DOI
`10.1103/PRXQuantum.6.010331`, reports gate-speed sweeps, an ab-initio error
model, and fidelity-response scaling. Reproducing tables/curves still leaves
room for a compact held-out surrogate and a transparent identifiability audit.

### Suitability

- **Checkable:** 4/5 — blind selected speeds/table entries.
- **Cheap:** 4/5 — small published tables; no full many-body simulation.
- **Headroom:** 5/5 — scaling priors and constrained component models.
- **Publishable:** 4/5 — useful if digitization/provenance is released.

### Metrics

- **Primary metric** — held-out fidelity error across Rabi frequencies.
- **Guard metric** — nonnegative component infidelities, total-budget
  consistency, and explicit “bound-only” labels for nonidentifiable parts.

### Cost and resources

One-time table extraction; seconds to minutes per fit.

### Gaming risk and negative control

Residual infidelity cannot all be called coherent error. Reject candidates
that equate residual with a uniquely identified coherent channel; include
that overclaim as a semantic negative control.

### Undergraduate prerequisites

Rydberg CZ gates, error budgets, power laws, constrained regression.

## Topic 10 — Active pulse-time sampling for identifiability

### Research question

Given a fixed measurement budget, which next Rabi or Ramsey time most reduces
uncertainty between competing envelope families?

### Evidence that the gap is open

The open Fig. 4a/4c grids permit an offline pool-based active-learning
benchmark: hide most times, let a policy acquire labels sequentially, and
score on a permanently sealed set. The source articles optimize physical
operations, not this acquisition-policy comparison.

### Suitability

- **Checkable:** 5/5 — fixed acquisition budget and sealed final grid.
- **Cheap:** 5/5 — reuse sub-kilobyte processed arrays.
- **Headroom:** 5/5 — variance, disagreement, information-gain policies.
- **Publishable:** 4/5 — reusable small-data active-design benchmark.

### Metrics

- **Primary metric** — area under held-out error versus acquired-label curve.
- **Guard metric** — exact acquisition budget, no access to unqueried labels,
  deterministic seeds, and correct uncertainty coverage.

### Cost and resources

Hundreds of short CPU simulations; no laboratory access required.

### Gaming risk and negative control

An offline policy can accidentally inspect the full label pool. Serve labels
through a metered oracle and test a policy that directly opens the source
array; the sandbox must reject it.

### Undergraduate prerequisites

Experimental design, uncertainty, greedy algorithms, reproducible simulation.
