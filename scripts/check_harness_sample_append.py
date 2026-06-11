#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys
from typing import Any

import check_harness_sample_templates
import check_harness_placeholder_replacement
import harness_sample_review_context
import harness_sample_review_commands
import harness_sample_slots
import harness_sample_templates
import plan_harness_sample_collection


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class SampleAppendReport:
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
    append_review_state: str
    append_review_blockers: list[str]
    review_command: str
    next_outcome_review_command: str
    checker_errors: list[str]
    inventory_errors: list[str]
    inventory_warnings: list[str]
    errors: list[str]
    append_allowed: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a new pending harness sample append without writing ledgers.")
    parser.add_argument("candidate", help="Path to a single JSON object or one-record JSONL append candidate.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def build_report(candidate_path: Path) -> SampleAppendReport:
    errors: list[str] = []
    candidate = check_harness_placeholder_replacement.load_candidate(candidate_path, errors)
    sample_id = text(candidate.get("id"))
    schema_version = text(candidate.get("schema_version"))
    source_type = text(candidate.get("source_type"))
    gap_id = gap_for_candidate(candidate, errors) if candidate else ""
    inventory_errors: list[str] = []
    inventory_warnings: list[str] = []
    review = (
        append_review_for_candidate(
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
    append_allowed = not blocking_errors
    return SampleAppendReport(
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
        append_review_state=review.review_state,
        append_review_blockers=review.review_blockers,
        review_command=queue_context.review_command,
        next_outcome_review_command=(
            harness_sample_review_commands.SAMPLE_OUTCOME_REVIEW_COMMAND
            if append_allowed
            else "not-applicable"
        ),
        checker_errors=review.checker_errors,
        inventory_errors=inventory_errors,
        inventory_warnings=inventory_warnings,
        errors=errors,
        append_allowed=append_allowed,
    )


def append_review_for_candidate(
    candidate: dict[str, Any],
    sample_id: str,
    gap_id: str,
    errors: list[str],
    inventory_errors: list[str],
    inventory_warnings: list[str],
) -> harness_sample_review_context.CandidateReview:
    slots = harness_sample_slots.load_all_slots(inventory_errors, inventory_warnings)
    validate_new_sample_id(sample_id, slots, errors)
    queue_context = append_queue_context_for_candidate(candidate, gap_id, errors)
    if text(candidate.get("outcome")) != "pending":
        errors.append("append candidate outcome must remain pending until a separate acceptance review")
    review_state = harness_sample_slots.pending_review_state_for_record(candidate)
    review_blockers = list(harness_sample_slots.pending_review_blockers_for_record(candidate))
    if review_state != "review-ready":
        errors.append("append candidate must be review-ready before appending a new pending row")
    return harness_sample_review_context.CandidateReview(
        queue_context=queue_context,
        review_state=review_state,
        review_blockers=review_blockers,
        checker_errors=validate_with_target_checker(candidate),
    )


def append_queue_context_for_candidate(
    candidate: dict[str, Any],
    gap_id: str,
    errors: list[str],
) -> harness_sample_review_context.SampleReviewContext:
    item = expected_append_item(gap_id, errors)
    if item is None:
        return harness_sample_review_context.SampleReviewContext()
    validate_candidate_matches_item(candidate, item, errors)
    return harness_sample_review_context.context_for_append_item(item)


def gap_for_candidate(candidate: dict[str, Any], errors: list[str]) -> str:
    explicit_gap = text(candidate.get("gap_id"))
    if explicit_gap:
        return explicit_gap
    schema = text(candidate.get("schema_version"))
    spec = spec_for_schema(schema)
    if spec is None:
        errors.append(f"cannot derive gap_id for unsupported schema_version: {schema or '<missing>'}")
        return ""
    gap_id = harness_sample_slots.gap_for_record(spec, candidate)
    if not gap_id:
        errors.append("candidate gap_id must be non-empty text or derivable from its ledger schema")
    return gap_id


def spec_for_schema(schema_version: str) -> harness_sample_slots.LedgerSpec | None:
    for spec in harness_sample_slots.LEDGERS:
        if spec.schema_version == schema_version:
            return spec
    return None


def validate_new_sample_id(
    sample_id: str,
    slots: list[harness_sample_slots.SampleSlot],
    errors: list[str],
) -> None:
    if not sample_id:
        errors.append("candidate id must be non-empty text")
        return
    matches = [slot for slot in slots if slot.sample_id == sample_id]
    if matches:
        refs = ", ".join(f"{slot.ledger_path}:{slot.line}" for slot in matches)
        errors.append(f"candidate id already exists in sample ledgers: {sample_id} ({refs})")


def expected_append_item(
    gap_id: str,
    errors: list[str],
) -> plan_harness_sample_collection.CollectionItem | None:
    if not gap_id:
        return None
    matches = plan_harness_sample_collection.build_queue(
        gap_ids={gap_id},
        ledger_actions={"append-new-pending-slot"},
        actionable_only=True,
        pending_state="without-pending",
    )
    if len(matches) == 1:
        return matches[0]
    explain_non_append_lane(gap_id, errors)
    return None


def explain_non_append_lane(gap_id: str, errors: list[str]) -> None:
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
        "candidate gap is not in append-new-pending-slot lane: "
        f"{gap_id} has ledger_action={item.ledger_action}, readiness={item.readiness}, "
        f"pending_slot_status={item.pending_slot_status}"
    )


def validate_candidate_matches_item(
    candidate: dict[str, Any],
    item: plan_harness_sample_collection.CollectionItem,
    errors: list[str],
) -> None:
    target_schema = check_harness_placeholder_replacement.schema_for_ledger(item.target_artifact)
    candidate_schema = text(candidate.get("schema_version"))
    if target_schema and candidate_schema != target_schema:
        errors.append(f"candidate schema_version {candidate_schema or '<missing>'} does not match target ledger schema {target_schema}")

    expected_template = expected_template_for(item)
    expected_source_type = text(expected_template.get("source_type"))
    candidate_source_type = text(candidate.get("source_type"))
    if expected_source_type and candidate_source_type != expected_source_type:
        errors.append(
            f"candidate source_type {candidate_source_type or '<missing>'} does not match expected source_type "
            f"{expected_source_type}"
        )


def expected_template_for(item: plan_harness_sample_collection.CollectionItem) -> dict[str, object]:
    return harness_sample_templates.sample_template(item, harness_sample_templates.default_sampled_at())


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


def emit_text(report: SampleAppendReport) -> None:
    print("Harness sample append review:")
    print(f"- candidate: {report.candidate_path}")
    print(f"- sample id: {report.sample_id or '<missing>'}")
    print(f"- gap id: {report.gap_id or '<missing>'}")
    print(f"- schema: {report.schema_version or '<missing>'}")
    print(f"- source type: {report.source_type or '<missing>'}")
    print(f"- target ledger: {report.target_ledger or '<not resolved>'}")
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
    print(f"- review command: {report.review_command or '<not resolved>'}")
    print(f"- next outcome review command: `{report.next_outcome_review_command}`")
    print(f"- append review state: {report.append_review_state or '<unknown>'}")
    if report.append_review_blockers:
        print(f"- append review blockers: {'; '.join(report.append_review_blockers)}")
    else:
        print("- append review blockers: none")
    print(f"- append allowed: {'yes' if report.append_allowed else 'no'}")
    for warning in report.inventory_warnings:
        print(f"WARN: {warning}")
    for error in report.inventory_errors:
        print(f"ERROR: {error}")
    for error in report.checker_errors:
        print(f"ERROR: {error}")
    for error in report.errors:
        print(f"ERROR: {error}")
    if report.append_allowed:
        print("ERRORS: none")


def main() -> int:
    args = parse_args()
    report = build_report(Path(args.candidate).expanduser())
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        emit_text(report)
    return 0 if report.append_allowed else 1


if __name__ == "__main__":
    sys.exit(main())
