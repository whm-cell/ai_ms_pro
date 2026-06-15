#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import sys

import harness_pending_capture_focus
import harness_pending_capture_focus_render as capture_focus_render
from harness_pending_sample_report import PendingSampleReport, REVIEW_STATES, build_report


EMPTY_SCOPE_MESSAGE = "No pending sample records or collection queue entries matched the selected scope/filter."
EMPTY_SCOPE_NOTE = "Empty pending-sample scope does not collect samples, change outcomes, or prove gap completion."


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit pending harness sample slots across JSONL ledgers.")
    parser.add_argument("--gap-id", action="append", default=[], help="Focus the report on one or more roadmap gaps.")
    parser.add_argument(
        "--review-state",
        choices=REVIEW_STATES,
        default="any",
        help="Filter pending slot rows/cards by review state without changing accepted evidence counts.",
    )
    parser.add_argument("--include-future", action="store_true", help="Include future-work gaps in queue comparison.")
    parser.add_argument("--include-accepted", action="store_true", help="Include accepted local/real gaps in queue comparison.")
    parser.add_argument("--review-cards", action="store_true", help="Emit pending sample review cards.")
    parser.add_argument("--capture-focus", action="store_true", help="Emit compact next capture focus cards.")
    parser.add_argument(
        "--capture-focus-limit",
        type=non_negative_int,
        default=5,
        help="Maximum next capture focus entries to emit; use 0 for all matching actionable capture lanes.",
    )
    for option, choices, help_text in (
        ("--capture-focus-priority", harness_pending_capture_focus.CAPTURE_FOCUS_PRIORITIES, "priority"),
        ("--capture-focus-area", harness_pending_capture_focus.CAPTURE_FOCUS_AREAS, "roadmap area"),
        ("--capture-focus-ledger-action", harness_pending_capture_focus.CAPTURE_FOCUS_LEDGER_ACTIONS, "ledger action"),
        ("--capture-focus-gate", harness_pending_capture_focus.CAPTURE_FOCUS_CAPTURE_GATES, "capture gate"),
        ("--capture-focus-readiness", harness_pending_capture_focus.CAPTURE_FOCUS_READINESS_STATES, "readiness state"),
    ):
        parser.add_argument(
            option,
            action="append",
            choices=choices,
            default=[],
            help=f"Filter next capture focus entries to one {help_text}; repeat to include multiple values.",
        )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def non_negative_int(raw_value: str) -> int:
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer") from exc
    if value < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return value


def emit_text(report: PendingSampleReport) -> None:
    print("Harness pending sample slot audit:")
    print(f"- ledgers checked: {report.ledger_count}")
    print(f"- scope gaps: {list(report.scope_gap_ids) if report.scope_gap_ids else 'all'}")
    print(f"- pending review-state filter: {report.pending_review_state_filter}")
    print(f"- sample records: {report.record_count}")
    print(f"- outcomes: {report.outcome_counts}")
    print(f"- pending review states: {report.pending_review_state_counts}")
    print(f"- pending review-ready by gap: {report.pending_review_ready_by_gap}")
    print(f"- pending placeholder by gap: {report.pending_placeholder_by_gap}")
    print(f"- accepted evidence classes: {report.accepted_evidence_class_counts}")
    print(f"- accepted real by gap: {report.accepted_real_by_gap}")
    print(f"- accepted synthetic by gap: {report.accepted_synthetic_by_gap}")
    print(f"- accepted local-replay by gap: {report.accepted_local_replay_by_gap}")
    print(f"- accepted local-only by gap: {report.accepted_local_only_by_gap}")
    print(f"- queued readiness metric rows: {len(report.queued_readiness_metrics_by_gap)}")
    print(f"- accepted real/readiness metric deltas: {report.accepted_real_readiness_metric_deltas}")
    print(f"- queued gaps: {report.queued_gap_count}")
    print(f"- queued ledger action counts: {report.queued_ledger_action_counts}")
    print(f"- queued gaps with pending slot: {report.queued_with_pending_count}")
    print(f"- queued gaps without pending slot: {report.queued_without_pending_count}")
    print(f"- queued gaps with review-ready pending: {report.queued_with_review_ready_pending_count}")
    print(f"- queued gaps without review-ready pending: {report.queued_without_review_ready_pending_count}")
    print(f"- actionable sample gaps: {report.actionable_sample_gap_count}")
    print(f"- actionable ledger action counts: {report.actionable_ledger_action_counts}")
    print(f"- actionable gaps with pending slot: {report.actionable_with_pending_count}")
    print(f"- actionable gaps with review-ready pending: {report.actionable_with_review_ready_pending_count}")
    print(f"- actionable gaps with placeholder pending: {report.actionable_with_placeholder_pending_count}")
    print(f"- actionable gaps without pending slot: {report.actionable_without_pending_count}")
    print(f"- actionable gaps without review-ready pending: {report.actionable_without_review_ready_pending_count}")
    print(f"- ready upgrade-decision gaps: {report.ready_upgrade_decision_gaps}")
    print(f"- ready upgrade-decision next evidence by gap: {report.ready_upgrade_decision_next_evidence_by_gap}")
    print(f"- contract-blocked gaps: {report.contract_blocked_gaps}")
    emit_contract_blocker_states(report)
    print(f"- local-only gaps: {report.local_only_gaps}")
    print(f"- pending by gap: {report.pending_by_gap}")
    if report.actionable_with_review_ready_pending:
        print(f"- actionable with review-ready pending: {report.actionable_with_review_ready_pending}")
    if report.actionable_with_placeholder_pending:
        print(f"- actionable with placeholder pending: {report.actionable_with_placeholder_pending}")
    if report.actionable_ledger_action_gaps:
        print(f"- actionable ledger action gaps: {report.actionable_ledger_action_gaps}")
    emit_next_collection_lane_commands(report)
    capture_focus_render.emit_next_capture_focus(report)
    if is_empty_scope(report):
        emit_empty_scope()
    if report.actionable_without_pending:
        print(f"- actionable without pending slot: {report.actionable_without_pending}")
    if report.actionable_without_review_ready_pending:
        print(f"- actionable without review-ready pending: {report.actionable_without_review_ready_pending}")
    if report.pending_slots:
        print()
        print("| Gap | Sample | Source type | Evidence class | Review state | Review blockers | Ledger line |")
        print("| --- | --- | --- | --- | --- | --- | --- |")
        for slot in report.pending_slots:
            blockers = "; ".join(slot.review_blockers) if slot.review_blockers else "none"
            print(
                f"| {slot.gap_id} | {slot.sample_id} | {slot.source_type} | "
                f"{slot.evidence_class} | {slot.pending_review_state} | {blockers} | {slot.ledger_path}:{slot.line} |"
            )
    for warning in report.warnings:
        print(f"WARN: {warning}")
    if report.errors:
        for error in report.errors:
            print(f"ERROR: {error}")
    else:
        print("ERRORS: none")


