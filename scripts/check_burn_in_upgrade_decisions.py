#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
from typing import Any

import check_burn_in_ledger
import evidence_ref_utils


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DECISIONS = ROOT / "docs" / "ai" / "standards" / "check-burn-in-upgrade-decisions.jsonl"
SCHEMA_VERSION = "check-burn-in-upgrade-decision/v1"
DECISIONS = {"keep-candidate", "ready-for-adr", "promote-to-blocking", "demote-to-advisory"}
DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
MAX_TEXT = 600
MAX_LIST_ITEMS = 10


@dataclass(frozen=True)
class UpgradeDecisionReport:
    decision_path: str
    upgrade_review_needed_count: int
    decision_count: int
    upgrade_review_needed_checks: list[str]
    decided_checks: list[str]
    missing_decisions: list[str]
    extra_decisions: list[str]
    decision_counts: dict[str, int]
    next_evidence_needed_by_check: dict[str, list[str]]
    errors: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate upgrade decisions for blocking-candidate checks ready for review.",
    )
    parser.add_argument("--decisions", default=str(DEFAULT_DECISIONS), help="Upgrade decisions JSONL path.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def build_report(path: Path = DEFAULT_DECISIONS) -> UpgradeDecisionReport:
    errors: list[str] = []
    ledger_result = check_burn_in_ledger.validate()
    errors.extend(f"burn-in ledger: {error}" for error in ledger_result.errors)
    rows_by_check = {row.check: row for row in ledger_result.rows}
    review_checks = sorted(ledger_result.upgrade_review_needed_checks)
    records = load_records(path, errors)
    seen_ids: set[str] = set()
    seen_checks: set[str] = set()
    decisions_by_check: dict[str, dict[str, Any]] = {}
    counts: dict[str, int] = {}
    next_evidence_needed_by_check: dict[str, list[str]] = {}
    for line_no, record in records:
        validate_record(line_no, record, seen_ids, seen_checks, rows_by_check, errors)
        check = text(record.get("check"))
        if check:
            decisions_by_check[check] = record
            next_evidence_needed_by_check[check] = safe_text_list(record.get("next_evidence_needed"))
        decision = text(record.get("decision"))
        if decision:
            counts[decision] = counts.get(decision, 0) + 1
    missing = sorted(set(review_checks) - set(decisions_by_check))
    extra = sorted(set(decisions_by_check) - set(review_checks))
    for check in missing:
        errors.append(f"missing upgrade decision for review-needed check: {check}")
    for check in extra:
        errors.append(f"upgrade decision exists for check that is not currently review-needed: {check}")
    return UpgradeDecisionReport(
        decision_path=relative(path),
        upgrade_review_needed_count=len(review_checks),
        decision_count=len(records),
        upgrade_review_needed_checks=review_checks,
        decided_checks=sorted(set(review_checks) & set(decisions_by_check)),
        missing_decisions=missing,
        extra_decisions=extra,
        decision_counts=dict(sorted(counts.items())),
        next_evidence_needed_by_check=dict(sorted(next_evidence_needed_by_check.items())),
        errors=errors,
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
    seen_checks: set[str],
    rows_by_check: dict[str, check_burn_in_ledger.BurnInLedgerRow],
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
    check = required_text(record, "check", prefix, errors)
    if check in seen_checks:
        errors.append(f"{prefix}: duplicate check: {check}")
    if check:
        seen_checks.add(check)
    row = rows_by_check.get(check)
    if row is None and check:
        errors.append(f"{prefix}: check is not tracked by burn-in ledger: {check}")
    validate_row_snapshot(record, row, prefix, errors)
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


def validate_row_snapshot(
    record: dict[str, Any],
    row: check_burn_in_ledger.BurnInLedgerRow | None,
    prefix: str,
    errors: list[str],
) -> None:
    if row is None:
        return
    if not row.upgrade_review_needed:
        errors.append(f"{prefix}: check is not currently marked upgrade_review_needed: {row.check}")
    validate_int_match(record, "accepted_samples", row.accepted_samples, prefix, errors)
    validate_int_match(record, "sample_target", row.sample_target, prefix, errors)
    if text(record.get("current_decision_at_review")) != row.current_decision:
        errors.append(f"{prefix}: current_decision_at_review is stale for {row.check}")


def validate_int_match(record: dict[str, Any], field: str, expected: int, prefix: str, errors: list[str]) -> None:
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
    print("Check burn-in upgrade decision audit:")
    print(f"- decisions: {report.decision_path}")
    print(f"- upgrade review needed checks: {report.upgrade_review_needed_count}")
    print(f"- decision rows: {report.decision_count}")
    print(f"- review-needed check ids: {report.upgrade_review_needed_checks}")
    print(f"- decided checks: {report.decided_checks}")
    print(f"- decision counts: {report.decision_counts}")
    print(f"- next evidence needed by check: {report.next_evidence_needed_by_check}")
    print(f"- missing decisions: {report.missing_decisions}")
    print(f"- extra decisions: {report.extra_decisions}")
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
    raise SystemExit(main())
