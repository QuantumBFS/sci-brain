# Survey: Agent Memory, Continual Learning & Catastrophic Forgetting in LLM-Based Agents

**Date:** 2026-03-02
**Papers:** 58 entries across 11 themes
**Focus:** LLM-based agents with parameter updates (LoRA, adapter tuning, experience replay) and catastrophic forgetting mitigation

---

## Field Landscape

### A. Surveys & Roadmaps

Comprehensive surveys establishing the taxonomy and scope of continual learning for LLMs:

- [Shi2025continual] — Definitive survey: CPT/DAP/CFT taxonomy, vertical vs. horizontal CL (ACM Computing Surveys 2025)
- [Zheng2025lifelong] — Internal vs. External Knowledge taxonomy, 12 scenarios (ACM Computing Surveys 2025)
- [Zheng2025roadmap] — First survey targeting LLM-based *agents* specifically: perception/memory/action modules (IEEE TPAMI 2025)
- [Zhang2025memory] — Agent memory taxonomy: sensory, working, long-term parametric, long-term external (ACM TOIS 2025)
- [vandeVen2024continual] — Canonical review of continual learning fundamentals and catastrophic forgetting (2024)

### B. LoRA / Adapter-Based Continual Learning (dominant 2023-2025 approach)

Parameter-efficient methods that train task-specific low-rank adapters while preventing cross-task interference:

**Orthogonal subspace methods:**
- [Wang2023OLoRA] — O-LoRA: tasks in orthogonal low-rank subspaces (EMNLP 2023 Findings)
- [Liang2024InfLoRA] — InfLoRA: interference-free subspace reparameterization (CVPR 2024)
- [Wan2025OAAdapter] — OA-Adapter: dynamic rank + orthogonal constraints, end-to-end (arXiv 2025)
- [Lu2025CLoRA] — CLoRA: null-space direction regularization on LoRA (ACL 2025)

**Hierarchical and structured approaches:**
- [Qian2025TreeLoRA] — TreeLoRA: layer-wise LoRAs organized by gradient-similarity tree (ICML 2025)
- [Qiao2024LearnMore] — Sensitivity-based initialization + gradient projection (NeurIPS 2024)

**Shared attention and masking:**
- [Zhao2024SAPT] — SAPT: shared attention aligning PET learning and selection (ACL 2024)
- [Kang2024SoftTF] — Soft-TransFormers: soft parameter masking per task (arXiv 2024)

**Modular composition:**
- [Wang2024MoCL] — MoCL: rehearsal-free modular composition (NAACL 2024)

**Analysis:**
- [Ren2024ILoRA] — I-LoRA: mode connectivity analysis + dual-memory LoRA interpolation (arXiv 2024)

### C. Replay & Rehearsal Methods

Storing or generating examples from prior tasks for interleaved training:

- [Rolnick2019ExperienceReplay] — CLEAR: foundational replay for RL continual learning (NeurIPS 2019)
- [Huang2024SelfSynthesizedRehearsal] — SSR: LLM generates own synthetic rehearsal data (ACL 2024)
- [Liu2025ContextualExperienceReplay] — CER: training-free context-window replay for web agents, SOTA 31.9% on VisualWebArena (ICLR 2025)
- [Hazard2025SuRe] — SuRe: surprise-driven selection + dual fast/slow LoRA learners (arXiv 2025)
- [Borhanifard2025ERILoRA] — ERI-LoRA: replay + LoRA hybrid for NLU (Computer Speech & Language 2025)

### D. Regularization & Loss-Landscape Methods

Penalty terms or optimization strategies protecting important weights:

- [Kirkpatrick2017overcoming] — EWC: Fisher-information-based quadratic penalty (PNAS 2017) — foundational
- [Sliogeris2025EWCGemma2] — EWC at full-parameter scale for Gemma2 continual pretraining (arXiv 2025)
- [Li2024RevisitingCatastrophicForgetting] — Loss landscape flatness → forgetting severity; SAM as mitigation (EMNLP 2024 Findings)

