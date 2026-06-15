#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass

import check_harness_burn_in_readiness
import collect_harness_sample_gaps
import harness_sample_capture_gates
import harness_sample_pending_summaries
import harness_sample_priorities
import harness_sample_template_records
from harness_sample_collection_config import (
    DEDICATED_TARGETS,
    FUTURE_WORK_CONTRACT_TARGET,
    TRIGGERS,
    UPGRADE_DECISION_TARGET,
)


@dataclass(frozen=True)
class CollectionItem:
    gap_id: str
    area: str
    priority: str
    readiness: str
    source_metric: str
    accepted_count: int
    upgrade_discussion_target: int
    readiness_metric_delta: str
    target_artifact: str
    review_command: str
    replacement_review_command: str
    append_review_command: str
    outcome_review_command: str
    upgrade_decision_review_command: str
    contract_precondition_review_command: str
    pending_slot_status: str
    pending_slot_count: int
    pending_review_states: tuple[str, ...]
    pending_slot_refs: tuple[str, ...]
    pending_review_blockers: tuple[str, ...]
    ledger_action: str
    contract_blocker_state: object | None
    source_type_needed: str
    capture_gate: str
    capture_gate_detail: str
    trigger: str
    evidence_needed: list[str]
    next_evidence_needed: list[str]
    current_evidence: list[str]
    boundary: str


def ledger_action_for(
    readiness: str,
    source_type_needed: str,
    pending_slot_summary: harness_sample_pending_summaries.PendingSlotSummary,
) -> str:
    return harness_sample_capture_gates.ledger_action_for_status(
        readiness,
        source_type_needed,
        pending_slot_summary.status,
    )


def is_actionable_sample_item(item: CollectionItem) -> bool:
    return (
        item.readiness in {"needs-first-real-sample", "needs-more-real-samples"}
        and item.source_type_needed != "contract-blocked"
    )


def priority_for(gap: collect_harness_sample_gaps.SampleGap) -> str:
    return harness_sample_priorities.priority_for_gap(gap)


def target_for(
    gap: collect_harness_sample_gaps.SampleGap,
    readiness_item: check_harness_burn_in_readiness.ReadinessItem,
) -> str:
    if readiness_item.readiness == "ready-for-upgrade-discussion":
        return UPGRADE_DECISION_TARGET
    if gap.status == "future-work" and readiness_item.readiness == "needs-contract-or-adr-first":
        return FUTURE_WORK_CONTRACT_TARGET
    return DEDICATED_TARGETS.get(gap.id, "docs/ai/standards/harness-sample-gap-evidence.jsonl")


def source_type_for(
    gap: collect_harness_sample_gaps.SampleGap,
    readiness_item: check_harness_burn_in_readiness.ReadinessItem,
) -> str:
    return harness_sample_capture_gates.source_type_for_gap(gap, readiness_item.readiness)


def trigger_for(
    gap: collect_harness_sample_gaps.SampleGap,
    readiness_item: check_harness_burn_in_readiness.ReadinessItem,
) -> str:
    if readiness_item.readiness == "ready-for-upgrade-discussion":
        return readiness_item.next_action
    if gap.status == "future-work" and readiness_item.readiness != "needs-contract-or-adr-first":
        return TRIGGERS.get(gap.id, gap.missing_real_scenario)
    return TRIGGERS.get(gap.id, gap.missing_real_scenario)


def evidence_needed_for(
    gap: collect_harness_sample_gaps.SampleGap,
    readiness_item: check_harness_burn_in_readiness.ReadinessItem,
) -> list[str]:
    if readiness_item.readiness == "ready-for-upgrade-discussion":
        return harness_sample_template_records.upgrade_decision_next_evidence_needed(readiness_item)
    return gap.evidence_needed


def capture_gate_for(
    gap: collect_harness_sample_gaps.SampleGap,
    readiness_item: check_harness_burn_in_readiness.ReadinessItem,
    ledger_action: str,
    source_type_needed: str,
) -> tuple[str, str]:
    return harness_sample_capture_gates.capture_gate_for_gap(
        gap,
        readiness_item.readiness,
        ledger_action,
        source_type_needed,
    )


def boundary_for(
    gap: collect_harness_sample_gaps.SampleGap,
    readiness_item: check_harness_burn_in_readiness.ReadinessItem,
) -> str:
    if readiness_item.readiness == "ready-for-upgrade-discussion":
        return "Upgrade decision review only; do not append more samples unless the decision asks for more evidence."
    if gap.status == "future-work" and readiness_item.readiness == "needs-contract-or-adr-first":
        return "Future-work contract precondition only; no sample collection until ADR/contract approval allows it."
    if gap.status == "accepted-local-sample":
        return "Local evidence is already bounded; do not append another sample unless the roadmap status changes."
    if gap.area == "trace-interop":
        return "Bounded evidence only; do not claim hosted/OpenAI/MCP/A2A interop without explicit remote proof."
    if gap.area == "agentic-red-team":
        return "Bounded incident summary only; do not store prompts, transcripts, secrets, or raw tool output."
    return "Bounded evidence only; no raw runtime paths, prompts, full command output, or external payload bodies."


def sort_key(item: CollectionItem) -> tuple[int, str, str]:
    order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    return (order.get(item.priority, 9), item.area, item.gap_id)
