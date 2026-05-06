from __future__ import annotations

import subprocess
from pathlib import Path


def run(cmd: list[str], root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(root), capture_output=True, text=True, check=False)


def text_or_stderr(result: subprocess.CompletedProcess[str]) -> str:
    return (result.stderr or result.stdout).strip().replace("\n", " ")
