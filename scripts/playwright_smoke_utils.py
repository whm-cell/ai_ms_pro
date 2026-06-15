from __future__ import annotations

import os
import shutil


def npx_candidate_names(os_name: str | None = None) -> tuple[str, ...]:
    if (os_name or os.name) == "nt":
        return ("npx.cmd", "npx.exe", "npx.bat", "npx")
    return ("npx",)


def resolve_npx_command(os_name: str | None = None) -> str:
    for name in npx_candidate_names(os_name):
        path = shutil.which(name)
        if path:
            return path
    raise RuntimeError("npx is required to run this smoke test.")
