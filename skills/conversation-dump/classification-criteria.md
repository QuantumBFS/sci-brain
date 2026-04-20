# Classification Criteria for 6-Dimension Dialog Analysis

Reference document for conversation-dump Phase 3. Defines decision rules, tie-breakers, and boundary examples for each dimension.

## 1. Bloom's Cognitive Level (`bloom:`)

| Level | Definition | Example |
|-------|-----------|---------|
| `remember` | Recall or recognize information | "What's the name of that function?" |
| `understand` | Explain or summarize | "So this means the data flows from A to B?" |
| `apply` | Use knowledge in a new situation | "Fix the tests" / "Run the pipeline" |
| `analyze` | Break down, compare, find structure | "Why does this fail only on the second run?" |
| `evaluate` | Judge, critique, decide between options | "No, not that approach" / "Option A is better because..." |
| `create` | Design, propose, synthesize something new | "What if we combined X and Y into a new abstraction?" |

**Tie-breaker:** When two levels seem equally valid, pick the higher one. The message demonstrates *at least* that cognitive complexity.

**Boundary cases:**
- "Yes" / "OK" / selecting an option without reasoning = `remember` (pure recall/recognition)
- "Yes, because..." with reasoning = `evaluate` (judgment)
- "Can you explain X?" = `understand` (requesting explanation)
- "How should we design X?" = `create` (requesting synthesis)

## 2. Question Depth (`depth:`)

Format: `<level>/<graesser-category>`

### Levels

| Level | When to use |
|-------|-------------|
| `shallow` | Direct factual questions, confirmations, yes/no |
| `intermediate` | Requires comparison, explanation, or connecting 2 concepts |
| `deep` | Requires causal reasoning, multi-step inference, or evaluation of trade-offs |

### Graesser Sub-categories

| Category | Definition | Example |
|----------|-----------|---------|
| `verification` | Yes/no, true/false | "Is this correct?" |
| `disjunctive` | Which of N options | "Should I use A or B?" |
| `concept-completion` | Fill in a blank | "What goes here?" |
| `feature-specification` | Properties of an entity | "What does this function return?" |
| `quantification` | How much/many | "How many tests fail?" |
| `causal-antecedent` | Why did X happen | "Why does this crash?" |
| `causal-consequent` | What happens if X | "What breaks if I remove this?" |
| `goal-orientation` | What is the purpose | "Why are we doing this?" |
| `instrumental` | How to achieve X | "Fix the tests" / "How do I deploy?" |
| `enablement` | What allows X | "What do I need installed?" |
| `expectational` | Why not the expected | "Why didn't it return 42?" |
| `judgmental` | What do you think | "Is this a good design?" |

**Tie-breaker:** For non-questions (commands, statements), classify by the implied cognitive task depth. "Fix the tests" is `deep/instrumental` because diagnosing + fixing requires multi-step reasoning.

**Boundary cases:**
- Confirmations ("yes", "option A") = `shallow/verification`
- Redirections ("no, focus on X instead") = `deep/judgmental` (implies evaluation of the current direction)
- Pasting code with no question = `intermediate/feature-specification` (implicit "what is this?")

## 3. Reasoning Probe (`probe:`)

Based on Paul & Elder's critical thinking framework.

| Probe | Definition | Example |
|-------|-----------|---------|
| `clarification` | Asking what is meant | "What do you mean by 'safe'?" |
| `assumption-probe` | Questioning unstated assumptions | "Are we sure the API is stable?" |
| `evidence-probe` | Asking for supporting evidence | "What data supports this?" |
| `perspective` | Exploring other viewpoints | "How would the ops team see this?" |
| `implication` | Exploring consequences | "If we do this, what happens to Y?" |
| `meta-question` | Questioning the question itself | "Are we even asking the right question?" |
| `none` | No probing intent | Most commands, confirmations, factual questions |

**Tie-breaker:** `none` is the default. Only assign a probe type when the message *actively* probes reasoning. A simple "why?" is `clarification`, not `assumption-probe` — unless it challenges an unstated assumption.

