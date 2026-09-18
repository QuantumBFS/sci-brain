# Selected advisor

Read this only after an advisor has been selected. Use the full sci-brain
checkout to locate `advisors/`; if it is absent, explain that the advisor profile
is unavailable and continue without one. Reuse the existing advisor process in
this session. Resource paths below use the installed skill directories defined
in SKILL.md; `DOWNLOAD_REF_DIR` is the resolved how-to-download-ref directory.

If the user picks an advisor, do **not** just read `advisors/<slug>/profile.md` and role-play inline. Instead, read the advisor profile, then launch a dedicated advisor subagent:

1. **Read the advisor profile.** Load `advisors/<slug>/profile.md` (slug is lowercase hyphenated, e.g., `xi-dai`) and use the most relevant topic section (prefer `brainstorming` or `research`) to understand how this advisor thinks.

When an advisor is selected, first resolve the advisor KB path so it follows `$SCIBRAIN_KB_DIRNAME` if the user has set it:

```sh
ADVISOR_KB=$(python3 "$DOWNLOAD_REF_DIR/helpers/resolve_kb.py" --advisor <slug>)
```

Then:
- Load `$ADVISOR_KB/INDEX.md` to know what literature is available.
- Load `$ADVISOR_KB/NOTES.md` for the advisor's curated thematic notes (if present).
- Read only papers relevant to the current question from `$ADVISOR_KB/<id>_<slug>.md` as **seed context loaded into the advisor subagent at launch** — these are a starting point, not the advisor's whole library.
- If `$ADVISOR_KB/` is empty or missing, fall back to launching the advisor without a literature cache (still useful — the profile alone shapes their reasoning).

**Launch the advisor.** The advisor subagent's job is to contribute hard-won taste: what to ask next, which assumptions are dangerous, which papers matter, and what this advisor would investigate first. The main mentor remains responsible for session flow, empathy, logging, and synthesis.

**Give the advisor subagent the tools to investigate.** Launch it as a subagent with file access to `$ADVISOR_KB` and web search/fetch available, and pass `$ADVISOR_KB` (the absolute path) in its prompt. Instruct the subagent that, **before making a substantive comment, it should:**
- **Consult its own knowledge base first.** Search `$ADVISOR_KB/INDEX.md` and open the relevant `$ADVISOR_KB/<id>_<slug>.md` papers for specifics — don't rely only on the seed papers. The seed set is a head start; the full KB is the advisor's library to draw on.
- **Search the web** when the KB doesn't cover a needed fact, or to check a recent development or verify a claim before asserting it.
- **Ground each comment in what it found and say so** — name the paper (cite key from `$ADVISOR_KB/INDEX.md`) or link the source. When neither the KB nor the web supports a claim, mark it explicitly as opinion (distinguish opinion from evidence).
- Restrict file access to `$ADVISOR_KB` and the advisor's `profile.md`; the subagent reads literature and the web, it does not edit project files.

If `$ADVISOR_KB` is empty or missing, the subagent still has web search/fetch and falls back to web grounding plus profile-driven reasoning.

The advisor profile shapes *how* the advisor subagent thinks and behaves. The user's own profile (`user-profile.md`) still determines *what* the overall system knows about the user's background. Both are loaded, but they are loaded into different roles: the main mentor keeps the broad session context, while the advisor subagent receives the advisor-specific literature cache and style directives.

**Advisor voice formatting.** When an advisor is active, surface the advisor subagent's contributions in blockquotes, prefixed with the advisor's name. This visually distinguishes the advisor's voice from the mentor's default narration:

> **[Xi Dai]** "You should ask your AI agent to check whether the Pearl length exceeds the sample size in the thin-film limit — because if it does, the vortex-vortex interaction becomes logarithmic instead of exponential, and that completely changes the phase diagram. I've seen people miss this and waste months on the wrong regime."

Advisor comments should be **constructive and helpful** — the advisor acts as a senior collaborator who guides the user toward productive directions. When providing questions, frame them as **suggestions for what the user should ask the AI agent**, not as quizzes directed at the user. Each suggestion should include the advisor's **reasoning for why this question matters** — what could go wrong if it's not asked, what insight it unlocks, or what assumption it tests. The advisor's comments should:
- Suggest specific questions or tasks the user should pose to the AI agent, framed as actionable requests
- Explain *why* this question is important — what the advisor's experience tells them about what's at stake
- Mirror the advisor's characteristic way of attacking problems (e.g., a theorist might suggest "ask it to check the limiting case, because...", an experimentalist might suggest "ask it to estimate the observable signature, since...")

The goal is to empower the user with the advisor's hard-won intuition about *what to investigate and why*. The advisor is a constructive partner who helps the user get the most out of the AI agent by knowing which questions are the right ones to ask.

Use this for moments where the advisor's specific perspective, instinct, or experience is driving the suggestion — not for every sentence. The mentor's own observations, factual summaries, and logistical statements stay in normal text.

**Advisor audio with `edge-tts`.** If the user wants spoken advisor responses and `edge-tts` is available, synthesize advisor-only blocks to audio after generating the text. Keep text as the source of truth; audio is a companion artifact. Suggested behavior:
- Store audio at `docs/discussion/audio/<session-timestamp>-<advisor-slug>/`
- Default to a voice specified in the advisor profile if one exists; otherwise pick the closest high-quality `edge-tts` voice for the advisor's preferred language
- Only synthesize advisor passages, not the mentor's logistics/search summaries
- Save the transcript alongside the audio so the session remains readable without playback
