---
name: how-to-flow
description: Agentic trigger. Use when one hard, testable goal resists a direct solution and needs an autonomous decide–simulate–learn–backjump search.
---

## Installed resources

Keep the working directory at the user's project. Resolve this `SKILL.md` to its
real path before locating bundled resources. `skills/<name>/...` refers to the
installed skill found by public name, not the user's project; dependencies need
not be siblings. Load only resources needed for the current task. If a required
dependency is missing, report it before that dependent step.


# Flow

A deep-thinker that **conquers one hard problem by autonomous search**, modeled on a
[CDCL](https://en.wikipedia.org/wiki/Conflict-driven_clause_learning)/DPLL SAT solver. Given a
goal, it iterates — assume, follow consequences, hit walls, *learn from the walls*, jump back, and
re-aim when truly stuck — until a solution emerges or the available budget and evidence justify reporting a partial result.

**Scope.** Goal-locked, fully autonomous, domain-agnostic. This is **not** `brainstorm-ideas`
(open-ended, collaborative, research-only). Use `how-to-flow` when you already have a *specific hard target*
and want a relentless solver thrown at it. KB-optional: if `<project>/.knowledge/INDEX.md` exists,
treat its papers as a fact source for propagation; never require it.

## The mental model

| Solver concept | Here |
|---|---|
| Variable assignment (Decide) | **what-if**: assume a new condition |
| Unit propagation (BCP) | **simulate**: run consequences forward, reflect |
| Conflict | a contradiction or dead-end on the current branch |
| Conflict analysis + learned clause | **the note** taken after every trial |
| Non-chronological backtracking | **backjump** to the real cause, not one step |
| Restart (clauses kept) | **pivot**: re-aim the goal; notes survive |
| Decision heuristic (VSIDS) | pick the lever that shrinks distance most + is easiest; favor conditions seen in recent conflicts |

## State to track

Maintain these throughout (in the journal file, see below):

- **GOAL** — restated crisply, with a concrete **success test**: *how will I know it is solved?*
- **TRAIL** — ordered list of decisions + propagated facts, each tagged with a **decision level**.
- **GOAL_STACK** — subgoals spawned by what-if recursion (current goal on top).
- **NOTES** — learned clauses: `trigger conditions → outcome → reusable lesson`. These are the
  whole point — they prune future search and guide backjumps.
- **distance** — a rough estimate of how far the current state is from GOAL.
- **no_progress** — consecutive trials with no distance drop (drives PIVOT).

## Preflight (gate — pass before the loop)

Before the first trial, establish the success test and gather facts needed for the
first discriminating step. Do not make exhaustive reading a prerequisite:

1. **Am I clear about the goal?** Can I state GOAL in one sentence *and* write a success test that
   would unambiguously tell me it is solved? If not — the goal is underspecified. Resolve it: derive
   the missing constraint from context if you can, otherwise ask the user **one** sharp clarifying
   question. A blurry goal makes every later distance estimate noise.
2. **Do I have the facts this step depends on?** Read relevant parts of the available
   sources, expanding only when a concrete dependency requires it:
   - the **conversation context** (constraints, examples, prior attempts the user mentioned),
   - the **project knowledge base** if present (`<project>/.knowledge/INDEX.md` + `NOTES.md`, and
     relevant rendered papers) — these become facts/unit clauses on the TRAIL for free,
   - the **repository / files** when the goal is about code or a concrete artifact.

   Record established facts and unresolved assumptions separately in "Levers & facts".
   Consult further files or papers when the next trial needs them.

Enter the loop when GOAL is testable and the first useful trial can be performed.

## Setup

1. Restate GOAL and write its success test. If vague, sharpen it into something testable.
2. Pick the journal path `docs/flow/<goal-slug>.md` (relative to the project working directory).
   Create it from `skills/how-to-flow/journal-template.md` and fill the header (GOAL, success test, date).
3. List the obvious **levers** (conditions you could assume) and known **facts** (from reasoning, or
   from `<project>/.knowledge/` if present). Estimate the initial distance.

## The loop

Run autonomously, one **trial** per iteration, until SOLVED / PIVOTED-SOLVED / EXHAUSTED.

```
1. ASSESS    Estimate distance to GOAL given the current TRAIL.
             Success test appears to pass?  → run the FINAL CHECK (below)
             before declaring SOLVED.
2. SELECT    Choose the move via the heuristic:
               · a promising untried lever exists      → WHAT-IF
               · you just made a decision              → SIMULATE
               · current branch is a dead-end/conflict → ANALYZE → NOTE → BACKJUMP
               · no_progress ≥ 3                       → review strategy; consider PIVOT
3. EXECUTE   Carry out the move (below).
4. NOTE      Append a trial entry to the journal — ALWAYS, even on success.
5. UPDATE    no_progress: reset to 0 if distance dropped, else +1.  Loop.
```

**Heuristic for picking the next what-if (VSIDS analogy):** prefer conditions that (a) most shrink
distance to GOAL if true, (b) are *easiest to achieve*, and (c) involve variables that showed up in
recent conflicts (bump their priority). Break ties toward conditions that, if false, also teach you
something.

### Move: what-if  (= Decide)

Pick a candidate condition **C** and apply two tests:

1. **Relevance** — assuming C is true, are we measurably closer to GOAL? If no → discard C and note
   *why it doesn't help* (a learned clause too).
2. **Tractability** — is *achieving C* easier than GOAL itself?
   - **Yes** → push C onto GOAL_STACK as a **subgoal** and recurse: the loop now works to establish
     C (a new, deeper decision level). When C is established, pop back and resume on the parent goal
     with C now a fact on the TRAIL.
   - **Closer but not easier** → C is a useful *reframing*, not progress. Record the insight, keep C
     as a tentative assumption at a new decision level, and continue searching.

Add C to the TRAIL at a fresh decision level either way.

### Move: simulate  (= Propagate)

From the current assumptions, follow the **forced or strongly-implied consequences** forward several
steps (`if C then likely D, then E…`). At each step, **feel and reflect**: note surprises, tensions,
symmetries, emerging structure — insight often arrives here, not at the decision.

- Consequences trend **toward** GOAL → record the gained insight, decrease distance, keep going.
- Consequences hit a **contradiction** or clearly trend **away** → declare a **conflict** and switch
  to ANALYZE.

**Parallel paths (optional, for wide forks).** When a fork has 2–3 genuinely competing continuations
and choosing blindly would waste effort, dispatch one subagent per path to simulate it independently,
then compare their reflections and adopt the most promising (and *note the others' dead-ends* so they
are never re-tried). Use this only when the fork is wide enough to justify the token cost; otherwise
simulate one path at a time.

### Move: analyze → note → backjump  (= clause learning)

On a conflict:

1. **Analyze** — find the *minimal subset of assumptions* on the TRAIL responsible for the dead-end.
2. **Note** — write a reusable constraint: `{X, Y} ⇒ dead-end because Z`. This is the learned clause;
   it must be general enough to fire again later.
3. **Backjump** — undo assumptions back to the **deepest decision level still consistent** with the
   new note (not merely one step). Resume the loop from there. The note guarantees you won't re-enter
   the same trap.

### Move: pivot  (= meta-restart, NOTES kept)

Consider a pivot when `no_progress ≥ 3` or conflicts stop teaching anything new; record the evidence rather than treating the count alone as a reason to abandon the method. Step
out of the search and ask, in order:

1. **Feasibility** — is GOAL actually achievable with the available tools, facts, and time?
2. **Re-aim** — is GOAL really what we want, or is there an *equally valuable* goal that is easier?
3. **Relaxation** — can GOAL be weakened, split, or specialized into a version reachable *now*?

Change methods, assumptions, or intermediate subgoals autonomously while keeping
the original success test. If the promising alternative weakens or replaces the
requested outcome, propose it and wait for the user's decision before adopting
it. Continue independent work on the original goal while that choice is pending.
Keep all NOTES, log the reason and any explicit authorization, and reset the
TRAIL for the chosen method. Preserve the original GOAL in the journal even when
a different goal is authorized.

## Final check (verify the model before declaring SOLVED)

A solver that claims SAT verifies the assignment satisfies *every* clause before stopping. Do the
same: **the last round is always a `simulate` pass over the candidate solution**, not a decision.
Take the proposed solution as the starting statement and run it forward, asking:

> **"Is this solution clear, actionable, and does it actually achieve the GOAL?"**

- **Clear** — could a competent reader follow it without filling gaps? No hand-waving, no "and then
  it works."
- **Actionable** — are the concrete steps / construction / proof spelled out, not just gestured at?
- **Achieves the GOAL** — simulate it against the **success test** and against every NOTE (learned
  clause): does any prior dead-end still apply? Does it meet the original success test, or an explicitly authorized replacement? Report any gap to the original.

If any answer is no, the check **is a conflict**: ANALYZE → NOTE the gap → BACKJUMP and keep
searching (do not declare SOLVED). Only when all three hold do you settle. Record this final
verification as the last trial in the journal.

## Termination

- **SOLVED** — success test passes *and the final check confirms it*. Write the solution and a clean
  summary of the reasoning trail.
- **PIVOTED-SOLVED** — a user-authorized replacement goal was solved. Report what was achieved *versus the original*,
  and what gap remains to the original GOAL.
- **EXHAUSTED** — after **at most 3 pivots** still stuck. Stop (do not loop forever). Report: the best
  partial result, the **map of dead-ends** (the NOTES), the current best lever, and *what new fact or
  tool would unblock it*.

Always end by ensuring the journal's final section is filled in.

## Journal

Append a trial entry after **every** trial (this is the user's standing rule and the solver's clause
store). Format in `skills/how-to-flow/journal-template.md`. Keep entries terse — one block per trial — so the
file stays scannable and survives context compaction (the journal is the recoverable state of the run).

## Worked example (abbreviated)

> **GOAL:** prove a given graph property P holds for all planar graphs. **Success test:** a complete
> argument with no unjustified step.
>
> - *Trial 1 — what-if:* assume the graph is a maximal planar triangulation. Relevance: yes (general
>   case reduces to it). Tractability: easier (extra edges only help). → subgoal pushed. distance ↓.
> - *Trial 2 — simulate:* propagate Euler's formula on triangulations → degree-sum bound emerges.
>   Insight noted. distance ↓.
> - *Trial 3 — simulate:* push the bound toward P → contradiction with a degree-2 vertex case.
>   **conflict.**
> - *Trial 4 — analyze/note/backjump:* note `{triangulation assumption} ⇒ misses low-degree vertices`.
>   Backjump to Trial 1's level; refine assumption to "triangulation *after* removing degree-≤2
>   vertices."
> - *Trial 5 — simulate:* re-propagate → P follows by induction on vertex removal. Success test
>   appears to pass.
> - *Trial 6 — final-check:* simulate the full argument forward — clear? actionable? meets the
>   original GOAL with no NOTE still firing? Yes on all three. **SOLVED.**
