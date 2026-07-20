# Neutral-Atom Autoresearch Suite Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:executing-plans` to implement this plan task-by-task. Do not
> dispatch subagents: this thread's collaboration policy requires inline
> execution. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run the complete sci-brain autoresearch pipeline on official
neutral-atom Rabi data, improve only the skill defects reproduced by that run,
produce ten validator-ready undergraduate topics, and submit the verified
changes as a pull request.

**Architecture:** Skill changes are developed in the isolated
`codex/test-autoresearch-neutral-atom` worktree with grep-based regression
tests. The scientific smoke test runs in a separate clean clone of
`AtomicQCPlatformData`; its validator executes candidates through a
macOS-sandboxed, standard-library-only process, while private labels and scorer
code remain outside attempt worktrees. Reproducible public results and the
ten-topic reserve are copied into sci-brain as an example; private benchmark
material and attempt worktrees are not committed to the PR.

**Tech Stack:** Markdown skill protocols, Python 3.9 standard library,
`sandbox-exec`, Git worktrees, pytest 8.4.1 in a temporary dependency directory,
CaltechDATA NPY files, GitHub CLI/app.

## Global Constraints

- Preserve the full four-stage pipeline: topics → db → validator → run.
- Use the official CaltechDATA record `10.22002/4m9sp-yzr58`; do not silently
  replace missing public data with synthetic data.
- Describe Fig. 4a as processed populations, not raw shot-level bitstrings.
- Keep estimable quantities, scenario bounds, and unidentifiable parameters
  distinct.
- Use `batch_size: 3`, `time_limit_seconds: 30`, and
  `authorized_rounds: 1` for the smoke run.
- Every skill edit must be preceded by a focused failing regression test.
- Do not modify or clean the user's existing uncommitted
  `AtomicQCPlatformData` files.
- A validator sandbox failure keeps the validator gate closed.
- Do not add reviewers to the pull request unless the user asks.
- Treat the seven repository-wide baseline failures as pre-existing; introduce
  no additional full-suite failures.

---

### Task 1: Make installation and stage approvals portable

**Files:**
- Modify: `.codex/INSTALL.md`
- Modify: `skills/autoresearch/SKILL.md`
- Modify: `skills/autoresearch/references/state-schema.md`
- Create: `skills/autoresearch/references/approval-contract.md`
- Modify: `skills/autoresearch-topics/SKILL.md`
- Modify: `skills/autoresearch-db/SKILL.md`
- Modify: `skills/autoresearch-validator/SKILL.md`
- Test: `tests/test_autoresearch_skills.py`

**Interfaces:**
- Consumes: an exact user decision from the current conversation or
  `<project>/research/APPROVALS.md`.
- Produces: a portable approval lookup protocol and a valid Codex installation
  procedure that links every real skill directory.

- [ ] **Step 1: Write failing portability tests**

Append these tests:

```python
def test_codex_install_links_real_skill_directories():
    text = (ROOT / ".codex" / "INSTALL.md").read_text()
    assert "skills/sci-brain" not in text
    assert 'for skill in "$HOME/.codex/sci-brain/skills"/*' in text
    assert 'ln -sfn "$skill"' in text


def test_approval_contract_is_portable_and_auditable():
    contract = _ref("autoresearch", "approval-contract.md")
    assert "research/APPROVALS.md" in contract
    assert "current conversation" in contract
    assert "platform" in contract.lower()
    assert "pre-authorized" in contract
    assert "never infer" in contract.lower()


def test_interactive_stages_use_shared_approval_contract():
    for skill in [
        "autoresearch",
        "autoresearch-topics",
        "autoresearch-db",
        "autoresearch-validator",
    ]:
        text = _read(skill)
        assert "approval-contract.md" in text
    state = _ref("autoresearch", "state-schema.md")
    assert "approval_log:" in state
```

- [ ] **Step 2: Run the tests and verify failure**

Run:

```bash
PYTHONPATH=/private/tmp/sci-brain-test-deps \
  /Users/mingrui/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  -m pytest -q tests/test_autoresearch_skills.py \
  -k 'codex_install or approval_contract or interactive_stages'
```

Expected: failures for the nonexistent install target, missing approval
contract, and missing `approval_log`.

In the same test edit, replace the existing stage-specific assertions that
require the literal `AskUserQuestion` tool with assertions for
`approval-contract.md`, explicit user selection, and the unchanged stage
advance. This prevents a Claude-specific UI name from remaining a false
portability requirement.

- [ ] **Step 3: Add the shared approval contract**

Create `approval-contract.md` with this complete protocol:

```markdown
# Stage approval contract

Every stage decision is explicit and auditable.

1. Check the current conversation for an exact decision that names the
   selected item or approved configuration.
2. Check `research/APPROVALS.md` when `approval_log:` in `STATE.md` points to
   it. A valid entry records UTC date, stage, decision, scope, and provenance
   (`conversation` or `approval-log`).
3. If the exact decision is already pre-authorized, copy it into the approval
   log and continue without asking again.
4. Otherwise use the platform's available user-input mechanism. `AskUserQuestion`
   is one implementation, not a required tool; plain chat or another native
   picker is valid.
5. Never infer approval from silence, a broad project goal, or approval of a
   different metric or stage.

Changing a recorded decision requires a new append-only entry. Protocol
deviations still belong under `overrides:` in `STATE.md`; an approval is not an
override.
```

- [ ] **Step 4: Update the dispatcher, stages, state, and installer**

Add `- approval_log: research/APPROVALS.md` to the state template. Link the
contract from every interactive stage and replace tool-specific
`AskUserQuestion` requirements with:

```markdown
Resolve the decision via
`skills/autoresearch/references/approval-contract.md`. Consume an exact
pre-authorized decision without prompting; otherwise use the platform's
available user-input mechanism.
```

Replace the broken Codex symlink with:

```bash
mkdir -p "$HOME/.agents/skills"
for skill in "$HOME/.codex/sci-brain/skills"/*; do
  [ -f "$skill/SKILL.md" ] || continue
  ln -sfn "$skill" "$HOME/.agents/skills/$(basename "$skill")"
done
```

- [ ] **Step 5: Run focused tests**

Run the Step 2 command. Expected: all selected tests pass.

- [ ] **Step 6: Commit**

```bash
git add .codex/INSTALL.md tests/test_autoresearch_skills.py \
  skills/autoresearch skills/autoresearch-topics/SKILL.md \
  skills/autoresearch-db/SKILL.md skills/autoresearch-validator/SKILL.md
git commit -m "fix: make autoresearch approvals portable"
```

---

### Task 2: Make validator privacy enforceable

**Files:**
- Modify: `skills/autoresearch-validator/SKILL.md`
- Modify: `skills/autoresearch-validator/references/validator-contract.md`
- Modify: `skills/autoresearch-validator/references/negative-controls.md`
- Test: `tests/test_autoresearch_skills.py`

**Interfaces:**
- Consumes: candidate directory, public development inputs, private scorer and
  holdout roots.
- Produces: a validator gate that fails closed unless candidate code is unable
  to read validator-private and holdout files.

- [ ] **Step 1: Write failing privacy tests**

Append:

```python
def test_validator_private_layout_is_outside_attempts():
    text = _read("autoresearch-validator")
    for marker in [
        "research/validator/private/",
        "research/benchmark/private/",
        "outside the attempt worktree",
        "fail closed",
        "policy hash",
    ]:
        assert marker in text


def test_env_escape_control_probes_both_private_roots():
    text = _ref("autoresearch-validator", "negative-controls.md")
    assert "validator/private" in text
    assert "benchmark/private" in text
    assert "network" in text


def test_contract_records_private_hashes_without_labels():
    text = _ref("autoresearch-validator", "validator-contract.md")
    assert "scorer_hash" in text
    assert "holdout_hash" in text
    assert "sandbox_policy_hash" in text
    assert "never labels" in text.lower()
```

