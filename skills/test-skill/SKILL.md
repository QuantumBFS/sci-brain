---
name: test-skill
description: Use when testing a skill — role-plays through a skill's conversational flow with a simulated user persona, then produces a test report with structural analysis, UX feedback, and actionable suggestions
---

## Test Skill

A general-purpose skill testing framework. It executes any skill's SKILL.md by role-playing the interaction: the main agent follows the skill's instructions, while a subagent plays a realistic simulated user. This tests whether the skill produces a coherent experience end-to-end.

**Architecture:** Main agent = AI executing the target skill. Subagent = simulated user with a persona, resumed at each decision point.

---

### Step 0 — Choose Target & Analyze

Accept a skill path from the user, or list available skills and let the user pick via `AskUserQuestion`.

**Find available skills:** Search for `SKILL.md` files under `skills/` in the current project. Also check common skill locations (`~/.claude/skills/`, plugin directories). Present each skill with its `name` and `description` from frontmatter.

Once the user selects a skill, read its full `SKILL.md` and extract:

- **Phases/steps** and their entry conditions (e.g., "skip if chaining from survey")
- **Decision points** — every place the skill calls `AskUserQuestion`, with the options it presents
- **Preconditions** — files, registries, context, or external services the skill expects (e.g., survey registries, user profiles, MCP servers)
- **Expected outputs** — files created, formats, locations
- **Dependencies** — other skills referenced, MCP servers, APIs

