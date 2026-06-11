#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys
from typing import Any

import check_harness_burn_in_readiness as readiness
import evidence_ref_utils


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DECISIONS = ROOT / "docs" / "ai" / "standards" / "harness-upgrade-decisions.jsonl"
SCHEMA_VERSION = "harness-upgrade-decision/v1"
DECISIONS = {"keep-advisory", "ready-for-adr", "promote-to-blocking", "defer-until-more-evidence"}
DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
MAX_TEXT = 600
MAX_LIST_ITEMS = 10


@dataclass(frozen=True)
class UpgradeDecisionReport:
    decision_path: str
    ready_gap_count: int
    decision_count: int
    ready_gap_ids: list[str]
    decided_ready_gap_ids: list[str]
    missing_decisions: list[str]
    extra_decisions: list[str]
    decision_counts: dict[str, int]
    next_evidence_needed_by_gap: dict[str, list[str]]
    errors: list[str]
    warnings: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate upgrade decisions for harness gaps that are ready for discussion.",
    )
    parser.add_argument("--decisions", default=str(DEFAULT_DECISIONS), help="Upgrade decisions JSONL path.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def build_report(path: Path = DEFAULT_DECISIONS) -> UpgradeDecisionReport:
    errors: list[str] = []
    warnings: list[str] = []
    readiness_report = readiness.build_report(include_future=True, include_accepted=True)
    errors.extend(f"readiness: {error}" for error in readiness_report.errors)
    items_by_gap = {item.gap_id: item for item in readiness_report.items}
    ready_gaps = sorted(
        item.gap_id for item in readiness_report.items if item.readiness == "ready-for-upgrade-discussion"
    )
    records = load_records(path, errors)
    seen_ids: set[str] = set()
    seen_gap_ids: set[str] = set()
    decisions_by_gap: dict[str, dict[str, Any]] = {}
    counts: dict[str, int] = {}
    next_evidence_needed_by_gap: dict[str, list[str]] = {}
    for line_no, record in records:
        validate_record(line_no, record, seen_ids, seen_gap_ids, items_by_gap, errors)
        gap_id = text(record.get("gap_id"))
        if gap_id:
            decisions_by_gap[gap_id] = record
            next_evidence_needed_by_gap[gap_id] = safe_text_list(record.get("next_evidence_needed"))
        decision = text(record.get("decision"))
        if decision:
            counts[decision] = counts.get(decision, 0) + 1
    missing = sorted(set(ready_gaps) - set(decisions_by_gap))
    extra = sorted(set(decisions_by_gap) - set(ready_gaps))
    for gap_id in missing:
        errors.append(f"missing upgrade decision for ready gap: {gap_id}")
    for gap_id in extra:
        errors.append(f"upgrade decision exists for gap that is not currently ready: {gap_id}")
    return UpgradeDecisionReport(
        decision_path=relative(path),
        ready_gap_count=len(ready_gaps),
        decision_count=len(records),
        ready_gap_ids=ready_gaps,
        decided_ready_gap_ids=sorted(set(ready_gaps) & set(decisions_by_gap)),
        missing_decisions=missing,
        extra_decisions=extra,
        decision_counts=dict(sorted(counts.items())),
        next_evidence_needed_by_gap=dict(sorted(next_evidence_needed_by_gap.items())),
        errors=errors,
        warnings=warnings,
    )


def load_records(path: Path, errors: list[str]) -> list[tuple[int, dict[str, Any]]]:
    if not path.exists():
        errors.append(f"upgrade decision file missing: {relative(path)}")
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
            errors.append(f"line {line_no}: decision must be a JSON object")
    return records


def validate_record(
    line_no: int,
    record: dict[str, Any],
    seen_ids: set[str],
    seen_gap_ids: set[str],
    items_by_gap: dict[str, readiness.ReadinessItem],
    errors: list[str],
) -> None:
    prefix = f"line {line_no}"
    scan_for_forbidden_runtime(prefix, record, errors)
    decision_id = required_text(record, "id", prefix, errors)
    if decision_id in seen_ids:
        errors.append(f"{prefix}: duplicate id: {decision_id}")
    seen_ids.add(decision_id)
    validate_choice(record, "schema_version", {SCHEMA_VERSION}, prefix, errors)
    validate_choice(record, "decision", DECISIONS, prefix, errors)
    validate_date(record, "decided_at", prefix, errors)
    gap_id = required_text(record, "gap_id", prefix, errors)
    if gap_id in seen_gap_ids:
        errors.append(f"{prefix}: duplicate gap_id: {gap_id}")
    if gap_id:
        seen_gap_ids.add(gap_id)
    item = items_by_gap.get(gap_id)
    if item is None and gap_id:
        errors.append(f"{prefix}: gap_id is not tracked by readiness audit: {gap_id}")
    validate_choice(record, "readiness_at_decision", {"ready-for-upgrade-discussion"}, prefix, errors)
    validate_metric_snapshot(record, item, prefix, errors)
    for field in (
        "false_positive_review",
        "repair_path",
        "cost_review",
        "reviewer_burden",
        "rationale",
        "decision_ref",
    ):
        validate_bounded_required_text(record, field, prefix, errors)
    validate_text_list(record, "evidence_refs", prefix, errors)
    validate_evidence_refs(record, prefix, errors)
    validate_text_list(record, "next_evidence_needed", prefix, errors)
    if record.get("no_raw_runtime") is not True:
        errors.append(f"{prefix}: no_raw_runtime must be true")


def validate_metric_snapshot(
    record: dict[str, Any],
    item: readiness.ReadinessItem | None,
    prefix: str,
    errors: list[str],
) -> None:
    if item is None:
        return
    if item.readiness != "ready-for-upgrade-discussion":
        errors.append(f"{prefix}: gap is not currently ready for upgrade discussion: {item.gap_id}")
    if text(record.get("source_metric")) != item.source_metric:
        errors.append(f"{prefix}: source_metric is stale for {item.gap_id}")
    validate_int_match(record, "accepted_count", item.accepted_count, prefix, errors)
    validate_int_match(record, "upgrade_discussion_target", item.upgrade_discussion_target, prefix, errors)


def validate_int_match(
    record: dict[str, Any],
    field: str,
    expected: int,
    prefix: str,
    errors: list[str],
) -> None:
    value = record.get(field)
    if not isinstance(value, int) or isinstance(value, bool):
        errors.append(f"{prefix}: {field} must be an integer")
    elif value != expected:
        errors.append(f"{prefix}: {field} is stale: expected {expected}, got {value}")


def required_text(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> str:
    value = text(record.get(field))
    if not value:
        errors.append(f"{prefix}: {field} must be non-empty text")
    return value


def validate_choice(record: dict[str, Any], field: str, choices: set[str], prefix: str, errors: list[str]) -> None:
    value = required_text(record, field, prefix, errors)
    if value and value not in choices:
        errors.append(f"{prefix}: {field} must be one of {sorted(choices)}")


def validate_date(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> None:
    value = required_text(record, field, prefix, errors)
    if value and not DATE_RE.match(value):
        errors.append(f"{prefix}: {field} must use YYYY-MM-DD")


def validate_bounded_required_text(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> None:
    value = required_text(record, field, prefix, errors)
    if len(value) > MAX_TEXT:
        errors.append(f"{prefix}: {field} exceeds {MAX_TEXT} characters")


def validate_text_list(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> None:
    value = record.get(field)
    if not isinstance(value, list) or not value:
        errors.append(f"{prefix}: {field} must be a non-empty list")
        return
    if len(value) > MAX_LIST_ITEMS:
        errors.append(f"{prefix}: {field} has too many items")
    for item in value:
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{prefix}: {field} items must be non-empty text")
        elif len(item) > MAX_TEXT:
            errors.append(f"{prefix}: {field} item exceeds {MAX_TEXT} characters")


def validate_evidence_refs(record: dict[str, Any], prefix: str, errors: list[str]) -> None:
    evidence_ref_utils.validate_existing_repo_relative_refs(
        safe_text_list(record.get("evidence_refs")),
        ROOT,
        "evidence_refs",
        prefix,
        errors,
        allow_selectors=True,
    )


def safe_text_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def scan_for_forbidden_runtime(prefix: str, value: Any, errors: list[str]) -> None:
    if isinstance(value, dict):
        for child in value.values():
            scan_for_forbidden_runtime(prefix, child, errors)
    elif isinstance(value, list):
        for child in value:
            scan_for_forbidden_runtime(prefix, child, errors)
    elif isinstance(value, str) and ".codex/runtime/" in value.replace("\\", "/"):
        errors.append(f"{prefix}: upgrade decisions must not reference local runtime material")


def text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def emit_text(report: UpgradeDecisionReport) -> None:
    print("Harness upgrade decision audit:")
    print(f"- decisions: {report.decision_path}")
    print(f"- ready gaps: {report.ready_gap_count}")
    print(f"- decision rows: {report.decision_count}")
    print(f"- ready gap ids: {report.ready_gap_ids}")
    print(f"- decided ready gap ids: {report.decided_ready_gap_ids}")
    print(f"- decision counts: {report.decision_counts}")
    print(f"- next evidence needed by gap: {report.next_evidence_needed_by_gap}")
    print(f"- missing decisions: {report.missing_decisions}")
    print(f"- extra decisions: {report.extra_decisions}")
    for warning in report.warnings:
        print(f"WARN: {warning}")
    if report.errors:
        for error in report.errors:
            print(f"ERROR: {error}")
    else:
        print("ERRORS: none")


def main() -> int:
    args = parse_args()
    report = build_report(Path(args.decisions).expanduser())
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        emit_text(report)
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
