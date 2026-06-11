from __future__ import annotations

from dataclasses import dataclass

import harness_sample_slots


@dataclass(frozen=True)
class PendingSlotDetail:
    refs: tuple[str, ...]
    review_blockers: tuple[str, ...]


EMPTY_PENDING_SLOT_DETAIL = PendingSlotDetail((), ())


def build_pending_slot_details_by_gap(
    pending_slots: list[harness_sample_slots.SampleSlot],
) -> dict[str, PendingSlotDetail]:
    refs_by_gap: dict[str, list[str]] = {}
    blockers_by_gap: dict[str, list[str]] = {}
    for slot in pending_slots:
        refs_by_gap.setdefault(slot.gap_id, []).append(f"{slot.sample_id} ({slot.ledger_path}:{slot.line})")
        blockers = "; ".join(slot.review_blockers) if slot.review_blockers else "none"
        blockers_by_gap.setdefault(slot.gap_id, []).append(f"{slot.sample_id}: {blockers}")
    return {
        gap_id: PendingSlotDetail(
            refs=tuple(refs_by_gap.get(gap_id, ())),
            review_blockers=tuple(blockers_by_gap.get(gap_id, ())),
        )
        for gap_id in sorted(set(refs_by_gap) | set(blockers_by_gap))
    }
