"""Exercise cycle notifications without playing audio."""

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import wave

import pytest


HELPER = (Path(__file__).resolve().parents[1] / "skills" / "autoresearch"
          / "helpers" / "cycle_end_hook.py")
spec = importlib.util.spec_from_file_location("cycle_end_hook", HELPER)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)


def test_disabled_hook_does_not_spawn(monkeypatch):
    def unexpected(*args, **kwargs):
        pytest.fail("disabled hook spawned a process")
    monkeypatch.setattr(hook.subprocess, "Popen", unexpected)
    hook.run_hook([], 1)


def test_builtin_bell_emits_one_character_without_spawning(monkeypatch, capsys):
    def unexpected(*args, **kwargs):
        pytest.fail("built-in bell spawned a process")
    monkeypatch.setattr(hook.subprocess, "Popen", unexpected)
    monkeypatch.setattr(sys, "argv", [str(HELPER), "--cycle", "1", "--bell"])
    hook.main()
    captured = capsys.readouterr()
    assert captured.out == "\a"
    assert captured.err == ""


@pytest.mark.parametrize("platform, available", [
    ("darwin", "afplay"), ("linux", "pw-play"),
    ("linux", "paplay"), ("linux", "aplay"),
])
def test_sound_generates_valid_audio_and_cleans_up(monkeypatch, platform, available):
    monkeypatch.setattr(hook.sys, "platform", platform)
    monkeypatch.setattr(hook.shutil, "which",
                        lambda name: f"/usr/bin/{name}" if name == available else None)
    played = []

    def playback(command, cycle):
        assert command[0] == f"/usr/bin/{available}"
        assert cycle == 4
        path = Path(command[1])
        played.append(path)
        with wave.open(str(path), "rb") as sound:
            assert sound.getnchannels() == 1
            assert sound.getsampwidth() == 2
            assert sound.getframerate() == 22050
            assert 0.4 < sound.getnframes() / sound.getframerate() < 0.6
            assert any(sound.readframes(sound.getnframes()))

    monkeypatch.setattr(hook, "run_hook", playback)
    monkeypatch.setattr(sys, "argv", [str(HELPER), "--cycle", "4", "--sound"])
    hook.main()
    assert len(played) == 1
    assert not played[0].parent.exists()


def test_sound_warns_when_no_player_is_installed(monkeypatch, capsys):
    monkeypatch.setattr(hook.shutil, "which", lambda name: None)
    hook.play_tone(1)
    assert "no audio player found" in capsys.readouterr().err


def test_sound_cleans_up_after_playback_failure(monkeypatch, capsys):
    monkeypatch.setattr(hook.shutil, "which", lambda name: "/fake/player")
    played = []

    def fail(command, **kwargs):
        played.append(Path(command[1]))
        raise OSError("audio player unavailable")

    monkeypatch.setattr(hook.subprocess, "Popen", fail)
    hook.play_tone(1)
    assert "audio player unavailable" in capsys.readouterr().err
    assert len(played) == 1
    assert not played[0].parent.exists()


def test_bell_rejects_custom_command_without_running_it(tmp_path):
    output = tmp_path / "should-not-exist"
    result = subprocess.run(
        [sys.executable, str(HELPER), "--cycle", "1", "--bell", "--",
         sys.executable, "-c",
         "import pathlib, sys; pathlib.Path(sys.argv[1]).touch()", str(output)],
        capture_output=True, text=True, timeout=5,
    )
    assert result.returncode != 0
    assert "cannot be combined" in result.stderr
    assert result.stdout == ""
    assert not output.exists()


def test_cli_preserves_arguments_and_passes_cycle_context(tmp_path):
    output = tmp_path / "notification.json"
    literal = "spaces and $(touch unwanted); $HOME"
    script = (
        "import json, os, pathlib, sys; "
        "pathlib.Path(sys.argv[1]).write_text(json.dumps(["
        "os.getcwd(), os.environ['AUTORESEARCH_CYCLE'], "
        "os.environ['AUTORESEARCH_PROJECT_DIR'], sys.argv[2]]))"
    )
    result = subprocess.run(
        [sys.executable, str(HELPER), "--cycle", "7", "--",
         sys.executable, "-c", script, str(output), literal],
        cwd=tmp_path, capture_output=True, text=True, timeout=5,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(output.read_text()) == [str(tmp_path.resolve()), "7",
                                             str(tmp_path.resolve()), literal]
    assert not (tmp_path / "unwanted").exists()


@pytest.mark.parametrize("command, warning", [
    ([sys.executable, "-c", "raise SystemExit(3)"], "exited with code 3"),
    (["/nonexistent/autoresearch-notifier"], "could not run"),
])
def test_cli_hook_failures_are_nonfatal(command, warning):
    result = subprocess.run(
        [sys.executable, str(HELPER), "--cycle", "1", "--", *command],
        capture_output=True, text=True, timeout=5,
    )
    assert result.returncode == 0
    assert warning in result.stderr


def test_timeout_stops_command_without_failing_cycle(tmp_path, capsys):
    output = tmp_path / "should-not-exist"
    hook.run_hook(
        [sys.executable, "-c",
         "import pathlib, sys, time; time.sleep(2); pathlib.Path(sys.argv[1]).touch()",
         str(output)],
        1, timeout=0.05,
    )
    assert "timed out" in capsys.readouterr().err
    assert not output.exists()


@pytest.mark.skipif(os.name != "posix", reason="POSIX process-group cleanup")
def test_timeout_stops_foreground_descendant_and_releases_output_pipe(tmp_path):
    marker = tmp_path / "escaped"
    child = (
        "import pathlib, sys, time; print('child started', flush=True); "
        "time.sleep(5); pathlib.Path(sys.argv[1]).touch(); print('escaped')"
    )
    parent = "import subprocess, sys; subprocess.run([sys.executable, '-c', sys.argv[1], sys.argv[2]])"
    runner = (
        "import importlib.util, sys; "
        "spec = importlib.util.spec_from_file_location('hook', sys.argv[1]); "
        "hook = importlib.util.module_from_spec(spec); spec.loader.exec_module(hook); "
        "hook.run_hook([sys.executable, '-c', sys.argv[2], sys.argv[3], sys.argv[4]], 1, timeout=0.5)"
    )
    result = subprocess.run(
        [sys.executable, "-c", runner, str(HELPER), parent, child, str(marker)],
        capture_output=True, text=True, timeout=3,
    )
    assert result.returncode == 0
    assert result.stdout == "child started\n"
    assert "timed out" in result.stderr
    assert not marker.exists()
