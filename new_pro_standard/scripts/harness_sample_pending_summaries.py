#!/usr/bin/env python3

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import harness_sample_slots


@dataclass(frozen=True)
class PendingSlotSummary:
    status: str
    count: int
    review_states: tuple[str, ...]
    refs: tuple[str, ...]
    review_blockers: tuple[str, ...]


EMPTY_PENDING_SLOT_SUMMARY = PendingSlotSummary("none", 0, (), (), ())


def build_by_gap() -> dict[str, PendingSlotSummary]:
    errors: list[str] = []
    warnings: list[str] = []
    slots_by_gap: dict[str, list[harness_sample_slots.SampleSlot]] = {}
    for slot in harness_sample_slots.load_all_slots(errors, warnings):
        if slot.outcome == "pending":
            slots_by_gap.setdefault(slot.gap_id, []).append(slot)
    return {gap_id: summary_for_slots(slots) for gap_id, slots in slots_by_gap.items()}


def summary_for_slots(slots: list[harness_sample_slots.SampleSlot]) -> PendingSlotSummary:
    sorted_slots = sorted(slots, key=lambda slot: (slot.pending_review_state, slot.ledger_path, slot.line, slot.sample_id))
    review_states = tuple(sorted({slot.pending_review_state for slot in sorted_slots}))
    blockers = unique_text(blocker for slot in sorted_slots for blocker in slot.review_blockers)
    refs = tuple(f"{slot.sample_id} @ {slot.ledger_path}:{slot.line}" for slot in sorted_slots)
    return PendingSlotSummary(status_for_states(review_states), len(sorted_slots), review_states, refs, blockers)


def status_for_states(review_states: tuple[str, ...]) -> str:
    if not review_states:
        return "none"
    if review_states == ("placeholder",):
        return "placeholder"
    if review_states == ("review-ready",):
        return "review-ready"
    return "mixed"


def unique_text(values: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            unique.append(value)
    return tuple(unique)
