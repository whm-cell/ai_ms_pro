from __future__ import annotations

from collections import Counter
from dataclasses import asdict
import json
from typing import Any


EMPTY_SCOPE_MESSAGE = "No harness sample collection items matched the selected scope/filter."
EMPTY_SCOPE_NOTE = "Empty planner scope does not accept evidence, reject evidence, or prove the gap is complete."


def emit_json(items: list[Any]) -> None:
    print(json.dumps([asdict(item) for item in items], ensure_ascii=False, indent=2))


def emit_markdown(items: list[Any]) -> None:
    print("# Harness Sample Collection Queue")
    print()
    emit_queue_summary(items)
    if not items:
        print()
        emit_empty_state()
        return
    print()
    print(
        "| Priority | Gap | Readiness | Metric | Current / Target | Metric delta | Pending slots | Ledger action | "
        "Lane review command | Target | Review command | Trigger |"
    )
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for item in items:
        pending_slots = f"{item.pending_slot_status} ({item.pending_slot_count})"
        metric_delta = item.readiness_metric_delta or "none"
        print(
            f"| {item.priority} | {item.gap_id} | {item.readiness} | {item.source_metric} | "
            f"{evidence_count(item)} | {metric_delta} | {pending_slots} | {item.ledger_action} | "
            f"`{lane_review_command(item)}` | {item.target_artifact} | `{item.review_command}` | {item.trigger} |"
        )


def emit_queue_summary(items: list[Any]) -> None:
    print(f"- queued gaps: {len(items)}")
    print(f"- priority counts: {format_counts(item.priority for item in items)}")
    print(f"- readiness counts: {format_counts(item.readiness for item in items)}")
    print(f"- pending slot status counts: {format_counts(item.pending_slot_status for item in items)}")
    print(f"- ledger action counts: {format_counts(item.ledger_action for item in items)}")
    print(f"- capture gate counts: {format_counts(item.capture_gate for item in items)}")


def format_counts(values: object) -> str:
    counts = Counter(values)
    return "none" if not counts else ", ".join(f"{key}={counts[key]}" for key in sorted(counts))


def emit_capture_cards(items: list[Any]) -> None:
    print("# Harness Sample Capture Cards")
    if not items:
        print()
        emit_empty_state()
        return
    for item in items:
        print()
        print(f"## {item.priority} {item.gap_id}")
        print()
        print(f"- Area: {item.area}")
        print(f"- Readiness: {item.readiness}")
        print(f"- Metric: {item.source_metric}")
        print(f"- Current / upgrade target: {evidence_count(item)}")
        if item.readiness_metric_delta:
            print(f"- Readiness metric delta: {item.readiness_metric_delta}")
        print(f"- Target artifact: `{item.target_artifact}`")
        print(f"- Review command: `{item.review_command}`")
        if lane_review_command(item) != "not-applicable":
            print(f"- Lane review command: `{lane_review_command(item)}`")
        print(f"- Pending slots: `{item.pending_slot_status}` ({item.pending_slot_count})")
        print(f"- Ledger action: `{item.ledger_action}`")
        if item.pending_slot_refs:
            print(f"- Pending slot refs: {'; '.join(item.pending_slot_refs)}")
        if item.pending_review_blockers:
            print(f"- Pending review blockers: {'; '.join(item.pending_review_blockers)}")
        print(f"- Source type needed: `{item.source_type_needed}`")
        print(f"- Capture gate: `{item.capture_gate}`")
        print(f"- Capture gate detail: {item.capture_gate_detail}")
        print(f"- Trigger: {item.trigger}")
        print(f"- Current evidence: {'; '.join(item.current_evidence) or 'not tracked yet'}")
        emit_contract_blocker_state(item)
        print(f"- Boundary: {item.boundary}")
        if item.ledger_action == "no-sample-collection":
            print("- No sample collection action:")
        elif item.ledger_action == "review-upgrade-decision":
            print("- Next evidence needed:")
        else:
            print("- Contract fields to define:" if item.source_type_needed == "contract-blocked" else "- Evidence to capture:")
        for evidence in item.evidence_needed:
            print(f"  - {evidence}")


def evidence_count(item: Any) -> str:
    if item.upgrade_discussion_target > 0:
        return f"{item.accepted_count}/{item.upgrade_discussion_target}"
    return str(item.accepted_count)


def emit_contract_blocker_state(item: Any) -> None:
    state = item.contract_blocker_state
    if state is None:
        return
    missing_adr = str(state.missing_adr_refs).lower()
    sample_allowed = str(state.sample_collection_allowed).lower()
    print(f"- Contract status: `{state.status}`")
    print(f"- Contract missing ADR refs: `{missing_adr}`")
    print(f"- Sample collection allowed: `{sample_allowed}`")
    print(f"- Sample boundary: {state.sample_collection_boundary}")
    print(f"- Contract next action: {state.next_action}")


def emit_empty_state() -> None:
    print(EMPTY_SCOPE_MESSAGE)
    print(EMPTY_SCOPE_NOTE)


def lane_review_command(item: Any) -> str:
    for command in (
        item.replacement_review_command,
        item.append_review_command,
        item.outcome_review_command,
        item.upgrade_decision_review_command,
        item.contract_precondition_review_command,
    ):
        if command != "not-applicable":
            return command
    return "not-applicable"
