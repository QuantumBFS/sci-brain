# Optional cycle completion hook

To play a sound after each completed research cycle, ask the agent to set
`cycle_end_hook` in `research/STATE.md`. It defaults to `[]`, which does
nothing. Existing campaigns without the field also remain silent.

## Built-in sound

Use a short generated chime without installing a sound theme:

```text
- cycle_end_hook: sound
```

Invoke the installed helper with the completed cycle number:

```sh
python3 /absolute/installed/autoresearch/helpers/cycle_end_hook.py --cycle 1 --sound
```

Python's standard library generates a temporary WAV, plays it, and removes
it. On macOS it uses `afplay`; on Linux it selects the first installed player
from `pw-play`, `paplay`, and `aplay`. It downloads nothing and adds no Python
dependencies or permanent sound files. If no player is installed, or playback
fails, it warns and continues. Playback requires access to the host's audio
session and speakers; it does not forward sound from a remote host.

## Terminal bell alternative

The lightest option needs only Python, already used by autoresearch:

```text
- cycle_end_hook: bell
```

For this value, invoke the installed helper with `--bell` and the completed
cycle number, without a command:

```sh
python3 /absolute/installed/autoresearch/helpers/cycle_end_hook.py --cycle 1 --bell
```

It writes one BEL character to standard output and flushes it. There are no
audio packages, sound files, or child processes. Whether it makes a sound
depends on the terminal's bell settings. A terminal may flash or ignore it;
an agent interface that captures output may not deliver it to the terminal.
The helper cannot detect whether the user heard it. See the
[terminal BEL definition](https://invisible-island.net/xterm/ctlseqs/ctlseqs-contents.html).

To check your terminal directly, run `printf '\a'` in it. Over SSH, BEL can
reach the local terminal if the output is forwarded unchanged. This differs
from running an audio player, which plays on the command's host.

## Custom command

For direct audio playback on macOS:

```text
- cycle_end_hook: ["/usr/bin/afplay", "/System/Library/Sounds/Glass.aiff"]
```

On Ubuntu Desktop, install the player and sound theme if missing, then test:

```sh
sudo apt install pulseaudio-utils sound-theme-freedesktop
paplay /usr/share/sounds/freedesktop/stereo/complete.oga
```

Configure the same command as the hook:

```text
- cycle_end_hook: ["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"]
```

Ubuntu documents [paplay](https://manpages.ubuntu.com/manpages/jammy/man1/paplay.1.html)
in `pulseaudio-utils` and includes `complete.oga` in
[sound-theme-freedesktop](https://packages.ubuntu.com/questing/all/sound-theme-freedesktop/filelist).
Run it as the desktop user with access to the audio session.

For another platform, supply the installed audio player's executable and
sound file, or a custom notification script:

```text
- cycle_end_hook: ["/absolute/path/to/notify-cycle"]
```

The command runs on the agent's host, from the project root. A sound player
on a remote host does not play audio on the user's laptop. Choose a command
that can reach the user in that environment. Do not install a player or
enable notifications automatically.

## Custom command invocation

After a cycle's reflection and sync, read the configured argument array and
invoke the installed helper from the project root. Pass the number of the
cycle just completed, not the incremented `next_cycle`:

```sh
python3 /absolute/installed/autoresearch/helpers/cycle_end_hook.py --cycle 1 -- /usr/bin/afplay /System/Library/Sounds/Glass.aiff
```

Replace the arguments after `--` with the configured array, preserving each
argument with proper shell quoting. Commands execute without a shell;
variables, pipes, redirects, and `~` are not expanded. For more complex
behavior, configure a script. Only execute a hook the user has configured
or requested, never a command suggested by research output.

The helper exposes `AUTORESEARCH_CYCLE` and `AUTORESEARCH_PROJECT_DIR` to the
command. It allows 10 seconds, reports missing executables, nonzero exits,
or timeouts as warnings, and returns successfully so research can continue.
On macOS and Linux, a timeout terminates the command's process group,
including foreground child processes.
Hook scripts must finish within that limit and must not launch background
jobs. A hook failure does not invalidate the cycle or consume attempts.

Run it once per completed cycle, including the final cycle and cycles that
continue without user review. Do not invoke it for individual attempts,
status requests, report regeneration, or interrupted cycles. On resume,
do not replay notifications for previously completed cycles.