**Flag structural issues** found during analysis:
- Decision points with no fallback/escape option (e.g., user must pick from presented choices with no "none of these")
- Abrupt phase transitions where the skill jumps from one mode to another without bridging
- Phases that reference files or context without checking if they exist first
- Asymmetric option handling (e.g., option (a) has a follow-up but (b) and (c) don't)

Present this structural analysis to the user, including any flagged issues. Example format:

```
## Skill Analysis: [name]

**Phases:** [list with brief descriptions]
**Decision points:** [count] AskUserQuestion calls identified
**Preconditions:**
  - [file/context] — [required/optional]
**Expected outputs:**
  - [file path] — [description]
**Dependencies:**
  - [skill/service] — [how it's used]
**Structural flags:**
  - [issue] at [location]
```

Ask the user via `AskUserQuestion`:

> "Here's what I found. Ready to proceed, or want to adjust the test scope?"
> - **(a)** Proceed — test the full skill flow
> - **(b)** Focus on specific phases — choose which phases to test
> - **(c)** Adjust preconditions — set up specific mock context before testing

### Step 1 — Generate Persona

Analyze the skill to infer what kind of user it serves. Consider:

- What domain knowledge does the skill assume?
- What motivations would bring someone to this skill?
- What range of experience levels does it handle?

Generate a persona with:

- **Name and background** — relevant to the skill's domain
- **Motivation** — why they'd use this skill (specific and concrete)
- **Experience level** — beginner, intermediate, or expert in the relevant domain
- **Decision tendencies** — how they'll behave at choice points (e.g., "explores broadly before committing", "wants quick results", "pushes back on suggestions", "asks lots of clarifying questions")
- **Quirks** — one or two realistic traits that make them not a perfectly compliant test subject (e.g., "sometimes goes off on tangents", "skeptical of AI-generated suggestions", "changes their mind after seeing options")

Present the persona to the user via `AskUserQuestion`:

> "[Persona description]"
> - **(a)** Looks good — start the test
> - **(b)** Make them more challenging — increase pushback and skepticism
> - **(c)** Make them more cooperative — reduce friction, focus on happy path
> - **(d)** Adversarial — generate a persona designed to break assumptions (one-word answers, misunderstandings, off-topic tangents, ignores instructions)
> - **(e)** Let me describe a custom persona

### Step 2 — Execute the Skill with Role Play

**Set up preconditions.** Based on Step 0 analysis, create any mock files or context the skill expects. For example:
- If the skill checks for a user profile, create a mock `docs/discussion/user-profile.md` matching the persona
- If the skill expects survey registries, create minimal mock registries
- If the skill needs MCP servers, note which are available and which will be absent

**Important:** Create mock files in a test-scoped location when possible (e.g., prefix with `test-` or use a temporary directory) to avoid polluting the user's actual data. When mock files must go in expected locations, track them for cleanup.

**Launch the user subagent** via `Task` tool (subagent_type: `general-purpose`):

```
You are role-playing as a simulated user testing a skill. Here is your persona:

Name: [name]
Background: [background]
Motivation: [motivation]
Experience: [experience level]
Decision tendencies: [tendencies]
Quirks: [quirks]

You are testing a tool that [one-line skill description].

When I present you with questions or options, respond in character:
- Be realistic — sometimes enthusiastic, sometimes uncertain, sometimes push back or ask for clarification
- Stay consistent with your persona's background and tendencies
- Give enough detail in your responses that the skill can work with them (don't just say "option A")
- If options don't fit what your persona would want, say so and explain what you'd prefer
- Don't break character or discuss the test itself

At the end, I'll ask for your feedback on the experience from your persona's perspective.

The first question is: [first decision point from the skill]
```

**Execute the target skill's phases**, following its SKILL.md instructions exactly. At each point where the skill calls `AskUserQuestion`:

1. **Resume the subagent** with the question and options, plus brief conversation context
2. Record the subagent's response
3. Continue executing the skill as if the subagent's response came from a real user

**Track the interaction** as a trace — record each:
- Phase/step being executed
- Question presented (with options)
- Subagent's response
- Main agent's next action
- Any files created or modified

**Safety caps:**
- Maximum **20 decision points** — if reached, gracefully wrap up the skill
- Maximum **10 subagent resumes** per phase — if a phase loops, note it and move on
- If the skill attempts to launch its own subagents (e.g., survey's parallel strategies), execute them normally — only the user-facing `AskUserQuestion` calls go to the simulated user

### Step 3 — Collect Feedback & Report

**Resume the subagent one final time** with:

```
The session is over. Step out of character briefly and give me structured feedback from your experience as the simulated user:

1. **Natural vs. forced** — What parts of the interaction felt natural? What felt forced, scripted, or awkward?
2. **Confusing moments** — Were you ever confused by the options presented? Were choices missing that you wanted?
3. **Understanding** — Did the agent seem to understand what you (as your persona) needed? Where did it miss?
4. **Pacing** — Was the flow too fast, too slow, or about right? Were there unnecessary steps?
5. **Missing or unnecessary** — What would you add? What would you remove?
6. **Overall impression** — Would your persona come back and use this skill again? Why or why not?
```

**Generate the test report** at `docs/test-reports/<skill-name>-<YYYYMMDD-HHMMSS>.md`:

```markdown
# Test Report: [skill name]

**Date:** [timestamp]
**Persona:** [name] — [one-line description]
**Phases tested:** [list]
**Decision points exercised:** [N of M total]

## Flow Completeness

- **Phases reached:** [which phases were entered]
- **Phases skipped:** [which were skipped and why]
- **Decision points exercised:** [list each with the option chosen]
- **Untested branches:** [options that were NOT selected — these represent untested paths]

## Interaction Trace

[Condensed trace of the full interaction — phase, question, response, action. Not a raw transcript — summarize each exchange in 2-3 lines.]

## Output Validation

- **Expected files:** [list from Step 0 analysis]
- **Actually created:** [list with status — created/missing/wrong format]
- **Format check:** [any format issues in created files]

## Broken References

[Files, skills, paths, or services mentioned in the SKILL.md that don't exist or aren't accessible]

## UX Feedback (from simulated user)

[Subagent's structured feedback from the final resume, organized by category]

## Structural Observations (from test executor)

[Main agent's own observations about the skill's design:]
- Ambiguous instructions encountered
- Edge cases not handled
- Phases that felt too long or too short
- Logic that was hard to follow

## Suggestions

[Actionable improvements, ordered by impact:]
1. [High impact suggestion]
2. [Medium impact suggestion]
...
```

**Clean up** any mock files created during testing. List what was cleaned up in the report.

**Add an intent-vs-experience comparison** to the Structural Observations section: for each phase tested, note what the skill's instructions intended to happen alongside what the simulated user actually experienced. Highlight gaps where the experience diverged from intent.

Present the report path to the user and offer:

> "Test complete. Report saved to `docs/test-reports/[file]`. What next?"
> - **(a)** Review the report together — walk through findings
> - **(b)** Run another test — same skill, different persona (skips Step 0 analysis — reuses the existing analysis)
> - **(c)** Test a different skill
> - **(d)** Done

**Re-run shortcut:** When the user selects **(b)**, skip Step 0 entirely — the skill analysis doesn't change. Go straight to Step 1 (persona generation) with the same target skill.
