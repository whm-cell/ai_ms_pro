#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass

import plan_harness_sample_collection


@dataclass(frozen=True)
class QueuedReadinessMetric:
    readiness: str
    source_metric: str
    accepted_count: int
    upgrade_discussion_target: int
    current_to_target: str
    ledger_accepted_real_count: int


def queued_readiness_metrics_by_gap(
    queued_items: list[plan_harness_sample_collection.CollectionItem],
    accepted_real_by_gap: dict[str, int],
) -> dict[str, QueuedReadinessMetric]:
    return {
        item.gap_id: QueuedReadinessMetric(
            readiness=item.readiness,
            source_metric=item.source_metric,
            accepted_count=item.accepted_count,
            upgrade_discussion_target=item.upgrade_discussion_target,
            current_to_target=current_to_target(item),
            ledger_accepted_real_count=accepted_real_by_gap.get(item.gap_id, 0),
        )
        for item in queued_items
    }


def accepted_real_readiness_metric_deltas(
    queued_items: list[plan_harness_sample_collection.CollectionItem],
    accepted_real_by_gap: dict[str, int],
) -> dict[str, str]:
    deltas: dict[str, str] = {}
    for item in queued_items:
        if item.source_metric == "accepted local samples":
            continue
        ledger_count = accepted_real_by_gap.get(item.gap_id, 0)
        if ledger_count == item.accepted_count:
            continue
        deltas[item.gap_id] = (
            f"ledger accepted real={ledger_count}; "
            f"{item.source_metric}={current_to_target(item)}"
        )
    return dict(sorted(deltas.items()))


def current_to_target(item: plan_harness_sample_collection.CollectionItem) -> str:
    if item.upgrade_discussion_target:
        return f"{item.accepted_count}/{item.upgrade_discussion_target}"
    return str(item.accepted_count)
