from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import check_agent_trace_schema


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class TraceEvidence:
    schema_version: str
    producer: str
    required_event: str
    grade: str
    matched_records: int
    trace_ids: list[str]
    trace_artifacts: list[str]
    redaction_states: list[str]
    errors: list[str]


def collect_trace_evidence(value: object, *, dry_run: bool) -> TraceEvidence | None:
    if not isinstance(value, dict):
        return None
    artifacts = [str(item) for item in value.get("evidence_artifacts", []) if isinstance(item, str)]
    if dry_run:
        return build_trace_evidence(value, artifacts, [], [], [], grade="not-run")

    paths = resolve_trace_artifacts(artifacts)
    errors: list[str] = []
    matched_records: list[dict[str, Any]] = []
    matched_artifacts: set[str] = set()
    for path in paths:
        validation_errors = check_agent_trace_schema.validate_trace(check_agent_trace_schema.DEFAULT_SCHEMA, path)
        if validation_errors:
            errors.extend(f"{relative(path)}: {error}" for error in validation_errors)
            continue
        for record in check_agent_trace_schema.load_jsonl(path):
            if trace_record_matches(record, value):
                matched_records.append(record)
                matched_artifacts.add(relative(path))
    if not paths:
        errors.append("no trace evidence artifacts matched")
    if not matched_records and not errors:
        errors.append("no trace records matched trace_expectations")

    return build_trace_evidence(
        value,
        sorted(matched_artifacts),
        matched_records,
        errors,
        sorted({str(record["redaction"]["state"]) for record in matched_records}),
        grade="fail" if errors else "pass",
    )


def build_trace_evidence(
    value: dict[str, Any],
    artifacts: list[str],
    records: list[dict[str, Any]],
    errors: list[str],
    redaction_states: list[str],
    *,
    grade: str,
) -> TraceEvidence:
    return TraceEvidence(
        schema_version=str(value.get("schema_version", "")),
        producer=str(value.get("producer", "")),
        required_event=str(value.get("required_event", "")),
        grade=grade,
        matched_records=len(records),
        trace_ids=sorted({str(record["trace_id"]) for record in records}),
        trace_artifacts=artifacts,
        redaction_states=redaction_states,
        errors=errors,
    )


def resolve_trace_artifacts(artifacts: list[str]) -> list[Path]:
    paths: list[Path] = []
    for artifact in artifacts:
        if any(char in artifact for char in "*?[]"):
            paths.extend(sorted(ROOT.glob(artifact)))
            continue
        path = ROOT / artifact
        if path.exists():
            paths.append(path)
    return sorted(set(paths))


def trace_record_matches(record: dict[str, Any], expectations: dict[str, Any]) -> bool:
    attributes = record.get("attributes", {})
    required_attributes = {str(item) for item in expectations.get("required_attributes", [])}
    return (
        record.get("schema_version") == expectations.get("schema_version")
        and record.get("event") == expectations.get("required_event")
        and record.get("kind") in expectations.get("required_kinds", [])
        and record.get("redaction", {}).get("state") in expectations.get("required_redaction_states", [])
        and required_attributes.issubset(set(attributes))
    )


def relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()
