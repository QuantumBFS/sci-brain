# QE Run Preparation Todo

Use this checklist before creating or submitting a QE native PHonon EPC run.
Keep completed answers beside the run directory when the calculation is meant to
be reproducible.

## 1. QE build and launcher

- [ ] Record QE version from the executable banner, module, build log, or source
  checkout.
- [ ] Record absolute paths for `pw.x`, `ph.x`, `q2r.x`, `matdyn.x`, and
  `alpha2f.x`.
- [ ] Confirm the MPI launcher (`mpirun`, `srun`, site wrapper) and whether
  `alpha2f.x`, `q2r.x`, and `matdyn.x` should be serial for this build.
- [ ] Decide the Slurm layout, rank count, `NPOOL`, and thread variables.

## 2. Structure

- [ ] Choose the exact relaxed structure to study, not an unrelaxed database
  starting point.
- [ ] Record the structure source, relaxation functional, pressure or lattice
  constraint, and whether spin-orbit or magnetism matters.
- [ ] Convert the cell and coordinates into the QE input convention to be used:
  `ibrav = 0` with `CELL_PARAMETERS` is the safest default.
- [ ] Verify `nat`, `ntyp`, species labels, masses, and atomic positions.

## 3. Pseudopotentials and cutoffs

- [ ] Select one consistent pseudopotential family and exchange-correlation
  functional for all species.
- [ ] Put the required UPF files under the run's `pseudo/` directory, or symlink
  them from a project pseudopotential archive.
- [ ] Make `ATOMIC_SPECIES` filenames match files that actually exist.
- [ ] Record validated `ecutwfc`, `ecutrho`, smearing or tetrahedron policy, and
  any semicore or relativistic assumptions.

## 4. Electronic and phonon grids

- [ ] Choose the SCF k grid and whether it is explicit automatic, gamma-shifted,
  or unshifted.
- [ ] Choose the unshifted IFC q grid for `ph_ifc.in -> q2r.in -> matdyn.x`.
- [ ] Choose the shifted EPC q grid for dVscf generation.
- [ ] Choose the dense electron k grid for `lambda_tetra`.
- [ ] Define at least one convergence follow-up: q-grid, dense-k grid, or
  lattice/structure sensitivity.

## 5. Run directory contract

- [ ] Set one consistent `prefix`, `outdir`, and `pseudo_dir` across all inputs.
- [ ] Decide whether IFC and EPC branches get separate directories or whether
  `tmp/_ph0` must be archived between branches.
- [ ] Remove or archive old `tmp/`, `_ph0/`, `.save/`, `.dyn*`, `.elph*`,
  `.out`, `.err`, and `CRASH` files before a fresh rerun.
- [ ] Prepare `scf.in`, `ph_ifc.in`, `q2r.in`, `matdyn_disp.in`,
  `ph_dvscf_epc.in`, `elph_densek_alpha2f.in`, and the batch wrapper.
- [ ] Run `bash -n` on the wrapper and inspect key input fields before
  submitting.

## 6. Result record

- [ ] Save `run_steps.tsv`, Slurm output, QE output tails, and non-empty error
  files.
- [ ] Record the final status of SCF, IFC, q2r, matdyn, dVscf, dense-k elph, and
  `alpha2f.x`.
- [ ] Report `lambda`, `omega_log`, `Tc(mu*)`, q/k grids, QE version, resources,
  and imaginary-frequency status together.
- [ ] Mark the result as canary, convergence check, or production-quality; do
  not present a single coarse point as converged.
