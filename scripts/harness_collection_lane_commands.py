#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass

import harness_pending_queue_state
import harness_sample_review_commands


RUNNER = ".codex/hooks/run_with_repo_python.sh"
NEXT_LANE_ORDER = (
    "fill-existing-placeholder",
    "review-existing-pending-slot",
    "inspect-mixed-pending-slots",
    "append-new-pending-slot",
    "review-upgrade-decision",
    "define-contract-precondition",
)
NOT_APPLICABLE = "not-applicable"
DEFAULT_LANE_REVIEW_COMMAND_FIELDS = {
    "replacement_review_command": NOT_APPLICABLE,
    "append_review_command": NOT_APPLICABLE,
    "outcome_review_command": NOT_APPLICABLE,
    "upgrade_decision_review_command": NOT_APPLICABLE,
    "contract_precondition_review_command": NOT_APPLICABLE,
}
LANE_REVIEW_COMMAND_FIELDS = {
    "fill-existing-placeholder": {
        **DEFAULT_LANE_REVIEW_COMMAND_FIELDS,
        "replacement_review_command": harness_sample_review_commands.PLACEHOLDER_REPLACEMENT_REVIEW_COMMAND,
    },
    "append-new-pending-slot": {
        **DEFAULT_LANE_REVIEW_COMMAND_FIELDS,
        "append_review_command": harness_sample_review_commands.PENDING_APPEND_REVIEW_COMMAND,
    },
    "review-existing-pending-slot": {
        **DEFAULT_LANE_REVIEW_COMMAND_FIELDS,
        "outcome_review_command": harness_sample_review_commands.SAMPLE_OUTCOME_REVIEW_COMMAND,
    },
    "review-upgrade-decision": {
        **DEFAULT_LANE_REVIEW_COMMAND_FIELDS,
        "upgrade_decision_review_command": (
            harness_sample_review_commands.UPGRADE_DECISION_CANDIDATE_REVIEW_COMMAND
        ),
    },
    "define-contract-precondition": {
        **DEFAULT_LANE_REVIEW_COMMAND_FIELDS,
        "contract_precondition_review_command": (
            harness_sample_review_commands.FUTURE_WORK_CONTRACT_CANDIDATE_REVIEW_COMMAND
        ),
    },
}


@dataclass(frozen=True)
class CollectionLaneCommand:
    ledger_action: str
    gap_count: int
    gap_ids: tuple[str, ...]
    boundary: str
    commands: tuple[str, ...]


def build_next_collection_lane_commands(
    selected_gap_ids: set[str],
    queue_state: harness_pending_queue_state.QueueState,
) -> list[CollectionLaneCommand]:
    lane_gaps = dict(queue_state.actionable_ledger_action_gaps)
    if "review-upgrade-decision" in queue_state.queued_ledger_action_gaps:
        lane_gaps["review-upgrade-decision"] = queue_state.queued_ledger_action_gaps["review-upgrade-decision"]
    if "define-contract-precondition" in queue_state.queued_ledger_action_gaps:
        lane_gaps["define-contract-precondition"] = queue_state.queued_ledger_action_gaps["define-contract-precondition"]
    return [
        CollectionLaneCommand(
            ledger_action=ledger_action,
            gap_count=len(gaps),
            gap_ids=tuple(gaps),
            boundary=lane_boundary(ledger_action),
            commands=lane_commands(ledger_action, selected_gap_ids),
        )
        for ledger_action, gaps in sorted(lane_gaps.items(), key=lane_sort_key)
    ]


def lane_sort_key(item: tuple[str, list[str]]) -> tuple[int, str]:
    ledger_action, _gaps = item
    try:
        return (NEXT_LANE_ORDER.index(ledger_action), ledger_action)
    except ValueError:
        return (len(NEXT_LANE_ORDER), ledger_action)


def lane_boundary(ledger_action: str) -> str:
    if ledger_action == "fill-existing-placeholder":
        return "Complete the existing pending placeholder from a real event; do not append a duplicate row."
    if ledger_action == "append-new-pending-slot":
        return "Capture a real event into a new pending row; templates are not accepted evidence."
    if ledger_action == "define-contract-precondition":
        return "Define or review the contract/ADR precondition; do not collect samples until sampling is approved."
    if ledger_action == "review-existing-pending-slot":
        return "Review the existing pending row with its target checker before changing outcome."
    if ledger_action == "review-upgrade-decision":
        return "Review the ready gap's upgrade decision; do not append another sample unless the decision asks for it."
    if ledger_action == "inspect-mixed-pending-slots":
        return "Inspect mixed pending states before choosing whether to review, fill, or append."
    return "Use the planner to inspect this ledger action before changing any sample ledger."


