#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import asdict
import json
from typing import Any

import check_agentic_red_team_samples as red_team
import check_harness_future_work_contracts as future_contracts
import check_harness_sample_gap_evidence as gap_evidence
import check_local_trace_summary_samples as local_trace
import check_loop_scope_monitor_samples as loop_scope
import check_pre_tool_use_preflight_samples as preflight
import check_stage_checkpoints as checkpoints
import check_task_profile_audit as task_profile
import collect_harness_sample_gaps
import harness_burn_in_readiness_cli
import harness_burn_in_readiness_deltas
import harness_burn_in_readiness_filters
import harness_burn_in_readiness_render
import harness_burn_in_readiness_routing
from harness_burn_in_readiness_types import ReadinessItem, ReadinessReport
import harness_sample_capture_gates
import harness_sample_pending_summaries
import harness_sample_priorities
import harness_sample_slots
import harness_upgrade_decision_status as upgrade_decision_status


DEFAULT_UPGRADE_TARGET = 2
LOCAL_TRACE_UPGRADE_TARGET = 3
TASK_PROFILE_REQUIRED_PROFILES = ("simple", "complex", "0-1-stage")


def build_report(
    *,
    include_future: bool = False,
    include_accepted: bool = False,
    areas: set[str] | None = None,
    priorities: set[str] | None = None,
    gap_ids: set[str] | None = None,
    capture_gates: set[str] | None = None,
    readinesses: set[str] | None = None,
) -> ReadinessReport:
    reports = load_reports()
    errors = collect_report_errors(reports)
    upgrade_decisions, decision_warnings = upgrade_decision_status.load_upgrade_decisions()
    items = [
        build_item(gap, reports, upgrade_decisions)
        for gap in collect_harness_sample_gaps.GAPS
        if include_gap(gap, include_future=include_future, include_accepted=include_accepted)
    ]
    items = harness_burn_in_readiness_filters.filter_by_area(items, areas)
    items = harness_burn_in_readiness_filters.filter_by_priority(items, priorities)
    items = harness_burn_in_readiness_filters.filter_by_gap_id(items, gap_ids)
    items = harness_burn_in_readiness_filters.filter_by_capture_gate(items, capture_gates)
    items = harness_burn_in_readiness_filters.filter_by_readiness(items, readinesses)
    warnings = [warning for warning in (warning_for(item) for item in items) if warning]
    warnings.extend(f"sample_slots: {warning}" for warning in reports.get("sample_slot_warnings", []))
    warnings.extend(decision_warnings)
    warnings.extend(decision_warning_for(item) for item in items if decision_warning_for(item))
    return ReadinessReport(
        item_count=len(items),
        ready_for_upgrade_discussion=harness_burn_in_readiness_filters.count_readiness(
            items, "ready-for-upgrade-discussion"
        ),
        needs_first_real_sample=harness_burn_in_readiness_filters.count_readiness(items, "needs-first-real-sample"),
        needs_more_real_samples=harness_burn_in_readiness_filters.count_readiness(items, "needs-more-real-samples"),
        local_sample_only=harness_burn_in_readiness_filters.count_readiness(items, "local-sample-only"),
        needs_contract_or_adr_first=harness_burn_in_readiness_filters.count_readiness(
            items, "needs-contract-or-adr-first"
        ),
        upgrade_decision_counts=harness_burn_in_readiness_filters.upgrade_decision_counts(items),
        area_counts=harness_burn_in_readiness_filters.bucket_counts(items, "area"),
        priority_counts=harness_burn_in_readiness_filters.bucket_counts(items, "priority"),
        capture_gate_counts=harness_burn_in_readiness_filters.capture_gate_counts(items),
        accepted_real_readiness_metric_deltas=(
            harness_burn_in_readiness_deltas.accepted_real_readiness_metric_deltas(
                items,
                reports["accepted_real_by_gap"],
            )
        ),
        readiness_gap_ids=harness_burn_in_readiness_filters.bucket_gap_ids(items, "readiness"),
        capture_gate_gap_ids=harness_burn_in_readiness_filters.bucket_gap_ids(items, "capture_gate"),
        ready_next_evidence_needed_by_gap={
            item.gap_id: item.next_evidence_needed for item in items if item.next_evidence_needed
        },
        area_filter=harness_burn_in_readiness_filters.normalize_filter(areas),
        priority_filter=harness_burn_in_readiness_filters.normalize_filter(priorities),
        gap_id_filter=harness_burn_in_readiness_filters.normalize_gap_id_filter(gap_ids),
        capture_gate_filter=harness_burn_in_readiness_filters.normalize_capture_gate_filter(capture_gates),
        readiness_filter=harness_burn_in_readiness_filters.normalize_readiness_filter(readinesses),
        ready_without_upgrade_decision=harness_burn_in_readiness_filters.ready_without_upgrade_decision(items),
        items=items,
        errors=errors,
        warnings=warnings,
    )


