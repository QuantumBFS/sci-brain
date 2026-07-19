# Neutral-atom autoresearch smoke test — design

**Date:** 2026-07-19
**Status:** User-approved design, pre-implementation
**Target:** `QuantumBFS/sci-brain` autoresearch skill family
**Research project:** `AtomicQCPlatformData`

## Goal

Exercise the complete autoresearch pipeline on a small, real neutral-atom
dataset:

1. choose and metricize a machine-checkable research topic;
2. build the literature and implementation evidence base;
3. build and self-test a sealed validator;
4. run one autonomous research cycle with three attempts;
5. use the observed friction to improve the skills;
6. produce ten additional metricized topics suitable for undergraduate
   training; and
7. submit the validated skill changes as a pull request to
   `QuantumBFS/sci-brain`.

The smoke test is not allowed to claim that a total gate infidelity uniquely
identifies a coherent error. It must preserve the project's distinction among
estimable quantities, scenario bounds, and unidentifiable parameters.

## Chosen smoke-test topic

**Robust recovery of microwave Rabi frequency and envelope dynamics from a
sparse processed population scan.**

The source is the official CaltechDATA record
`10.22002/4m9sp-yzr58`, specifically:

- `fig4a_rabi_duration.npy`;
- `fig4a_rabi_pop_1.npy`; and
- `fig4a_rabi_pop_1_std.npy`.

These three 768-byte arrays contain durations, processed state-\(|1\rangle\)
populations, and one-standard-deviation uncertainties used for Fig. 4a of
Manetsch et al., *Nature* 647, 60–67 (2025),
DOI `10.1038/s41586-025-09641-4`.

This is a processed-population inference task. It does not claim raw
shot-level inversion.

## Topic suitability

| Criterion | Score | Rationale |
|---|---:|---|
| Checkable | 5 | A validator can compute held-out predictive error and reject invalid outputs. |
| Cheap | 5 | Each fit uses tens of scalar observations and must finish within 30 seconds. |
| Headroom | 4 | Attempts can vary envelope families, weighting, robust losses, parameterizations, and search strategies. |
| Publishable | 3 | A single scan is a method smoke test, not a paper; the reusable bar is robust recovery under predefined sparse/noisy regimes. |

## Approved metrics

### Primary metric

**Uncertainty-normalized held-out RMSE**, minimized:

\[
\operatorname{NRMSE}_{\sigma}
=
\sqrt{\frac{1}{N}
\sum_i
\left(\frac{\widehat p_i-p_i}{\max(\sigma_i,\sigma_{\min})}\right)^2}.
\]

The validator reports this scalar on development instances. The held-out query
returns aggregate pass/fail only. The smoke-test goal is a development score
below the trivial undamped-sinusoid baseline and a final held-out score below
the threshold fixed in `research/validator/GOAL.md` before attempts begin.

### Guard metrics

- Every requested instance ID has exactly one finite prediction.
- Every predicted population is in \([0,1]\).
- The submitted Rabi frequency is positive and lies inside the predefined
  physically plausible search interval.
- The candidate passes unseen-instance and perturbed-grid checks; a lookup
  table keyed by public row or instance IDs is rejected.
- Runtime is at most 30 seconds per scored invocation.
- Candidate execution has no network access and cannot read the private
  benchmark or validator-private files.

## Pipeline layout

The smoke test runs in a clean, isolated git worktree derived from
`AtomicQCPlatformData`. The current user worktree and its uncommitted files are
not modified.

The target project produces the standard suite artifacts:

```text
topics.md
research/
  STATE.md
  CATALOG.md
  INSIGHTS.md
  database/
  benchmark/
    dev/
    private/
  validator/
    GOAL.md
    manifest.json
    controls/
docs/discussion/
.knowledge/
.worktrees/attempt-NNN/
```

The three source arrays are recorded with the CaltechDATA URL, DOI, file MD5,
and acquisition date. Public source bytes are immutable inputs. A deterministic
conversion step creates the visible development instances. A separate sealing
step creates private perturbed-grid instances without printing their labels
into the research-design context.

## Evidence-base stage

The evidence map covers:

1. driven two-level population dynamics and parameter identifiability;
2. damping/envelope model selection for Rabi oscillations;
3. uncertainty-weighted and robust nonlinear fitting;
4. leakage between model selection and held-out evaluation; and
5. neutral-atom microwave-control inhomogeneity and coherent-control error.

Each selected insight must cite a rendered reference in `.knowledge/INDEX.md`.
For this smoke test, the user pre-authorized all five insight areas above as
`## Selected`. The catalog must reproduce at least the trivial undamped
baseline; other entries may be `pinned` or `paper-only` only when their status
is explicit.

## Validator design

Docker is unavailable on the test machine. The approved fallback is:

- pinned CPython 3.9 standard-library execution;
- macOS `sandbox-exec` with reads limited to the candidate, public input, and
  pinned interpreter/runtime files, no network, a scrubbed environment, and
  read-only input;
- parent-enforced 30-second wall-clock timeout;
- validator-private scorer and holdout files outside attempt worktrees; and
- a manifest that records the fallback reason, interpreter identity, sandbox
  policy hash, source-data hashes, holdout query budget, and self-test results.

The CLI implements the published contract:

```text
validate <candidate-dir> [--precheck] [--instances dev|holdout]
         [--out report.json]
```

The validator gate requires:

- a baseline end-to-end development score;
- rejection of `cheater`, `wrong-answer`, `timeout`, and `env-escape`;
- rejection of a topic-specific public-row lookup-table control;
- an informative `errors[]` entry for every rejection; and
- no more than five-percent timeout overshoot.

If the platform cannot make validator-private files inaccessible to the
candidate process, the gate fails. A prompt-only “do not read” instruction is
not an acceptable fallback.

## Research-loop design

`research/STATE.md` is configured with:

- `batch_size: 3`;
- `time_limit_seconds: 30`;
- `authorized_rounds: 1`;
- one holdout aggregate query available for the cycle; and
- attempts numbered from `001`.

Before creating attempt worktrees, all public pipeline artifacts required by a
candidate are committed as an immutable baseline. `.worktrees/` is ignored.
Every attempt branch records its exact base commit.

The batch contains:

- at least one distinct draft;
- at least one single-change improvement over the best known baseline; and
- at most one debug attempt.

Each attempt writes `LOG.md` before implementation, runs `--precheck`, receives
exactly one development score, and records the complete JSON result. Crashes
and timeouts consume an attempt. The cycle ends with an honest yield report in
`docs/discussion/`, including the denominator, best score, causal interpretation,
dead approaches, holdout use, and distance to the goal.

## Ten-topic undergraduate reserve

A separate deliverable, `examples/neutral-atom-autoresearch-topics.md`, contains
exactly ten topics. Each topic includes:

- a concrete research question;
- at least one current primary reference showing an open method or modeling
  gap;
- Checkable, Cheap, Headroom, and Publishable scores with justifications;
- one primary metric and at least one guard metric;
- per-attempt cost;
- required dataset or simulator;
- principal gaming risk and its negative control; and
- recommended undergraduate prerequisites.

All ten topics must score at least 3 on Checkable and Cheap. Topics that only
repackage data collection, require private hardware, or need multi-day
simulation per attempt are excluded.

## Expected skill improvements

Only friction reproduced by the smoke test is changed. The initial audit will
specifically test these suspected protocol gaps:

1. whether a new-project dispatcher initializes portable state without
   assuming a platform-specific `AskUserQuestion` tool;
2. whether the validator's “scorer unreachable” rule is compatible with its
   prescribed repository layout;
3. whether attempt worktrees receive a committed public baseline and an
   explicit parent ref;
4. whether `.worktrees/` is ignored before creation;
5. whether pre-authorized stage choices can be consumed without repeated
   blocking prompts; and
6. whether structural tests verify the operational invariants rather than
   only marker phrases.

Each accepted fix gets a failing regression test first. Unreproduced concerns
remain documented findings, not speculative edits.

## Error handling

- Source download failure: retry the three exact CaltechDATA file URLs, verify
  MD5, then stop rather than substitute synthetic data silently.
- NPY incompatibility: reject unsupported dtype/shape with a specific error;
  do not coerce silently.
- Missing Docker: use the recorded `sandbox-exec` fallback above.
- Sandbox self-test failure: validator gate remains closed.
- Dirty or uncommitted attempt baseline: run stage refuses to create a
  worktree.
- Existing unrelated test failures: report separately and require the focused
  autoresearch regression suite to remain green.
- GitHub upstream lacks push permission: push the PR branch to a user-owned
  fork and open a PR against `QuantumBFS/sci-brain:main`.

## Verification

Completion requires all of the following evidence:

1. the dispatcher routes the isolated project through `topics`, `db`,
   `validator`, `run`, and `done`;
2. all survey and validator gate artifacts exist and agree with `STATE.md`;
3. every negative control is rejected as specified;
4. three attempt worktrees and three complete `LOG.md` files exist;
5. one reflection report records the three-attempt yield;
6. the ten-topic reserve has exactly ten fully metricized entries backed by
   primary references;
7. focused autoresearch tests pass;
8. the repository-wide test delta introduces no new failure beyond the seven
   failures present at baseline (111 passed, 7 failed);
9. the PR diff contains only reproduced skill fixes, their tests, the example,
   and the worktree-ignore rule; and
10. the pushed branch and pull request are inspectable on GitHub.
