#!/usr/bin/env python3
"""Parse a Zotero SQLite database and produce a personal survey registry.

Usage:
    python parse_zotero.py <zotero.sqlite> <output_dir>

Produces:
    <output_dir>/summary.md      — papers listed by topic cluster
    <output_dir>/references.bib  — BibTeX entries with DOI/URL
"""

import re
import shutil
import sqlite3
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Topic classification keywords — ordered most-specific-first
# ---------------------------------------------------------------------------
TOPIC_PATTERNS = [
    # Quantum sub-fields (specific first)
    ("quantum error correct|fault.tolerant|surface code|stabilizer code", "Quantum Error Correction"),
    ("tensor network|tensor train|matrix product state|\\bmps\\b|\\bdmrg\\b|\\bpeps\\b|tensor contract|tensor decompos", "Tensor Networks"),
    ("variational quantum|\\bvqe\\b|\\bqaoa\\b", "Variational Quantum Algorithms"),
    ("quantum circuit|circuit optim|quantum compil|zx.calculus|\\bgate\\b", "Quantum Circuits & Compilation"),
    ("quantum simul|hamiltonian simul|trotter|quantum walk", "Quantum Simulation"),
    ("entangle|quantum inform|quantum channel|quantum entrop|\\bbell\\b", "Quantum Information Theory"),
    # Physics
    ("many.body|condensed matter|hubbard|strongly correlat|topolog|superconduct|phase transition", "Many-Body Physics & Condensed Matter"),
    ("\\bising\\b|\\bspin\\b|partition function|monte carlo|statistical mechanic|renormali", "Statistical Mechanics & Spin Models"),
    # CS / Math
    ("automatic differ|autodiff|differentiable program|backpropagat|adjoint method|reverse.mode|forward.mode", "Automatic Differentiation"),
    ("neural network|deep learn|machine learn|reinforcement learn|generative model|diffusion model|\\btransformer\\b|graph neural", "Machine Learning"),
    ("optim|\\balgorithm", "Optimization & Algorithms"),
    ("comput complex|\\bnp.hard", "Computational Complexity"),
    ("\\bgraph\\b|combinator", "Graph Theory & Combinatorics"),
    ("symmetr|group theor|representat|equivariant", "Group Theory & Symmetry"),
    ("probabili|bayesian|stochastic", "Probability & Statistics"),
    ("\\bjulia\\b|compiler|programm", "Programming Languages & Software"),
    # Broad quantum catch-all (must be last among quantum patterns)
    ("quantum|\\bqubit", "Quantum Computing (General)"),
]


