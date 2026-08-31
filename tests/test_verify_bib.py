"""Tests for the dependency-free BibTeX metadata verifier."""
import importlib.util
import json
import sys
from pathlib import Path


HELPERS = Path(__file__).resolve().parents[1] / "skills" / "how-to-download-ref" / "helpers"
HELPER = HELPERS / "verify_bib.py"


def _load():
    sys.path.insert(0, str(HELPERS))
    try:
        spec = importlib.util.spec_from_file_location("verify_bib_helper", HELPER)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.path.pop(0)


def _metadata(title, *, authors=None, year=2024, venue="Journal of Tests",
              venue_aliases=None, volume="7", pages="10-20", doi=None, arxiv=None):
    external = {}
    if doi:
        external["DOI"] = doi
    if arxiv:
        external["ArXiv"] = arxiv
    return {
        "paperId": f"paper-{title}",
        "title": title,
        "authors": [{"name": author} for author in (authors or ["Ada Lovelace"])],
        "year": year,
        "venue": venue,
        "publicationVenue": {
            "name": venue,
            "alternate_names": venue_aliases or [],
        },
        "journal": {"name": venue, "volume": volume, "pages": pages},
        "externalIds": external,
    }


def test_parse_bib_handles_nested_braces_and_all_real_entries():
    mod = _load()
    entries = mod.parse_bib(r'''
@string{jtest = "Journal of Tests"}
@article{nested,
  title = {A {Nested {Quantum}} Title},
  author = {Lovelace, Ada and {The ATLAS Collaboration}},
  journal = jtest,
  note = {A 3" disk},
  year = 2024,
}
@inproceedings(quoted,
  title = "A quoted title",
  booktitle = {Proceedings of Tests}
)
''')

    assert [entry["key"] for entry in entries] == ["nested", "quoted"]
    assert entries[0]["fields"]["title"] == "A {Nested {Quantum}} Title"
    assert entries[0]["fields"]["journal"] == "Journal of Tests"
    assert entries[0]["fields"]["note"] == 'A 3" disk'


def test_parser_ignores_email_addresses_between_entries():
    mod = _load()
    entries = mod.parse_bib('''
@article{one, title={First}}
Contact author@example.com for details.
@article{two, title={Second}}
''')

    assert [entry["key"] for entry in entries] == ["one", "two"]


def test_identifier_prefers_normalized_doi_then_arxiv_then_title():
    mod = _load()
    both = {"fields": {
        "doi": "https://doi.org/10.1000/ABC.",
        "eprint": "2401.12345v2",
        "archiveprefix": "arXiv",
    }}
    arxiv = {"fields": {"eprint": "2401.54321v3", "archiveprefix": "arXiv"}}
    title = {"fields": {"title": "No identifiers"}}

    assert mod.entry_identifier(both) == ("doi", "10.1000/abc")
    assert mod.entry_identifier(arxiv) == ("arxiv", "2401.54321")
    assert mod.entry_identifier(title) is None


def test_compare_normalizes_cosmetic_differences_and_ranks_real_findings():
    mod = _load()
    entry = {
        "key": "lovelace2023",
        "type": "article",
        "fields": {
            "title": "A {Quantum}-Test!",
            "author": "Lovelace, Ada",
            "year": "2023",
            "journal": "Journal of Tests",
            "volume": "7",
            "pages": "10--20",
        },
    }
    metadata = _metadata(
        "A Quantum Test", year=2024, pages="10 – 20", doi="10.1000/test",
    )

    result = mod.compare_entry(entry, metadata, {"type": "title", "value": "A", "source": "title"})

    assert result["status"] == "mismatch"
    assert result["severity"] == "high"
    assert [(finding["field"], finding["kind"], finding["severity"])
            for finding in result["findings"]] == [
        ("year", "mismatch", "high"),
        ("doi", "missing", "low"),
    ]
    assert mod.normalize_author("Lovelace, Jr., Ada") == mod.normalize_author("Ada Lovelace Jr.")


def test_incomplete_metadata_is_unverifiable_not_ok():
    mod = _load()
    entry = {
        "key": "partial",
        "type": "article",
        "fields": {"title": "Partial Paper", "author": "Ada Lovelace", "year": "2024"},
    }
    metadata = {"paperId": "partial", "title": "Partial Paper"}

    result = mod.compare_entry(entry, metadata, {"type": "doi", "value": "10.1/x", "source": "cache"})

    assert result["status"] == "unverifiable"
    assert result["unverified_fields"] == ["authors", "year"]
    assert [(finding["field"], finding["kind"]) for finding in result["findings"]] == [
        ("authors", "unverifiable"),
        ("year", "unverifiable"),
    ]


def test_comparison_accepts_venue_abbreviations_and_truncated_authors():
    mod = _load()
    entry = {
        "key": "abbreviated",
        "type": "article",
        "fields": {
            "title": "Abbreviated Metadata",
            "author": "Ada Lovelace and others",
            "year": "2024",
            "journal": "Phys. Rev. Lett.",
        },
    }
    metadata = _metadata(
        "Abbreviated Metadata",
        authors=["Ada Lovelace", "Grace Hopper"],
        venue="Physical Review Letters",
        venue_aliases=["Phys Rev Lett"],
        volume=None,
        pages=None,
    )

    result = mod.compare_entry(entry, metadata, {"type": "title", "value": "Abbreviated Metadata", "source": "title"})

    assert result["status"] == "ok"
    assert result["findings"] == []


