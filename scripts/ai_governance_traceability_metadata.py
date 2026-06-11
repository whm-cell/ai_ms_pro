from __future__ import annotations

from pathlib import Path

from ai_governance_metadata import (
    REQ_ID_PATTERN,
    ROOT,
    WS_ID_PATTERN,
    extract_markdown_section,
    metadata_identifier_tokens,
    split_metadata_field,
    validate_identifier_field,
)
from ai_governance_traceability import (
    extract_known_ids,
    validate_requirement_workstream_pairings,
)


TRACEABILITY_METADATA_SECTION = "## 需求与工作流标识"
TRACEABILITY_METADATA_REQUIRED_KEYS = (
    "Requirement IDs",
    "Workstream IDs",
)


def parse_traceability_metadata(path: Path) -> dict[str, str]:
    metadata: dict[str, str] = {}
    for raw_line in extract_markdown_section(path, TRACEABILITY_METADATA_SECTION):
        if not raw_line.startswith("- "):
            continue
        key, value = split_metadata_field(raw_line[2:].strip())
        if key and value:
            metadata[key] = value
    return metadata


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
