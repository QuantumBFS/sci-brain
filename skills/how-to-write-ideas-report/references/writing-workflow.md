# Shared Writing Workflow

Use this from `how-to-write-ideas-report`, `survey` report mode, and `write-paper` for mechanics that are not product-specific.

Resolve the installed `how-to-download-ref` skill from the agent's catalog and set `DOWNLOAD_REF_DIR` to its absolute directory before running these commands. Keep the working directory at the user's project. The companion `typst-reference.md` lives beside this file.

## Context

Start from what the user supplied: text, source files, scope, format, and any
authorization already given. A local prose edit needs the passage plus the
definitions and citations it depends on, not the whole KB or conversation history.

- Resolve the project KB when KB-backed context is needed: `KB=$(python3 "$DOWNLOAD_REF_DIR/helpers/resolve_kb.py")`.
- Read `$KB/INDEX.md` and `$KB/NOTES.md` for the topic, then the relevant notes and bibliography entries. Screening the whole bibliography belongs to an explicitly selected review.
- Read `docs/discussion/user-profile.md` when audience, background, or positioning matters.
- For ideas/manuscripts, read the relevant `docs/discussion/*-brainstorm-ideas-log.md`, starting from the wrap-up section.
- Papers the user supplied and a manuscript-local bibliography are valid sources without a sci-brain KB. If the needed literature base is missing, suggest the `survey` skill or ask the user for explicit source files.

The canonical bib is `$KB/references.bib`.

**Legacy compatibility.** Pre-0.3 KBs kept the bib at the project root as `$(dirname $KB)/ref.bib`. If `$KB/references.bib` is absent but that legacy file exists, use it for this run and offer to migrate it (`git mv "$(dirname $KB)/ref.bib" "$KB/references.bib"`) so future runs find it in the canonical spot. If neither exists, glob `$KB/*.bib` and confirm with the user before using another file.

## Scope the source set

For a KB-backed report, a write-up covers a *subset* of the bib — the references the relevant `NOTES.md` section(s) actually cite, not all 100+ accumulated entries. Determine that subset deterministically instead of by eye:

```sh
python3 "$DOWNLOAD_REF_DIR/helpers/scope_refs.py" --notes "$KB/NOTES.md" --bib "$KB/references.bib"
```

When the user supplied explicit sources instead, use those directly; do not require NOTES.md. The helper prints the scoped cite keys (one per line) and exits non-zero if any `[@key]` anchor in the notes has no bib entry — fix dangling anchors before drafting. Use `--json` for `{scoped, missing, unused}`. Draft against the scoped keys; the `unused` list is out of scope unless the user asks to widen it.

## References

- Never invent BibTeX from memory.
- Use existing cite keys from `$KB/references.bib` (scoped as above).
- For missing papers, use `how-to-download-ref` to add DOI/arXiv IDs to the active KB.
- For report-local output, copy `$KB/references.bib` beside the generated document when citations are used.

## Gap Filling

Search only for gaps needed to support the document's main claims. Prefer the active KB first, then MCP/Semantic Scholar/arXiv/CrossRef/web search. Stop when the main claims have citations; completeness is not the goal.

**Recency gate — decide whether to search at all.** Read the build date in the `NOTES.md` header. If it is recent (≲ 4 weeks old), the literature base is fresh: skip discovery gap-filling entirely and only resolve *citation-level* gaps (a claim in the draft with no key to back it). Only when `NOTES.md` is older — or absent — run the recency search for SOTA results, active groups, and method families that may have superseded the notes.

## Output Format

Check `CLAUDE.md`/`AGENTS.md` for a configured format. Otherwise ask:

- Typst (`.typ`) — recommended when no venue template overrides it
- LaTeX (`.tex`) — traditional academic format
- Markdown (`.md`) — fastest, but citations remain inline unless rendered elsewhere

## Figures And Diagrams

Use visuals when they make an abstract structure easier to critique: reductions, workflows, architecture, comparisons, timelines, or dependency graphs.

- Typst: use `skills/how-to-write-ideas-report/references/typst-reference.md`.
- LaTeX: use TikZ.
- Markdown: use Mermaid or ASCII.

For Typst, prefer native `grid` + `rect` + fixed-width `box()` for text-heavy layouts; use CeTZ for timelines, dependency graphs, and geometric sketches. Compile and visually inspect figures when producing a final PDF.

## Finish

Run these checks before declaring the document done — do not eyeball them:

- **Compile** the document and check both the exit status and the log. For Typst, a missing cite key only warns, so a clean exit alone is not a pass; the block below fails on a nonzero exit *or* on any warning, and prints the log either way (replace `main.typ` with the source file):
  ```sh
  LOG=$(mktemp)
  typst compile main.typ >"$LOG" 2>&1; status=$?
  cat "$LOG"
  grep -Eiq 'unresolved|warning' "$LOG" && status=1
  rm -f "$LOG"
  [ "$status" -eq 0 ] && echo clean
  ```
  Use the LaTeX/Markdown equivalent for other formats. Read every warning before calling the build clean.
- **Every scoped claim is cited.** Confirm each `@key` in the prose resolves to a bib entry and that no scoped key was silently dropped (cross-check against `scope_refs.py` output).
- **Non-empty bibliography** renders in the output.
- Report the output path and any skipped verification.
