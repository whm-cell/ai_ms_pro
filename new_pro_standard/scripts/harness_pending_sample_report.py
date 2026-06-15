#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass

import check_harness_future_work_contracts as future_contracts
import harness_collection_lane_commands
import harness_future_work_contract_states as contract_state_report
import harness_pending_capture_focus
import harness_pending_readiness_metrics
import harness_pending_review_cards
import harness_pending_queue_state
import harness_sample_slots
import plan_harness_sample_collection


REVIEW_STATES = ("any", "placeholder", "review-ready", "unknown")


@dataclass(frozen=True)
class SlotAccounting:
    outcome_counts: dict[str, int]
    pending_by_gap: dict[str, int]
    pending_review_state_counts: dict[str, int]
    pending_review_ready_by_gap: dict[str, int]
    pending_placeholder_by_gap: dict[str, int]
    accepted_by_gap: dict[str, int]
    accepted_evidence_class_counts: dict[str, int]
    accepted_real_by_gap: dict[str, int]
    accepted_synthetic_by_gap: dict[str, int]
    accepted_local_replay_by_gap: dict[str, int]
    accepted_local_only_by_gap: dict[str, int]
    rejected_by_gap: dict[str, int]


@dataclass(frozen=True)
class PendingSampleReport:
    scope_gap_ids: tuple[str, ...]
    pending_review_state_filter: str
    ledger_count: int
    record_count: int
    outcome_counts: dict[str, int]
    pending_by_gap: dict[str, int]
    pending_review_state_counts: dict[str, int]
    pending_review_ready_by_gap: dict[str, int]
    pending_placeholder_by_gap: dict[str, int]
    accepted_by_gap: dict[str, int]
    accepted_evidence_class_counts: dict[str, int]
    accepted_real_by_gap: dict[str, int]
    accepted_synthetic_by_gap: dict[str, int]
    accepted_local_replay_by_gap: dict[str, int]
    accepted_local_only_by_gap: dict[str, int]
    rejected_by_gap: dict[str, int]
    queued_readiness_metrics_by_gap: dict[str, harness_pending_readiness_metrics.QueuedReadinessMetric]
    accepted_real_readiness_metric_deltas: dict[str, str]
    queued_gap_count: int
    queued_ledger_action_counts: dict[str, int]
    queued_ledger_action_gaps: dict[str, list[str]]
    queued_with_pending_count: int
    queued_without_pending_count: int
    queued_with_review_ready_pending_count: int
    queued_without_review_ready_pending_count: int
    queued_with_pending: list[str]
    queued_without_pending: list[str]
    queued_with_review_ready_pending: list[str]
    queued_without_review_ready_pending: list[str]
    actionable_sample_gap_count: int
    actionable_ledger_action_counts: dict[str, int]
    actionable_ledger_action_gaps: dict[str, list[str]]
    actionable_with_pending_count: int
    actionable_with_review_ready_pending_count: int
    actionable_with_placeholder_pending_count: int
    actionable_without_pending_count: int
    actionable_without_review_ready_pending_count: int
    actionable_with_pending: list[str]
    actionable_with_review_ready_pending: list[str]
    actionable_with_placeholder_pending: list[str]
    actionable_without_pending: list[str]
    actionable_without_review_ready_pending: list[str]
    ready_upgrade_decision_gaps: list[str]
    ready_upgrade_decision_next_evidence_by_gap: dict[str, list[str]]
    contract_blocked_gaps: list[str]
    contract_blocker_states: list[contract_state_report.FutureContractState]
    local_only_gaps: list[str]
    next_collection_lane_commands: list[harness_collection_lane_commands.CollectionLaneCommand]
    next_capture_focus_area_filter: tuple[str, ...]
    next_capture_focus_priority_filter: tuple[str, ...]
    next_capture_focus_ledger_action_filter: tuple[str, ...]
    next_capture_focus_capture_gate_filter: tuple[str, ...]
    next_capture_focus_readiness_filter: tuple[str, ...]
    next_capture_focus_count: int
    next_capture_focus_available_count: int
    next_capture_focus_limit: int
    next_capture_focus_truncated: bool
    next_capture_focus_hidden_gap_ids: tuple[str, ...]
    next_capture_focus_shown_priority_counts: dict[str, int]
    next_capture_focus_available_priority_counts: dict[str, int]
    next_capture_focus_shown_area_counts: dict[str, int]
    next_capture_focus_available_area_counts: dict[str, int]
    next_capture_focus_shown_ledger_action_counts: dict[str, int]
    next_capture_focus_available_ledger_action_counts: dict[str, int]
    next_capture_focus_shown_capture_gate_counts: dict[str, int]
    next_capture_focus_available_capture_gate_counts: dict[str, int]
    next_capture_focus_shown_readiness_counts: dict[str, int]
    next_capture_focus_available_readiness_counts: dict[str, int]
    next_capture_focus: list[harness_pending_capture_focus.CaptureFocusItem]
    pending_slots: list[harness_sample_slots.SampleSlot]
    review_cards: list[harness_pending_review_cards.PendingReviewCard]
    warnings: list[str]
    errors: list[str]


