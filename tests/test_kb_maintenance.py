"""Behavioral checks for acquisition, annotations, identity, and cache maintenance."""
import json
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

HELPERS = Path(__file__).resolve().parents[1] / 'skills/how-to-download-ref/helpers'
sys.path.insert(0, str(HELPERS))
import append_bibtex as bib
import fetch_metadata as fetch
import import_pdfs
import index
import kb_doctor as doctor
import kb_identity as identity
import kb_sync as sync
import render

DOI = '10.1234/example'
ARXIV = '2601.12345'
META = {'title': 'A test paper', 'authors': [{'name': 'Test Author'}], 'year': 2026,
        'venue': 'Test Journal', 'abstract': 'An abstract. ' * 60,
        'externalIds': {'DOI': DOI, 'ArXiv': ARXIV},
        'citationStyles': {'bibtex': '@article{test, title={A test paper}, author={Test Author}, journal={Test Journal}, year={2026}, doi={10.1234/example}, eprint={2601.12345}}'}}
PDF = b'%PDF-1.7\n' + b'x' * 1100 + b'\n%%EOF\n'


def seed(kb):
    fetch.save(kb / '.raw/doi/10.1234-example.json', META)
    render.render_doi(kb, kb / '.raw')
    (kb / 'references.bib').write_text(META['citationStyles']['bibtex'])
    index.main(['--kb', str(kb), '--title', 'Reading list', '--source-note', 'Keep this note.'])
    return kb / '10-1234-example.md'


def invoke_fetch(monkeypatch, kb, manifest, *flags):
    mf = kb.parent / 'manifest.json'
    mf.write_text(json.dumps(manifest))
    monkeypatch.setattr(sys, 'argv', ['fetch_metadata.py', '--kb', str(kb), '--manifest', str(mf), '--no-aps', *flags])
    monkeypatch.setattr(fetch.time, 'sleep', lambda _: None)
    return fetch.main()


def test_rerender_keeps_human_yaml_and_refreshes_generated_content(tmp_path):
    md = seed(tmp_path)
    human = 'note: |\n  read section 3\n  compare with my result\ntags:\n  - dmrg\n  - "review: later"\nrating: 5\n'
    md.write_text(md.read_text().replace('---\n', '---\n' + human, 1).replace('title: "A test paper"', 'title: "WRONG"') + '\nDELETE BODY MARKER')
    render.render_doi(tmp_path, tmp_path / '.raw')
    assert human in md.read_text()
    assert 'title: "A test paper"' in md.read_text()
    assert 'WRONG' not in md.read_text() and 'DELETE BODY MARKER' not in md.read_text()
    for kind in ('arxiv', 'web', 'github', 'stub'):
        path = tmp_path / f'{kind}.md'
        path.write_text('---\n' + human + 'title: WRONG\n---\nold body')
        render.write_rendered(path, ['---\ntitle: "Refreshed"\nnote: "machine note"\n---', 'new body'])
        assert human in path.read_text() and 'machine note' not in path.read_text()
    bad = tmp_path / 'bad.md'
    bad.write_text('---\nnote: do not lose this')
    with pytest.raises(ValueError, match='refusing'):
        render.write_rendered(bad, ['---\ntitle: test\n---'])
    assert 'do not lose this' in bad.read_text()