- [ ] **Step 2: Verify the tests fail**

Run:

```bash
PYTHONPATH=/private/tmp/sci-brain-test-deps \
  /Users/mingrui/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  -m pytest -q tests/test_autoresearch_skills.py \
  -k 'validator_private or env_escape_control or private_hashes'
```

Expected: all three tests fail on missing operational requirements.

- [ ] **Step 3: Correct the validator layout and gate**

Specify:

```text
research/validator/            tracked public contract, launcher, manifest
research/validator/private/    ignored scorer core and private expected values
research/benchmark/dev/        tracked public development inputs
research/benchmark/private/    ignored holdout inputs/labels
```

Require both private directories in `.gitignore`; require the validator process
to live outside attempt worktrees; require candidate execution in a sandbox
that can read only candidate files, public inputs, and pinned runtime files.
Record `scorer_hash`, `holdout_hash`, and `sandbox_policy_hash` in the manifest.
Use the exact phrase “fail closed” when any forbidden read or network probe
succeeds.

- [ ] **Step 4: Strengthen the environment-escape control**

Define an `env-escape` candidate that separately attempts:

```python
open("../research/validator/private/scorer.py", "rb")
open("../research/benchmark/private/labels.json", "rb")
socket.create_connection(("example.com", 80), timeout=1)
```

The control passes only if all attempts are blocked and named in `errors[]`.

- [ ] **Step 5: Run focused and full autoresearch tests**

Run the Step 2 command, then:

```bash
PYTHONPATH=/private/tmp/sci-brain-test-deps \
  /Users/mingrui/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  -m pytest -q tests/test_autoresearch_skills.py
```

Expected: privacy tests pass; the entire focused file passes.

- [ ] **Step 6: Commit**

```bash
git add tests/test_autoresearch_skills.py skills/autoresearch-validator
git commit -m "fix: seal autoresearch validator private state"
```

---

### Task 3: Make attempt worktrees reproducible

**Files:**
- Modify: `skills/autoresearch/references/state-schema.md`
- Modify: `skills/autoresearch-run/SKILL.md`
- Modify: `skills/autoresearch-run/references/attempt-protocol.md`
- Modify: `skills/autoresearch-run/references/reflection-template.md`
- Test: `tests/test_autoresearch_skills.py`

**Interfaces:**
- Consumes: a clean committed `baseline_commit` and an optional ancestor attempt
  commit.
- Produces: explicit attempt branches/worktrees whose parent commit is recorded
  before implementation.

- [ ] **Step 1: Write failing worktree tests**

Append:

```python
def test_state_records_committed_attempt_baseline():
    text = _ref("autoresearch", "state-schema.md")
    assert "baseline_commit:" in text


def test_run_preflights_worktree_and_clean_baseline():
    text = _read("autoresearch-run")
    for marker in [
        "git check-ignore -q .worktrees",
        "git status --porcelain",
        "git merge-base --is-ancestor",
        "baseline_commit",
        "public pipeline artifacts",
        "refuse",
    ]:
        assert marker in text


def test_attempt_creation_names_branch_and_parent_ref():
    text = _ref("autoresearch-run", "attempt-protocol.md")
    assert "git worktree add -b autoresearch/attempt-NNN" in text
    assert "<parent-ref>" in text
    assert "**base commit**" in text
    assert "**result commit**" in text
```

- [ ] **Step 2: Verify the tests fail**

Run:

```bash
PYTHONPATH=/private/tmp/sci-brain-test-deps \
  /Users/mingrui/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  -m pytest -q tests/test_autoresearch_skills.py \
  -k 'committed_attempt_baseline or preflights_worktree or names_branch'
```

Expected: failures for missing baseline and explicit worktree lineage.

- [ ] **Step 3: Add baseline preflight**

