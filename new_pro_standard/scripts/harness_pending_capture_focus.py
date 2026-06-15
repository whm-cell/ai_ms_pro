#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass

import harness_pending_queue_state
import harness_collection_lane_commands
import harness_pending_capture_focus_filters as focus_filters
import harness_pending_capture_focus_slots as focus_slots
import harness_sample_slots
from harness_burn_in_readiness_types import READINESS_STATES
from harness_sample_collection_config import CAPTURE_GATES
import plan_harness_sample_collection


CAPTURE_FOCUS_LIMIT = 5
CAPTURE_FOCUS_AREAS = (
    "agentic-red-team",
    "ai-guardrail",
    "runtime-durability",
    "security-evidence",
    "trace-interop",
    "workflow-skills",
)
CAPTURE_FOCUS_PRIORITIES = ("P0", "P1", "P2", "P3")
CAPTURE_FOCUS_LEDGER_ACTIONS = ("fill-existing-placeholder", "append-new-pending-slot")
CAPTURE_FOCUS_CAPTURE_GATES = CAPTURE_GATES
CAPTURE_FOCUS_READINESS_STATES = READINESS_STATES


@dataclass(frozen=True)
class CaptureFocusItem:
    gap_id: str
    area: str
    priority: str
    ledger_action: str
    readiness: str
    source_metric: str
    current_to_target: str
    readiness_metric_delta: str
    pending_slot_status: str
    pending_slot_refs: tuple[str, ...]
    pending_review_blockers: tuple[str, ...]
    source_type_needed: str
    capture_gate: str
    capture_gate_detail: str
    target_artifact: str
    review_command: str
    lane_review_command: str
    planner_command: str
    intake_command: str
    evidence_needed: list[str]
    trigger: str
    boundary: str
    reason: str


@dataclass(frozen=True)
class CaptureFocusSelection:
    items: list[CaptureFocusItem]
    hidden_gap_ids: tuple[str, ...]
    available_count: int
    limit: int
    truncated: bool
    shown_priority_counts: dict[str, int]
    available_priority_counts: dict[str, int]
    shown_area_counts: dict[str, int]
    available_area_counts: dict[str, int]
    shown_ledger_action_counts: dict[str, int]
    available_ledger_action_counts: dict[str, int]
    shown_capture_gate_counts: dict[str, int]
    available_capture_gate_counts: dict[str, int]
    shown_readiness_counts: dict[str, int]
    available_readiness_counts: dict[str, int]


def build_next_capture_focus_selection(
    queued_items: list[plan_harness_sample_collection.CollectionItem],
    queue_state: harness_pending_queue_state.QueueState,
    *,
    limit: int = CAPTURE_FOCUS_LIMIT,
    areas: set[str] | None = None,
    priorities: set[str] | None = None,
    ledger_actions: set[str] | None = None,
    capture_gates: set[str] | None = None,
    readinesses: set[str] | None = None,
    pending_slots: list[harness_sample_slots.SampleSlot] | None = None,
    readiness_metric_deltas: dict[str, str] | None = None,
) -> CaptureFocusSelection:
    if limit < 0:
        raise ValueError("capture focus limit must be zero or greater")
    area_filter = focus_filters.normalize_focus_filter(areas, CAPTURE_FOCUS_AREAS, "capture focus area")
    priority_filter = focus_filters.normalize_focus_filter(priorities, CAPTURE_FOCUS_PRIORITIES, "capture focus priority")
    ledger_action_filter = focus_filters.normalize_focus_filter(
        ledger_actions,
        CAPTURE_FOCUS_LEDGER_ACTIONS,
        "capture focus ledger action",
    )
    capture_gate_filter = focus_filters.normalize_focus_filter(
        capture_gates,
        CAPTURE_FOCUS_CAPTURE_GATES,
        "capture focus gate",
    )
    readiness_filter = focus_filters.normalize_focus_filter(
        readinesses, CAPTURE_FOCUS_READINESS_STATES, "capture focus readiness"
    )
    all_items = build_all_next_capture_focus(
        queued_items,
        queue_state,
        areas=area_filter,
        priorities=priority_filter,
        ledger_actions=ledger_action_filter,
        capture_gates=capture_gate_filter,
        readinesses=readiness_filter,
        pending_slots=pending_slots,
        readiness_metric_deltas=readiness_metric_deltas,
    )
    items = all_items if limit == 0 else all_items[:limit]
    hidden_items = [] if limit == 0 else all_items[limit:]
    return CaptureFocusSelection(
        items=items,
        hidden_gap_ids=tuple(item.gap_id for item in hidden_items),
        available_count=len(all_items),
        limit=limit,
        truncated=bool(limit and len(items) < len(all_items)),
        shown_priority_counts=focus_filters.count_focus_items(items, "priority"),
        available_priority_counts=focus_filters.count_focus_items(all_items, "priority"),
        shown_area_counts=focus_filters.count_focus_items(items, "area"),
        available_area_counts=focus_filters.count_focus_items(all_items, "area"),
        shown_ledger_action_counts=focus_filters.count_focus_items(items, "ledger_action"),
        available_ledger_action_counts=focus_filters.count_focus_items(all_items, "ledger_action"),
        shown_capture_gate_counts=focus_filters.count_focus_items(items, "capture_gate"),
        available_capture_gate_counts=focus_filters.count_focus_items(all_items, "capture_gate"),
        shown_readiness_counts=focus_filters.count_focus_items(items, "readiness"),
        available_readiness_counts=focus_filters.count_focus_items(all_items, "readiness"),
    )


