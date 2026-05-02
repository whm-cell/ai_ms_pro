#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import date
from functools import lru_cache
from pathlib import Path

from harness_config import ContextSurfaceConfig, HarnessConfigError, load_harness_config


ROOT = Path(__file__).resolve().parents[1]
AI_DOC_ROOT = ROOT / "docs" / "ai"
REQ_DOC_ROOT = ROOT / "docs" / "requirements"
ADR_DIR = AI_DOC_ROOT / "adr"
WORKING_CONTEXT_PATH = AI_DOC_ROOT / "working-context.md"
PLAN_PATH = AI_DOC_ROOT / "plan.md"
ACTIVE_HANDOFF_DIR = AI_DOC_ROOT / "handoffs" / "active"
STATUS_DIR = AI_DOC_ROOT / "status"
SOURCE_DOC_DIR = REQ_DOC_ROOT / "source"
NORMALIZED_REQ_DIR = REQ_DOC_ROOT / "normalized"
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
SYNC_METADATA_SECTION = "## 同步元数据"
TRACEABILITY_METADATA_SECTION = "## 需求与工作流标识"
SYNC_METADATA_REQUIRED_KEYS = (
    "Current Stage",
    "Active Status Source",
    "Active Handoff Sources",
    "Requirement IDs",
    "Workstream IDs",
    "Last Synced From",
    "Last Synced At",
)
TRACEABILITY_METADATA_REQUIRED_KEYS = (
    "Requirement IDs",
    "Workstream IDs",
)
SYNC_ALLOWED_SOURCE_TOKENS = {"bootstrap", "handoff", "status", "manual"}
UNBOUND_VALUE = "未绑定"
PLACEHOLDER_DATE = "YYYY-MM-DD"
REQDOC_ID_PATTERN = re.compile(r"REQDOC-\d+")
REQ_ID_PATTERN = re.compile(r"REQ-\d+")
WS_ID_PATTERN = re.compile(r"WS-\d+")
STAGE_TOKEN_PATTERN = re.compile(r"stage-\d+", re.IGNORECASE)
RUNTIME_TRACEABILITY_SCAN_LIMIT = 20


def main() -> int:
    failures = []
    errors = []
    warnings = []
    context_surface = None

    try:
        context_surface = load_harness_config(ROOT).context_surface
    except HarnessConfigError as exc:
        errors.append(str(exc))

    changed_paths = load_changed_paths()
    if changed_paths:
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

    sync_errors, sync_warnings = validate_working_context_sync_metadata(
        active_handoffs=active_handoffs,
        status_docs=status_docs,
        context_surface=context_surface,
    )
    errors.extend(sync_errors)
    warnings.extend(sync_warnings)

    validate_requirements_traceability_alignment(errors)
    validate_runtime_traceability_artifact_alignment(warnings)

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


def parse_traceability_metadata(path: Path) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for raw_line in extract_markdown_section(path, TRACEABILITY_METADATA_SECTION):
        if not raw_line.startswith("- "):
            continue
        key, value = split_metadata_field(raw_line[2:].strip())
        if key and value:
            metadata[key] = value
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


def context_surface_budget_warnings(
    *,
    count: int,
    label: str,
    config: ContextSurfaceConfig,
) -> list[str]:
    budget = config.active_handoff_budget
    over_budget = count > budget
    at_budget = config.warn_at_budget and count >= budget
    if not over_budget and not at_budget:
        return []

    relation = ">=" if count == budget else ">"
    return [
        (
            f"{label} has reached the configured default surface budget "
            f"({count} {relation} {budget}). Run scripts/check_archive_candidates.py "
            "and archive or compress handoffs already absorbed by stage status/ADR."
        )
    ]


def ordered_unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def first_pattern_match(text: str | None, pattern: re.Pattern[str]) -> str | None:
    if not text:
        return None
    match = pattern.search(text)
    if match is None:
        return None
    return match.group(0)


def extract_ids_from_section(path: Path, heading: str, pattern: re.Pattern[str]) -> list[str]:
    section_text = "\n".join(extract_markdown_section(path, heading))
    return ordered_unique(pattern.findall(section_text))


