#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

from ai_governance_metadata import (
    REQ_ID_PATTERN,
    UNBOUND_VALUE,
    WS_ID_PATTERN,
    context_surface_budget_warnings,
    extract_markdown_section,
    metadata_identifier_tokens,
    normalize_stage_token,
    ordered_unique,
    parse_working_context_sync_metadata,
    read_prefixed_value,
    split_metadata_field,
    validate_identifier_field,
)
from ai_governance_traceability import (
    extract_known_ids,
    load_traceability_catalog,
    stage_alignment_mismatches,
    validate_requirement_workstream_pairings,
    validate_requirements_traceability_alignment,
)
from ai_governance_working_context import validate_working_context_sync_metadata
from harness_config import HarnessConfigError, load_harness_config


ROOT = Path(__file__).resolve().parents[1]
AI_DOC_ROOT = ROOT / "docs" / "ai"
REQ_DOC_ROOT = ROOT / "docs" / "requirements"
ADR_DIR = AI_DOC_ROOT / "adr"
WORKING_CONTEXT_PATH = AI_DOC_ROOT / "working-context.md"
PLAN_PATH = AI_DOC_ROOT / "plan.md"
ACTIVE_HANDOFF_DIR = AI_DOC_ROOT / "handoffs" / "active"
STATUS_DIR = AI_DOC_ROOT / "status"
WORKSTREAM_DIR = REQ_DOC_ROOT / "workstreams"
TRACEABILITY_MATRIX_PATH = REQ_DOC_ROOT / "traceability-matrix.md"
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
PLAN_STATE_LABELS = (
    "项目状态：",
    "当前状态：",
    "验证状态：",
    "完成度：",
    "最新验证：",
    "验收证据：",
)
WORKSTREAM_STATE_LABELS = (
    "状态：",
    "当前状态：",
    "验证状态：",
    "完成度：",
    "最新验证：",
    "验收证据：",
)
TRACEABILITY_METADATA_SECTION = "## 需求与工作流标识"
TRACEABILITY_METADATA_REQUIRED_KEYS = (
    "Requirement IDs",
    "Workstream IDs",
)
RUNTIME_TRACEABILITY_SCAN_LIMIT = 20


def load_context_surface_config() -> tuple[object | None, list[str]]:
    try:
        return load_harness_config(ROOT).context_surface, []
    except HarnessConfigError as exc:
        return None, [str(exc)]


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


