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
DEFAULT_SAMPLES = ROOT / "docs" / "ai" / "standards" / "loop-scope-monitor-samples.jsonl"
ID_RE = re.compile(r"^LOOP-SAMPLE-\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SOURCE_TYPES = {"real-session", "synthetic-regression", "manual-review"}
OUTCOMES = {"accepted", "pending", "rejected"}
FINDING_CODES = {"repeated-command", "repeated-failure", "validation-loop", "prompt-churn", "none"}
RECOMMENDATIONS = {
    "checkpoint",
    "inspect-repeated-command",
    "narrow-task",
    "new-session",
    "shrink-validation",
    "none",
}
FORBIDDEN_KEYS = {
    "cwd",
    "prompt",
    "prompt_preview",
    "promptPreview",
    "raw_output",
    "rawOutput",
    "transcript",
    "transcript_path",
    "transcriptPath",
}
MAX_TEXT = 600
MAX_LIST_ITEMS = 12


@dataclass(frozen=True)
class LoopScopeSampleReport:
    sample_path: str
    record_count: int
    real_sample_count: int
    accepted_real_sample_count: int
    accepted_warning_sample_count: int
    false_positive_count: int
    errors: list[str]
    warnings: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate loop/scope monitor burn-in samples.")
    parser.add_argument("--samples", default=str(DEFAULT_SAMPLES), help="Loop/scope sample JSONL path.")
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


def build_report(path: Path = DEFAULT_SAMPLES) -> LoopScopeSampleReport:
    errors: list[str] = []
    warnings: list[str] = []
    records = load_records(path, errors)
    seen_ids: set[str] = set()
    real_count = 0
    accepted_real_count = 0
    accepted_warning_count = 0
    false_positive_count = 0
    for line_no, record in records:
        validate_record(line_no, record, seen_ids, errors, warnings)
        source_type = text(record.get("source_type"))
        outcome = text(record.get("outcome"))
        findings = text_list(record.get("triggered_findings"))
        if source_type == "real-session":
            real_count += 1
        if source_type == "real-session" and outcome == "accepted":
            accepted_real_count += 1
            if findings != ["none"]:
                accepted_warning_count += 1
        if record.get("false_positive") is True:
            false_positive_count += 1
    if accepted_warning_count == 0:
        warnings.append("no accepted real warning sample recorded yet")
    return LoopScopeSampleReport(
        relative(path),
        len(records),
        real_count,
        accepted_real_count,
        accepted_warning_count,
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
    if text(record.get("schema_version")) != "loop-scope-monitor-sample/v1":
        errors.append(f"{prefix}: schema_version must be loop-scope-monitor-sample/v1")
    validate_date(record, "sampled_at", prefix, errors)
    validate_choice(record, "source_type", SOURCE_TYPES, prefix, errors)
    validate_choice(record, "outcome", OUTCOMES, prefix, errors)
    validate_bounded_required_text(record, "task_summary", prefix, errors)
    validate_bounded_required_text(record, "note", prefix, errors)
    validate_bool(record, "false_positive", prefix, errors)
    validate_list_choices(record, "triggered_findings", FINDING_CODES, prefix, errors)
    validate_list_choices(record, "monitor_recommendations", RECOMMENDATIONS, prefix, errors)
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


def validate_list_choices(
    record: dict[str, Any],
    field: str,
    choices: set[str],
    prefix: str,
    errors: list[str],
) -> None:
    values = validate_text_list(record, field, prefix, errors)
    invalid = [value for value in values if value not in choices]
    if invalid:
        errors.append(f"{prefix}: {field} has invalid values: {', '.join(invalid)}")
    if "none" in values and len(values) > 1:
        errors.append(f"{prefix}: {field} cannot mix none with other values")


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


def validate_outcome_rules(
    record: dict[str, Any],
    prefix: str,
    errors: list[str],
    warnings: list[str],
) -> None:
    outcome = text(record.get("outcome"))
    source_type = text(record.get("source_type"))
    action_taken = text_list(record.get("action_taken"))
    evidence_refs = text_list(record.get("evidence_refs"))
    if outcome == "accepted" and (not action_taken or action_taken == ["none"]):
        errors.append(f"{prefix}: accepted samples need action_taken")
    if outcome == "accepted" and (not evidence_refs or evidence_refs == ["none"]):
        errors.append(f"{prefix}: accepted samples need evidence_refs")
    if source_type == "synthetic-regression" and outcome == "accepted":
        warnings.append(f"{prefix}: synthetic samples do not count as real burn-in evidence")


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


def emit_text(report: LoopScopeSampleReport) -> None:
    print("Loop/scope monitor sample audit:")
    print(f"- samples: {report.sample_path}")
    print(f"- records: {report.record_count}")
    print(f"- real samples: {report.real_sample_count}")
    print(f"- accepted real samples: {report.accepted_real_sample_count}")
    print(f"- accepted real warning samples: {report.accepted_warning_sample_count}")
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
