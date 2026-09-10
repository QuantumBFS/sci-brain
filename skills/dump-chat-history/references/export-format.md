# Export record

`history.json` is a local, source-preserving record, not a harness backup.
Retain original exported files if a restorable archive is requested. Text is
never rewritten to fit this schema; use one entry per original text block when
necessary, linked by `message_id`, `turn_id`, and `branch_id` if present.

```json
{
  "title": "Designing a Research Website",
  "subtitle": "From a visual brief to a simpler guide",
  "window": {
    "start": "2026-09-03T21:41:00+08:00",
    "end": "2026-09-10T21:41:00+08:00",
    "timezone": "Asia/Shanghai"
  },
  "scope": "Website conversations for the selected project; human text is shown in the PDF.",
  "coverage": "Selected local sessions; remote conversations were not available.",
  "sources": [
    {"id": "S1", "location": "export/session.jsonl", "note": "Selected session and active branch."}
  ],
  "entries": [
    {
      "id": "P1",
      "source": "codex",
      "session_id": "session-a",
      "timestamp": "2026-09-07T00:08:00+08:00",
      "role": "user",
      "kind": "prompt",
      "text": "keep the original logo",
      "source_id": "S1",
      "provenance": "S1, line 12",
      "include_in_report": true,
      "annotation": "The original mark is an explicit design constraint."
    }
  ]
}
```

Required: topic `title`; `window`; explicit `scope` and `coverage`; `sources`
with unique IDs and locations; `entries` with unique IDs, source/harness name,
session ID, timestamp, role, kind, exact text, source ID, and provenance.

- `window.start` can be `null` for an explicitly selected all-time export;
  `window.end` is the captured cutoff with an offset; timezone is an IANA name.
- Timestamp is an offset-aware ISO string or `null`. Unknown-time entries require
  `undated: true`; keep them outside claims about precisely bounded coverage.
- `outside_window: true` marks retained context outside the selected interval.
- Roles are `user` and `assistant`; exclude internal reasoning and tool payloads
  from these conversational text fields. Keep necessary tool evidence separately.
- Kinds can identify `prompt`, `answer`, `queued`, `response`, or `attachment`.
  Structured answers include the exact `question`. Unavailable attachment entries
  use an empty `text` plus `attachment_note`; a placeholder is not original text.
- `message_id`, `turn_id`, and `branch_id` preserve relations where available.
  Multi-part text shares a message ID and remains in source block order.
- `include_in_report` controls the PDF view without dropping data from JSON.
  Default: human entries; assistant context stays in JSON and Markdown.
- `phase`, `annotation`, top-level `analysis`, and `method` are optional editorial
  fields. They must never be concatenated into `text`.
- Entries are ordered chronologically across sources, preserving source order for
  timestamp ties. Undated records follow the dated transcript. Do not invent a
  time or flatten sibling branches into one conversation.
- `provenance` names the source record's line, database item ID, or export path.
  Keep additional source locators/digests as extra fields when useful.

The helper adds SHA-256 text digests and checks declared boundaries; it does not
prove that every source message was found. Completeness and human-origin checks
require comparing the export with the selected source records.
