# Technique-to-Qubit-Feature Matrix

Use this reference when selecting techniques, comparing evidence, or correcting a measurement summary. The matrix is a starting point; the exact pulse sequence, sample state, temperature, field, and signal model determine what can actually be claimed.

## Corrected summary of the source slide

The four methods are complementary:

- **TAS** resolves photoexcited populations and kinetic pathways, making it useful for screening optical initialization dynamics, but it is not intrinsically spin-selective.
- **EPR** directly detects paramagnetic resonances; pulsed protocols quantify spin relaxation and coherence and can demonstrate microwave control.
- **ODMR** converts magnetic resonance into an optical signal, linking optical initialization/readout to spin manipulation and enabling high spatial sensitivity when the platform supports sufficient contrast.
- **FSRS** adds ultrafast vibrational and structural dynamics, helping connect molecular motion to optical or spin behavior, but it is a complementary structural probe rather than a direct measure of qubit memory, readout fidelity, or gate operation.

The strongest strategy combines optical kinetics, direct spin resonance, and structural dynamics instead of asking one method to establish every qubit requirement.

## Core matrix

| Technique and protocol | Primary observable | Strongest qubit use | Evidence level | Typical limitations and confounders |
|---|---|---|---|---|
| Broadband TAS / pump–probe | Differential absorption versus wavelength and delay; excited-state absorption, ground-state bleach, stimulated emission, kinetic components | Screen optical excitation, population transfer, excited-state lifetime, and candidate initialization pathways | Direct for optical population kinetics under an assignment model; supporting for spin identity or polarization | Spectral congestion, chirp, coherent artifacts near time zero, pump scatter, photodegradation, non-unique global fits, and no intrinsic spin label |
| Time-resolved or transient EPR | Field/frequency-resolved paramagnetic signal and non-Boltzmann spin polarization | Establish paramagnetic state formation, spin Hamiltonian, and transient polarization after excitation | Direct spin-sensitive evidence when the species is resolved and assigned | Ensemble averaging, orientation selection, sensitivity, time resolution, overlap of species, resonator bandwidth, and sample heating |
| CW EPR | Resonance field/frequency, linewidth, g tensor, zero-field and hyperfine structure | Identify addressable spin transitions and characterize the spin Hamiltonian | Direct for resonances; model-dependent for microscopic assignment | Does not by itself establish coherent control, T1, T2, or single-qubit readout |
| Pulsed EPR: inversion/saturation recovery | Recovery of longitudinal magnetization | T1 and relaxation pathways | Direct within the pulse sequence and fit model | Spectral diffusion, instantaneous diffusion, repetition-rate bias, pulse selectivity, and multiexponential decay |
| Pulsed EPR: Hahn echo / dynamical decoupling | Echo amplitude versus interpulse delay | Phase-memory/coherence time and decoupling response | Direct within the named sequence; sequence-dependent | T2 is not T2*; concentration, nuclear spins, pulse errors, orientation, and stretched/multiexponential fits matter |
| Rabi / nutation in EPR or ODMR | Coherent oscillation versus pulse duration or amplitude | Demonstrate coherent microwave control and calibrate rotations | Direct evidence of driven coherent response | Inhomogeneous driving, detuning, heating, pulse distortion, and ensemble dephasing |
| CW ODMR | Spin-dependent photoluminescence or fluorescence versus microwave frequency/field | Demonstrate an optical–spin interface and locate resonances | Direct for optically detected resonance; supporting for initialization fidelity | Optical background, low contrast, charge/photophysical dynamics, heating, power broadening, and ambiguous sign of contrast |
| Pulsed ODMR | Time-gated photon counts after optical and microwave pulse sequences | Optical initialization/readout, Rabi control, T1, echo, and decoupling when implemented with the corresponding protocol | Direct for the protocol-specific observable | Readout fidelity requires photon statistics and a declared metric; ensemble ODMR is not single-spin readout |
| FSRS | Raman gain/loss spectra versus delay; vibrational frequencies, linewidths, and structural marker evolution | Correlate ultrafast structural motion with state conversion, relaxation, or optical contrast | Direct for vibrational dynamics under assignments; correlative for qubit performance | Cross-phase modulation, fluorescence/background subtraction, pump overlap artifacts, resonance effects, mode congestion, photodamage, and complex lineshapes |

