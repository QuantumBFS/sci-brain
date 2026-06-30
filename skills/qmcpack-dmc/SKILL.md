---
name: qmcpack-dmc
description: Use when preparing, running, monitoring, debugging, or interpreting plane-wave solid QMCPACK Slater-Jastrow VMC and DMC workflows starting from Quantum ESPRESSO orbitals, including QE SCF/NSCF, pw2qmcpack.x ESHDF conversion, Slater determinant setup, Jastrow optimization, twist averaging, fixed-node DMC, timestep checks, scalar analysis, and MPI or twist-parallel launch tuning.
---

# QMCPACK DMC

Run a structured **QE -> Slater-Jastrow VMC -> DMC** workflow for periodic
solids: generate plane-wave orbitals with Quantum ESPRESSO, convert them with
`pw2qmcpack.x`, build QMCPACK XML inputs, optimize the Jastrow, run fixed-node
DMC, and summarize twist-averaged energies with defensible uncertainty and
convergence caveats.

**Scope note.** This skill is for plane-wave solid workflows that use QE
orbitals and QMCPACK's ESHDF/einspline path. It is not a QMCPACK build guide,
not a molecular Gaussian-basis workflow, and not a substitute for a
project-specific production campaign generator. Use it to create or review the
scientific workflow and launch discipline; use host/project skills for exact
binary paths and scheduler quirks.

The reusable source templates live in `skills/qmcpack-dmc/source/`:

```text
prepare-qmcpack-todo.md
input-sources.md
qe_scf.in
qe_nscf.in
pw2qmcpack.in
sj_vmc_dmc_tw00.xml
run_qe_to_dmc.template.sh
```

Do not embed pseudopotential files or production scalar/HDF5 output in this
skill. `source/input-sources.md` points to documentation and starting locations
for matched QE/QMCPACK pseudopotential pairs.

## Version assumptions

- Skill/template revision: 2026-06-30.
- Target route: QE 7.5-style `pw.x` plus matching HDF5-enabled
  `pw2qmcpack.x`, feeding a QMCPACK 4.3.x complex-valued ESHDF/einspline solid
  workflow.
- Orbital handoff: `pw2qmcpack.x` writes `<prefix>.pwscf.h5` under the QE
  `outdir`; QMCPACK XML `href` values point to that exact file.
- The exact QE and QMCPACK builds are not bundled with this skill. Before each
  run, record executable paths, versions, compiler/MPI/HDF5 stack,
  pseudopotential hashes, scheduler launcher, and source-template revision.
- Re-run a one-twist VMC smoke before expanding if the project uses a different
  major QE/QMCPACK version, a different orbital route, or a new
  pseudopotential pair.

---

## Operating principle

**Pseudopotential-consistent, twist-first, stage-gated.**

- **Pseudopotential-consistent** - use a norm-conserving QE UPF and the matching
  QMCPACK XML pseudopotential from the same source. Do not mix a convenient QE
  ultrasoft/PAW potential with a different QMC pseudopotential.
- **Twist-first** - choose the QMC supercell and twist grid before generating
  QE NSCF orbitals. A dense QE k grid is not a substitute for a QMC twist plan.
- **Stage-gated** - prove each stage with a tiny smoke before expanding: QE
  SCF/NSCF, `pw2qmcpack`, one QMCPACK twist, all twists, then production DMC.

---

## The workflow spine

Use this sequence unless the active project convention gives a validated reason
to deviate:

```text
choose structure, supercell, twist grid, and pseudopotential pair
pw.x scf                    # charge density
pw.x nscf                   # exact full twist grid, nosym/noinv
pw2qmcpack.x                # writes ESHDF under QE outdir
build QMCPACK XML           # Slater determinant + Jastrow + Hamiltonian
tiny VMC smoke              # one twist, short blocks
Jastrow optimization        # linear method loops
final VMC / SJ statistics   # fixed optimized Jastrow
DMC                         # fixed-node, timestep/warmup/replica plan
twist average and compare   # size-matched structures only
```

Use one directory per system/grid/campaign:

