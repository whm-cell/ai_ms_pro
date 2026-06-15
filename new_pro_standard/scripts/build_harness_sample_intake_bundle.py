#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import sys

import check_harness_future_work_contracts as future_contracts
import check_harness_sample_templates
import harness_collection_lane_commands
import harness_future_work_contract_states as contract_state_report
import harness_sample_intake_render
import harness_sample_review_commands
import harness_sample_slots
import harness_sample_templates
import plan_harness_sample_collection


@dataclass(frozen=True)
class PendingSlotRef:
    sample_id: str
    review_state: str
    review_blockers: tuple[str, ...]
    evidence_class: str
    source_type: str
    ledger_ref: str


@dataclass(frozen=True)
class BundleEntry:
    gap_id: str
    priority: str
    area: str
    readiness: str
    source_metric: str
    accepted_count: int
    upgrade_discussion_target: int
    current_to_target: str
    readiness_metric_delta: str
    target_artifact: str
    schema_version: str
    source_type: str
    capture_gate: str
    capture_gate_detail: str
    trigger: str
    evidence_needed: list[str]
    boundary: str
    review_command: str
    replacement_review_command: str
    append_review_command: str
    outcome_review_command: str
    upgrade_decision_review_command: str
    contract_precondition_review_command: str
    pending_slot_status: str
    pending_slot_count: int
    ledger_action: str
    contract_blocker_state: contract_state_report.FutureContractState | None
    pending_slots: list[PendingSlotRef]
    template_review_state: str
    template_review_blockers: tuple[str, ...]
    validation_errors: list[str]
    template: dict[str, object]


@dataclass(frozen=True)
class BundleTarget:
    target_artifact: str
    entry_count: int
    entries: list[BundleEntry]


@dataclass(frozen=True)
class BundleReport:
    sampled_at: str
    item_count: int
    target_count: int
    priority_counts: dict[str, int]
    pending_slot_status_counts: dict[str, int]
    ledger_action_counts: dict[str, int]
    capture_gate_counts: dict[str, int]
    readiness_counts: dict[str, int]
    schema_counts: dict[str, int]
    template_review_state_counts: dict[str, int]
    targets: list[BundleTarget]
    errors: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a grouped stdout-only harness sample intake bundle.")
    parser.add_argument("--area", action="append", default=[], help="Filter by gap area. Repeatable.")
    parser.add_argument(
        "--priority",
        action="append",
        choices=plan_harness_sample_collection.PRIORITY_LEVELS,
        default=[],
        help="Filter by collection priority.",
    )
    parser.add_argument(
        "--ledger-action",
        action="append",
        choices=plan_harness_sample_collection.LEDGER_ACTIONS,
        default=[],
        help="Filter by ledger action routing.",
    )
    parser.add_argument(
        "--capture-gate",
        action="append",
        choices=plan_harness_sample_collection.CAPTURE_GATES,
        default=[],
        help="Filter by real-event capture gate.",
    )
    parser.add_argument(
        "--readiness",
        action="append",
        choices=plan_harness_sample_collection.READINESS_STATES,
        default=[],
        help="Filter by readiness state.",
    )
    parser.add_argument("--gap-id", action="append", default=[], help="Filter by exact gap id. Repeatable.")
    parser.add_argument(
        "--pending-state",
        choices=plan_harness_sample_collection.PENDING_STATES,
        default="without-review-ready-pending",
        help="Filter by existing pending sample slot coverage.",
    )
    parser.add_argument("--sampled-at", help="YYYY-MM-DD date used in generated template ids. Defaults to today's date.")
    parser.add_argument("--summary", action="store_true", help="Emit compact markdown without JSONL templates.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def build_report(
    sampled_at: str | None = None,
    gap_ids: set[str] | None = None,
    *,
    areas: set[str] | None = None,
    priorities: set[str] | None = None,
    ledger_actions: set[str] | None = None,
    capture_gates: set[str] | None = None,
    readinesses: set[str] | None = None,
    pending_state: str = "without-review-ready-pending",
) -> BundleReport:
    sampled_at = sampled_at or harness_sample_templates.default_sampled_at()
    selected_ledger_actions = ledger_actions or set()
    selected_readinesses = readinesses or set()
    include_contract_preconditions = "define-contract-precondition" in selected_ledger_actions
    include_upgrade_decisions = (
        "review-upgrade-decision" in selected_ledger_actions
        or "ready-for-upgrade-discussion" in selected_readinesses
    )
    items = plan_harness_sample_collection.build_queue(
        areas=areas or set(),
        gap_ids=gap_ids or set(),
        priorities=priorities or set(),
        ledger_actions=selected_ledger_actions,
        capture_gates=capture_gates or set(),
        readinesses=selected_readinesses,
        include_future=True,
        include_accepted=True,
        actionable_only=False,
        pending_state=pending_state,
    )
    items = filter_bundle_items(items, include_contract_preconditions, include_upgrade_decisions)
    pending_slots, inventory_errors = load_pending_slots()
    contract_states, contract_errors = load_contract_blocker_states(include_contract_preconditions)
    entries = [build_entry(item, sampled_at, pending_slots, contract_states) for item in items]
    schema_counts: dict[str, int] = {}
    errors: list[str] = [*inventory_errors, *contract_errors]
    for entry in entries:
        schema_counts[entry.schema_version] = schema_counts.get(entry.schema_version, 0) + 1
        errors.extend(f"{entry.gap_id}: {error}" for error in entry.validation_errors)
    targets = []
    for target_artifact in sorted({entry.target_artifact for entry in entries}):
        target_entries = [entry for entry in entries if entry.target_artifact == target_artifact]
        targets.append(BundleTarget(target_artifact, len(target_entries), target_entries))
    return BundleReport(
        sampled_at=sampled_at,
        item_count=len(entries),
        target_count=len(targets),
        priority_counts=count_entries(entries, "priority"),
        pending_slot_status_counts=count_entries(entries, "pending_slot_status"),
        ledger_action_counts=count_entries(entries, "ledger_action"),
        capture_gate_counts=count_entries(entries, "capture_gate"),
        readiness_counts=count_entries(entries, "readiness"),
        schema_counts=dict(sorted(schema_counts.items())),
        template_review_state_counts=count_entries(entries, "template_review_state"),
        targets=targets,
        errors=errors,
    )


