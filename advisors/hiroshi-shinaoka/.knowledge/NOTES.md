# Hiroshi Shinaoka — curated notes

Thematic map of this advisor's literature cache (70 works with DOIs, from the ORCID public record 0000-0002-7058-8765), for grounding brainstorming comments.

## Researcher profile

- **Name:** Hiroshi Shinaoka (Saitama University; homepage https://shinaoka.github.io).
- **Field:** computational condensed-matter physics — strongly correlated electrons, quantum many-body methods, and the numerical infrastructure behind them.
- **Through-line:** **compress first, then compute.** Many-body objects (Green's functions, vertices, propagators in space-time) carry far less information than their naive grids suggest. Find the compact representation (the intermediate-representation (IR) basis, sparse sampling, quantics tensor trains) and the expensive diagrammatic or Monte Carlo calculation becomes cheap enough for real materials.
- **Style:** method papers go out with open-source software (ALPS, CT-HYB, DCore, irbasis, sparse-ir, SpM, and the tensor cross interpolation libraries). Benchmarks on model systems come first, then *ab initio* applications.

## Topic clusters

### Sparse modeling, the IR basis, and sparse-ir
Compact orthogonal bases between imaginary time and real frequency, plus sparse sampling in Matsubara frequencies.
- Foundations: *Compressing Green's function using intermediate representation* (2017) [@shinaoka_2017_compressing]; *Performance analysis of a physically constructed orthogonal representation* (2018) [@chikano_2018_performance]; *Overcomplete compact representation of two-particle Green's functions* (2018) [@shinaoka_2018_overcomplete].
- Sparse sampling: *Sparse sampling approach to efficient ab initio calculations at finite temperature* (2020) [@li_2019_sparse]; *Sparse sampling and tensor network representation of two-particle Green's functions* (2020) [@shinaoka_2019_sparse]; *Solving the Bethe-Salpeter equation with exponential convergence* (2021) [@wallerberger_2020_solving]; *Sparse modeling of large-scale quantum impurity models with low symmetries* (2021) [@shinaoka_2020_sparse].
- Analytic continuation: *Sparse modeling approach to analytical continuation of imaginary-time QMC data* (2017) [@otsuki_2017_sparse]; *SpM* tool (2019) [@yoshimi_2019_spm]; *Bosonic Nevanlinna analytic continuation* (2023) [@nogaki_2023_bosonic].
- Software and reviews: *irbasis* (2019) [@chikano_2018_irbasis]; *sparse-ir* (2023) [@wallerberger_2022_sparse]; *Sparse modeling in quantum many-body problems* (JPSJ review, 2020) [@otsuki_2019_sparse]; *Efficient ab initio many-body calculations based on sparse modeling of Matsubara Green's function* (lecture notes, 2022) [@shinaoka_2021_efficient].
- IR filtering in DMFT: *Smooth self-energy in exact-diagonalization-based DMFT* (2019) [@nagai_2018_smooth].

### Quantics tensor trains (QTT) and tensor cross interpolation (TCI)
The current main line: represent space-time correlation functions as tensor trains over "quantics" bits that resolve exponentially separated scales.
- The ansatz: *Multiscale space-time ansatz for correlation functions based on quantics tensor trains* (PRX 2023) [@shinaoka_2022_multiscale].
- Algorithms and libraries: *Quantics tensor cross interpolation for high-resolution parsimonious representations of multivariate functions* (PRL 2024) [@ritter_2023_quantics]; *Learning tensor networks with tensor cross interpolation: new algorithms and libraries* (2025) [@fernndez_2024_learning]; *Compactness of QTT representations of local imaginary-time propagators* (2025) [@takahashi_2024_compactness]; *Adaptive sampling-based optimization of QTTs for noisy functions* (2025) [@sakaue_2024_adaptive].
- Diagrammatics in QTT form: *Two-particle calculations with QTTs: solving the parquet equations* (2025) [@rohshap_2024_two]; *Low-rank QTT representations of Feynman diagrams for multiorbital electron-phonon models* (2025) [@ishida_2024_low]; *TCI approach for quantum impurity problems based on the weak-coupling expansion* (2025) [@matsuura_2025_tensor].

### Nonequilibrium Green's functions
Using QTTs to cope with two-time memory in Kadanoff-Baym-type calculations.
- *Nonequilibrium diagrammatic many-body simulations with QTTs* (2024) [@murray_2023_nonequilibrium]; *Memory-efficient NEGF framework built on QTTs* (2025) [@roda_2024_memory]; *A causality-based divide-and-conquer algorithm for NEGF with QTTs* (2026) [@inayoshi_2025_causality].

### DMFT and quantum impurity solvers (CT-QMC, DCore, ALPS)
- Hybridization-expansion CT-QMC: *Matrix product formalism and improved sampling* (2014) [@shinaoka_2014_hybridization]; *Negative sign problem in CT-QMC: optimal choice of single-particle basis* (2015) [@shinaoka_2015_negative]; *CT-HYB solver for multi-orbital systems with complex hybridizations* (2017) [@shinaoka_2016_continuous]; *QMC impurity solvers for multi-orbital problems and frequency-dependent interactions* (2017) [@shinaoka_2017_quantum].
- Interaction expansion: *Efficient implementation of the CT-INT method* (2020) [@shinaoka_2018_efficient].
- Infrastructure: *Updated core libraries of the ALPS project* (2017) [@gaenko_2016_updated]; *DCore: integrated DMFT software for correlated electrons* (2021) [@shinaoka_2021_dcore].
- Physics from impurity/DMFT: *Fidelity susceptibility perspective on the Kondo effect* (PRL 2015) [@wang_2015_fidelity]; *A spin-freezing perspective on cuprates* (2016) [@werner_2016_spin]; *Strong-coupling formula for momentum-dependent susceptibilities in DMFT* (2019) [@otsuki_2018_strong]; *Multipolar ordering in the three-orbital Hubbard model* (2021) [@chikano_2021_multipolar]; *Multipolar ordering from DMFT with application to CeB6* (2024) [@otsuki_2022_multipolar].

### Ab initio correlated materials and cRPA downfolding
- Downfolding methodology: *Accuracy of downfolding based on the constrained RPA* (2015) [@shinaoka_2014_accuracy]; *Limitations of cRPA downfolding* (2018) [@honerkamp_2018_limitations].
- Organics: *Mott transition and phase diagram of κ-(BEDT-TTF)2Cu(NCS)2 from an ab initio 2D model* (2012) [@shinaoka_2011_mott].
- 5d/4d pyrochlores and spin-orbit physics: *Noncollinear magnetism and spin-orbit coupling in Cd2Os2O7* (PRL 2012) [@shinaoka_2011_noncollinear]; *Spin-orbital frustration in molybdenum pyrochlores* (2013) [@shinaoka_2013_spin]; *Phase diagram of pyrochlore iridates: all-in-all-out ordering and non-Fermi-liquid properties* (PRL 2015) [@shinaoka_2015_phase]; *Charge-spin-orbital fluctuations in Cd2Os2O7* (2015) [@uehara_2015_analysis]; *Enhanced thermopower in hole-doped pyrochlore iridates* (2019) [@kaneko_2019_enhanced]; review *First-principles studies of spin-orbital physics in pyrochlore oxides* (2019) [@shinaoka_2018_first].
- Other compounds: *Charge-spin-orbital fluctuations in mixed-valence spinels AlV2O4 and LiV2O4* (2015) [@uehara_2015_charge]; *Material-based analysis of spin-orbital Mott insulators* (2023) [@iwazaki_2023_material]; *Hidden covalent insulator and spin excitations in SrRu2O6* (2023) [@csontosov_2023_hidden]; *Ab initio study on heavy-fermion behavior in LiV2O4: role of Hund's coupling* (2025) [@backes_2024_i].

### Superconductivity and Eliashberg theory
- *Efficient ab initio Migdal-Eliashberg calculation considering the retardation effect* (2020) [@wang_2020_efficient]; *Sparse modeling approach for quasiclassical theory of superconductivity* (2023) [@nagai_2022_sparse]; *Uniform electron benchmark for the first-principles GW0-Eliashberg theory* (2026) [@akashi_2025_uniform]. The electron-phonon QTT work [@ishida_2024_low] also belongs here.

### Frustrated magnetism, spin glasses, and classical Monte Carlo
- Algorithms: *Loop algorithm for classical Heisenberg models with spin-ice type degeneracy* (2010) [@shinaoka_2010_loop]; *... with biquadratic interactions* (2011) [@shinaoka_2011_loop].
- Pyrochlore spin glass: *Spin-glass transition in bond-disordered Heisenberg antiferromagnets coupled with local lattice distortions* (PRL 2011) [@shinaoka_2010_spin]; *Critical property of the spin-glass transition with a biquadratic interaction* (2012) [@shinaoka_2011_critical]; *Effect of magnetoelastic coupling on spin-glass behavior* (2014) [@shinaoka_2014_effect].
- Disorder-induced spirals: *Multiferroic magnetic spirals induced by random magnetic exchanges* (PRX 2018) [@scaramucci_2016_multiferroic]; *Spiral order from orientationally correlated random bonds in classical XY models* (2020) [@scaramucci_2016_spiral].
- Kagome: *Low-temperature phase diagrams of the J1-J2 classical XY kagome antiferromagnet* (2024) [@kakizawa_2023_monte].

### Hybrid quantum-classical algorithms
- *Hybrid quantum-classical algorithm for computing imaginary-time correlation functions* (2022) [@sakurai_2021_hybrid]; *Comparative study on compact quantum circuits of hybrid algorithms for quantum impurity models* (2024) [@sakurai_2023_comparative]; QTT fitting of noisy quantum-simulation data [@sakaue_2024_adaptive].

### Early work: disorder plus correlation
- *Soft Hubbard gaps in disordered itinerant models with short-range interaction* (PRL 2009) [@shinaoka_2008_soft]; *Single-particle excitations in the Anderson-Hubbard model* (2009) [@shinaoka_2009_single]; *Metallic phases under coexisting short-range interaction and diagonal disorder* (2010) [@shinaoka_2009_electronic]; *Theory of electron transport near Anderson-Mott transitions* (2010) [@shinaoka_2010_theory]; *Ill-contact effects of d-orbital channels in nanometer-scale conductors* (2008) [@shinaoka_2008_ill]. An earlier experimental co-authorship on pentacene FETs (2005) [@sekitani_2005_bending] is outside the main line.

## Temporal arc

1. **2008–2010 (PhD era, Univ. Tokyo):** Anderson-Hubbard physics, meaning how disorder and short-range interaction together create soft Hubbard gaps and shape transport near Anderson-Mott transitions. Exact-diagonalization and Hartree-Fock-style numerics.
2. **2010–2014 (frustration and spin-orbit materials):** classical Monte Carlo with custom loop algorithms for pyrochlore spin glasses and magnetoelastic coupling, alongside first-principles work on 5d pyrochlores (Cd2Os2O7, molybdates) and organic Mott systems.
3. **2014–2017 (impurity solvers and correlated materials, incl. ETH Zurich and Fribourg collaborations):** CT-HYB development (sign problem, complex hybridization, ALPS), a critical look at cRPA downfolding, DMFT phase diagram of pyrochlore iridates, Kondo fidelity susceptibility.
4. **2017–2022 (sparse modeling and the IR basis):** the IR basis (2017) becomes the organizing idea. It brings sparse sampling, SpM analytic continuation, irbasis and later sparse-ir, IR-based two-particle and Bethe-Salpeter solvers, and the DCore package. This is the period of ab initio Eliashberg and GW-type finite-temperature calculations at scale.
5. **2022–present (quantics tensor trains and TCI):** the PRX 2023 multiscale QTT ansatz generalizes "compression" from imaginary time to full space-time. TCI libraries, parquet equations, impurity problems, electron-phonon diagrams, memory-efficient and causal NEGF solvers, and QTT-based processing of noisy quantum-computer data follow. Hybrid quantum-classical algorithms for impurity models run in parallel. Ab initio material studies continue (LiV2O4, SrRu2O6, CeB6, GW0-Eliashberg benchmark).

## How this advisor tends to probe ideas

- **What is the information content?** Before scaling a calculation, ask whether the object has a low-rank or sparse structure, and whether it can be stored in IR or QTT form with controlled error.
- **Exponential convergence beats brute force.** He prefers representations whose error falls exponentially with basis size, with no tunable cutoffs that hide bias.
- **Benchmark, then ship.** A method is not finished until it has a reproducible benchmark and an open-source implementation others can use.
- **Downfolding has limits.** Effective models from cRPA or similar schemes need validation. Ask what screening channels or double counting are being mishandled.
- **Bridge model and material.** Results on the Hubbard model should be connected to a real compound through ab initio parameters.
