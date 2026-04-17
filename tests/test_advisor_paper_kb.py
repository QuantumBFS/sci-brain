from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
ADVISORS = ["xi-dai", "lei-wang"]


def test_raw_advisor_cache_is_gitignored():
    text = (ROOT / ".gitignore").read_text()
    assert ".cache/advisors/" in text


def test_advisor_profiles_reference_publication_kb():
    for slug in ADVISORS:
        profile = (ROOT / "advisors" / slug / "profile.md").read_text()
        assert "## Publication Sources" in profile
        assert "## Representative Publications" in profile


def test_advisor_publication_manifests_define_ten_representative_papers():
    for slug in ADVISORS:
        manifest_path = ROOT / "advisors" / slug / "publications.yml"
        manifest = yaml.safe_load(manifest_path.read_text())

        assert manifest["advisor_slug"] == slug
        papers = manifest["papers"]
        assert len(papers) == 10

        for paper in papers:
            assert paper["title"]
            assert paper["year"]
            assert paper["summary"]
            assert paper["landing_url"]
            assert paper["pdf_url"]
            assert paper["kb_slug"]


def test_each_advisor_has_ten_markdown_paper_cards_and_an_index():
    for slug in ADVISORS:
        papers_dir = ROOT / "advisors" / slug / "papers"
        paper_cards = sorted(papers_dir.glob("*.md"))
        assert len(paper_cards) == 10

        index_path = ROOT / "advisors" / slug / "survey" / "index.md"
        index_text = index_path.read_text()

        for paper_card in paper_cards:
            assert paper_card.stem in index_text