def filter_bundle_items(
    items: list[plan_harness_sample_collection.CollectionItem],
    include_contract_preconditions: bool,
    include_upgrade_decisions: bool,
) -> list[plan_harness_sample_collection.CollectionItem]:
    return [
        item
        for item in items
        if plan_harness_sample_collection.is_actionable_sample_item(item)
        or (include_contract_preconditions and item.ledger_action == "define-contract-precondition")
        or (include_upgrade_decisions and item.ledger_action == "review-upgrade-decision")
    ]


def build_entry(
    item: plan_harness_sample_collection.CollectionItem,
    sampled_at: str,
    pending_slots: dict[str, list[PendingSlotRef]],
    contract_states: dict[str, contract_state_report.FutureContractState],
) -> BundleEntry:
    template = harness_sample_templates.sample_template(item, sampled_at)
    validation = check_harness_sample_templates.validate_item(item, sampled_at)
    slots = pending_slots.get(item.gap_id, [])
    template_review_state, template_review_blockers = template_review_state_for(template)
    return BundleEntry(
        gap_id=item.gap_id,
        priority=item.priority,
        area=item.area,
        readiness=item.readiness,
        source_metric=item.source_metric,
        accepted_count=item.accepted_count,
        upgrade_discussion_target=item.upgrade_discussion_target,
        current_to_target=current_to_target(item),
        readiness_metric_delta=item.readiness_metric_delta,
        target_artifact=item.target_artifact,
        schema_version=str(template.get("schema_version", "")),
        source_type=str(template.get("source_type", "")),
        capture_gate=item.capture_gate,
        capture_gate_detail=item.capture_gate_detail,
        trigger=item.trigger,
        evidence_needed=item.evidence_needed,
        boundary=item.boundary,
        review_command=harness_sample_review_commands.review_command_for(item.target_artifact),
        **harness_collection_lane_commands.lane_review_command_fields(item.ledger_action),
        pending_slot_status=pending_slot_status(slots),
        pending_slot_count=len(slots),
        ledger_action=item.ledger_action,
        contract_blocker_state=contract_states.get(item.gap_id),
        pending_slots=slots,
        template_review_state=template_review_state,
        template_review_blockers=template_review_blockers,
        validation_errors=validation.errors,
        template=template,
    )


def current_to_target(item: plan_harness_sample_collection.CollectionItem) -> str:
    if item.upgrade_discussion_target:
        return f"{item.accepted_count}/{item.upgrade_discussion_target}"
    return str(item.accepted_count)


def template_review_state_for(template: dict[str, object]) -> tuple[str, tuple[str, ...]]:
    if template.get("outcome") != "pending":
        return "not-applicable", ()
    return (
        harness_sample_slots.pending_review_state_for_record(template),
        harness_sample_slots.pending_review_blockers_for_record(template),
    )


def load_contract_blocker_states(
    include_contract_preconditions: bool,
) -> tuple[dict[str, contract_state_report.FutureContractState], list[str]]:
    if not include_contract_preconditions:
        return {}, []
    report = future_contracts.build_report()
    states = {state.gap_id: state for state in report.contract_states}
    errors = [f"future_contracts: {error}" for error in report.errors]
    return states, errors


def load_pending_slots() -> tuple[dict[str, list[PendingSlotRef]], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    slots_by_gap: dict[str, list[PendingSlotRef]] = {}
    for slot in harness_sample_slots.load_all_slots(errors, warnings):
        if slot.outcome != "pending":
            continue
        slots_by_gap.setdefault(slot.gap_id, []).append(
            PendingSlotRef(
                sample_id=slot.sample_id,
                review_state=slot.pending_review_state,
                review_blockers=slot.review_blockers,
                evidence_class=slot.evidence_class,
                source_type=slot.source_type,
                ledger_ref=f"{slot.ledger_path}:{slot.line}",
            )
        )
    sorted_slots = {
        gap_id: sorted(slots, key=lambda slot: (slot.review_state, slot.ledger_ref, slot.sample_id))
        for gap_id, slots in slots_by_gap.items()
    }
    return sorted_slots, errors


def pending_slot_status(slots: list[PendingSlotRef]) -> str:
    states = sorted({slot.review_state for slot in slots})
    if not states:
        return "none"
    if states == ["placeholder"]:
        return "placeholder"
    if states == ["review-ready"]:
        return "review-ready"
    return "mixed"


def count_entries(entries: list[BundleEntry], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for entry in entries:
        value = str(getattr(entry, field))
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def emit_text(report: BundleReport) -> None:
    harness_sample_intake_render.emit_text(report)


def emit_summary(report: BundleReport) -> None:
    harness_sample_intake_render.emit_summary(report)


def main() -> int:
    args = parse_args()
    report = build_report(
        args.sampled_at,
        set(args.gap_id),
        areas=set(args.area),
        priorities=set(args.priority),
        ledger_actions=set(args.ledger_action),
        capture_gates=set(args.capture_gate),
        readinesses=set(args.readiness),
        pending_state=args.pending_state,
    )
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    elif args.summary:
        emit_summary(report)
    else:
        emit_text(report)
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