Add `baseline_commit: (unset)` to state. Before a cycle, require:

```bash
git check-ignore -q .worktrees
git status --porcelain --untracked-files=all
git rev-parse HEAD
```

The run stage refuses if `.worktrees/` is not ignored, if any public pipeline
artifact is uncommitted, or if `baseline_commit` is not an ancestor of the
clean orchestration HEAD. Ignored private validator and holdout files are
allowed. The baseline SHA names the immutable candidate-visible tree; the
later commit that records that SHA in `STATE.md` is orchestration metadata and
does not redefine the baseline.

- [ ] **Step 4: Make attempt creation explicit**

Define parent resolution:

```text
draft   -> baseline_commit
improve -> result commit of the named successful parent attempt
debug   -> result commit of the named failed parent attempt
```

Create with:

```bash
git worktree add -b autoresearch/attempt-NNN \
  .worktrees/attempt-NNN <parent-ref>
```

Record base commit before implementation and result commit after the attempt.
If the candidate crashes before a result commit, record `result commit:
(none—crashed)` and never reuse the number.

- [ ] **Step 5: Run tests**

Run the Step 2 command followed by the entire focused test file. Expected: all
pass.

- [ ] **Step 6: Commit**

```bash
git add tests/test_autoresearch_skills.py \
  skills/autoresearch/references/state-schema.md \
  skills/autoresearch-run
git commit -m "fix: pin autoresearch attempt worktree lineage"
```

---

### Task 4: Build the isolated neutral-atom smoke project

**Files:**
- Create outside PR repo:
  `/private/tmp/atomicqc-autoresearch-smoke/`
- Create runtime artifacts:
  `topics.md`, `research/STATE.md`, `research/APPROVALS.md`,
  `.knowledge/`, `research/INSIGHTS.md`, `research/CATALOG.md`,
  `research/database/`, `research/benchmark/`, `research/validator/`
- Test:
  `/private/tmp/atomicqc-autoresearch-smoke/tests/test_data_and_validator.py`

**Interfaces:**
- Consumes: three CaltechDATA NPY URLs and their published MD5 values.
- Produces: immutable public data, development/private splits, a baseline
  candidate, and a validator ready for strictness self-test.

- [ ] **Step 1: Clone the local dataset project without user dirt**

Run:

```bash
git clone --no-hardlinks /Users/mingrui/Projects/AtomicQCPlatformData \
  /private/tmp/atomicqc-autoresearch-smoke
git -C /private/tmp/atomicqc-autoresearch-smoke switch -c \
  autoresearch/rabi-envelope-smoke
```

Expected: a clean independent clone; no files are written into the user's
existing checkout.

- [ ] **Step 2: Initialize dispatcher state and pre-authorizations**

Create `research/STATE.md` from the revised template with:

```text
stage: topics
topic: rabi-envelope-recovery
batch_size: 3
time_limit_seconds: 30
authorized_rounds: 1
next_attempt: 1
next_cycle: 1
baseline_commit: (unset)
approval_log: research/APPROVALS.md
```

Create append-only approvals for the topic, approved metrics, five Selected
insight areas, validator goal, fallback environment, and one authorized round.

- [ ] **Step 3: Download and verify the official arrays**

Download:

```text
https://data.caltech.edu/records/4m9sp-yzr58/files/fig4a_rabi_duration.npy?download=1
https://data.caltech.edu/records/4m9sp-yzr58/files/fig4a_rabi_pop_1.npy?download=1
https://data.caltech.edu/records/4m9sp-yzr58/files/fig4a_rabi_pop_1_std.npy?download=1
```

Verify MD5:

```text
93c6bd2d084f5c80075c75c8976fe765  fig4a_rabi_duration.npy
a0432de3d76551610e2a795803eb82dd  fig4a_rabi_pop_1.npy
7b95de05b41d1e05fdba72dc90b20334  fig4a_rabi_pop_1_std.npy
```

