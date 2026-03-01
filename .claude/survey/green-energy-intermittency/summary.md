# Survey: Green Energy Intermittency — Materials and Algorithms

**Date:** 2026-03-01
**Focus:** How can better materials and better algorithms solve the intermittency problem in renewable energy?

## Field Landscape

### A. Battery & Storage Materials

**Grid-scale battery technologies** are the primary hardware approach to intermittency. The field is diversifying beyond lithium-ion:

- [Jiang2025] — Nature Reviews Clean Technology survey of battery technologies for grid-scale storage: Li-ion (LFP), sodium-ion, vanadium redox flow, high-temperature, and gas batteries. Li-ion costs dropped from $800/kWh (2013) to <$140/kWh (2023).
- [Jacobson2024] — Modeling 145 countries: batteries + hydropower always cheaper than hydrogen alone; integrated infrastructure reduces cost. CH + GHS is never lowest cost without batteries.
- [Gulraiz2025] — Comprehensive review of hydrogen and battery storage integration for renewables, covering AI/ML for energy management.
- [Huang2022] — Key challenges for grid-scale Li-ion BESS: lithium reserve limits, degradation, inability to do seasonal storage cost-effectively.

**Sodium-ion** (2024-2025 trend):
- CATL, HiNa commercializing at 175 Wh/kg, 20-30% cheaper than Li-ion
- IRENA 2025 technology brief projects growing market share
- MIT Technology Review named it 2026 breakthrough technology
- Solid-state sodium-air achieving 86% energy efficiency [Sun2025]

**Iron-air** (emerging, 2024-2025):
- Form Energy: reversible rusting, targeting <$20/kWh, 100-hour duration
- PacifiCorp plans 3,073 MW by 2045
- Ore Energy: first grid-connected iron-air battery (Netherlands, 2025)
- Passed UL9540A safety testing with no thermal event propagation

### B. Green Hydrogen & Electrolysis Materials

Current bottleneck: round-trip efficiency ~36%, costs $4-12/kg vs. $1-2/kg conventional.

- [Zhang2025] — AEM water electrolysis review: combines PEM zero-gap design with alkaline environment, enabling earth-abundant catalysts.
- [Kumar2025] — Catalyst advances: single-atom catalysts (37.4x mass activity vs. commercial Pt/C), transition metal alternatives, MOF-based catalysts.
- [GreenH2Review2025] — Green hydrogen production via electrolysis: materials innovation, system integration, global deployment pathways.
- Non-precious FeCoNiPx catalysts achieving 72 mV overpotential at 10 mA/cm²
- Seawater electrolysis: direct ocean water use, but chlorine evolution reaction remains a challenge

### C. ML/AI for Forecasting & Grid Optimization

- [Ponse2024] — RL for Sustainable Energy survey: systematically catalogs decision-making problems across wind farms, grid management, EV charging as RL problems. Emphasizes multi-agent, offline, and safe RL.
- [Ukoba2024] — AI for optimizing renewable systems: 15% grid efficiency improvement, 10-20% battery storage efficiency gains.
- [Singh2024] — ML-based energy management in grid-connected microgrids: LSTM and CNN for spatiotemporal forecasting, SVR achieving MSE 2.002 (solar) and 3.059 (wind).
- [RESIntegration2024] — Systematic review of ML for renewable integration: deep ANNs and ensemble methods best suited for RES forecasting.
- [DRLReview2025] — Comprehensive DRL review (500+ papers, 2020-2026): value-based, policy-based, actor-critic, model-based approaches for dispatch, pricing, load balancing, demand response.

### D. Model Predictive Control & Virtual Power Plants

- [Yaghoubi2025] — Data-driven NLMPC with Gaussian Process Regression for microgrid ESS optimization under uncertainty.
- [MPCBESS2025] — Neural network-based MPC for peak shaving: 35% power loss reduction with 24h predictive horizon.
- [MPCReview2024] — Comprehensive MPC analysis for isolated microgrids with storage and renewables.
- [VPP2024] — VPP aggregation of DERs, BESS, EVs, controllable loads for grid resilience.
- [ApproxMPC2025] — Approximate MPC via deep learning for real-time microgrid dispatch scalability.

## Key Open Problems

1. **Long-duration storage economics** — Iron-air and sodium-ion show promise but lack commercial-scale validation at multi-GWh level
2. **Hydrogen round-trip efficiency** — 36% is far below batteries (85-95%); needs fundamental catalyst/membrane breakthroughs to reach viability
3. **Forecasting under extreme weather** — ML models trained on historical data fail during unprecedented climate events
4. **Scalable real-time optimization** — MPC becomes intractable for large interconnected grids; approximate methods (RL, neural MPC) need reliability guarantees
5. **Integrated co-optimization** — Most studies optimize storage OR algorithms independently; joint materials-aware algorithm design is nascent
6. **Degradation-aware dispatch** — Battery dispatch algorithms rarely account for real-time degradation state, leading to suboptimal lifetime costs
7. **Lithium supply constraints** — Proven reserves insufficient for global grid-scale Li-ion; alternative chemistries must scale before Li bottleneck hits

## Key Bottlenecks

1. **Cost gap**: Green hydrogen at $4-12/kg vs. $1-2/kg conventional; iron-air and sodium-ion not yet at scale pricing
2. **Efficiency gap**: Hydrogen round-trip ~36% vs. batteries ~85-95% vs. pumped hydro ~80%
3. **Data scarcity**: ML forecasting models need years of high-resolution weather+grid data; many regions lack this
4. **Regulatory barriers**: VPP aggregation and demand response require market design changes that lag behind technology
5. **Materials supply chains**: Vanadium, lithium, platinum-group metals all face supply concentration risks
