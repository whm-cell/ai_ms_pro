#!/usr/bin/env python3

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
from pathlib import Path


PARENT_ENV_PYTHON_KEYS = (
    "CODEX_HARNESS_PYTHON",
    "PYTHON",
    "PYTHON3",
    "PYTHON_BIN",
    "PYTHON_EXECUTABLE",
)
PARENT_ENV_PYTHON_VERSION_KEYS = (
    "CODEX_HARNESS_PYTHON_VERSION",
    "PYTHON_VERSION",
    "PYENV_VERSION",
)


def parent_env_python_commands(root: Path) -> list[list[str]]:
    values = load_parent_env_values(root)
    commands: list[list[str]] = []
    for key in PARENT_ENV_PYTHON_KEYS:
        command = python_command_from_env_value(
            values.get(key, "").strip(),
            base_dir=parent_env_path(root).parent,
        )
        if command is not None and command not in commands:
            commands.append(command)
    return commands


def pyenv_python_commands(root: Path) -> list[list[str]]:
    commands: list[list[str]] = []
    versions = [*parent_env_python_versions(root), *python_version_file_values(root), None]
    for version in versions:
        command = pyenv_python_command(root, version)
        if command is not None and command not in commands:
            commands.append(command)
    return commands


def parent_env_path(root: Path) -> Path:
    return root.parent / ".env"


def load_parent_env_values(root: Path) -> dict[str, str]:
    path = parent_env_path(root)
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return values

    for line in lines:
        parsed = parse_env_assignment(line)
        if parsed is not None:
            key, value = parsed
            values[key] = value
    return values


def parse_env_assignment(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    if stripped.startswith("export "):
        stripped = stripped[len("export ") :].strip()
    if "=" not in stripped:
        return None
    key, raw_value = stripped.split("=", 1)
    key = key.strip()
    if not key.replace("_", "A").isalnum() or not key[0].isalpha():
        return None
    return key, strip_env_value(raw_value.strip())


def strip_env_value(raw_value: str) -> str:
    if len(raw_value) >= 2 and raw_value[0] == raw_value[-1] and raw_value[0] in {"'", '"'}:
        return raw_value[1:-1]
    return raw_value


def python_command_from_env_value(value: str, *, base_dir: Path) -> list[str] | None:
    if not value:
        return None
    try:
        parts = shlex.split(value)
    except ValueError:
        return None
    if not parts:
        return None
    if len(parts) > 1:
        return parts

    command_path = Path(parts[0]).expanduser()
    if not command_path.is_absolute() and any(separator in parts[0] for separator in ("/", "\\")):
        command_path = (base_dir / command_path).resolve()
    return [str(command_path)]


def parent_env_python_versions(root: Path) -> list[str]:
    values = load_parent_env_values(root)
    versions: list[str] = []
    for key in PARENT_ENV_PYTHON_VERSION_KEYS:
        value = values.get(key, "").strip()
        if value and value not in versions:
            versions.append(value)
    return versions


def python_version_file_values(root: Path) -> list[str]:
    versions: list[str] = []
    for path in (root / ".python-version", root.parent / ".python-version"):
        try:
            value = path.read_text(encoding="utf-8").splitlines()[0].strip()
        except (OSError, IndexError):
            continue
        if value and value not in versions:
            versions.append(value)
    return versions


def pyenv_python_command(root: Path, version: str | None) -> list[str] | None:
    pyenv = shutil.which("pyenv")
    if not pyenv:
        return None
    env = os.environ.copy()
    if version:
        env["PYENV_VERSION"] = version
    try:
        result = subprocess.run(
            [pyenv, "which", "python"],
            cwd=str(root),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    python_path = result.stdout.strip()
    return [python_path] if python_path else None
