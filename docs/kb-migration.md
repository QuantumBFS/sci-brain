# Migrating from the pre-0.3 `<registry-root>/<slug>/` layout

Old sci-brain (≤ 0.2.x) stored surveys under `~/.claude/survey/<topic>/` (or `.codex/survey/`, `.config/opencode/survey/`, `.claude/survey/`) with `summary.md` + `references.bib` per topic. 0.3 moves to one `<project>/.knowledge/` per project (plus per-advisor caches). Migrate by hand:

```sh
# Pick your project root (where you want .knowledge/ to live):
PROJ=/path/to/your/project
mkdir -p "$PROJ/.knowledge"

# Move a single old registry into the project KB:
OLD=~/.claude/survey/topological-orders     # adapt path
mv "$OLD/references.bib" "$PROJ/.knowledge/references.bib"   # or merge into existing references.bib
mv "$OLD/summary.md"     "$PROJ/.knowledge/NOTES.md"
mv "$OLD"/*.md           "$PROJ/.knowledge/"   2>/dev/null  # rendered papers
mv "$OLD/.raw"           "$PROJ/.knowledge/.raw"
mv "$OLD/.figures"       "$PROJ/.knowledge/.figures"

# Regenerate INDEX.md (use a stable title — re-runs must use the same string):
python3 skills/how-to-download-ref/helpers/index.py \
  --kb "$PROJ/.knowledge" \
  --title "topological-orders — references" \
  --source-note "Migrated from ~/.claude/survey/topological-orders on $(date -u +%Y-%m-%d)."

# Remove the old registry:
rmdir "$OLD"
```

For advisor caches built by the abandoned 0.2-era `publications.yml` flow: that layout was never populated; nothing to migrate. The new flow builds `advisors/<slug>/.knowledge/` via `/know-me-better` or `/how-to-download-ref` invoked from `/create-advisor`.

Multiple old registries can be merged into one project KB (run the `mv` block per topic; `references.bib` accepts appends; `NOTES.md` accepts merges as separate top-level headings).
