"""Offline end-to-end test of the autoresearch tidy-up helper on a fixture repo."""

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

HELPER = (Path(__file__).resolve().parents[1] / "skills" / "autoresearch"
          / "helpers" / "tidy_attempts.py")
spec = importlib.util.spec_from_file_location("tidy_attempts", HELPER)
tidy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tidy)


def git(cwd, *args):
    return subprocess.run(["git", "-C", str(cwd), *args], check=True,
                          capture_output=True, text=True).stdout


def add_attempt(project, n, log=True, report=None, code=True, commit=True):
    wt = project / ".worktrees" / f"attempt-{n:03d}"
    git(project, "worktree", "add", "-q", "-b", f"attempt-{n:03d}", str(wt), "main")
    if log:
        (wt / "LOG.md").write_text(
            f"# Attempt {n:03d}\n\n- **kind** — draft\n- **parent** — none\n"
            f"- **hypothesis** — idea number {n}\n")
    if report is not None:
        (wt / "report.json").write_text(json.dumps(report))
    if code:
        (wt / "solver.py").write_text(f"print({n})\n")
    if commit and (log or report or code):
        git(wt, "add", "-A")
        git(wt, "commit", "-q", "-m", f"attempt {n}")
    return wt


@pytest.fixture
def project(tmp_path):
    p = tmp_path / "proj"
    p.mkdir()
    git(p, "init", "-q", "-b", "main")
    git(p, "config", "user.email", "t@example.com")
    git(p, "config", "user.name", "t")
    (p / "research").mkdir()
    (p / "research" / "STATE.md").write_text(
        "# Autoresearch State\n\n- stage: run\n- topic: demo\n"
        "- authorized_attempts: 0\n- next_attempt: 5\n")
    (p / "research" / "GOAL.md").write_text("bar: 0.9\n")
    git(p, "add", "-A")
    git(p, "commit", "-q", "-m", "init")
    # 001: scored, committed, plus a build artifact and an uncommitted edit -> keep
    wt1 = add_attempt(p, 1, report={"status": "scored", "score": 0.42})
    (wt1 / "__pycache__").mkdir()
    (wt1 / "__pycache__" / "solver.cpython-311.pyc").write_bytes(b"\0" * 10)
    (wt1 / "solver.py").write_text("print('edited')\n")
    # 002: validator error (timeout-like), fully committed -> keep
    add_attempt(p, 2, report={"status": "error", "score": None,
                              "errors": [{"code": "timeout"}]})
    # 003: code but no LOG.md -> ask
    add_attempt(p, 3, log=False, commit=False)
    # 004: nothing at all -> drop automatically
    add_attempt(p, 4, log=False, code=False)
    return p


def test_inventory_classifies_every_worktree(project):
    inv = tidy.inventory(project)
    by_id = {a["id"]: a for a in inv["attempts"]}
    assert set(by_id) == {1, 2, 3, 4}
    assert by_id[1]["decision"] == "keep"
    assert by_id[1]["status"] == "scored" and by_id[1]["score"] == 0.42
    assert by_id[1]["dirty"] and by_id[1]["artifacts"] == ["__pycache__/"]
    assert by_id[1]["hypothesis"] == "idea number 1"
    assert by_id[2]["decision"] == "keep" and by_id[2]["status"] == "error"
    assert by_id[3]["decision"] == "ask" and "no LOG.md" in by_id[3]["reason"]
    assert by_id[4]["decision"] == "drop"
    assert inv["remote"] is None
    assert all(a["pushed"] is False for a in inv["attempts"])


def test_apply_keeps_drops_and_leaves_ask_rows_alone(project, tmp_path):
    snapshot = tmp_path / "inv.json"
    snapshot.write_text(json.dumps(tidy.inventory(project)))
    result = tidy.apply(project, json.loads(snapshot.read_text()), drop=set())
    assert result["kept"] == [1, 2] and result["dropped"] == [4]
    assert result["skipped"] == [3]
    # kept: edit committed, artifact ignored, worktree removed, branch intact
    assert not (project / ".worktrees" / "attempt-001").exists()
    files = git(project, "ls-tree", "-r", "--name-only", "attempt-001").split()
    assert "solver.py" in files and ".gitignore" in files
    assert not any(f.startswith("__pycache__") for f in files)
    assert "edited" in git(project, "show", "attempt-001:solver.py")
    assert "__pycache__/" in git(project, "show", "attempt-001:.gitignore")
    # dropped: worktree and branch gone
    assert not (project / ".worktrees" / "attempt-004").exists()
    assert "attempt-004" not in git(project, "branch", "--list", "attempt-*")
    # ask row untouched
    assert (project / ".worktrees" / "attempt-003" / "solver.py").exists()


def test_apply_pushes_when_a_remote_exists(project, tmp_path):
    bare = tmp_path / "remote.git"
    git(tmp_path, "init", "-q", "--bare", str(bare))
    git(project, "remote", "add", "origin", str(bare))
    inv = tidy.inventory(project)
    assert inv["remote"] == "origin"
    tidy.apply(project, inv, drop={3})
    assert "attempt-001" in git(bare, "branch", "--list")
    assert "attempt-003" not in git(project, "branch", "--list", "attempt-*")
    record = tidy.record(project, inv)
    assert "attempt-001" in record and "pushed" in record
    assert "local only" not in record


def test_second_apply_pass_handles_ask_rows_and_is_idempotent(project):
    inv = tidy.inventory(project)
    first = tidy.apply(project, inv)
    assert first["skipped"] == [3]
    second = tidy.apply(project, inv, keep={3})
    assert second["kept"] == [1, 2, 3] and second["dropped"] == [4]
    assert "attempt-003" in git(project, "branch", "--list", "attempt-*")
    assert "solver.py" in git(project, "ls-tree", "-r", "--name-only", "attempt-003")
    assert not (project / ".worktrees" / "attempt-003").exists()
    third = tidy.apply(project, inv, keep={3})
    assert third["kept"] == [1, 2, 3] and third["warnings"] == []


def test_record_marks_dropped_rows_and_warns_without_remote(project, tmp_path):
    inv = tidy.inventory(project)
    tidy.apply(project, inv, drop={3})
    out = project / "research" / "ATTEMPTS.md"
    text = tidy.record(project, inv, out=out)
    assert out.read_text() == text
    rows = [l for l in text.splitlines() if l.startswith("| 00")]
    assert len(rows) == 4
    assert "| 001 |" in text and "scored" in text and "0.42" in text
    assert "| 003 |" in text and "dropped" in text
    assert "| 004 |" in text
    assert "local only" in text and "not a backup" in text
    assert "stage: run" in text and "next_attempt: 5" in text


def test_cli_inventory_prints_summary_and_ask_rows_only(project, capsys):
    rc = tidy.main(["inventory", "--project", str(project)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "keep: 2" in out and "drop: 1" in out and "ask: 1" in out
    assert "attempt-003" in out and "attempt-001" not in out
