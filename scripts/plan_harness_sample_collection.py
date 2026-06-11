#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys

import check_harness_burn_in_readiness
import check_harness_future_work_contracts as future_contracts
import collect_harness_sample_gaps
import harness_collection_lane_commands
from harness_burn_in_readiness_types import READINESS_STATES
from harness_sample_collection_items import (
    CollectionItem,
    boundary_for,
    capture_gate_for,
    evidence_needed_for,
    is_actionable_sample_item,
    ledger_action_for,
    priority_for,
    sort_key,
    source_type_for,
    target_for,
    trigger_for,
)
from harness_sample_collection_config import (
    CAPTURE_GATES,
    LEDGER_ACTIONS,
    PENDING_STATES,
    PRIORITY_LEVELS,
)
from harness_sample_collection_render import emit_capture_cards, emit_json, emit_markdown
import harness_sample_pending_summaries
import harness_sample_review_commands
from harness_sample_templates import emit_sample_templates


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Plan the next real harness sample collection targets.")
    parser.add_argument("--area", action="append", default=[], help="Filter by gap area. Repeatable.")
    parser.add_argument("--priority", action="append", choices=PRIORITY_LEVELS, default=[], help="Filter by priority.")
    parser.add_argument(
        "--ledger-action",
        action="append",
        choices=LEDGER_ACTIONS,
        default=[],
        help="Filter by ledger action routing. Repeatable.",
    )
    parser.add_argument(
        "--capture-gate",
        action="append",
        choices=CAPTURE_GATES,
        default=[],
        help="Filter by real-event capture gate. Repeatable.",
    )
    parser.add_argument(
        "--readiness",
        action="append",
        choices=READINESS_STATES,
        default=[],
        help="Filter by readiness state. Repeatable.",
    )
    parser.add_argument("--gap-id", action="append", default=[], help="Filter by exact gap id. Repeatable.")
    parser.add_argument("--include-future", action="store_true", help="Include future-work gaps.")
    parser.add_argument("--include-accepted", action="store_true", help="Include already accepted local/real gaps.")
    parser.add_argument("--actionable-only", action="store_true", help="Only include real sample gaps that can be acted on now.")
    parser.add_argument(
        "--pending-state",
        choices=PENDING_STATES,
        default="any",
        help="Filter by existing pending sample slot coverage.",
    )
    parser.add_argument("--capture-card", action="store_true", help="Emit detailed capture cards instead of the queue table.")
    parser.add_argument("--sample-template", action="store_true", help="Emit JSONL draft templates for selected gaps.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def build_queue(
    areas: set[str] | None = None,
    gap_ids: set[str] | None = None,
    *,
    priorities: set[str] | None = None,
    ledger_actions: set[str] | None = None,
    capture_gates: set[str] | None = None,
    readinesses: set[str] | None = None,
    include_future: bool = False,
    include_accepted: bool = False,
    actionable_only: bool = False,
    pending_state: str = "any",
) -> list[CollectionItem]:
    gaps = collect_harness_sample_gaps.select_gaps(areas or set())
    readiness_report = check_harness_burn_in_readiness.build_report(include_future=True, include_accepted=True)
    readiness_by_gap = {item.gap_id: item for item in readiness_report.items}
    contract_states = {state.gap_id: state for state in future_contracts.build_report().contract_states}
    pending_slots_by_gap = harness_sample_pending_summaries.build_by_gap()
    items = [
        build_item(
            gap,
            readiness_by_gap[gap.id],
            pending_slots_by_gap.get(gap.id, harness_sample_pending_summaries.EMPTY_PENDING_SLOT_SUMMARY),
            contract_states,
            readiness_report.accepted_real_readiness_metric_deltas.get(gap.id, ""),
        )
        for gap in gaps
        if (not gap_ids or gap.id in gap_ids) and include_gap(gap, include_future, include_accepted, contract_states)
    ]
    items = filter_actionable(items, actionable_only)
    items = filter_pending_state(items, pending_state)
    items = filter_priority(items, priorities or set())
    items = filter_ledger_action(items, ledger_actions or set())
    items = filter_capture_gate(items, capture_gates or set())
    items = filter_readiness(items, readinesses or set())
    return sorted(items, key=sort_key)


def include_gap(
    gap: collect_harness_sample_gaps.SampleGap,
    include_future: bool,
    include_accepted: bool,
    contract_states: dict[str, object],
) -> bool:
    if gap.status.startswith("accepted-"):
        return include_accepted
    if gap.status == "future-work":
        state = contract_states.get(gap.id)
        if state and getattr(state, "sample_collection_allowed", False):
            return True
        return include_future
    return True