Write provenance to `research/database/README.md` and immutable records to
`research/database/source-manifest.json`.

- [ ] **Step 4: Write the NPY/data tests first**

Create standard-library `unittest` cases that assert:

```python
self.assertEqual(len(duration), len(population))
self.assertEqual(len(population), len(sigma))
self.assertGreater(len(duration), 20)
self.assertTrue(all(t >= 0 for t in duration))
self.assertTrue(all(0 <= p <= 1 for p in population))
self.assertTrue(all(s > 0 for s in sigma))
```

Also test that an MD5 mismatch and a non-1D/non-float NPY file raise specific
`ValueError` messages.

- [ ] **Step 5: Implement the smallest standard-library NPY reader**

Implement `load_1d_float(path: Path) -> list[float]` using:

```python
magic = stream.read(6)
version = tuple(stream.read(2))
header_len = struct.unpack("<H" if version == (1, 0) else "<I",
                           stream.read(2 if version == (1, 0) else 4))[0]
header = ast.literal_eval(stream.read(header_len).decode("latin1"))
```

Accept only little-endian `f8` or `f4`, `fortran_order == False`, and one
dimension. Reject all other formats explicitly.

- [ ] **Step 6: Run data tests**

Run:

```bash
python3 -m unittest discover -s tests -p 'test_data_and_validator.py' -v
```

Expected: all data tests pass.

- [ ] **Step 7: Execute the topics and DB stages**

Write the approved smoke topic and metric block to `topics.md`. Use
`download-ref` to populate `.knowledge/` from authoritative arXiv/DOI
references covering all five approved insight areas. Write
`research/INSIGHTS.md`, select all five pre-authorized areas, reproduce the
undamped baseline, and write `research/CATALOG.md`.

Advance only after the survey gate checklist passes on disk.

- [ ] **Step 8: Write validator controls and tests before the scorer**

The tests invoke the public CLI against:

```text
baseline
controls/cheater
controls/wrong-answer
controls/timeout
controls/env-escape
controls/public-row-lookup
```

Assert exit codes, JSON status, named `errors[]`, timeout overshoot below five
percent, and blocked private/network access.

- [ ] **Step 9: Implement and self-test the validator**

Use a public launcher and ignored private scorer. Candidate output contract:

```json
{
  "predictions": [{"instance": "id", "population": 0.5}],
  "omega_rad_per_s": 1.0,
  "model": "undamped|exponential|gaussian|other"
}
```

The scorer computes uncertainty-normalized RMSE, enforces guards, and emits the
validator-contract JSON. Run all controls, hash the private scorer, holdout,
sandbox policy, and interpreter, then record results in `manifest.json`.

- [ ] **Step 10: Commit the public baseline**

Ensure private paths and `.worktrees/` are ignored. Commit all public topic,
evidence, database, development, validator-contract, and baseline-candidate
artifacts while `baseline_commit` is unset; capture that commit SHA. Update
`STATE.md` with the captured SHA and create a second orchestration commit.
Verify the baseline is an ancestor of the clean HEAD and that later
orchestration-only changes do not alter candidate-visible files.

---

### Task 5: Run one three-attempt autoresearch cycle

**Files:**
- Runtime:
  `/private/tmp/atomicqc-autoresearch-smoke/.worktrees/attempt-001..003/`
- Runtime:
  `/private/tmp/atomicqc-autoresearch-smoke/docs/discussion/<timestamp>-cycle-01.md`

**Interfaces:**
- Consumes: passed survey/validator gates and committed baseline.
- Produces: three validator-scored attempts, lineage-complete logs, and one
  reflection report.

- [ ] **Step 1: Verify entry gate and worktree preflight**

Check every artifact named by `autoresearch-run`, `.worktrees/` ignore state,
clean public baseline, and state/HEAD SHA agreement. Expected: gate passes.

- [ ] **Step 2: Plan a surplus and choose three non-duplicate hypotheses**