def test_search_title_unwraps_live_response_shape_and_rejects_wrong_match(monkeypatch):
    mod = _load()

    class Response:
        def __init__(self, payload):
            self.payload = payload

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return json.dumps(self.payload).encode()

    exact = _metadata("Exact Paper", doi="10.1000/exact") | {"matchScore": 177.0}
    monkeypatch.setattr(mod.urllib.request, "urlopen", lambda *args, **kwargs: Response({"data": [exact]}))
    assert mod.search_title("Exact-Paper!") == exact

    wrong = _metadata("Different Paper", doi="10.1000/wrong") | {"matchScore": 170.0}
    monkeypatch.setattr(mod.urllib.request, "urlopen", lambda *args, **kwargs: Response({"data": [wrong]}))
    assert mod.search_title("Requested Paper") is None


def test_verify_uses_cache_batch_and_title_lookup_for_every_entry(tmp_path, monkeypatch):
    mod = _load()
    bib = tmp_path / "references.bib"
    bib.write_text(r'''
@article{cached, title={Cached Paper}, author={Ada Lovelace}, year={2024}, doi={10.1/cached}}
@article{batched, title={Batched Paper}, author={Ada Lovelace}, year={2024}, eprint={2401.12345}, archivePrefix={arXiv}}
@article{orphan, title={Uncited Orphan}, author={Ada Lovelace}, year={2024}}
''')
    cached = _metadata("Cached Paper", doi="10.1/cached")
    cache_path = tmp_path / ".raw" / "doi" / "10.1-cached.json"
    cache_path.parent.mkdir(parents=True)
    cache_path.write_text(json.dumps(cached))
    calls = {"batch": [], "titles": []}

    def fake_batch(ids):
        calls["batch"].append(ids)
        return [_metadata("Batched Paper", arxiv="2401.12345")]

    def fake_title(title):
        calls["titles"].append(title)
        return _metadata(title, doi="10.1/orphan")

    monkeypatch.setattr(mod, "post_batch", fake_batch)
    monkeypatch.setattr(mod, "search_title", fake_title)

    report = mod.verify_bibliography(bib, tmp_path)

    assert {entry["key"] for entry in report["entries"]} == {"cached", "batched", "orphan"}
    by_key = {entry["key"]: entry for entry in report["entries"]}
    assert by_key["cached"]["lookup"]["source"] == "cache"
    assert by_key["batched"]["lookup"]["source"] == "batch"
    assert by_key["orphan"]["lookup"]["source"] == "title"
    assert calls == {"batch": [["ARXIV:2401.12345"]], "titles": ["Uncited Orphan"]}
    assert (tmp_path / ".raw" / "arxiv" / "2401.12345.json").is_file()
    assert (tmp_path / ".raw" / "doi" / "10.1-orphan.json").is_file()


def test_title_lookup_is_deduplicated_and_reused_from_cache(tmp_path, monkeypatch):
    mod = _load()
    bib = tmp_path / "references.bib"
    bib.write_text(r'''
@article{one, title={Cached Title}, author={Ada Lovelace}, year={2024}}
@article{two, title={cached-title!}, author={Ada Lovelace}, year={2024}}
''')
    calls = []

    def fake_title(title):
        calls.append(title)
        return _metadata("Cached Title", doi="10.1/title")

    monkeypatch.setattr(mod, "search_title", fake_title)
    first = mod.verify_bibliography(bib, tmp_path)
    assert calls == ["Cached Title"]
    assert {entry["lookup"]["source"] for entry in first["entries"]} == {"title"}

    monkeypatch.setattr(mod, "search_title", lambda title: (_ for _ in ()).throw(AssertionError("network used")))
    second = mod.verify_bibliography(bib, tmp_path)
    assert {entry["lookup"]["source"] for entry in second["entries"]} == {"cache"}


def test_completed_scan_with_findings_exits_zero_and_json_matches_table(tmp_path, monkeypatch, capsys):
    mod = _load()
    bib = tmp_path / "references.bib"
    bib.write_text("""@article{wrong,
  title={Wrong Year},
  author={Ada Lovelace},
  year={2020},
  journal={Journal of Tests},
  volume={7},
  pages={10--20},
  doi={10.1/wrong}
}""")
    monkeypatch.setattr(mod, "post_batch", lambda ids: [
        _metadata("Wrong Year", year=2024, doi="10.1/wrong")
    ])

    assert mod.main(["--bib", str(bib), "--json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["summary"]["mismatch"] == 1
    assert report["summary"]["findings"]["high"] == 1
    table = mod.render_table(report)
    assert "wrong" in table
    assert "1 entries: 0 ok, 1 mismatch, 0 unverifiable" in table


def test_malformed_bib_exits_two(tmp_path, capsys):
    mod = _load()
    bib = tmp_path / "broken.bib"
    bib.write_text("@article{broken, title={Never closes}")

    assert mod.main(["--bib", str(bib), "--json"]) == 2
    assert "verification failed" in capsys.readouterr().err


def test_plain_text_and_malformed_headers_fail_but_comments_may_be_empty(tmp_path, capsys):
    mod = _load()
    plain = tmp_path / "plain.bib"
    plain.write_text("this is not a bibliography")
    assert mod.main(["--bib", str(plain), "--json"]) == 2
    assert "no valid BibTeX entries" in capsys.readouterr().err

    malformed = tmp_path / "malformed.bib"
    malformed.write_text("@article broken")
    assert mod.main(["--bib", str(malformed), "--json"]) == 2
    assert "malformed BibTeX declaration" in capsys.readouterr().err

    comments = tmp_path / "comments.bib"
    comments.write_text("% @article{fake, title={Not an entry}}\n")
    assert mod.main(["--bib", str(comments), "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["summary"]["entries"] == 0