def emit_contract_blocker_states(report: PendingSampleReport) -> None:
    if not report.contract_blocker_states:
        return
    print("- contract blocker states:")
    for state in report.contract_blocker_states:
        missing_adr = str(state.missing_adr_refs).lower()
        print(f"  - {state.gap_id}: {state.status}; missing_adr_refs={missing_adr}")
        print(f"    boundary: {state.sample_collection_boundary}")
        print(f"    next_action: {state.next_action}")
        print(f"    review_command: `{state.review_command}`")


def emit_next_collection_lane_commands(report: PendingSampleReport) -> None:
    if not report.next_collection_lane_commands:
        return
    print("- next collection lane commands:")
    for lane in report.next_collection_lane_commands:
        print(f"  - {lane.ledger_action} ({lane.gap_count} gaps): {list(lane.gap_ids)}")
        print(f"    boundary: {lane.boundary}")
        for command in lane.commands:
            print(f"    command: `{command}`")


def is_empty_scope(report: PendingSampleReport) -> bool:
    return (
        report.record_count == 0
        and report.queued_gap_count == 0
        and report.actionable_sample_gap_count == 0
        and not report.pending_slots
        and not report.review_cards
    )


def emit_empty_scope() -> None:
    print(EMPTY_SCOPE_MESSAGE)
    print(EMPTY_SCOPE_NOTE)


def emit_review_cards(report: PendingSampleReport) -> None:
    print("# Pending Harness Sample Review Cards")
    print()
    print("Review cards are read-only; they do not accept samples or edit ledgers.")
    print(f"Scope gaps: {', '.join(report.scope_gap_ids) if report.scope_gap_ids else 'all'}")
    print(f"Review-state filter: {report.pending_review_state_filter}")
    if not report.review_cards:
        print()
        print("No pending sample review cards matched the selected scope/filter.")
        print("Pending rows remain unaccepted until a separate review changes a ledger outcome.")
        return
    for card in report.review_cards:
        print()
        print(f"## {card.gap_id}")
        print()
        print(f"- Sample: `{card.sample_id}`")
        print(f"- Ledger: `{card.ledger_ref}`")
        print(f"- Source type: `{card.source_type}`")
        print(f"- Evidence class: `{card.evidence_class}`")
        print(f"- Review state: `{card.pending_review_state}`")
        blockers = "; ".join(card.review_blockers) if card.review_blockers else "none"
        print(f"- Review blockers: {blockers}")
        print(f"- Ledger action: `{card.ledger_action}`")
        print(f"- Readiness: `{card.readiness}`")
        print(f"- Metric: {card.source_metric}")
        print(f"- Current / target: {card.current_to_target}")
        print(f"- Capture gate: `{card.capture_gate}`")
        print(f"- Gate detail: {card.capture_gate_detail}")
        print(f"- Trigger: {card.trigger}")
        print(f"- Evidence needed: {capture_focus_render.capture_focus_evidence_label(list(card.evidence_needed))}")
        print(f"- Review command: `{card.review_command}`")
        if card.replacement_review_command != "not-applicable":
            print(f"- Replacement review command: `{card.replacement_review_command}`")
        if card.outcome_review_command != "not-applicable":
            print(f"- Outcome review command: `{card.outcome_review_command}`")
        print(f"- Boundary: {card.review_boundary}")


def main() -> int:
    args = parse_args()
    report = build_report(
        gap_ids=set(args.gap_id),
        review_state=args.review_state,
        include_future=args.include_future,
        include_accepted=args.include_accepted,
        capture_focus_limit=args.capture_focus_limit,
        capture_focus_areas=set(args.capture_focus_area),
        capture_focus_priorities=set(args.capture_focus_priority),
        capture_focus_ledger_actions=set(args.capture_focus_ledger_action),
        capture_focus_gates=set(args.capture_focus_gate),
        capture_focus_readinesses=set(args.capture_focus_readiness),
    )
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    elif args.capture_focus:
        capture_focus_render.emit_capture_focus_cards(report)
    elif args.review_cards:
        emit_review_cards(report)
    else:
        emit_text(report)
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
