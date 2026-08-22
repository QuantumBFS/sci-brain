# Shared Writing Workflow

Use this from `brainstorm-ideas` report mode, `survey` report mode, and `paper-writer` for mechanics that are not product-specific.

## Context

- Resolve the project KB with `KB=$(python3 skills/download-ref/helpers/resolve_kb.py)`.
- If present, read `$KB/NOTES.md`, `$KB/INDEX.md`, and the canonical bib `$KB/references.bib`.
- Read `docs/discussion/user-profile.md` when audience, background, or positioning matters.
- For ideas/manuscripts, read relevant `docs/discussion/*-brainstorm-ideas-log.md`.
- If the needed literature base is missing, suggest `/survey` or ask the user for explicit source files.

The canonical bib is `$KB/references.bib`.

**Legacy compatibility.** Pre-0.3 KBs kept the bib at the project root as `$(dirname $KB)/ref.bib`. If `$KB/references.bib` is absent but that legacy file exists, use it for this run and offer to migrate it (`git mv "$(dirname $KB)/ref.bib" "$KB/references.bib"`) so future runs find it in the canonical spot. If neither exists, glob `$KB/*.bib` and confirm with the user before using another file.

## Scope the source set

A write-up covers a *subset* of the bib — the references the relevant `NOTES.md` section(s) actually cite, not all 100+ accumulated entries. Determine that subset deterministically instead of by eye:

```sh
python3 skills/download-ref/helpers/scope_refs.py --notes "$KB/NOTES.md" --bib "$KB/references.bib"
```

It prints the scoped cite keys (one per line) and exits non-zero if any `[@key]` anchor in the notes has no bib entry — fix dangling anchors before drafting. Use `--json` for `{scoped, missing, unused}`. Draft against the scoped keys; the `unused` list is out of scope unless the user asks to widen it.

## References

- Never invent BibTeX from memory.
- Use existing cite keys from `$KB/references.bib` (scoped as above).
- For missing papers, use `download-ref` to add DOI/arXiv IDs to the active KB.
- For report-local output, copy `$KB/references.bib` beside the generated document when citations are used.

## Gap Filling

Search only for gaps needed to support the document's main claims. Prefer the active KB first, then MCP/Semantic Scholar/arXiv/CrossRef/WebSearch. Stop when the main claims have citations; completeness is not the goal.

**Recency gate — decide whether to search at all.** Read the build date in the `NOTES.md` header. If it is recent (≲ 4 weeks old), the literature base is fresh: skip discovery gap-filling entirely and only resolve *citation-level* gaps (a claim in the draft with no key to back it). Only when `NOTES.md` is older — or absent — run the recency search for SOTA results, active groups, and method families that may have superseded the notes.

## Output Format

Check `CLAUDE.md`/`AGENTS.md` for a configured format. Otherwise ask:

- Typst (`.typ`) — recommended when no venue template overrides it
- LaTeX (`.tex`) — traditional academic format
- Markdown (`.md`) — fastest, but citations remain inline unless rendered elsewhere

## Figures And Diagrams

Use visuals when they make an abstract structure easier to critique: reductions, workflows, architecture, comparisons, timelines, or dependency graphs.

- Typst: use `skills/_shared/typst-reference.md`.
- LaTeX: use TikZ.
- Markdown: use Mermaid or ASCII.

For Typst, prefer native `grid` + `rect` + fixed-width `box()` for text-heavy layouts; use CeTZ for timelines, dependency graphs, and geometric sketches. Compile and visually inspect figures when producing a final PDF.

## Finish

Run these checks before declaring the document done — do not eyeball them:

- **Compile** the document (`typst compile <file>.typ`, or the LaTeX/Markdown equivalent) and confirm it exits cleanly.
- **No dangling citations.** Grep the compile log for unresolved-reference warnings; for Typst, a missing key warns rather than errors, so an empty grep is the pass condition:
  ```sh
  typst compile <file>.typ 2>&1 | grep -i "unresolved\|warning" || echo "clean"
  ```
- **Every scoped claim is cited.** Confirm each `@key` in the prose resolves to a bib entry and that no scoped key was silently dropped (cross-check against `scope_refs.py` output).
- **Non-empty bibliography** renders in the output.
- Report the output path and any skipped verification.
