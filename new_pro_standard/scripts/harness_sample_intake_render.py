from __future__ import annotations

import json
from typing import Any


EMPTY_SCOPE_MESSAGE = "No harness sample intake entries matched the selected scope/filter."
EMPTY_SCOPE_NOTE = "Empty intake scope does not accept evidence, write ledgers, or prove the gap is complete."


def iter_entries(report: Any) -> list[Any]:
    entries = [entry for target in report.targets for entry in target.entries]
    priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    return sorted(entries, key=lambda entry: (priority_order.get(entry.priority, 9), entry.area, entry.gap_id))


def emit_text(report: Any) -> None:
    print("# Harness Sample Intake Bundle")
    print()
    print("stdout-only draft bundle; review a real event before appending any line to a ledger.")
    print("Queue: actionable gaps without review-ready pending; placeholder pending rows remain in scope.")
    print("Safety: does not write ledgers, accept evidence, approve future-work sampling, or upgrade checks.")
    print()
    print(f"- sampled_at: {report.sampled_at}")
    print(f"- draft templates: {report.item_count}")
    print(f"- target artifacts: {report.target_count}")
    print(f"- priority counts: {report.priority_counts}")
    print(f"- pending slot status counts: {report.pending_slot_status_counts}")
    print(f"- ledger action counts: {report.ledger_action_counts}")
    print(f"- capture gate counts: {report.capture_gate_counts}")
    print(f"- readiness counts: {report.readiness_counts}")
    print(f"- schema counts: {report.schema_counts}")
    print(f"- draft review state counts: {report.template_review_state_counts}")
    print(f"- validation errors: {len(report.errors) if report.errors else 'none'}")
    if not iter_entries(report):
        print()
        emit_empty_state()
        emit_errors(report.errors)
        return
    for target in report.targets:
        print()
        print(f"## {target.target_artifact}")
        print()
        print(f"- entries: {target.entry_count}")
        for entry in target.entries:
            emit_text_entry(entry)
    emit_errors(report.errors)


def emit_text_entry(entry: Any) -> None:
    print()
    print(f"### {entry.priority} {entry.gap_id}")
    print()
    print(f"- area: `{entry.area}`")
    print(f"- readiness: `{entry.readiness}`")
    print(f"- metric: {entry.source_metric}")
    print(f"- current / target: {entry.current_to_target}")
    if entry.readiness_metric_delta:
        print(f"- readiness metric delta: {entry.readiness_metric_delta}")
    print(f"- schema: `{entry.schema_version}`")
    print(f"- source_type: `{entry.source_type or '<none>'}`")
    print(f"- capture gate: `{entry.capture_gate}`")
    print(f"- capture gate detail: {entry.capture_gate_detail}")
    print(f"- review command: `{entry.review_command}`")
    if entry.replacement_review_command != "not-applicable":
        print(f"- replacement review command: `{entry.replacement_review_command}`")
    if entry.append_review_command != "not-applicable":
        print(f"- append review command: `{entry.append_review_command}`")
    if entry.outcome_review_command != "not-applicable":
        print(f"- outcome review command: `{entry.outcome_review_command}`")
    if entry.upgrade_decision_review_command != "not-applicable":
        print(f"- upgrade-decision review command: `{entry.upgrade_decision_review_command}`")
    if entry.contract_precondition_review_command != "not-applicable":
        print(f"- contract precondition review command: `{entry.contract_precondition_review_command}`")
    emit_contract_blocker_state_text(entry)
    print(f"- pending slots: `{entry.pending_slot_status}` ({entry.pending_slot_count})")
    print(f"- ledger action: `{entry.ledger_action}`")
    print(f"- draft review state: `{entry.template_review_state}`")
    if entry.template_review_blockers:
        print(f"- draft review blockers: {'; '.join(entry.template_review_blockers)}")
    if entry.ledger_action == "fill-existing-placeholder":
        print("- template write mode: replace existing pending placeholder row; do not append duplicate")
    if entry.ledger_action == "review-existing-pending-slot":
        print("- template write mode: outcome candidate for existing pending row; do not append duplicate evidence")
    for slot in entry.pending_slots:
        blockers = "; ".join(slot.review_blockers) if slot.review_blockers else "none"
        print(
            f"  - `{slot.sample_id}` at `{slot.ledger_ref}`; "
            f"state=`{slot.review_state}`, blockers=`{blockers}`, "
            f"evidence=`{slot.evidence_class}`, source=`{slot.source_type}`"
        )
    print(f"- trigger: {entry.trigger}")
    print(f"- evidence needed: {', '.join(entry.evidence_needed) if entry.evidence_needed else '<none>'}")
    print(f"- boundary: {entry.boundary}")
    print(f"- validation: {entry.validation_errors if entry.validation_errors else 'OK'}")
    print()
    print("```json")
    print(json.dumps(entry.template, ensure_ascii=False, separators=(",", ":")))
    print("```")