def parse_matrix_row(raw_line: str) -> dict[str, str] | None:
    stripped = raw_line.strip()
    if not stripped.startswith("|"):
        return None

    cells = [cell.strip() for cell in stripped.split("|")[1:-1]]
    if len(cells) < 6:
        return None
    if cells[0] == "原始文档":
        return None
    if all(re.fullmatch(r"-+", cell) for cell in cells):
        return None

    source_id = first_pattern_match(cells[0], REQDOC_ID_PATTERN)
    requirement_id = first_pattern_match(cells[1], REQ_ID_PATTERN)
    workstream_id = first_pattern_match(cells[2], WS_ID_PATTERN)
    stage_token = normalize_stage_token(cells[3])
    if not source_id or not requirement_id or not workstream_id:
        return None

    return {
        "source_id": source_id,
        "requirement_id": requirement_id,
        "workstream_id": workstream_id,
        "stage_token": stage_token or "",
    }


@lru_cache(maxsize=1)
def load_traceability_catalog() -> dict[str, object]:
    rows: list[dict[str, str]] = []
    if TRACEABILITY_MATRIX_PATH.exists():
        in_matrix = False
        for raw_line in load_text(TRACEABILITY_MATRIX_PATH).splitlines():
            stripped = raw_line.strip()
            if stripped == "## 矩阵":
                in_matrix = True
                continue
            if in_matrix and stripped.startswith("## "):
                break
            if not in_matrix:
                continue
            row = parse_matrix_row(raw_line)
            if row is not None:
                rows.append(row)

    req_to_ws: dict[str, set[str]] = defaultdict(set)
    ws_to_req: dict[str, set[str]] = defaultdict(set)
    source_ids: set[str] = set()
    requirement_ids: set[str] = set()
    workstream_ids: set[str] = set()
    for row in rows:
        source_id = row["source_id"]
        requirement_id = row["requirement_id"]
        workstream_id = row["workstream_id"]
        source_ids.add(source_id)
        requirement_ids.add(requirement_id)
        workstream_ids.add(workstream_id)
        req_to_ws[requirement_id].add(workstream_id)
        ws_to_req[workstream_id].add(requirement_id)

    source_doc_paths: dict[str, Path] = {}
    for path in iter_docs(SOURCE_DOC_DIR):
        source_id = first_pattern_match(path.name, REQDOC_ID_PATTERN)
        if source_id:
            source_doc_paths[source_id] = path

    normalized_doc_paths: dict[str, Path] = {}
    normalized_doc_workstreams: dict[str, list[str]] = {}
    for path in iter_docs(NORMALIZED_REQ_DIR):
        requirement_id = first_pattern_match(
            read_prefixed_value(path, ("需求编号：",)),
            REQ_ID_PATTERN,
        )
        if not requirement_id:
            requirement_id = first_pattern_match(path.name, REQ_ID_PATTERN)
        if not requirement_id:
            continue
        normalized_doc_paths[requirement_id] = path
        normalized_doc_workstreams[requirement_id] = extract_ids_from_section(
            path,
            "## 关联工作流",
            WS_ID_PATTERN,
        )

    workstream_doc_paths: dict[str, Path] = {}
    workstream_doc_requirements: dict[str, list[str]] = {}
    for path in iter_docs(WORKSTREAM_DIR):
        workstream_id = first_pattern_match(
            read_prefixed_value(path, ("工作流编号：",)),
            WS_ID_PATTERN,
        )
        if not workstream_id:
            workstream_id = first_pattern_match(path.name, WS_ID_PATTERN)
        if not workstream_id:
            continue
        workstream_doc_paths[workstream_id] = path
        workstream_doc_requirements[workstream_id] = extract_ids_from_section(
            path,
            "## 覆盖需求",
            REQ_ID_PATTERN,
        )

    return {
        "rows": rows,
        "source_ids": source_ids,
        "requirement_ids": requirement_ids,
        "workstream_ids": workstream_ids,
        "req_to_ws": dict(req_to_ws),
        "ws_to_req": dict(ws_to_req),
        "source_doc_paths": source_doc_paths,
        "normalized_doc_paths": normalized_doc_paths,
        "normalized_doc_workstreams": normalized_doc_workstreams,
        "workstream_doc_paths": workstream_doc_paths,
        "workstream_doc_requirements": workstream_doc_requirements,
    }


