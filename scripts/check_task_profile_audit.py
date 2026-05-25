#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys
from typing import Any

import evidence_ref_utils


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AUDIT = ROOT / "docs" / "ai" / "standards" / "task-profile-audit-sample.jsonl"
PROFILES = {"simple", "medium", "complex", "0-1-stage", "recovery-dispute"}
SOURCE_TYPES = {"real-task", "synthetic-regression", "manual-review"}
OUTCOMES = {"accepted", "pending", "rejected"}
FORBIDDEN_KEYS = {"cwd", "prompt", "prompt_preview", "promptPreview", "raw_output", "rawOutput", "transcript", "transcript_path", "transcriptPath"}
HEAVY_SURFACES = ("docs/requirements/", "docs/ai/adr/", "docs/ai/handoffs/", "docs/ai/archive/")
COMMON_READS = ("docs/ai/index.md", "docs/ai/working-context.md")
ZERO_ONE_READS = ("docs/requirements/index.md", "docs/requirements/traceability-matrix.md", "docs/ai/plan.md")


@dataclass(frozen=True)
class AuditRecord:
    schema_version: str
    id: str
    source_type: str
    outcome: str
    profile: str
    task_summary: str
    read_files: tuple[str, ...]
    changed_files: tuple[str, ...]
    verification_commands: tuple[str, ...]
    requirement_ids: tuple[str, ...]
    workstream_ids: tuple[str, ...]
    traceability_note: str
    false_positive: bool
    process_tax_note: str
    evidence_refs: tuple[str, ...]


