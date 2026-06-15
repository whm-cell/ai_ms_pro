#!/usr/bin/env python3

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from bootstrap_ai_docs import render_ai_index, render_working_context
from bootstrap_cli import parse_args
from bootstrap_plan_renderer import render_plan as render_bootstrap_plan
from bootstrap_requirements_docs import render_requirements_index, render_traceability_matrix
from bootstrap_scaffold_config import render_harness_config, render_requirements_txt
from bootstrap_scaffold_files import (
    ensure_directories,
    print_write_result,
    scaffold_files,
    write_bootstrap_prerequisites,
    write_hooks_config,
    write_scaffold_files,
)
from hook_config_lib import render_hooks_config as render_platform_hooks_config


__all__ = [
    "render_ai_index",
    "render_harness_config",
    "render_hooks_config",
    "render_plan",
    "render_requirements_index",
    "render_requirements_txt",
    "render_traceability_matrix",
    "render_working_context",
]


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VENV_DIR = ROOT / ".codex" / ".venv"
DEFAULT_REQUIREMENTS_PATH = ROOT / ".codex" / "requirements.txt"


def is_windows_host() -> bool:
    return os.name == "nt"


def python_candidates(prefix: Path) -> list[Path]:
    candidates: list[Path] = []
    if is_windows_host():
        candidates.extend(
            [
                prefix / "Scripts" / "python.exe",
                prefix / "Scripts" / "python",
            ]
        )
    candidates.extend(
        [
            prefix / "bin" / "python",
            prefix / "bin" / "python3",
            prefix / "python.exe",
            prefix / "python",
        ]
    )
    return candidates


def resolve_existing_python(prefix: Path) -> Path | None:
    for candidate in python_candidates(prefix):
        if candidate.exists():
            return candidate
    return None


def common_windows_python_candidates() -> list[Path]:
    if not is_windows_host():
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


def is_runnable_python(command: list[str]) -> bool:
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


def all_commands_on_path(name: str) -> list[str]:
    candidates: list[str] = []
    seen: set[str] = set()
    candidate_names = path_candidate_names(name)
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        if not directory:
            continue
        for candidate_name in candidate_names:
            candidate = Path(directory) / candidate_name
            rendered = str(candidate)
            if rendered in seen:
                continue
            if candidate.is_file() and is_executable_command(candidate):
                candidates.append(rendered)
                seen.add(rendered)
    return candidates


def path_candidate_names(name: str) -> list[str]:
    if not is_windows_host() or command_name_has_suffix(name):
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


def is_executable_command(candidate: Path) -> bool:
    if is_windows_host():
        return candidate.is_file()
    return candidate.is_file() and os.access(candidate, os.X_OK)


def best_python_command(commands: list[list[str]]) -> list[str] | None:
    runnable: list[tuple[int, tuple[int, int, int], list[str]]] = []
    for index, command in enumerate(commands):
        version = python_version(command)
        if version is not None:
            runnable.append((index, version, command))
    if not runnable:
        return None
    preferred = [item for item in runnable if item[1] >= (3, 11, 0)]
    pool = preferred or runnable
    _, _, command = max(pool, key=lambda item: (item[1], -item[0]))
    return command


def expected_repo_venv_python() -> Path:
    return python_candidates(DEFAULT_VENV_DIR)[0]


def main() -> int:
    args = parse_args()
    ensure_directories(ROOT)

    files = scaffold_files(
        root=ROOT,
        project_name=args.project_name,
        stage_label=args.stage_label,
        hooks_config=render_hooks_config(),
    )
    write_bootstrap_prerequisites(files=files, root=ROOT, force=args.force)

    if not args.skip_venv:
        bootstrap_python_environment(
            explicit_python=args.python,
            strict_dependency_install=args.strict_python_deps,
        )

    write_hooks_config(files=files, root=ROOT)
    written, skipped = write_scaffold_files(files=files, force=args.force)
    print_write_result(written=written, skipped=skipped, root=ROOT)

    return 0


def render_hooks_config() -> str:
    return render_platform_hooks_config(root=ROOT)


