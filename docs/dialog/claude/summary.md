# Conversation Analysis Summary

- **Sessions analyzed:** 33 (26 debugging, 7 research; 51 skipped as automated/empty/config)
- **Total turns classified:** 854 (784 debugging, 70 research)

## Aggregate Distributions

### Bloom's Cognitive Level
| Tag | Count | % |
|-----|-------|---|
| apply | 331 | 38.8% |
| remember | 184 | 21.5% |
| analyze | 131 | 15.3% |
| evaluate | 127 | 14.9% |
| understand | 57 | 6.7% |
| create | 24 | 2.8% |

### Depth
| Level | Count | % |
|-------|-------|---|
| shallow (procedural + verification + factual) | ~460 | ~54% |
| intermediate (comparison + interpretive) | ~155 | ~18% |
| deep (causal-antecedent + goal + synthesis) | ~150 | ~18% |

### Probe
| Tag | Count | % |
|-----|-------|---|
| none | 700 | 82.0% |
| assumption-probe | 61 | 7.1% |
| evidence-probe | 46 | 5.4% |
| clarification | 28 | 3.3% |
| implication | 13 | 1.5% |
| perspective | 6 | 0.7% |

### Presupposition Quality
| Tag | Count | % |
|-----|-------|---|
| sound | 796 | 93.2% |
| existential-gap | 35 | 4.1% |
| missing-context | 9 | 1.1% |
| ambiguous | 6 | 0.7% |
| loaded | 4 | 0.5% |
| factive-gap | 4 | 0.5% |

### Discourse Function
| Tag | Count | % |
|-----|-------|---|
| referential | 382 | 44.7% |
| indirect-request | 267 | 31.3% |
| conversation-control | 86 | 10.1% |
| display | 43 | 5.0% |
| confirmation-check | 38 | 4.4% |
| clarification-request | 23 | 2.7% |
| rhetorical | 15 | 1.8% |

### Generation Mechanism
| Tag | Count | % |
|-----|-------|---|
| action-coordination | 269 | 31.5% |
| debugging | 196 | 23.0% |
| knowledge-deficit | 131 | 15.3% |
| exploration | 123 | 14.4% |
| conversation-control | 106 | 12.4% |
| common-ground | 28 | 3.3% |

## Presupposition Issues
58 non-sound presuppositions found across sessions. Most common: `existential-gap` (35 instances) — typically asking about job IDs or entities that don't exist as assumed.

## Top Patterns

Lei Wang's conversation style is **strongly directive and execution-oriented**. The dominant pattern is issuing compound action commands (apply + indirect-request + action-coordination = ~32%) followed by monitoring results (remember + referential + knowledge-deficit = ~15%). When problems arise, engagement deepens rapidly to causal analysis (analyze + deep/causal-antecedent + debugging = ~15%). Probing is rare (82% none) but when it appears, it targets assumptions (7%) and evidence (5%) — indicating a researcher who comes with strong hypotheses and tests them against data rather than exploring open-endedly. The 93% sound presupposition rate reflects precise domain knowledge, with gaps mainly on job-specific references (existential-gap 4%) where the user assumes an entity exists or has a property it doesn't.