def build_all_next_capture_focus(
    queued_items: list[plan_harness_sample_collection.CollectionItem],
    queue_state: harness_pending_queue_state.QueueState,
    *,
    areas: set[str] | None = None,
    priorities: set[str] | None = None,
    ledger_actions: set[str] | None = None,
    capture_gates: set[str] | None = None,
    readinesses: set[str] | None = None,
    pending_slots: list[harness_sample_slots.SampleSlot] | None = None,
    readiness_metric_deltas: dict[str, str] | None = None,
) -> list[CaptureFocusItem]:
    area_filter = focus_filters.normalize_focus_filter(areas, CAPTURE_FOCUS_AREAS, "capture focus area")
    priority_filter = focus_filters.normalize_focus_filter(priorities, CAPTURE_FOCUS_PRIORITIES, "capture focus priority")
    ledger_action_filter = focus_filters.normalize_focus_filter(
        ledger_actions,
        CAPTURE_FOCUS_LEDGER_ACTIONS,
        "capture focus ledger action",
    )
    capture_gate_filter = focus_filters.normalize_focus_filter(
        capture_gates,
        CAPTURE_FOCUS_CAPTURE_GATES,
        "capture focus gate",
    )
    readiness_filter = focus_filters.normalize_focus_filter(
        readinesses, CAPTURE_FOCUS_READINESS_STATES, "capture focus readiness"
    )
    actionable_ids = set(queue_state.actionable_without_review_ready_pending)
    pending_slot_details_by_gap = focus_slots.build_pending_slot_details_by_gap(pending_slots or [])
    metric_deltas = readiness_metric_deltas or {}
    focus: list[CaptureFocusItem] = []
    for item in queued_items:
        if item.gap_id not in actionable_ids:
            continue
        if item.ledger_action not in CAPTURE_FOCUS_LEDGER_ACTIONS:
            continue
        focus_item = capture_focus_item(item, pending_slot_details_by_gap, metric_deltas)
        if not focus_filters.focus_item_matches_filters(
            focus_item,
            area_filter,
            priority_filter,
            ledger_action_filter,
            capture_gate_filter,
            readiness_filter,
        ):
            continue
        focus.append(focus_item)
    return focus


def build_next_capture_focus(
    queued_items: list[plan_harness_sample_collection.CollectionItem],
    queue_state: harness_pending_queue_state.QueueState,
    *,
    limit: int = CAPTURE_FOCUS_LIMIT,
    areas: set[str] | None = None,
    priorities: set[str] | None = None,
    ledger_actions: set[str] | None = None,
    capture_gates: set[str] | None = None,
    readinesses: set[str] | None = None,
    pending_slots: list[harness_sample_slots.SampleSlot] | None = None,
    readiness_metric_deltas: dict[str, str] | None = None,
) -> list[CaptureFocusItem]:
    return build_next_capture_focus_selection(
        queued_items,
        queue_state,
        limit=limit,
        areas=areas,
        priorities=priorities,
        ledger_actions=ledger_actions,
        capture_gates=capture_gates,
        readinesses=readinesses,
        pending_slots=pending_slots,
        readiness_metric_deltas=readiness_metric_deltas,
    ).items


