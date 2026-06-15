from __future__ import annotations

from typing import Any


def emit_text(report: Any) -> None:
    print("Harness burn-in readiness audit:")
    print(f"- tracked gaps: {report.item_count}")
    print(f"- ready for upgrade discussion: {report.ready_for_upgrade_discussion}")
    print(f"- needs first real sample: {report.needs_first_real_sample}")
    print(f"- needs more real samples: {report.needs_more_real_samples}")
    print(f"- local sample only: {report.local_sample_only}")
    print(f"- needs contract or ADR first: {report.needs_contract_or_adr_first}")
    print(f"- ready upgrade decision counts: {report.upgrade_decision_counts}")
    print(f"- area filter: {filter_label(report.area_filter)}")
    print(f"- priority filter: {filter_label(report.priority_filter)}")
    print(f"- gap filter: {filter_label(report.gap_id_filter)}")
    print(f"- capture gate filter: {filter_label(report.capture_gate_filter)}")
    print(f"- readiness filter: {filter_label(report.readiness_filter)}")
    print(f"- area counts: {report.area_counts}")
    print(f"- priority counts: {report.priority_counts}")
    print(f"- capture gate counts: {report.capture_gate_counts}")
    print(f"- accepted real/readiness metric deltas: {report.accepted_real_readiness_metric_deltas}")
    print(f"- readiness gap ids: {report.readiness_gap_ids}")
    print(f"- capture gate gap ids: {report.capture_gate_gap_ids}")
    print(f"- ready next evidence needed by gap: {report.ready_next_evidence_needed_by_gap}")
    print(f"- ready gaps without upgrade decision: {report.ready_without_upgrade_decision}")
    print()
    print(
        "| Gap | Area | Priority | Readiness | Upgrade decision | Metric | Current / Upgrade target | "
        "Capture gate | Ledger action | Next action |"
    )
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    if not report.items:
        print("| no matching readiness items | - | - | - | - | - | - | - | - | active filters matched no gaps |")
    for item in report.items:
        upgrade_decision = item.upgrade_decision if item.readiness == "ready-for-upgrade-discussion" else "-"
        print(
            f"| {item.gap_id} | {item.area} | {item.priority} | {item.readiness} | {upgrade_decision} | "
            f"{item.source_metric} | {progress_for(item)} | {item.capture_gate} | {item.ledger_action} | "
            f"{item.next_action} |"
        )
    print()
    print("## Next Collection Commands")
    print()
    print(
        "Read-only routing for the next manual review step; these commands do not write ledgers or accept samples."
    )
    print()
    print("| Gap | Target | Target checker | Planner | Intake | Lane review |")
    print("| --- | --- | --- | --- | --- | --- |")
    if not report.items:
        print("| no matching readiness items | - | - | - | - | - |")
    for item in report.items:
        print(
            f"| {item.gap_id} | {item.target_artifact} | `{item.target_checker_command}` | "
            f"`{item.planner_command}` | `{item.intake_command}` | `{item.lane_review_command}` |"
        )
    if report.ready_next_evidence_needed_by_gap:
        print()
        print("## Ready Gap Next Evidence")
        print()
        print("| Gap | Next evidence needed |")
        print("| --- | --- |")
        for gap_id, evidence in report.ready_next_evidence_needed_by_gap.items():
            print(f"| {gap_id} | {'; '.join(evidence)} |")
    for error in report.errors:
        print(f"ERROR: {error}")
    for warning in report.warnings:
        print(f"WARN: {warning}")


def progress_for(item: Any) -> str:
    if item.upgrade_discussion_target > 0:
        return f"{item.accepted_count}/{item.upgrade_discussion_target}"
    return str(item.accepted_count)


def filter_label(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "all"
