#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys
from typing import Any

import check_harness_sample_templates
import harness_sample_review_context
import harness_sample_review_commands
import harness_sample_slots
import plan_harness_sample_collection


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class PlaceholderReplacementReport:
    candidate_path: str
    sample_id: str
    gap_id: str
    schema_version: str
    source_type: str
    target_ledger: str
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
    target_line: int
    target_review_state: str
    replacement_review_state: str
    replacement_review_blockers: list[str]
    next_outcome_review_command: str
    checker_errors: list[str]
    inventory_errors: list[str]
    inventory_warnings: list[str]
    errors: list[str]
    replacement_allowed: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a completed harness sample placeholder replacement without writing ledgers."
    )
    parser.add_argument("candidate", help="Path to a single JSON object or one-record JSONL replacement candidate.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def build_report(candidate_path: Path) -> PlaceholderReplacementReport:
    errors: list[str] = []
    candidate = load_candidate(candidate_path, errors)
    sample_id = text(candidate.get("id"))
    gap_id = text(candidate.get("gap_id"))
    schema_version = text(candidate.get("schema_version"))
    source_type = text(candidate.get("source_type"))
    inventory_errors: list[str] = []
    inventory_warnings: list[str] = []
    review = (
        replacement_review_for_candidate(
            candidate,
            sample_id,
            gap_id,
            errors,
            inventory_errors,
            inventory_warnings,
        )
        if candidate
        else harness_sample_review_context.empty_review()
    )
    queue_context = review.queue_context

    blocking_errors = errors + review.checker_errors + inventory_errors
    replacement_allowed = not blocking_errors
    return PlaceholderReplacementReport(
        candidate_path=relative(candidate_path),
        sample_id=sample_id,
        gap_id=gap_id,
        schema_version=schema_version,
        source_type=source_type,
        target_ledger=queue_context.target_ledger,
        ledger_action=queue_context.ledger_action,
        readiness=queue_context.readiness,
        source_metric=queue_context.source_metric,
        current_to_target=queue_context.current_to_target,
        capture_gate=queue_context.capture_gate,
        capture_gate_detail=queue_context.capture_gate_detail,
        evidence_needed=list(queue_context.evidence_needed),
        trigger=queue_context.trigger,
        boundary=queue_context.boundary,
        planner_command=queue_context.planner_command,
        intake_command=queue_context.intake_command,
        target_line=queue_context.target_line,
        target_review_state=queue_context.target_review_state,
        replacement_review_state=review.review_state,
        replacement_review_blockers=review.review_blockers,
        next_outcome_review_command=(
            harness_sample_review_commands.SAMPLE_OUTCOME_REVIEW_COMMAND
            if replacement_allowed
            else "not-applicable"
        ),
        checker_errors=review.checker_errors,
        inventory_errors=inventory_errors,
        inventory_warnings=inventory_warnings,
        errors=errors,
        replacement_allowed=replacement_allowed,
    )


def replacement_review_for_candidate(
    candidate: dict[str, Any],
    sample_id: str,
    gap_id: str,
    errors: list[str],
    inventory_errors: list[str],
    inventory_warnings: list[str],
) -> harness_sample_review_context.CandidateReview:
    slots = harness_sample_slots.load_all_slots(inventory_errors, inventory_warnings)
    target_slot = find_placeholder_slot(sample_id, slots, errors)
    queue_context = replacement_queue_context_for_target(candidate, gap_id, target_slot, errors)
    if text(candidate.get("outcome")) != "pending":
        errors.append("replacement candidate outcome must remain pending until a separate acceptance review")
    review_state = harness_sample_slots.pending_review_state_for_record(candidate)
    review_blockers = list(harness_sample_slots.pending_review_blockers_for_record(candidate))
    if review_state != "review-ready":
        errors.append("replacement candidate must be review-ready before replacing a placeholder")
    return harness_sample_review_context.CandidateReview(
        queue_context=queue_context,
        review_state=review_state,
        review_blockers=review_blockers,
        checker_errors=validate_with_target_checker(candidate),
    )


def replacement_queue_context_for_target(
    candidate: dict[str, Any],
    gap_id: str,
    target_slot: harness_sample_slots.SampleSlot | None,
    errors: list[str],
) -> harness_sample_review_context.SampleReviewContext:
    if target_slot is None:
        return harness_sample_review_context.SampleReviewContext()
    validate_candidate_matches_slot(candidate, target_slot, errors)
    item = expected_replacement_item(gap_id, errors)
    if item is None:
        return harness_sample_review_context.context_for_replacement_target(target_slot)
    return harness_sample_review_context.context_for_replacement_item(target_slot, item)


def load_candidate(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.exists():
        errors.append(f"candidate file missing: {relative(path)}")
        return {}
    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        errors.append("candidate file is empty")
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        lines = [line for line in raw.splitlines() if line.strip()]
        if len(lines) != 1:
            errors.append("candidate must be a single JSON object or one-record JSONL")
            return {}
        try:
            payload = json.loads(lines[0])
        except json.JSONDecodeError as exc:
            errors.append(f"invalid candidate JSON: {exc.msg}")
            return {}
    if not isinstance(payload, dict):
        errors.append("candidate must be a JSON object")
        return {}
    return payload


def find_placeholder_slot(
    sample_id: str,
    slots: list[harness_sample_slots.SampleSlot],
    errors: list[str],
) -> harness_sample_slots.SampleSlot | None:
    if not sample_id:
        errors.append("candidate id must be non-empty text")
        return None
    matches = [slot for slot in slots if slot.sample_id == sample_id and slot.outcome == "pending"]
    if not matches:
        errors.append(f"candidate id does not match an existing pending sample placeholder: {sample_id}")
        return None
    if len(matches) > 1:
        errors.append(f"candidate id matches multiple pending slots: {sample_id}")
        return None
    slot = matches[0]
    if slot.pending_review_state != "placeholder":
        errors.append(f"target pending slot must be placeholder, got {slot.pending_review_state}")
    return slot


def validate_candidate_matches_slot(
    candidate: dict[str, Any],
    slot: harness_sample_slots.SampleSlot,
    errors: list[str],
) -> None:
    candidate_gap = text(candidate.get("gap_id"))
    if not candidate_gap:
        errors.append("candidate gap_id must be non-empty text")
    elif candidate_gap != slot.gap_id:
        errors.append(f"candidate gap_id {candidate_gap} does not match placeholder gap {slot.gap_id}")
    candidate_source_type = text(candidate.get("source_type"))
    if candidate_source_type != slot.source_type:
        errors.append(f"candidate source_type {candidate_source_type or '<missing>'} does not match placeholder source_type {slot.source_type}")
    target_schema = schema_for_ledger(slot.ledger_path)
    candidate_schema = text(candidate.get("schema_version"))
    if target_schema and candidate_schema != target_schema:
        errors.append(f"candidate schema_version {candidate_schema or '<missing>'} does not match target ledger schema {target_schema}")


def expected_replacement_item(
    gap_id: str,
    errors: list[str],
) -> plan_harness_sample_collection.CollectionItem | None:
    if not gap_id:
        return None
    matches = plan_harness_sample_collection.build_queue(
        gap_ids={gap_id},
        ledger_actions={"fill-existing-placeholder"},
        actionable_only=True,
        pending_state="with-placeholder-pending",
    )
    if len(matches) == 1:
        return matches[0]
    explain_non_replacement_lane(gap_id, errors)
    return None


def explain_non_replacement_lane(gap_id: str, errors: list[str]) -> None:
    items = plan_harness_sample_collection.build_queue(
        gap_ids={gap_id},
        include_future=True,
        include_accepted=True,
    )
    if not items:
        errors.append(f"candidate gap is not in the current sample collection queue: {gap_id}")
        return
    item = items[0]
    errors.append(
        "candidate gap is not in fill-existing-placeholder lane: "
        f"{gap_id} has ledger_action={item.ledger_action}, readiness={item.readiness}, "
        f"pending_slot_status={item.pending_slot_status}"
    )


def schema_for_ledger(ledger_path: str) -> str:
    for spec in harness_sample_slots.LEDGERS:
        if harness_sample_slots.relative(spec.path) == ledger_path:
            return spec.schema_version
    return ""


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


def emit_text(report: PlaceholderReplacementReport) -> None:
    print("Harness placeholder replacement review:")
    print(f"- candidate: {report.candidate_path}")
    print(f"- sample id: {report.sample_id or '<missing>'}")
    print(f"- gap id: {report.gap_id or '<missing>'}")
    print(f"- schema: {report.schema_version or '<missing>'}")
    print(f"- source type: {report.source_type or '<missing>'}")
    print(f"- ledger action: {report.ledger_action or '<not resolved>'}")
    print(f"- readiness: {report.readiness or '<not resolved>'}")
    print(f"- source metric: {report.source_metric or '<not resolved>'}")
    print(f"- current / target: {report.current_to_target or '<not resolved>'}")
    print(f"- capture gate: {report.capture_gate or '<not resolved>'}")
    print(f"- capture gate detail: {report.capture_gate_detail or '<not resolved>'}")
    if report.evidence_needed:
        print(f"- evidence needed: {'; '.join(report.evidence_needed)}")
    else:
        print("- evidence needed: <not resolved>")
    print(f"- trigger: {report.trigger or '<not resolved>'}")
    print(f"- boundary: {report.boundary or '<not resolved>'}")
    print(f"- planner command: `{report.planner_command or '<not resolved>'}`")
    print(f"- intake command: `{report.intake_command or '<not resolved>'}`")
    if report.target_ledger:
        print(f"- target placeholder: {report.target_ledger}:{report.target_line}")
        print(f"- target review state: {report.target_review_state}")
    else:
        print("- target placeholder: <not found>")
    print(f"- replacement review state: {report.replacement_review_state or '<unknown>'}")
    if report.replacement_review_blockers:
        print(f"- replacement review blockers: {'; '.join(report.replacement_review_blockers)}")
    else:
        print("- replacement review blockers: none")
    print(f"- next outcome review command: `{report.next_outcome_review_command}`")
    print(f"- replacement allowed: {'yes' if report.replacement_allowed else 'no'}")
    for warning in report.inventory_warnings:
        print(f"WARN: {warning}")
    for error in report.inventory_errors:
        print(f"ERROR: {error}")
    for error in report.checker_errors:
        print(f"ERROR: {error}")
    for error in report.errors:
        print(f"ERROR: {error}")
    if report.replacement_allowed:
        print("ERRORS: none")


def main() -> int:
    args = parse_args()
    report = build_report(Path(args.candidate).expanduser())
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        emit_text(report)
    return 0 if report.replacement_allowed else 1


if __name__ == "__main__":
    sys.exit(main())
