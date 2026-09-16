#!/usr/bin/env python3
"""Run an optional cycle completion command, with non-fatal failures."""

import argparse
import math
import os
from pathlib import Path
import shutil
import signal
import struct
import subprocess
import sys
import tempfile
import wave


def write_tone(path):
    """Generate a quiet, short two-note chime as mono 16-bit PCM."""
    rate = 22050
    frames = bytearray()
    for frequency in (660, 880):
        count = int(rate * 0.18)
        ramp = int(rate * 0.01)
        for index in range(count):
            envelope = min(1, index / ramp, (count - 1 - index) / ramp)
            sample = int(6000 * envelope * math.sin(2 * math.pi * frequency * index / rate))
            frames.extend(struct.pack("<h", sample))
        frames.extend(b"\x00\x00" * int(rate * 0.06))
    with wave.open(str(path), "wb") as sound:
        sound.setnchannels(1)
        sound.setsampwidth(2)
        sound.setframerate(rate)
        sound.writeframes(frames)


def play_tone(cycle):
    """Use an installed system player; never download or install anything."""
    names = ("afplay",) if sys.platform == "darwin" else ("pw-play", "paplay", "aplay")
    player = next((path for name in names if (path := shutil.which(name))), None)
    if player is None:
        print("Warning: no audio player found; configure cycle_end_hook with an available notifier.",
              file=sys.stderr)
        return
    try:
        with tempfile.TemporaryDirectory(prefix="autoresearch-tone-") as directory:
            path = Path(directory) / "complete.wav"
            write_tone(path)
            run_hook([player, str(path)], cycle)
    except OSError as exc:
        print(f"Warning: cycle-end tone could not be created: {exc}", file=sys.stderr)


def run_hook(command, cycle, *, timeout=10):
    """Run argv from the project cwd; an empty command disables the hook."""
    if not command:
        return
    env = os.environ.copy()
    env.update(
        AUTORESEARCH_CYCLE=str(cycle),
        AUTORESEARCH_PROJECT_DIR=str(Path.cwd()),
    )
    try:
        with subprocess.Popen(
            command, env=env, stdin=subprocess.DEVNULL,
            start_new_session=(os.name == "posix"),
        ) as process:
            try:
                returncode = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                if os.name == "posix":
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                else:
                    process.kill()
                process.wait()
                raise
            if returncode:
                raise subprocess.CalledProcessError(returncode, command)
    except subprocess.TimeoutExpired:
        print(f"Warning: cycle-end hook timed out after {timeout}s.", file=sys.stderr)
    except subprocess.CalledProcessError as exc:
        print(f"Warning: cycle-end hook exited with code {exc.returncode}.", file=sys.stderr)
    except OSError as exc:
        print(f"Warning: cycle-end hook could not run: {exc}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cycle", type=int, required=True)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--bell", action="store_true",
                      help="emit a terminal bell without an external player")
    mode.add_argument("--sound", action="store_true",
                      help="generate a short chime and use an installed audio player")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.cycle < 1:
        parser.error("--cycle must be positive")
    command = args.command
    if command[:1] == ["--"]:
        command = command[1:]
    if args.sound:
        if command:
            parser.error("--sound cannot be combined with a command")
        play_tone(args.cycle)
        return
    if args.bell:
        if command:
            parser.error("--bell cannot be combined with a command")
        try:
            print("\a", end="", flush=True)
        except OSError as exc:
            print(f"Warning: terminal bell could not be written: {exc}", file=sys.stderr)
        return
    run_hook(command, args.cycle)


if __name__ == "__main__":
    main()
