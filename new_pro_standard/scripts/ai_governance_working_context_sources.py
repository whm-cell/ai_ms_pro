from __future__ import annotations

from pathlib import Path

from harness_config import ContextSurfaceConfig

from ai_governance_metadata import (
    ACTIVE_HANDOFF_DIR,
    ROOT,
    STATUS_DIR,
    UNBOUND_VALUE,
    WORKING_CONTEXT_PATH,
    context_surface_budget_warnings,
    is_under_root,
    latest_doc,
    normalize_stage_token,
    parse_csv_values,
    read_prefixed_value,
    resolve_repo_relative_path,
    scalar_metadata_value,
)


def validate_current_stage(
    metadata: dict[str, str | list[str]],
    errors: list[str],
) -> str | None:
    document_stage = read_prefixed_value(WORKING_CONTEXT_PATH, ("当前阶段：",))
    current_stage = scalar_metadata_value(metadata, "Current Stage", errors)
    if current_stage and document_stage:
        if normalize_stage_token(current_stage) != normalize_stage_token(document_stage):
            errors.append(
                "working-context sync metadata field 'Current Stage' does not match the document "
                f"header stage: metadata={current_stage}, header={document_stage}"
            )
    return current_stage


def validate_active_status_source(
    metadata: dict[str, str | list[str]],
    *,
    status_docs: list[Path],
    bootstrap_like: bool,
    current_stage: str | None,
    errors: list[str],
    warnings: list[str],
) -> str | None:
    active_status_source = scalar_metadata_value(metadata, "Active Status Source", errors)
    if not active_status_source:
        return active_status_source
    if active_status_source == UNBOUND_VALUE:
        if status_docs and not bootstrap_like:
            warnings.append(
                "working-context sync metadata leaves 'Active Status Source' unbound even though "
                "stage status documents already exist."
            )
        return active_status_source

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
        validate_bound_status_source(active_status_path, active_status_source, current_stage, errors, warnings)
    return active_status_source


def validate_bound_status_source(
    active_status_path: Path,
    active_status_source: str,
    current_stage: str | None,
    errors: list[str],
    warnings: list[str],
) -> None:
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


def validate_active_handoff_sources(
    metadata: dict[str, str | list[str]],
    *,
    active_handoffs: list[Path],
    bootstrap_like: bool,
    errors: list[str],
    warnings: list[str],
) -> tuple[bool, list[Path]]:
    handoff_value = metadata.get("Active Handoff Sources")
    if handoff_value is None:
        return False, []
    if isinstance(handoff_value, list):
        return validate_handoff_path_values(handoff_value, errors)

    stripped = handoff_value.strip()
    if not stripped:
        errors.append("working-context sync metadata field 'Active Handoff Sources' is empty.")
        return False, []
    if stripped == UNBOUND_VALUE:
        if active_handoffs and not bootstrap_like:
            warnings.append(
                "working-context sync metadata leaves 'Active Handoff Sources' unbound even "
                "though active handoff documents already exist."
            )
        return True, []
    return validate_handoff_path_values(parse_csv_values(stripped), errors)


def validate_handoff_path_values(
    raw_paths: list[str],
    errors: list[str],
) -> tuple[bool, list[Path]]:
    cleaned = [item.strip() for item in raw_paths if item.strip()]
    if not cleaned:
        errors.append("working-context sync metadata field 'Active Handoff Sources' is empty.")
        return False, []

    bound_handoff_paths: list[Path] = []
    for raw_path in cleaned:
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
    return False, bound_handoff_paths


def validate_bound_handoff_freshness(
    bound_handoff_paths: list[Path],
    warnings: list[str],
) -> None:
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


def validate_context_surface_budget(
    *,
    bound_handoff_paths: list[Path],
    context_surface: ContextSurfaceConfig | None,
    warnings: list[str],
) -> None:
    if context_surface is None:
        return
    warnings.extend(
        context_surface_budget_warnings(
            count=len(bound_handoff_paths),
            label="working-context sync metadata bound handoff count",
            config=context_surface,
        )
    )