Generate at least six hypotheses from Selected insights. Rank by information
gain, cost, and distinctness. Promote one draft, one atomic improvement, and
one additional draft or debug according to the run protocol. Record rejected
near-duplicates before implementation.

- [ ] **Step 3: Execute attempts 001–003**

For each attempt:

1. increment state numbering immediately;
2. create the explicitly named branch/worktree from the resolved parent;
3. write `LOG.md` before candidate code;
4. run unlimited `--precheck`;
5. run exactly one development score;
6. append JSON result and learning to `LOG.md`;
7. commit the candidate and log; and
8. leave the worktree intact.

- [ ] **Step 4: Spend the authorized aggregate holdout query**

Run only the cycle's best development candidate on holdout. Record aggregate
pass/fail and budget decrement; do not expose labels.

- [ ] **Step 5: Write reflection and update state**

Write all required reflection sections, including “K of 3 attempts improved”,
best score versus baseline, causal ranking, dead approaches, literature
check, holdout decision, and distance to goal. Set `authorized_rounds: 0`;
set `stage: done` only if the predefined dev and holdout bars both pass.

- [ ] **Step 6: Verify the run audit**

Assert exactly three unique attempt directories, three complete `LOG.md`
files, three validator reports, one reflection, and consistent state counters.

---

### Task 6: Build the ten-topic undergraduate reserve

**Files:**
- Create: `examples/neutral-atom-autoresearch-topics.md`
- Test: `tests/test_neutral_atom_autoresearch_example.py`

**Interfaces:**
- Consumes: current primary literature and the `autoresearch-topics` scoring
  protocol.
- Produces: exactly ten independently runnable, fully metricized topics.

- [ ] **Step 1: Write the failing reserve-structure test**

Parse headings `## Topic 01` through `## Topic 10` and require, within each
section:

```text
### Research question
### Evidence that the gap is open
### Suitability
### Metrics
### Cost and resources
### Gaming risk and negative control
### Undergraduate prerequisites
```

Require `**Checkable:**`, `**Cheap:**`, `**Headroom:**`,
`**Publishable:**`, `**Primary metric**`, and `**Guard metric**`. Parse scores
and assert Checkable and Cheap are each at least 3.

- [ ] **Step 2: Run the test and verify failure**

Run:

```bash
PYTHONPATH=/private/tmp/sci-brain-test-deps \
  /Users/mingrui/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  -m pytest -q tests/test_neutral_atom_autoresearch_example.py
```

Expected: failure because the reserve does not exist.

- [ ] **Step 3: Search and deduplicate current primary references**

For each candidate topic, search arXiv/CrossRef/publisher sources first,
deduplicate by normalized DOI or title/first-author, and retain at least one
primary reference that explicitly supplies data, a benchmark, or an open
limitation. Do not use a review alone as evidence that the gap is open.

- [ ] **Step 4: Write all ten fully metricized topics**

Cover complementary neutral-atom modeling lanes:

1. Rabi envelope recovery;
2. Ramsey dephasing-family discrimination;
3. spatial Rabi-inhomogeneity compression;
4. coherent transport trajectory surrogate modeling;
5. RB decay with leakage/loss separation;
6. CZ coherent-angle scenario bounds;
7. gate-speed error-budget response fitting;
8. Aquila bitstring observation-model checks;
9. correlated phase-noise detection;
10. active pulse sampling for identifiability.

If literature evidence makes one lane uncheckable or too costly, replace it
with another lane rather than lowering the score threshold.

- [ ] **Step 5: Run the reserve test**

Run the Step 2 command. Expected: pass with exactly ten topics.

- [ ] **Step 6: Commit**

```bash
git add examples/neutral-atom-autoresearch-topics.md \
  tests/test_neutral_atom_autoresearch_example.py
git commit -m "docs: add neutral-atom autoresearch topic reserve"
```

---

### Task 7: Add the reproducible smoke-test report

