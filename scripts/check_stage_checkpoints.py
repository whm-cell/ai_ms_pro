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
DEFAULT_CHECKPOINTS = ROOT / "docs" / "ai" / "checkpoints" / "stage-checkpoints.jsonl"
DEFAULT_SAMPLES = ROOT / "docs" / "ai" / "checkpoints" / "resume-samples.jsonl"
ID_RE = re.compile(r"^CP-\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*$")
SAMPLE_ID_RE = re.compile(r"^CP-SAMPLE-\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*$")
STAGE_RE = re.compile(r"^STAGE-\d{2}[A-Z]?$")
REQ_RE = re.compile(r"^REQ-\d{3}$")
WS_RE = re.compile(r"^WS-\d{2}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
STATUSES = {"planned", "in_progress", "blocked", "complete", "superseded"}
EVIDENCE_STATUSES = {"pending", "passed", "failed", "not_applicable"}
SAMPLE_OUTCOMES = {"accepted", "pending", "rejected"}
RESUME_SCOPES = {"same-task", "cross-task"}
FORBIDDEN_KEYS = {"prompt", "prompt_preview", "transcript", "transcript_path", "cwd", "raw_output"}
MAX_TEXT = 600
MAX_LIST_ITEMS = 12

@dataclass(frozen=True)
class CheckpointReport:
    checkpoint_path: str
    record_count: int
    sample_path: str
    sample_count: int
    accepted_sample_count: int
    accepted_cross_task_sample_count: int
    errors: list[str]
    warnings: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate durable stage checkpoint artifacts.")
    parser.add_argument("--checkpoints", default=str(DEFAULT_CHECKPOINTS), help="Checkpoint JSONL path.")
    parser.add_argument("--samples", help="Resume sample JSONL path. Defaults to repo checkpoint samples.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()

def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()

def normalize_path(value: str) -> str:
    normalized = value.strip().replace("\\", "/")
    root = ROOT.as_posix().rstrip("/") + "/"
    if normalized.startswith(root):
        normalized = normalized[len(root) :]
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized

def text(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""

def text_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]

def build_report(path: Path = DEFAULT_CHECKPOINTS, sample_path: Path | None = None) -> CheckpointReport:
    errors: list[str] = []
    warnings: list[str] = []
    records = load_records(path, errors)
    seen_ids: set[str] = set()
    checkpoint_ids: set[str] = set()
    for line_no, record in records:
        validate_record(line_no, record, seen_ids, errors, warnings)
        checkpoint_id = text(record.get("id"))
        if checkpoint_id:
            checkpoint_ids.add(checkpoint_id)
    resolved_sample_path = sample_path or default_sample_path(path)
    sample_count = 0
    accepted_sample_count = 0
    accepted_cross_task_sample_count = 0
    if resolved_sample_path is not None:
        samples = load_records(resolved_sample_path, errors, label="resume sample")
        sample_count = len(samples)
        accepted_sample_count, accepted_cross_task_sample_count = validate_samples(samples, checkpoint_ids, errors, warnings)
        if accepted_sample_count and accepted_cross_task_sample_count == 0:
            warnings.append("no accepted cross-task resume sample recorded yet")
    return CheckpointReport(
        relative(path),
        len(records),
        relative(resolved_sample_path) if resolved_sample_path else "",
        sample_count,
        accepted_sample_count,
        accepted_cross_task_sample_count,
        errors,
        warnings,
    )

def default_sample_path(path: Path) -> Path | None:
    if path.resolve() == DEFAULT_CHECKPOINTS.resolve():
        return DEFAULT_SAMPLES
    return None

def load_records(path: Path, errors: list[str], *, label: str = "checkpoint") -> list[tuple[int, dict[str, Any]]]:
    if not path.exists():
        errors.append(f"{label} file missing: {relative(path)}")
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
            errors.append(f"line {line_no}: {label} must be a JSON object")
    return records

def validate_record(
    line_no: int,
    record: dict[str, Any],
    seen_ids: set[str],
    errors: list[str],
    warnings: list[str],
) -> None:
    prefix = f"line {line_no}"
    scan_for_forbidden_keys(prefix, record, errors)
    checkpoint_id = required_text(record, "id", prefix, errors)
    if checkpoint_id and not ID_RE.match(checkpoint_id):
        errors.append(f"{prefix}: id must match {ID_RE.pattern}")
    if checkpoint_id in seen_ids:
        errors.append(f"{prefix}: duplicate id: {checkpoint_id}")
    seen_ids.add(checkpoint_id)
    if text(record.get("schema_version")) != "stage-checkpoint/v1":
        errors.append(f"{prefix}: schema_version must be stage-checkpoint/v1")
    stage = required_text(record, "stage", prefix, errors)
    if stage and not STAGE_RE.match(stage):
        errors.append(f"{prefix}: stage must match {STAGE_RE.pattern}")
    status = required_text(record, "status", prefix, errors)
    if status and status not in STATUSES:
        errors.append(f"{prefix}: status must be one of {sorted(STATUSES)}")
    validate_date(record, "updated_at", prefix, errors)
    for field in ("goal", "owner_surface", "resume_prompt", "next_action"):
        validate_bounded_required_text(record, field, prefix, errors)
    validate_ids(record, "requirement_ids", REQ_RE, prefix, errors)
    validate_ids(record, "workstream_ids", WS_RE, prefix, errors)
    validate_artifact_paths(record, prefix, errors, warnings)
    validate_evidence(record, prefix, errors)
    validate_status_rules(record, prefix, errors)

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

def validate_ids(record: dict[str, Any], field: str, pattern: re.Pattern[str], prefix: str, errors: list[str]) -> None:
    values = text_list(record.get(field))
    if len(values) > MAX_LIST_ITEMS:
        errors.append(f"{prefix}: {field} has too many items")
    invalid = [value for value in values if value != "未绑定" and not pattern.match(value)]
    if invalid:
        errors.append(f"{prefix}: {field} has invalid ids: {', '.join(invalid)}")

def validate_artifact_paths(
    record: dict[str, Any],
    prefix: str,
    errors: list[str],
    warnings: list[str],
) -> None:
    values = text_list(record.get("artifact_paths"))
    if not values:
        errors.append(f"{prefix}: artifact_paths must be a non-empty list")
        return
    if len(values) > MAX_LIST_ITEMS:
        errors.append(f"{prefix}: artifact_paths has too many items")
    for raw_path in values:
        path = normalize_path(raw_path)
        if path.startswith(".codex/runtime/"):
            errors.append(f"{prefix}: artifact_paths must not point at local runtime material: {path}")
        if path.startswith("/") or ".." in Path(path).parts:
            errors.append(f"{prefix}: artifact_paths must be repo-relative: {raw_path}")
        if not (ROOT / path).exists():
            warnings.append(f"{prefix}: artifact path does not exist yet: {path}")

def validate_evidence(record: dict[str, Any], prefix: str, errors: list[str]) -> None:
    evidence = record.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        errors.append(f"{prefix}: evidence must be a non-empty list")
        return
    if len(evidence) > MAX_LIST_ITEMS:
        errors.append(f"{prefix}: evidence has too many items")
    for index, item in enumerate(evidence, 1):
        item_prefix = f"{prefix} evidence {index}"
        if not isinstance(item, dict):
            errors.append(f"{item_prefix}: item must be an object")
            continue
        for field in ("kind", "ref", "status", "note"):
            validate_bounded_required_text(item, field, item_prefix, errors)
        status = text(item.get("status"))
        if status and status not in EVIDENCE_STATUSES:
            errors.append(f"{item_prefix}: status must be one of {sorted(EVIDENCE_STATUSES)}")

def validate_status_rules(record: dict[str, Any], prefix: str, errors: list[str]) -> None:
    status = text(record.get("status"))
    evidence_statuses = [text(item.get("status")) for item in record.get("evidence", []) if isinstance(item, dict)]
    if status == "complete" and not evidence_statuses:
        errors.append(f"{prefix}: complete checkpoints need evidence")
    if status == "complete" and any(value in {"pending", "failed"} for value in evidence_statuses):
        errors.append(f"{prefix}: complete checkpoints cannot have pending or failed evidence")
    if status in {"planned", "in_progress", "blocked"} and not text(record.get("next_action")):
        errors.append(f"{prefix}: active checkpoints need next_action")

def validate_samples(
    samples: list[tuple[int, dict[str, Any]]],
    checkpoint_ids: set[str],
    errors: list[str],
    warnings: list[str],
) -> tuple[int, int]:
    seen_ids: set[str] = set()
    accepted = 0
    accepted_cross_task = 0
    for line_no, sample in samples:
        prefix = f"sample line {line_no}"
        scan_for_forbidden_keys(prefix, sample, errors)
        sample_id = required_text(sample, "id", prefix, errors)
        if sample_id and not SAMPLE_ID_RE.match(sample_id):
            errors.append(f"{prefix}: id must match {SAMPLE_ID_RE.pattern}")
        if sample_id in seen_ids:
            errors.append(f"{prefix}: duplicate id: {sample_id}")
        seen_ids.add(sample_id)
        if text(sample.get("schema_version")) != "stage-checkpoint-resume-sample/v1":
            errors.append(f"{prefix}: schema_version must be stage-checkpoint-resume-sample/v1")
        checkpoint_id = required_text(sample, "checkpoint_id", prefix, errors)
        if checkpoint_id and checkpoint_id not in checkpoint_ids:
            errors.append(f"{prefix}: unknown checkpoint_id: {checkpoint_id}")
        outcome = required_text(sample, "outcome", prefix, errors)
        if outcome and outcome not in SAMPLE_OUTCOMES:
            errors.append(f"{prefix}: outcome must be one of {sorted(SAMPLE_OUTCOMES)}")
        resume_scope = required_text(sample, "resume_scope", prefix, errors)
        if resume_scope and resume_scope not in RESUME_SCOPES:
            errors.append(f"{prefix}: resume_scope must be one of {sorted(RESUME_SCOPES)}")
        if outcome == "accepted":
            accepted += 1
            if resume_scope == "cross-task":
                accepted_cross_task += 1
        validate_date(sample, "resumed_at", prefix, errors)
        validate_sample_text_fields(sample, prefix, errors)
        validate_sample_lists(sample, prefix, errors, warnings)
        if outcome == "accepted" and sample.get("used_checkpoint") is not True:
            errors.append(f"{prefix}: accepted sample must set used_checkpoint=true")
        if outcome == "accepted" and not text_list(sample.get("evidence_refs")):
            errors.append(f"{prefix}: accepted sample needs evidence_refs")
    return accepted, accepted_cross_task


def validate_sample_text_fields(sample: dict[str, Any], prefix: str, errors: list[str]) -> None:
    for field in ("task_summary", "note"):
        validate_bounded_required_text(sample, field, prefix, errors)
def validate_sample_lists(
    sample: dict[str, Any],
    prefix: str,
    errors: list[str],
    warnings: list[str],
) -> None:
    for field in (
        "avoided_rework",
        "missed_validation_prevented",
        "missing_fields",
        "false_positive_notes",
        "evidence_refs",
    ):
        values = text_list(sample.get(field))
        if len(values) > MAX_LIST_ITEMS:
            errors.append(f"{prefix}: {field} has too many items")
        if field == "evidence_refs" and not values:
            warnings.append(f"{prefix}: evidence_refs is empty")
        if field == "evidence_refs":
            evidence_ref_utils.validate_existing_repo_relative_refs(
                values, ROOT, "evidence_refs", prefix, errors, allow_selectors=True
            )
        for value in values:
            if len(value) > MAX_TEXT:
                errors.append(f"{prefix}: {field} item exceeds {MAX_TEXT} characters")
def scan_for_forbidden_keys(prefix: str, value: object, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            if key_text in FORBIDDEN_KEYS:
                errors.append(f"{prefix}: forbidden raw runtime key: {key_text}")
            scan_for_forbidden_keys(prefix, child, errors)
    elif isinstance(value, list):
        for child in value:
            scan_for_forbidden_keys(prefix, child, errors)

def emit_text(report: CheckpointReport) -> None:
    print("Stage checkpoint audit:")
    print(f"- checkpoints: {report.checkpoint_path}")
    print(f"- records: {report.record_count}")
    if report.sample_path:
        print(f"- resume samples: {report.sample_path}")
        print(f"- sample records: {report.sample_count}")
        print(f"- accepted samples: {report.accepted_sample_count}")
        print(f"- accepted cross-task samples: {report.accepted_cross_task_sample_count}")
    for warning in report.warnings:
        print(f"WARN: {warning}")
    if report.errors:
        for error in report.errors:
            print(f"ERROR: {error}")
    else:
        print("ERRORS: none")

def main() -> int:
    args = parse_args()
    sample_path = Path(args.samples).expanduser() if args.samples else None
    report = build_report(Path(args.checkpoints).expanduser(), sample_path)
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        emit_text(report)
    return 1 if report.errors else 0

if __name__ == "__main__":
    sys.exit(main())