def validate_active_document_state(
    *,
    active_handoffs: list[Path],
    status_docs: list[Path],
    context_surface: object | None,
    warnings: list[str],
) -> None:
    if len(active_handoffs) >= ACTIVE_HANDOFF_STATUS_WARNING_THRESHOLD and not status_docs:
        warnings.append(
            "Active handoffs have accumulated without a stage status summary. "
            f"Current active handoff count: {len(active_handoffs)}."
        )

    if context_surface is not None:
        warnings.extend(
            context_surface_budget_warnings(
                count=len(active_handoffs),
                label="Active handoff count",
                config=context_surface,
            )
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


def validate_traceability_metadata_docs(
    *,
    active_handoffs: list[Path],
    status_docs: list[Path],
    errors: list[str],
    warnings: list[str],
) -> None:
    for path in active_handoffs:
        validate_traceability_metadata_doc(
            path,
            doc_kind="active handoff",
            errors=errors,
            warnings=warnings,
        )
    for path in status_docs:
        validate_traceability_metadata_doc(
            path,
            doc_kind="status",
            errors=errors,
            warnings=warnings,
        )


def run_child_checks() -> list[tuple[str, str, str]]:
    failures: list[tuple[str, str, str]] = []
    for label, script in CHECKS:
        result = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            failures.append((label, result.stdout.strip(), result.stderr.strip()))
    return failures


def print_result(
    *,
    errors: list[str],
    failures: list[tuple[str, str, str]],
    warnings: list[str],
) -> int:
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


def main() -> int:
    errors = []
    warnings = []
    context_surface, config_errors = load_context_surface_config()
    errors.extend(config_errors)

    changed_paths = load_changed_paths()
    validate_changed_path_governance_sync(changed_paths, errors=errors, warnings=warnings)
    validate_staged_runtime_state(errors)

    active_handoffs = iter_docs(ACTIVE_HANDOFF_DIR)
    status_docs = iter_docs(STATUS_DIR)
    validate_active_document_state(
        active_handoffs=active_handoffs,
        status_docs=status_docs,
        context_surface=context_surface,
        warnings=warnings,
    )

    sync_errors, sync_warnings = validate_working_context_sync_metadata(
        active_handoffs=active_handoffs,
        status_docs=status_docs,
        context_surface=context_surface,
    )
    errors.extend(sync_errors)
    warnings.extend(sync_warnings)

    validate_requirements_traceability_alignment(errors)
    validate_runtime_traceability_artifact_alignment(warnings)
    validate_traceability_metadata_docs(
        active_handoffs=active_handoffs,
        status_docs=status_docs,
        errors=errors,
        warnings=warnings,
    )
    errors.extend(
        projection_freshness_errors(active_handoffs=active_handoffs, status_docs=status_docs)
    )

    return print_result(
        errors=errors,
        failures=run_child_checks(),
        warnings=warnings,
    )


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


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def find_projection_state_labels(path: Path, labels: tuple[str, ...]) -> list[str]:
    if not path.exists():
        return []

    matches: list[str] = []
    for raw_line in load_text(path).splitlines():
        stripped = raw_line.strip()
        if stripped.startswith(("- ", "* ")):
            stripped = stripped[2:].strip()
        for label in labels:
            if stripped.startswith(label):
                matches.append(label)
                break
    return matches


def projection_freshness_errors(
    *,
    active_handoffs: list[Path],
    status_docs: list[Path],
) -> list[str]:
    errors: list[str] = []

    plan_state_labels = find_projection_state_labels(PLAN_PATH, PLAN_STATE_LABELS)
    plan_truth_sources = [
        path
        for path in [WORKING_CONTEXT_PATH, *active_handoffs, *status_docs]
        if path.exists()
    ]
    plan_truth_target = latest_doc(plan_truth_sources)
    if (
        plan_state_labels
        and PLAN_PATH.exists()
        and plan_truth_target is not None
        and plan_truth_target.stat().st_mtime > PLAN_PATH.stat().st_mtime
    ):
        labels = ", ".join(sorted(set(plan_state_labels)))
        errors.append(
            "docs/ai/plan.md still carries explicit current-state fields "
            f"({labels}) but is older than the latest primary truth document "
            f"{plan_truth_target.relative_to(ROOT)}. Remove those fields or sync them in the same change."
        )

    if TRACEABILITY_MATRIX_PATH.exists():
        traceability_mtime = TRACEABILITY_MATRIX_PATH.stat().st_mtime
        for workstream_path in iter_docs(WORKSTREAM_DIR):
            workstream_state_labels = find_projection_state_labels(
                workstream_path,
                WORKSTREAM_STATE_LABELS,
            )
            if not workstream_state_labels:
                continue
            if traceability_mtime <= workstream_path.stat().st_mtime:
                continue
            labels = ", ".join(sorted(set(workstream_state_labels)))
            errors.append(
                f"{workstream_path.relative_to(ROOT)} still carries explicit current-state fields "
                f"({labels}) but is older than docs/requirements/traceability-matrix.md. "
                "Remove those fields or sync them in the same change."
            )

    return errors


def parse_traceability_metadata(path: Path) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for raw_line in extract_markdown_section(path, TRACEABILITY_METADATA_SECTION):
        if not raw_line.startswith("- "):
            continue
        key, value = split_metadata_field(raw_line[2:].strip())
        if key and value:
            metadata[key] = value
    return metadata


def validate_traceability_metadata_doc(
    path: Path,
    *,
    doc_kind: str,
    errors: list[str],
    warnings: list[str],
) -> None:
    metadata = parse_traceability_metadata(path)
    try:
        rendered_path = path.relative_to(ROOT)
    except ValueError:
        rendered_path = path
    owner_label = f"{doc_kind} {rendered_path} traceability metadata"

    for key in TRACEABILITY_METADATA_REQUIRED_KEYS:
        if key not in metadata:
            errors.append(
                f"{rendered_path} is missing '{key}' under "
                f"{TRACEABILITY_METADATA_SECTION}."
            )

    validate_identifier_field(
        metadata,
        key="Requirement IDs",
        pattern=REQ_ID_PATTERN,
        known_ids=extract_known_ids(REQ_ID_PATTERN),
        bootstrap_like=False,
        errors=errors,
        warnings=warnings,
        owner_label=owner_label,
        warn_on_unbound=False,
    )
    validate_identifier_field(
        metadata,
        key="Workstream IDs",
        pattern=WS_ID_PATTERN,
        known_ids=extract_known_ids(WS_ID_PATTERN),
        bootstrap_like=False,
        errors=errors,
        warnings=warnings,
        owner_label=owner_label,
        warn_on_unbound=False,
    )
    requirement_ids, requirements_unbound = metadata_identifier_tokens(
        metadata,
        "Requirement IDs",
        REQ_ID_PATTERN,
    )
    workstream_ids, workstreams_unbound = metadata_identifier_tokens(
        metadata,
        "Workstream IDs",
        WS_ID_PATTERN,
    )
    if not requirements_unbound and not workstreams_unbound:
        validate_requirement_workstream_pairings(
            requirement_ids=requirement_ids,
            workstream_ids=workstream_ids,
            owner_label=owner_label,
            errors=errors,
        )


def validate_runtime_traceability_artifact_alignment(warnings: list[str]) -> None:
    if not WORKING_CONTEXT_PATH.exists():
        return

    sync_metadata = parse_working_context_sync_metadata()
    current_stage = sync_metadata.get("Current Stage")
    if not isinstance(current_stage, str) or not current_stage.strip():
        return

    catalog = load_traceability_catalog()
    rows: list[dict[str, str]] = catalog["rows"]  # type: ignore[assignment]
    for owner_label, requirement_ids, workstream_ids in runtime_traceability_records():
        mismatches = stage_alignment_mismatches(
            rows=rows,
            requirement_ids=requirement_ids,
            workstream_ids=workstream_ids,
            current_stage=current_stage,
        )
        if not mismatches:
            continue
        rendered = ", ".join(mismatches)
        warnings.append(
            f"{owner_label} carries REQ/WS metadata outside current stage "
            f"{normalize_stage_token(current_stage)}: {rendered}"
        )


def runtime_traceability_records() -> list[tuple[str, list[str], list[str]]]:
    records: list[tuple[str, list[str], list[str]]] = []
    records.extend(runtime_session_traceability_records())
    records.extend(runtime_observation_traceability_records())
    return records


def runtime_session_traceability_records() -> list[tuple[str, list[str], list[str]]]:
    if not RUNTIME_SESSION_DIR.exists():
        return []

    records: list[tuple[str, list[str], list[str]]] = []
    session_paths = sorted(RUNTIME_SESSION_DIR.glob("*.md"), key=lambda path: path.stat().st_mtime)
    for path in session_paths[-RUNTIME_TRACEABILITY_SCAN_LIMIT:]:
        if path.name.startswith("_") or path.name == "README.md":
            continue
        metadata = parse_traceability_metadata(path)
        requirement_ids, requirements_unbound = metadata_identifier_tokens(
            metadata,
            "Requirement IDs",
            REQ_ID_PATTERN,
        )
        workstream_ids, workstreams_unbound = metadata_identifier_tokens(
            metadata,
            "Workstream IDs",
            WS_ID_PATTERN,
        )
        if requirements_unbound or workstreams_unbound or not requirement_ids or not workstream_ids:
            continue
        records.append((f"runtime session {path.relative_to(ROOT)}", requirement_ids, workstream_ids))
    return records


def runtime_observation_traceability_records() -> list[tuple[str, list[str], list[str]]]:
    if not RUNTIME_OBSERVATION_DIR.exists():
        return []

    entries: list[tuple[float, Path, dict[str, object]]] = []
    for path in sorted(RUNTIME_OBSERVATION_DIR.glob("*.jsonl")):
        if path.name.startswith("_"):
            continue
        for record in load_runtime_observation_records(path):
            timestamp = str(record.get("timestamp") or "")
            sort_key = path.stat().st_mtime
            if timestamp:
                sort_key += 0.001
            entries.append((sort_key, path, record))

    records: list[tuple[str, list[str], list[str]]] = []
    for _, path, record in entries[-RUNTIME_TRACEABILITY_SCAN_LIMIT:]:
        requirement_ids = identifier_list_from_json(record.get("requirement_ids"), REQ_ID_PATTERN)
        workstream_ids = identifier_list_from_json(record.get("workstream_ids"), WS_ID_PATTERN)
        if not requirement_ids or not workstream_ids:
            continue
        session_id = str(record.get("session_id") or "unknown-session")
        records.append(
            (
                f"runtime observation {path.relative_to(ROOT)} session {session_id}",
                requirement_ids,
                workstream_ids,
            )
        )
    return records


def load_runtime_observation_records(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for raw_line in load_text(path).splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            records.append(payload)
    return records


def identifier_list_from_json(value: object, pattern: re.Pattern[str]) -> list[str]:
    if not isinstance(value, list):
        return []
    tokens: list[str] = []
    for item in value:
        if isinstance(item, str) and pattern.fullmatch(item.strip()):
            tokens.append(item.strip())
    return ordered_unique(tokens)


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


if __name__ == "__main__":
    raise SystemExit(main())
