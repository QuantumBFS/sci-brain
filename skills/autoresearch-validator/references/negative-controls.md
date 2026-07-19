# Negative controls — validator strictness self-test

The validator gate requires the validator to *reject* all four controls
below, each with an informative `errors[]` entry. Controls live in
`research/validator/controls/<name>/` as runnable candidate directories;
self-test results are recorded in `research/validator/manifest.json`.

| control | what it does | validator must |
|---|---|---|
| `cheater` | returns hard-coded answers for the dev instances (e.g. a lookup table keyed on instance id or input hash) | reject: guard metrics / unseen-instance check catches it |
| `wrong-answer` | runs plausibly but returns an incorrect result on ≥1 instance | reject: exactness check fails, error names the instance and the wrong value |
| `timeout` | busy-loops past the wall-clock limit | mark `timeout` on the instance, enforce the limit with margin <5% overshoot, score accordingly |
| `env-escape` | attempts network access or reads outside the candidate dir (e.g. tries to open the holdout labels) | reject: the environment blocks it and the report says what was attempted |

Rules:

- Controls are written *before* the first real attempt and kept working; a
  validator change that stops rejecting any control re-opens the gate.
- Each control's rejection report is pasted into `manifest.json` under
  `"self_test"` with the date it last passed.
- When gaming risks in `topics.md` metrics suggest topic-specific cheats,
  add a fifth-plus control per risk — the four above are the floor.