def extract_known_ids(pattern: re.Pattern[str]) -> set[str]:
    catalog = load_traceability_catalog()
    if pattern.pattern == REQDOC_ID_PATTERN.pattern:
        return set(catalog["source_ids"])
    if pattern.pattern == REQ_ID_PATTERN.pattern:
        return set(catalog["requirement_ids"])
    if pattern.pattern == WS_ID_PATTERN.pattern:
        return set(catalog["workstream_ids"])
    return set()


def metadata_identifier_tokens(
    metadata: dict[str, str | list[str]],
    key: str,
    pattern: re.Pattern[str],
) -> tuple[list[str], bool]:
    value = metadata.get(key)
    if value is None:
        return [], False

    raw_values = value if isinstance(value, list) else [value]
    tokens: list[str] = []
    for raw_value in raw_values:
        stripped = raw_value.strip()
        if not stripped:
            continue
        if stripped == UNBOUND_VALUE:
            return [], True
        tokens.extend(
            token
            for token in parse_csv_values(stripped)
            if pattern.fullmatch(token)
        )
    return ordered_unique(tokens), False


def validate_requirement_workstream_pairings(
    *,
    requirement_ids: list[str],
    workstream_ids: list[str],
    owner_label: str,
    errors: list[str],
) -> None:
    if not requirement_ids or not workstream_ids:
        return

    catalog = load_traceability_catalog()
    req_to_ws: dict[str, set[str]] = catalog["req_to_ws"]  # type: ignore[assignment]
    ws_to_req: dict[str, set[str]] = catalog["ws_to_req"]  # type: ignore[assignment]

    unmatched_requirements = [
        requirement_id
        for requirement_id in requirement_ids
        if not req_to_ws.get(requirement_id, set()).intersection(workstream_ids)
    ]
    if unmatched_requirements:
        rendered = ", ".join(unmatched_requirements)
        workstreams_rendered = ", ".join(workstream_ids)
        errors.append(
            f"{owner_label} declares Requirement IDs [{rendered}] that do not map to any of its "
            f"declared Workstream IDs [{workstreams_rendered}] in "
            "docs/requirements/traceability-matrix.md."
        )

    unmatched_workstreams = [
        workstream_id
        for workstream_id in workstream_ids
        if not ws_to_req.get(workstream_id, set()).intersection(requirement_ids)
    ]
    if unmatched_workstreams:
        rendered = ", ".join(unmatched_workstreams)
        requirements_rendered = ", ".join(requirement_ids)
        errors.append(
            f"{owner_label} declares Workstream IDs [{rendered}] that do not map to any of its "
            f"declared Requirement IDs [{requirements_rendered}] in "
            "docs/requirements/traceability-matrix.md."
        )


def stage_alignment_mismatches(
    *,
    rows: list[dict[str, str]],
    requirement_ids: list[str],
    workstream_ids: list[str],
    current_stage: str,
) -> list[str]:
    normalized_stage = normalize_stage_token(current_stage)
    if not normalized_stage or not requirement_ids or not workstream_ids:
        return []

    requirement_set = set(requirement_ids)
    workstream_set = set(workstream_ids)
    mismatches: list[str] = []
    for row in rows:
        requirement_id = row.get("requirement_id", "")
        workstream_id = row.get("workstream_id", "")
        if requirement_id not in requirement_set or workstream_id not in workstream_set:
            continue
        matrix_stage = row.get("stage_token", "")
        if matrix_stage != normalized_stage:
            rendered_stage = matrix_stage or "未绑定"
            mismatches.append(f"{requirement_id}/{workstream_id}={rendered_stage}")
    return mismatches


