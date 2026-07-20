# Neutral-atom Rabi autoresearch smoke test

This example records a complete `autoresearch` run:

1. `autoresearch-topics` selected robust Rabi carrier/envelope recovery;
2. `autoresearch-db` built a five-paper evidence base and passed the survey
   gate;
3. `autoresearch-validator` built a sealed scorer, passed the validator gate
   against four negative controls, and froze an undamped baseline score;
4. `autoresearch-run` executed attempt-001 through attempt-003 in separate
   branches, reflected on the batch, and spent one aggregate holdout query.

The source is the open Fig. 4a processed population scan from CaltechDATA DOI
[`10.22002/4m9sp-yzr58`](https://doi.org/10.22002/4m9sp-yzr58). These are
processed populations and uncertainties, not raw bitstrings.

## Reproduction outline

- Download the three files in `source-manifest.json` and verify their MD5
  hashes.
- Fit the frozen undamped weighted sinusoid on the even-index development
  rows and score odd-index predictions with an uncertainty floor of `1e-4`.
- Compare a Gaussian frequency-spread envelope and an exponential envelope
  under the same frequency bounds and output guards.
- Keep the scorer and holdout outside candidate worktrees; run the cheater,
  wrong-answer, timeout, and environment-escape controls before scoring.
- Use development scores to select one winner, then consume at most one
  aggregate holdout query and write a cycle reflection.

The original run used CPython 3.12.13 with macOS `sandbox-exec` because Docker
was unavailable. The fallback and its policy hash were recorded rather than
silently substituted.
