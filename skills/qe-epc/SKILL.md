---
name: qe-epc
description: Use when preparing, running, monitoring, debugging, or interpreting Quantum ESPRESSO native DFPT electron-phonon coupling and superconductivity calculations involving pw.x, ph.x, q2r.x, matdyn.x, alpha2f.x, lambda_tetra, alpha2F(omega), lambda, omega_log, McMillan/Allen-Dynes Tc, q/k convergence, or PHonon scratch failures. This skill is for QE PHonon workflows, not EPW.
---

# QE EPC

Run a structured **Quantum ESPRESSO native DFPT-EPC** workflow: build SCF and
PHonon inputs, keep IFC and EPC branches separate, monitor long `ph.x` jobs,
diagnose fragile PHonon failures, and turn `alpha2F(omega)` into a qualified
superconducting `Tc` estimate.

**Scope note.** This skill is for QE's PHonon route (`pw.x`, `ph.x`, `q2r.x`,
`matdyn.x`, `alpha2f.x`). It is **not** an EPW workflow. Use it when the user
wants native QE electron-phonon coupling, `lambda_tetra`, `alpha2F(omega)`,
`lambda`, `omega_log`, or McMillan/Allen-Dynes `Tc`. If the user asks for
Wannier interpolation, dense electron-phonon matrix interpolation, or EPW input
generation, switch to an EPW-specific workflow instead.

The reusable source templates live in `skills/qe-epc/source/`:

```text
prepare-qe-todo.md
input-sources.md
scf.in
ph_ifc.in
q2r.in
matdyn_disp.in
ph_dvscf_epc.in
elph_densek_alpha2f.in
run_epc_sbatch.template.sh
```

Do not embed pseudopotential files in this skill. `source/input-sources.md`
points to QE/SSSP download locations and records what the PdH-style templates
assume.

## Version assumptions

- Skill/template revision: 2026-06-30.
- Target route: Quantum ESPRESSO native PHonon EPC with `lambda_tetra`, as used
  by common QE 7.x PHonon builds and `PHonon/examples/tetra_example/`.
- The exact QE build is not bundled with this skill. Before each run, record the
  installed QE version, executable paths, module or build prefix, and whether
  `alpha2f.x` is serial-only for that build.
- Re-check input keywords against the installed QE documentation when using
  older QE 6.x builds, patched site builds, or future QE releases.

---

## Operating principle

**Branch-separated, evidence-first, convergence-qualified.**

- **Branch-separated** - keep the normal IFC/phonon-dispersion branch separate
  from the shifted-q EPC branch. Shared PHonon scratch is a common source of
  false k-grid failures.
- **Evidence-first** - judge jobs from `run_steps.tsv`, output tails, q-point
  progress, and concrete QE error text, not from scheduler state alone.
- **Convergence-qualified** - report `Tc` only with its q-grid, dense k-grid,
  structure, imaginary-frequency status, and remaining convergence caveats.

---

## The workflow spine

Use this sequence unless the active QE example or project convention gives a
validated reason to deviate:

```text
pw.x scf
ph.x ph_ifc                 # unshifted IFC branch
q2r.x
matdyn.x
archive tmp/_ph0 from IFC branch if one outdir is reused
ph.x ph_dvscf_epc           # shifted-q dVscf branch
ph.x elph_densek            # lambda_tetra on dense electron k grid
alpha2f.x                  # serial post-processing in common QE 7.x builds
```

Use one directory per parameter point:

```text
runs/<material-or-lattice>_q<N>_k<M>/
  pseudo/
  scf.in
  ph_ifc.in
  q2r.in
  matdyn_disp.in
  ph_dvscf_epc.in
  elph_densek_alpha2f.in
  run_epc.sbatch
  run_steps.tsv
```

Case names should be readable in a result table: include the structure or
lattice tag, EPC q grid, and dense electron k grid.

---

## Phase 0 - Preflight

Resolve the calculation context before writing or submitting anything:

If starting a new calculation, first walk through
`source/prepare-qe-todo.md` and keep the completed copy or answers beside the
run tree.

1. **QE executables.** Verify the QE version and paths for `pw.x`, `ph.x`,
   `q2r.x`, `matdyn.x`, and `alpha2f.x`. Confirm the MPI launcher expected by
   the cluster or workstation.
2. **Structure.** Use the relaxed structure that the project actually wants to
   study. Check whether it is close to a phonon instability; EPC `Tc` is not
   meaningful if the relevant q grid has unresolved imaginary modes.
3. **Pseudopotentials and cutoffs.** Keep the exchange-correlation functional
   and pseudopotential family consistent across species. Copy or symlink UPF
   files into `pseudo/`; do not assume this skill ships them.
4. **Grid plan.** Record the SCF k grid, EPC shifted q grid, dense electron k
   grid, and at least one follow-up convergence comparison.
