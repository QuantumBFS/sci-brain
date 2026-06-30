# Input Sources For QE EPC Examples

The files in this directory are minimal source templates, not a complete runnable
project. Before running them, provide project-specific structure files,
pseudopotentials, executable paths, and cluster settings.

For a run-preparation checklist, use `prepare-qe-todo.md` in this directory.

## Quantum ESPRESSO

- Install or build Quantum ESPRESSO with `pw.x`, `ph.x`, `q2r.x`, `matdyn.x`,
  and `alpha2f.x`.
- The official PHonon input documentation is:
  <https://www.quantum-espresso.org/Doc/INPUT_PH.html>
- QE source trees often include a useful reference under:
  `PHonon/examples/tetra_example/`

## Pseudopotentials

Do not copy UPF files into this skill. Download them into each project or use
the project's existing pseudopotential archive.

- Quantum ESPRESSO pseudopotential portal:
  <https://www.quantum-espresso.org/pseudopotentials>
- SSSP Precision library:
  <https://www.materialscloud.org/discover/sssp/table/precision>
- Materials Cloud SSSP archive:
  <https://archive.materialscloud.org/records/rcyfm-68h65>

These source templates use names from a PdH/PBE/SSSP-precision workflow:

```text
Pd_ONCV_PBE-1.0.oncvpsp.upf
H_ONCV_PBE-1.0.oncvpsp.upf
```

Replace them if your material, functional, or validated cutoff policy differs.

## Structures

Use a relaxed structure from your own workflow. Public crystal databases can
provide starting points, but EPC calculations should not rely on an unrelaxed
database cell. The example inputs use a primitive fcc PdH 2-atom cell with
conventional lattice constant `a = 4.08 A`; each primitive-cell off-diagonal
half-vector component is therefore `a/2 = 2.04 A`.
