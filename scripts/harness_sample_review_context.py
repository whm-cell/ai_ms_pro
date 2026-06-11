from __future__ import annotations

from dataclasses import dataclass

import harness_collection_lane_commands
import harness_sample_slots
import plan_harness_sample_collection


@dataclass(frozen=True)
class SampleReviewContext:
    target_ledger: str = ""
    ledger_action: str = ""
    readiness: str = ""
    source_metric: str = ""
    current_to_target: str = ""
    capture_gate: str = ""
    capture_gate_detail: str = ""
    evidence_needed: tuple[str, ...] = ()
    trigger: str = ""
    boundary: str = ""
    planner_command: str = ""
    intake_command: str = ""
    review_command: str = ""
    target_line: int = 0
    target_review_state: str = ""


@dataclass(frozen=True)
class CandidateReview:
    queue_context: SampleReviewContext
    review_state: str
    review_blockers: list[str]
    checker_errors: list[str]


def empty_review() -> CandidateReview:
    return CandidateReview(
        queue_context=SampleReviewContext(),
        review_state="",
        review_blockers=[],
        checker_errors=[],
    )


def item_current_to_target(
    item: plan_harness_sample_collection.CollectionItem,
) -> str:
    if item.upgrade_discussion_target:
        return f"{item.accepted_count}/{item.upgrade_discussion_target}"
    return str(item.accepted_count)


def context_for_append_item(
    item: plan_harness_sample_collection.CollectionItem,
) -> SampleReviewContext:
    planner_command, intake_command = focused_commands(item.gap_id, item.ledger_action)
    return SampleReviewContext(
        target_ledger=item.target_artifact,
        ledger_action=item.ledger_action,
        readiness=item.readiness,
        source_metric=item.source_metric,
        current_to_target=item_current_to_target(item),
        capture_gate=item.capture_gate,
        capture_gate_detail=item.capture_gate_detail,
        evidence_needed=tuple(item.evidence_needed),
        trigger=item.trigger,
        boundary=item.boundary,
        planner_command=planner_command,
        intake_command=intake_command,
        review_command=item.review_command,
    )


def context_for_replacement_target(
    target_slot: harness_sample_slots.SampleSlot,
) -> SampleReviewContext:
    return SampleReviewContext(
        target_ledger=target_slot.ledger_path,
        target_line=target_slot.line,
        target_review_state=target_slot.pending_review_state,
    )


def context_for_replacement_item(
    target_slot: harness_sample_slots.SampleSlot,
    item: plan_harness_sample_collection.CollectionItem,
) -> SampleReviewContext:
    planner_command, intake_command = focused_commands(item.gap_id, item.ledger_action)
    return SampleReviewContext(
        target_ledger=target_slot.ledger_path,
        ledger_action=item.ledger_action,
        readiness=item.readiness,
        source_metric=item.source_metric,
        current_to_target=item_current_to_target(item),
        capture_gate=item.capture_gate,
        capture_gate_detail=item.capture_gate_detail,
        evidence_needed=tuple(item.evidence_needed),
        trigger=item.trigger,
        boundary=item.boundary,
        planner_command=planner_command,
        intake_command=intake_command,
        target_line=target_slot.line,
        target_review_state=target_slot.pending_review_state,
    )


def focused_commands(gap_id: str, ledger_action: str = "") -> tuple[str, str]:
    selected_gap_ids = {gap_id} if gap_id else set()
    return (
        harness_collection_lane_commands.lane_planner_command(selected_gap_ids, ledger_action),
        harness_collection_lane_commands.lane_intake_command(selected_gap_ids, ledger_action),
    )
