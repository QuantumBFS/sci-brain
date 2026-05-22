"""Tests for skills/download-ref/helpers/resolve_kb.py.

resolve_kb walks up from a starting directory looking for .git/, then returns
<root>/.knowledge as the project KB path. If no .git/ is found and the start
is at or above $HOME, it returns None to signal "ask the user".
"""
import importlib.util
import os
from pathlib import Path

import pytest


HELPER = Path(__file__).resolve().parents[1] / "skills" / "download-ref" / "helpers" / "resolve_kb.py"


def _load():
    spec = importlib.util.spec_from_file_location("resolve_kb", HELPER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_finds_git_root_from_subdirectory(tmp_path):
    repo = tmp_path / "proj"
    (repo / ".git").mkdir(parents=True)
    sub = repo / "src" / "deep"
    sub.mkdir(parents=True)
    mod = _load()
    assert mod.resolve_kb(start=sub) == repo / ".knowledge"


def test_finds_git_root_when_start_is_repo_root(tmp_path):
    repo = tmp_path / "proj"
    (repo / ".git").mkdir(parents=True)
    mod = _load()
    assert mod.resolve_kb(start=repo) == repo / ".knowledge"


def test_returns_none_when_at_or_above_home_with_no_git(tmp_path, monkeypatch):
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))
    mod = _load()
    # Exactly at $HOME with no .git/
    assert mod.resolve_kb(start=fake_home) is None
    # Above $HOME with no .git/
    assert mod.resolve_kb(start=tmp_path) is None


def test_falls_back_to_start_when_no_git_but_below_home(tmp_path, monkeypatch):
    fake_home = tmp_path / "home"
    (fake_home / "scratch").mkdir(parents=True)
    monkeypatch.setenv("HOME", str(fake_home))
    mod = _load()
    start = fake_home / "scratch"
    assert mod.resolve_kb(start=start) == start / ".knowledge"


def test_cli_prints_kb_path(tmp_path, capsys):
    repo = tmp_path / "proj"
    (repo / ".git").mkdir(parents=True)
    mod = _load()
    rc = mod.main(["--start", str(repo)])
    out = capsys.readouterr().out.strip()
    assert rc == 0
    assert out == str(repo / ".knowledge")


def test_cli_exits_nonzero_when_unresolvable(tmp_path, capsys, monkeypatch):
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))
    mod = _load()
    rc = mod.main(["--start", str(fake_home)])
    err = capsys.readouterr().err
    assert rc != 0
    assert "unresolvable" in err.lower()


def test_default_dirname_is_dot_knowledge(tmp_path, monkeypatch):
    repo = tmp_path / "proj"
    (repo / ".git").mkdir(parents=True)
    monkeypatch.delenv("SCIBRAIN_KB_DIRNAME", raising=False)
    mod = _load()
    assert mod.resolve_kb(start=repo) == repo / ".knowledge"


def test_env_var_overrides_dirname_with_git_root(tmp_path, monkeypatch):
    repo = tmp_path / "proj"
    (repo / ".git").mkdir(parents=True)
    monkeypatch.setenv("SCIBRAIN_KB_DIRNAME", "kb")
    mod = _load()
    assert mod.resolve_kb(start=repo) == repo / "kb"


def test_env_var_overrides_dirname_with_fallback(tmp_path, monkeypatch):
    fake_home = tmp_path / "home"
    (fake_home / "scratch").mkdir(parents=True)
    monkeypatch.setenv("HOME", str(fake_home))
    monkeypatch.setenv("SCIBRAIN_KB_DIRNAME", "papers")
    mod = _load()
    start = fake_home / "scratch"
    assert mod.resolve_kb(start=start) == start / "papers"


def test_empty_env_var_uses_default_dirname(tmp_path, monkeypatch):
    repo = tmp_path / "proj"
    (repo / ".git").mkdir(parents=True)
    monkeypatch.setenv("SCIBRAIN_KB_DIRNAME", "")
    mod = _load()
    assert mod.resolve_kb(start=repo) == repo / ".knowledge"


@pytest.mark.parametrize("dirname", ["/tmp/kb", "../outside", "nested/kb", r"nested\kb", ".", ".."])
def test_rejects_invalid_env_var_dirnames(tmp_path, monkeypatch, dirname):
    repo = tmp_path / "proj"
    (repo / ".git").mkdir(parents=True)
    monkeypatch.setenv("SCIBRAIN_KB_DIRNAME", dirname)
    mod = _load()
    with pytest.raises(ValueError, match="SCIBRAIN_KB_DIRNAME"):
        mod.resolve_kb(start=repo)


def test_cli_exits_nonzero_for_invalid_env_var(tmp_path, capsys, monkeypatch):
    repo = tmp_path / "proj"
    (repo / ".git").mkdir(parents=True)
    monkeypatch.setenv("SCIBRAIN_KB_DIRNAME", "/tmp/kb")
    mod = _load()
    rc = mod.main(["--start", str(repo)])
    err = capsys.readouterr().err
    assert rc != 0
    assert "SCIBRAIN_KB_DIRNAME" in err


def test_advisor_kb_under_plugin_root(monkeypatch):
    monkeypatch.delenv("SCIBRAIN_KB_DIRNAME", raising=False)
    mod = _load()
    plugin_root = HELPER.resolve().parents[3]
    assert mod.resolve_kb(advisor="lei-wang") == plugin_root / "advisors" / "lei-wang" / ".knowledge"


def test_advisor_kb_honors_env_var(monkeypatch):
    monkeypatch.setenv("SCIBRAIN_KB_DIRNAME", "kb")
    mod = _load()
    plugin_root = HELPER.resolve().parents[3]
    assert mod.resolve_kb(advisor="xi-dai") == plugin_root / "advisors" / "xi-dai" / "kb"


def test_advisor_ignores_start(tmp_path, monkeypatch):
    """When --advisor is set, --start has no effect."""
    monkeypatch.delenv("SCIBRAIN_KB_DIRNAME", raising=False)
    repo = tmp_path / "proj"
    (repo / ".git").mkdir(parents=True)
    mod = _load()
    plugin_root = HELPER.resolve().parents[3]
    assert mod.resolve_kb(start=repo, advisor="some-advisor") == \
        plugin_root / "advisors" / "some-advisor" / ".knowledge"


def test_cli_advisor_flag(capsys, monkeypatch):
    monkeypatch.delenv("SCIBRAIN_KB_DIRNAME", raising=False)
    mod = _load()
    rc = mod.main(["--advisor", "lei-wang"])
    out = capsys.readouterr().out.strip()
    plugin_root = HELPER.resolve().parents[3]
    assert rc == 0
    assert out == str(plugin_root / "advisors" / "lei-wang" / ".knowledge")
