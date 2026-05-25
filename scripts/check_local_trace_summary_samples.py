#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys
from typing import Any

import evidence_ref_utils


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLES = ROOT / "docs" / "ai" / "standards" / "local-trace-summary-samples.jsonl"
ID_RE = re.compile(r"^TRACE-SUMMARY-SAMPLE-\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SOURCE_TYPES = {"real-local-report", "synthetic-regression", "manual-review"}
OUTCOMES = {"accepted", "pending", "rejected"}
SUMMARY_FORMATS = {"markdown", "json"}
REDACTION_STATES = {"redacted", "not_applicable", "unset", "unknown"}
FORBIDDEN_KEYS = {"cwd", "prompt", "prompt_preview", "promptPreview", "raw_output", "rawOutput", "transcript", "transcript_path", "transcriptPath"}
TASK_CLASS_PLACEHOLDERS = {"tbd", "unknown", "none", "n/a", "na"}
MAX_TEXT = 600
MAX_LIST_ITEMS = 12


@dataclass(frozen=True)
class LocalTraceSummarySampleReport:
    sample_path: str
    record_count: int
    real_report_count: int
    accepted_real_report_count: int
    accepted_real_task_classes: dict[str, int]
    accepted_real_task_class_count: int
    false_positive_count: int
    errors: list[str]
    warnings: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Local Trace Summary burn-in samples.")
    parser.add_argument("--samples", default=str(DEFAULT_SAMPLES), help="Local trace summary sample JSONL path.")
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


def int_value(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def task_class(record: dict[str, Any]) -> str:
    return text(record.get("task_class"))


def countable_task_class(value: str) -> bool:
    return bool(value) and value.lower() not in TASK_CLASS_PLACEHOLDERS


def build_report(path: Path = DEFAULT_SAMPLES) -> LocalTraceSummarySampleReport:
    errors: list[str] = []
    warnings: list[str] = []
    records = load_records(path, errors)
    seen_ids: set[str] = set()
    real_count = 0
    accepted_count = 0
    accepted_task_classes: dict[str, int] = {}
    false_positive_count = 0
    for line_no, record in records:
        validate_record(line_no, record, seen_ids, errors, warnings)
        if text(record.get("source_type")) == "real-local-report":
            real_count += 1
        if text(record.get("source_type")) == "real-local-report" and text(record.get("outcome")) == "accepted":
            accepted_count += 1
            sample_task_class = task_class(record)
            if countable_task_class(sample_task_class):
                accepted_task_classes[sample_task_class] = accepted_task_classes.get(sample_task_class, 0) + 1
        if record.get("false_positive") is True:
            false_positive_count += 1
    if accepted_count == 0:
        warnings.append("no accepted real local trace summary report sample recorded yet")
    elif not accepted_task_classes:
        warnings.append("no accepted real local trace summary task class recorded yet")
    return LocalTraceSummarySampleReport(
        relative(path),
        len(records),
        real_count,
        accepted_count,
        dict(sorted(accepted_task_classes.items())),
        len(accepted_task_classes),
        false_positive_count,
        errors,
        warnings,
    )


def load_records(path: Path, errors: list[str]) -> list[tuple[int, dict[str, Any]]]:
    if not path.exists():
        errors.append(f"sample file missing: {relative(path)}")
        return []
    records: list[tuple[int, dict[str, Any]]] = []
    for line_no, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw_line.strip():
            errors.append(f"line {line_no}: blank line is not allowed")
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
    seen_ids: set[str],
    errors: list[str],
    warnings: list[str],
) -> None:
    prefix = f"line {line_no}"
    scan_for_forbidden_runtime(prefix, record, errors)
    sample_id = required_text(record, "id", prefix, errors)
    if sample_id and not ID_RE.match(sample_id):
        errors.append(f"{prefix}: id must match {ID_RE.pattern}")
    if sample_id in seen_ids:
        errors.append(f"{prefix}: duplicate id: {sample_id}")
    seen_ids.add(sample_id)
    if text(record.get("schema_version")) != "local-trace-summary-sample/v1":
        errors.append(f"{prefix}: schema_version must be local-trace-summary-sample/v1")
    validate_date(record, "sampled_at", prefix, errors)
    validate_choice(record, "source_type", SOURCE_TYPES, prefix, errors)
    validate_choice(record, "outcome", OUTCOMES, prefix, errors)
    validate_choice(record, "summary_format", SUMMARY_FORMATS, prefix, errors)
    validate_bool(record, "no_network", prefix, errors)
    validate_bool(record, "local_only", prefix, errors)
    validate_bool(record, "false_positive", prefix, errors)
    validate_task_class(record, prefix, errors)
    for field in ("task_summary", "note"):
        validate_bounded_required_text(record, field, prefix, errors)
    for field in ("observation_count", "trace_record_count", "trace_count", "promotion_needed_count", "warning_count"):
        validate_count(record, field, prefix, errors)
    validate_text_list(record, "key_findings", prefix, errors)
    validate_text_list(record, "action_taken", prefix, errors)
    evidence_refs = validate_text_list(record, "evidence_refs", prefix, errors)
    evidence_ref_utils.validate_existing_repo_relative_refs(
        evidence_refs,
        ROOT,
        "evidence_refs",
        prefix,
        errors,
        allow_selectors=True,
    )
    validate_redaction_states(record, prefix, errors)
    validate_outcome_rules(record, prefix, errors, warnings)


def required_text(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> str:
    value = text(record.get(field))
    if not value:
        errors.append(f"{prefix}: {field} must be non-empty text")
    return value


def validate_bounded_required_text(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> None:
    value = required_text(record, field, prefix, errors)
    if len(value) > MAX_TEXT:
        errors.append(f"{prefix}: {field} exceeds {MAX_TEXT} characters")


def validate_date(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> None:
    value = required_text(record, field, prefix, errors)
    if value and not DATE_RE.match(value):
        errors.append(f"{prefix}: {field} must use YYYY-MM-DD")


def validate_choice(
    record: dict[str, Any],
    field: str,
    choices: set[str],
    prefix: str,
    errors: list[str],
) -> None:
    value = required_text(record, field, prefix, errors)
    if value and value not in choices:
        errors.append(f"{prefix}: {field} must be one of {sorted(choices)}")


def validate_bool(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> None:
    if not isinstance(record.get(field), bool):
        errors.append(f"{prefix}: {field} must be a boolean")


def validate_count(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> None:
    value = int_value(record.get(field))
    if value is None or value < 0:
        errors.append(f"{prefix}: {field} must be a non-negative integer")


def validate_task_class(record: dict[str, Any], prefix: str, errors: list[str]) -> None:
    value = task_class(record)
    if text(record.get("source_type")) == "real-local-report":
        if not value:
            errors.append(f"{prefix}: task_class must be non-empty text for real-local-report samples")
            return
        if len(value) > MAX_TEXT:
            errors.append(f"{prefix}: task_class exceeds {MAX_TEXT} characters")
        if text(record.get("outcome")) == "accepted" and not countable_task_class(value):
            errors.append(f"{prefix}: accepted real-local-report samples must use a concrete task_class")
        return
    if value and len(value) > MAX_TEXT:
        errors.append(f"{prefix}: task_class exceeds {MAX_TEXT} characters")


def validate_text_list(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> list[str]:
    values = text_list(record.get(field))
    if not values:
        errors.append(f"{prefix}: {field} must be a non-empty list")
        return []
    if len(values) > MAX_LIST_ITEMS:
        errors.append(f"{prefix}: {field} has too many items")
    for value in values:
        if len(value) > MAX_TEXT:
            errors.append(f"{prefix}: {field} item exceeds {MAX_TEXT} characters")
    return values


def validate_redaction_states(record: dict[str, Any], prefix: str, errors: list[str]) -> None:
    states = validate_text_list(record, "redaction_states", prefix, errors)
    invalid = [state for state in states if state not in REDACTION_STATES]
    if invalid:
        errors.append(f"{prefix}: redaction_states has invalid values: {', '.join(invalid)}")


def validate_outcome_rules(record: dict[str, Any], prefix: str, errors: list[str], warnings: list[str]) -> None:
    outcome = text(record.get("outcome"))
    source_type = text(record.get("source_type"))
    accepted = outcome == "accepted"
    if source_type == "synthetic-regression" and accepted:
        warnings.append(f"{prefix}: synthetic samples do not count as real local trace summary burn-in evidence")
    if accepted and (record.get("no_network") is not True or record.get("local_only") is not True):
        errors.append(f"{prefix}: accepted samples must set no_network=true and local_only=true")
    if accepted and text_list(record.get("evidence_refs")) == ["none"]:
        errors.append(f"{prefix}: accepted samples need evidence_refs")
    if accepted and text_list(record.get("key_findings")) == ["none"]:
        errors.append(f"{prefix}: accepted samples need key_findings")


def scan_for_forbidden_runtime(prefix: str, value: Any, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            if key_text in FORBIDDEN_KEYS:
                errors.append(f"{prefix}: forbidden raw runtime key: {key_text}")
            scan_for_forbidden_runtime(prefix, child, errors)
    elif isinstance(value, list):
        for child in value:
            scan_for_forbidden_runtime(prefix, child, errors)
    elif isinstance(value, str) and ".codex/runtime/" in value.replace("\\", "/"):
        errors.append(f"{prefix}: shared samples must not reference local runtime material")


def emit_text(report: LocalTraceSummarySampleReport) -> None:
    print("Local trace summary sample audit:")
    print(f"- samples: {report.sample_path}")
    print(f"- records: {report.record_count}")
    print(f"- real reports: {report.real_report_count}")
    print(f"- accepted real reports: {report.accepted_real_report_count}")
    print(f"- accepted real task classes: {report.accepted_real_task_class_count}")
    if report.accepted_real_task_classes:
        task_class_summary = ", ".join(
            f"{sample_task_class}={count}" for sample_task_class, count in report.accepted_real_task_classes.items()
        )
        print(f"- task classes: {task_class_summary}")
    print(f"- false positives: {report.false_positive_count}")
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
