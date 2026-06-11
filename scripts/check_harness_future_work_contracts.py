#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys
from typing import Any

import collect_harness_sample_gaps
import harness_future_work_contract_states as contract_state_report


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACTS = ROOT / "docs" / "ai" / "standards" / "harness-future-work-contracts.jsonl"
SCHEMA_VERSION = "harness-future-work-contract/v1"
STATUSES = {"needs-adr", "approved-for-sampling", "retired"}
KINDS = {"remote-interop", "agentic-control"}
MAX_TEXT = 500
MAX_LIST_ITEMS = 8
ADR_REF_RE = re.compile(r"^docs/ai/adr/ADR-[0-9]{3}[-A-Za-z0-9]*\.md$")
ADOPTED_MARKERS = ("状态：已采纳", "Status: accepted", "status: accepted")
REQUIRED_ADR_COVERAGE_TERMS = (
    "auth_model",
    "endpoint_or_authority_scope",
    "redaction_or_boundary_model",
    "cost_or_stop_boundary",
)


@dataclass(frozen=True)
class FutureContractReport:
    contract_path: str
    future_gap_count: int
    contract_count: int
    approved_for_sampling_count: int
    blocked_until_adr_count: int
    missing_contracts: list[str]
    extra_contracts: list[str]
    contract_states: list[contract_state_report.FutureContractState]
    errors: list[str]
    warnings: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate future-work gap contracts before sample collection.")
    parser.add_argument("--contracts", default=str(DEFAULT_CONTRACTS), help="Future-work contract JSONL path.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def build_report(path: Path = DEFAULT_CONTRACTS) -> FutureContractReport:
    errors: list[str] = []
    warnings: list[str] = []
    future_gap_ids = [gap.id for gap in collect_harness_sample_gaps.GAPS if gap.status == "future-work"]
    future_gaps = set(future_gap_ids)
    records = load_records(path, errors)
    seen_ids: set[str] = set()
    seen_gap_ids: set[str] = set()
    contracts_by_gap: dict[str, dict[str, Any]] = {}
    approved = 0
    blocked = 0
    for line_no, record in records:
        validate_record(line_no, record, seen_ids, seen_gap_ids, future_gaps, errors, warnings)
        gap_id = text(record.get("gap_id"))
        if gap_id:
            contracts_by_gap[gap_id] = record
        if text(record.get("status")) == "approved-for-sampling":
            approved += 1
        elif record.get("sample_collection_allowed") is False:
            blocked += 1
    missing = sorted(future_gaps - set(contracts_by_gap))
    extra = sorted(set(contracts_by_gap) - future_gaps)
    for gap_id in missing:
        errors.append(f"missing future-work contract for gap: {gap_id}")
    for gap_id in extra:
        errors.append(f"contract is not for a future-work gap: {gap_id}")
    contract_states = contract_state_report.build_contract_states(
        future_gap_ids,
        contracts_by_gap,
    )
    return FutureContractReport(
        contract_path=relative(path),
        future_gap_count=len(future_gaps),
        contract_count=len(records),
        approved_for_sampling_count=approved,
        blocked_until_adr_count=blocked,
        missing_contracts=missing,
        extra_contracts=extra,
        contract_states=contract_states,
        errors=errors,
        warnings=warnings,
    )


def contract_statuses(path: Path = DEFAULT_CONTRACTS) -> dict[str, str]:
    errors: list[str] = []
    return {text(record.get("gap_id")): text(record.get("status")) for _, record in load_records(path, errors)}


def validate_single_contract_record(record: dict[str, Any], line_no: int = 1) -> list[str]:
    errors: list[str] = []
    warnings: list[str] = []
    future_gaps = {gap.id for gap in collect_harness_sample_gaps.GAPS if gap.status == "future-work"}
    validate_record(line_no, record, set(), set(), future_gaps, errors, warnings)
    return errors


def load_records(path: Path, errors: list[str]) -> list[tuple[int, dict[str, Any]]]:
    if not path.exists():
        errors.append(f"future-work contract file missing: {relative(path)}")
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
            errors.append(f"line {line_no}: contract must be a JSON object")
    return records


def validate_record(
    line_no: int,
    record: dict[str, Any],
    seen_ids: set[str],
    seen_gap_ids: set[str],
    future_gaps: set[str],
    errors: list[str],
    warnings: list[str],
) -> None:
    prefix = f"line {line_no}"
    scan_for_forbidden_runtime(prefix, record, errors)
    contract_id = required_text(record, "id", prefix, errors)
    if contract_id in seen_ids:
        errors.append(f"{prefix}: duplicate id: {contract_id}")
    seen_ids.add(contract_id)
    validate_choice(record, "schema_version", {SCHEMA_VERSION}, prefix, errors)
    validate_choice(record, "status", STATUSES, prefix, errors)
    validate_choice(record, "contract_kind", KINDS, prefix, errors)
    gap_id = required_text(record, "gap_id", prefix, errors)
    if gap_id in seen_gap_ids:
        errors.append(f"{prefix}: duplicate gap_id: {gap_id}")
    if gap_id:
        seen_gap_ids.add(gap_id)
    if gap_id and gap_id not in future_gaps:
        errors.append(f"{prefix}: gap_id is not a future-work gap: {gap_id}")
    validate_bool(record, "adr_required", prefix, errors)
    validate_bool(record, "sample_collection_allowed", prefix, errors)
    validate_bool(record, "no_external_claim", prefix, errors)
    for field in (
        "auth_model",
        "endpoint_or_authority_scope",
        "redaction_or_boundary_model",
        "cost_or_stop_boundary",
        "decision",
        "note",
    ):
        validate_bounded_required_text(record, field, prefix, errors)
    for field in ("adr_refs", "evidence_refs"):
        validate_text_list(record, field, prefix, errors)
    validate_status_rules(record, prefix, errors, warnings)


def validate_status_rules(record: dict[str, Any], prefix: str, errors: list[str], warnings: list[str]) -> None:
    status = text(record.get("status"))
    adr_refs = text_list(record.get("adr_refs"))
    if record.get("no_external_claim") is not True:
        errors.append(f"{prefix}: no_external_claim must stay true for future-work contracts")
    if status == "approved-for-sampling":
        if record.get("adr_required") is not True:
            errors.append(f"{prefix}: approved sampling still requires adr_required=true")
        if record.get("sample_collection_allowed") is not True:
            errors.append(f"{prefix}: approved sampling must set sample_collection_allowed=true")
        if adr_refs == ["none"] or not adr_refs:
            errors.append(f"{prefix}: approved sampling requires concrete adr_refs")
        else:
            validate_approved_adr_refs(prefix, record, adr_refs, errors)
    else:
        if record.get("sample_collection_allowed") is not False:
            errors.append(f"{prefix}: non-approved contracts must set sample_collection_allowed=false")
        if status == "needs-adr" and adr_refs != ["none"]:
            warnings.append(f"{prefix}: needs-adr contract already has adr_refs; consider approved-for-sampling or retired")


def validate_approved_adr_refs(
    prefix: str,
    record: dict[str, Any],
    adr_refs: list[str],
    errors: list[str],
) -> None:
    for adr_ref in adr_refs:
        path = adr_path_for_ref(adr_ref)
        if path is None:
            errors.append(f"{prefix}: approved sampling adr_ref must be a repo ADR path: {adr_ref}")
            continue
        if not path.exists():
            errors.append(f"{prefix}: approved sampling adr_ref does not exist: {adr_ref}")
            continue
        adr_text = path.read_text(encoding="utf-8")
        if not any(marker in adr_text for marker in ADOPTED_MARKERS):
            errors.append(f"{prefix}: approved sampling adr_ref must point to an adopted ADR: {adr_ref}")
        validate_adr_contract_coverage(prefix, record, adr_ref, adr_text, errors)


def adr_path_for_ref(adr_ref: str) -> Path | None:
    normalized = adr_ref.strip().replace("\\", "/")
    if not ADR_REF_RE.match(normalized):
        return None
    path = (ROOT / normalized).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError:
        return None
    return path


def validate_adr_contract_coverage(
    prefix: str,
    record: dict[str, Any],
    adr_ref: str,
    adr_text: str,
    errors: list[str],
) -> None:
    gap_id = text(record.get("gap_id"))
    contract_id = text(record.get("id"))
    if gap_id and gap_id not in adr_text:
        errors.append(f"{prefix}: approved sampling adr_ref must mention gap_id {gap_id}: {adr_ref}")
    if contract_id and contract_id not in adr_text:
        errors.append(f"{prefix}: approved sampling adr_ref must mention contract id {contract_id}: {adr_ref}")
    for term in REQUIRED_ADR_COVERAGE_TERMS:
        if term not in adr_text:
            errors.append(f"{prefix}: approved sampling adr_ref must cover {term}: {adr_ref}")


def required_text(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> str:
    value = text(record.get(field))
    if not value:
        errors.append(f"{prefix}: {field} must be non-empty text")
    return value


def validate_choice(record: dict[str, Any], field: str, choices: set[str], prefix: str, errors: list[str]) -> None:
    value = required_text(record, field, prefix, errors)
    if value and value not in choices:
        errors.append(f"{prefix}: {field} must be one of {sorted(choices)}")


def validate_bool(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> None:
    if not isinstance(record.get(field), bool):
        errors.append(f"{prefix}: {field} must be a boolean")


def validate_bounded_required_text(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> None:
    value = required_text(record, field, prefix, errors)
    if len(value) > MAX_TEXT:
        errors.append(f"{prefix}: {field} exceeds {MAX_TEXT} characters")


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


def scan_for_forbidden_runtime(prefix: str, value: Any, errors: list[str]) -> None:
    if isinstance(value, dict):
        for child in value.values():
            scan_for_forbidden_runtime(prefix, child, errors)
    elif isinstance(value, list):
        for child in value:
            scan_for_forbidden_runtime(prefix, child, errors)
    elif isinstance(value, str) and ".codex/runtime/" in value.replace("\\", "/"):
        errors.append(f"{prefix}: future-work contracts must not reference local runtime material")


def text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def text_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def emit_text(report: FutureContractReport) -> None:
    print("Harness future-work contract audit:")
    print(f"- contracts: {report.contract_path}")
    print(f"- future-work gaps: {report.future_gap_count}")
    print(f"- contract rows: {report.contract_count}")
    print(f"- approved for sampling: {report.approved_for_sampling_count}")
    print(f"- blocked until ADR/contract approval: {report.blocked_until_adr_count}")
    print(f"- missing contracts: {report.missing_contracts}")
    print("- contract states:")
    for state in report.contract_states:
        allowed = str(state.sample_collection_allowed).lower()
        missing_adr = str(state.missing_adr_refs).lower()
        print(f"  - {state.gap_id}: {state.status}; sample_allowed={allowed}; missing_adr_refs={missing_adr}")
        print(f"    boundary: {state.sample_collection_boundary}")
        print(f"    next_action: {state.next_action}")
        print(f"    review_command: {state.review_command}")
    for warning in report.warnings:
        print(f"WARN: {warning}")
    if report.errors:
        for error in report.errors:
            print(f"ERROR: {error}")
    else:
        print("ERRORS: none")


def main() -> int:
    args = parse_args()
    report = build_report(Path(args.contracts).expanduser())
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        emit_text(report)
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
