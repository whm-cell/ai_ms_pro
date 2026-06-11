from __future__ import annotations

from typing import Any


def normalized_report_filter(values: set[str] | None) -> tuple[str, ...]:
    if not values:
        return ()
    return tuple(sorted(values))


def normalize_focus_filter(
    values: set[str] | None,
    allowed_values: tuple[str, ...],
    label: str,
) -> set[str] | None:
    if not values:
        return None
    invalid = sorted(value for value in values if value not in allowed_values)
    if invalid:
        raise ValueError(f"invalid {label}: {', '.join(invalid)}")
    return set(values)


def focus_item_matches_filters(
    item: Any,
    areas: set[str] | None,
    priorities: set[str] | None,
    ledger_actions: set[str] | None,
    capture_gates: set[str] | None,
    readinesses: set[str] | None,
) -> bool:
    return not (
        (areas and item.area not in areas)
        or (priorities and item.priority not in priorities)
        or (ledger_actions and item.ledger_action not in ledger_actions)
        or (capture_gates and item.capture_gate not in capture_gates)
        or (readinesses and item.readiness not in readinesses)
    )


def count_focus_items(items: list[Any], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        value = getattr(item, field)
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))
