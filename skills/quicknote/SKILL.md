---
name: quicknote
description: Use when the user wants to save a Q&A exchange as a shareable quick note — captures the last substantive question and answer, saves to file, and copies to clipboard
---

## Quick Note

Capture the last substantive Q&A exchange from the conversation as a shareable note.

### Step 1 — Find the exchange

Scan back through the conversation to find the last **substantive** user message — skip short affirmations like "yes", "go on", "sounds good", "ok", "sure", "do it", "go ahead". The substantive message is the one that asks a real question, describes a problem, or shares an idea.

Pair it with the assistant's response to that message.

### Step 2 — Format the note

```markdown
# Quick Note — YYYY-MM-DD HH:MM

## Question
<the substantive user message, verbatim>

## Answer
<the assistant's response, verbatim>
```

No rewriting, no added context. Keep it raw.

### Step 3 — Save and copy

1. Create `docs/discussion/notes/` if it doesn't exist.
2. Save to `docs/discussion/notes/YYYY-MM-DD-HHMMSS-quicknote.md`.
3. Copy the note content to clipboard:
   - macOS: `pbcopy`
   - Linux: `xclip -selection clipboard` (fall back to `xsel --clipboard` if xclip unavailable)
4. Tell the user: saved to `<path>` and copied to clipboard.