def lane_commands(ledger_action: str, selected_gap_ids: set[str]) -> tuple[str, ...]:
    if ledger_action == "fill-existing-placeholder":
        return fill_existing_placeholder_commands(selected_gap_ids)
    if ledger_action == "append-new-pending-slot":
        return append_new_pending_slot_commands(selected_gap_ids)
    if ledger_action == "define-contract-precondition":
        return define_contract_precondition_commands(selected_gap_ids)
    if ledger_action == "review-existing-pending-slot":
        return review_existing_pending_slot_commands(selected_gap_ids)
    if ledger_action == "review-upgrade-decision":
        return review_upgrade_decision_commands(selected_gap_ids)
    if ledger_action == "inspect-mixed-pending-slots":
        return inspect_mixed_pending_slot_commands(selected_gap_ids)
    return (planner_command(selected_gap_ids, "--ledger-action", ledger_action, "--capture-card"),)


def lane_review_command_fields(ledger_action: str) -> dict[str, str]:
    return dict(LANE_REVIEW_COMMAND_FIELDS.get(ledger_action, DEFAULT_LANE_REVIEW_COMMAND_FIELDS))


def fill_existing_placeholder_commands(selected_gap_ids: set[str]) -> tuple[str, ...]:
    return (
        lane_planner_command(selected_gap_ids, "fill-existing-placeholder"),
        lane_intake_command(selected_gap_ids, "fill-existing-placeholder"),
        harness_sample_review_commands.PLACEHOLDER_REPLACEMENT_REVIEW_COMMAND,
        pending_audit_command(selected_gap_ids, "--review-state", "placeholder", "--review-cards"),
    )


def append_new_pending_slot_commands(selected_gap_ids: set[str]) -> tuple[str, ...]:
    return (
        lane_planner_command(selected_gap_ids, "append-new-pending-slot"),
        lane_intake_command(selected_gap_ids, "append-new-pending-slot"),
        harness_sample_review_commands.PENDING_APPEND_REVIEW_COMMAND,
    )


def define_contract_precondition_commands(selected_gap_ids: set[str]) -> tuple[str, ...]:
    return (
        lane_planner_command(selected_gap_ids, "define-contract-precondition"),
        lane_intake_command(selected_gap_ids, "define-contract-precondition"),
        harness_sample_review_commands.FUTURE_WORK_CONTRACT_CANDIDATE_REVIEW_COMMAND,
        command("scripts/check_harness_future_work_contracts.py", set()),
    )


def review_existing_pending_slot_commands(selected_gap_ids: set[str]) -> tuple[str, ...]:
    return (
        lane_planner_command(selected_gap_ids, "review-existing-pending-slot"),
        lane_intake_command(selected_gap_ids, "review-existing-pending-slot"),
        pending_audit_command(selected_gap_ids, "--review-state", "review-ready", "--review-cards"),
        harness_sample_review_commands.SAMPLE_OUTCOME_REVIEW_COMMAND,
    )


def review_upgrade_decision_commands(selected_gap_ids: set[str]) -> tuple[str, ...]:
    return (
        lane_planner_command(selected_gap_ids, "review-upgrade-decision"),
        lane_intake_command(selected_gap_ids, "review-upgrade-decision"),
        harness_sample_review_commands.UPGRADE_DECISION_CANDIDATE_REVIEW_COMMAND,
        command("scripts/check_harness_upgrade_decisions.py", set()),
    )


def inspect_mixed_pending_slot_commands(selected_gap_ids: set[str]) -> tuple[str, ...]:
    return (
        lane_planner_command(selected_gap_ids, "inspect-mixed-pending-slots"),
        pending_audit_command(selected_gap_ids, "--review-cards"),
    )


def lane_planner_command(selected_gap_ids: set[str], ledger_action: str) -> str:
    return planner_command(selected_gap_ids, *lane_planner_args(ledger_action))


def lane_intake_command(selected_gap_ids: set[str], ledger_action: str) -> str:
    return intake_command(selected_gap_ids, *lane_intake_args(ledger_action))


def lane_planner_args(ledger_action: str) -> tuple[str, ...]:
    if ledger_action == "define-contract-precondition":
        return ("--include-future", "--ledger-action", ledger_action, "--capture-card")
    if ledger_action:
        return ("--ledger-action", ledger_action, "--capture-card")
    return ("--capture-card",)


def lane_intake_args(ledger_action: str) -> tuple[str, ...]:
    if ledger_action == "review-existing-pending-slot":
        return ("--ledger-action", ledger_action, "--pending-state", "with-review-ready-pending", "--summary")
    if ledger_action:
        return ("--ledger-action", ledger_action, "--summary")
    return ("--summary",)


def planner_command(selected_gap_ids: set[str], *args: str) -> str:
    return command("scripts/plan_harness_sample_collection.py", selected_gap_ids, *args)


def intake_command(selected_gap_ids: set[str], *args: str) -> str:
    return command("scripts/build_harness_sample_intake_bundle.py", selected_gap_ids, *args)


def pending_audit_command(selected_gap_ids: set[str], *args: str) -> str:
    return command("scripts/check_harness_pending_samples.py", selected_gap_ids, *args)


def command(script: str, selected_gap_ids: set[str], *args: str) -> str:
    parts = [RUNNER, script]
    for gap_id in sorted(selected_gap_ids):
        parts.extend(["--gap-id", gap_id])
    parts.extend(args)
    return " ".join(parts)