def build_report(
    *,
    gap_ids: set[str] | None = None,
    review_state: str = "any",
    include_future: bool = False,
    include_accepted: bool = False,
    capture_focus_limit: int = harness_pending_capture_focus.CAPTURE_FOCUS_LIMIT,
    capture_focus_areas: set[str] | None = None,
    capture_focus_priorities: set[str] | None = None,
    capture_focus_ledger_actions: set[str] | None = None,
    capture_focus_gates: set[str] | None = None,
    capture_focus_readinesses: set[str] | None = None,
) -> PendingSampleReport:
    errors: list[str] = []
    warnings: list[str] = []
    selected_gap_ids = gap_ids or set()
    slots = filter_slots_by_gap(harness_sample_slots.load_all_slots(errors, warnings), selected_gap_ids)
    accounting = build_slot_accounting(slots)
    queued_items = plan_harness_sample_collection.build_queue(
        gap_ids=selected_gap_ids,
        include_future=include_future,
        include_accepted=include_accepted,
    )
    queue_state = harness_pending_queue_state.build_queue_state(
        queued_items,
        accounting.pending_by_gap,
        accounting.pending_review_ready_by_gap,
        accounting.pending_placeholder_by_gap,
    )
    warnings.extend(queue_warnings(accounting.pending_by_gap, queue_state.queued_gaps))
    pending_slots = filter_pending_slots([slot for slot in slots if slot.outcome == "pending"], review_state)
    return report_from_accounting(
        selected_gap_ids,
        review_state,
        slots,
        accounting,
        queue_state,
        pending_slots,
        queued_items,
        capture_focus_limit,
        capture_focus_areas,
        capture_focus_priorities,
        capture_focus_ledger_actions,
        capture_focus_gates,
        capture_focus_readinesses,
        warnings,
        errors,
    )


def build_slot_accounting(slots: list[harness_sample_slots.SampleSlot]) -> SlotAccounting:
    return SlotAccounting(
        outcome_counts=harness_sample_slots.count_by_outcome(slots),
        pending_by_gap=harness_sample_slots.count_by_gap(slots, "pending"),
        pending_review_state_counts=harness_sample_slots.count_pending_by_review_state(slots),
        pending_review_ready_by_gap=harness_sample_slots.count_pending_by_gap_and_review_state(slots, "review-ready"),
        pending_placeholder_by_gap=harness_sample_slots.count_pending_by_gap_and_review_state(slots, "placeholder"),
        accepted_by_gap=harness_sample_slots.count_by_gap(slots, "accepted"),
        accepted_evidence_class_counts=harness_sample_slots.count_by_evidence_class(slots, "accepted"),
        accepted_real_by_gap=harness_sample_slots.count_by_gap(slots, "accepted", "real"),
        accepted_synthetic_by_gap=harness_sample_slots.count_by_gap(slots, "accepted", "synthetic"),
        accepted_local_replay_by_gap=harness_sample_slots.count_by_gap(slots, "accepted", "local-replay"),
        accepted_local_only_by_gap=harness_sample_slots.count_by_gap(slots, "accepted", "local-only"),
        rejected_by_gap=harness_sample_slots.count_by_gap(slots, "rejected"),
    )


