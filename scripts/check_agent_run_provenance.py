#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys
from typing import Any

import agent_run_metrics
import evidence_ref_utils
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECORDS = ROOT / "docs" / "ai" / "standards" / "agent-run-provenance-sample.jsonl"
DEFAULT_CONTRACTS = ROOT / "docs" / "ai" / "tool-contracts" / "contracts.json"
ID_RE = re.compile(r"^ARP-\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
REQ_RE = re.compile(r"^REQ-\d{3}$")
WS_RE = re.compile(r"^WS-\d{2}$")
TASK_PROFILES = {"simple", "medium", "complex", "0-1-stage", "recovery-dispute"}
AUTHORITY_LEVELS = {"canonical-writer", "draft-only", "read-only"}
ACTOR_TYPES = {"main-agent", "subagent", "automation", "human"}
PLATFORM_BOUNDARIES = {"local-only", "local-with-ci-evidence", "manual-github-evidence"}
VALIDATION_OUTCOMES = {"pass", "warn", "review-required", "not-run"}
CLAIM_STATES = {"verified-local", "ci-evidence", "manual-confirmed", "unknown-plan-limited", "future-work"}
FORBIDDEN_KEYS = {"prompt", "prompt_preview", "raw_output", "rawOutput", "transcript", "transcript_path"}
MAX_TEXT = 600
MAX_LIST_ITEMS = 20
@dataclass(frozen=True)
class AgentRunProvenanceReport:
    record_path: str
    record_count: int
    canonical_write_count: int
    local_first_count: int
    model_usage_counts: dict[str, int]
    estimated_cost_usd_total: float
    referenced_tool_contracts: list[str]
    errors: list[str]
    warnings: list[str]
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate local agent-run provenance records.")
    parser.add_argument("--records", default=str(DEFAULT_RECORDS), help="agent-run-provenance/v1 JSONL path.")
    parser.add_argument("--contracts", default=str(DEFAULT_CONTRACTS), help="Tool contract registry path.")
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

def build_report(records_path: Path = DEFAULT_RECORDS, contracts_path: Path = DEFAULT_CONTRACTS) -> AgentRunProvenanceReport:
    errors: list[str] = []
    warnings: list[str] = []
    records = load_records(records_path, errors)
    contract_names = load_contract_names(contracts_path, errors)
    seen_ids: set[str] = set()
    referenced_contracts: set[str] = set()
    canonical_count = 0
    local_first_count = 0
    model_usage_counts: dict[str, int] = {}
    estimated_cost_total = 0.0
    for line_no, record in records:
        validate_record(line_no, record, seen_ids, contract_names, referenced_contracts, errors, warnings)
        authority = record.get("authority", {})
        if isinstance(authority, dict) and authority.get("canonical_write") is True:
            canonical_count += 1
        if text(record.get("platform_boundary")) in {"local-only", "local-with-ci-evidence"}:
            local_first_count += 1
        metrics = record.get("run_metrics")
        usage = agent_run_metrics.model_usage(metrics)
        model_usage_counts[usage] = model_usage_counts.get(usage, 0) + 1
        estimated_cost_total += agent_run_metrics.estimated_cost(metrics)
    if not records:
        warnings.append("no agent-run provenance records found")
    return AgentRunProvenanceReport(
        relative(records_path),
        len(records),
        canonical_count,
        local_first_count,
        dict(sorted(model_usage_counts.items())),
        round(estimated_cost_total, 6),
        sorted(referenced_contracts),
        errors,
        warnings,
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
    return {text(contract.get("name")) for contract in contracts if isinstance(contract, dict) and text(contract.get("name"))}

def validate_record(
    line_no: int,
    record: dict[str, Any],
    seen_ids: set[str],
    contract_names: set[str],
    referenced_contracts: set[str],
    errors: list[str],
    warnings: list[str],
) -> None:
    prefix = f"line {line_no}"
    scan_for_forbidden_runtime(prefix, record, errors)
    record_id = required_text(record, "id", prefix, errors)
    if record_id and not ID_RE.match(record_id):
        errors.append(f"{prefix}: id must match {ID_RE.pattern}")
    if record_id in seen_ids:
        errors.append(f"{prefix}: duplicate id: {record_id}")
    seen_ids.add(record_id)
    if text(record.get("schema_version")) != "agent-run-provenance/v1":
        errors.append(f"{prefix}: schema_version must be agent-run-provenance/v1")
    validate_date(record, "recorded_at", prefix, errors)
    validate_choice(record, "task_profile", TASK_PROFILES, prefix, errors)
    validate_choice(record, "platform_boundary", PLATFORM_BOUNDARIES, prefix, errors)
    for field in ("task_summary", "decision_summary"):
        validate_bounded_required_text(record, field, prefix, errors)
    validate_traceability(record, prefix, errors)
    validate_authority(record.get("authority"), prefix, errors)
    validate_validation(record.get("validation"), prefix, errors)
    agent_run_metrics.validate_run_metrics(record.get("run_metrics"), prefix, errors)
    validate_tool_contracts(record, prefix, contract_names, referenced_contracts, errors)
    validate_claim_boundaries(record.get("claim_boundaries"), prefix, errors, warnings)
    for field in ("changed_files", "evidence_refs"):
        refs = validate_text_list(record, field, prefix, errors)
        evidence_ref_utils.validate_existing_repo_relative_refs(
            refs,
            ROOT,
            field,
            prefix,
            errors,
            allow_selectors=True,
        )


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


def validate_choice(record: dict[str, Any], field: str, choices: set[str], prefix: str, errors: list[str]) -> None:
    value = required_text(record, field, prefix, errors)
    if value and value not in choices:
        errors.append(f"{prefix}: {field} must be one of {sorted(choices)}")

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

def validate_traceability(record: dict[str, Any], prefix: str, errors: list[str]) -> None:
    req_ids = text_list(record.get("requirement_ids"))
    ws_ids = text_list(record.get("workstream_ids"))
    if not req_ids:
        errors.append(f"{prefix}: requirement_ids must be a non-empty list or ['unbound']")
    if not ws_ids:
        errors.append(f"{prefix}: workstream_ids must be a non-empty list or ['unbound']")
    if req_ids != ["unbound"]:
        for req_id in req_ids:
            if not REQ_RE.match(req_id):
                errors.append(f"{prefix}: invalid requirement id: {req_id}")
    if ws_ids != ["unbound"]:
        for ws_id in ws_ids:
            if not WS_RE.match(ws_id):
                errors.append(f"{prefix}: invalid workstream id: {ws_id}")
    if (req_ids == ["unbound"]) != (ws_ids == ["unbound"]):
        errors.append(f"{prefix}: requirement_ids and workstream_ids must be bound or unbound together")

def validate_authority(value: Any, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix}: authority must be an object")
        return
    validate_choice(value, "actor", ACTOR_TYPES, prefix, errors)
    validate_choice(value, "authority_level", AUTHORITY_LEVELS, prefix, errors)
    canonical_write = value.get("canonical_write")
    if not isinstance(canonical_write, bool):
        errors.append(f"{prefix}: authority.canonical_write must be a boolean")
    if value.get("authority_level") != "canonical-writer" and canonical_write is True:
        errors.append(f"{prefix}: only canonical-writer authority may set canonical_write=true")
    validate_text_list(value, "allowed_outputs", prefix, errors)

def validate_validation(value: Any, prefix: str, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append(f"{prefix}: validation must be a non-empty list")
        return
    for index, item in enumerate(value):
        label = f"{prefix}: validation[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        command = text(item.get("command"))
        if not command:
            errors.append(f"{label}.command must be non-empty text")
        elif len(command) > MAX_TEXT:
            errors.append(f"{label}.command exceeds {MAX_TEXT} characters")
        outcome = text(item.get("outcome"))
        if outcome not in VALIDATION_OUTCOMES:
            errors.append(f"{label}.outcome must be one of {sorted(VALIDATION_OUTCOMES)}")
        refs = text_list(item.get("evidence_refs"))
        if not refs:
            errors.append(f"{label}.evidence_refs must be a non-empty list")
        evidence_ref_utils.validate_existing_repo_relative_refs(refs, ROOT, f"validation[{index}].evidence_refs", prefix, errors, allow_selectors=True)

def validate_tool_contracts(
    record: dict[str, Any],
    prefix: str,
    contract_names: set[str],
    referenced_contracts: set[str],
    errors: list[str],
) -> None:
    contracts = validate_text_list(record, "tool_contracts", prefix, errors)
    for contract in contracts:
        if contract not in contract_names:
            errors.append(f"{prefix}: unknown tool contract: {contract}")
        referenced_contracts.add(contract)

def validate_claim_boundaries(value: Any, prefix: str, errors: list[str], warnings: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"{prefix}: claim_boundaries must be an object")
        return
    claims = value.get("claims")
    unknowns = text_list(value.get("unknown_or_plan_limited"))
    not_claimed = text_list(value.get("not_claimed"))
    if not isinstance(claims, list) or not claims:
        errors.append(f"{prefix}: claim_boundaries.claims must be a non-empty list")
        claims = []
    if not unknowns:
        errors.append(f"{prefix}: claim_boundaries.unknown_or_plan_limited must be a non-empty list")
    if not not_claimed:
        errors.append(f"{prefix}: claim_boundaries.not_claimed must be a non-empty list")
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            errors.append(f"{prefix}: claim_boundaries.claims[{index}] must be an object")
            continue
        state = text(claim.get("state"))
        if state not in CLAIM_STATES:
            errors.append(f"{prefix}: claim_boundaries.claims[{index}].state must be one of {sorted(CLAIM_STATES)}")
        summary = text(claim.get("summary"))
        if not summary:
            errors.append(f"{prefix}: claim_boundaries.claims[{index}].summary must be non-empty text")
        elif len(summary) > MAX_TEXT:
            errors.append(f"{prefix}: claim_boundaries.claims[{index}].summary exceeds {MAX_TEXT} characters")
    combined = " ".join(unknowns + not_claimed).lower()
    if "cloud agent" not in combined and "github copilot" not in combined:
        warnings.append(f"{prefix}: claim boundaries should explicitly exclude hosted/cloud agent task claims when relevant")

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
        errors.append(f"{prefix}: provenance records must not reference local runtime material")

def emit_text(report: AgentRunProvenanceReport) -> None:
    print("Agent-run provenance audit:")
    print(f"- records: {report.record_path}")
    print(f"- record count: {report.record_count}")
    print(f"- canonical write records: {report.canonical_write_count}")
    print(f"- local-first records: {report.local_first_count}")
    if report.model_usage_counts:
        print(f"- model usage: {report.model_usage_counts}")
    print(f"- estimated cost usd total: {report.estimated_cost_usd_total:.6f}")
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
