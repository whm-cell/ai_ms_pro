#!/usr/bin/env python3

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HOOK_DIR = ROOT / ".codex" / "hooks"
PREFERRED_MIN_VERSION = (3, 11)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print("usage: run_hook.py <hook-script> [args...]", file=sys.stderr)
        return 2

    raw_target = args[0]
    target_args = args[1:]
    target_path = resolve_target_path(raw_target)
    python_cmd = resolve_python_command()

    result = subprocess.run(
        [*python_cmd, str(target_path), *target_args],
        cwd=str(ROOT),
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr,
        check=False,
    )
    return int(result.returncode)


def resolve_target_path(raw_target: str) -> Path:
    candidate = Path(raw_target)
    if not candidate.is_absolute():
        if "/" not in raw_target and "\\" not in raw_target:
            candidate = HOOK_DIR / raw_target
        else:
            candidate = ROOT / raw_target

    candidate = candidate.resolve()
    if not candidate.exists():
        raise SystemExit(f"ERROR: target script not found: {raw_target}")
    return candidate


def resolve_python_command() -> list[str]:
    system = platform.system()
    prefix_candidates: list[list[str]] = []

    for prefix in python_prefixes():
        for candidate in python_candidates_for_prefix(prefix, system):
            add_unique_command(prefix_candidates, [candidate])

    prefix_command = first_runnable_command(prefix_candidates)
    if prefix_command is not None:
        return prefix_command

    env_python = os.environ.get("CODEX_HARNESS_PYTHON", "").strip()
    if env_python and python_can_run([env_python]):
        return [env_python]

    path_candidates: list[list[str]] = []
    if system == "Windows":
        for name in ("python3", "python"):
            for python_path in all_commands_on_path(name, system=system):
                add_unique_command(path_candidates, [python_path])
        py_path = shutil.which("py")
        if py_path:
            add_unique_command(path_candidates, [py_path, "-3"])
        for python_path in common_windows_python_candidates(system):
            add_unique_command(path_candidates, [str(python_path)])
    else:
        for name in ("python3", "python"):
            for python_path in all_commands_on_path(name, system=system):
                add_unique_command(path_candidates, [python_path])

    path_command = best_runnable_python(path_candidates)
    if path_command is not None:
        return path_command

    current_command = [sys.executable] if sys.executable else []
    if current_command and python_can_run(current_command):
        return current_command

    raise SystemExit("ERROR: could not determine a runnable Python executable for harness scripts")


def add_unique_command(candidates: list[list[str]], command: list[str]) -> None:
    if command and command not in candidates:
        candidates.append(command)


def first_runnable_command(candidates: list[list[str]]) -> list[str] | None:
    for command in candidates:
        if python_can_run(command):
            return command
    return None


def best_runnable_python(candidates: list[list[str]]) -> list[str] | None:
    runnable: list[tuple[int, tuple[int, int, int], list[str]]] = []
    for index, command in enumerate(candidates):
        version = python_version(command)
        if version is not None:
            runnable.append((index, version, command))

    if not runnable:
        return None

    preferred = [
        item for item in runnable if item[1] >= (*PREFERRED_MIN_VERSION, 0)
    ]
    pool = preferred or runnable
    _, _, command = max(pool, key=lambda item: (item[1], -item[0]))
    return command


def all_commands_on_path(name: str, system: str | None = None) -> list[str]:
    results: list[str] = []
    seen: set[str] = set()
    candidate_names = path_candidate_names(name, system or platform.system())
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        if not directory:
            continue
        for candidate_name in candidate_names:
            candidate = Path(directory) / candidate_name
            resolved = str(candidate)
            if resolved in seen:
                continue
            if candidate.is_file() and is_executable_command(candidate, system or platform.system()):
                results.append(resolved)
                seen.add(resolved)
    return results


def path_candidate_names(name: str, system: str) -> list[str]:
    if system != "Windows" or command_name_has_suffix(name):
        return [name]

    extensions = [".exe", ".cmd", ".bat", ".com"]
    raw_pathext = os.environ.get("PATHEXT", "")
    for extension in raw_pathext.replace(";", os.pathsep).split(os.pathsep):
        normalized = extension.strip().lower()
        if normalized and normalized not in extensions:
            extensions.append(normalized)

    return [name, *[f"{name}{extension}" for extension in extensions]]


def command_name_has_suffix(name: str) -> bool:
    basename = name.replace("\\", "/").rsplit("/", 1)[-1]
    return "." in basename


def is_executable_command(candidate: Path, system: str) -> bool:
    if system == "Windows":
        return candidate.is_file()
    return candidate.is_file() and os.access(candidate, os.X_OK)


def common_windows_python_candidates(system: str) -> list[Path]:
    if system != "Windows":
        return []

    roots: list[Path] = []
    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        roots.append(Path(local_appdata) / "Programs" / "Python")

    candidates: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for prefix in sorted(root.glob("Python*"), reverse=True):
            candidate = prefix / "python.exe"
            if candidate.exists():
                candidates.append(candidate)
    return candidates


def python_prefixes() -> list[Path]:
    prefixes: list[Path] = [ROOT / ".codex" / ".venv"]
    for env_var in ("VIRTUAL_ENV", "CONDA_PREFIX"):
        value = os.environ.get(env_var, "").strip()
        if value:
            prefixes.append(Path(value))
    return prefixes


def python_candidates_for_prefix(prefix: Path, system: str) -> list[str]:
    if not prefix.exists():
        return []

    if system == "Windows":
        names = [
            "Scripts/python.exe",
            "Scripts/python",
            "python.exe",
            "python",
        ]
    else:
        names = [
            "bin/python",
            "bin/python3",
            "python",
        ]

    results: list[str] = []
    for name in names:
        candidate = prefix / name
        if candidate.is_file():
            results.append(str(candidate))
    return results


def python_can_run(command: list[str]) -> bool:
    return python_version(command) is not None


def python_version(command: list[str]) -> tuple[int, int, int] | None:
    try:
        result = subprocess.run(
            [
                *command,
                "-c",
                "import sys; print('%d.%d.%d' % sys.version_info[:3])",
            ],
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    parts = result.stdout.strip().split(".")
    if len(parts) != 3:
        return None
    try:
        return tuple(int(part) for part in parts)  # type: ignore[return-value]
    except ValueError:
        return None


if __name__ == "__main__":
    raise SystemExit(main())
