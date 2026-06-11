#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECORDS = ROOT / "docs" / "ai" / "standards" / "ci-agent-contract.sample.jsonl"
DEFAULT_CONTRACTS = ROOT / "docs" / "ai" / "tool-contracts" / "contracts.json"
SCHEMA_VERSION = "ci-agent-contract/v1"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
READ_ONLY_PROFILES = {"default-minimal", "read-only"}
READ_ONLY_SCOPE_VALUES = {"read", "none", "disabled", "false"}
DISABLED_SCOPE_VALUES = {"none", "disabled", "false"}
FORBIDDEN_TRIGGER = "pull_request_target"
FORBIDDEN_CAPABILITIES = (
    "secrets",
    "oidc",
    "repository_writes",
    "pr_comments",
    "pr_labels",
    "merge",
    "release",
    "deploy",
    "external_send",
)
FORBIDDEN_KEY_ALIASES = {
    "secret": "secrets",
    "secrets": "secrets",
    "oidc": "oidc",
    "id_token": "oidc",
    "id-token": "oidc",
    "repository_write": "repository_writes",
    "repository_writes": "repository_writes",
    "repo_write": "repository_writes",
    "repo_writes": "repository_writes",
    "pr_comment": "pr_comments",
    "pr_comments": "pr_comments",
    "pull_request_comment": "pr_comments",
    "pull_request_comments": "pr_comments",
    "pr_label": "pr_labels",
    "pr_labels": "pr_labels",
    "label": "pr_labels",
    "labels": "pr_labels",
    "merge": "merge",
    "release": "release",
    "deploy": "deploy",
    "external_send": "external_send",
    "external-send": "external_send",
}
CLAIM_FLAGS = (
    "no_hosted_cloud_agent_claim",
    "no_remote_enforcement_claim",
    "no_real_agent_workflow_claim",
)
MAX_TEXT = 500
MAX_LIST_ITEMS = 12


@dataclass(frozen=True)
class CIAgentContractReport:
    record_path: str
    record_count: int
    referenced_tool_contracts: list[str]
    errors: list[str]
    warnings: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate advisory CI agent contract records.")
    parser.add_argument("--records", default=str(DEFAULT_RECORDS), help="ci-agent-contract/v1 JSONL path.")
    parser.add_argument("--contracts", default=str(DEFAULT_CONTRACTS), help="Tool contract registry path.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def build_report(records_path: Path = DEFAULT_RECORDS, contracts_path: Path = DEFAULT_CONTRACTS) -> CIAgentContractReport:
    errors: list[str] = []
    warnings: list[str] = []
    records = load_records(records_path, errors)
    contract_names = load_contract_names(contracts_path, errors)
    referenced_contracts: set[str] = set()
    for line_no, record in records:
        validate_record(line_no, record, contract_names, referenced_contracts, errors)
    if not records:
        warnings.append("no CI agent contract records found")
    return CIAgentContractReport(
        record_path=relative(records_path),
        record_count=len(records),
        referenced_tool_contracts=sorted(referenced_contracts),
        errors=errors,
        warnings=warnings,
    )


def load_records(path: Path, errors: list[str]) -> list[tuple[int, dict[str, Any]]]:
    if not path.exists():
        errors.append(f"record file missing: {relative(path)}")
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
            errors.append(f"line {line_no}: record must be a JSON object")
    return records


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
    referenced_contracts: set[str],
    errors: list[str],
) -> None:
    prefix = f"line {line_no}"
    scan_for_forbidden_markers(record, prefix, errors)
    validate_choice(record, "schema_version", {SCHEMA_VERSION}, prefix, errors)
    validate_bounded_required_text(record, "id", prefix, errors)
    validate_date(record, "recorded_at", prefix, errors)
    validate_bounded_required_text(record, "purpose", prefix, errors)
    validate_event(record.get("event"), prefix, errors)
    validate_permissions(record.get("permissions"), prefix, errors)
    validate_capabilities(record.get("capabilities"), prefix, errors)
    validate_text_list(record, "bounded_inputs", prefix, errors)
    validate_text_list(record, "bounded_outputs", prefix, errors)
    validate_tool_contracts(record, prefix, contract_names, referenced_contracts, errors)
    validate_claim_boundary(record.get("claim_boundary"), prefix, errors)
    validate_evidence_refs(record, prefix, errors)


def validate_event(value: Any, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix}: event must be an object")
        return
    triggers = validate_text_list(value, "execution_triggers", f"{prefix}: event", errors)
    if triggers != ["pull_request"]:
        errors.append(f"{prefix}: event.execution_triggers must be exactly ['pull_request']")
    if FORBIDDEN_TRIGGER in triggers:
        errors.append(f"{prefix}: pull_request_target is forbidden for CI agent execution")


