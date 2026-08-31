---
name: yunzeshi-qubit-measurement
description: Analyze, compare, and plan spectroscopy and spin-resonance measurements for lanthanide and molecular spin qubits. Use when mapping TAS, EPR, ODMR, FSRS, or related instrument stacks to initialization, control, readout, coherence, and structure; not for generic qubit-platform surveys or raw multidimensional data fitting.
---

# Yunzeshi Qubit Measurement

Turn a proposed qubit feature into an evidence-bounded measurement strategy. Keep the measurement technique, physical observable, instrument hardware, and qubit claim distinct.

## Establish the system before selecting a method

Identify, or clearly mark as unknown:

- host and sample form: molecule, diluted crystal, film, surface, nanostructure, or device;
- lanthanide ion, oxidation state, electron configuration, relevant term/manifold, and isotope nuclear spin;
- qubit basis: ground-state electronic spin, hyperfine/nuclear spin, crystal-field doublet, clock transition, or photoexcited state;
- target operation: initialization, coherent control, readout, storage/coherence, or structure–property correlation;
- operating temperature, magnetic field, concentration, optical wavelength, and ensemble versus single-emitter regime.

Do not silently transfer conclusions between lanthanide complexes, rare-earth ions in crystals, and transition-metal molecular qubits. Their selection rules, relaxation pathways, and addressability can differ materially.

## Map the claim to an observable

1. State the claim to be tested in one sentence.
2. Name the physical observable required to test it.
3. Choose the technique and pulse protocol that directly measure that observable.
4. List the instrument stack and required sample environment.
5. Separate direct evidence from supporting or correlative evidence.
6. Add controls, confounders, and the criterion that would confirm or falsify the claim.

For technique selection or comparison, read [references/technique-matrix.md](references/technique-matrix.md). For hardware and setup descriptions, read [references/instrument-stacks.md](references/instrument-stacks.md).

## Use calibrated evidence language

- **Direct:** the measured channel is the target quantity under the stated model, such as a pulsed-EPR inversion-recovery determination of T1 or a Hahn-echo decay used to estimate T2.
- **Supporting:** the measurement is sensitive to a state or pathway but needs assignments or a complementary modality. TAS evidence for intersystem crossing is normally supporting unless the spin character is independently established.
- **Correlative:** the measurement reveals a change that covaries with qubit performance. FSRS can correlate vibrational or structural evolution with relaxation, but it does not by itself measure qubit memory or gate fidelity.
- **Not established:** the observable cannot answer the claim under the proposed conditions.

Use “shows” or “measures” only for direct evidence. Use “supports,” “is consistent with,” or “correlates with” for assignments that depend on kinetic, spectral, or structural models.

## Preserve important distinctions

- A **technique** is not a device. Name the technique first, then the laser, magnet, microwave chain, resonator/antenna, cryostat, optics, detector, timing electronics, and software that implement it.
- CW spectra characterize resonances and steady-state contrast; pulse sequences determine dynamics. Do not claim T1 or T2 from “EPR” or “ODMR” without naming the relevant protocol.
- T2, Hahn-echo phase-memory time, and T2* are not interchangeable. Report the sequence, fit model, temperature, field, concentration, and uncertainty.
- Optical population kinetics are not automatically spin kinetics. Require spin-sensitive confirmation for spin polarization, triplet identity, or state-selective readout.
- Structural sensitivity is a continuum. EPR/ODMR can reveal g tensors, zero-field splitting, and hyperfine couplings, while FSRS reports vibrational coordinates; none alone guarantees a complete molecular structure.
- Initialization, manipulation, and readout are separate demonstrations. A signal contrast is not automatically single-shot or high-fidelity readout; require the stated fidelity metric and experimental regime.

## Lanthanide-specific checks

- Verify electron count and term symbols instead of inferring them from an analogy. Distinguish Kramers from non-Kramers ions and electronic from hyperfine qubits.
- Treat strong spin–orbit coupling and orbital angular momentum as design variables, not universal advantages: they can enable anisotropy and optical–spin mixing while also opening relaxation channels.
- Verify isotope-specific nuclear spin and abundance before recommending isotopic purification or claiming an I = 0 bath.
- Distinguish parity-forbidden 4f–4f transitions from allowed 4f–5d or charge-transfer transitions; the optical cycle, linewidth, phonon coupling, and photostability implications differ.
- For relaxation claims, account for spin concentration, magnetic dilution, host matrix, phonons, temperature, field orientation, and spectral diffusion.

## Default output

Unless the user requests another format, provide:

1. a one-paragraph conclusion naming the decisive technique and why;
2. a compact table with `Target claim | Observable | Technique/protocol | Evidence level | Key hardware | Controls | Limitation`;
3. a staged plan separating screening, direct spin validation, coherence/control, and structure–property correlation;
4. explicit unknowns and the next experiment that would reduce the largest uncertainty;
5. citations for non-trivial scientific claims and any system-specific performance values.

When summarizing a slide, preserve its intended message but flag technically consequential overstatements. Prefer a corrected, presentation-ready version over repeating inaccurate language.