```text
runs/<system>_k<NxNyNz>/
  pseudo/
  qmc_pseudo/
  qe_tmp/
  qe_scf.in
  qe_nscf.in
  pw2qmcpack.in
  sj_vmc_dmc_tw00.xml
  sj_vmc_dmc_twNN.xml
  run_qe_to_dmc.sh
  case_timing.dat
  twist_timings.dat
  summary.dat
```

Keep generated scalar/HDF5/wavefunction payloads out of version control unless
the project explicitly treats a small result file as durable evidence.

---

## Phase 0 - Preflight

Resolve the calculation context before writing or submitting anything.

If starting a new calculation, first walk through
`source/prepare-qmcpack-todo.md` and keep the completed copy or answers beside
the run tree.

1. **Binaries.** Verify `pw.x`, `pw2qmcpack.x`, and `qmcpack_complex`. For
   non-Gamma solid twists, default to a complex QMCPACK build.
2. **Structure.** Use the relaxed structure intended for QMC. Check atom count,
   species labels, cell units, pressure/lattice provenance, and whether
   structures being compared are size-matched.
3. **Pseudopotential pair.** Confirm the QE UPF and QMCPACK XML are a matched
   norm-conserving pair. If the QE route uses an ultrasoft UPF, stop and choose
   or generate a QMC-safe pair.
4. **Supercell and twists.** Choose the many-body cell and twist grid first.
   Record `K_POINTS`, twist count, `twistnum` range, and whether all structures
   being compared are size-matched.
5. **Run stage.** Decide whether this is a smoke, Jastrow optimization, fixed
   optimized DMC, timestep-bias suite, or production replica.
6. **Run directory state.** Inspect old `qe_tmp/`, `.save/`, `.pwscf.h5`,
   `*.scalar.dat`, `*.stat.h5`, `.out`, and `.err` files. Decide whether this
   is a fresh run, continuation, or post-processing pass.

---

## Phase 1 - Generate QE orbitals

Start from `source/qe_scf.in`, `source/qe_nscf.in`, and
`source/pw2qmcpack.in`.

### SCF

- Use the target structure, the matched QE UPF, and project-validated cutoffs.
- Run with enough k-points to converge the charge density.
- Keep `prefix`, `outdir`, and pseudopotential names consistent with NSCF and
  `pw2qmcpack.in`.
- Use the QE build that belongs with `pw2qmcpack.x`.

### NSCF

- Run at the exact full twist grid required by the QMC supercell.
- Set `nosym = .true.` and `noinv = .true.` so QE writes every twist, not a
  symmetry-reduced subset.
- Keep `K_POINTS automatic` synchronized with the intended twist count.
- Do not change the structure, pseudopotential, or prefix between SCF and NSCF.

### Conversion

- Run `pw2qmcpack.x` after the NSCF completes.
- Expect the ESHDF file under the QE `outdir`, often
  `qe_tmp/<prefix>.pwscf.h5`.
- Keep the QMCPACK XML `href` pointed at that actual path, not a guessed file
  in the run-directory root.
- Use a serial converter launch (`PW2QMCPACK_NP=1`) unless this exact converter
  build has been proven safe with MPI.

---

## Phase 2 - Prepare QMCPACK XML

Start from `source/sj_vmc_dmc_tw00.xml` and generate one XML per twist.

Required consistency checks:

- `determinantset` uses `type="einspline"` and `href` points to the ESHDF
  written by `pw2qmcpack.x`.
- `twistnum` matches the per-file twist index.
- Electron group sizes match the valence electron count implied by the QMC
  pseudopotentials.
- `simulationcell` lattice vectors are in bohr.
- Ionic positions and species match the QE structure.
- The Hamiltonian uses the matching QMCPACK XML pseudopotential.
- Jastrow coefficients marked `optimize="yes"` are only optimized during the
  intended optimization stage.

Run one short VMC smoke before any optimization or DMC. Treat parser failures,
missing HDF5, wrong electron counts, or pseudopotential mismatches as hard
workflow errors; do not paper over them by changing DMC parameters.

---

## Phase 3 - Optimize and run DMC

Use a short staged XML during development:

```text
tiny VMC preface
linear-method Jastrow optimization loops
final VMC with optimized Slater-Jastrow
short DMC smoke
```