def emit_contract_blocker_state_text(entry: Any) -> None:
    state = entry.contract_blocker_state
    if state is None:
        return
    missing_adr = str(state.missing_adr_refs).lower()
    sample_allowed = str(state.sample_collection_allowed).lower()
    print(f"- contract status: `{state.status}`")
    print(f"- contract missing ADR refs: `{missing_adr}`")
    print(f"- sample collection allowed: `{sample_allowed}`")
    print(f"- sample boundary: {state.sample_collection_boundary}")
    print(f"- contract next action: {state.next_action}")


def emit_summary(report: Any) -> None:
    print("# Harness Sample Intake Summary")
    print()
    print("Read-only queue for real sample capture; templates are not accepted evidence.")
    print()
    print(f"- sampled_at: {report.sampled_at}")
    print(f"- draft templates: {report.item_count}")
    print(f"- target artifacts: {report.target_count}")
    print(f"- priority counts: {report.priority_counts}")
    print(f"- pending slot status counts: {report.pending_slot_status_counts}")
    print(f"- ledger action counts: {report.ledger_action_counts}")
    print(f"- capture gate counts: {report.capture_gate_counts}")
    print(f"- readiness counts: {report.readiness_counts}")
    print(f"- draft review state counts: {report.template_review_state_counts}")
    print(f"- validation errors: {len(report.errors) if report.errors else 'none'}")
    if not iter_entries(report):
        print()
        emit_empty_state()
        emit_errors(report.errors)
        return
    emit_queue_table(report)
    emit_draft_template_review(report)
    emit_pending_slot_blockers(report)
    emit_capture_gates(report)
    emit_capture_checklist(report)
    emit_placeholder_replacement_review(report)
    emit_pending_append_review(report)
    emit_pending_outcome_review(report)
    emit_upgrade_decision_review(report)
    emit_contract_precondition_review(report)
    emit_targets(report)
    emit_errors(report.errors)