### E. Model Merging

Post-hoc combination of independently fine-tuned models via weight arithmetic:

- [Ilharco2023TaskArithmetic] — Task Arithmetic: task vectors via weight subtraction, composable via addition/negation (ICLR 2023)
- [Alexandrov2024ModelMergingLanguageTransfer] — Branch-and-Merge (BaM): iterative merging for language transfer (EMNLP 2024 Findings)
- [Daheim2024ModelMergingGradient] — Uncertainty-based gradient matching for merge quality (ICLR 2024)

### F. MoE & Dynamic Routing

Mixture-of-experts with per-task adapters and learned routing:

- [Ge2025DynamicMixtureCurriculumLoRA] — D-MoLE: dynamic layer-wise LoRA expert allocation + curriculum (ICML 2025)
- [Yu2024BoostingContinualLearningMoE] — MoE adapters for CLIP + distribution-discriminative routing (CVPR 2024)
- [Wang2025MixtureLoRAExpertsEMNLP] — Token-level LoRA expert routing for continual IE (EMNLP 2025 Findings)
- [Araujo2024L2R] — L2R: learned router composing isolated PEFT modules (arXiv 2024)

### G. Gradient-Free / Training-Free Continual Learning

Avoiding parameter updates entirely:

- [Li2025JitRL] — JitRL: non-parametric trajectory memory → logit corrections, 30x cheaper than fine-tuning (arXiv 2025)
- [Wu2025AgentDice] — Agent-Dice: geometric consensus filters conflicting gradients (arXiv 2025)

### H. Prompt-Based Methods

Frozen backbone + learned prompt tokens:

- [Razdaibiedina2023ProgressivePrompts] — Progressive Prompts: sequential concatenation, >20% improvement over prior SOTA (ICLR 2023)
- [Wang2022L2P] — L2P: dynamic prompt pool with query-key matching (CVPR 2022)

### I. Memory-Augmented Methods

External or semi-external memory stores:

- [Wang2023LongMem] — LongMem: frozen backbone + side-network for 65k-token memory retrieval (NeurIPS 2023)
- [Fountas2025EMLLM] — EM-LLM: Bayesian surprise-based episodic memory, processes 10M tokens (ICLR 2025)
- [Ai2025MemoryBench] — MemoryBench: benchmark for LLM memory + continual learning from user feedback (arXiv 2025)

### J. Cross-Field Analogues

Same structural problem, different vocabulary:

**Transfer learning / Negative transfer:**
- [Zhang2023NegativeTransfer] — Survey of 50+ negative transfer approaches (IEEE/CAA JAS 2023)
- [Holton2025Humans] — Humans and ANNs share the transfer-interference tradeoff (Nature Human Behaviour 2025)

**Federated continual learning:**
- [Zhang2023TARGET] — TARGET: exemplar-free distillation under non-IID (ICCV 2023)
- [Bakman2023FedOrth] — Federated Orthogonal Training: gradient subspace projection (ICLR 2024)
- [Hamedi2025FedCL] — FCL survey: global/local forgetting, client drift (Neurocomputing 2025)

**Robotics / Lifelong RL:**
- [Meng2025LEGION] — LEGION: Bayesian non-parametric skill composition (Nature Machine Intelligence 2025)
- [Liu2023LIBERO] — LIBERO: 130-task benchmark for lifelong robot manipulation (NeurIPS 2023)
- [Yang2024TaskAgnostic] — Task-free lifelong robot learning via retrieval-based adaptation (arXiv 2024)

**Multi-task interference:**
- [Ding2023ETR] — ETR-NLP: explicit task routing with non-learnable primitives (CVPR 2023)
- [Leng2024TaskNeurons] — Task-specific neuron detection and overlap analysis in LLMs (arXiv 2024)
- [Wu2025ImbalancedGradients] — Gradient imbalance in RL post-training of multi-task LLMs (arXiv 2025)