**Boundary cases:**
- "Why?" after an explanation = `clarification`
- "But does that assume X?" = `assumption-probe`
- "What if we're wrong about X?" = `assumption-probe`
- "Show me where it says that" = `evidence-probe`
- "What about performance?" = `implication` (if current discussion wasn't about performance)

## 4. Presupposition Quality (`presup:`)

Based on Walton's presupposition analysis.

| Quality | Definition | Example |
|---------|-----------|---------|
| `sound` | All presuppositions are warranted | "How do I fix the failing test?" (test does fail) |
| `existential-gap` | Presupposes something exists that may not | "Where is the config file?" (no config file exists) |
| `factive-gap` | Presupposes a fact that may be wrong | "Since the API is REST..." (it might be GraphQL) |
| `loaded` | Embeds a value judgment in the question | "Why is this code so bad?" |
| `complex` | Multiple intertwined presuppositions | "Why did removing X fix the Y bug?" (presupposes both removal and fix) |
| `ambiguous` | Key terms are vague or polysemous | "Make it faster" (faster startup? throughput? latency?) |
| `missing-context` | Question lacks necessary background | "Fix it" with no prior context about what's broken |
| `leading` | Question steers toward a specific answer | "Don't you think we should use Rust?" |

**Tie-breaker:** `sound` is the default. Only flag issues when the presupposition is genuinely problematic — not just informal. A command like "fix the tests" in context where tests are failing is `sound`, not `missing-context`.

**Boundary cases:**
- "Fix it" after discussing a specific bug = `sound` (context supplies the referent)
- "Fix it" as first message with no context = `missing-context`
- "Why doesn't this work?" = `sound` if there's a clear failure; `existential-gap` if the user hasn't shown a failure

## 5. Discourse Function (`discourse:`)

Based on Long & Sato's discourse analysis.

| Function | Definition | Example |
|----------|-----------|---------|
| `referential` | Genuine information-seeking or providing | "How does the auth middleware work?" |
| `display` | Testing/demonstrating knowledge | "So this is basically a monad, right?" |
| `rhetorical` | Making a point, not seeking answer | "Who writes tests like that?" |
| `confirmation-check` | Verifying understanding or selection | "So option A, right?" / "yes" |
| `clarification-request` | Asking for clarification | "What do you mean by 'idiomatic'?" |
| `indirect-request` | Command phrased as question/statement | "Fix the tests" / "Can you refactor this?" |

**Tie-breaker:** Look at what the user *wants to happen*. If they want the assistant to do something, it's `indirect-request`. If they want information, it's `referential`. If they're checking alignment, it's `confirmation-check`.

**Boundary cases:**
- "Can you do X?" = `indirect-request` (not a genuine question about capability)
- "Is X possible?" = `referential` (genuine question about feasibility)
- "Right?" at end of statement = `confirmation-check`
- Pasting an error with no text = `indirect-request` (implicit "fix this")

## 6. Generation Mechanism (`mechanism:`)

Based on Graesser's question generation mechanisms.

| Mechanism | Definition | Example |
|-----------|-----------|---------|
| `knowledge-deficit` | User lacks information and asks for it | "What does this error mean?" |
| `common-ground` | Establishing shared understanding | "So we agree to use approach A?" |
| `action-coordination` | Coordinating who does what | "Fix the tests" / "I'll handle the frontend" |
| `conversation-control` | Steering the conversation | "Let's move on to the API" / "Go back to what you said about X" |
| `exploration` | Open-ended investigation without specific target | "What if we tried X?" / "Let's see what happens" |
| `debugging` | Diagnosing a specific known failure | "Why does this crash on input Y?" |
| `undetermined` | Cannot confidently classify | (rare — prefer a best guess over this) |

**Tie-breaker:** `exploration` vs `debugging` — does the user have a *specific failure* in mind? If yes, `debugging`. If they're probing possibilities without a concrete problem, `exploration`.

**Boundary cases:**
- "Let's try a different approach" = `conversation-control` (redirecting, not exploring)
- "What if we used GraphQL instead?" = `exploration` (genuine what-if)
- "Why did the migration fail?" = `debugging` (specific failure)
- "What could go wrong with migrations?" = `exploration` (hypothetical)

## Cross-dimension Consistency Rules

1. `bloom:remember` + `depth:deep/*` is rare — if you assign both, double-check
2. `probe:assumption-probe` almost always implies `bloom:analyze` or higher
3. `discourse:confirmation-check` almost always pairs with `mechanism:common-ground`
4. `discourse:indirect-request` almost always pairs with `mechanism:action-coordination`
5. `presup:sound` should be the majority (>80%) — if you're flagging more, you're being too strict
