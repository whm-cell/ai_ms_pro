#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys
from typing import Any

import check_harness_placeholder_replacement
import check_harness_sample_templates
import harness_sample_review_commands
import harness_sample_slots
import harness_sample_outcome_context
import harness_sample_outcome_validation


ROOT = Path(__file__).resolve().parents[1]
FINAL_OUTCOMES = {"accepted", "rejected"}


@dataclass(frozen=True)
class SampleOutcomeReport:
    candidate_path: str
    sample_id: str
    gap_id: str
    schema_version: str
    source_type: str
    outcome: str
    evidence_class: str
    target_ledger: str
    target_line: int
    target_review_state: str
    review_command: str
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
    burn_in_counted: bool
    checker_errors: list[str]
    inventory_errors: list[str]
    inventory_warnings: list[str]
    errors: list[str]
    outcome_change_allowed: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a pending harness sample outcome change without writing ledgers."
    )
    parser.add_argument("candidate", help="Path to a single JSON object or one-record JSONL outcome candidate.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def build_report(candidate_path: Path) -> SampleOutcomeReport:
    errors: list[str] = []
    candidate = check_harness_placeholder_replacement.load_candidate(candidate_path, errors)
    sample_id = text(candidate.get("id"))
    gap_id = text(candidate.get("gap_id"))
    schema_version = text(candidate.get("schema_version"))
    source_type = text(candidate.get("source_type"))
    outcome = text(candidate.get("outcome"))
    evidence_class = harness_sample_slots.evidence_class_for_record(candidate) if candidate else ""
    target_ledger = ""
    target_line = 0
    target_review_state = ""
    review_command = ""
    queue_context = harness_sample_outcome_context.OutcomeQueueContext()
    checker_errors: list[str] = []
    inventory_errors: list[str] = []
    inventory_warnings: list[str] = []

    if candidate:
        slots = harness_sample_slots.load_all_slots(inventory_errors, inventory_warnings)
        target_slot = find_pending_slot(sample_id, slots, errors)
        if target_slot is not None:
            target_ledger = target_slot.ledger_path
            target_line = target_slot.line
            target_review_state = target_slot.pending_review_state
            review_command = harness_sample_review_commands.review_command_for(target_slot.ledger_path)
            harness_sample_outcome_validation.validate_candidate_matches_slot(candidate, target_slot, errors)
            harness_sample_outcome_validation.validate_candidate_boundary(candidate, errors)
            target_record = load_target_record(target_slot, errors)
            harness_sample_outcome_validation.validate_stable_fields(candidate, target_record, errors)
            if target_slot.pending_review_state != "review-ready":
                errors.append(
                    f"target pending slot must be review-ready before outcome review, got {target_slot.pending_review_state}"
                )
            else:
                queue_context = harness_sample_outcome_context.expected_outcome_context(target_slot.gap_id, errors)
        if outcome not in FINAL_OUTCOMES:
            errors.append("outcome candidate must change outcome to accepted or rejected")
        checker_errors = validate_with_target_checker(candidate)

    blocking_errors = errors + checker_errors + inventory_errors
    outcome_change_allowed = not blocking_errors
    return SampleOutcomeReport(
        candidate_path=relative(candidate_path),
        sample_id=sample_id,
        gap_id=gap_id,
        schema_version=schema_version,
        source_type=source_type,
        outcome=outcome,
        evidence_class=evidence_class,
        target_ledger=target_ledger,
        target_line=target_line,
        target_review_state=target_review_state,
        review_command=review_command,
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
        burn_in_counted=outcome_change_allowed and outcome == "accepted" and evidence_class == "real",
        checker_errors=checker_errors,
        inventory_errors=inventory_errors,
        inventory_warnings=inventory_warnings,
        errors=errors,
        outcome_change_allowed=outcome_change_allowed,
    )


def find_pending_slot(
    sample_id: str,
    slots: list[harness_sample_slots.SampleSlot],
    errors: list[str],
) -> harness_sample_slots.SampleSlot | None:
    if not sample_id:
        errors.append("candidate id must be non-empty text")
        return None
    matches = [slot for slot in slots if slot.sample_id == sample_id and slot.outcome == "pending"]
    if not matches:
        errors.append(f"candidate id does not match an existing pending sample row: {sample_id}")
        return None
    if len(matches) > 1:
        errors.append(f"candidate id matches multiple pending sample rows: {sample_id}")
        return None
    return matches[0]


def load_target_record(slot: harness_sample_slots.SampleSlot, errors: list[str]) -> dict[str, Any]:
    return harness_sample_outcome_validation.load_target_record(slot, errors)


def validate_with_target_checker(candidate: dict[str, Any]) -> list[str]:
    schema_version = text(candidate.get("schema_version"))
    validator = check_harness_sample_templates.VALIDATORS.get(schema_version)
    if not validator:
        return [f"no target checker mapped for schema_version: {schema_version or '<missing>'}"]
    temp_path = check_harness_sample_templates.write_jsonl(candidate)
    try:
        return validator(temp_path)
    finally:
        temp_path.unlink(missing_ok=True)


def emit_text(report: SampleOutcomeReport) -> None:
    print("Harness sample outcome review:")
    print(f"- candidate: {report.candidate_path}")
    print(f"- sample id: {report.sample_id or '<missing>'}")
    print(f"- gap id: {report.gap_id or '<missing>'}")
    print(f"- schema: {report.schema_version or '<missing>'}")
    print(f"- source type: {report.source_type or '<missing>'}")
    print(f"- outcome: {report.outcome or '<missing>'}")
    print(f"- evidence class: {report.evidence_class or '<unknown>'}")
    print(f"- burn-in counted: {'yes' if report.burn_in_counted else 'no'}")
    if report.target_ledger:
        print(f"- target pending row: {report.target_ledger}:{report.target_line}")
        print(f"- target review state: {report.target_review_state}")
        print(f"- review command: `{report.review_command}`")
        print(f"- ledger action: {report.ledger_action or '<unknown>'}")
        print(f"- readiness: {report.readiness or '<unknown>'}")
        print(f"- source metric: {report.source_metric or '<unknown>'}")
        print(f"- current / target: {report.current_to_target or '<unknown>'}")
        print(f"- capture gate: {report.capture_gate or '<unknown>'}")
        print(f"- capture gate detail: {report.capture_gate_detail or '<unknown>'}")
        if report.evidence_needed:
            print("- evidence needed:")
            for item in report.evidence_needed:
                print(f"  - {item}")
        else:
            print("- evidence needed: <unknown>")
        print(f"- trigger: {report.trigger or '<unknown>'}")
        print(f"- boundary: {report.boundary or '<unknown>'}")
        print(f"- planner command: `{report.planner_command or '<not resolved>'}`")
        print(f"- intake command: `{report.intake_command or '<not resolved>'}`")
    else:
        print("- target pending row: <not found>")
    print(f"- outcome change allowed: {'yes' if report.outcome_change_allowed else 'no'}")
    for warning in report.inventory_warnings:
        print(f"WARN: {warning}")
    for error in report.inventory_errors:
        print(f"ERROR: {error}")
    for error in report.checker_errors:
        print(f"ERROR: {error}")
    for error in report.errors:
        print(f"ERROR: {error}")
    if report.outcome_change_allowed:
        print("ERRORS: none")


def main() -> int:
    args = parse_args()
    report = build_report(Path(args.candidate).expanduser())
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        emit_text(report)
    return 0 if report.outcome_change_allowed else 1


if __name__ == "__main__":
    sys.exit(main())
