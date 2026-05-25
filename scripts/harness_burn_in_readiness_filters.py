from __future__ import annotations

from typing import Any


def normalize_filter(values: set[str] | None) -> tuple[str, ...]:
    return tuple(sorted(values or ()))


def normalize_capture_gate_filter(capture_gates: set[str] | None) -> tuple[str, ...]:
    return normalize_filter(capture_gates)


def normalize_readiness_filter(readinesses: set[str] | None) -> tuple[str, ...]:
    return normalize_filter(readinesses)


def normalize_gap_id_filter(gap_ids: set[str] | None) -> tuple[str, ...]:
    return normalize_filter(gap_ids)


def filter_by_area(items: list[Any], areas: set[str] | None) -> list[Any]:
    if not areas:
        return items
    return [item for item in items if item.area in areas]


def filter_by_priority(items: list[Any], priorities: set[str] | None) -> list[Any]:
    if not priorities:
        return items
    return [item for item in items if item.priority in priorities]


def filter_by_gap_id(items: list[Any], gap_ids: set[str] | None) -> list[Any]:
    if not gap_ids:
        return items
    return [item for item in items if item.gap_id in gap_ids]


def filter_by_capture_gate(items: list[Any], capture_gates: set[str] | None) -> list[Any]:
    if not capture_gates:
        return items
    return [item for item in items if item.capture_gate in capture_gates]


def filter_by_readiness(items: list[Any], readinesses: set[str] | None) -> list[Any]:
    if not readinesses:
        return items
    return [item for item in items if item.readiness in readinesses]


def count_readiness(items: list[Any], readiness: str) -> int:
    return sum(1 for item in items if item.readiness == readiness)


def upgrade_decision_counts(items: list[Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        if item.readiness != "ready-for-upgrade-discussion":
            continue
        counts[item.upgrade_decision] = counts.get(item.upgrade_decision, 0) + 1
    return dict(sorted(counts.items()))


def capture_gate_counts(items: list[Any]) -> dict[str, int]:
    return bucket_counts(items, "capture_gate")


def bucket_counts(items: list[Any], attr: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        value = getattr(item, attr)
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def bucket_gap_ids(items: list[Any], attr: str) -> dict[str, list[str]]:
    buckets: dict[str, list[str]] = {}
    for item in items:
        value = getattr(item, attr)
        buckets.setdefault(value, []).append(item.gap_id)
    return {key: buckets[key] for key in sorted(buckets)}


def ready_without_upgrade_decision(items: list[Any]) -> list[str]:
    return sorted(
        item.gap_id
        for item in items
        if item.readiness == "ready-for-upgrade-discussion" and item.upgrade_decision == "missing"
    )