def render_plan(project_name: str, stage_label: str) -> str:
    return render_bootstrap_plan(project_name, stage_label)


def bootstrap_python_environment(
    *,
    explicit_python: str | None,
    strict_dependency_install: bool,
) -> None:
    python_cmd = resolve_bootstrap_python(explicit_python)
    refresh_existing_venv = resolve_runnable_repo_python_command() is None

    if not DEFAULT_VENV_DIR.exists() or refresh_existing_venv:
        create_args = [*python_cmd, "-m", "venv"]
        if DEFAULT_VENV_DIR.exists():
            create_args.append("--clear")
        subprocess.run(
            [*create_args, str(DEFAULT_VENV_DIR)],
            cwd=str(ROOT),
            check=True,
        )

    repo_python_cmd = resolve_runnable_repo_python_command()
    venv_python = resolve_existing_python(DEFAULT_VENV_DIR) or expected_repo_venv_python()
    if not venv_python.exists() or repo_python_cmd is None:
        raise SystemExit(f"ERROR: expected venv python at {venv_python}")

    if DEFAULT_REQUIREMENTS_PATH.exists():
        install_optional_requirements(
            venv_python=venv_python,
            strict_dependency_install=strict_dependency_install,
        )

    print(f"Python environment ready: {venv_python}")


def install_optional_requirements(
    *,
    venv_python: Path,
    strict_dependency_install: bool,
) -> None:
    try:
        subprocess.run(
            [str(venv_python), "-m", "pip", "install", "-r", str(DEFAULT_REQUIREMENTS_PATH)],
            cwd=str(ROOT),
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        message = (
            "WARN: Python dependency install failed; continuing because bootstrap only "
            "requires a repo-local venv to finish initialization. "
            f"Re-run `{venv_python} -m pip install -r {DEFAULT_REQUIREMENTS_PATH}` later if needed."
        )
        if strict_dependency_install:
            raise SystemExit(
                f"ERROR: {message[6:]}"
            ) from exc
        print(message)


def resolve_bootstrap_python(explicit_python: str | None) -> list[str]:
    if explicit_python:
        command = [explicit_python]
        if is_runnable_python(command):
            return command
        raise SystemExit(f"ERROR: explicit Python is not runnable: {explicit_python}")

    prefix_commands: list[list[str]] = []
    if os.environ.get("VIRTUAL_ENV"):
        env_python = resolve_existing_python(Path(os.environ["VIRTUAL_ENV"]))
        if env_python is not None:
            prefix_commands.append([str(env_python)])

    if os.environ.get("CONDA_PREFIX"):
        env_python = resolve_existing_python(Path(os.environ["CONDA_PREFIX"]))
        if env_python is not None:
            prefix_commands.append([str(env_python)])

    for command in prefix_commands:
        if is_runnable_python(command):
            return command

    env_python = os.environ.get("CODEX_HARNESS_PYTHON", "").strip()
    if env_python:
        command = [env_python]
        if is_runnable_python(command):
            return command

    path_commands: list[list[str]] = []
    for name in ("python3", "python"):
        for python_path in all_commands_on_path(name):
            command = [python_path]
            if command not in path_commands:
                path_commands.append(command)

    path_command = best_python_command(path_commands)
    if path_command is not None:
        return path_command

    if is_windows_host():
        py_launcher = shutil.which("py")
        if py_launcher:
            command = [py_launcher, "-3"]
            if is_runnable_python(command):
                return command

    for candidate in common_windows_python_candidates():
        command = [str(candidate)]
        if is_runnable_python(command):
            return command

    if sys.executable:
        command = [sys.executable]
        if is_runnable_python(command):
            return command

    raise SystemExit("ERROR: could not determine a Python executable for bootstrap")


def resolve_runnable_repo_python_command() -> list[str] | None:
    repo_python = resolve_existing_python(DEFAULT_VENV_DIR)
    if repo_python is None:
        return None
    command = [str(repo_python)]
    if is_runnable_python(command):
        return command
    return None


if __name__ == "__main__":
    raise SystemExit(main())