def emit_queue_table(report: Any) -> None:
    print()
    print("## Queue")
    print()
    print("| Priority | Gap | Readiness | Metric | Current / Target | Metric Delta | Pending slots | Ledger action | Target |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for entry in iter_entries(report):
        pending = f"{entry.pending_slot_status} ({entry.pending_slot_count})"
        metric_delta = entry.readiness_metric_delta or "none"
        print(
            f"| {entry.priority} | {entry.gap_id} | {entry.readiness} | {entry.source_metric} | "
            f"{entry.current_to_target} | {metric_delta} | {pending} | {entry.ledger_action} | "
            f"{entry.target_artifact} |"
        )


def emit_pending_slot_blockers(report: Any) -> None:
    pending_refs = [
        (entry, slot)
        for entry in iter_entries(report)
        for slot in entry.pending_slots
        if slot.review_blockers
    ]
    if not pending_refs:
        return
    print()
    print("## Pending Slot Blockers")
    print()
    print("| Gap | Sample | Review state | Blockers |")
    print("| --- | --- | --- | --- |")
    for entry, slot in pending_refs:
        print(f"| {entry.gap_id} | {slot.sample_id} | {slot.review_state} | {'; '.join(slot.review_blockers)} |")


def emit_draft_template_review(report: Any) -> None:
    entries = [
        entry
        for entry in iter_entries(report)
        if entry.template_review_state != "not-applicable" or entry.template_review_blockers
    ]
    if not entries:
        return
    print()
    print("## Draft Template Review")
    print()
    print("| Gap | Draft state | Blockers |")
    print("| --- | --- | --- |")
    for entry in entries:
        blockers = "; ".join(entry.template_review_blockers) if entry.template_review_blockers else "none"
        print(f"| {entry.gap_id} | {entry.template_review_state} | {blockers} |")


def emit_capture_checklist(report: Any) -> None:
    entries = [entry for entry in iter_entries(report) if entry.evidence_needed]
    if not entries:
        return
    print()
    print("## Capture Checklist")
    print()
    print("| Gap | Evidence needed | Boundary |")
    print("| --- | --- | --- |")
    for entry in entries:
        evidence = "; ".join(entry.evidence_needed)
        print(f"| {entry.gap_id} | {evidence} | {entry.boundary} |")


def emit_capture_gates(report: Any) -> None:
    entries = [entry for entry in iter_entries(report) if entry.capture_gate]
    if not entries:
        return
    print()
    print("## Capture Gates")
    print()
    print("| Gap | Gate | Detail |")
    print("| --- | --- | --- |")
    for entry in entries:
        print(f"| {entry.gap_id} | `{entry.capture_gate}` | {entry.capture_gate_detail} |")


def emit_placeholder_replacement_review(report: Any) -> None:
    replacement_refs = [
        (entry, slot)
        for entry in iter_entries(report)
        if entry.replacement_review_command != "not-applicable"
        for slot in entry.pending_slots
    ]
    if not replacement_refs:
        return
    print()
    print("## Placeholder Replacement Review")
    print()
    print("| Gap | Sample | Command |")
    print("| --- | --- | --- |")
    for entry, slot in replacement_refs:
        print(f"| {entry.gap_id} | {slot.sample_id} | `{entry.replacement_review_command}` |")


def emit_pending_append_review(report: Any) -> None:
    append_entries = [entry for entry in iter_entries(report) if entry.append_review_command != "not-applicable"]
    if not append_entries:
        return
    print()
    print("## Pending Append Review")
    print()
    print("| Gap | Command |")
    print("| --- | --- |")
    for entry in append_entries:
        print(f"| {entry.gap_id} | `{entry.append_review_command}` |")


def emit_pending_outcome_review(report: Any) -> None:
    outcome_entries = [entry for entry in iter_entries(report) if entry.outcome_review_command != "not-applicable"]
    if not outcome_entries:
        return
    print()
    print("## Pending Outcome Review")
    print()
    print("| Gap | Sample | Command |")
    print("| --- | --- | --- |")
    for entry in outcome_entries:
        sample_ids = ", ".join(slot.sample_id for slot in entry.pending_slots) or "<unknown>"
        print(f"| {entry.gap_id} | {sample_ids} | `{entry.outcome_review_command}` |")


def emit_upgrade_decision_review(report: Any) -> None:
    upgrade_entries = [
        entry for entry in iter_entries(report) if entry.upgrade_decision_review_command != "not-applicable"
    ]
    if not upgrade_entries:
        return
    print()
    print("## Upgrade Decision Review")
    print()
    print("| Gap | Next evidence needed | Command |")
    print("| --- | --- | --- |")
    for entry in upgrade_entries:
        next_evidence = "; ".join(entry.evidence_needed) if entry.evidence_needed else "none"
        print(f"| {entry.gap_id} | {next_evidence} | `{entry.upgrade_decision_review_command}` |")


def emit_contract_precondition_review(report: Any) -> None:
    contract_entries = [
        entry for entry in iter_entries(report) if entry.contract_precondition_review_command != "not-applicable"
    ]
    if not contract_entries:
        return
    print()
    print("## Contract Precondition Review")
    print()
    print("| Gap | Status | Missing ADR refs | Boundary | Command |")
    print("| --- | --- | --- | --- | --- |")
    for entry in contract_entries:
        state = entry.contract_blocker_state
        status = state.status if state else "unknown"
        missing_adr = str(state.missing_adr_refs).lower() if state else "unknown"
        boundary = state.sample_collection_boundary if state else entry.boundary
        print(
            f"| {entry.gap_id} | {status} | {missing_adr} | "
            f"{boundary} | `{entry.contract_precondition_review_command}` |"
        )


def emit_targets(report: Any) -> None:
    print()
    print("## Targets")
    print()
    print("| Target | Entries | Review command |")
    print("| --- | --- | --- |")
    for target in report.targets:
        review_command = target.entries[0].review_command if target.entries else "unknown"
        print(f"| {target.target_artifact} | {target.entry_count} | `{review_command}` |")


def emit_errors(errors: list[str]) -> None:
    if not errors:
        return
    print()
    for error in errors:
        print(f"ERROR: {error}")


def emit_empty_state() -> None:
    print(EMPTY_SCOPE_MESSAGE)
    print(EMPTY_SCOPE_NOTE)
