# Lei Wang — curated notes

Thematic map of this advisor's literature cache, for grounding brainstorming comments.
The unifying thread across all of it is **variational / generative methods as a computational engine for many-body physics** — "free energy minimization from Nature to LLM."

## Sub-themes

### Machine learning for phase recognition & RG
- *Discovering phase transitions with unsupervised learning* (2016) — the founding paper; unsupervised detection of order parameters.
- *Neural Network Renormalization Group* (2018) — normalizing flows realize an exact, invertible RG transformation.

### Variational autoregressive & generative models for statistical mechanics
- *Solving Statistical Mechanics using Variational Autoregressive Networks* (2018) and the quantum extension *…with Variational Autoregressive Networks and Quantum Circuits* (2019) — direct variational free-energy minimization with tractable normalization.
- *Unsupervised Generative Modeling Using Matrix Product States* (2017) — tensor networks as generative models.
- *Monge-Ampère Flow* (2018), *Neural Canonical Transformation with Symplectic Flows* (2019) — structure-preserving flows; enforce known symmetries/constraints exactly rather than learning them.

### Deep variational free energy for ab initio many-body physics
- *Deep Variational Free Energy Approach to Dense Hydrogen* (2022) — flagship application to a real material at finite temperature.

### Quantum Monte Carlo
- *Fidelity Susceptibility Made Simple* (2015) — unified QMC estimator.
- *Fermionic quantum critical point of spinless fermions on a honeycomb lattice* (2014) — sign-problem-free fermionic QMC.

### Differentiable programming & tensor networks
- *Differentiable Programming Tensor Networks* (2019, PRX) — backprop through tensor-network contraction; the methodological cornerstone.
- *Automatic differentiation for second renormalization of tensor networks* (2019), *AD of dominant eigensolver* (2020), *Tropical Tensor Network for Ground States of Spin Glasses* (2020), *Continuous MPO for finite-temperature states* (2020), *Diff. programming TN for Kitaev magnets* (2023).

### Generative models for materials & quantum software
- *Space Group Informed Transformer for Crystalline Materials Generation* (CrystalFormer, 2024) — autoregressive crystal-structure generation respecting symmetry.
- *Variational Benchmarks for Quantum Many-Body Problems* (Science 2023) — community benchmark suite.
- *Yao.jl* (2019), *Variational Quantum Eigensolver with Fewer Qubits* (2019), *Differentiable Learning of Quantum Circuit Born Machine* (2018) — the QuantumBFS software/algorithm line.
- *Equivariant neural network for Green's functions* (2023) — symmetry-equivariant ML for correlated electrons.

## Open problems / recurring concerns (how this advisor attacks ideas)
- **Enforce known constraints exactly, don't learn them** — initial/boundary conditions, symmetries, normalization should be architectural, not approximated.
- **Demand the mathematical justification** of any empirical trick before trusting it; ask whether the principle generalizes.
- **Necessary vs sufficient** — when many factors vary at once, design ablations to find which are causally necessary.
- **Cross-domain transfer** — partition functions, fixed-point iteration, mixing-time arguments recur across QMC, RL (target networks), and generative models; look for the shared mathematical structure.
- **Scaling variational free energy** to larger systems and to ab initio settings remains the open frontier.
