from __future__ import annotations

from typing import Any


def emit_next_capture_focus(report: Any) -> None:
    if not report.next_capture_focus and report.next_capture_focus_available_count == 0:
        return
    print(
        "- next capture focus: "
        f"{report.next_capture_focus_count}/{report.next_capture_focus_available_count} shown "
        f"(limit: {capture_focus_limit_label(report)}, "
        f"truncated: {str(report.next_capture_focus_truncated).lower()})"
    )
    print(f"  shown priorities: {report.next_capture_focus_shown_priority_counts}")
    print(f"  available priorities: {report.next_capture_focus_available_priority_counts}")
    print(f"  shown areas: {report.next_capture_focus_shown_area_counts}")
    print(f"  available areas: {report.next_capture_focus_available_area_counts}")
    print(f"  shown ledger actions: {report.next_capture_focus_shown_ledger_action_counts}")
    print(f"  available ledger actions: {report.next_capture_focus_available_ledger_action_counts}")
    print(f"  shown capture gates: {report.next_capture_focus_shown_capture_gate_counts}")
    print(f"  available capture gates: {report.next_capture_focus_available_capture_gate_counts}")
    print(f"  shown readiness: {report.next_capture_focus_shown_readiness_counts}")
    print(f"  available readiness: {report.next_capture_focus_available_readiness_counts}")
    print(f"  hidden gap ids: {capture_focus_hidden_gap_label(report)}")
    print(f"  area filter: {capture_focus_filter_label(report.next_capture_focus_area_filter)}")
    print(f"  priority filter: {capture_focus_filter_label(report.next_capture_focus_priority_filter)}")
    print(f"  ledger-action filter: {capture_focus_filter_label(report.next_capture_focus_ledger_action_filter)}")
    print(f"  capture-gate filter: {capture_focus_filter_label(report.next_capture_focus_capture_gate_filter)}")
    print(f"  readiness filter: {capture_focus_filter_label(report.next_capture_focus_readiness_filter)}")
    for item in report.next_capture_focus:
        print(f"  - {item.priority} {item.gap_id} ({item.area}): {item.ledger_action}; {item.reason}")
        print(f"    trigger: {item.trigger}")
        print(f"    metric: {item.source_metric} ({item.current_to_target})")
        if item.readiness_metric_delta:
            print(f"    readiness metric delta: {item.readiness_metric_delta}")
        print(f"    pending refs: {capture_focus_tuple_label(item.pending_slot_refs)}")
        print(f"    pending blockers: {capture_focus_tuple_label(item.pending_review_blockers)}")
        print(f"    capture gate: {item.capture_gate}")
        print(f"    gate detail: {item.capture_gate_detail}")
        print(f"    evidence needed: {capture_focus_evidence_label(item.evidence_needed)}")
        print(f"    planner: `{item.planner_command}`")
        print(f"    intake: `{item.intake_command}`")
        print(f"    review: `{item.lane_review_command}`")


def emit_capture_focus_cards(report: Any) -> None:
    print("# Pending Harness Next Capture Focus")
    print()
    print("Capture focus is read-only; it does not collect samples, write ledgers, or accept pending rows.")
    print(f"Scope gaps: {', '.join(report.scope_gap_ids) if report.scope_gap_ids else 'all'}")
    print(f"Focus area filter: {capture_focus_filter_label(report.next_capture_focus_area_filter)}")
    print(f"Focus priority filter: {capture_focus_filter_label(report.next_capture_focus_priority_filter)}")
    print(f"Focus ledger-action filter: {capture_focus_filter_label(report.next_capture_focus_ledger_action_filter)}")
    print(f"Focus capture-gate filter: {capture_focus_filter_label(report.next_capture_focus_capture_gate_filter)}")
    print(f"Focus readiness filter: {capture_focus_filter_label(report.next_capture_focus_readiness_filter)}")
    print(f"Focus entries: {report.next_capture_focus_count}/{report.next_capture_focus_available_count}")
    print(f"Focus limit: {capture_focus_limit_label(report)}")
    print(f"Focus truncated: {str(report.next_capture_focus_truncated).lower()}")
    print(f"Focus shown priorities: {report.next_capture_focus_shown_priority_counts}")
    print(f"Focus available priorities: {report.next_capture_focus_available_priority_counts}")
    print(f"Focus shown areas: {report.next_capture_focus_shown_area_counts}")
    print(f"Focus available areas: {report.next_capture_focus_available_area_counts}")
    print(f"Focus shown ledger actions: {report.next_capture_focus_shown_ledger_action_counts}")
    print(f"Focus available ledger actions: {report.next_capture_focus_available_ledger_action_counts}")
    print(f"Focus shown capture gates: {report.next_capture_focus_shown_capture_gate_counts}")
    print(f"Focus available capture gates: {report.next_capture_focus_available_capture_gate_counts}")
    print(f"Focus shown readiness: {report.next_capture_focus_shown_readiness_counts}")
    print(f"Focus available readiness: {report.next_capture_focus_available_readiness_counts}")
    print(f"Focus hidden gap ids: {capture_focus_hidden_gap_label(report)}")
    if not report.next_capture_focus:
        print()
        print("No next capture focus entries matched the selected scope/filter.")
        print("Use the full pending audit to inspect non-sample lanes such as upgrade decisions or contract blockers.")
        return
    for item in report.next_capture_focus:
        print()
        print(f"## {item.priority} {item.gap_id}")
        print()
        print(f"- Ledger action: `{item.ledger_action}`")
        print(f"- Area: `{item.area}`")
        print(f"- Reason: {item.reason}")
        print(f"- Readiness: `{item.readiness}`")
        print(f"- Metric: {item.source_metric}")
        print(f"- Current / target: {item.current_to_target}")
        if item.readiness_metric_delta:
            print(f"- Readiness metric delta: {item.readiness_metric_delta}")
        print(f"- Pending slots: `{item.pending_slot_status}`")
        print(f"- Pending refs: {capture_focus_tuple_label(item.pending_slot_refs)}")
        print(f"- Pending blockers: {capture_focus_tuple_label(item.pending_review_blockers)}")
        print(f"- Source type needed: `{item.source_type_needed}`")
        print(f"- Capture gate: `{item.capture_gate}`")
        print(f"- Gate detail: {item.capture_gate_detail}")
        print(f"- Target artifact: `{item.target_artifact}`")
        print(f"- Target checker: `{item.review_command}`")
        print(f"- Planner: `{item.planner_command}`")
        print(f"- Intake: `{item.intake_command}`")
        print(f"- Lane review: `{item.lane_review_command}`")
        print(f"- Trigger: {item.trigger}")
        print(f"- Evidence needed: {capture_focus_evidence_label(item.evidence_needed)}")
        print(f"- Boundary: {item.boundary}")


def capture_focus_limit_label(report: Any) -> str:
    if report.next_capture_focus_limit == 0:
        return "all"
    return str(report.next_capture_focus_limit)


def capture_focus_filter_label(values: tuple[str, ...]) -> str:
    if not values:
        return "all"
    return ", ".join(values)


def capture_focus_evidence_label(values: list[str]) -> str:
    if not values:
        return "<none>"
    return "; ".join(values)


def capture_focus_tuple_label(values: tuple[str, ...]) -> str:
    if not values:
        return "<none>"
    return "; ".join(values)


def capture_focus_hidden_gap_label(report: Any) -> str:
    if not report.next_capture_focus_hidden_gap_ids:
        return "<none>"
    return ", ".join(report.next_capture_focus_hidden_gap_ids)
