# Flow journal — <goal-slug>

**GOAL:** <crisp restatement>
**Success test:** <how I will know it is solved>
**Started:** <YYYY-MM-DD>
**KB:** <path to .knowledge/ if used, else "none">

## Levers & facts (initial)

- Levers (conditions I could assume): <…>
- Facts (known / from KB): <…>
- Initial distance estimate: <low / medium / high, with a one-line why>

## Trail

Each trial is one block. Move ∈ {what-if, simulate, parallel-simulate, analyze, pivot, final-check}.
The last trial before SOLVED is always a `final-check` simulate: "is this solution clear, actionable,
and does it achieve the GOAL?"

### Trial N — <move> — level <decision level>
- **Action:** <the condition assumed / path simulated / conflict analyzed / re-aim chosen>
- **Outcome:** <toward goal / away / contradiction / subgoal pushed / backjumped to level k>
- **Distance:** <new estimate> (was <prev>)  →  no_progress = <n>
- **Note (learned clause):** <trigger conditions → outcome → reusable lesson>  *(omit only if none)*

<!-- repeat the Trial block per iteration -->

## Notes store (learned clauses, deduplicated)

Running list of the reusable lessons, copied here so they are findable in one place and survive
across pivots:

- `{X, Y} ⇒ dead-end because Z`
- …

## Outcome

- **Status:** SOLVED / PIVOTED-SOLVED / EXHAUSTED
- **Result:** <the solution, or the re-aimed result, or the best partial>
- **Vs. original goal (if pivoted):** <what was achieved, what gap remains>
- **Reasoning trail (clean):** <the winning decisions in order, dead-ends pruned>
- **What would unblock it (if exhausted):** <the missing fact / tool / assumption>