def load_reports() -> dict[str, Any]:
    slot_errors: list[str] = []
    slot_warnings: list[str] = []
    slots = harness_sample_slots.load_all_slots(slot_errors, slot_warnings)
    future_contract_report = future_contracts.build_report()
    red_team_report = red_team.build_report()
    return {
        "accepted_real_by_gap": harness_sample_slots.count_by_gap(slots, "accepted", "real"),
        "preflight": preflight.build_report(),
        "loop_scope": loop_scope.build_report(),
        "checkpoints": checkpoints.build_report(),
        "local_trace": local_trace.build_report(),
        "task_profile": task_profile.build_report(),
        "red_team": red_team_report,
        "red_team_real_by_risk": red_team_report.accepted_real_by_risk,
        "future_contracts": future_contract_report,
        "future_contract_states": {
            state.gap_id: state for state in future_contract_report.contract_states
        },
        "gap_evidence": gap_evidence.build_report(),
        "pending_slots_by_gap": harness_sample_pending_summaries.build_by_gap(),
        "sample_slot_errors": slot_errors,
        "sample_slot_warnings": slot_warnings,
    }


def collect_report_errors(reports: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for name, report in reports.items():
        if isinstance(report, dict):
            continue
        if name == "sample_slot_errors":
            errors.extend(f"sample_slots: {error}" for error in report)
            continue
        if name == "sample_slot_warnings":
            continue
        for error in getattr(report, "errors", []):
            errors.append(f"{name}: {error}")
    return errors


def include_gap(
    gap: collect_harness_sample_gaps.SampleGap,
    *,
    include_future: bool,
    include_accepted: bool,
) -> bool:
    if gap.status == "future-work":
        return include_future
    if gap.status.startswith("accepted-"):
        return include_accepted
    return True


def build_item(
    gap: collect_harness_sample_gaps.SampleGap,
    reports: dict[str, Any],
    upgrade_decisions: dict[str, upgrade_decision_status.UpgradeDecisionSnapshot],
) -> ReadinessItem:
    metric, count, first_target, upgrade_target = metric_for(gap, reports)
    readiness = readiness_for(gap, count, first_target, upgrade_target, reports)
    upgrade_decision = upgrade_decision_for(gap, readiness, upgrade_decisions)
    source_type = harness_burn_in_readiness_routing.source_type_for(gap, readiness)
    pending_summary = harness_burn_in_readiness_routing.pending_summary_for(gap, reports)
    ledger_action = harness_sample_capture_gates.ledger_action_for_status(
        readiness,
        source_type,
        pending_summary.status,
    )
    capture_gate, capture_gate_detail = harness_sample_capture_gates.capture_gate_for_gap(
        gap,
        readiness,
        ledger_action,
        source_type,
    )
    target_artifact = harness_burn_in_readiness_routing.target_artifact_for(gap, readiness)
    return ReadinessItem(
        gap_id=gap.id,
        area=gap.area,
        priority=harness_sample_priorities.priority_for_gap(gap),
        source_metric=metric,
        accepted_count=count,
        first_evidence_target=first_target,
        upgrade_discussion_target=upgrade_target,
        readiness=readiness,
        upgrade_decision=upgrade_decision,
        upgrade_decision_ref=upgrade_decision_ref_for(gap, readiness, upgrade_decisions),
        next_evidence_needed=next_evidence_needed_for(gap, readiness, upgrade_decisions),
        capture_gate=capture_gate,
        capture_gate_detail=capture_gate_detail,
        target_artifact=target_artifact,
        target_checker_command=harness_burn_in_readiness_routing.target_checker_command_for(target_artifact),
        ledger_action=ledger_action,
        planner_command=harness_burn_in_readiness_routing.planner_command_for(gap, ledger_action),
        intake_command=harness_burn_in_readiness_routing.intake_command_for(gap, ledger_action),
        lane_review_command=harness_burn_in_readiness_routing.lane_review_command_for(ledger_action),
        current_evidence=current_evidence_for(gap, reports),
        next_action=next_action_for(gap, readiness, reports, upgrade_decision),
    )


def metric_for(gap: collect_harness_sample_gaps.SampleGap, reports: dict[str, Any]) -> tuple[str, int, int, int]:
    if gap.id == "GAP-GUARDRAIL-PREFLIGHT-WARNING":
        return (
            "accepted real preflight warning samples",
            reports["preflight"].accepted_real_warning_sample_count,
            1,
            DEFAULT_UPGRADE_TARGET,
        )
    if gap.id == "GAP-RUNTIME-LOOP-SCOPE-WARNING":
        return ("accepted real loop/scope warning samples", reports["loop_scope"].accepted_warning_sample_count, 1, 2)
    if gap.id == "GAP-RUNTIME-STAGE-CHECKPOINT-RESUME":
        return ("accepted cross-task resume samples", reports["checkpoints"].accepted_cross_task_sample_count, 1, 2)
    if gap.id == "GAP-TRACE-LOCAL-SUMMARY-BURNIN":
        return (
            "accepted real local trace summary task classes",
            reports["local_trace"].accepted_real_task_class_count,
            1,
            LOCAL_TRACE_UPGRADE_TARGET,
        )
    if gap.id == "GAP-WORKFLOW-TASK-PROFILE-AUDIT":
        profiles = reports["task_profile"].accepted_real_profiles
        covered = sum(1 for profile in TASK_PROFILE_REQUIRED_PROFILES if profiles.get(profile, 0) > 0)
        return ("accepted real task-profile classes", covered, 2, len(TASK_PROFILE_REQUIRED_PROFILES))
    risk = collect_harness_sample_gaps.RED_TEAM_RISKS_BY_GAP.get(gap.id)
    if risk:
        return ("accepted real red-team incidents for risk", reports["red_team_real_by_risk"].get(risk, 0), 1, 2)
    generic = reports["gap_evidence"]
    if gap.status.startswith("accepted-"):
        return ("accepted local samples", generic.accepted_local_by_gap.get(gap.id, 0), 0, 0)
    return ("accepted real generic gap samples", generic.accepted_real_by_gap.get(gap.id, 0), 1, 2)


def readiness_for(
    gap: collect_harness_sample_gaps.SampleGap,
    count: int,
    first_target: int,
    upgrade_target: int,
    reports: dict[str, Any],
) -> str:
    if gap.status == "future-work":
        state = reports["future_contract_states"].get(gap.id)
        if not state or not state.sample_collection_allowed or state.missing_adr_refs:
            return "needs-contract-or-adr-first"
    if gap.status.startswith("accepted-"):
        return "local-sample-only"
    if count < first_target:
        return "needs-first-real-sample"
    if count < upgrade_target:
        return "needs-more-real-samples"
    return "ready-for-upgrade-discussion"


def current_evidence_for(gap: collect_harness_sample_gaps.SampleGap, reports: dict[str, Any]) -> list[str]:
    evidence = collect_harness_sample_gaps.current_evidence_for(gap)
    state = reports["future_contract_states"].get(gap.id)
    if state:
        evidence.append(f"future-work contract status: {state.status}")
        evidence.append(f"future-work missing ADR refs: {str(state.missing_adr_refs).lower()}")
        evidence.append(f"future-work sample boundary: {state.sample_collection_boundary}")
    return evidence


def upgrade_decision_for(
    gap: collect_harness_sample_gaps.SampleGap,
    readiness: str,
    upgrade_decisions: dict[str, upgrade_decision_status.UpgradeDecisionSnapshot],
) -> str:
    if readiness != "ready-for-upgrade-discussion":
        return "not-required"
    snapshot = upgrade_decisions.get(gap.id)
    return snapshot.decision if snapshot else "missing"


def upgrade_decision_ref_for(
    gap: collect_harness_sample_gaps.SampleGap,
    readiness: str,
    upgrade_decisions: dict[str, upgrade_decision_status.UpgradeDecisionSnapshot],
) -> str:
    if readiness != "ready-for-upgrade-discussion":
        return ""
    snapshot = upgrade_decisions.get(gap.id)
    return snapshot.decision_ref if snapshot else ""


def next_evidence_needed_for(
    gap: collect_harness_sample_gaps.SampleGap,
    readiness: str,
    upgrade_decisions: dict[str, upgrade_decision_status.UpgradeDecisionSnapshot],
) -> list[str]:
    if readiness != "ready-for-upgrade-discussion":
        return []
    snapshot = upgrade_decisions.get(gap.id)
    return list(snapshot.next_evidence_needed) if snapshot else []


def next_action_for(
    gap: collect_harness_sample_gaps.SampleGap,
    readiness: str,
    reports: dict[str, Any],
    upgrade_decision: str,
) -> str:
    if readiness == "ready-for-upgrade-discussion":
        if upgrade_decision not in {"missing", "not-required"}:
            return f"Upgrade decision recorded as {upgrade_decision}; rerun upgrade decision audit before changing status or ADR."
        return "Review false positives, repair path, CI cost, reviewer burden, and decide in status or ADR."
    if readiness == "needs-contract-or-adr-first":
        state = reports["future_contract_states"].get(gap.id)
        if state:
            return state.next_action
        return "Define contract, auth, endpoint, redaction, and cost boundary before collecting samples."
    if readiness == "local-sample-only":
        return "Keep local evidence bounded; do not claim real external or remote coverage."
    return gap.missing_real_scenario


def warning_for(item: ReadinessItem) -> str:
    if item.readiness == "ready-for-upgrade-discussion":
        return ""
    if item.readiness in {"local-sample-only", "needs-contract-or-adr-first"}:
        return f"{item.gap_id}: {item.readiness} ({item.source_metric}: {item.accepted_count})"
    return f"{item.gap_id}: {item.readiness} ({item.source_metric}: {item.accepted_count}/{item.upgrade_discussion_target})"


def decision_warning_for(item: ReadinessItem) -> str:
    if item.readiness == "ready-for-upgrade-discussion" and item.upgrade_decision == "missing":
        return f"{item.gap_id}: ready-for-upgrade-discussion but no upgrade decision snapshot recorded"
    return ""


def main() -> int:
    args = harness_burn_in_readiness_cli.parse_args()
    report = build_report(
        include_future=args.include_future,
        include_accepted=args.include_accepted,
        areas=set(args.area),
        priorities=set(args.priority),
        gap_ids=set(args.gap_id),
        capture_gates=set(args.capture_gate),
        readinesses=set(args.readiness),
    )
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        harness_burn_in_readiness_render.emit_text(report)
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