**Files:**
- Create: `examples/neutral-atom-autoresearch-smoke/README.md`
- Create: `examples/neutral-atom-autoresearch-smoke/run-summary.md`
- Create: `examples/neutral-atom-autoresearch-smoke/source-manifest.json`
- Modify: `tests/test_neutral_atom_autoresearch_example.py`

**Interfaces:**
- Consumes: authoritative runtime state, manifest, attempts, and reflection.
- Produces: a source-grounded public audit without private labels.

- [ ] **Step 1: Extend the example test first**

Require the summary to name:

```text
topics
survey gate
validator gate
attempt-001
attempt-002
attempt-003
baseline score
best development score
holdout
reflection
```

Validate source-manifest DOI, three filenames, MD5 values, and that no path
contains `benchmark/private`, `validator/private`, or `.worktrees`.

- [ ] **Step 2: Verify the extended test fails**

Run the example test. Expected: missing report artifacts.

- [ ] **Step 3: Copy only public evidence**

Write the README with reproduction instructions and the run summary with exact
scores, gate results, environment downgrade, negative-control results, attempt
yield, and skill friction/fixes. Copy only public source metadata, never the
private benchmark, private scorer, or worktree contents.

- [ ] **Step 4: Run example tests**

Run the example test. Expected: pass.

- [ ] **Step 5: Commit**

```bash
git add examples/neutral-atom-autoresearch-smoke \
  tests/test_neutral_atom_autoresearch_example.py
git commit -m "test: document neutral-atom autoresearch smoke run"
```

---

### Task 8: Complete regression and scope verification

**Files:**
- Inspect all changed files.

**Interfaces:**
- Consumes: complete branch.
- Produces: evidence that focused tests pass and no new repository-wide failure
  was introduced.

- [ ] **Step 1: Run focused tests**

```bash
PYTHONPATH=/private/tmp/sci-brain-test-deps \
  /Users/mingrui/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  -m pytest -q tests/test_autoresearch_skills.py \
  tests/test_neutral_atom_autoresearch_example.py
```

Expected: all pass.

- [ ] **Step 2: Run the full suite**

```bash
PYTHONPATH=/private/tmp/sci-brain-test-deps \
  /Users/mingrui/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  -m pytest -q
```

Expected: exactly the same seven pre-existing failures and no new failures.

- [ ] **Step 3: Audit diff and protocol coverage**

Run:

```bash
git diff --check origin/main...HEAD
git diff --stat origin/main...HEAD
git status --short --branch
```

Review every spec requirement against the branch and runtime artifacts. Remove
speculative changes not reproduced by the smoke test.

- [ ] **Step 4: Perform a read-only code/skill review**

Use the requesting-code-review workflow locally. Resolve every correctness or
scope issue before publishing.

---

### Task 9: Publish the pull request

**Files:**
- No new source files unless publication checks reveal a defect.

**Interfaces:**
- Consumes: clean reviewed branch.
- Produces: pushed `codex/test-autoresearch-neutral-atom` branch and PR against
  `QuantumBFS/sci-brain:main`.

- [ ] **Step 1: Confirm GitHub identity and permission**

Run `gh auth status`. Upstream currently grants pull but not push permission,
so create or reuse the authenticated user's fork.

- [ ] **Step 2: Push the exact reviewed branch**

Push `codex/test-autoresearch-neutral-atom` to the user-owned fork. Re-run
`git rev-parse HEAD` and confirm the remote branch SHA matches.

- [ ] **Step 3: Open a ready PR with no requested reviewers**

The PR body includes:

- problem reproduced by the real smoke run;
- concise protocol fixes;
- actual three-attempt results;
- ten-topic reserve;
- focused and full-suite test evidence;
- seven pre-existing failures clearly separated; and
- source-data DOI/license.

- [ ] **Step 4: Verify PR metadata and checks**

Read back PR base/head, diff, reviewer requests, and initial checks. Reviewer
requests must be empty. Report PR, CI, reviewer, and merge state separately.
