# Session history and logging

## Resume relevant history

Reuse a session already named by the user. Otherwise inspect file names, headers,
and recent wrap-up sections under `docs/discussion/` to find relevant sessions.
If several plausible sessions remain, offer their topics and dates plus a fresh
start. Read the selected log in full only when needed to recover the discussion;
do not read every historical log at startup or again at wrap-up.

Use `docs/discussion/user-profile.md` when background matters. Preserve existing
profile content and update it with facts the user supplied. For a fresh session,
use relevant previous outcomes as context without forcing continuity.

### Conversation Log

Maintain a running log at `docs/discussion/YYYY-MM-DD-HHMMSS-brainstorm-ideas-log.md` (timestamp from session start). Create the `docs/discussion/` directory if it doesn't exist.

**Append-only logging.** Save progress by appending to the log at checkpoints. Each append captures the **full conversation content** since the last save — all options presented (with descriptions), reasoning shared, user responses, search results, and key ideas. Not a summary — a readable record of what was actually said.

**When to append (checkpoints):**
- Every 3-5 exchanges, at a natural pause — when a sub-topic wraps up, a decision is made, or the conversation shifts direction
- When the discussion moves from exploration to a chosen direction or concrete plan
- At session wrap-up

Don't log after every message. Wait for a moment that feels like a natural checkpoint — the end of a thread, a decision point, a topic shift.


**Order: log first, then reply.** At a checkpoint, append to the log file before writing your response to the user. This ensures progress is saved even if the session is interrupted mid-reply.

**File header** — write once when creating the log:

```markdown
# Ideas Session — YYYY-MM-DD HH:MM
```

**Session wrap-up** — append a final section that consolidates the key outcomes: direction chosen, ideas explored, action items, and recommended readings.

These logs accumulate across sessions as separate files, building a record of the user's research interests, thinking patterns, and explored directions.
