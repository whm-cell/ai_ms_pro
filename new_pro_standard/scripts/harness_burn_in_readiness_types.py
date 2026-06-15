from __future__ import annotations

from dataclasses import dataclass


READINESS_STATES: tuple[str, ...] = (
    "local-sample-only",
    "needs-contract-or-adr-first",
    "needs-first-real-sample",
    "needs-more-real-samples",
    "ready-for-upgrade-discussion",
)


@dataclass(frozen=True)
class ReadinessItem:
    gap_id: str
    area: str
    priority: str
    source_metric: str
    accepted_count: int
    first_evidence_target: int
    upgrade_discussion_target: int
    readiness: str
    upgrade_decision: str
    upgrade_decision_ref: str
    next_evidence_needed: list[str]
    capture_gate: str
    capture_gate_detail: str
    target_artifact: str
    target_checker_command: str
    ledger_action: str
    planner_command: str
    intake_command: str
    lane_review_command: str
    current_evidence: list[str]
    next_action: str


@dataclass(frozen=True)
class ReadinessReport:
    item_count: int
    ready_for_upgrade_discussion: int
    needs_first_real_sample: int
    needs_more_real_samples: int
    local_sample_only: int
    needs_contract_or_adr_first: int
    upgrade_decision_counts: dict[str, int]
    area_counts: dict[str, int]
    priority_counts: dict[str, int]
    capture_gate_counts: dict[str, int]
    accepted_real_readiness_metric_deltas: dict[str, str]
    readiness_gap_ids: dict[str, list[str]]
    capture_gate_gap_ids: dict[str, list[str]]
    ready_next_evidence_needed_by_gap: dict[str, list[str]]
    area_filter: tuple[str, ...]
    priority_filter: tuple[str, ...]
    gap_id_filter: tuple[str, ...]
    capture_gate_filter: tuple[str, ...]
    readiness_filter: tuple[str, ...]
    ready_without_upgrade_decision: list[str]
    items: list[ReadinessItem]
    errors: list[str]
    warnings: list[str]