def validate_permissions(value: Any, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix}: permissions must be an object")
        return
    human_confirmed = value.get("human_confirmed")
    if not isinstance(human_confirmed, bool):
        errors.append(f"{prefix}: permissions.human_confirmed must be a boolean")
        human_confirmed = False
    profile = text(value.get("profile"))
    if not profile:
        errors.append(f"{prefix}: permissions.profile must be non-empty text")
    if not human_confirmed and profile not in READ_ONLY_PROFILES:
        errors.append(f"{prefix}: permissions.profile must be read-only/default-minimal unless human_confirmed=true")
    scopes = value.get("scopes")
    if not isinstance(scopes, dict) or not scopes:
        errors.append(f"{prefix}: permissions.scopes must be a non-empty object")
        return
    for key, raw_value in scopes.items():
        if not isinstance(key, str) or not key.strip():
            errors.append(f"{prefix}: permissions.scopes keys must be non-empty strings")
            continue
        scope_value = text(raw_value).lower() if isinstance(raw_value, str) else raw_value
        normalized_key = key.replace("-", "_")
        if normalized_key in {"id_token", "oidc"} and isinstance(scope_value, str) and scope_value not in DISABLED_SCOPE_VALUES:
            errors.append(f"{prefix}: permissions.scopes.{key} must disable OIDC/id-token")
        if scope_value == "write":
            errors.append(f"{prefix}: permissions.scopes.{key} must not request write permission")
        if not human_confirmed and isinstance(scope_value, str) and scope_value not in READ_ONLY_SCOPE_VALUES:
            errors.append(f"{prefix}: permissions.scopes.{key} must be read-only/default-minimal")


def validate_capabilities(value: Any, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix}: capabilities must be an object")
        return
    for field in FORBIDDEN_CAPABILITIES:
        if field not in value:
            errors.append(f"{prefix}: capabilities.{field} must be present and false")
        elif value[field] is not False:
            errors.append(f"{prefix}: capabilities.{field} is forbidden and must be false")


def validate_tool_contracts(
    record: dict[str, Any],
    prefix: str,
    contract_names: set[str],
    referenced_contracts: set[str],
    errors: list[str],
) -> None:
    contracts = validate_text_list(record, "tool_contracts", prefix, errors)
    for contract in contracts:
        referenced_contracts.add(contract)
        if contract not in contract_names:
            errors.append(f"{prefix}: unknown tool contract: {contract}")


def validate_claim_boundary(value: Any, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix}: claim_boundary must be an object")
        return
    for field in CLAIM_FLAGS:
        if value.get(field) is not True:
            errors.append(f"{prefix}: claim_boundary.{field} must be true")
    validate_bounded_required_text(value, "summary", f"{prefix}: claim_boundary", errors)


def validate_evidence_refs(record: dict[str, Any], prefix: str, errors: list[str]) -> None:
    refs = validate_text_list(record, "evidence_refs", prefix, errors)
    for ref in refs:
        if Path(ref).is_absolute():
            errors.append(f"{prefix}: evidence_refs must be repo-relative: {ref}")
        elif not (ROOT / ref).exists():
            errors.append(f"{prefix}: evidence_ref does not exist: {ref}")


def validate_date(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> None:
    value = validate_bounded_required_text(record, field, prefix, errors)
    if value and not DATE_RE.match(value):
        errors.append(f"{prefix}: {field} must use YYYY-MM-DD")


def validate_choice(record: dict[str, Any], field: str, choices: set[str], prefix: str, errors: list[str]) -> None:
    value = validate_bounded_required_text(record, field, prefix, errors)
    if value and value not in choices:
        errors.append(f"{prefix}: {field} must be one of {sorted(choices)}")


def validate_bounded_required_text(record: dict[str, Any], field: str, prefix: str, errors: list[str]) -> str:
    value = text(record.get(field))
    if not value:
        errors.append(f"{prefix}: {field} must be non-empty text")
    elif len(value) > MAX_TEXT:
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
            errors.append(f"{prefix}: {field}[{index}] must be a non-empty string")
            continue
        if len(item) > MAX_TEXT:
            errors.append(f"{prefix}: {field}[{index}] exceeds {MAX_TEXT} characters")
        items.append(item)
    return items


def scan_for_forbidden_markers(value: Any, prefix: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            normalized = key_text.replace("-", "_")
            if FORBIDDEN_KEY_ALIASES.get(normalized) and truthy_forbidden(child):
                errors.append(f"{prefix}: {key_text} capability is forbidden in CI agent contracts")
            scan_for_forbidden_markers(child, f"{prefix}: {key_text}", errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            scan_for_forbidden_markers(child, f"{prefix}[{index}]", errors)
    elif value == FORBIDDEN_TRIGGER:
        errors.append(f"{prefix}: pull_request_target is forbidden for CI agent execution")


def truthy_forbidden(value: Any) -> bool:
    if value in (False, None):
        return False
    if isinstance(value, str) and value.strip().lower() in READ_ONLY_SCOPE_VALUES | {"not-claimed", "not_claimed"}:
        return False
    return True


def text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def emit_text(report: CIAgentContractReport) -> None:
    print("CI agent contract audit:")
    print(f"- records: {report.record_path}")
    print(f"- record count: {report.record_count}")
    if report.referenced_tool_contracts:
        print(f"- referenced tool contracts: {', '.join(report.referenced_tool_contracts)}")
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
