#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from ai_governance_changed_paths import (
    ADR_DIR as ADR_DIR,
    DIFF_WARNING_EXCLUDE_FILES as DIFF_WARNING_EXCLUDE_FILES,
    DIFF_WARNING_EXCLUDE_ROOTS as DIFF_WARNING_EXCLUDE_ROOTS,
    DOC_ROOTS as DOC_ROOTS,
    GOVERNANCE_DOC_SYNC_WARNING_ONLY_FILES as GOVERNANCE_DOC_SYNC_WARNING_ONLY_FILES,
    GOVERNANCE_IMPLEMENTATION_FILES as GOVERNANCE_IMPLEMENTATION_FILES,
    GOVERNANCE_IMPLEMENTATION_ROOTS as GOVERNANCE_IMPLEMENTATION_ROOTS,
    RUNTIME_STATE_ROOTS as RUNTIME_STATE_ROOTS,
    has_governance_sync_docs as has_governance_sync_docs,
    is_governance_implementation_path as is_governance_implementation_path,
    is_implementation_candidate as is_implementation_candidate,
    is_runtime_state_file as is_runtime_state_file,
    load_changed_paths,
    load_ci_changed_paths as load_ci_changed_paths,
    load_staged_paths as load_staged_paths,
    requires_governance_doc_sync as requires_governance_doc_sync,
    validate_changed_path_governance_sync,
    validate_staged_runtime_state,
)
from ai_governance_metadata import (
    ACTIVE_HANDOFF_DIR as ACTIVE_HANDOFF_DIR,
    AI_DOC_ROOT as AI_DOC_ROOT,
    REQ_ID_PATTERN as REQ_ID_PATTERN,
    REQ_DOC_ROOT as REQ_DOC_ROOT,
    ROOT,
    STATUS_DIR as STATUS_DIR,
    WORKING_CONTEXT_PATH,
    WS_ID_PATTERN as WS_ID_PATTERN,
    context_surface_budget_warnings,
    extract_markdown_section as extract_markdown_section,
    is_under_root as is_under_root,
    latest_doc,
    load_text as load_text,
    metadata_identifier_tokens as metadata_identifier_tokens,
    normalize_stage_token as normalize_stage_token,
    ordered_unique as ordered_unique,
    parse_working_context_sync_metadata as parse_working_context_sync_metadata,
    split_metadata_field as split_metadata_field,
    validate_identifier_field as validate_identifier_field,
)
from ai_governance_projection import (
    PLAN_PATH as PLAN_PATH,
    PLAN_STATE_LABELS as PLAN_STATE_LABELS,
    TRACEABILITY_MATRIX_PATH as TRACEABILITY_MATRIX_PATH,
    WORKSTREAM_DIR as WORKSTREAM_DIR,
    WORKSTREAM_STATE_LABELS as WORKSTREAM_STATE_LABELS,
    find_projection_state_labels as find_projection_state_labels,
    projection_freshness_errors,
)
from ai_governance_runtime_traceability import (
    RUNTIME_OBSERVATION_DIR as RUNTIME_OBSERVATION_DIR,
    RUNTIME_SESSION_DIR as RUNTIME_SESSION_DIR,
    RUNTIME_TRACEABILITY_SCAN_LIMIT as RUNTIME_TRACEABILITY_SCAN_LIMIT,
    identifier_list_from_json as identifier_list_from_json,
    load_runtime_observation_records as load_runtime_observation_records,
    runtime_observation_traceability_records as runtime_observation_traceability_records,
    runtime_session_traceability_records as runtime_session_traceability_records,
    runtime_traceability_records as runtime_traceability_records,
    validate_runtime_traceability_artifact_alignment,
)
from ai_governance_traceability import (
    extract_known_ids as extract_known_ids,
    iter_docs,
    load_traceability_catalog as load_traceability_catalog,
    stage_alignment_mismatches as stage_alignment_mismatches,
    validate_requirement_workstream_pairings as validate_requirement_workstream_pairings,
    validate_requirements_traceability_alignment,
)
from ai_governance_traceability_metadata import (
    TRACEABILITY_METADATA_REQUIRED_KEYS as TRACEABILITY_METADATA_REQUIRED_KEYS,
    TRACEABILITY_METADATA_SECTION as TRACEABILITY_METADATA_SECTION,
    parse_traceability_metadata as parse_traceability_metadata,
    validate_traceability_metadata_doc as validate_traceability_metadata_doc,
    validate_traceability_metadata_docs,
)
from ai_governance_working_context import validate_working_context_sync_metadata
from check_context_budget import (
    build_report as build_context_budget_report,
)
from context_budget_warnings import blocking_findings as context_budget_blocking_findings
from harness_config import HarnessConfigError, load_harness_config


CHECKS = [
    ("structure", ROOT / "scripts" / "check_ai_docs.py"),
    ("quality", ROOT / "scripts" / "check_ai_doc_quality.py"),
]
ACTIVE_HANDOFF_STATUS_WARNING_THRESHOLD = 3


def load_context_surface_config() -> tuple[object | None, list[str]]:
    try:
        return load_harness_config(ROOT).context_surface, []
    except HarnessConfigError as exc:
        return None, [str(exc)]


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


def validate_context_budget_gate(errors: list[str]) -> None:
    try:
        report = build_context_budget_report(ROOT)
    except HarnessConfigError as exc:
        errors.append(str(exc))
        return

    errors.extend(context_budget_blocking_findings(report))


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
    validate_context_budget_gate(errors)

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


if __name__ == "__main__":
    raise SystemExit(main())