For production:

- Reuse optimized Slater-Jastrow files only when the structure, ESHDF, twist
  grid, pseudopotential pair, and relevant XML conventions match.
- Keep timestep-bias checks explicit, usually at multiple `timestep` values.
- Run independent DMC replicas with different seeds when statistics matter.
- Define warmup/discard policy before summarizing scalar data.
- Record `blocks`, `steps`, `timestep`, `targetwalkers`, warmup, seed, and
  `twistnum` in a machine-readable timing or metadata file.

Project-specific defaults belong to the project workflow, not this generic
skill. For example, the post-HCP reference workflow uses fixed optimized DMC
replicas and a 50-block production discard after warmup for long 3000-block
runs; do not silently transfer that exact rule to unrelated systems without a
fresh scalar-data check.

---

## Phase 4 - Submit safely

Treat QE parallelism and QMCPACK twist parallelism as different problems.

### QE

- Use `QE_NP` MPI ranks for `pw.x`.
- Pass a project-validated `-npool` for SCF/NSCF when useful.
- Verify QE reports the expected rank and pool counts in `qe_scf.out` and
  `qe_nscf.out`.

### Converter

- Default `PW2QMCPACK_NP=1`.
- If the converter needs a special HDF5 library path, apply it only to the
  converter command rather than polluting the global QMCPACK runtime.

### QMCPACK

- Prefer parallel independent twists over large thread counts inside one small
  twist.
- Use this accounting:

  ```text
  total QMC CPU slots = PARALLEL_TWISTS * QMC_NP * OMP_NUM_THREADS
  ```

- Default `OMP_NUM_THREADS=1` until a case is benchmarked otherwise.
- With OpenMPI plus outer CPU sets, use MPI flags such as `--bind-to none`.
- With Intel MPI, prefer explicit per-twist processor lists when the site
  launcher otherwise rebinds ranks onto one CPU.
- Print CPU sets, `PARALLEL_TWISTS`, `QMC_NP`, `OMP_NUM_THREADS`, and MPI flags
  before launching.

Before submission, check:

```bash
bash -n run_qe_to_dmc.sh
rg -n "prefix|outdir|K_POINTS|nosym|noinv" qe_*.in pw2qmcpack.in
rg -n "href=|twistnum|particleset|pseudo|timestep|targetwalkers" *.xml
test -d pseudo && test -d qmc_pseudo
```

Then verify by inspection:

- UPF names in QE `ATOMIC_SPECIES` exist under `pseudo/`.
- QMCPACK pseudopotential XML paths resolve under `qmc_pseudo/`.
- SCF, NSCF, and `pw2qmcpack.in` use the same `prefix` and `outdir`.
- The NSCF grid matches the intended twist count and has `nosym` plus `noinv`.
- XML `href` points to the expected ESHDF under QE `outdir`.
- Slurm resources, `QE_NP`, `QE_NPOOL`, `PARALLEL_TWISTS`, `QMC_NP`, and
  `OMP_NUM_THREADS` match the launch plan.

Do not trust CPU use by assumption. Check live placement when performance looks
wrong:

```bash
ps -C qmcpack_complex -o pid,ppid,psr,stat,pcpu,comm,args
grep Cpus_allowed_list /proc/<pid>/status
```

---

## Phase 5 - Monitor and diagnose

Use output evidence from every stage:

```bash
grep -n "JOB DONE." qe_scf.out qe_nscf.out pw2qmcpack.out
test -s qe_tmp/*.pwscf.h5
grep -n "QMCPACK execution completed successfully" qmcpack_*.out
ls -1 *.scalar.dat
```

For live jobs, combine scheduler state with case-local evidence:

```bash
stat -c "%y %s %n" *.out *.err *.scalar.dat 2>/dev/null
tail -n 40 qe_scf.out qe_nscf.out pw2qmcpack.out qmcpack_*.out 2>/dev/null
grep -E "JOB DONE|Error in routine|Total Energy|DMC|VMC|execution completed" -n *.out 2>/dev/null | tail -n 80
```

Treat a job as active, not stuck, when scalar files or output timestamps keep
advancing and there is no non-empty `.err`, `CRASH`, parser failure, missing
HDF5 error, or MPI abort.