def filter_actionable(items: list[CollectionItem], actionable_only: bool) -> list[CollectionItem]:
    if not actionable_only:
        return items
    return [item for item in items if is_actionable_sample_item(item)]


def filter_pending_state(items: list[CollectionItem], pending_state: str) -> list[CollectionItem]:
    if pending_state == "any":
        return items
    if pending_state == "with-pending":
        return [item for item in items if item.pending_slot_count > 0]
    if pending_state == "without-pending":
        return [item for item in items if item.pending_slot_count == 0]
    if pending_state == "with-review-ready-pending":
        return [item for item in items if "review-ready" in item.pending_review_states]
    if pending_state == "without-review-ready-pending":
        return [item for item in items if "review-ready" not in item.pending_review_states]
    if pending_state == "with-placeholder-pending":
        return [item for item in items if "placeholder" in item.pending_review_states]
    if pending_state == "without-placeholder-pending":
        return [item for item in items if "placeholder" not in item.pending_review_states]
    raise ValueError(f"unsupported pending state: {pending_state}")


def filter_priority(items: list[CollectionItem], priorities: set[str]) -> list[CollectionItem]:
    if not priorities:
        return items
    return [item for item in items if item.priority in priorities]


def filter_ledger_action(items: list[CollectionItem], ledger_actions: set[str]) -> list[CollectionItem]:
    if not ledger_actions:
        return items
    return [item for item in items if item.ledger_action in ledger_actions]


def filter_capture_gate(items: list[CollectionItem], capture_gates: set[str]) -> list[CollectionItem]:
    if not capture_gates:
        return items
    return [item for item in items if item.capture_gate in capture_gates]


def filter_readiness(items: list[CollectionItem], readinesses: set[str]) -> list[CollectionItem]:
    if not readinesses:
        return items
    return [item for item in items if item.readiness in readinesses]

def build_item(
    gap: collect_harness_sample_gaps.SampleGap,
    readiness_item: check_harness_burn_in_readiness.ReadinessItem,
    pending_slot_summary: harness_sample_pending_summaries.PendingSlotSummary,
    contract_states: dict[str, object],
    readiness_metric_delta: str,
) -> CollectionItem:
    target_artifact = target_for(gap, readiness_item)
    source_type = source_type_for(gap, readiness_item)
    ledger_action = ledger_action_for(readiness_item.readiness, source_type, pending_slot_summary)
    capture_gate, capture_gate_detail = capture_gate_for(gap, readiness_item, ledger_action, source_type)
    return CollectionItem(
        gap_id=gap.id,
        area=gap.area,
        priority=priority_for(gap),
        readiness=readiness_item.readiness,
        source_metric=readiness_item.source_metric,
        accepted_count=readiness_item.accepted_count,
        upgrade_discussion_target=readiness_item.upgrade_discussion_target,
        readiness_metric_delta=readiness_metric_delta,
        target_artifact=target_artifact,
        review_command=harness_sample_review_commands.review_command_for(target_artifact),
        **harness_collection_lane_commands.lane_review_command_fields(ledger_action),
        pending_slot_status=pending_slot_summary.status,
        pending_slot_count=pending_slot_summary.count,
        pending_review_states=pending_slot_summary.review_states,
        pending_slot_refs=pending_slot_summary.refs,
        pending_review_blockers=pending_slot_summary.review_blockers,
        ledger_action=ledger_action,
        contract_blocker_state=contract_states.get(gap.id)
        if ledger_action == "define-contract-precondition"
        else None,
        source_type_needed=source_type,
        capture_gate=capture_gate,
        capture_gate_detail=capture_gate_detail,
        trigger=trigger_for(gap, readiness_item),
        evidence_needed=evidence_needed_for(gap, readiness_item),
        next_evidence_needed=readiness_item.next_evidence_needed,
        current_evidence=readiness_item.current_evidence,
        boundary=boundary_for(gap, readiness_item),
    )


def main() -> int:
    args = parse_args()
    items = build_queue(
        set(args.area),
        set(args.gap_id),
        priorities=set(args.priority),
        ledger_actions=set(args.ledger_action),
        capture_gates=set(args.capture_gate),
        readinesses=set(args.readiness),
        include_future=args.include_future,
        include_accepted=args.include_accepted,
        actionable_only=args.actionable_only,
        pending_state=args.pending_state,
    )
    if args.sample_template:
        emit_sample_templates(items)
    elif args.json:
        emit_json(items)
    elif args.capture_card:
        emit_capture_cards(items)
    else:
        emit_markdown(items)
    return 0


if __name__ == "__main__":
    sys.exit(main())