def test_alias_add_render_and_bib_append_do_not_duplicate(tmp_path, monkeypatch, capsys):
    md = seed(tmp_path)
    monkeypatch.setattr(fetch, 'post_batch', lambda _: pytest.fail('known alias should not use network'))
    invoke_fetch(monkeypatch, tmp_path, {'arxiv': [ARXIV + 'v2']})
    assert 'present' in capsys.readouterr().out
    assert not (tmp_path / '.raw/arxiv').exists()
    fetch.save(tmp_path / f'.raw/arxiv/{ARXIV}.json', META)
    render.render_arxiv(tmp_path, tmp_path / '.raw')
    assert sorted(p.name for p in tmp_path.glob('*.md')) == ['10-1234-example.md', 'INDEX.md']
    before = (tmp_path / 'references.bib').read_bytes()
    bib.cmd_append(SimpleNamespace(kb=str(tmp_path), type='arxiv', id=ARXIV, key='different_key', bib=str(tmp_path / 'references.bib')))
    assert (tmp_path / 'references.bib').read_bytes() == before
    # Changed source title must update the existing path and retain annotations.
    md.write_text(md.read_text().replace('---\n', '---\nnote: keep\n', 1))
    updated = {**META, 'title': 'Revised title'}
    fetch.save(tmp_path / '.raw/doi/10.1234-example.json', updated)
    render.render_doi(tmp_path, tmp_path / '.raw')
    assert 'Revised title' in md.read_text() and 'note: keep' in md.read_text()


def test_batch_dedup_resolves_aliases_and_allows_explicit_override(tmp_path, monkeypatch):
    monkeypatch.setattr(fetch, 'post_batch', lambda ids: [META for _ in ids])
    invoke_fetch(monkeypatch, tmp_path, {'arxiv': [ARXIV], 'doi': [DOI]})
    assert len(list((tmp_path / '.raw').glob('*/*.json'))) == 1
    invoke_fetch(monkeypatch, tmp_path, {'doi': [DOI]}, '--allow-duplicate')
    assert len(list((tmp_path / '.raw').glob('*/*.json'))) == 2
    with pytest.raises(SystemExit) as error:
        invoke_fetch(monkeypatch, tmp_path, {'arxiv': ['../../escape']})
    assert error.value.code == 2


class Response:
    def __init__(self, body): self.body = body
    def __enter__(self): return self
    def __exit__(self, *args): pass
    def read(self): return self.body


def atom(*entries):
    body = ''.join(f'''<entry><id>http://arxiv.org/abs/{aid}v2</id><title>{title}</title>
        <published>2013-05-31T00:00:00Z</published><summary>Abstract.</summary>
        <author><name>Daniel Kats</name></author>{f"<arxiv:doi>{doi}</arxiv:doi>" if doi else ""}</entry>'''
        for aid, title, doi in entries)
    return ('<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">'
            + body + '</feed>').encode()


def test_s2_rate_limit_fails_fast(monkeypatch):
    sleeps, calls = [], []
    def urlopen(req, **kwargs):
        calls.append(req.full_url)
        raise fetch.urllib.error.HTTPError(req.full_url, 429, 'Too Many Requests', {}, None)
    monkeypatch.setattr(fetch.urllib.request, 'urlopen', urlopen)
    monkeypatch.setattr(fetch.time, 'sleep', sleeps.append)
    with pytest.raises(fetch.urllib.error.HTTPError):
        fetch.post_batch(['DOI:' + DOI])
    assert len(calls) == 3 and sum(sleeps) <= 10


