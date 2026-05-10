from __future__ import annotations

import os
import subprocess
from pathlib import Path

from ai_governance_metadata import AI_DOC_ROOT, REQ_DOC_ROOT, ROOT, is_under_root


ADR_DIR = AI_DOC_ROOT / "adr"
WORKING_CONTEXT_PATH = AI_DOC_ROOT / "working-context.md"
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
GOVERNANCE_DOC_SYNC_WARNING_ONLY_FILES = {
    ROOT / "scripts" / "check_ai_governance.py",
}
DOC_ROOTS = (AI_DOC_ROOT, REQ_DOC_ROOT)
DIFF_WARNING_EXCLUDE_ROOTS = (
    ROOT / "mysjzhishidian",
    ROOT / ".codex" / "runtime",
)
DIFF_WARNING_EXCLUDE_FILES = {
    ROOT / "AGENTS.md",
}


def validate_changed_path_governance_sync(
    changed_paths: list[Path],
    *,
    errors: list[str],
    warnings: list[str],
) -> None:
    if not changed_paths:
        return

    docs_changed = any(is_under_root(path, DOC_ROOTS) for path in changed_paths)
    non_docs_changed = any(is_implementation_candidate(path) for path in changed_paths)
    if non_docs_changed and not docs_changed:
        warnings.append(
            "Implementation changes detected outside docs/ai and docs/requirements, "
            "but no docs updates were found."
        )

    governance_impl_changed = any(
        is_governance_implementation_path(path) for path in changed_paths
    )
    governance_impl_doc_sync_required = [
        path for path in changed_paths if requires_governance_doc_sync(path)
    ]
    if governance_impl_doc_sync_required and not has_governance_sync_docs(changed_paths):
        errors.append(
            "Core governance implementation changed, but neither working-context.md nor an ADR "
            "was updated. Sync current-state or decision docs before completing the task."
        )
    elif governance_impl_changed and not has_governance_sync_docs(changed_paths):
        warnings.append(
            "Governance verification surfaces changed without working-context/ADR updates. "
            "Confirm shared docs still describe the effective control plane."
        )


def validate_staged_runtime_state(errors: list[str]) -> None:
    staged_runtime_state_files = [
        path for path in load_staged_paths() if is_runtime_state_file(path)
    ]
    if not staged_runtime_state_files:
        return

    rendered = ", ".join(str(path.relative_to(ROOT)) for path in staged_runtime_state_files)
    errors.append(
        "Runtime session/observation files must not be staged. "
        f"Remove these from the index: {rendered}"
    )


def load_changed_paths() -> list[Path]:
    ci_paths = load_ci_changed_paths()
    if ci_paths is not None:
        return ci_paths

    try:
        result = subprocess.run(
            ["git", "status", "--porcelain=v1", "-uall"],
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


def load_ci_changed_paths() -> list[Path] | None:
    if os.environ.get("GITHUB_ACTIONS") != "true":
        return None

    for base_ref in ("HEAD^1", "HEAD~1"):
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "--relative", base_ref, "HEAD"],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                check=True,
            )
        except (OSError, subprocess.CalledProcessError):
            continue
        return [(ROOT / entry).resolve() for entry in result.stdout.splitlines() if entry.strip()]

    return []


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


def is_runtime_state_file(path: Path) -> bool:
    if not is_under_root(path, RUNTIME_STATE_ROOTS):
        return False
    return path.name != "README.md" and not path.name.startswith("_")


def is_governance_implementation_path(path: Path) -> bool:
    if path in GOVERNANCE_IMPLEMENTATION_FILES:
        return True
    return is_under_root(path, GOVERNANCE_IMPLEMENTATION_ROOTS)


def requires_governance_doc_sync(path: Path) -> bool:
    if not is_governance_implementation_path(path):
        return False
    return path not in GOVERNANCE_DOC_SYNC_WARNING_ONLY_FILES


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