def find_zotero_db():
    """Search standard Zotero database locations."""
    candidates = [
        Path.home() / "Zotero" / "zotero.sqlite",
        Path.home() / "Library" / "Application Support" / "Zotero" / "zotero.sqlite",
        Path.home() / "snap" / "zotero-snap" / "common" / "Zotero" / "zotero.sqlite",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def copy_db(src: Path) -> Path:
    """Copy the database to a temp file to avoid locking issues."""
    tmp = Path(tempfile.mktemp(suffix=".sqlite"))
    shutil.copy2(src, tmp)
    return tmp


def query_items(db_path: Path) -> dict:
    """Extract all items with metadata using a pivot query."""
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("""
        SELECT i.itemID,
            MAX(CASE WHEN f.fieldName = 'title' THEN idv.value END),
            MAX(CASE WHEN f.fieldName = 'abstractNote' THEN idv.value END),
            MAX(CASE WHEN f.fieldName = 'DOI' THEN idv.value END),
            MAX(CASE WHEN f.fieldName = 'date' THEN idv.value END),
            MAX(CASE WHEN f.fieldName = 'url' THEN idv.value END)
        FROM items i
        JOIN itemData id ON i.itemID = id.itemID
        JOIN fields f ON id.fieldID = f.fieldID
        JOIN itemDataValues idv ON id.valueID = idv.valueID
        WHERE i.itemTypeID NOT IN (
            SELECT itemTypeID FROM itemTypes WHERE typeName IN ('attachment', 'note'))
            AND f.fieldName IN ('title', 'abstractNote', 'DOI', 'date', 'url')
        GROUP BY i.itemID
        HAVING MAX(CASE WHEN f.fieldName = 'title' THEN idv.value END) IS NOT NULL
        ORDER BY i.itemID
    """)
    items = {}
    for row in cur.fetchall():
        item_id, title, abstract, doi, date, url = row
        year_match = re.search(r"(\d{4})", date or "")
        items[item_id] = {
            "title": title or "",
            "abstract": abstract or "",
            "doi": doi or "",
            "year": year_match.group(1) if year_match else "",
            "url": url or "",
            "authors": "",
        }
    conn.close()
    return items


def query_authors(db_path: Path) -> dict:
    """Extract authors grouped by item ID."""
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute("""
        SELECT ic.itemID,
            GROUP_CONCAT(c.lastName || ', ' || c.firstName, '; ')
        FROM itemCreators ic
        JOIN creators c ON ic.creatorID = c.creatorID
        WHERE ic.creatorTypeID = (
            SELECT creatorTypeID FROM creatorTypes WHERE creatorType = 'author')
        GROUP BY ic.itemID
        ORDER BY ic.itemID
    """)
    authors = {}
    for row in cur.fetchall():
        authors[row[0]] = row[1] or ""
    conn.close()
    return authors


def make_cite_key(authors: str, year: str, title: str) -> str:
    """Generate an AuthorYear cite key from the first author's last name."""
    if authors:
        first_author = authors.split(";")[0].split(",")[0].strip()
        first_author = re.sub(r"[^a-zA-Z]", "", first_author)
    else:
        words = re.sub(r"[^a-zA-Z\s]", "", title).split()
        first_author = words[0] if words else "Unknown"
    return f"{first_author}{year or 'XXXX'}"


def assign_cite_keys(items: dict) -> None:
    """Assign deduplicated cite keys to all items (mutates in place)."""
    key_counts = defaultdict(int)
    for item in items.values():
        base = make_cite_key(item["authors"], item["year"], item["title"])
        key_counts[base] += 1
        if key_counts[base] > 1:
            item["cite_key"] = f"{base}{chr(96 + key_counts[base])}"
        else:
            item["cite_key"] = base


def classify(title: str, abstract: str) -> str:
    """Classify a paper into a topic by keyword matching."""
    text = (title + " " + abstract).lower()
    for pattern, category in TOPIC_PATTERNS:
        if re.search(pattern, text):
            return category
    return "Other"


def write_summary(items: dict, output_dir: Path) -> None:
    """Write summary.md grouped by topic."""
    topic_items = defaultdict(list)
    for item in items.values():
        topic_items[classify(item["title"], item["abstract"])].append(item)

    sorted_topics = sorted(topic_items, key=lambda c: -len(topic_items[c]))

    with open(output_dir / "summary.md", "w") as f:
        f.write("# Personal Research Library\n\n")
        f.write(f"**Total papers:** {len(items)}\n\n")
        f.write("## Topic Overview\n\n")
        for topic in sorted_topics:
            f.write(f"- **{topic}**: {len(topic_items[topic])} papers\n")
        f.write("\n---\n\n")
        for topic in sorted_topics:
            f.write(f"## {topic}\n\n")
            sorted_items = sorted(
                topic_items[topic], key=lambda x: x.get("year") or "0000", reverse=True
            )
            for item in sorted_items:
                year_str = f" ({item['year']})" if item["year"] else ""
                authors_parts = item["authors"].split(";")
                authors_short = authors_parts[0].strip() if item["authors"] else ""
                if len(authors_parts) > 1:
                    authors_short += " et al."
                f.write(f"- [{item['cite_key']}] {authors_short}{year_str}: *{item['title']}*\n")
            f.write("\n")


def format_authors_bibtex(authors_str: str) -> str:
    """Convert 'Last, First; Last, First' to BibTeX 'Last, First and Last, First'."""
    if not authors_str:
        return ""
    return " and ".join(a.strip() for a in authors_str.split(";"))


def write_bibtex(items: dict, output_dir: Path) -> int:
    """Write references.bib, returning count of entries written."""
    count = 0
    with open(output_dir / "references.bib", "w") as f:
        for item in items.values():
            if not item["doi"] and not item["url"]:
                continue
            count += 1
            f.write(f"@article{{{item['cite_key']},\n")
            if item["authors"]:
                f.write(f"  author = {{{format_authors_bibtex(item['authors'])}}},\n")
            f.write(f"  title = {{{item['title']}}},\n")
            if item["year"]:
                f.write(f"  year = {{{item['year']}}},\n")
            if item["doi"]:
                f.write(f"  doi = {{{item['doi']}}},\n")
            if item["url"]:
                f.write(f"  url = {{{item['url']}}},\n")
            if item["abstract"]:
                abstract_oneline = " ".join(item["abstract"].split())
                f.write(f"  abstract = {{{abstract_oneline}}},\n")
            f.write("}\n\n")
    return count


def main():
    if len(sys.argv) < 3:
        # Try to auto-detect
        db_path = find_zotero_db() if len(sys.argv) < 2 else Path(sys.argv[1])
        output_dir = Path(sys.argv[2]) if len(sys.argv) >= 3 else None
        if db_path is None:
            print("Usage: python parse_zotero.py <zotero.sqlite> <output_dir>")
            print("Could not auto-detect Zotero database location.")
            sys.exit(1)
        if output_dir is None:
            print("Usage: python parse_zotero.py <zotero.sqlite> <output_dir>")
            sys.exit(1)
    else:
        db_path = Path(sys.argv[1])
        output_dir = Path(sys.argv[2])

    if not db_path.exists():
        print(f"Error: database not found at {db_path}")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Copy to avoid locking
    print(f"Copying database from {db_path}...")
    tmp_db = copy_db(db_path)

    try:
        print("Querying items...")
        items = query_items(tmp_db)
        print(f"  Found {len(items)} items")

        print("Querying authors...")
        authors = query_authors(tmp_db)
        for item_id, author_str in authors.items():
            if item_id in items:
                items[item_id]["authors"] = author_str
        print(f"  Found authors for {len(authors)} items")
    finally:
        tmp_db.unlink(missing_ok=True)

    print("Assigning cite keys...")
    assign_cite_keys(items)

    print("Writing summary.md...")
    write_summary(items, output_dir)

    print("Writing references.bib...")
    bib_count = write_bibtex(items, output_dir)
    print(f"  {bib_count} entries with DOI or URL (out of {len(items)} total)")

    print(f"\nDone. Output at {output_dir}/")


if __name__ == "__main__":
    main()
