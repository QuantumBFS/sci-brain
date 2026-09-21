"""Execute the documented Typst build check against realistic outcomes."""

import os
import re
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "compiler_exit,diagnostic,expected_exit",
    [
        (0, "", 0),
        (0, "warning: unresolved citation", 1),
        (2, "error: unknown variable", 1),
        (127, "compiler unavailable", 1),
    ],
)
def test_documented_compile_check_handles_failure_and_warnings(
    tmp_path, compiler_exit, diagnostic, expected_exit
):
    workflow = (
        ROOT / "skills/how-to-write-ideas-report/references/writing-workflow.md"
    ).read_text()
    blocks = re.findall(r"```sh\n(.*?)\n\s*```", workflow, re.DOTALL)
    checks = [block for block in blocks if "typst compile" in block]
    assert len(checks) == 1

    compiler = tmp_path / "typst"
    compiler.write_text(
        '#!/bin/sh\nprintf "%s\\n" "$TEST_DIAGNOSTIC" >&2\n'
        'exit "$TEST_COMPILER_EXIT"\n'
    )
    compiler.chmod(0o755)
    logs = tmp_path / "logs"
    logs.mkdir()
    env = {
        **os.environ,
        "PATH": str(tmp_path) + os.pathsep + os.environ["PATH"],
        "TMPDIR": str(logs),
        "TEST_DIAGNOSTIC": diagnostic,
        "TEST_COMPILER_EXIT": str(compiler_exit),
    }
    result = subprocess.run(
        ["/bin/sh", "-c", checks[0]],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == expected_exit, result
    assert diagnostic in result.stdout + result.stderr
    assert not list(logs.iterdir()), "temporary compiler log was not removed"
