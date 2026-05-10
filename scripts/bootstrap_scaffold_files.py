#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path

from bootstrap_ai_docs import render_ai_index, render_working_context
from bootstrap_plan_renderer import render_plan
from bootstrap_requirements_docs import render_requirements_index, render_traceability_matrix
from bootstrap_scaffold_config import render_harness_config, render_requirements_txt


SCAFFOLD_DIRECTORY_PARTS = [
    (".codex",),
    (".githooks",),
    (".codex", "runtime"),
    (".codex", "runtime", "sessions"),
    (".codex", "runtime", "observations"),
    ("docs", "ai"),
    ("docs", "ai", "handoffs", "active"),
    ("docs", "ai", "handoffs", "archive"),
    ("docs", "ai", "status"),
    ("docs", "ai", "changelog"),
    ("docs", "ai", "adr"),
    ("docs", "ai", "archive"),
    ("docs", "requirements"),
    ("docs", "requirements", "source"),
    ("docs", "requirements", "normalized"),
    ("docs", "requirements", "workstreams"),
]

BOOTSTRAP_PREREQUISITE_PARTS = [
    (".codex", "harness.toml"),
    (".codex", "requirements.txt"),
]


def ensure_directories(root: Path) -> None:
    for parts in SCAFFOLD_DIRECTORY_PARTS:
        (root.joinpath(*parts)).mkdir(parents=True, exist_ok=True)


def scaffold_files(
    *,
    root: Path,
    project_name: str,
    stage_label: str,
    hooks_config: str,
) -> dict[Path, str]:
    return {
        root / ".codex" / "harness.toml": render_harness_config(),
        root / ".codex" / "requirements.txt": render_requirements_txt(),
        root / ".codex" / "hooks.json": hooks_config,
        root / "docs" / "ai" / "index.md": render_ai_index(project_name, stage_label),
        root / "docs" / "ai" / "plan.md": render_plan(project_name, stage_label),
        root / "docs" / "ai" / "working-context.md": render_working_context(project_name, stage_label),
        root / "docs" / "requirements" / "index.md": render_requirements_index(),
        root / "docs" / "requirements" / "traceability-matrix.md": render_traceability_matrix(),
    }


def write_bootstrap_prerequisites(
    *,
    files: dict[Path, str],
    root: Path,
    force: bool,
) -> None:
    for parts in BOOTSTRAP_PREREQUISITE_PARTS:
        path = root.joinpath(*parts)
        content = files[path]
        if path.exists() and not force:
            continue
        path.write_text(content, encoding="utf-8")


def write_hooks_config(
    *,
    files: dict[Path, str],
    root: Path,
) -> None:
    hooks_config_path = root / ".codex" / "hooks.json"
    hooks_config_path.write_text(files[hooks_config_path], encoding="utf-8")


def write_scaffold_files(
    *,
    files: dict[Path, str],
    force: bool,
) -> tuple[list[Path], list[Path]]:
    written = []
    skipped = []

    for path, content in files.items():
        if path.exists() and not force:
            skipped.append(path)
            continue
        path.write_text(content, encoding="utf-8")
        written.append(path)

    return written, skipped


def print_write_result(
    *,
    written: list[Path],
    skipped: list[Path],
    root: Path,
) -> None:
    if written:
        print("Bootstrapped harness starter files:")
        for path in written:
            print(f"- {path.relative_to(root)}")
    if skipped:
        print("Skipped existing files:")
        for path in skipped:
            print(f"- {path.relative_to(root)}")