def report_fields(
    queued_items: list[plan_harness_sample_collection.CollectionItem],
    queue_state: harness_pending_queue_state.QueueState,
    capture_focus_limit: int,
    capture_focus_areas: set[str] | None,
    capture_focus_priorities: set[str] | None,
    capture_focus_ledger_actions: set[str] | None,
    capture_focus_gates: set[str] | None,
    capture_focus_readinesses: set[str] | None,
    pending_slots: list[harness_sample_slots.SampleSlot],
    readiness_metric_deltas: dict[str, str],
) -> dict[str, object]:
    area_filter = focus_filters.normalized_report_filter(capture_focus_areas)
    priority_filter = focus_filters.normalized_report_filter(capture_focus_priorities)
    ledger_action_filter = focus_filters.normalized_report_filter(capture_focus_ledger_actions)
    capture_gate_filter = focus_filters.normalized_report_filter(capture_focus_gates)
    readiness_filter = focus_filters.normalized_report_filter(capture_focus_readinesses)
    selection = build_next_capture_focus_selection(
        queued_items,
        queue_state,
        limit=capture_focus_limit,
        areas=set(area_filter),
        priorities=set(priority_filter),
        ledger_actions=set(ledger_action_filter),
        capture_gates=set(capture_gate_filter),
        readinesses=set(readiness_filter),
        pending_slots=pending_slots,
        readiness_metric_deltas=readiness_metric_deltas,
    )
    return {
        "next_capture_focus_area_filter": area_filter,
        "next_capture_focus_priority_filter": priority_filter,
        "next_capture_focus_ledger_action_filter": ledger_action_filter,
        "next_capture_focus_capture_gate_filter": capture_gate_filter,
        "next_capture_focus_readiness_filter": readiness_filter,
        "next_capture_focus_count": len(selection.items),
        "next_capture_focus_available_count": selection.available_count,
        "next_capture_focus_limit": selection.limit,
        "next_capture_focus_truncated": selection.truncated,
        "next_capture_focus_hidden_gap_ids": selection.hidden_gap_ids,
        "next_capture_focus_shown_priority_counts": selection.shown_priority_counts,
        "next_capture_focus_available_priority_counts": selection.available_priority_counts,
        "next_capture_focus_shown_area_counts": selection.shown_area_counts,
        "next_capture_focus_available_area_counts": selection.available_area_counts,
        "next_capture_focus_shown_ledger_action_counts": selection.shown_ledger_action_counts,
        "next_capture_focus_available_ledger_action_counts": selection.available_ledger_action_counts,
        "next_capture_focus_shown_capture_gate_counts": selection.shown_capture_gate_counts,
        "next_capture_focus_available_capture_gate_counts": selection.available_capture_gate_counts,
        "next_capture_focus_shown_readiness_counts": selection.shown_readiness_counts,
        "next_capture_focus_available_readiness_counts": selection.available_readiness_counts,
        "next_capture_focus": selection.items,
    }


def capture_focus_item(
    item: plan_harness_sample_collection.CollectionItem,
    pending_slot_details_by_gap: dict[str, focus_slots.PendingSlotDetail],
    readiness_metric_deltas: dict[str, str],
) -> CaptureFocusItem:
    pending_detail = pending_slot_details_by_gap.get(item.gap_id, focus_slots.EMPTY_PENDING_SLOT_DETAIL)
    return CaptureFocusItem(
        gap_id=item.gap_id,
        area=item.area,
        priority=item.priority,
        ledger_action=item.ledger_action,
        readiness=item.readiness,
        source_metric=item.source_metric,
        current_to_target=current_to_target(item),
        readiness_metric_delta=readiness_metric_deltas.get(item.gap_id, ""),
        pending_slot_status=item.pending_slot_status,
        pending_slot_refs=pending_detail.refs,
        pending_review_blockers=pending_detail.review_blockers,
        source_type_needed=item.source_type_needed,
        capture_gate=item.capture_gate,
        capture_gate_detail=item.capture_gate_detail,
        target_artifact=item.target_artifact,
        review_command=item.review_command,
        lane_review_command=lane_review_command(item),
        planner_command=focused_planner_command(item),
        intake_command=focused_intake_command(item),
        evidence_needed=item.evidence_needed,
        trigger=item.trigger,
        boundary=item.boundary,
        reason=focus_reason(item),
    )


def current_to_target(item: plan_harness_sample_collection.CollectionItem) -> str:
    if item.upgrade_discussion_target:
        return f"{item.accepted_count}/{item.upgrade_discussion_target}"
    return str(item.accepted_count)


def lane_review_command(item: plan_harness_sample_collection.CollectionItem) -> str:
    if item.ledger_action == "fill-existing-placeholder":
        return item.replacement_review_command
    if item.ledger_action == "append-new-pending-slot":
        return item.append_review_command
    return "not-applicable"


def focused_planner_command(item: plan_harness_sample_collection.CollectionItem) -> str:
    return harness_collection_lane_commands.lane_planner_command({item.gap_id}, item.ledger_action)


def focused_intake_command(item: plan_harness_sample_collection.CollectionItem) -> str:
    return harness_collection_lane_commands.lane_intake_command({item.gap_id}, item.ledger_action)


def focus_reason(item: plan_harness_sample_collection.CollectionItem) -> str:
    if item.ledger_action == "fill-existing-placeholder":
        return "existing placeholder pending row needs real-event replacement before outcome review"
    return "no review-ready pending row exists; append a bounded pending sample candidate first"