### K. Historical Foundations

The intellectual lineage of catastrophic forgetting:

**Foundational era (1989-1999):**
- [McCloskey1989catastrophic] — Named the phenomenon: catastrophic interference in connectionist networks
- [Ratcliff1990connectionist] — Independent confirmation in recognition memory models
- [French1999catastrophic] — Canonical review; two-area hypothesis (hippocampus + neocortex)

**Deep learning era (2016-2018):**
- [Li2018learning] — Learning without Forgetting: knowledge distillation baseline
- [Rusu2016progressive] — Progressive Neural Networks: frozen columnar architecture
- [LopezPaz2017gradient] — GEM: gradient-constrained replay
- [Rebuffi2017icarl] — iCaRL: exemplar-based class-incremental learning
- [Mallya2018packnet] — PackNet: pruning-based parameter isolation

**LLM transition:**
- [Jin2022LifelongPretraining] — Lifelong pretraining: temporal/domain/language shift taxonomy (NAACL 2022)
- [Luo2023CatastrophicForgettingLLM] — First large-scale empirical study of CF in decoder LLMs (arXiv 2023)

---

## Key Open Problems

1. **Agent-level vs. LLM-level forgetting** — Most methods target the LLM backbone; forgetting in tool use, planning strategies, and world models is underexplored. Only [Zheng2025roadmap] and [Ai2025MemoryBench] begin to address this gap.

2. **Task-boundary-free continual learning** — Real agents don't receive clean task delimiters. The task-free setting ([Yang2024TaskAgnostic] in robotics) is largely absent from LLM-agent CL literature.

3. **Rank allocation theory** — Adaptive rank methods ([Wan2025OAAdapter]) outperform fixed rank, but no principled theory explains optimal rank allocation per layer per task.

4. **Replay without stored data at scale** — SSR generates synthetic rehearsal but synthetic samples drift from real distributions over long task sequences. SuRe's surprise-based selection helps but doesn't solve the data-free setting.

5. **Gradient-free vs. parametric CL tradeoffs** — JitRL and CER avoid weight updates entirely but depend on trajectory memory quality; no systematic comparison exists at deployment scale.

6. **Multimodal continual learning** — [Ge2025DynamicMixtureCurriculumLoRA] touches this, but interaction between vision encoder and LLM backbone updates in sequential tasks is largely unsolved.

7. **The fundamental stability-plasticity limit** — [Holton2025Humans] suggests perfect retention with full plasticity may be mathematically impossible with shared parameters. No single method simultaneously achieves zero forgetting, forward transfer, no replay storage, and constant parameter count.

---

## Key Bottlenecks

- **Fisher computation at scale**: EWC requires estimating the Fisher information matrix over billions of parameters, making it expensive even with diagonal approximations
- **Subspace exhaustion**: Orthogonal methods (O-LoRA, InfLoRA) eventually run out of orthogonal directions as task count grows
- **Routing accuracy**: MoE methods depend on correct task-routing at inference; misrouting degrades both old and new task performance
- **Evaluation fragmentation**: No unified benchmark covers all CL settings (CPT, CFT, agent-level) — different papers use incompatible setups

---

## Temporal Trends

| Period | Dominant approach | Key shift |
|--------|------------------|-----------|
| 1989-2016 | Problem identification | Naming the phenomenon, biological analogies |
| 2017-2020 | EWC, replay, progressive nets | Canonical algorithm families established |
| 2021-2022 | Prompt-based (L2P), lifelong pretraining | Frozen backbone paradigm; scale changes the problem |
| 2023-2024 | LoRA-based orthogonal methods, model merging | PEFT dominates; post-hoc merging as alternative |
| 2025 | MoE routing, gradient-free CL, agent-specific | Agent-level forgetting recognized; training-free methods emerge |
