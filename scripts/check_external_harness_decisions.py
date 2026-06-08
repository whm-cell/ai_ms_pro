#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys
from typing import Any

import external_harness_default_permission
import external_harness_source_evidence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECORDS = ROOT / "docs" / "ai" / "standards" / "external-harness-decisions.jsonl"
DEFAULT_CONTRACTS = ROOT / "docs" / "ai" / "tool-contracts" / "contracts.json"
SCHEMA_VERSION = "external-harness-decision/v1"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MAX_TEXT = 700
MAX_LIST_ITEMS = 12

AREA_DECISIONS = {
    "remote-trace-pilot": {"defer-external-send-pending-endpoint"},
    "external-eval-sandbox": {"comparison-only-no-dependency"},
    "mcp-a2a": {"contract-registry-only-no-runtime"},
    "ci-agent-workflow": {"keep-advisory-no-real-workflow"},
}

STATUSES = {"active", "superseded"}
REQUIRED_BOUNDARY_FLAGS = (
    "no_hosted_trace_or_eval_claim",
    "no_verified_remote_claim_without_operator_review",
    "no_native_sandbox_claim",
    "no_mcp_a2a_runtime_claim",
    "no_real_ci_agent_workflow_claim",
    "no_external_effect_without_explicit_confirmation",
)

@dataclass(frozen=True)
class DecisionReport:
    record_path: str
    record_count: int
    active_areas: list[str]
    referenced_tool_contracts: list[str]
    source_evidence_count: int
    local_upgrade_scopes: list[str]
    default_permission_count: int
    default_permission_scopes: list[str]
    errors: list[str]
    warnings: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate external harness decision records.")
    parser.add_argument("--records", default=str(DEFAULT_RECORDS), help="external-harness-decision/v1 JSONL path.")
    parser.add_argument("--contracts", default=str(DEFAULT_CONTRACTS), help="Tool contract registry path.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def build_report(records_path: Path = DEFAULT_RECORDS, contracts_path: Path = DEFAULT_CONTRACTS) -> DecisionReport:
    errors: list[str] = []
    warnings: list[str] = []
    records = load_records(records_path, errors)
    contract_names = load_contract_names(contracts_path, errors)
    seen_ids: set[str] = set()
    active_areas: set[str] = set()
    referenced_contracts: set[str] = set()
    local_upgrade_scopes: set[str] = set()
    default_permission_scopes: set[str] = set()
    source_evidence_count = 0
    default_permission_count = 0
    for line_no, record in records:
        source_count, permission_count = validate_record(
            line_no,
            record,
            contract_names,
            seen_ids,
            active_areas,
            referenced_contracts,
            local_upgrade_scopes,
            default_permission_scopes,
            errors,
        )
        source_evidence_count += source_count
        default_permission_count += permission_count
    missing = sorted(set(AREA_DECISIONS) - active_areas)
    if missing:
        errors.append(f"missing active decision areas: {', '.join(missing)}")
    if not records:
        warnings.append("no external harness decision records found")
    return DecisionReport(
        record_path=relative(records_path),
        record_count=len(records),
        active_areas=sorted(active_areas),
        referenced_tool_contracts=sorted(referenced_contracts),
        source_evidence_count=source_evidence_count,
        local_upgrade_scopes=sorted(local_upgrade_scopes),
        default_permission_count=default_permission_count,
        default_permission_scopes=sorted(default_permission_scopes),
        errors=errors,
        warnings=warnings,
    )


def load_records(path: Path, errors: list[str]) -> list[tuple[int, dict[str, Any]]]:
    if not path.exists():
        errors.append(f"record file missing: {relative(path)}")
        return []
    rows: list[tuple[int, dict[str, Any]]] = []
    for line_no, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw_line.strip():
            errors.append(f"line {line_no}: blank line is not allowed")
            continue
        try:
            value = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_no}: invalid JSON: {exc.msg}")
            continue
        if isinstance(value, dict):
            rows.append((line_no, value))
        else:
            errors.append(f"line {line_no}: record must be a JSON object")
    return rows


def load_contract_names(path: Path, errors: list[str]) -> set[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"tool contract registry missing: {relative(path)}")
        return set()
    except json.JSONDecodeError as exc:
        errors.append(f"tool contract registry is invalid JSON: {exc.msg}")
        return set()
    contracts = data.get("contracts") if isinstance(data, dict) else None
    if not isinstance(contracts, list):
        errors.append("tool contract registry contracts must be a list")
        return set()
    return {text(item.get("name")) for item in contracts if isinstance(item, dict) and text(item.get("name"))}


def validate_record(
    line_no: int,
    record: dict[str, Any],
    contract_names: set[str],
    seen_ids: set[str],
    active_areas: set[str],
    referenced_contracts: set[str],
    local_upgrade_scopes: set[str],
    default_permission_scopes: set[str],
    errors: list[str],
) -> tuple[int, int]:
    prefix = f"line {line_no}"
    validate_choice(record, "schema_version", {SCHEMA_VERSION}, prefix, errors)
    record_id = validate_bounded_required_text(record, "id", prefix, errors)
    if record_id:
        if record_id in seen_ids:
            errors.append(f"{prefix}: duplicate id {record_id}")
        seen_ids.add(record_id)
    validate_date(record, "recorded_at", prefix, errors)
    area = validate_choice(record, "decision_area", set(AREA_DECISIONS), prefix, errors)
    decision = validate_bounded_required_text(record, "decision", prefix, errors)
    if area and decision and decision not in AREA_DECISIONS[area]:
        errors.append(f"{prefix}: decision {decision} is not allowed for {area}")
    status = validate_choice(record, "status", STATUSES, prefix, errors)
    if status == "active" and area:
        active_areas.add(area)
    validate_binding_list(record, "requirement_ids", "REQ-", prefix, errors)
    validate_binding_list(record, "workstream_ids", "WS-", prefix, errors)
    validate_bounded_required_text(record, "rationale", prefix, errors)
    validate_bounded_required_text(record, "bounded_next_action", prefix, errors)
    validate_text_list(record, "activation_gates", prefix, errors)
    validate_boundaries(record.get("claim_boundaries"), prefix, errors)
    validate_tool_contracts(record, contract_names, referenced_contracts, prefix, errors)
    validate_evidence_refs(record, prefix, errors)
    permission_count, permission_scopes = external_harness_default_permission.validate(
        record,
        status,
        prefix,
        errors,
    )
    default_permission_scopes.update(permission_scopes)
    source_count, source_scopes = external_harness_source_evidence.validate(record, prefix, errors)
    local_upgrade_scopes.update(source_scopes)
    return source_count, permission_count


