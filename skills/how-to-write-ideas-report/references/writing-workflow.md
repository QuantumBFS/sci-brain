# Shared Writing Workflow

Use this from `how-to-write-ideas-report`, `survey` report mode, and `write-paper` for mechanics that are not product-specific.

Resolve the installed `how-to-download-ref` skill from the agent's catalog and set `DOWNLOAD_REF_DIR` to its absolute directory before running these commands. Keep the working directory at the user's project. The companion `typst-reference.md` lives beside this file.

## Context

Start with the user's supplied text, source files, scope, format, and existing
authorization. A local prose edit needs the passage and its relevant definitions
or citations, not the whole literature library or conversation history.

- Resolve the project KB only when KB-backed context is needed, using
  `KB=$(python3 "$DOWNLOAD_REF_DIR/helpers/resolve_kb.py")`.
- Search INDEX.md/NOTES.md for the topic, then read relevant notes and bibliography
  entries. Full bibliographic screening belongs to an explicitly selected review.
- Read `docs/discussion/user-profile.md` when audience or positioning matters;
  read only relevant brainstorming logs, starting with their wrap-up sections.
- Supplied papers and a manuscript-local bibliography are valid source material
  without a sci-brain KB. Fill evidence gaps within the requested task, asking
  only for missing substance that cannot be established from the sources.

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

**Search according to the claim.** A recent NOTES.md can avoid repeating discovery,
but its date does not establish that a volatile or SOTA claim is current. Verify
such claims when the document relies on them or the user requests an update.
Stable derivations and local language edits do not require a new field survey.

## Output Format

Reuse the user's format, the existing document, or the project's configured
format. For a new standalone report with no convention, use Markdown. Use the
venue's format when required, and Typst or LaTeX when requested or needed for a
PDF. Ask only when the choice affects a requirement that remains unresolved.

## Figures And Diagrams

Use visuals when they make an abstract structure easier to critique: reductions, workflows, architecture, comparisons, timelines, or dependency graphs.

- Typst: use `skills/how-to-write-ideas-report/references/typst-reference.md`.
- LaTeX: use TikZ.
- Markdown: use Mermaid or ASCII.

For Typst, prefer native `grid` + `rect` + fixed-width `box()` for text-heavy layouts; use CeTZ for timelines, dependency graphs, and geometric sketches. Compile and visually inspect figures when producing a final PDF.

## Finish

Verify the requested output, not an unrelated full workflow:

- **Compile changed document source** and inspect the result when producing a
  final PDF. A plain Markdown or inline-text request needs only its relevant
  rendering/text checks; report when no build applies.
- **Check both exit status and citation diagnostics.** For Typst, run from the
  document directory (replace `main.typ` with the actual source):

  ```sh
  BUILD_LOG=$(mktemp)
  if typst compile main.typ >"$BUILD_LOG" 2>&1; then
    cat "$BUILD_LOG"
  else
    cat "$BUILD_LOG" >&2
    rm -f "$BUILD_LOG"
    exit 1
  fi
  if grep -Ei 'unresolved|warning' "$BUILD_LOG"; then
    rm -f "$BUILD_LOG"
    exit 1
  fi
  rm -f "$BUILD_LOG"
  ```

  A warning requires inspection before declaring completion; do not classify a
  failed compiler as clean merely because its error lacks the word “warning”.
- **Citations:** verify each used key resolves and that sources support the main
  claims. A selected paper need not be cited when it does not support the final
  argument. If citations are used, ensure the bibliography renders; do not
  require one for an uncited excerpt.
- Fix failures introduced by the requested changes and rerun affected checks.
  Stop after they pass unless a concrete unresolved finding requires more work.
- Deliver the requested artifact with verification and any remaining limitations.
