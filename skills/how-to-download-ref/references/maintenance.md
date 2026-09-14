# Restore an existing KB

Use the installed `DOWNLOAD_REF_DIR` and resolved `KB` from SKILL.md.

## Regenerating a cloned KB

```sh
python3 "$DOWNLOAD_REF_DIR/helpers/kb_sync.py" --kb "$KB"
```

Requires `references.bib` and at least one rendered paper. This restores `.raw/`
and `.figures/` using each tracked entry's declared identifier namespace. Bib-only
references recover caches with a warning. It creates or rewrites no Markdown,
INDEX.md, or bibliography files. Complete caches need no network on repeat runs;
unavailable assets remain WARNs and can be retried. Invalid input or failed
restoration produces FAIL and a nonzero exit.

PDF figure restoration needs the same `pymupdf4llm` version used to render the
entry so filenames match tracked image links. Missing dependencies and mismatched
filenames are reported. LaTeX figures are restored from the cached source tree or
a new source download. Publisher JATS is restored for `full_text: jats` entries.
`--email` / `SCIBRAIN_CONTACT_EMAIL` enable Unpaywall here too.
