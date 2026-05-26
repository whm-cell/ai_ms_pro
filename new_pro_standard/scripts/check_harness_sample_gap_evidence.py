#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from pathlib import Path
import json
import re
import sys
from typing import Any

import collect_harness_sample_gaps
from harness_sample_collection_config import SAMPLE_LEDGER


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLES = ROOT / SAMPLE_LEDGER
ID_RE = re.compile(r"^GAP-SAMPLE-\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SOURCE_TYPES = {
    "real-user-action",
    "real-workflow-run",
    "real-security-event",
    "real-workflow-task",
    "real-incident",
    "real-interop-run",
    "local-only-mechanism",
    "manual-review",
    "synthetic-regression",
}
REAL_SOURCE_TYPES = {source_type for source_type in SOURCE_TYPES if source_type.startswith("real-")}
OUTCOMES = {"accepted", "pending", "rejected"}
ENDPOINT_SCOPES = {"none", "local-capture-server", "external-test-endpoint", "hosted-service"}
REMOTE_STATUSES = {"none", "http-2xx", "http-error", "not-sent"}
FORBIDDEN_KEYS = {
    "cwd",
    "prompt",
    "prompt_preview",
    "raw_output",
    "request_body",
    "response_body",
    "transcript",
    "transcript_path",
}
MAX_TEXT = 700
MAX_LIST_ITEMS = 12


@dataclass(frozen=True)
class GapEvidenceReport:
    sample_path: str
    record_count: int
    accepted_real_sample_count: int
    accepted_by_gap: dict[str, int]
    accepted_real_by_gap: dict[str, int]
    errors: list[str]
    warnings: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate starter harness sample-gap evidence JSONL.")
    parser.add_argument("--samples", default=str(DEFAULT_SAMPLES), help="Sample-gap evidence JSONL path.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def text_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def build_report(path: Path = DEFAULT_SAMPLES) -> GapEvidenceReport:
    errors: list[str] = []
    warnings: list[str] = []
    records = load_records(path, errors)
    seen: set[str] = set()
    accepted_by_gap: dict[str, int] = {}
    accepted_real_by_gap: dict[str, int] = {}
    accepted_real = 0
    for line_no, record in records:
        validate_record(line_no, record, seen, errors, warnings)
        if text(record.get("outcome")) != "accepted":
            continue
        gap_id = text(record.get("gap_id"))
        source_type = text(record.get("source_type"))
        accepted_by_gap[gap_id] = accepted_by_gap.get(gap_id, 0) + 1
        if source_type in REAL_SOURCE_TYPES:
            accepted_real += 1
            accepted_real_by_gap[gap_id] = accepted_real_by_gap.get(gap_id, 0) + 1
    return GapEvidenceReport(
        sample_path=relative(path),
        record_count=len(records),
        accepted_real_sample_count=accepted_real,
        accepted_by_gap=accepted_by_gap,
        accepted_real_by_gap=accepted_real_by_gap,
        errors=errors,
        warnings=warnings,
    )


def load_records(path: Path, errors: list[str]) -> list[tuple[int, dict[str, Any]]]:
    if not path.exists():
        errors.append(f"sample file missing: {relative(path)}")
        return []
    records: list[tuple[int, dict[str, Any]]] = []
    for line_no, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw_line.strip():
            continue
        try:
            payload = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_no}: invalid JSON: {exc.msg}")
            continue
        if isinstance(payload, dict):
            records.append((line_no, payload))
        else:
            errors.append(f"line {line_no}: sample must be a JSON object")
    return records


def validate_record(
    line_no: int,
    record: dict[str, Any],
    seen: set[str],
    errors: list[str],
    warnings: list[str],
) -> None:
    prefix = f"line {line_no}"
    scan_for_forbidden(prefix, record, errors)
    sample_id = required_text(record, "id", prefix, errors)
    if sample_id and not ID_RE.match(sample_id):
        errors.append(f"{prefix}: id must match {ID_RE.pattern}")
    if sample_id in seen:
        errors.append(f"{prefix}: duplicate id: {sample_id}")
    seen.add(sample_id)
    if text(record.get("schema_version")) != "harness-sample-gap-evidence/v1":
        errors.append(f"{prefix}: schema_version must be harness-sample-gap-evidence/v1")
    validate_date(record, "sampled_at", prefix, errors)
    validate_choice(record, "source_type", SOURCE_TYPES, prefix, errors)
    validate_choice(record, "outcome", OUTCOMES, prefix, errors)
    validate_choice(record, "endpoint_scope", ENDPOINT_SCOPES, prefix, errors)
    validate_choice(record, "remote_status", REMOTE_STATUSES, prefix, errors)
    for field in ("local_only", "no_external_claim", "false_positive", "network_exported"):
        validate_bool(record, field, prefix, errors)
    for field in ("gap_id", "sample_summary", "decision", "boundary_note"):
        validate_bounded_text(record, field, prefix, errors)
    validate_known_gap_id(record, prefix, errors)
    for field in ("action_taken", "evidence_refs", "checker_refs"):
        validate_text_list(record, field, prefix, errors)
    validate_existing_refs(text_list(record.get("evidence_refs")), prefix, errors)
    validate_outcome_rules(record, prefix, errors, warnings)