def queue_warnings(pending_by_gap: dict[str, int], queued_gaps: list[str]) -> list[str]:
    queued_set = set(queued_gaps)
    return [
        f"pending sample slot is outside selected collection queue: {gap_id}"
        for gap_id in sorted(pending_by_gap)
        if gap_id not in queued_set
    ]


def report_from_accounting(
    selected_gap_ids: set[str],
    review_state: str,
    slots: list[harness_sample_slots.SampleSlot],
    accounting: SlotAccounting,
    queue_state: harness_pending_queue_state.QueueState,
    pending_slots: list[harness_sample_slots.SampleSlot],
    queued_items: list[plan_harness_sample_collection.CollectionItem],
    capture_focus_limit: int,
    capture_focus_areas: set[str] | None,
    capture_focus_priorities: set[str] | None,
    capture_focus_ledger_actions: set[str] | None,
    capture_focus_gates: set[str] | None,
    capture_focus_readinesses: set[str] | None,
    warnings: list[str],
    errors: list[str],
) -> PendingSampleReport:
    ready_next_evidence = ready_upgrade_decision_next_evidence_by_gap(queued_items, queue_state.ready_upgrade_decision_gaps)
    readiness_metric_fields = readiness_metric_report_fields(queued_items, accounting.accepted_real_by_gap)
    return PendingSampleReport(
        scope_gap_ids=tuple(sorted(selected_gap_ids)),
        pending_review_state_filter=review_state,
        ledger_count=len(harness_sample_slots.LEDGERS),
        record_count=len(slots),
        outcome_counts=accounting.outcome_counts,
        pending_by_gap=accounting.pending_by_gap,
        pending_review_state_counts=accounting.pending_review_state_counts,
        pending_review_ready_by_gap=accounting.pending_review_ready_by_gap,
        pending_placeholder_by_gap=accounting.pending_placeholder_by_gap,
        accepted_by_gap=accounting.accepted_by_gap,
        accepted_evidence_class_counts=accounting.accepted_evidence_class_counts,
        accepted_real_by_gap=accounting.accepted_real_by_gap,
        accepted_synthetic_by_gap=accounting.accepted_synthetic_by_gap,
        accepted_local_replay_by_gap=accounting.accepted_local_replay_by_gap,
        accepted_local_only_by_gap=accounting.accepted_local_only_by_gap,
        rejected_by_gap=accounting.rejected_by_gap,
        **readiness_metric_fields,
        **queue_state_report_fields(queue_state),
        ready_upgrade_decision_next_evidence_by_gap=ready_next_evidence,
        contract_blocker_states=contract_blocker_states(queue_state.contract_blocked_gaps, errors),
        next_collection_lane_commands=harness_collection_lane_commands.build_next_collection_lane_commands(
            selected_gap_ids, queue_state
        ),
        **harness_pending_capture_focus.report_fields(
            queued_items, queue_state, capture_focus_limit, capture_focus_areas, capture_focus_priorities,
            capture_focus_ledger_actions,
            capture_focus_gates,
            capture_focus_readinesses,
            pending_slots,
            readiness_metric_fields["accepted_real_readiness_metric_deltas"],
        ),
        pending_slots=pending_slots,
        review_cards=harness_pending_review_cards.build_review_cards(pending_slots, queued_items),
        warnings=warnings,
        errors=errors,
    )


