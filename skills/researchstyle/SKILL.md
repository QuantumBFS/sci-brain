---
name: researchstyle
description: Use when indexing a personal paper collection into a survey registry — supports Zotero library, a PDF folder, or a Google Scholar profile
---

# Personal Survey Registry

Turn an existing paper collection into a structured survey registry (`summary.md` + `references.bib`). The output uses the same registry format as the `survey` skill — so personal and topic registries can be merged.

**Step 1 — Locate the source.** Ask which source to index:

> "Where are your papers?"
> - **(a)** Zotero library
> - **(b)** A PDF folder (give me the path)
> - **(c)** Google Scholar profile (give me the URL)

**Step 2 — Index the collection.**

**Zotero:**

1. Locate `zotero.sqlite` at standard paths (`~/Zotero/`, `~/Library/Application Support/Zotero/`). If not found, ask for the path.
2. Query all items:

```bash
sqlite3 ~/Zotero/zotero.sqlite "
  SELECT i.itemID, v_title.value AS title, v_abstract.value AS abstract
  FROM items i
  JOIN itemData id_t ON i.itemID = id_t.itemID
  JOIN itemDataValues v_title ON id_t.valueID = v_title.valueID
  JOIN fields f_t ON id_t.fieldID = f_t.fieldID AND f_t.fieldName = 'title'
  LEFT JOIN itemData id_a ON i.itemID = id_a.itemID
  LEFT JOIN fields f_a ON id_a.fieldID = f_a.fieldID AND f_a.fieldName = 'abstractNote'
  LEFT JOIN itemDataValues v_abstract ON id_a.valueID = v_abstract.valueID
  LIMIT 200;
"
```

3. For papers missing abstracts or DOIs, find the PDF via:

```bash
sqlite3 ~/Zotero/zotero.sqlite "
  SELECT ia.parentItemID, ia.key, ia.contentType
  FROM itemAttachments ia
  WHERE ia.parentItemID IN (ITEM_IDS)
    AND ia.contentType = 'application/pdf';
"
```

PDFs are at `~/Zotero/storage/<key>/<filename>.pdf`. Read them to extract the abstract.

**PDF folder:**

1. List all PDFs in the given path.
2. Read each PDF — extract title, authors, year, abstract, DOI/URL from the content.
3. For bulk keyword search: `pdfgrep -r -i "KEYWORD" <folder>` (install via package manager if missing, e.g., `apt install pdfgrep` or `brew install pdfgrep`).

**Google Scholar:**

1. Fetch the profile page.
2. Extract paper titles, years, citation counts.
3. For each paper, search for the DOI and abstract via WebSearch.

**Step 3 — Produce the registry.** Output a folder at a location the user specifies, or default to `articles/personal-registry/`, containing:

**1. `summary.md`** — all papers listed by topic cluster, with BibTeX cite keys (e.g., `[AuthorYear]`) as indices.

**2. `references.bib`** — BibTeX entries. Every entry **must** contain:

- `abstract` — the paper's abstract
- `doi` or `url` — at least one identifier for retrieval