def test_arxiv_api_fallback_when_s2_unavailable(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(fetch, 'post_batch', lambda ids: (_ for _ in ()).throw(OSError('HTTP Error 429')))
    calls = []
    def urlopen(req, **kwargs):
        calls.append(req.full_url)
        return Response(atom((ARXIV, 'The distinguishable  cluster approximation', '10.1063/1.4813481')))
    monkeypatch.setattr(fetch.urllib.request, 'urlopen', urlopen)
    invoke_fetch(monkeypatch, tmp_path, {'arxiv': [ARXIV]})
    meta = json.loads((tmp_path / f'.raw/arxiv/{ARXIV}.json').read_text())
    assert meta['metadata_source'] == 'arxiv' and meta['title'] == 'The distinguishable cluster approximation'
    assert meta['externalIds'] == {'ArXiv': ARXIV, 'DOI': '10.1063/1.4813481'} and meta['year'] == 2013
    assert 'eprint = {2601.12345}' in meta['citationStyles']['bibtex']
    assert len(calls) == 1 and 'id_list=' in calls[0]
    assert f'ok arxiv:{ARXIV} (arxiv)' in capsys.readouterr().out


def test_crossref_record_links_arxiv_preprint_by_exact_title(monkeypatch):
    monkeypatch.setattr(fetch, 'post_batch', lambda ids: [None] * len(ids))
    monkeypatch.setattr(fetch.time, 'sleep', lambda _: None)
    monkeypatch.setattr(fetch, 'crossref_metadata', lambda doi, email: {'title': 'The distinguishable cluster approximation', 'externalIds': {'DOI': doi}})
    monkeypatch.setattr(fetch.urllib.request, 'urlopen', lambda req, **kw: Response(atom(
        ('1903.06932', 'On the distinguishable cluster approximation for triple excitations', None),
        ('1305.7451', 'The Distinguishable Cluster Approximation', None))))
    [meta] = fetch.lookup_metadata([('doi', '10.1063/1.4813481')])
    assert meta['externalIds'] == {'DOI': '10.1063/1.4813481', 'ArXiv': '1305.7451'}


def test_crossref_miss_fallback_reaches_render_and_bibliography(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(fetch, 'post_batch', lambda ids: [None] * len(ids))
    calls = []
    crossref = json.dumps({'message': {'DOI': DOI, 'title': ['A & B'], 'author': [{'given': 'Test', 'family': 'Author'}], 'published': {'date-parts': [[2026]]}, 'container-title': ['Chemistry Journal'], 'type': 'journal-article'}}).encode()
    def urlopen(req, **kwargs):
        calls.append(req.full_url)
        return Response(atom() if 'arxiv.org' in req.full_url else crossref)
    monkeypatch.setattr(fetch.urllib.request, 'urlopen', urlopen)
    invoke_fetch(monkeypatch, tmp_path, {'doi': [DOI]}, '--email', 'reader@example.org')
    meta = json.loads((tmp_path / '.raw/doi/10.1234-example.json').read_text())
    assert meta['title'] == 'A & B' and meta['year'] == 2026
    assert meta['authors'] == [{'name': 'Test Author'}]
    assert meta['metadata_source'] == 'crossref'
    assert '(crossref)' in capsys.readouterr().out
    assert len(calls) == 2 and 'api.crossref.org/works/' in calls[0] and 'search_query=ti' in calls[1]
    assert 'ArXiv' not in meta['externalIds']
    render.render_doi(tmp_path, tmp_path / '.raw')
    assert 'full_text: no' in (tmp_path / '10-1234-example.md').read_text()
    bib.cmd_append(SimpleNamespace(kb=str(tmp_path), type='doi', id=DOI, key='author_2026_test', bib=str(tmp_path / 'references.bib')))
    assert 'journal = {Chemistry Journal}' in (tmp_path / 'references.bib').read_text()
    calls.clear()
    monkeypatch.setattr(fetch, 'post_batch', lambda _: pytest.fail('cache must avoid network'))
    invoke_fetch(monkeypatch, tmp_path, {'doi': [DOI]})
    assert calls == []


def test_s2_known_record_unchanged_and_double_miss_clean(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(fetch, 'post_batch', lambda ids: [META])
    monkeypatch.setattr(fetch, 'crossref_metadata', lambda *args: pytest.fail('known DOI must not call Crossref'))
    invoke_fetch(monkeypatch, tmp_path, {'doi': [DOI]})
    assert json.loads((tmp_path / '.raw/doi/10.1234-example.json').read_text()) == META
    monkeypatch.undo()
    monkeypatch.setattr(fetch, 'post_batch', lambda ids: [None])
    monkeypatch.setattr(fetch, 'get_json', lambda *args: (_ for _ in ()).throw(OSError('404')))
    invoke_fetch(monkeypatch, tmp_path, {'doi': ['10.9999/missing']})
    assert not (tmp_path / '.raw/doi/10.9999-missing.json').exists()
    assert 'miss doi:10.9999/missing' in capsys.readouterr().err


@pytest.mark.parametrize('payload,locations,expected', [
    (PDF, [{'url_for_pdf': 'https://repository.example/paper.pdf'}], 'unpaywall'),
    (b'<html>login</html>', [{'url_for_pdf': 'https://repository.example/paper.pdf'}], 'arxiv'),
    (PDF, [], 'arxiv'),
])
def test_unpaywall_wiring_pdf_validation_and_fallback(tmp_path, monkeypatch, payload, locations, expected, capsys):
    urls = []
    class Response:
        def __init__(self, body): self.body = body
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self): return self.body
    def urlopen(req, **kwargs):
        urls.append(req.full_url)
        if 'api.unpaywall.org' in req.full_url:
            return Response(json.dumps({'best_oa_location': None, 'oa_locations': locations}).encode())
        return Response(PDF if 'arxiv.org' in req.full_url else payload)
    monkeypatch.setattr(fetch.urllib.request, 'urlopen', urlopen)
    monkeypatch.setattr(fetch, 'post_batch', lambda ids: [META])
    invoke_fetch(monkeypatch, tmp_path, {'doi': [DOI]}, '--download-arxiv-pdfs', '--email', 'reader@example.org')
    out = tmp_path / '.raw/doi/10.1234-example.pdf'
    assert out.read_bytes() == PDF and f'({expected})' in capsys.readouterr().out
    assert len(urls) == (3 if expected == 'arxiv' and locations else 2)
    urls.clear()
    assert fetch.fetch_doi_pdf(DOI, META, out, 'reader@example.org') == 'cached'
    assert urls == []
    assert fetch.unpaywall_urls(DOI, '') == []


def test_doctor_seeded_defects_and_safe_index_fix(tmp_path):
    md = seed(tmp_path)
    assert doctor.main(['--kb', str(tmp_path)]) == 0
    original = {p.name: p.read_bytes() for p in tmp_path.glob('*') if p.is_file() and p.name != 'INDEX.md'}
    idx = tmp_path / 'INDEX.md'
    idx.write_text(idx.read_text() + '| [ghost.md](ghost.md) | bogus |\n')
    assert doctor.main(['--kb', str(tmp_path), '--checks', 'index-sync']) == 1
    assert doctor.main(['--kb', str(tmp_path), '--fix']) == 0
    assert '# Reading list' in idx.read_text() and 'Keep this note.' in idx.read_text()
    assert {p.name: p.read_bytes() for p in tmp_path.glob('*') if p.is_file() and p.name != 'INDEX.md'} == original
    (tmp_path / 'duplicate.md').write_bytes(md.read_bytes())
    assert any(c == 'duplicate-identity' for _, c, _ in doctor.check_kb(tmp_path))
    (tmp_path / 'duplicate.md').unlink()
    md.write_text(md.read_text().replace('full_text: no\n', '').replace('year: "2026"', 'year: "bad"'))
    checks = {c for _, c, _ in doctor.check_kb(tmp_path)}
    assert {'frontmatter-required', 'frontmatter-types'} <= checks
    (tmp_path / 'references.bib').write_text('@book{broken, title={Book}, author={An Author}, year={2020}}')
    checks = {c for _, c, _ in doctor.check_kb(tmp_path)}
    assert {'bib-required-keys', 'bib-md-sync'} <= checks
    assert doctor.main(['--kb', str(tmp_path)]) == 1


def test_sync_restores_declared_namespace_without_touching_text(tmp_path, monkeypatch, capsys):
    seed(tmp_path)
    md = tmp_path / '10-1234-example.md'
    md.write_text(md.read_text().replace('full_text: no', 'full_text: latex'))
    original = {p.name: p.read_bytes() for p in tmp_path.glob('*') if p.is_file()}
    shutil.rmtree(tmp_path / '.raw')
    calls = []
    def lookup(refs, email):
        calls.extend(refs)
        return [META for _ in refs]
    def pdf(doi, meta, path, email):
        if not fetch.valid_pdf(path): path.write_bytes(PDF)
        return 'cached'
    def source(aid, kb, **kwargs):
        tex = kwargs['out_tex']; tex.write_text('source' * 30)
        figs = kb / '.figures' / kwargs['fig_subdir']; figs.mkdir(parents=True, exist_ok=True)
        (figs / 'figure.pdf').write_bytes(PDF)
        return 'cached'
    monkeypatch.setattr(sync, 'lookup_metadata', lookup)
    monkeypatch.setattr(sync, 'fetch_doi_pdf', pdf)
    monkeypatch.setattr(sync, 'fetch_arxiv_source', source)
    monkeypatch.setattr(sync.time, 'sleep', lambda _: None)
    assert sync.main(['--kb', str(tmp_path)]) == 0
    assert calls == [('doi', DOI)]
    assert (tmp_path / '.raw/doi/10.1234-example.tex').exists()
    assert not (tmp_path / '.raw/arxiv').exists()
    assert (tmp_path / '.figures/doi__10.1234-example/figure.pdf').is_file()
    assert original == {p.name: p.read_bytes() for p in tmp_path.glob('*') if p.is_file()}
    calls.clear()
    assert sync.main(['--kb', str(tmp_path)]) == 0 and calls == []
    (tmp_path / '.raw/doi/10.1234-example.pdf').write_bytes(b'truncated')
    assert sync.main(['--kb', str(tmp_path)]) == 0
    assert fetch.valid_pdf(tmp_path / '.raw/doi/10.1234-example.pdf')
    assert 'PASS doi:' in capsys.readouterr().out
    with pytest.raises(SystemExit) as error:
        sync.main(['--kb', str(tmp_path / 'empty')])
    assert error.value.code != 0


def test_pdf_figure_restore_preserves_links_and_skips_complete_cache(tmp_path, monkeypatch):
    subdir = 'doi__10.1234-example'
    target = tmp_path / '.figures' / subdir / 'paper.pdf-0-0.png'
    calls = []
    def extract(*args, **kwargs):
        calls.append(args)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b'image')
        return 'paper text'
    monkeypatch.setitem(sys.modules, 'pymupdf4llm', SimpleNamespace())
    monkeypatch.setattr(render, 'extract_pdf_text', extract)
    text = f'![](.figures/{subdir}/{target.name})'
    pdf = tmp_path / 'paper.pdf'; pdf.write_bytes(PDF)
    assert sync.restore_pdf_figures(tmp_path, pdf, subdir, text) == 'ok'
    assert sync.restore_pdf_figures(tmp_path, pdf, subdir, text) == 'cached'
    assert len(calls) == 1
    target.unlink()
    assert sync.restore_pdf_figures(tmp_path, pdf, subdir, text) == 'ok'
    assert len(calls) == 2


def test_copied_and_symlinked_skill_resources_work_from_external_project(tmp_path):
    root = HELPERS.parents[2]
    project = tmp_path / 'user project'; project.mkdir(); (project / '.git').mkdir()
    copied = tmp_path / 'installed skills'
    shutil.copytree(root / 'skills/how-to-download-ref', copied / 'how-to-download-ref')
    shutil.copytree(root / 'skills/how-to-write-ideas-report', copied / 'how-to-write-ideas-report')
    link = tmp_path / 'linked-download'; link.symlink_to(copied / 'how-to-download-ref', target_is_directory=True)
    for directory in (copied / 'how-to-download-ref', link.resolve()):
        result = subprocess.run([sys.executable, str(directory / 'helpers/resolve_kb.py')], cwd=project, text=True, capture_output=True, check=True)
        assert result.stdout.strip() == str(project / '.knowledge')
        assert (directory / 'helpers/kb_doctor.py').is_file()
    assert (copied / 'how-to-write-ideas-report/references/writing-workflow.md').is_file()
    assert (copied / 'how-to-write-ideas-report/references/typst-reference.md').is_file()
    for skill in (root / 'skills').glob('*/SKILL.md'):
        text = skill.read_text()
        assert '## Installed resources' in text
        assert 'skills/_shared/' not in text
        assert 'python3 skills/' not in text


def test_build_kb_handoff_fetches_full_text_in_existing_namespace(tmp_path, monkeypatch, capsys):
    md = seed(tmp_path)
    monkeypatch.setattr(fetch, 'post_batch', lambda _: pytest.fail('metadata already cached'))
    calls = []
    def pdf(doi, meta, path, email):
        calls.append(doi)
        path.write_bytes(PDF)
        return 's2'
    monkeypatch.setattr(fetch, 'fetch_doi_pdf', pdf)
    invoke_fetch(monkeypatch, tmp_path, {'doi': [DOI]}, '--download-arxiv-pdfs')
    assert calls == [DOI]
    monkeypatch.setattr(render, 'extract_pdf_text', lambda *a, **k: 'FULL TEXT AFTER SURVEY')
    render.render_doi(tmp_path, tmp_path / '.raw')
    assert 'full_text: yes' in md.read_text() and 'FULL TEXT AFTER SURVEY' in md.read_text()
    # Same namespace also works when the clone has no metadata cache yet.
    (tmp_path / '.raw/doi/10.1234-example.json').unlink()
    monkeypatch.setattr(fetch, 'post_batch', lambda _: [META])
    invoke_fetch(monkeypatch, tmp_path, {'doi': [DOI]})
    assert (tmp_path / '.raw/doi/10.1234-example.json').exists()
    assert len(list(tmp_path.glob('10*.md'))) == 1


def test_multiline_note_cannot_override_identity_and_bad_types_are_findings(tmp_path):
    md = seed(tmp_path)
    md.write_text(md.read_text().replace('---\n', '---\nnote: |\n  doi: verify later\n  type: prose\n', 1))
    assert index.parse_frontmatter(md)['doi'] == DOI
    render.render_doi(tmp_path, tmp_path / '.raw')
    assert '  doi: verify later' in md.read_text()
    assert doctor.main(['--kb', str(tmp_path)]) == 0
    md.write_text(md.read_text().replace('type: "doi"', 'type:\n  - doi'))
    (tmp_path / 'INDEX.md').unlink()
    assert doctor.main(['--kb', str(tmp_path), '--fix']) == 1
    assert not (tmp_path / 'INDEX.md').exists()


def test_crossref_doi_with_underscore_remains_usable(tmp_path, monkeypatch):
    import verify_bib
    doi = '10.1007/book_3'
    monkeypatch.setattr(fetch, 'get_json', lambda *args: {'message': {
        'DOI': doi, 'title': ['A <i>chapter</i>\n title'], 'author': [{'name': 'An Author'}],
        'issued': {'date-parts': [[2020]]}, 'publisher': 'Publisher',
        'container-title': ['Book'], 'type': 'book-chapter'}})
    meta = fetch.crossref_metadata(doi)
    assert meta['title'] == 'A chapter title'
    fetch.save(tmp_path / '.raw/doi/10.1007-book_3.json', meta)
    render.render_doi(tmp_path, tmp_path / '.raw')
    bib.cmd_append(SimpleNamespace(kb=str(tmp_path), type='doi', id=doi, key='chapter', bib=str(tmp_path / 'references.bib')))
    fields = verify_bib.parse_bib((tmp_path / 'references.bib').read_text())[0]['fields']
    assert fields['doi'] == doi
    index.main(['--kb', str(tmp_path), '--title', 'Chapters'])
    assert doctor.main(['--kb', str(tmp_path)]) == 0
    assert verify_bib._load_cache(verify_bib._cache_path(tmp_path, 'doi', doi)) == meta


def test_case_normalized_acquisition_preserves_legacy_cache_and_clone_paths(tmp_path, monkeypatch):
    mixed = '10.1103/PhysRevLett.130.036401'
    meta = {**META, 'externalIds': {'DOI': mixed}}
    monkeypatch.setattr(fetch, 'post_batch', lambda _: [meta])
    invoke_fetch(monkeypatch, tmp_path, {'doi': [mixed]})
    assert bib.load_meta(tmp_path, 'doi', mixed) == meta
    dest = identity.cache_path(tmp_path, 'doi', mixed)
    render.render_doi(tmp_path, tmp_path / '.raw')
    # Legacy caches retain the spelling used in existing figure links.
    legacy = dest.with_name(mixed.replace('/', '-') + '.json')
    dest.rename(legacy)
    assert identity.cache_path(tmp_path, 'doi', mixed.lower()) == legacy
    assert identity.cache_path(tmp_path, 'doi', mixed.lower(), '.pdf').stem == legacy.stem
    assert bib.load_meta(tmp_path, 'doi', mixed.lower()) == meta
    monkeypatch.setattr(fetch, 'post_batch', lambda _: pytest.fail('mixed-case cache should be reused'))
    invoke_fetch(monkeypatch, tmp_path, {'doi': [mixed.lower()]})
    legacy.unlink()
    assert identity.cache_path(tmp_path, 'doi', mixed.lower()).name == legacy.name


def test_cache_free_clone_uses_tracked_image_case_not_s2_doi_case(tmp_path):
    mixed = '10.1103/PhysRevLett.130.036401'
    meta = {**META, 'externalIds': {'DOI': mixed}}
    dest = identity.cache_path(tmp_path, 'doi', mixed)
    fetch.save(dest, meta)
    render.render_doi(tmp_path, tmp_path / '.raw')
    md = next(tmp_path.glob('*.md'))
    md.write_text(md.read_text() + f'\n![](.figures/doi__{dest.stem}/paper.pdf-0-0.png)\n')
    shutil.rmtree(tmp_path / '.raw')
    assert identity.cache_path(tmp_path, 'doi', mixed) == dest
    assert identity.cache_path(tmp_path, 'doi', mixed, '.pdf') == dest.with_suffix('.pdf')


def test_only_chemistry_publisher_misses_are_listed_for_a_person(tmp_path, monkeypatch, capsys):
    chem, aps = '10.1063/1.4944087', '10.1103/physrevb.98.045103'
    monkeypatch.setattr(fetch, 'post_batch', lambda ids: [dict(META, externalIds={'DOI': i.split(':', 1)[1]}) for i in ids])
    monkeypatch.setattr(fetch, 'fetch_doi_pdf', lambda *args: 'miss')
    monkeypatch.setattr(fetch, 'PROXY_PREFIX', 'https://proxy.example.edu/login?url=')
    invoke_fetch(monkeypatch, tmp_path, {'doi': [chem, aps]}, '--download-arxiv-pdfs', '--allow-duplicate')
    out = capsys.readouterr().out
    assert '1 chemistry-publisher PDF(s) need a human check' in out
    assert f'https://proxy.example.edu/login?url=https://doi.org/{chem}' in out
    assert f'https://doi.org/{aps}' not in out


def test_import_pdfs_matches_by_doi_then_title_and_skips_others(tmp_path, monkeypatch, capsys):
    kb, downloads = tmp_path / 'kb', tmp_path / 'Downloads'
    downloads.mkdir()
    papers = {'10.1063/1.4944087': 'Assessing the distinguishable cluster approximation',
              '10.1021/acs.jctc.2c00059': 'FCIQMC-tailored distinguishable cluster approach',
              '10.1103/physrevb.98.045103': 'An APS paper that is never imported'}
    for doi, title in papers.items():
        fetch.save(identity.cache_path(kb, 'doi', doi), {'title': title, 'externalIds': {'DOI': doi}})
    (downloads / '124117_1_online.pdf').write_bytes(PDF.replace(b'x' * 40, b'doi.org/10.1063/1.4944087.\nxxxxx', 1))
    (downloads / 'acs.pdf').write_bytes(PDF)
    (downloads / 'aps.pdf').write_bytes(PDF.replace(b'x' * 30, b'10.1103/PhysRevB.98.045103\nxxx', 1))
    (downloads / 'notes.pdf').write_bytes(PDF)
    real = import_pdfs.first_pages_text
    def text(pdf):
        title = b'FCIQMC-Tailored Distinguishable\nCluster Approach' if pdf.name == 'acs.pdf' else b''
        return title + real(pdf)
    monkeypatch.setattr(import_pdfs, 'first_pages_text', text)
    monkeypatch.setattr(sys, 'argv', ['import_pdfs.py', '--kb', str(kb), '--from', str(downloads)])
    assert import_pdfs.main() == 0
    raw = kb / '.raw/doi'
    assert (raw / '10.1063-1.4944087.pdf').read_bytes() == (downloads / '124117_1_online.pdf').read_bytes()
    assert (raw / '10.1021-acs.jctc.2c00059.pdf').exists()
    assert not (raw / '10.1103-physrevb.98.045103.pdf').exists()
    out = capsys.readouterr().out
    assert '2 imported' in out and 'notes.pdf' not in out
    assert import_pdfs.pending(kb) == {}


def test_append_adds_identity_fields_to_preprint_bibtex(tmp_path, capsys):
    # Semantic Scholar's bibtex for an arXiv-only preprint: no eprint, no doi,
    # @Inproceedings without booktitle.  Appended verbatim, kb_doctor reports
    # bib-md-sync "no rendered entry" and bib-required-keys "missing booktitle".
    arxiv = '2611.03241'
    meta = {'title': 'A preprint', 'authors': [{'name': 'Pre Print'}], 'year': 2026,
            'abstract': 'An abstract. ' * 60, 'externalIds': {'ArXiv': arxiv},
            'citationStyles': {'bibtex': '@Inproceedings{Print2026AP,\n author = {Pre Print},\n'
                                         ' title = {A preprint},\n year = {2026}\n}\n'}}
    fetch.save(tmp_path / f'.raw/arxiv/{arxiv}.json', meta)
    render.render_arxiv(tmp_path, tmp_path / '.raw')
    bib_path = tmp_path / 'references.bib'
    bib.cmd_append(SimpleNamespace(kb=str(tmp_path), type='arxiv', id=arxiv, key='print_2026_preprint', bib=str(bib_path)))
    assert 'appended' in capsys.readouterr().out
    text = bib_path.read_text()
    assert text.lstrip().startswith('@misc{print_2026_preprint,')
    assert f'eprint = {{{arxiv}}}' in text and 'archiveprefix = {arXiv}' in text
    index.main(['--kb', str(tmp_path), '--title', 'Reading list', '--source-note', ''])
    assert doctor.check_kb(tmp_path) == []
    # Re-running the append must recognise the paper by its new eprint field.
    bib.cmd_append(SimpleNamespace(kb=str(tmp_path), type='arxiv', id=arxiv, key='other_key', bib=str(bib_path)))
    assert 'skip: same paper' in capsys.readouterr().out
    # Entries that already carry identifiers and a booktitle are left alone.
    full = {**META, 'citationStyles': {'bibtex': '@inproceedings{k, title={T}, author={A}, booktitle={B}, year={2026}, doi={10.1234/example}, eprint={2601.12345}}'}}
    assert bib.ensure_identity_fields(full['citationStyles']['bibtex'], full) == full['citationStyles']['bibtex']