def validate_stage_traceability_alignment(
    *,
    requirement_ids: list[str],
    workstream_ids: list[str],
    current_stage: str | None,
    owner_label: str,
    errors: list[str],
) -> None:
    if not current_stage:
        return
    normalized_stage = normalize_stage_token(current_stage)
    if not normalized_stage:
        errors.append(f"{owner_label} current stage is empty.")
        return

    catalog = load_traceability_catalog()
    rows: list[dict[str, str]] = catalog["rows"]  # type: ignore[assignment]
    mismatches = stage_alignment_mismatches(
        rows=rows,
        requirement_ids=requirement_ids,
        workstream_ids=workstream_ids,
        current_stage=normalized_stage,
    )
    if mismatches:
        rendered = ", ".join(mismatches)
        errors.append(
            f"{owner_label} declares stage {normalized_stage}, but these REQ/WS bindings have "
            f"different stages in docs/requirements/traceability-matrix.md: {rendered}"
        )


def validate_requirements_traceability_alignment(errors: list[str]) -> None:
    catalog = load_traceability_catalog()
    source_doc_paths: dict[str, Path] = catalog["source_doc_paths"]  # type: ignore[assignment]
    normalized_doc_paths: dict[str, Path] = catalog["normalized_doc_paths"]  # type: ignore[assignment]
    normalized_doc_workstreams: dict[str, list[str]] = catalog["normalized_doc_workstreams"]  # type: ignore[assignment]
    workstream_doc_paths: dict[str, Path] = catalog["workstream_doc_paths"]  # type: ignore[assignment]
    workstream_doc_requirements: dict[str, list[str]] = catalog["workstream_doc_requirements"]  # type: ignore[assignment]
    matrix_source_ids: set[str] = catalog["source_ids"]  # type: ignore[assignment]
    matrix_requirement_ids: set[str] = catalog["requirement_ids"]  # type: ignore[assignment]
    matrix_workstream_ids: set[str] = catalog["workstream_ids"]  # type: ignore[assignment]
    req_to_ws: dict[str, set[str]] = catalog["req_to_ws"]  # type: ignore[assignment]
    ws_to_req: dict[str, set[str]] = catalog["ws_to_req"]  # type: ignore[assignment]

    missing_source_docs = sorted(matrix_source_ids - set(source_doc_paths))
    if missing_source_docs:
        rendered = ", ".join(missing_source_docs)
        errors.append(
            "docs/requirements/traceability-matrix.md references source ids with no matching "
            f"source document: {rendered}"
        )

    missing_normalized_docs = sorted(matrix_requirement_ids - set(normalized_doc_paths))
    if missing_normalized_docs:
        rendered = ", ".join(missing_normalized_docs)
        errors.append(
            "docs/requirements/traceability-matrix.md references requirement ids with no matching "
            f"normalized requirement document: {rendered}"
        )

    missing_workstream_docs = sorted(matrix_workstream_ids - set(workstream_doc_paths))
    if missing_workstream_docs:
        rendered = ", ".join(missing_workstream_docs)
        errors.append(
            "docs/requirements/traceability-matrix.md references workstream ids with no matching "
            f"workstream document: {rendered}"
        )

    for requirement_id, path in sorted(normalized_doc_paths.items()):
        declared_workstreams = normalized_doc_workstreams.get(requirement_id, [])
        matrix_workstreams = sorted(req_to_ws.get(requirement_id, set()))
        if requirement_id not in matrix_requirement_ids:
            errors.append(
                f"{path.relative_to(ROOT)} declares {requirement_id}, but the requirement id is "
                "missing from docs/requirements/traceability-matrix.md."
            )
            continue
        if not declared_workstreams:
            errors.append(
                f"{path.relative_to(ROOT)} is missing bound workstreams under '## 关联工作流' "
                f"for matrix-backed requirement {requirement_id}."
            )
            continue

        invalid_workstreams = [
            workstream_id
            for workstream_id in declared_workstreams
            if workstream_id not in req_to_ws.get(requirement_id, set())
        ]
        if invalid_workstreams:
            rendered = ", ".join(invalid_workstreams)
            errors.append(
                f"{path.relative_to(ROOT)} declares workstreams not mapped from {requirement_id} "
                f"in docs/requirements/traceability-matrix.md: {rendered}"
            )

        missing_workstreams = [
            workstream_id
            for workstream_id in matrix_workstreams
            if workstream_id not in declared_workstreams
        ]
        if missing_workstreams:
            rendered = ", ".join(missing_workstreams)
            errors.append(
                f"{path.relative_to(ROOT)} omits matrix-bound workstreams for {requirement_id}: "
                f"{rendered}"
            )

    for workstream_id, path in sorted(workstream_doc_paths.items()):
        declared_requirements = workstream_doc_requirements.get(workstream_id, [])
        matrix_requirements = sorted(ws_to_req.get(workstream_id, set()))
        if workstream_id not in matrix_workstream_ids:
            errors.append(
                f"{path.relative_to(ROOT)} declares {workstream_id}, but the workstream id is "
                "missing from docs/requirements/traceability-matrix.md."
            )
            continue
        if not declared_requirements:
            errors.append(
                f"{path.relative_to(ROOT)} is missing covered requirements under '## 覆盖需求' "
                f"for matrix-backed workstream {workstream_id}."
            )
            continue

        invalid_requirements = [
            requirement_id
            for requirement_id in declared_requirements
            if requirement_id not in ws_to_req.get(workstream_id, set())
        ]
        if invalid_requirements:
            rendered = ", ".join(invalid_requirements)
            errors.append(
                f"{path.relative_to(ROOT)} declares requirements not mapped from {workstream_id} "
                f"in docs/requirements/traceability-matrix.md: {rendered}"
            )

        missing_requirements = [
            requirement_id
            for requirement_id in matrix_requirements
            if requirement_id not in declared_requirements
        ]
        if missing_requirements:
            rendered = ", ".join(missing_requirements)
            errors.append(
                f"{path.relative_to(ROOT)} omits matrix-bound requirements for {workstream_id}: "
                f"{rendered}"
            )


