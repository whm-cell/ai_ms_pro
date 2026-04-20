#!/usr/bin/env python3

from __future__ import annotations

import re
import subprocess
import sys
from datetime import date
from pathlib import Path


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
SYNC_METADATA_SECTION = "## 同步元数据"
SYNC_METADATA_REQUIRED_KEYS = (
    "Current Stage",
    "Active Status Source",
    "Active Handoff Sources",
    "Requirement IDs",
    "Workstream IDs",
    "Last Synced From",
    "Last Synced At",
)
SYNC_ALLOWED_SOURCE_TOKENS = {"bootstrap", "handoff", "status", "manual"}
UNBOUND_VALUE = "未绑定"
PLACEHOLDER_DATE = "YYYY-MM-DD"
REQ_ID_PATTERN = re.compile(r"REQ-\d+")
WS_ID_PATTERN = re.compile(r"WS-\d+")
STAGE_TOKEN_PATTERN = re.compile(r"stage-\d+", re.IGNORECASE)


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

    sync_errors, sync_warnings = validate_working_context_sync_metadata(
        active_handoffs=active_handoffs,
        status_docs=status_docs,
    )
    errors.extend(sync_errors)
    warnings.extend(sync_warnings)

    errors.extend(
        projection_freshness_errors(active_handoffs=active_handoffs, status_docs=status_docs)
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


def extract_markdown_section(path: Path, heading: str) -> list[str]:
    if not path.exists():
        return []

    lines = load_text(path).splitlines()
    in_section = False
    collected: list[str] = []
    for line in lines:
        if line.startswith("## "):
            if line.strip() == heading:
                in_section = True
                continue
            if in_section:
                break
        if in_section:
            collected.append(line.rstrip())
    return collected


def split_metadata_field(text: str) -> tuple[str | None, str | None]:
    for separator in (":", "："):
        if separator in text:
            key, value = text.split(separator, 1)
            return key.strip(), value.strip()
    return None, None


def parse_working_context_sync_metadata() -> dict[str, str | list[str]]:
    metadata: dict[str, str | list[str]] = {}
    current_key: str | None = None

    for raw_line in extract_markdown_section(WORKING_CONTEXT_PATH, SYNC_METADATA_SECTION):
        if raw_line.startswith("- "):
            key, value = split_metadata_field(raw_line[2:].strip())
            if not key:
                current_key = None
                continue
            if value:
                metadata[key] = value
                current_key = None
                continue
            metadata[key] = []
            current_key = key
            continue

        if raw_line.startswith("  - ") or raw_line.startswith("    - "):
            if current_key is None:
                continue
            nested_value = raw_line.strip()[2:].strip()
            existing_value = metadata.get(current_key)
            if isinstance(existing_value, list) and nested_value:
                existing_value.append(nested_value)

    return metadata


def scalar_metadata_value(
    metadata: dict[str, str | list[str]],
    key: str,
    errors: list[str],
) -> str | None:
    value = metadata.get(key)
    if value is None:
        return None
    if isinstance(value, list):
        if not value:
            errors.append(f"working-context sync metadata field '{key}' is empty.")
        else:
            errors.append(f"working-context sync metadata field '{key}' must be a single value.")
        return None

    stripped = value.strip()
    if not stripped:
        errors.append(f"working-context sync metadata field '{key}' is empty.")
        return None
    return stripped


def normalize_stage_token(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        return ""
    match = STAGE_TOKEN_PATTERN.search(stripped)
    if match:
        return match.group(0).upper()
    return stripped.upper()


def read_prefixed_value(path: Path, prefixes: tuple[str, ...]) -> str | None:
    if not path.exists():
        return None
    for raw_line in load_text(path).splitlines():
        stripped = raw_line.strip()
        for prefix in prefixes:
            if stripped.startswith(prefix):
                return stripped[len(prefix):].strip()
    return None


def resolve_repo_relative_path(path_text: str) -> Path | None:
    stripped = path_text.strip()
    if not stripped:
        return None
    if stripped.startswith("/"):
        return None
    if stripped.startswith("./"):
        stripped = stripped[2:]
    return (ROOT / stripped).resolve()


def parse_csv_values(text: str) -> list[str]:
    return [part.strip() for part in re.split(r"[，,]", text) if part.strip()]


def extract_known_ids(pattern: re.Pattern[str]) -> set[str]:
    if not TRACEABILITY_MATRIX_PATH.exists():
        return set()
    return set(pattern.findall(load_text(TRACEABILITY_MATRIX_PATH)))


def validate_identifier_field(
    metadata: dict[str, str | list[str]],
    *,
    key: str,
    pattern: re.Pattern[str],
    known_ids: set[str],
    bootstrap_like: bool,
    errors: list[str],
    warnings: list[str],
) -> None:
    value = metadata.get(key)
    if value is None:
        return

    raw_values: list[str]
    if isinstance(value, list):
        raw_values = value
    else:
        raw_values = [value]

    tokens: list[str] = []
    for raw_value in raw_values:
        stripped = raw_value.strip()
        if not stripped:
            continue
        if stripped == UNBOUND_VALUE:
            if known_ids and not bootstrap_like:
                warnings.append(
                    f"working-context sync metadata leaves '{key}' unbound even though "
                    "traceability ids already exist."
                )
            return
        tokens.extend(parse_csv_values(stripped))

    if not tokens:
        errors.append(f"working-context sync metadata field '{key}' is empty.")
        return

    invalid_tokens = [token for token in tokens if not pattern.fullmatch(token)]
    if invalid_tokens:
        rendered = ", ".join(sorted(set(invalid_tokens)))
        errors.append(
            f"working-context sync metadata field '{key}' contains malformed ids: {rendered}"
        )
        return

    unknown_ids = [token for token in tokens if token not in known_ids]
    if unknown_ids:
        rendered = ", ".join(sorted(set(unknown_ids)))
        errors.append(
            f"working-context sync metadata field '{key}' contains ids missing from "
            f"docs/requirements/traceability-matrix.md: {rendered}"
        )


def validate_working_context_sync_metadata(
    *,
    active_handoffs: list[Path],
    status_docs: list[Path],
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if not WORKING_CONTEXT_PATH.exists():
        return errors, warnings

    metadata = parse_working_context_sync_metadata()
    for key in SYNC_METADATA_REQUIRED_KEYS:
        if key not in metadata:
            errors.append(
                "working-context.md is missing required sync metadata field "
                f"'{key}' under {SYNC_METADATA_SECTION}."
            )

    bootstrap_like = not active_handoffs and not status_docs
    document_stage = read_prefixed_value(WORKING_CONTEXT_PATH, ("当前阶段：",))
    document_updated_at = read_prefixed_value(WORKING_CONTEXT_PATH, ("更新时间：",))

    current_stage = scalar_metadata_value(metadata, "Current Stage", errors)
    if current_stage and document_stage:
        if normalize_stage_token(current_stage) != normalize_stage_token(document_stage):
            errors.append(
                "working-context sync metadata field 'Current Stage' does not match the document "
                f"header stage: metadata={current_stage}, header={document_stage}"
            )

    active_status_source = scalar_metadata_value(metadata, "Active Status Source", errors)
    active_status_path: Path | None = None
    if active_status_source:
        if active_status_source == UNBOUND_VALUE:
            if status_docs and not bootstrap_like:
                warnings.append(
                    "working-context sync metadata leaves 'Active Status Source' unbound even though "
                    "stage status documents already exist."
                )
        else:
            active_status_path = resolve_repo_relative_path(active_status_source)
            if active_status_path is None:
                errors.append(
                    "working-context sync metadata field 'Active Status Source' must use a "
                    "repo-relative path."
                )
            elif not active_status_path.exists():
                errors.append(
                    "working-context sync metadata points to a missing status document: "
                    f"{active_status_source}"
                )
            elif not is_under_root(active_status_path, (STATUS_DIR,)):
                errors.append(
                    "working-context sync metadata field 'Active Status Source' must point into "
                    f"{STATUS_DIR.relative_to(ROOT)}."
                )
            else:
                status_stage = read_prefixed_value(active_status_path, ("阶段：", "当前阶段："))
                if current_stage and status_stage:
                    if normalize_stage_token(current_stage) != normalize_stage_token(status_stage):
                        errors.append(
                            "working-context sync metadata field 'Current Stage' does not match the "
                            f"bound status source {active_status_source}: {status_stage}"
                        )
                if active_status_path.stat().st_mtime > WORKING_CONTEXT_PATH.stat().st_mtime:
                    warnings.append(
                        "working-context.md is older than its bound Active Status Source "
                        f"{active_status_source}. Refresh the current-state summary."
                    )

    handoff_value = metadata.get("Active Handoff Sources")
    handoff_unbound = False
    bound_handoff_paths: list[Path] = []
    if handoff_value is None:
        pass
    elif isinstance(handoff_value, list):
        cleaned_handoffs = [item.strip() for item in handoff_value if item.strip()]
        if not cleaned_handoffs:
            errors.append("working-context sync metadata field 'Active Handoff Sources' is empty.")
        else:
            for raw_path in cleaned_handoffs:
                resolved_path = resolve_repo_relative_path(raw_path)
                if resolved_path is None:
                    errors.append(
                        "working-context sync metadata field 'Active Handoff Sources' must use "
                        "repo-relative paths."
                    )
                    continue
                if not resolved_path.exists():
                    errors.append(
                        "working-context sync metadata points to a missing active handoff: "
                        f"{raw_path}"
                    )
                    continue
                if not is_under_root(resolved_path, (ACTIVE_HANDOFF_DIR,)):
                    errors.append(
                        "working-context sync metadata field 'Active Handoff Sources' must point "
                        f"into {ACTIVE_HANDOFF_DIR.relative_to(ROOT)}."
                    )
                    continue
                bound_handoff_paths.append(resolved_path)
    else:
        stripped = handoff_value.strip()
        if not stripped:
            errors.append("working-context sync metadata field 'Active Handoff Sources' is empty.")
        elif stripped == UNBOUND_VALUE:
            handoff_unbound = True
            if active_handoffs and not bootstrap_like:
                warnings.append(
                    "working-context sync metadata leaves 'Active Handoff Sources' unbound even "
                    "though active handoff documents already exist."
                )
        else:
            for raw_path in parse_csv_values(stripped):
                resolved_path = resolve_repo_relative_path(raw_path)
                if resolved_path is None:
                    errors.append(
                        "working-context sync metadata field 'Active Handoff Sources' must use "
                        "repo-relative paths."
                    )
                    continue
                if not resolved_path.exists():
                    errors.append(
                        "working-context sync metadata points to a missing active handoff: "
                        f"{raw_path}"
                    )
                    continue
                if not is_under_root(resolved_path, (ACTIVE_HANDOFF_DIR,)):
                    errors.append(
                        "working-context sync metadata field 'Active Handoff Sources' must point "
                        f"into {ACTIVE_HANDOFF_DIR.relative_to(ROOT)}."
                    )
                    continue
                bound_handoff_paths.append(resolved_path)

    newer_bound_handoffs = [
        path for path in bound_handoff_paths if path.stat().st_mtime > WORKING_CONTEXT_PATH.stat().st_mtime
    ]
    if newer_bound_handoffs:
        newest = latest_doc(newer_bound_handoffs)
        assert newest is not None
        warnings.append(
            "working-context.md is older than one of its bound Active Handoff Sources, latest: "
            f"{newest.relative_to(ROOT)}."
        )

    validate_identifier_field(
        metadata,
        key="Requirement IDs",
        pattern=REQ_ID_PATTERN,
        known_ids=extract_known_ids(REQ_ID_PATTERN),
        bootstrap_like=bootstrap_like,
        errors=errors,
        warnings=warnings,
    )
    validate_identifier_field(
        metadata,
        key="Workstream IDs",
        pattern=WS_ID_PATTERN,
        known_ids=extract_known_ids(WS_ID_PATTERN),
        bootstrap_like=bootstrap_like,
        errors=errors,
        warnings=warnings,
    )

    last_synced_from = scalar_metadata_value(metadata, "Last Synced From", errors)
    if last_synced_from:
        source_tokens = [token.strip() for token in last_synced_from.split(",") if token.strip()]
        if not source_tokens:
            errors.append("working-context sync metadata field 'Last Synced From' is empty.")
        invalid_tokens = [token for token in source_tokens if token not in SYNC_ALLOWED_SOURCE_TOKENS]
        if invalid_tokens:
            rendered = ", ".join(sorted(set(invalid_tokens)))
            errors.append(
                "working-context sync metadata field 'Last Synced From' contains unsupported tokens: "
                f"{rendered}"
            )
        if "status" in source_tokens and active_status_source == UNBOUND_VALUE:
            errors.append(
                "working-context sync metadata field 'Last Synced From' references 'status' but "
                "'Active Status Source' is unbound."
            )
        if "handoff" in source_tokens and handoff_unbound:
            errors.append(
                "working-context sync metadata field 'Last Synced From' references 'handoff' but "
                "'Active Handoff Sources' is unbound."
            )

    last_synced_at = scalar_metadata_value(metadata, "Last Synced At", errors)
    if last_synced_at:
        if last_synced_at == PLACEHOLDER_DATE:
            if not bootstrap_like:
                errors.append(
                    "working-context sync metadata field 'Last Synced At' still uses the starter "
                    "placeholder outside bootstrap state."
                )
        else:
            try:
                date.fromisoformat(last_synced_at)
            except ValueError:
                errors.append(
                    "working-context sync metadata field 'Last Synced At' must use YYYY-MM-DD."
                )

        if document_updated_at:
            if document_updated_at == PLACEHOLDER_DATE:
                if last_synced_at != PLACEHOLDER_DATE:
                    errors.append(
                        "working-context header 更新时间 and sync metadata 'Last Synced At' must "
                        "both leave bootstrap state together."
                    )
            elif last_synced_at == PLACEHOLDER_DATE:
                errors.append(
                    "working-context sync metadata field 'Last Synced At' is still a starter "
                    "placeholder while 更新时间 is already bound."
                )
            elif document_updated_at != last_synced_at:
                errors.append(
                    "working-context header 更新时间 and sync metadata 'Last Synced At' differ: "
                    f"header={document_updated_at}, metadata={last_synced_at}"
                )

    return errors, warnings


def load_changed_paths() -> list[Path]:
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
