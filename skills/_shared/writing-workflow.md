# Shared Writing Workflow

Use this from `idea-writer`, `survey-writer`, and `paper-writer` for mechanics that are not product-specific.

## Context

- Resolve the project KB with `KB=$(python3 skills/download-ref/helpers/resolve_kb.py)`.
- If present, read `$KB/NOTES.md`, `$KB/INDEX.md`, and `$(dirname $KB)/ref.bib`.
- Read `docs/discussion/user-profile.md` when audience, background, or positioning matters.
- For ideas/manuscripts, read relevant `docs/discussion/*-brainstorm-ideas-log.md`.
- If the needed literature base is missing, suggest `/survey` or ask the user for explicit source files.

## References

- Never invent BibTeX from memory.
- Use existing cite keys from `$(dirname $KB)/ref.bib`.
- For missing papers, use `download-ref` to add DOI/arXiv IDs to the active KB.
- For report-local output, copy the active `ref.bib` beside the generated document when citations are used.

## Gap Filling

Search only for gaps needed to support the document's main claims. Prefer the active KB first, then MCP/Semantic Scholar/arXiv/CrossRef/WebSearch. Stop when the main claims have citations; completeness is not the goal.

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

- Check that cited reports have a non-empty bibliography.
- Report the output path and any skipped verification.