If the user asks for live status or ETA, use queue state plus workflow-local
timing files (`case_timing.dat`, `twist_timings.dat`, per-twist logs), not
queue state alone.

### Failure map

| Symptom | Likely cause | Response |
|---|---|---|
| QMCPACK cannot find `.pwscf.h5` | XML assumes the ESHDF is in the run root | Point `href` at the file under the QE `outdir`, e.g. `qe_tmp/<prefix>.pwscf.h5`. |
| QMCPACK rejects lattice/cell parsing | XML lattice vectors written in Angstrom | Convert lattice vectors to bohr before writing `simulationcell`. |
| NSCF or converted twist count is too small | QE symmetry reduced the k grid | Set `nosym=.true.` and `noinv=.true.` in NSCF and regenerate orbitals. |
| QMCPACK electron count or SPO setup fails | Valence count, species labels, or pseudopotential XML paths do not match the QE structure | Recompute electron groups from the QMC pseudopotential valence and inspect every `<pseudo href=...>`. |
| `pw2qmcpack.x` runs but no useful HDF5 appears | Wrong QE build, wrong prefix/outdir, or converter launched with a bad library/MPI setup | Use the QE build paired with `pw2qmcpack.x`; verify `prefix`, `outdir`, and converter library path. |
| CPU use is concentrated on a few cores | MPI rebinding inside outer twist CPU sets | Inspect rank affinity and switch to no-bind or explicit per-twist CPU lists. |

---

## Phase 6 - Interpret results

For summaries:

- Discard the agreed warmup blocks before computing means.
- Report mean and uncertainty in Hartree and in the project-normalized unit
  such as meV/atom or meV/H.
- Twist-average equal-weight only when the twist grid and weights justify it.
- Compare relative energies only across size-matched many-body cells or label
  the comparison as a finite-size diagnostic.
- Keep VMC/SJ and DMC sections separate in human-facing reports.

For DMC comparisons, first check:

- size matching and atom-count normalization;
- twist grid and twist weights;
- ESHDF provenance and pseudopotential hashes;
- warmup/discard policy;
- timestep-bias evidence;
- independent replica count and seed plan.

DMC rankings that fail any of these checks are finite-size or workflow
diagnostics, not phase-ordering results.

Write a short result note beside the run tree with the case name, structure,
QE/QMCPACK versions, pseudopotential hashes, twist grid, resources, stage
statuses, scalar discard rule, VMC/SJ result, DMC result, and remaining
convergence caveats.

---

## Common mistakes

| Mistake | Instead |
|---|---|
| Using a QE ultrasoft pseudopotential for production QMC orbitals | Use a norm-conserving QE UPF and matching QMCPACK XML pair. |
| Choosing QE k-points before the QMC twist plan | Choose the QMC cell and twist grid first, then generate NSCF twists. |
| Reusing optimized Jastrows across different twist grids or ESHDF files | Reoptimize or prove equivalence before reuse. |
| Running all production twists before a one-twist smoke passes | Gate every campaign with a tiny VMC smoke. |
| Comparing DMC energies from different atom counts as phase rankings | Use size-matched cells or label the result as a finite-size warning. |
| Reporting one timestep as production DMC | Run or cite a timestep-bias check. |
| Trusting `RUNNING` as proof of health | Inspect output tails, scalar timestamps, error files, and timing records. |

---

## Integrations

- **Run preparation checklist:** `skills/qmcpack-dmc/source/prepare-qmcpack-todo.md`.
- **Source templates:** `skills/qmcpack-dmc/source/`.
- **Input provenance and download locations:** `skills/qmcpack-dmc/source/input-sources.md`.
- **Cluster wrapper template:** `skills/qmcpack-dmc/source/run_qe_to_dmc.template.sh`.
- **QE EPC skill for DFPT superconductivity:** `skills/qe-epc/SKILL.md` (different workflow).
- **Local machine build note:** user-level `qmcpack-local-build` when available.
- **Project reference used to seed this workflow:** `/home/zq/zqcodeml/posthcp-hydrogen-stru/.skills/qmcpack`.
