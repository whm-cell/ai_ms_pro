#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys
from typing import Any

import check_harness_burn_in_readiness as readiness
import check_harness_placeholder_replacement as candidate_io
import check_harness_upgrade_decisions as upgrade_decisions
import harness_sample_review_commands
import harness_upgrade_decision_context


ROOT = Path(__file__).resolve().parents[1]
DECISION_AUDIT_COMMAND = ".codex/hooks/run_with_repo_python.sh scripts/check_harness_upgrade_decisions.py"


@dataclass(frozen=True)
class UpgradeDecisionCandidateReport:
    candidate_path: str
    decision_id: str
    gap_id: str
    decision: str
    current_decision_id: str
    current_decision_line: int
    current_decision: str
    readiness_at_decision: str
    accepted_count: int | None
    upgrade_discussion_target: int | None
    ledger_action: str
    readiness: str
    source_metric: str
    current_to_target: str
    capture_gate: str
    capture_gate_detail: str
    current_evidence_needed: list[str]
    trigger: str
    boundary: str
    planner_command: str
    intake_command: str
    next_evidence_needed: list[str]
    target_ledger: str
    candidate_review_command: str
    next_decision_audit_command: str
    checker_errors: list[str]
    inventory_errors: list[str]
    errors: list[str]
    review_allowed: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate an upgrade-decision candidate without writing ledgers.",
    )
    parser.add_argument("candidate", help="Path to a single JSON object or one-record JSONL upgrade-decision candidate.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def build_report(candidate_path: Path) -> UpgradeDecisionCandidateReport:
    errors: list[str] = []
    candidate = candidate_io.load_candidate(candidate_path, errors)
    decision_id = text(candidate.get("id"))
    gap_id = text(candidate.get("gap_id"))
    decision = text(candidate.get("decision"))
    readiness_at_decision = text(candidate.get("readiness_at_decision"))
    accepted_count = int_or_none(candidate.get("accepted_count"))
    upgrade_discussion_target = int_or_none(candidate.get("upgrade_discussion_target"))
    next_evidence_needed = upgrade_decisions.safe_text_list(candidate.get("next_evidence_needed"))
    checker_errors: list[str] = []
    current_decision_id = ""
    current_decision_line = 0
    current_decision = ""
    queue_context = harness_upgrade_decision_context.UpgradeDecisionQueueContext()
    inventory_errors = current_inventory_errors(gap_id)

    if candidate:
        queue_context = harness_upgrade_decision_context.expected_upgrade_decision_context(gap_id, errors)
        readiness_report = readiness.build_report(include_future=True, include_accepted=True)
        items_by_gap = {item.gap_id: item for item in readiness_report.items}
        checker_errors.extend(f"readiness: {error}" for error in readiness_report.errors)
        upgrade_decisions.validate_record(1, candidate, set(), set(), items_by_gap, checker_errors)
        rows = current_decision_rows()
        current = rows.get(gap_id)
        if current is not None:
            current_decision_line, current_record = current
            current_decision_id = text(current_record.get("id"))
            current_decision = text(current_record.get("decision"))
            if decision_id != current_decision_id:
                errors.append(
                    "candidate id must match existing upgrade decision id "
                    f"{current_decision_id}; replace the row instead of appending a duplicate"
                )

    blocking_errors = errors + checker_errors + inventory_errors
    return UpgradeDecisionCandidateReport(
        candidate_path=candidate_io.relative(candidate_path),
        decision_id=decision_id,
        gap_id=gap_id,
        decision=decision,
        current_decision_id=current_decision_id,
        current_decision_line=current_decision_line,
        current_decision=current_decision,
        readiness_at_decision=readiness_at_decision,
        accepted_count=accepted_count,
        upgrade_discussion_target=upgrade_discussion_target,
        ledger_action=queue_context.ledger_action,
        readiness=queue_context.readiness,
        source_metric=queue_context.source_metric,
        current_to_target=queue_context.current_to_target,
        capture_gate=queue_context.capture_gate,
        capture_gate_detail=queue_context.capture_gate_detail,
        current_evidence_needed=queue_context.evidence_list(),
        trigger=queue_context.trigger,
        boundary=queue_context.boundary,
        planner_command=queue_context.planner_command,
        intake_command=queue_context.intake_command,
        next_evidence_needed=next_evidence_needed,
        target_ledger=upgrade_decisions.relative(upgrade_decisions.DEFAULT_DECISIONS),
        candidate_review_command=harness_sample_review_commands.UPGRADE_DECISION_CANDIDATE_REVIEW_COMMAND,
        next_decision_audit_command=DECISION_AUDIT_COMMAND,
        checker_errors=checker_errors,
        inventory_errors=inventory_errors,
        errors=errors,
        review_allowed=not blocking_errors,
    )


def current_inventory_errors(candidate_gap_id: str) -> list[str]:
    report = upgrade_decisions.build_report()
    allowed_missing = f"missing upgrade decision for ready gap: {candidate_gap_id}"
    return [f"upgrade_decisions: {error}" for error in report.errors if error != allowed_missing]


def current_decision_rows() -> dict[str, tuple[int, dict[str, Any]]]:
    errors: list[str] = []
    rows = upgrade_decisions.load_records(upgrade_decisions.DEFAULT_DECISIONS, errors)
    return {text(record.get("gap_id")): (line_no, record) for line_no, record in rows}


def text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def int_or_none(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    return value if isinstance(value, int) else None


def emit_text(report: UpgradeDecisionCandidateReport) -> None:
    print("Harness upgrade decision candidate review:")
    print(f"- candidate: {report.candidate_path}")
    print(f"- decision id: {report.decision_id or '<missing>'}")
    print(f"- gap id: {report.gap_id or '<missing>'}")
    print(f"- decision: {report.decision or '<missing>'}")
    if report.current_decision_id:
        print(
            f"- current decision: {report.target_ledger}:{report.current_decision_line} "
            f"({report.current_decision_id}, {report.current_decision})"
        )
    else:
        print("- current decision: <not found>")
    print(f"- readiness at decision: {report.readiness_at_decision or '<missing>'}")
    print(f"- accepted count: {report.accepted_count if report.accepted_count is not None else '<missing>'}")
    print(
        "- upgrade discussion target: "
        f"{report.upgrade_discussion_target if report.upgrade_discussion_target is not None else '<missing>'}"
    )
    if report.ledger_action:
        print(f"- current queue ledger action: {report.ledger_action}")
        print(f"- current readiness: {report.readiness or '<missing>'}")
        print(f"- current source metric: {report.source_metric or '<missing>'}")
        print(f"- current / target: {report.current_to_target or '<missing>'}")
        print(f"- capture gate: {report.capture_gate or '<missing>'}")
        print(f"- capture gate detail: {report.capture_gate_detail or '<missing>'}")
        print(f"- current evidence needed: {report.current_evidence_needed or ['<missing>']}")
        print(f"- trigger: {report.trigger or '<missing>'}")
        print(f"- boundary: {report.boundary or '<missing>'}")
        print(f"- planner command: `{report.planner_command or '<not resolved>'}`")
        print(f"- intake command: `{report.intake_command or '<not resolved>'}`")
    print(f"- next evidence needed: {report.next_evidence_needed or ['<missing>']}")
    print(f"- candidate review command: `{report.candidate_review_command}`")
    print(f"- next decision audit command: `{report.next_decision_audit_command}`")
    print(f"- review allowed: {'yes' if report.review_allowed else 'no'}")
    for error in report.inventory_errors:
        print(f"ERROR: {error}")
    for error in report.checker_errors:
        print(f"ERROR: {error}")
    for error in report.errors:
        print(f"ERROR: {error}")
    if report.review_allowed:
        print("ERRORS: none")


def main() -> int:
    args = parse_args()
    report = build_report(Path(args.candidate).expanduser())
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        emit_text(report)
    return 0 if report.review_allowed else 1


if __name__ == "__main__":
    sys.exit(main())
