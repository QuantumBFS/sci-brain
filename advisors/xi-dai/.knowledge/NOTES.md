# Xi Dai — curated notes

Thematic map of this advisor's literature cache, for grounding brainstorming comments.
The through-line is **first-principles prediction of topological materials**: take a real compound, compute its band structure (DFT, often LDA+Gutzwiller for correlations), extract a topological invariant, and predict an experimentally observable signature.

## Sub-themes

### Topological insulators (the founding line)
- *Topological insulators in Bi2Se3, Bi2Te3 and Sb2Te3 with a single Dirac cone* (Nat. Phys. 2009) — the prediction; *Experimental Realization … Bi2Te3* (Science 2009) confirms it.
- *Model Hamiltonian for topological insulators* (2010) — the effective 4-band model used everywhere downstream.
- *Crossover of Bi2Se3 to the 2D limit* (2009) — thin-film thickness dependence.

### Quantum anomalous Hall effect
- *Quantum anomalous Hall effect in Hg1-yMnyTe quantum wells* (2008) — early proposal.
- *Quantized Anomalous Hall Effect in Magnetic Topological Insulators* (Science 2010) — the prediction; *Experimental Observation of the QAHE* (Science 2013) confirms it.
- *Chern semimetal and the quantized anomalous Hall effect in HgCr2Se4* (2011).
- Review: *Quantum anomalous Hall effect and related topological electronic states* (Adv. Phys. 2015).

### Weyl & Dirac semimetals
- *Weyl Semimetal Phase in Noncentrosymmetric Transition-Metal Monophosphides* (PRX 2015) — predicts TaAs as the first Weyl semimetal; confirmed in *Observation of Weyl nodes in TaAs* (2015) and *Chiral-anomaly negative magnetoresistance in TaAs* (2015).
- *Type-II Weyl semimetals* (Nature 2015) and *MoTe2: a Type-II Weyl topological metal* (2015) — tilted Weyl cones.
- Dirac semimetals: *A3Bi (Na,K,Rb)* (2012), *Discovery of Na3Bi* (Science 2013), *Three-dimensional Dirac semimetal and quantum transport in Cd3As2* (2013), *A stable 3D topological Dirac semimetal Cd3As2* (Nat. Mater. 2014).
- *Multi-Weyl topological semimetals stabilized by point group symmetry* (2011); *Three-component fermions … in tungsten carbide* (2017) — beyond-Weyl band crossings.

### Nodal-line semimetals
- *Topological node-line semimetal in 3D graphene networks* (2014), *…in antiperovskite Cu3PdN* (2015); reviews *Topological nodal line semimetals* (2016) and *Topological semimetals predicted from first-principles* (2016).

### Methods & invariants
- *LDA+Gutzwiller method for correlated electron systems* (2008) — the correlation-aware DFT engine.
- *Equivalent expression of Z2 invariant using the non-Abelian Berry connection* (2011) and *Wilson-loop characterization of inversion-symmetric topological insulators* (2012) — how invariants are actually computed.

### Correlated & moiré topology
- *Correlated topological insulators with mixed valence* (2012) — topological Kondo (SmB6-type).
- *Pseudo Landau level representation of twisted bilayer graphene* (2018) and *Heavy-fermion representation for twisted bilayer graphene* (2022) — the heavy-fermion view of magic-angle TBG.
- *Topological charge pumping in a 1D optical lattice* (2013, with Lei Wang) — cold-atom realization.

## Open problems / recurring concerns (how this advisor attacks ideas)
- **Geometry and boundary conditions decide everything** — periodic vs open boundaries, sample thickness vs a characteristic length can flip which physics (and which method) applies. Check limiting cases first.
- **Hidden assumptions in the band picture** — when a prediction relies on a symmetry or a gap, ask what breaks it.
- **Predict an observable** — a topological claim is only useful if it maps to ARPES, transport (chiral anomaly, QAHE plateau), or a spectroscopic fingerprint.
- **Correlations beyond DFT** — when LDA fails, LDA+Gutzwiller / heavy-fermion mappings are the route; the frontier is correlated and moiré topology.
- **Sign/symmetry bookkeeping** — invariant computations are error-prone; cross-check Z2 via Wilson loops.
