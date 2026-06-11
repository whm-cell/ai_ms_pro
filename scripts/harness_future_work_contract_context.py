from __future__ import annotations

from dataclasses import dataclass

import harness_sample_review_context
import plan_harness_sample_collection


@dataclass(frozen=True)
class ContractQueueContext:
    ledger_action: str = ""
    readiness: str = ""
    source_metric: str = ""
    current_to_target: str = ""
    capture_gate: str = ""
    capture_gate_detail: str = ""
    evidence_needed: list[str] | None = None
    trigger: str = ""
    boundary: str = ""
    planner_command: str = ""
    intake_command: str = ""

    def evidence_list(self) -> list[str]:
        return list(self.evidence_needed or [])


def expected_contract_precondition_context(gap_id: str, errors: list[str]) -> ContractQueueContext:
    items = plan_harness_sample_collection.build_queue(
        gap_ids={gap_id},
        include_future=True,
        include_accepted=True,
    )
    if not items:
        errors.append(f"{gap_id}: no current collection queue item found for define-contract-precondition lane")
        return ContractQueueContext()
    if len(items) > 1:
        errors.append(f"{gap_id}: expected one queue item, found {len(items)}")
        return ContractQueueContext()
    item = items[0]
    planner_command, intake_command = harness_sample_review_context.focused_commands(item.gap_id, item.ledger_action)
    context = ContractQueueContext(
        ledger_action=item.ledger_action,
        readiness=item.readiness,
        source_metric=item.source_metric,
        current_to_target=item_current_to_target(item),
        capture_gate=item.capture_gate,
        capture_gate_detail=item.capture_gate_detail,
        evidence_needed=item.evidence_needed,
        trigger=item.trigger,
        boundary=item.boundary,
        planner_command=planner_command,
        intake_command=intake_command,
    )
    if item.ledger_action != "define-contract-precondition":
        errors.append(
            f"{gap_id}: current queue lane is {item.ledger_action} "
            f"(readiness={item.readiness}, pending_slot_status={item.pending_slot_status}); "
            "contract candidate review requires define-contract-precondition"
        )
    return context


def item_current_to_target(item: plan_harness_sample_collection.CollectionItem) -> str:
    if item.upgrade_discussion_target:
        return f"{item.accepted_count}/{item.upgrade_discussion_target}"
    return str(item.accepted_count)
