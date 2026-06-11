#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys
from typing import Any

import check_harness_future_work_contracts as future_contracts
import check_harness_placeholder_replacement as candidate_io
import collect_harness_sample_gaps
import harness_future_work_contract_context
import harness_sample_review_commands


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_AUDIT_COMMAND = ".codex/hooks/run_with_repo_python.sh scripts/check_harness_future_work_contracts.py"


@dataclass(frozen=True)
class ContractCandidateReport:
    candidate_path: str
    contract_id: str
    gap_id: str
    status: str
    contract_kind: str
    current_contract_id: str
    current_contract_line: int
    current_status: str
    sample_collection_allowed: bool
    missing_adr_refs: bool
    ledger_action: str
    readiness: str
    source_metric: str
    current_to_target: str
    capture_gate: str
    capture_gate_detail: str
    evidence_needed: list[str]
    trigger: str
    boundary: str
    planner_command: str
    intake_command: str
    target_ledger: str
    candidate_review_command: str
    next_contract_audit_command: str
    checker_errors: list[str]
    inventory_errors: list[str]
    errors: list[str]
    review_allowed: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a future-work contract candidate without writing ledgers."
    )
    parser.add_argument("candidate", help="Path to a single JSON object or one-record JSONL contract candidate.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def build_report(candidate_path: Path) -> ContractCandidateReport:
    errors: list[str] = []
    candidate = candidate_io.load_candidate(candidate_path, errors)
    contract_id = text(candidate.get("id"))
    gap_id = text(candidate.get("gap_id"))
    status = text(candidate.get("status"))
    contract_kind = text(candidate.get("contract_kind"))
    sample_allowed = candidate.get("sample_collection_allowed") is True
    missing_adr_refs = adr_refs_missing(candidate)
    checker_errors: list[str] = []
    current_contract_id = ""
    current_contract_line = 0
    current_status = ""
    queue_context = harness_future_work_contract_context.ContractQueueContext()
    inventory_errors = current_inventory_errors(gap_id)

    if candidate:
        queue_context = harness_future_work_contract_context.expected_contract_precondition_context(gap_id, errors)
        checker_errors = future_contracts.validate_single_contract_record(candidate)
        rows = current_contract_rows()
        current = rows.get(gap_id)
        if current is None:
            validate_missing_current_contract(gap_id, errors)
        else:
            current_contract_line, current_record = current
            current_contract_id = text(current_record.get("id"))
            current_status = text(current_record.get("status"))
            if contract_id != current_contract_id:
                errors.append(
                    "candidate id must match existing future-work contract id "
                    f"{current_contract_id}; replace the row instead of appending a duplicate"
                )

    blocking_errors = errors + checker_errors + inventory_errors
    return ContractCandidateReport(
        candidate_path=candidate_io.relative(candidate_path),
        contract_id=contract_id,
        gap_id=gap_id,
        status=status,
        contract_kind=contract_kind,
        current_contract_id=current_contract_id,
        current_contract_line=current_contract_line,
        current_status=current_status,
        sample_collection_allowed=sample_allowed,
        missing_adr_refs=missing_adr_refs,
        ledger_action=queue_context.ledger_action,
        readiness=queue_context.readiness,
        source_metric=queue_context.source_metric,
        current_to_target=queue_context.current_to_target,
        capture_gate=queue_context.capture_gate,
        capture_gate_detail=queue_context.capture_gate_detail,
        evidence_needed=queue_context.evidence_list(),
        trigger=queue_context.trigger,
        boundary=queue_context.boundary,
        planner_command=queue_context.planner_command,
        intake_command=queue_context.intake_command,
        target_ledger=future_contracts.relative(future_contracts.DEFAULT_CONTRACTS),
        candidate_review_command=harness_sample_review_commands.FUTURE_WORK_CONTRACT_CANDIDATE_REVIEW_COMMAND,
        next_contract_audit_command=CONTRACT_AUDIT_COMMAND,
        checker_errors=checker_errors,
        inventory_errors=inventory_errors,
        errors=errors,
        review_allowed=not blocking_errors,
    )


def current_inventory_errors(candidate_gap_id: str) -> list[str]:
    report = future_contracts.build_report()
    allowed_missing = f"missing future-work contract for gap: {candidate_gap_id}"
    return [f"future_contracts: {error}" for error in report.errors if error != allowed_missing]


def current_contract_rows() -> dict[str, tuple[int, dict[str, Any]]]:
    errors: list[str] = []
    rows = future_contracts.load_records(future_contracts.DEFAULT_CONTRACTS, errors)
    return {text(record.get("gap_id")): (line_no, record) for line_no, record in rows}


def validate_missing_current_contract(gap_id: str, errors: list[str]) -> None:
    future_gap_ids = {gap.id for gap in collect_harness_sample_gaps.GAPS if gap.status == "future-work"}
    if gap_id in future_gap_ids:
        return
    errors.append(f"candidate gap does not match an existing future-work contract row: {gap_id or '<missing>'}")


def adr_refs_missing(candidate: dict[str, Any]) -> bool:
    adr_refs = future_contracts.text_list(candidate.get("adr_refs"))
    return adr_refs == ["none"] or not adr_refs


def text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def emit_text(report: ContractCandidateReport) -> None:
    print("Harness future-work contract candidate review:")
    print(f"- candidate: {report.candidate_path}")
    print(f"- contract id: {report.contract_id or '<missing>'}")
    print(f"- gap id: {report.gap_id or '<missing>'}")
    print(f"- status: {report.status or '<missing>'}")
    print(f"- contract kind: {report.contract_kind or '<missing>'}")
    if report.current_contract_id:
        print(
            f"- current contract: {report.target_ledger}:{report.current_contract_line} "
            f"({report.current_contract_id}, {report.current_status})"
        )
    else:
        print("- current contract: <not found>")
    print(f"- sample collection allowed: {str(report.sample_collection_allowed).lower()}")
    print(f"- missing ADR refs: {str(report.missing_adr_refs).lower()}")
    if report.ledger_action:
        print(f"- current queue ledger action: {report.ledger_action}")
        print(f"- current readiness: {report.readiness or '<missing>'}")
        print(f"- current source metric: {report.source_metric or '<missing>'}")
        print(f"- current / target: {report.current_to_target or '<missing>'}")
        print(f"- capture gate: {report.capture_gate or '<missing>'}")
        print(f"- capture gate detail: {report.capture_gate_detail or '<missing>'}")
        print(f"- evidence needed: {report.evidence_needed or ['<missing>']}")
        print(f"- trigger: {report.trigger or '<missing>'}")
        print(f"- boundary: {report.boundary or '<missing>'}")
        print(f"- planner command: `{report.planner_command or '<not resolved>'}`")
        print(f"- intake command: `{report.intake_command or '<not resolved>'}`")
    print(f"- candidate review command: `{report.candidate_review_command}`")
    print(f"- next contract audit command: `{report.next_contract_audit_command}`")
    print(f"- review allowed: {'yes' if report.review_allowed else 'no'}")
    for error in report.inventory_errors:
        print(f"ERROR: {error}")
    for error in report.checker_errors:
        print(f"ERROR: {error}")
    for error in report.errors:
        print(f"ERROR: {error}")
    if report.review_allowed:
        print("ERRORS: none")


def main() -> int:
    args = parse_args()
    report = build_report(Path(args.candidate).expanduser())
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        emit_text(report)
    return 0 if report.review_allowed else 1


if __name__ == "__main__":
    sys.exit(main())