def validate_boundaries(value: Any, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix}: claim_boundaries must be an object")
        return
    for flag in REQUIRED_BOUNDARY_FLAGS:
        if value.get(flag) is not True:
            errors.append(f"{prefix}: claim_boundaries.{flag} must be true")
    extra_truthy = sorted(key for key, raw in value.items() if key not in REQUIRED_BOUNDARY_FLAGS and raw is True)
    if extra_truthy:
        errors.append(f"{prefix}: unexpected truthy claim boundary flags: {', '.join(extra_truthy)}")


def validate_tool_contracts(
    record: dict[str, Any],
    contract_names: set[str],
    referenced_contracts: set[str],
    prefix: str,
    errors: list[str],
) -> None:
    tools = validate_text_list(record, "tool_contracts", prefix, errors)
    for name in tools:
        if name not in contract_names:
            errors.append(f"{prefix}: unknown tool contract {name}")
        referenced_contracts.add(name)


def validate_evidence_refs(record: dict[str, Any], prefix: str, errors: list[str]) -> None:
    refs = validate_text_list(record, "evidence_refs", prefix, errors)
    for ref in refs:
        base = ref.split("#", 1)[0].split("::", 1)[0]
        if not base:
            errors.append(f"{prefix}: evidence_refs entry must include a path")
            continue
        path = Path(base)
        if path.is_absolute():
            errors.append(f"{prefix}: evidence_refs must be repo-relative: {ref}")
            continue
        if base.startswith(".codex/runtime/"):
            errors.append(f"{prefix}: evidence_refs must not use raw runtime artifacts: {ref}")
            continue
        if not (ROOT / path).exists():
            errors.append(f"{prefix}: evidence_refs path does not exist: {ref}")

def validate_binding_list(record: dict[str, Any], field: str, prefix_value: str, prefix: str, errors: list[str]) -> None:
    items = validate_text_list(record, field, prefix, errors)
    if items == ["unbound"]:
        return
    for item in items:
        if not item.startswith(prefix_value):
            errors.append(f"{prefix}: {field} values must be ['unbound'] or start with {prefix_value}")


def validate_choice(
    record: dict[str, Any],
    field: str,
    choices: set[str],
    prefix: str,
    errors: list[str],
) -> str:
    value = text(record.get(field))
    if not value:
        errors.append(f"{prefix}: {field} must be non-empty text")
        return ""
    if value not in choices:
        errors.append(f"{prefix}: {field} must be one of {sorted(choices)}")
    return value


def validate_date(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> None:
    value = text(record.get(field))
    if not value or not DATE_RE.match(value):
        errors.append(f"{prefix}: {field} must be YYYY-MM-DD")


def validate_bounded_required_text(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> str:
    value = text(record.get(field))
    if not value:
        errors.append(f"{prefix}: {field} must be non-empty text")
        return ""
    if len(value) > MAX_TEXT:
        errors.append(f"{prefix}: {field} exceeds {MAX_TEXT} characters")
    return value


def validate_text_list(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> list[str]:
    value = record.get(field)
    if not isinstance(value, list) or not value:
        errors.append(f"{prefix}: {field} must be a non-empty list")
        return []
    if len(value) > MAX_LIST_ITEMS:
        errors.append(f"{prefix}: {field} has too many items")
    items: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{prefix}: {field}[{index}] must be non-empty text")
            continue
        if len(item) > MAX_TEXT:
            errors.append(f"{prefix}: {field}[{index}] exceeds {MAX_TEXT} characters")
        items.append(item.strip())
    return items


def text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def emit_text(report: DecisionReport) -> None:
    print("External harness decision audit:")
    print(f"- records: {report.record_path}")
    print(f"- record count: {report.record_count}")
    print(f"- active areas: {', '.join(report.active_areas) if report.active_areas else 'none'}")
    if report.referenced_tool_contracts:
        print(f"- referenced tool contracts: {', '.join(report.referenced_tool_contracts)}")
    print(f"- source evidence records: {report.source_evidence_count}")
    if report.local_upgrade_scopes:
        print(f"- local upgrade scopes: {', '.join(report.local_upgrade_scopes)}")
    print(f"- default permission records: {report.default_permission_count}")
    if report.default_permission_scopes:
        print(f"- default permission scopes: {', '.join(report.default_permission_scopes)}")
    for warning in report.warnings:
        print(f"WARN: {warning}")
    if report.errors:
        for error in report.errors:
            print(f"ERROR: {error}")
    else:
        print("ERRORS: none")


def main() -> int:
    args = parse_args()
    report = build_report(Path(args.records).expanduser(), Path(args.contracts).expanduser())
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        emit_text(report)
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
