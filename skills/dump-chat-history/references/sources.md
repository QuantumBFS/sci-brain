# Finding the selected history

Discovery notes checked 10 September 2026. Read only the selected harness sections. These are discovery hints, not a stable
cross-version storage API. Check the installed version/help and inspect a sample
record before extracting. Honor a user-supplied export or configured data root.
Never assume a model name determines which application saved the conversation.

## Codex

Start with the selected Codex home (normally `~/.codex`). `history.jsonl` can
supply typed text and timestamps; rollouts under `sessions/` supply context and
source records. Find project/session metadata before scanning message content.
Inspect archived session stores when present and relevant to the requested range.

Current local installations may index sessions in `state_*.sqlite` and messages
in `thread_history_*.sqlite`. Open SQLite with `mode=ro`, inspect `sqlite_master`
and column names, and query only selected threads; version suffixes and schemas
are not fixed. The message projection can recover text absent from the current
rollout, but it can also duplicate it. Prefer stable item IDs for reconciliation.

For rollouts, identify actual user `response_item` messages or `event_msg`
user events; their coexistence does not mean two submitted prompts. Skill,
environment, and AGENTS.md injections can have a user role. Use origin/turn
metadata and the typed history to distinguish them; do not regex-strip arbitrary
XML-like text from a genuine human message. Recover structured question answers
from their associated call/result records, including the original question.
Do not substitute compaction summaries for original messages.

## Claude Code

Start with the selected Claude data root (normally `~/.claude`): `history.jsonl`
and `projects/<encoded-project>/<session-id>.jsonl`. Confirm project identity
from `cwd`/session metadata; encoding a path is only a discovery hint.

A `type: user` record may be a tool result, not human input. Inspect content
blocks, `origin`, `isMeta`, and sidechain metadata. Include human
`queue-operation` enqueue records and `AskUserQuestion` answer payloads.
Enqueue/pop/remove and re-enqueue events may describe one submission: reconcile
stable IDs, source text, and queue lifecycle. Do not collapse distinct repeated
human submissions because the words match. The global history may timestamp
queue consumption rather than submission; preserve both when known.

Inspect `pastedContents` and attachment references when the history display is a
placeholder. Keep the full pasted text if recoverable; record unavailable media
without inventing its content. Child-agent logs and task notifications are not
human prompts. Include child-agent transcripts only when selected explicitly.

## pi agent

Pi records JSONL sessions under `~/.pi/agent/sessions/`, grouped by working
directory; check configured directory overrides. A session is a tree:
`id`/`parentId` identify branches. Preserve branch provenance, and state whether
the selected export covers the active branch or all branches. A linear file scan
must not pretend sibling branches form one conversation. Read text from message
entries, not compaction summaries or extension-generated custom messages.

Prefer the installed local export command when suitable (`/export` or
`--export`, depending on version); verify its output format first. Do not use a
sharing command to obtain a local export.

Primary reference: [Pi session format](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/docs/session.md).

## OpenCode

Use `opencode session list --format json` to identify sessions, then
`opencode export <sessionID>` to save JSON locally. Inspect each exported
message's role, time, and parts; preserve text parts and attachment references.
Do not assume the internal storage is always individual JSON files or always
SQLite. A sanitized export is a redacted derivative and cannot establish the
original wording.

Primary reference: [OpenCode CLI: session and export](https://opencode.ai/docs/cli/).

## Kimi Code

Check `kimi --version` and `kimi export --help`. Supported versions provide
`kimi export <session-id> -o <path.zip>`. Export to a local file; inspect the ZIP
listing and read selected members without blindly extracting paths. Some versions
also support a local Markdown export in the TUI.

Storage has changed across Kimi CLI/Code versions: older exports include
`context.jsonl`, `wire.jsonl`, and state files; newer ones can use
`agents/main/wire.jsonl` under the configured Kimi home. Prefer native export
and version-specific schema inspection over a hard-coded `~/.kimi*` layout.
Where supported, use `--no-include-global-log` to avoid gathering diagnostics
from unrelated sessions. Compacted context alone may omit original messages;
check the event stream and disclose remaining gaps.

Primary references: [Kimi CLI export](https://github.com/MoonshotAI/kimi-cli/blob/main/docs/en/reference/kimi-command.md),
[Kimi Code sessions](https://github.com/MoonshotAI/kimi-code/blob/main/docs/en/guides/sessions.md).

## DeepSeek harness or client

Keep **DeepSeek** as a visible source choice. Ask for the actual application,
CLI executable/repository, or exported history file if it is not supplied.
DeepSeek used through OpenCode, pi, Claude Code, or another client inherits that
client's history format. Record both the harness and model/provider when known;
do not relabel it as a separate session or invent a universal DeepSeek directory.
For a web/app export, inspect the provided format and available timestamps.

## Gemini CLI, GitHub Copilot CLI, Cursor, Windsurf, Aider, Cline, Roo Code

Offer these names in the source picker. For a selected product, inspect the
installed help or its official export/session documentation and prefer a local
JSON/JSONL/Markdown export. Preserve the original export beside normalized text
when requested. Aider's Markdown history, for example, needs role-boundary
inspection; it must not be assumed to have per-message timestamps.

Useful primary entry points:
- [Gemini CLI commands](https://github.com/google-gemini/gemini-cli/blob/main/docs/reference/commands.md)
- [GitHub Copilot CLI session data](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/chronicle)

## Another harness (user input), or supplied exports

Ask for the name and local export/root location. Inspect representative records
and identify role, text, time, session, branch, and attachment fields. Explain any
missing fields before using them for filtering. Do not guess a parser based on a
`.jsonl` suffix. If no local export exists, guide the user through the selected
application's documented export flow; a local-history task does not authorize
logging into accounts or publishing share links.
