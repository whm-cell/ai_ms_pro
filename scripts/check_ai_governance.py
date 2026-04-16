#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AI_DOC_ROOT = ROOT / "docs" / "ai"
REQ_DOC_ROOT = ROOT / "docs" / "requirements"
ADR_DIR = AI_DOC_ROOT / "adr"
WORKING_CONTEXT_PATH = AI_DOC_ROOT / "working-context.md"
ACTIVE_HANDOFF_DIR = AI_DOC_ROOT / "handoffs" / "active"
STATUS_DIR = AI_DOC_ROOT / "status"
RUNTIME_SESSION_DIR = ROOT / ".codex" / "runtime" / "sessions"
RUNTIME_OBSERVATION_DIR = ROOT / ".codex" / "runtime" / "observations"
RUNTIME_STATE_ROOTS = (RUNTIME_SESSION_DIR, RUNTIME_OBSERVATION_DIR)
GOVERNANCE_IMPLEMENTATION_ROOTS = (
    ROOT / "scripts",
    ROOT / ".codex" / "hooks",
    ROOT / ".githooks",
)
GOVERNANCE_IMPLEMENTATION_FILES = {
    ROOT / ".codex" / "hooks.json",
    ROOT / ".codex" / "config.toml",
}
CHECKS = [
    ("structure", ROOT / "scripts" / "check_ai_docs.py"),
    ("quality", ROOT / "scripts" / "check_ai_doc_quality.py"),
]
DOC_ROOTS = (AI_DOC_ROOT, REQ_DOC_ROOT)
DIFF_WARNING_EXCLUDE_ROOTS = (
    ROOT / "mysjzhishidian",
    ROOT / ".codex" / "runtime",
)
DIFF_WARNING_EXCLUDE_FILES = {
    ROOT / "AGENTS.md",
}
ACTIVE_HANDOFF_STATUS_WARNING_THRESHOLD = 3


def main() -> int:
    failures = []
    errors = []
    warnings = []

    changed_paths = load_changed_paths()
    if changed_paths:
        docs_changed = any(is_under_root(path, DOC_ROOTS) for path in changed_paths)
        non_docs_changed = any(is_implementation_candidate(path) for path in changed_paths)
        if non_docs_changed and not docs_changed:
            warnings.append(
                "Implementation changes detected outside docs/ai and docs/requirements, "
                "but no docs updates were found."
            )
        governance_impl_changed = any(is_governance_implementation_path(path) for path in changed_paths)
        if governance_impl_changed and not has_governance_sync_docs(changed_paths):
            errors.append(
                "Core governance implementation changed, but neither working-context.md nor an ADR "
                "was updated. Sync current-state or decision docs before completing the task."
            )

    staged_paths = load_staged_paths()
    staged_runtime_state_files = [
        path for path in staged_paths if is_runtime_state_file(path)
    ]
    if staged_runtime_state_files:
        rendered = ", ".join(str(path.relative_to(ROOT)) for path in staged_runtime_state_files)
        errors.append(
            "Runtime session/observation files must not be staged. "
            f"Remove these from the index: {rendered}"
        )

    active_handoffs = iter_docs(ACTIVE_HANDOFF_DIR)
    status_docs = iter_docs(STATUS_DIR)
    if len(active_handoffs) >= ACTIVE_HANDOFF_STATUS_WARNING_THRESHOLD and not status_docs:
        warnings.append(
            "Active handoffs have accumulated without a stage status summary. "
            f"Current active handoff count: {len(active_handoffs)}."
        )

    freshness_target = latest_doc(active_handoffs + status_docs)
    if (
        WORKING_CONTEXT_PATH.exists()
        and freshness_target is not None
        and freshness_target.stat().st_mtime > WORKING_CONTEXT_PATH.stat().st_mtime
    ):
        warnings.append(
            "working-context.md is older than the latest active handoff/status document. "
            f"Consider refreshing current-state summary from {freshness_target.relative_to(ROOT)}."
        )

    for label, script in CHECKS:
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            failures.append((label, result.stdout.strip(), result.stderr.strip()))

    if errors or failures:
        print("AI governance checks: FAILED")
        for message in errors:
            print(f"ERROR: {message}")
        for label, stdout, stderr in failures:
            print(f"[{label}]")
            if stdout:
                print(stdout)
            if stderr:
                print(stderr)
        for message in warnings:
            print(f"WARN: {message}")
        return 1

    print("AI governance checks: OK")
    for message in warnings:
        print(f"WARN: {message}")
    return 0


def iter_docs(directory: Path) -> list[Path]:
    if not directory.exists():
        return []
    files: list[Path] = []
    for path in sorted(directory.glob("*.md")):
        if path.name.startswith("_"):
            continue
        if path.name == "README.md":
            continue
        files.append(path)
    return files


def latest_doc(paths: list[Path]) -> Path | None:
    if not paths:
        return None
    return max(paths, key=lambda path: path.stat().st_mtime)


def load_changed_paths() -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain=v1"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return []

    entries = [entry for entry in result.stdout.splitlines() if entry.strip()]
    paths: list[Path] = []
    for entry in entries:
        if len(entry) < 4:
            continue
        path_text = entry[3:]
        if " -> " in path_text:
            path_text = path_text.split(" -> ", 1)[1]
        paths.append((ROOT / path_text).resolve())
    return paths


def load_staged_paths() -> list[Path]:
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--relative"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return []

    return [(ROOT / entry).resolve() for entry in result.stdout.splitlines() if entry.strip()]


def is_under_root(path: Path, roots: tuple[Path, ...]) -> bool:
    for root in roots:
        try:
            path.relative_to(root)
            return True
        except ValueError:
            continue
    return False


def is_runtime_state_file(path: Path) -> bool:
    if not is_under_root(path, RUNTIME_STATE_ROOTS):
        return False
    return path.name != "README.md" and not path.name.startswith("_")


def is_governance_implementation_path(path: Path) -> bool:
    if path in GOVERNANCE_IMPLEMENTATION_FILES:
        return True
    return is_under_root(path, GOVERNANCE_IMPLEMENTATION_ROOTS)


def has_governance_sync_docs(paths: list[Path]) -> bool:
    for path in paths:
        if path == WORKING_CONTEXT_PATH:
            return True
        if is_under_root(path, (ADR_DIR,)):
            return True
    return False


def is_implementation_candidate(path: Path) -> bool:
    if is_under_root(path, DOC_ROOTS):
        return False
    if is_under_root(path, DIFF_WARNING_EXCLUDE_ROOTS):
        return False
    if path in DIFF_WARNING_EXCLUDE_FILES:
        return False
    return True


if __name__ == "__main__":
    raise SystemExit(main())