@dataclass(frozen=True)
class AuditReport:
    audit_path: str
    record_count: int
    real_sample_count: int
    accepted_real_sample_count: int
    accepted_real_profiles: dict[str, int]
    false_positive_count: int
    errors: list[str]
    warnings: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit task profile selection against read and verification surface.")
    parser.add_argument("--audit", default=str(DEFAULT_AUDIT), help="Task profile audit JSONL path.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def normalize_path(value: str) -> str:
    normalized = value.replace("\\", "/")
    root = ROOT.as_posix().rstrip("/") + "/"
    if normalized.startswith(root):
        normalized = normalized[len(root) :]
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def text_tuple(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(normalize_path(item.strip()) for item in value if isinstance(item, str) and item.strip())


def load_records(path: Path, errors: list[str]) -> list[AuditRecord]:
    if not path.exists():
        errors.append(f"audit file missing: {relative(path)}")
        return []
    records: list[AuditRecord] = []
    seen: set[str] = set()
    for line_no, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw_line.strip():
            errors.append(f"line {line_no}: blank line is not allowed")
            continue
        try:
            payload = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_no}: invalid JSON: {exc.msg}")
            continue
        if not isinstance(payload, dict):
            errors.append(f"line {line_no}: record must be a JSON object")
            continue
        scan_for_forbidden_keys(f"line {line_no}", payload, errors)
        record = coerce_record(line_no, payload, errors)
        if not record:
            continue
        if record.id in seen:
            errors.append(f"line {line_no}: duplicate id: {record.id}")
        seen.add(record.id)
        records.append(record)
    return records


def coerce_record(line_no: int, payload: dict[str, Any], errors: list[str]) -> AuditRecord | None:
    schema_version = text(payload.get("schema_version"))
    identifier = text(payload.get("id"))
    source_type = text(payload.get("source_type"))
    outcome = text(payload.get("outcome"))
    profile = text(payload.get("profile"))
    task_summary = text(payload.get("task_summary"))
    read_files = text_tuple(payload.get("read_files"))
    verification_commands = text_tuple(payload.get("verification_commands"))
    process_tax_note = text(payload.get("process_tax_note"))
    evidence_refs = text_tuple(payload.get("evidence_refs"))
    false_positive = payload.get("false_positive")
    if schema_version != "task-profile-audit-sample/v1":
        errors.append(f"line {line_no}: schema_version must be task-profile-audit-sample/v1")
    for field, value in (
        ("id", identifier),
        ("task_summary", task_summary),
        ("process_tax_note", process_tax_note),
    ):
        if not value:
            errors.append(f"line {line_no}: {field} must be non-empty text")
    if source_type not in SOURCE_TYPES:
        errors.append(f"line {line_no}: source_type must be one of {sorted(SOURCE_TYPES)}")
    if outcome not in OUTCOMES:
        errors.append(f"line {line_no}: outcome must be one of {sorted(OUTCOMES)}")
    if profile not in PROFILES:
        errors.append(f"line {line_no}: profile must be one of {sorted(PROFILES)}")
    if not read_files:
        errors.append(f"line {line_no}: read_files must be a non-empty list")
    if not verification_commands:
        errors.append(f"line {line_no}: verification_commands must be a non-empty list")
    if not isinstance(false_positive, bool):
        errors.append(f"line {line_no}: false_positive must be a boolean")
    if not evidence_refs:
        errors.append(f"line {line_no}: evidence_refs must be a non-empty list")
    invalid = schema_version != "task-profile-audit-sample/v1" or not identifier or source_type not in SOURCE_TYPES or outcome not in OUTCOMES or profile not in PROFILES or not task_summary or not read_files or not verification_commands or not isinstance(false_positive, bool) or not process_tax_note or not evidence_refs
    if invalid:
        return None
    return AuditRecord(
        schema_version=schema_version,
        id=identifier,
        source_type=source_type,
        outcome=outcome,
        profile=profile,
        task_summary=task_summary,
        read_files=read_files,
        changed_files=text_tuple(payload.get("changed_files")),
        verification_commands=verification_commands,
        requirement_ids=text_tuple(payload.get("requirement_ids")),
        workstream_ids=text_tuple(payload.get("workstream_ids")),
        traceability_note=text(payload.get("traceability_note")),
        false_positive=bool(false_positive),
        process_tax_note=process_tax_note,
        evidence_refs=evidence_refs,
    )


def build_report(path: Path = DEFAULT_AUDIT) -> AuditReport:
    errors: list[str] = []
    warnings: list[str] = []
    records = load_records(path, errors)
    for record in records:
        validate_record(record, errors, warnings)
    accepted_profiles: dict[str, int] = {}
    for record in records:
        if record.source_type == "real-task" and record.outcome == "accepted":
            accepted_profiles[record.profile] = accepted_profiles.get(record.profile, 0) + 1
    if accepted_profiles.get("simple", 0) == 0:
        warnings.append("no accepted real simple-task profile sample recorded yet")
    if accepted_profiles.get("complex", 0) == 0:
        warnings.append("no accepted real complex-task profile sample recorded yet")
    return AuditReport(
        audit_path=relative(path),
        record_count=len(records),
        real_sample_count=sum(1 for record in records if record.source_type == "real-task"),
        accepted_real_sample_count=sum(1 for record in records if record.source_type == "real-task" and record.outcome == "accepted"),
        accepted_real_profiles=accepted_profiles,
        false_positive_count=sum(1 for record in records if record.false_positive),
        errors=errors,
        warnings=warnings,
    )


def validate_record(record: AuditRecord, errors: list[str], warnings: list[str]) -> None:
    prefix = f"{record.id}:"
    missing = [path for path in COMMON_READS if path not in record.read_files]
    for path in missing:
        errors.append(f"{prefix} missing common read surface: {path}")
    if record.profile == "simple":
        validate_simple(record, errors, warnings)
    elif record.profile == "complex":
        validate_complex(record, errors)
    elif record.profile == "0-1-stage":
        validate_zero_one(record, errors)
    elif record.profile == "recovery-dispute":
        validate_recovery(record, errors)
    validate_sample_evidence(record, errors, warnings)


def validate_simple(record: AuditRecord, errors: list[str], warnings: list[str]) -> None:
    heavy = [path for path in record.read_files if starts_any(path, HEAVY_SURFACES)]
    if heavy:
        errors.append(f"{record.id}: simple profile read heavy surfaces: {', '.join(heavy)}")
    if len(record.read_files) > 8:
        warnings.append(f"{record.id}: simple profile read_files count is high: {len(record.read_files)}")
    if len(record.verification_commands) > 3:
        warnings.append(
            f"{record.id}: simple profile verification command count is high: {len(record.verification_commands)}"
        )


def validate_complex(record: AuditRecord, errors: list[str]) -> None:
    if not has_traceability_closure(record):
        errors.append(
            f"{record.id}: complex profile needs traceability matrix, REQ/WS ids, or not-applicable traceability_note"
        )
    require_governance_check(record, errors)
    if changes_requirements(record) and not command_mentions(record, "check_requirements_shape.py"):
        errors.append(f"{record.id}: requirements changes need check_requirements_shape.py verification")


def validate_zero_one(record: AuditRecord, errors: list[str]) -> None:
    for path in ZERO_ONE_READS:
        if path not in record.read_files:
            errors.append(f"{record.id}: 0-1-stage profile missing read surface: {path}")
    if not any(path.startswith("docs/ai/status/") for path in record.read_files):
        errors.append(f"{record.id}: 0-1-stage profile needs a stage status read")
    if not any(path.startswith("docs/requirements/workstreams/") for path in record.read_files):
        errors.append(f"{record.id}: 0-1-stage profile needs a workstream read")
    validate_complex(record, errors)


def validate_recovery(record: AuditRecord, errors: list[str]) -> None:
    recovery_surface = any(
        path.startswith(".codex/runtime/") or path.startswith("docs/ai/handoffs/")
        for path in record.read_files
    )
    if not recovery_surface:
        errors.append(f"{record.id}: recovery-dispute profile needs runtime or handoff recovery surface")
    require_governance_check(record, errors)


def starts_any(value: str, prefixes: tuple[str, ...]) -> bool:
    return any(value.startswith(prefix) for prefix in prefixes)


def has_traceability_closure(record: AuditRecord) -> bool:
    if "docs/requirements/traceability-matrix.md" in record.read_files:
        return True
    if record.requirement_ids or record.workstream_ids:
        return True
    return record.traceability_note.startswith("not-applicable:")


def command_mentions(record: AuditRecord, needle: str) -> bool:
    return any(needle in command for command in record.verification_commands)


def changes_governance(record: AuditRecord) -> bool:
    return any(
        path == "AGENTS.md" or path.startswith("docs/ai/") or path.startswith("docs/requirements/")
        for path in record.changed_files
    )


def changes_requirements(record: AuditRecord) -> bool:
    return any(path.startswith("docs/requirements/") for path in record.changed_files)


def require_governance_check(record: AuditRecord, errors: list[str]) -> None:
    if changes_governance(record) and not command_mentions(record, "check_ai_governance.py"):
        errors.append(f"{record.id}: governance changes need check_ai_governance.py verification")


def validate_sample_evidence(record: AuditRecord, errors: list[str], warnings: list[str]) -> None:
    if record.source_type == "synthetic-regression" and record.outcome == "accepted":
        warnings.append(f"{record.id}: synthetic samples do not count as real task-profile burn-in evidence")
    if record.outcome == "accepted" and record.evidence_refs == ("none",):
        errors.append(f"{record.id}: accepted samples need evidence_refs")
    for path in record.evidence_refs:
        if path.startswith(".codex/runtime/"):
            errors.append(f"{record.id}: evidence_refs must not point at local runtime material: {path}")
    evidence_ref_utils.validate_existing_repo_relative_refs(
        list(record.evidence_refs), ROOT, "evidence_refs", record.id, errors, allow_selectors=True
    )


def scan_for_forbidden_keys(prefix: str, value: Any, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            if key_text in FORBIDDEN_KEYS:
                errors.append(f"{prefix}: forbidden raw runtime key: {key_text}")
            scan_for_forbidden_keys(prefix, child, errors)
    elif isinstance(value, list):
        for child in value:
            scan_for_forbidden_keys(prefix, child, errors)
    elif isinstance(value, str) and ".codex/runtime/" in value.replace("\\", "/"):
        errors.append(f"{prefix}: shared samples must not reference local runtime material")


def emit_text(report: AuditReport) -> None:
    print("Task profile audit:")
    print(f"- audit: {report.audit_path}")
    print(f"- records: {report.record_count}")
    print(f"- real samples: {report.real_sample_count}")
    print(f"- accepted real samples: {report.accepted_real_sample_count}")
    print(f"- accepted real profiles: {report.accepted_real_profiles}")
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
    report = build_report(Path(args.audit).expanduser())
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        emit_text(report)
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
