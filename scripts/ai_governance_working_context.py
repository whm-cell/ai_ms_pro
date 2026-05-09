from __future__ import annotations

from datetime import date
from pathlib import Path

from ai_governance_traceability import (
    extract_known_ids,
    validate_requirement_workstream_pairings,
    validate_stage_traceability_alignment,
)
from harness_config import ContextSurfaceConfig

from ai_governance_metadata import (
    PLACEHOLDER_DATE,
    REQ_ID_PATTERN,
    SYNC_ALLOWED_SOURCE_TOKENS,
    SYNC_METADATA_REQUIRED_KEYS,
    SYNC_METADATA_SECTION,
    UNBOUND_VALUE,
    WORKING_CONTEXT_PATH,
    WS_ID_PATTERN,
    metadata_identifier_tokens,
    parse_working_context_sync_metadata,
    read_prefixed_value,
    scalar_metadata_value,
    validate_identifier_field,
)
from ai_governance_working_context_sources import (
    validate_active_handoff_sources,
    validate_active_status_source,
    validate_bound_handoff_freshness,
    validate_context_surface_budget,
    validate_current_stage,
)


def validate_required_sync_metadata(
    metadata: dict[str, str | list[str]],
    errors: list[str],
) -> None:
    for key in SYNC_METADATA_REQUIRED_KEYS:
        if key not in metadata:
            errors.append(
                "working-context.md is missing required sync metadata field "
                f"'{key}' under {SYNC_METADATA_SECTION}."
            )


def validate_working_context_identifiers(
    metadata: dict[str, str | list[str]],
    *,
    bootstrap_like: bool,
    current_stage: str | None,
    errors: list[str],
    warnings: list[str],
) -> None:
    for key, pattern in (("Requirement IDs", REQ_ID_PATTERN), ("Workstream IDs", WS_ID_PATTERN)):
        validate_identifier_field(
            metadata,
            key=key,
            pattern=pattern,
            known_ids=extract_known_ids(pattern),
            bootstrap_like=bootstrap_like,
            errors=errors,
            warnings=warnings,
            owner_label="working-context sync metadata",
            warn_on_unbound=True,
        )
    validate_working_context_identifier_pairings(metadata, current_stage, errors)


def validate_working_context_identifier_pairings(
    metadata: dict[str, str | list[str]],
    current_stage: str | None,
    errors: list[str],
) -> None:
    requirement_ids, requirements_unbound = metadata_identifier_tokens(metadata, "Requirement IDs", REQ_ID_PATTERN)
    workstream_ids, workstreams_unbound = metadata_identifier_tokens(metadata, "Workstream IDs", WS_ID_PATTERN)
    if requirements_unbound or workstreams_unbound:
        return
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


def validate_last_synced_from(
    metadata: dict[str, str | list[str]],
    *,
    active_status_source: str | None,
    handoff_unbound: bool,
    errors: list[str],
) -> None:
    last_synced_from = scalar_metadata_value(metadata, "Last Synced From", errors)
    if not last_synced_from:
        return
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


def validate_last_synced_at(
    metadata: dict[str, str | list[str]],
    errors: list[str],
) -> None:
    document_updated_at = read_prefixed_value(WORKING_CONTEXT_PATH, ("更新时间：",))
    last_synced_at = scalar_metadata_value(metadata, "Last Synced At", errors)
    if not last_synced_at:
        return
    validate_last_synced_at_value(last_synced_at, document_updated_at, errors)


def validate_last_synced_at_value(
    last_synced_at: str,
    document_updated_at: str | None,
    errors: list[str],
) -> None:
    if last_synced_at == PLACEHOLDER_DATE:
        errors.append(
            "working-context sync metadata field 'Last Synced At' still uses the starter "
            "placeholder outside bootstrap state."
        )
    else:
        try:
            date.fromisoformat(last_synced_at)
        except ValueError:
            errors.append("working-context sync metadata field 'Last Synced At' must use YYYY-MM-DD.")
    if document_updated_at:
        validate_last_synced_header_alignment(last_synced_at, document_updated_at, errors)


def validate_last_synced_header_alignment(
    last_synced_at: str,
    document_updated_at: str,
    errors: list[str],
) -> None:
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
    bootstrap_like = not active_handoffs and not status_docs
    validate_required_sync_metadata(metadata, errors)
    current_stage = validate_current_stage(metadata, errors)
    active_status_source = validate_active_status_source(
        metadata,
        status_docs=status_docs,
        bootstrap_like=bootstrap_like,
        current_stage=current_stage,
        errors=errors,
        warnings=warnings,
    )
    handoff_unbound, bound_handoff_paths = validate_active_handoff_sources(
        metadata,
        active_handoffs=active_handoffs,
        bootstrap_like=bootstrap_like,
        errors=errors,
        warnings=warnings,
    )
    validate_bound_handoff_freshness(bound_handoff_paths, warnings)
    validate_context_surface_budget(
        bound_handoff_paths=bound_handoff_paths,
        context_surface=context_surface,
        warnings=warnings,
    )
    validate_working_context_identifiers(
        metadata,
        bootstrap_like=bootstrap_like,
        current_stage=current_stage,
        errors=errors,
        warnings=warnings,
    )
    validate_last_synced_from(
        metadata,
        active_status_source=active_status_source,
        handoff_unbound=handoff_unbound,
        errors=errors,
    )
    validate_last_synced_at(metadata, errors)
    return errors, warnings