def validate_identifier_field(
    metadata: dict[str, str | list[str]],
    *,
    key: str,
    pattern: re.Pattern[str],
    known_ids: set[str],
    bootstrap_like: bool,
    errors: list[str],
    warnings: list[str],
    owner_label: str,
    warn_on_unbound: bool,
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
            if warn_on_unbound and known_ids and not bootstrap_like:
                warnings.append(
                    f"{owner_label} leaves '{key}' unbound even though "
                    "traceability ids already exist."
                )
            return
        tokens.extend(parse_csv_values(stripped))

    if not tokens:
        errors.append(f"{owner_label} field '{key}' is empty.")
        return

    invalid_tokens = [token for token in tokens if not pattern.fullmatch(token)]
    if invalid_tokens:
        rendered = ", ".join(sorted(set(invalid_tokens)))
        errors.append(
            f"{owner_label} field '{key}' contains malformed ids: {rendered}"
        )
        return

    unknown_ids = [token for token in tokens if token not in known_ids]
    if unknown_ids:
        rendered = ", ".join(sorted(set(unknown_ids)))
        errors.append(
            f"{owner_label} field '{key}' contains ids missing from "
            f"docs/requirements/traceability-matrix.md: {rendered}"
        )


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


def validate_working_context_sync_metadata(
    *,
    active_handoffs: list[Path],
    status_docs: list[Path],
    context_surface: ContextSurfaceConfig | None,
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
    if context_surface is not None:
        warnings.extend(
            context_surface_budget_warnings(
                count=len(bound_handoff_paths),
                label="working-context sync metadata bound handoff count",
                config=context_surface,
            )
        )

    validate_identifier_field(
        metadata,
        key="Requirement IDs",
        pattern=REQ_ID_PATTERN,
        known_ids=extract_known_ids(REQ_ID_PATTERN),
        bootstrap_like=bootstrap_like,
        errors=errors,
        warnings=warnings,
        owner_label="working-context sync metadata",
        warn_on_unbound=True,
    )
    validate_identifier_field(
        metadata,
        key="Workstream IDs",
        pattern=WS_ID_PATTERN,
        known_ids=extract_known_ids(WS_ID_PATTERN),
        bootstrap_like=bootstrap_like,
        errors=errors,
        warnings=warnings,
        owner_label="working-context sync metadata",
        warn_on_unbound=True,
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
            owner_label="working-context sync metadata",
            errors=errors,
        )
        validate_stage_traceability_alignment(
            requirement_ids=requirement_ids,
            workstream_ids=workstream_ids,
            current_stage=current_stage,
            owner_label="working-context sync metadata",
            errors=errors,
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
