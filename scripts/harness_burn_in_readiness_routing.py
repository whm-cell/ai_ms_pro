from __future__ import annotations

import collect_harness_sample_gaps
import harness_collection_lane_commands
import harness_sample_capture_gates
from harness_sample_collection_config import (
    DEDICATED_TARGETS,
    FUTURE_WORK_CONTRACT_TARGET,
    UPGRADE_DECISION_TARGET,
)
import harness_sample_pending_summaries
import harness_sample_review_commands


def source_type_for(gap: collect_harness_sample_gaps.SampleGap, readiness: str) -> str:
    return harness_sample_capture_gates.source_type_for_gap(gap, readiness)


def pending_summary_for(
    gap: collect_harness_sample_gaps.SampleGap,
    reports: dict[str, object],
) -> harness_sample_pending_summaries.PendingSlotSummary:
    return reports["pending_slots_by_gap"].get(
        gap.id,
        harness_sample_pending_summaries.EMPTY_PENDING_SLOT_SUMMARY,
    )


def target_artifact_for(gap: collect_harness_sample_gaps.SampleGap, readiness: str) -> str:
    if readiness == "ready-for-upgrade-discussion":
        return UPGRADE_DECISION_TARGET
    if gap.status == "future-work" and readiness == "needs-contract-or-adr-first":
        return FUTURE_WORK_CONTRACT_TARGET
    if gap.status.startswith("accepted-"):
        return "not-applicable"
    return DEDICATED_TARGETS.get(gap.id, "docs/ai/standards/harness-sample-gap-evidence.jsonl")


def target_checker_command_for(target_artifact: str) -> str:
    if target_artifact == "not-applicable":
        return "not-applicable"
    return harness_sample_review_commands.review_command_for(target_artifact)


def planner_command_for(gap: collect_harness_sample_gaps.SampleGap, ledger_action: str) -> str:
    if ledger_action == "no-sample-collection":
        return "not-applicable"
    return harness_collection_lane_commands.lane_planner_command({gap.id}, ledger_action)


def intake_command_for(gap: collect_harness_sample_gaps.SampleGap, ledger_action: str) -> str:
    if ledger_action == "no-sample-collection":
        return "not-applicable"
    return harness_collection_lane_commands.lane_intake_command({gap.id}, ledger_action)


def lane_review_command_for(ledger_action: str) -> str:
    fields = harness_collection_lane_commands.lane_review_command_fields(ledger_action)
    for value in fields.values():
        if value != harness_collection_lane_commands.NOT_APPLICABLE:
            return value
    return "not-applicable"
