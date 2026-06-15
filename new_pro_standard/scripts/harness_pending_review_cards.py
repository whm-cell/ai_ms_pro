from __future__ import annotations

from dataclasses import dataclass

import harness_sample_review_commands
import harness_sample_slots
import plan_harness_sample_collection


@dataclass(frozen=True)
class PendingReviewCard:
    gap_id: str
    sample_id: str
    source_type: str
    evidence_class: str
    pending_review_state: str
    review_blockers: tuple[str, ...]
    ledger_ref: str
    ledger_action: str
    readiness: str
    source_metric: str
    current_to_target: str
    capture_gate: str
    capture_gate_detail: str
    evidence_needed: tuple[str, ...]
    trigger: str
    review_command: str
    replacement_review_command: str
    outcome_review_command: str
    review_boundary: str


def build_review_cards(
    pending_slots: list[harness_sample_slots.SampleSlot],
    queued_items: list[plan_harness_sample_collection.CollectionItem],
) -> list[PendingReviewCard]:
    queued_by_gap = {item.gap_id: item for item in queued_items}
    cards: list[PendingReviewCard] = []
    for slot in pending_slots:
        item = queued_by_gap.get(slot.gap_id)
        cards.append(
            PendingReviewCard(
                gap_id=slot.gap_id,
                sample_id=slot.sample_id,
                source_type=slot.source_type,
                evidence_class=slot.evidence_class,
                pending_review_state=slot.pending_review_state,
                review_blockers=slot.review_blockers,
                ledger_ref=f"{slot.ledger_path}:{slot.line}",
                ledger_action=item.ledger_action if item else "outside-selected-queue",
                readiness=item.readiness if item else "outside-selected-queue",
                source_metric=item.source_metric if item else "unknown",
                current_to_target=evidence_count(item),
                capture_gate=item.capture_gate if item else "unknown",
                capture_gate_detail=item.capture_gate_detail if item else "unknown",
                evidence_needed=tuple(item.evidence_needed) if item else (),
                trigger=item.trigger if item else "unknown",
                review_command=harness_sample_review_commands.review_command_for(slot.ledger_path),
                replacement_review_command=replacement_review_command(slot),
                outcome_review_command=outcome_review_command(slot),
                review_boundary=review_boundary(item),
            )
        )
    return cards


def replacement_review_command(slot: harness_sample_slots.SampleSlot) -> str:
    if slot.pending_review_state != "placeholder":
        return "not-applicable"
    return harness_sample_review_commands.PLACEHOLDER_REPLACEMENT_REVIEW_COMMAND


def outcome_review_command(slot: harness_sample_slots.SampleSlot) -> str:
    if slot.pending_review_state != "review-ready":
        return "not-applicable"
    return harness_sample_review_commands.SAMPLE_OUTCOME_REVIEW_COMMAND


def evidence_count(item: plan_harness_sample_collection.CollectionItem | None) -> str:
    if item is None:
        return "unknown"
    if item.upgrade_discussion_target:
        return f"{item.accepted_count}/{item.upgrade_discussion_target}"
    return str(item.accepted_count)


def review_boundary(item: plan_harness_sample_collection.CollectionItem | None) -> str:
    boundary = item.boundary if item else "Review with the target checker before changing outcome."
    outcome_boundary = "Pending samples stay unaccepted until a separate review changes outcome to accepted or rejected."
    return f"{boundary} {outcome_boundary}"
