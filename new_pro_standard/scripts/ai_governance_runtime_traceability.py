from __future__ import annotations

import json
import re
from pathlib import Path

from ai_governance_metadata import (
    REQ_ID_PATTERN,
    ROOT,
    WORKING_CONTEXT_PATH,
    WS_ID_PATTERN,
    load_text,
    metadata_identifier_tokens,
    normalize_stage_token,
    ordered_unique,
    parse_working_context_sync_metadata,
)
from ai_governance_traceability import load_traceability_catalog, stage_alignment_mismatches
from ai_governance_traceability_metadata import parse_traceability_metadata


RUNTIME_SESSION_DIR = ROOT / ".codex" / "runtime" / "sessions"
RUNTIME_OBSERVATION_DIR = ROOT / ".codex" / "runtime" / "observations"
RUNTIME_TRACEABILITY_SCAN_LIMIT = 20


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
