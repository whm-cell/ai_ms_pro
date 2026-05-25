#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass

import plan_harness_sample_collection


@dataclass(frozen=True)
class QueueState:
    queued_gaps: list[str]
    queued_ledger_action_counts: dict[str, int]
    queued_ledger_action_gaps: dict[str, list[str]]
    queued_with_pending: list[str]
    queued_without_pending: list[str]
    queued_with_review_ready_pending: list[str]
    queued_without_review_ready_pending: list[str]
    actionable_gaps: list[str]
    actionable_ledger_action_counts: dict[str, int]
    actionable_ledger_action_gaps: dict[str, list[str]]
    actionable_with_pending: list[str]
    actionable_with_review_ready_pending: list[str]
    actionable_with_placeholder_pending: list[str]
    actionable_without_pending: list[str]
    actionable_without_review_ready_pending: list[str]
    ready_upgrade_decision_gaps: list[str]
    contract_blocked_gaps: list[str]
    local_only_gaps: list[str]


def build_queue_state(
    queued_items: list[plan_harness_sample_collection.CollectionItem],
    pending_by_gap: dict[str, int],
    pending_review_ready_by_gap: dict[str, int],
    pending_placeholder_by_gap: dict[str, int],
) -> QueueState:
    queued_gaps = [item.gap_id for item in queued_items]
    actionable_items = actionable_sample_items(queued_items)
    actionable_gaps = sorted(item.gap_id for item in actionable_items)
    return QueueState(
        queued_gaps=queued_gaps,
        queued_ledger_action_counts=count_by_ledger_action(queued_items),
        queued_ledger_action_gaps=group_gaps_by_ledger_action(queued_items),
        queued_with_pending=gaps_with_records(queued_gaps, pending_by_gap),
        queued_without_pending=gaps_without_records(queued_gaps, pending_by_gap),
        queued_with_review_ready_pending=gaps_with_records(queued_gaps, pending_review_ready_by_gap),
        queued_without_review_ready_pending=gaps_without_records(queued_gaps, pending_review_ready_by_gap),
        actionable_gaps=actionable_gaps,
        actionable_ledger_action_counts=count_by_ledger_action(actionable_items),
        actionable_ledger_action_gaps=group_gaps_by_ledger_action(actionable_items),
        actionable_with_pending=gaps_with_records(actionable_gaps, pending_by_gap),
        actionable_with_review_ready_pending=gaps_with_records(actionable_gaps, pending_review_ready_by_gap),
        actionable_with_placeholder_pending=gaps_with_records(actionable_gaps, pending_placeholder_by_gap),
        actionable_without_pending=gaps_without_records(actionable_gaps, pending_by_gap),
        actionable_without_review_ready_pending=gaps_without_records(actionable_gaps, pending_review_ready_by_gap),
        ready_upgrade_decision_gaps=sorted(
            item.gap_id for item in queued_items if item.ledger_action == "review-upgrade-decision"
        ),
        contract_blocked_gaps=sorted(
            item.gap_id for item in queued_items if item.source_type_needed == "contract-blocked"
        ),
        local_only_gaps=sorted(item.gap_id for item in queued_items if item.readiness == "local-sample-only"),
    )


def actionable_sample_items(
    items: list[plan_harness_sample_collection.CollectionItem],
) -> list[plan_harness_sample_collection.CollectionItem]:
    return [
        item
        for item in items
        if item.readiness in {"needs-first-real-sample", "needs-more-real-samples"}
        and item.source_type_needed != "contract-blocked"
    ]


def count_by_ledger_action(items: list[plan_harness_sample_collection.CollectionItem]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        counts[item.ledger_action] = counts.get(item.ledger_action, 0) + 1
    return dict(sorted(counts.items()))


def group_gaps_by_ledger_action(
    items: list[plan_harness_sample_collection.CollectionItem],
) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for item in items:
        groups.setdefault(item.ledger_action, []).append(item.gap_id)
    return {action: sorted(gaps) for action, gaps in sorted(groups.items())}


def gaps_with_records(gaps: list[str], counts_by_gap: dict[str, int]) -> list[str]:
    return sorted(gap for gap in gaps if counts_by_gap.get(gap, 0) > 0)


def gaps_without_records(gaps: list[str], counts_by_gap: dict[str, int]) -> list[str]:
    return sorted(gap for gap in gaps if counts_by_gap.get(gap, 0) == 0)
