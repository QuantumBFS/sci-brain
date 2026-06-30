# Input Sources For QMCPACK DMC Templates

The files in this directory are source templates, not a complete production
workflow. Before running them, provide project-specific structures,
pseudopotentials, executable paths, twist grids, and scheduler settings.

## Documentation

- QMCPACK documentation: <https://qmcpack.readthedocs.io/>
- QMCPACK input examples and source: <https://github.com/QMCPACK/qmcpack>
- Quantum ESPRESSO documentation: <https://www.quantum-espresso.org/documentation/>

## Version Assumptions

These templates follow the route validated in the local/post-HCP reference
workflow:

```text
QE:       7.5-style HDF5 build with pw2qmcpack.x
QMCPACK: 4.3.x complex-valued ESHDF/einspline workflow
```

Record the exact executable paths, versions, compiler/MPI/HDF5 stack, and input
template revision in each run directory. Treat these files as examples unless
that version record has been filled for the active machine.

## Pseudopotentials

For production QMCPACK, use a matched pseudopotential pair:

```text
QE:       norm-conserving UPF
QMCPACK: XML pseudopotential for the same element/source
```

Do not use an ultrasoft or PAW QE pseudopotential as a production QMC orbital
source unless the project has an explicit, validated route for doing so. In the
post-HCP hydrogen reference workflow, the useful pair was a ccECP-style
`H.ccECP.upf` for QE and matching `H.ccECP.xml` for QMCPACK.

Starting points:

```text
QMCPACK pseudopotential library:
https://github.com/QMCPACK/pseudopotentiallibrary

Hydrogen ccECP recipe:
https://github.com/QMCPACK/pseudopotentiallibrary/tree/main/recipes/H/ccECP

H ccECP QE UPF:
https://github.com/QMCPACK/pseudopotentiallibrary/blob/main/recipes/H/ccECP/H.ccECP.upf

H ccECP QMCPACK XML:
https://github.com/QMCPACK/pseudopotentiallibrary/blob/main/recipes/H/ccECP/H.ccECP.xml
```

Raw download form:

```bash
curl -L -o H.ccECP.upf \
  https://raw.githubusercontent.com/QMCPACK/pseudopotentiallibrary/main/recipes/H/ccECP/H.ccECP.upf
curl -L -o H.ccECP.xml \
  https://raw.githubusercontent.com/QMCPACK/pseudopotentiallibrary/main/recipes/H/ccECP/H.ccECP.xml
```

For a custom potential, keep the generator input or trusted library recipe as
the source of truth and export both the QE UPF and QMCPACK XML from that same
source. Record SHA256 hashes beside the run.

## Units

The QE templates use `CELL_PARAMETERS angstrom`. The QMCPACK XML template uses
`<parameter name="lattice" units="bohr">`. Convert the QE cell before writing
QMCPACK XML.

## ESHDF Location

`pw2qmcpack.x` typically writes the ESHDF under QE `outdir`, for example:

```text
qe_tmp/qmc_solid.pwscf.h5
```

Keep the QMCPACK `href` pointed at the real generated file.
