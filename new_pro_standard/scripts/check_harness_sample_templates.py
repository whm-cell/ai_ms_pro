#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys
import tempfile
from typing import Callable

import check_agentic_red_team_samples
import check_harness_future_work_contracts
import check_harness_upgrade_decisions
import check_harness_sample_gap_evidence
import check_local_trace_summary_samples
import check_loop_scope_monitor_samples
import check_pre_tool_use_preflight_samples
import check_stage_checkpoints
import check_task_profile_audit
import harness_sample_slots
import harness_sample_templates
import plan_harness_sample_collection


Validator = Callable[[Path], list[str]]


@dataclass(frozen=True)
class TemplateValidation:
    gap_id: str
    target_artifact: str
    schema_version: str
    source_type: str
    capture_gate: str
    capture_gate_detail: str
    template_review_state: str
    template_review_blockers: tuple[str, ...]
    errors: list[str]


@dataclass(frozen=True)
class TemplateReport:
    sampled_at: str
    template_count: int
    skipped_no_sample_collection_count: int
    skipped_no_sample_collection_gap_ids: tuple[str, ...]
    schema_counts: dict[str, int]
    capture_gate_counts: dict[str, int]
    template_review_state_counts: dict[str, int]
    validations: list[TemplateValidation]
    errors: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate generated harness sample templates against ledger checkers.")
    parser.add_argument("--area", action="append", default=[], help="Filter by gap area. Repeatable.")
    parser.add_argument(
        "--priority",
        action="append",
        choices=plan_harness_sample_collection.PRIORITY_LEVELS,
        default=[],
        help="Filter by collection priority.",
    )
    parser.add_argument(
        "--ledger-action",
        action="append",
        choices=plan_harness_sample_collection.LEDGER_ACTIONS,
        default=[],
        help="Filter generated templates by ledger action routing.",
    )
    parser.add_argument(
        "--capture-gate",
        action="append",
        choices=plan_harness_sample_collection.CAPTURE_GATES,
        default=[],
        help="Filter generated templates by real-event capture gate.",
    )
    parser.add_argument(
        "--readiness",
        action="append",
        choices=plan_harness_sample_collection.READINESS_STATES,
        default=[],
        help="Filter generated templates by readiness state.",
    )
    parser.add_argument("--gap-id", action="append", default=[], help="Filter by exact gap id. Repeatable.")
    parser.add_argument("--actionable-only", action="store_true", help="Only validate real sample gaps that can be acted on now.")
    parser.add_argument(
        "--pending-state",
        choices=plan_harness_sample_collection.PENDING_STATES,
        default="any",
        help="Filter generated templates by existing pending sample slot coverage.",
    )
    parser.add_argument(
        "--sampled-at",
        default=None,
        help="YYYY-MM-DD date used in generated template ids. Defaults to today's date.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def preflight_errors(path: Path) -> list[str]:
    return check_pre_tool_use_preflight_samples.build_report(path).errors


def loop_scope_errors(path: Path) -> list[str]:
    return check_loop_scope_monitor_samples.build_report(path).errors


def checkpoint_errors(path: Path) -> list[str]:
    return check_stage_checkpoints.build_report(check_stage_checkpoints.DEFAULT_CHECKPOINTS, path).errors


def local_trace_errors(path: Path) -> list[str]:
    return check_local_trace_summary_samples.build_report(path).errors


def task_profile_errors(path: Path) -> list[str]:
    return check_task_profile_audit.build_report(path).errors


def red_team_errors(path: Path) -> list[str]:
    return check_agentic_red_team_samples.build_report(path).errors


def generic_gap_errors(path: Path) -> list[str]:
    return check_harness_sample_gap_evidence.build_report(path).errors


def future_contract_errors(path: Path) -> list[str]:
    errors: list[str] = []
    records = check_harness_future_work_contracts.load_records(path, errors)
    for line_no, record in records:
        errors.extend(check_harness_future_work_contracts.validate_single_contract_record(record, line_no))
    return errors


def upgrade_decision_errors(path: Path) -> list[str]:
    import check_harness_upgrade_decision_candidate

    report = check_harness_upgrade_decision_candidate.build_report(path)
    return report.inventory_errors + report.checker_errors + report.errors


VALIDATORS: dict[str, Validator] = {
    "pre-tool-use-preflight-sample/v1": preflight_errors,
    "loop-scope-monitor-sample/v1": loop_scope_errors,
    "stage-checkpoint-resume-sample/v1": checkpoint_errors,
    "local-trace-summary-sample/v1": local_trace_errors,
    "task-profile-audit-sample/v1": task_profile_errors,
    "agentic-red-team-sample/v1": red_team_errors,
    "harness-sample-gap-evidence/v1": generic_gap_errors,
    "harness-future-work-contract/v1": future_contract_errors,
    "harness-upgrade-decision/v1": upgrade_decision_errors,
}


def build_report(
    sampled_at: str | None = None,
    gap_ids: set[str] | None = None,
    *,
    areas: set[str] | None = None,
    priorities: set[str] | None = None,
    ledger_actions: set[str] | None = None,
    capture_gates: set[str] | None = None,
    readinesses: set[str] | None = None,
    actionable_only: bool = False,
    pending_state: str = "any",
) -> TemplateReport:
    sampled_at = sampled_at or harness_sample_templates.default_sampled_at()
    items = plan_harness_sample_collection.build_queue(
        areas=areas or set(),
        gap_ids=gap_ids or set(),
        priorities=priorities or set(),
        ledger_actions=ledger_actions or set(),
        capture_gates=capture_gates or set(),
        readinesses=readinesses or set(),
        include_future=True,
        include_accepted=True,
        actionable_only=actionable_only,
        pending_state=pending_state,
    )
    skipped_items = [item for item in items if not harness_sample_templates.should_emit_sample_template(item)]
    template_items = [item for item in items if harness_sample_templates.should_emit_sample_template(item)]
    validations = [validate_item(item, sampled_at) for item in template_items]
    schema_counts: dict[str, int] = {}
    capture_gate_counts: dict[str, int] = {}
    template_review_state_counts: dict[str, int] = {}
    errors: list[str] = []
    for validation in validations:
        schema_counts[validation.schema_version] = schema_counts.get(validation.schema_version, 0) + 1
        capture_gate_counts[validation.capture_gate] = capture_gate_counts.get(validation.capture_gate, 0) + 1
        template_review_state_counts[validation.template_review_state] = (
            template_review_state_counts.get(validation.template_review_state, 0) + 1
        )
        errors.extend(f"{validation.gap_id}: {error}" for error in validation.errors)
    return TemplateReport(
        sampled_at=sampled_at,
        template_count=len(validations),
        skipped_no_sample_collection_count=len(skipped_items),
        skipped_no_sample_collection_gap_ids=tuple(item.gap_id for item in skipped_items),
        schema_counts=dict(sorted(schema_counts.items())),
        capture_gate_counts=dict(sorted(capture_gate_counts.items())),
        template_review_state_counts=dict(sorted(template_review_state_counts.items())),
        validations=validations,
        errors=errors,
    )


def validate_item(
    item: plan_harness_sample_collection.CollectionItem,
    sampled_at: str,
) -> TemplateValidation:
    template = harness_sample_templates.sample_template(item, sampled_at)
    schema_version = str(template.get("schema_version", ""))
    source_type = str(template.get("source_type", ""))
    template_review_state, template_review_blockers = template_review_state_for(template)
    errors: list[str] = []
    contract_schemas = {
        check_harness_future_work_contracts.SCHEMA_VERSION,
        check_harness_upgrade_decisions.SCHEMA_VERSION,
    }
    if item.ledger_action == "review-existing-pending-slot":
        if template.get("outcome") not in {"accepted", "rejected"}:
            errors.append("outcome candidate template must change outcome to accepted or rejected")
        errors.extend(validate_outcome_candidate_template(template))
        return TemplateValidation(
            item.gap_id,
            item.target_artifact,
            schema_version,
            source_type,
            item.capture_gate,
            item.capture_gate_detail,
            template_review_state,
            template_review_blockers,
            errors,
        )
    if schema_version not in contract_schemas and template.get("outcome") != "pending":
        errors.append("template outcome must stay pending")
    validator = VALIDATORS.get(schema_version)
    if not validator:
        errors.append(f"no checker mapped for schema_version: {schema_version or '<missing>'}")
    else:
        errors.extend(validate_with_checker(template, validator))
    return TemplateValidation(
        item.gap_id,
        item.target_artifact,
        schema_version,
        source_type,
        item.capture_gate,
        item.capture_gate_detail,
        template_review_state,
        template_review_blockers,
        errors,
    )


def template_review_state_for(template: dict[str, object]) -> tuple[str, tuple[str, ...]]:
    if template.get("outcome") != "pending":
        return "not-applicable", ()
    return (
        harness_sample_slots.pending_review_state_for_record(template),
        harness_sample_slots.pending_review_blockers_for_record(template),
    )


def validate_outcome_candidate_template(template: dict[str, object]) -> list[str]:
    temp_path = write_jsonl(template)
    try:
        return outcome_candidate_errors(temp_path)
    finally:
        temp_path.unlink(missing_ok=True)


def outcome_candidate_errors(path: Path) -> list[str]:
    import check_harness_sample_outcome

    report = check_harness_sample_outcome.build_report(path)
    return report.inventory_errors + report.checker_errors + report.errors


def validate_with_checker(template: dict[str, object], validator: Validator) -> list[str]:
    temp_path = write_jsonl(template)
    try:
        return validator(temp_path)
    finally:
        temp_path.unlink(missing_ok=True)


def write_jsonl(template: dict[str, object]) -> Path:
    temp = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".jsonl")
    with temp:
        temp.write(json.dumps(template, ensure_ascii=False, separators=(",", ":")) + "\n")
    return Path(temp.name)


def emit_text(report: TemplateReport) -> None:
    print("Harness sample template audit:")
    print(f"- sampled_at: {report.sampled_at}")
    print(f"- templates checked: {report.template_count}")
    print(f"- skipped no-sample-collection templates: {report.skipped_no_sample_collection_count}")
    print(f"- skipped no-sample-collection gap ids: {list(report.skipped_no_sample_collection_gap_ids)}")
    print(f"- schema counts: {report.schema_counts}")
    print(f"- capture gate counts: {report.capture_gate_counts}")
    print(f"- draft review state counts: {report.template_review_state_counts}")
    if report.errors:
        for error in report.errors:
            print(f"ERROR: {error}")
    else:
        print("ERRORS: none")


def main() -> int:
    args = parse_args()
    report = build_report(
        args.sampled_at,
        set(args.gap_id),
        areas=set(args.area),
        priorities=set(args.priority),
        ledger_actions=set(args.ledger_action),
        capture_gates=set(args.capture_gate),
        readinesses=set(args.readiness),
        actionable_only=args.actionable_only,
        pending_state=args.pending_state,
    )
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        emit_text(report)
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
