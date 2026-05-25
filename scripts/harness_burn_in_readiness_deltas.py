#!/usr/bin/env python3

from __future__ import annotations

from harness_burn_in_readiness_types import ReadinessItem


def accepted_real_readiness_metric_deltas(
    items: list[ReadinessItem],
    accepted_real_by_gap: dict[str, int],
) -> dict[str, str]:
    deltas: dict[str, str] = {}
    for item in items:
        if item.source_metric == "accepted local samples":
            continue
        ledger_count = accepted_real_by_gap.get(item.gap_id, 0)
        if ledger_count == item.accepted_count:
            continue
        deltas[item.gap_id] = (
            f"ledger accepted real={ledger_count}; "
            f"{item.source_metric}={progress_for_delta(item)}"
        )
    return dict(sorted(deltas.items()))


def progress_for_delta(item: ReadinessItem) -> str:
    if item.upgrade_discussion_target:
        return f"{item.accepted_count}/{item.upgrade_discussion_target}"
    return str(item.accepted_count)