def queue_state_report_fields(queue_state: harness_pending_queue_state.QueueState) -> dict[str, object]:
    return {
        "queued_gap_count": len(queue_state.queued_gaps),
        "queued_ledger_action_counts": queue_state.queued_ledger_action_counts,
        "queued_ledger_action_gaps": queue_state.queued_ledger_action_gaps,
        "queued_with_pending_count": len(queue_state.queued_with_pending),
        "queued_without_pending_count": len(queue_state.queued_without_pending),
        "queued_with_review_ready_pending_count": len(queue_state.queued_with_review_ready_pending),
        "queued_without_review_ready_pending_count": len(queue_state.queued_without_review_ready_pending),
        "queued_with_pending": queue_state.queued_with_pending,
        "queued_without_pending": queue_state.queued_without_pending,
        "queued_with_review_ready_pending": queue_state.queued_with_review_ready_pending,
        "queued_without_review_ready_pending": queue_state.queued_without_review_ready_pending,
        "actionable_sample_gap_count": len(queue_state.actionable_gaps),
        "actionable_ledger_action_counts": queue_state.actionable_ledger_action_counts,
        "actionable_ledger_action_gaps": queue_state.actionable_ledger_action_gaps,
        "actionable_with_pending_count": len(queue_state.actionable_with_pending),
        "actionable_with_review_ready_pending_count": len(queue_state.actionable_with_review_ready_pending),
        "actionable_with_placeholder_pending_count": len(queue_state.actionable_with_placeholder_pending),
        "actionable_without_pending_count": len(queue_state.actionable_without_pending),
        "actionable_without_review_ready_pending_count": len(queue_state.actionable_without_review_ready_pending),
        "actionable_with_pending": queue_state.actionable_with_pending,
        "actionable_with_review_ready_pending": queue_state.actionable_with_review_ready_pending,
        "actionable_with_placeholder_pending": queue_state.actionable_with_placeholder_pending,
        "actionable_without_pending": queue_state.actionable_without_pending,
        "actionable_without_review_ready_pending": queue_state.actionable_without_review_ready_pending,
        "ready_upgrade_decision_gaps": queue_state.ready_upgrade_decision_gaps,
        "contract_blocked_gaps": queue_state.contract_blocked_gaps,
        "local_only_gaps": queue_state.local_only_gaps,
    }


def readiness_metric_report_fields(
    queued_items: list[plan_harness_sample_collection.CollectionItem],
    accepted_real_by_gap: dict[str, int],
) -> dict[str, object]:
    return {
        "queued_readiness_metrics_by_gap": harness_pending_readiness_metrics.queued_readiness_metrics_by_gap(
            queued_items,
            accepted_real_by_gap,
        ),
        "accepted_real_readiness_metric_deltas": harness_pending_readiness_metrics.accepted_real_readiness_metric_deltas(
            queued_items,
            accepted_real_by_gap,
        ),
    }


def ready_upgrade_decision_next_evidence_by_gap(
    queued_items: list[plan_harness_sample_collection.CollectionItem],
    ready_upgrade_decision_gaps: list[str],
) -> dict[str, list[str]]:
    ready_gap_ids = set(ready_upgrade_decision_gaps)
    return {
        item.gap_id: list(item.next_evidence_needed)
        for item in sorted(queued_items, key=lambda queued_item: queued_item.gap_id)
        if item.gap_id in ready_gap_ids and item.next_evidence_needed
    }


def contract_blocker_states(
    contract_blocked_gaps: list[str],
    errors: list[str],
) -> list[contract_state_report.FutureContractState]:
    if not contract_blocked_gaps:
        return []
    report = future_contracts.build_report()
    errors.extend(f"future_contracts: {error}" for error in report.errors)
    states_by_gap = {state.gap_id: state for state in report.contract_states}
    return [states_by_gap[gap_id] for gap_id in contract_blocked_gaps if gap_id in states_by_gap]


def filter_slots_by_gap(
    slots: list[harness_sample_slots.SampleSlot],
    gap_ids: set[str],
) -> list[harness_sample_slots.SampleSlot]:
    if not gap_ids:
        return slots
    return [slot for slot in slots if slot.gap_id in gap_ids]


def filter_pending_slots(
    pending_slots: list[harness_sample_slots.SampleSlot],
    review_state: str,
) -> list[harness_sample_slots.SampleSlot]:
    if review_state == "any":
        return pending_slots
    return [slot for slot in pending_slots if slot.pending_review_state == review_state]