def required_text(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> str:
    value = text(record.get(field))
    if not value:
        errors.append(f"{prefix}: {field} must be non-empty text")
    return value


def validate_bounded_text(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> None:
    value = required_text(record, field, prefix, errors)
    if len(value) > MAX_TEXT:
        errors.append(f"{prefix}: {field} exceeds {MAX_TEXT} characters")


def validate_date(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> None:
    value = required_text(record, field, prefix, errors)
    if value and not DATE_RE.match(value):
        errors.append(f"{prefix}: {field} must use YYYY-MM-DD")


def validate_choice(record: dict[str, Any], field: str, choices: set[str], prefix: str, errors: list[str]) -> None:
    value = required_text(record, field, prefix, errors)
    if value and value not in choices:
        errors.append(f"{prefix}: {field} must be one of {sorted(choices)}")


def validate_bool(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> None:
    if not isinstance(record.get(field), bool):
        errors.append(f"{prefix}: {field} must be a boolean")


def validate_known_gap_id(record: dict[str, Any], prefix: str, errors: list[str]) -> None:
    gap_id = text(record.get("gap_id"))
    known_ids = {gap.id for gap in collect_harness_sample_gaps.GAPS}
    if gap_id and gap_id not in known_ids:
        errors.append(f"{prefix}: unknown gap_id: {gap_id}")


def validate_text_list(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> None:
    values = text_list(record.get(field))
    if not values:
        errors.append(f"{prefix}: {field} must be a non-empty list")
        return
    if len(values) > MAX_LIST_ITEMS:
        errors.append(f"{prefix}: {field} has too many items")
    for value in values:
        if len(value) > MAX_TEXT:
            errors.append(f"{prefix}: {field} item exceeds {MAX_TEXT} characters")


def validate_existing_refs(values: list[str], prefix: str, errors: list[str]) -> None:
    for value in values:
        path_text = value.split("::", 1)[0].split("#", 1)[0]
        if re.search(r":\d+(?::\d+)?$", path_text):
            path_text = path_text.rsplit(":", 1)[0]
        path = Path(path_text)
        if path.is_absolute():
            errors.append(f"{prefix}: evidence_refs items must be repo-relative paths: {value}")
            continue
        resolved = (ROOT / path).resolve()
        if ROOT.resolve() not in (resolved, *resolved.parents):
            errors.append(f"{prefix}: evidence_refs item escapes repository scope: {value}")
            continue
        if not resolved.exists():
            errors.append(f"{prefix}: evidence_refs item does not exist: {value}")


def validate_outcome_rules(record: dict[str, Any], prefix: str, errors: list[str], warnings: list[str]) -> None:
    accepted = text(record.get("outcome")) == "accepted"
    source_type = text(record.get("source_type"))
    if source_type == "synthetic-regression":
        warnings.append(f"{prefix}: synthetic samples are regression fixtures only")
        if accepted:
            errors.append(f"{prefix}: synthetic samples must not be accepted as real evidence")
    if accepted and source_type not in REAL_SOURCE_TYPES:
        errors.append(f"{prefix}: accepted starter samples must use a real-* source_type")
    if accepted and record.get("no_external_claim") is not True:
        errors.append(f"{prefix}: accepted samples must set no_external_claim=true")
    if text(record.get("gap_id")) == "GAP-STARTER-REMOTE-INTEROP":
        validate_remote_interop(record, prefix, errors)


def validate_remote_interop(record: dict[str, Any], prefix: str, errors: list[str]) -> None:
    if text(record.get("source_type")) != "real-interop-run":
        errors.append(f"{prefix}: remote interop samples need source_type=real-interop-run")
    if record.get("local_only") is not False:
        errors.append(f"{prefix}: remote interop samples must set local_only=false")
    if text(record.get("endpoint_scope")) not in {"external-test-endpoint", "hosted-service"}:
        errors.append(f"{prefix}: remote interop samples need an external-test-endpoint or hosted-service scope")
    if record.get("network_exported") is True and text(record.get("remote_status")) not in {"http-2xx", "http-error"}:
        errors.append(f"{prefix}: exported remote interop samples must record http-2xx or http-error")


def scan_for_forbidden(prefix: str, value: Any, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            if key_text in FORBIDDEN_KEYS:
                errors.append(f"{prefix}: forbidden raw context key: {key_text}")
            scan_for_forbidden(prefix, child, errors)
    elif isinstance(value, list):
        for child in value:
            scan_for_forbidden(prefix, child, errors)
    elif isinstance(value, str) and ".codex/runtime/" in value.replace("\\", "/"):
        errors.append(f"{prefix}: shared samples must not reference local runtime material")


def emit_text(report: GapEvidenceReport) -> None:
    print("Harness sample-gap evidence audit:")
    print(f"- samples: {report.sample_path}")
    print(f"- records: {report.record_count}")
    print(f"- accepted real samples: {report.accepted_real_sample_count}")
    print(f"- accepted by gap: {report.accepted_by_gap}")
    for warning in report.warnings:
        print(f"WARN: {warning}")
    if report.errors:
        for error in report.errors:
            print(f"ERROR: {error}")
    else:
        print("ERRORS: none")


def main() -> int:
    args = parse_args()
    report = build_report(Path(args.samples).expanduser())
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        emit_text(report)
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
