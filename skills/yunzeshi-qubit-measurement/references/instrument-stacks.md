# Common Instrument Stacks

Use this reference when the user asks about devices, setup architecture, procurement categories, or what hardware implements a technique. Do not substitute brand names for functional requirements unless the user asks for a vendor-specific plan.

## TAS

**Functional chain**

Ultrafast laser → beam split → tunable pump generation → pump modulation → variable pump–probe delay → broadband probe generation → sample → reference/signal spectrometer and detector → synchronized acquisition and kinetic analysis.

**Typical subsystems**

- femtosecond amplifier and timing reference;
- OPA/OPG or harmonic generation for the pump;
- optical chopper or electronic modulation;
- mechanical delay stage or asynchronous timing method;
- white-light supercontinuum or narrowband probe;
- polarization optics, beam diagnostics, and calibrated fluence measurement;
- cryostat, magnet, vacuum, or inert sample environment as required;
- spectrograph with array detector and shot-to-shot referencing;
- chirp correction, coherent-artifact checks, global/target analysis, and residual inspection.

**Minimum controls**

Pump-off/reference stability, fluence dependence, sample-only/background measurements, polarization/magic-angle condition where appropriate, repeated scans for degradation, time-zero/chirp calibration, and a kinetic model whose residuals and uncertainty are reported.

## EPR

**Functional chain**

Static magnetic field + microwave source/bridge → resonator or transmission structure containing the sample → phase-sensitive microwave detection → field/frequency and pulse-sequence control → signal averaging and spin-Hamiltonian/relaxation analysis.

**Typical subsystems**

- electromagnet or superconducting magnet with field controller;
- microwave synthesizer/bridge, amplifier, attenuators, and phase control;
- resonator, cavity, loop-gap resonator, or on-chip line;
- cryostat and temperature controller;
- pulse programmer/AWG, digitizer, and transient recorder for pulsed EPR;
- optical access and synchronized laser for photo-EPR or transient EPR;
- field calibration and spin-standard capability.

**Protocol-to-quantity examples**

- CW field/frequency sweep → resonance positions, linewidths, g/ZFS/hyperfine model;
- inversion or saturation recovery → T1;
- two-pulse Hahn echo → phase-memory T2 under that sequence;
- nutation/Rabi → driven coherent rotations;
- ESEEM, ENDOR, HYSCORE, or DEER → local hyperfine or distance constraints when relevant.

**Minimum controls**

Blank/diamagnetic host, concentration dependence, field calibration, resonator Q/bandwidth, pulse calibration, repetition time relative to T1, orientation selection, temperature stability, and fit-model comparison.

## ODMR

**Functional chain**

Optical excitation and collection + microwave generation/delivery + static field + pulse synchronization → photon detection → resonance/sequence-dependent optical contrast.

**Typical subsystems**

- CW or pulsed laser with wavelength and linewidth appropriate to the optical transition;
- confocal, wide-field, fiber, or cavity-enhanced optical path;
- filters, dichroics, polarization control, and objective/sample positioning;
- photon counter, APD/SPAD, PMT, camera, or spectrometer;
- microwave synthesizer, switch/IQ modulation, amplifier, and antenna/resonator;
- magnet/coil set and field alignment;
- pulse generator/AWG and time-tagging/counting electronics;
- cryostat or controlled-atmosphere sample stage as needed.

**Minimum controls**

Laser-only and microwave-only baselines, optical and microwave power dependence, field dependence, detuning/phase checks for coherent control, detector linearity, heating assessment, charge-state/photobleaching stability, and photon-statistics analysis for fidelity claims.

## FSRS

**Functional chain**

Femtosecond source → actinic pump + narrowband picosecond Raman pump + broadband femtosecond probe → controlled relative delays and polarizations → sample → spectrograph/array detector → Raman-gain/loss extraction and time-dependent mode analysis.

**Typical subsystems**

- femtosecond amplifier;
- tunable actinic-pump generation;
- narrowband Raman-pump generation by spectral compression, pulse shaping, or a picosecond OPA;
- broadband probe generation;
- independent delay stages and modulation for beam combinations;
- polarization optics, overlap diagnostics, and calibrated pulse energies;
- high-dynamic-range spectrograph and array detector;
- sample translation/flow and environmental control;
- baseline, ground-state bleach, cross-phase-modulation, and lineshape analysis.

**Minimum controls**

All relevant beam-on/beam-off combinations, solvent/substrate background, Raman-pump and actinic-pump power dependence, temporal-overlap scans, polarization dependence, ground-state Raman reference, repeated scans for damage, and explicit inspection for dispersive or negative artifact features.

## Selection notes

- Match temporal range to the physics: femtoseconds–nanoseconds for ultrafast population/structure, microseconds–seconds for many spin-relaxation processes.
- Match sensitivity to the sample: an ensemble EPR spectrometer, confocal ODMR microscope, and single-emitter photonic device are not interchangeable.
- Match bandwidth to the spin Hamiltonian and pulse duration. A nominal microwave frequency range does not guarantee uniform coherent rotations across a broad or anisotropic spectrum.
- Plan multimodal registration when correlating structure and spin: use the same batch, host, concentration, temperature, field, excitation conditions, and damage history where possible.
- Report functional specifications before vendor/model names so the plan remains portable.