5. **Scratch policy.** Inspect whether old `tmp/`, `_ph0/`, `.save/`, `.dyn*`,
   `.elph*`, `.out`, or `.err` files exist. Decide whether this is a fresh run,
   a full rerun, or a post-processing continuation.

---

## Phase 1 - Prepare inputs

Start from `skills/qe-epc/source/` and adapt values to the project.

### SCF

Use `scf.in` as the pattern:

- exact relaxed cell and atomic positions;
- `prefix`, `outdir`, and `pseudo_dir` that match every PHonon input;
- `occupations = 'tetrahedra_opt'` for the `lambda_tetra` route;
- a dense explicit `K_POINTS automatic` grid;
- project-validated `ecutwfc`, `ecutrho`, `conv_thr`, and mixing settings.

### IFC branch

Use `ph_ifc.in -> q2r.in -> matdyn_disp.in` for ordinary force constants and
phonon dispersion:

- unshifted `ldisp = .true.` q grid;
- `q2r.x` and `matdyn.x` only on this IFC branch;
- `asr` / `zasr` selected according to the material and project convention.

### EPC branch

Use `ph_dvscf_epc.in` for shifted-q dVscf generation:

- `ldisp = .true.`;
- `lshift_q = .true.`;
- `fildyn`, `fildvscf`, and `fildrho` set explicitly;
- `recover = .true.` allowed for restartable dVscf generation.

Then use `elph_densek_alpha2f.in` for dense-k `lambda_tetra`:

- `trans = .false.`;
- `electron_phonon = 'lambda_tetra'`;
- `nk1`, `nk2`, `nk3` set to the dense electron k grid;
- no `recover = .true.` in this dense-k lambda input;
- `&INPUTa2F nfreq = ... /` present so the same file can feed `alpha2f.x`.

Run `alpha2f.x` serially unless the exact QE build has been verified to support
parallel execution for that executable.

---

## Phase 2 - Submit safely

Use `source/run_epc_sbatch.template.sh` as a starting point for cluster jobs.
Adapt the SBATCH header, modules, `QE_ROOT`, MPI launcher, `NPOOL`, and resource
request to the target system.

### Parallel settings

Treat the Slurm allocation, MPI rank count, QE pool count, and thread variables
as one contract. Do not tune them independently.

- Use a CPU-only pure-MPI default unless a project has validated hybrid MPI/OpenMP.
- Set math-library threads to one for this default:
  `OMP_NUM_THREADS=1`, `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1`.
- Match the launch command to the allocation. A portable pure-MPI layout is:

  ```bash
  #SBATCH --nodes=1
  #SBATCH --ntasks-per-node=64
  #SBATCH --cpus-per-task=1
  NP="${SLURM_NTASKS}"
  ```

  then run `mpirun -np "$NP" ...`.
- Some clusters prefer one Slurm task with many CPUs and a launcher that
  expands inside the allocated cpuset:

  ```bash
  #SBATCH --nodes=1
  #SBATCH --ntasks-per-node=1
  #SBATCH --cpus-per-task=64
  NP="${SLURM_CPUS_PER_TASK}"
  ```

  Use this only after verifying that the site MPI launcher really starts `NP`
  MPI ranks inside the allocation.
- Pass `-npool "$NPOOL"` to `pw.x` and the MPI `ph.x` steps. Choose `NPOOL` so
  it divides the MPI rank count and is sensible for the k-point count. Start
  conservative (`1`, `2`, `4`, or `8`) and verify QE reports the expected pools.
- Keep `q2r.x`, `matdyn.x`, and `alpha2f.x` serial unless the exact executable
  has been tested in parallel.
- Print `NP`, `NPOOL`, thread variables, `QE_ROOT`, and the node list at job
  start. After the first run, check `scf.out` or `ph*.out` for the reported
  processor count and pool count before trusting timing or failures.

Before submission, check:

```bash
bash -n run_epc.sbatch
rg -n "occupations|K_POINTS|electron_phonon|trans|recover|nk1|nfreq" *.in
rg -n "recover *= *.true." elph_densek_alpha2f.in && echo "remove recover"
```

Then verify by inspection:

- UPF names in `ATOMIC_SPECIES` exist under `pseudo/`.
- All QE inputs use the same `prefix` and `outdir`.
- Dense-k `lambda_tetra` input has `trans = .false.` and no `recover`.
- A full-rerun wrapper archives old outputs before starting.
- If IFC and EPC branches share one `outdir`, the wrapper archives `tmp/_ph0`
  after `matdyn.x` and before `ph_dvscf_epc`.
- The Slurm request, `NP`, `NPOOL`, and thread variables match the intended
  parallel layout.
- The dense k grid stays below the QE build's k-point array limit. A
  `set_kplusq: too many k points` failure means reduce `nk` or rebuild QE with
  a larger `npk`.

---