## Claim-to-measurement routing

| Claim | Minimum persuasive measurement | Useful complement |
|---|---|---|
| Photoexcitation creates a long-lived excited population | TAS or time-resolved photoluminescence with kinetic and spectral assignments | Fluence dependence, oxygen/temperature controls, transient EPR |
| The populated state has triplet or other paramagnetic character | Transient EPR, spin-sensitive ODMR, or another direct magnetic-resonance signature | TAS kinetic model and sensitization/quenching controls |
| Optical pumping initializes a non-thermal spin population | Time-resolved EPR polarization or pulsed ODMR with a population-sensitive sequence | Polarization dependence and field/temperature controls |
| A transition is microwave addressable | CW EPR or CW ODMR with field/frequency dependence | Spin-Hamiltonian simulation and orientation dependence |
| The state can be coherently manipulated | Rabi/nutation oscillations with phase/power/detuning checks | Ramsey or randomized benchmarking when available |
| The qubit has a stated T1 | Inversion/saturation recovery or a validated optical pump–probe relaxation sequence | Temperature and field dependence; phonon measurements |
| The qubit has a stated T2 | Hahn echo or explicitly named coherence sequence | Ramsey for T2*, decoupling series, concentration and isotope controls |
| Readout is high fidelity or single shot | Declared assignment-fidelity/SNR analysis from repeated single-event measurements | Photon-count histograms, confusion matrix, detector calibration |
| Molecular motion limits coherence | Correlated temperature/isotope/host dependence plus spin relaxation/coherence measurements | FSRS, Raman, infrared, inelastic neutron scattering, or calculation of relevant modes |
| A structural change accompanies photoexcitation | FSRS or another time-resolved structural probe with mode assignment | TAS for electronic populations and computation/static spectroscopy for assignment |

## Presentation-ready wording

Use this concise version when a slide needs four rows:

| Technique | What it contributes | Qubit feature | Main caution |
|---|---|---|---|
| TAS | Ultrafast excited-state populations and lifetimes | Screens optical-initialization pathways | Spin assignment requires a spin-sensitive measurement |
| EPR | Spin resonances, Hamiltonian parameters, T1/T2, and microwave control with pulse protocols | Addressability, coherence, memory, and control | Mostly ensemble-based; sensitivity and sample conditions matter |
| ODMR | Spin-dependent optical contrast under microwave resonance | Optical initialization/readout and coherent control | Contrast is not automatically high-fidelity or single-spin readout |
| FSRS | Femtosecond vibrational and structural dynamics | Structure–property correlation and relaxation mechanism | Complementary; artifacts and mode assignments must be controlled |

## Scientific anchors

- He et al., “Transient absorption spectroscopy,” *Nature Reviews Methods Primers* (2026), [doi:10.1038/s43586-026-00488-1](https://doi.org/10.1038/s43586-026-00488-1).
- Takahashi et al., “Pulsed electron paramagnetic resonance spectroscopy powered by a free-electron laser,” *Nature* (2012), [doi:10.1038/nature11437](https://doi.org/10.1038/nature11437).
- Bayliss et al., “Optically addressable molecular spins for quantum information processing,” *Science* (2020), [doi:10.1126/science.abb9352](https://doi.org/10.1126/science.abb9352).
- Batignani et al., “Femtosecond stimulated Raman spectroscopy,” *Nature Reviews Methods Primers* (2024), [doi:10.1038/s43586-024-00314-6](https://doi.org/10.1038/s43586-024-00314-6).
- Lynch et al., “Mastering Femtosecond Stimulated Raman Spectroscopy: A Practical Guide,” *ACS Physical Chemistry Au* (2023), [doi:10.1021/acsphyschemau.3c00031](https://doi.org/10.1021/acsphyschemau.3c00031).
- Luis et al., “Heterodimetallic [LnLn′] Lanthanide Complexes: Toward a Chemical Design of Two-Qubit Molecular Spin Quantum Gates,” *JACS* (2014), [doi:10.1021/ja507809w](https://doi.org/10.1021/ja507809w).

Treat these as methodological anchors, not proof that a claim holds for the user’s material. Cite the system-specific paper or data for system-specific conclusions.