## Phase 3 - Monitor and diagnose

For live jobs, combine scheduler state with case-local evidence:

```bash
tail -n 20 run_steps.tsv 2>/dev/null
stat -c "%y %s %n" *.out 2>/dev/null
grep -E "Calculation of q|Representation #|JOB DONE|Error in routine|lambda|omega" -n *.out 2>/dev/null | tail -n 80
find . -maxdepth 1 \( -name "CRASH" -o -name "*.err" \) -type f -size +0 -print
```

Treat `ph_ifc` and `ph_dvscf_epc` as long-running stages. A job is slow/active,
not stuck, when q-point or representation lines continue advancing and there is
no non-empty `.err`, `CRASH`, or `Error in routine`.

### Failure map

| Symptom | Likely cause | Response |
|---|---|---|
| `opt_tetra_init (2): cannot remap grid on k-point list` | EPC branch is reading stale PH scratch, or the SCF k list is incompatible with the tetrahedron remap | First inspect `Reading xml data from directory` in `ph_ifc.out` and `ph_dvscf_epc.out`. If EPC reads `tmp/_ph0/<prefix>.save/`, archive `_ph0` and rerun from the EPC branch before changing grids. |
| `read_control_ph (1): wrong trans` | Dense-k `elph` step recovered a previous `ph.x` control file with a different `trans` mode | Remove `recover = .true.` from `elph_densek_alpha2f.in`; archive only old dense-k outputs and rerun the post-dVscf branch. |
| `read_lam: Imaginary frequency` in `alpha2f.x` | Shifted EPC q grid contains imaginary modes | Do not force a physical `Tc`. Inspect structural stability, q-grid dependence, and phonon branches first. |
| Shifted q grid cannot be used by `q2r.x` | EPC shifted q grid is being reused as an IFC interpolation grid | Keep unshifted IFC/dispersion and shifted EPC grids as separate branches. |
| `set_kplusq: too many k points` | Dense electron k grid exceeds the QE build's static k-point array | Reduce `nk` or rebuild QE with a larger `npk`; record the limit in the result note. |

---

## Phase 4 - Interpret results

After `alpha2f.x` succeeds, collect:

- `lambda` from QE's direct `omega_q/lambda_q` summary;
- `omega_log` / `omega_ln`, with units;
- the `alpha2F(omega)` data file;
- an independent `alpha2F` integration check when the data file is present;
- `Tc` for at least `mu* = 0.10, 0.13, 0.15`;
- IFC branch and shifted EPC q-grid imaginary-frequency status.

Use this McMillan/Allen-Dynes form when the project does not specify another
convention:

```text
Tc = (omega_log / 1.2) *
     exp[-1.04 * (1 + lambda) /
         (lambda - mu_star * (1 + 0.62 * lambda))]
```

Convert `omega_log` to Kelvin before reporting `Tc`.

Do not call one parameter point final. At minimum compare:

- q-grid convergence at fixed dense k;
- dense-k convergence at fixed q grid;
- structural or lattice-constant sensitivity when the material is close to an
  instability;
- direct QE values against integrated `alpha2F(omega)` values.

Write a short result note beside the run tree with the case name, QE version,
input grids, resources, step statuses, failure/success evidence, `lambda`,
`omega_log`, `Tc(mu*)`, imaginary-frequency status, and remaining convergence
caveats.

---

## Common mistakes

| Mistake | Instead |
|---|---|
| Reusing `tmp/_ph0` from the IFC branch for shifted-q EPC | Archive or separate PH scratch before `ph_dvscf_epc`. |
| Running `q2r.x` on the shifted EPC q grid | Use an unshifted IFC branch for `q2r.x` / `matdyn.x`. |
| Leaving `recover = .true.` in the dense-k `lambda_tetra` input | Keep `recover` only in compatible restartable PHonon branches. |
| Reporting `Tc` after `alpha2f.x` reports imaginary frequencies | Report the instability; do not treat that `Tc` as physical. |
| Calling a q4/k21 canary a converged result | Add q-grid and dense-k checks before presenting a final number. |
| Trusting `RUNNING` or quiet stdout as proof of health | Inspect `run_steps.tsv`, output timestamps, q progress, and error files. |
| Requesting one Slurm shape but launching a different number of MPI ranks | Make Slurm tasks, `NP`, `NPOOL`, and thread variables agree, then verify QE's reported processor and pool counts. |

---

## Integrations

- **Source templates:** `skills/qe-epc/source/`.
- **Run preparation checklist:** `skills/qe-epc/source/prepare-qe-todo.md`.
- **Input provenance and download locations:** `skills/qe-epc/source/input-sources.md`.
- **Cluster wrapper template:** `skills/qe-epc/source/run_epc_sbatch.template.sh`.
- **QE upstream reference:** the installed QE documentation and
  `PHonon/examples/tetra_example/` in a QE source tree.
