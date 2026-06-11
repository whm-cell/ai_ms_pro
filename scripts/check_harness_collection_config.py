#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys

import check_harness_burn_in_readiness
import collect_harness_sample_gaps
from change_triggered_harness_sample_rules import HARNESS_SAMPLE_GAP_COMMANDS
import check_harness_future_work_contracts as future_contracts
import harness_collection_command_coverage as command_coverage
from harness_burn_in_readiness_types import READINESS_STATES
import harness_sample_collection_config as config
import harness_sample_review_commands as review_commands


ROOT = Path(__file__).resolve().parents[1]
GENERIC_GAP_TARGET = "docs/ai/standards/harness-sample-gap-evidence.jsonl"
REAL_SAMPLE_LEDGER_ACTIONS = set(command_coverage.REAL_SAMPLE_LEDGER_ACTIONS)


@dataclass(frozen=True)
class CollectionConfigReport:
    gap_count: int
    future_gap_count: int
    dedicated_target_count: int
    priority_override_count: int
    trigger_count: int
    configured_target_count: int
    active_capture_gate_count: int
    real_sample_capture_gate_count: int
    real_sample_area_count: int
    real_sample_priority_count: int
    real_sample_ledger_action_count: int
    real_sample_readiness_count: int
    errors: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate harness sample collection routing config.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def audit() -> CollectionConfigReport:
    errors: list[str] = []
    gaps = {gap.id: gap for gap in collect_harness_sample_gaps.GAPS}
    future_gap_ids = {gap.id for gap in collect_harness_sample_gaps.GAPS if gap.status == "future-work"}
    future_contract_states = {
        state.gap_id: state for state in future_contracts.build_report().contract_states
    }
    readiness_report = check_harness_burn_in_readiness.build_report(
        include_future=True,
        include_accepted=True,
    )

    validate_gap_keyed_mapping("DEDICATED_TARGETS", config.DEDICATED_TARGETS, gaps, errors)
    validate_gap_keyed_mapping("PRIORITIES", config.PRIORITIES, gaps, errors)
    validate_gap_keyed_mapping("TRIGGERS", config.TRIGGERS, gaps, errors)
    validate_priorities(errors)
    validate_dedicated_targets(gaps, future_contract_states, errors)
    validate_future_triggers(future_gap_ids, future_contract_states, errors)
    validate_high_priority_triggers(gaps, errors)
    validate_review_targets(errors)
    validate_active_readiness_routing(readiness_report, errors)
    validate_focused_capture_gate_commands(readiness_report, errors)
    validate_focused_real_sample_ledger_action_commands(readiness_report, errors)
    validate_focused_real_sample_readiness_commands(readiness_report, errors)
    validate_focused_real_sample_area_commands(readiness_report, errors)
    validate_focused_real_sample_priority_commands(readiness_report, errors)
    validate_pending_capture_focus_choices(readiness_report, errors)

    configured_targets = configured_target_paths()
    active_capture_gates = active_capture_gate_values(readiness_report)
    real_sample_capture_gates = real_sample_capture_gate_values(readiness_report)
    real_sample_areas = real_sample_area_values(readiness_report)
    real_sample_priorities = real_sample_priority_values(readiness_report)
    real_sample_ledger_actions = real_sample_ledger_action_values(readiness_report)
    real_sample_readiness = real_sample_readiness_values(readiness_report)
    return CollectionConfigReport(
        gap_count=len(gaps),
        future_gap_count=len(future_gap_ids),
        dedicated_target_count=len(config.DEDICATED_TARGETS),
        priority_override_count=len(config.PRIORITIES),
        trigger_count=len(config.TRIGGERS),
        configured_target_count=len(configured_targets),
        active_capture_gate_count=len(active_capture_gates),
        real_sample_capture_gate_count=len(real_sample_capture_gates),
        real_sample_area_count=len(real_sample_areas),
        real_sample_priority_count=len(real_sample_priorities),
        real_sample_ledger_action_count=len(real_sample_ledger_actions),
        real_sample_readiness_count=len(real_sample_readiness),
        errors=tuple(errors),
    )


def validate_gap_keyed_mapping(
    name: str,
    mapping: dict[str, object],
    gaps: dict[str, collect_harness_sample_gaps.SampleGap],
    errors: list[str],
) -> None:
    unknown = sorted(set(mapping) - set(gaps))
    for gap_id in unknown:
        errors.append(f"{name}: unknown gap id: {gap_id}")


def validate_priorities(errors: list[str]) -> None:
    invalid = sorted({priority for priority in config.PRIORITIES.values() if priority not in config.PRIORITY_LEVELS})
    for priority in invalid:
        errors.append(f"PRIORITIES: invalid priority value: {priority}")


def validate_dedicated_targets(
    gaps: dict[str, collect_harness_sample_gaps.SampleGap],
    future_contract_states: dict[str, object],
    errors: list[str],
) -> None:
    for gap_id, target in sorted(config.DEDICATED_TARGETS.items()):
        gap = gaps.get(gap_id)
        if gap and gap.status == "future-work":
            state = future_contract_states.get(gap_id)
            allowed = state and state.sample_collection_allowed and not state.missing_adr_refs
            if not allowed:
                errors.append(
                    "DEDICATED_TARGETS: future-work gap must use future contract target "
                    f"until sample collection is approved: {gap_id}"
                )
        validate_target_path("DEDICATED_TARGETS", target, errors)


def validate_future_triggers(
    future_gap_ids: set[str],
    future_contract_states: dict[str, object],
    errors: list[str],
) -> None:
    missing = sorted(future_gap_ids - set(config.TRIGGERS))
    for gap_id in missing:
        state = future_contract_states.get(gap_id)
        approved = state and state.sample_collection_allowed and not state.missing_adr_refs
        if approved:
            errors.append(f"TRIGGERS: approved future-work gap needs explicit sample trigger: {gap_id}")
        else:
            errors.append(f"TRIGGERS: future-work gap needs explicit contract-boundary trigger: {gap_id}")


def validate_high_priority_triggers(
    gaps: dict[str, collect_harness_sample_gaps.SampleGap],
    errors: list[str],
) -> None:
    missing = sorted(
        gap.id
        for gap in gaps.values()
        if gap.status.startswith("pending-") and priority_for(gap) in {"P0", "P1"} and gap.id not in config.TRIGGERS
    )
    for gap_id in missing:
        errors.append(f"TRIGGERS: P0/P1 gap needs explicit capture trigger: {gap_id}")


def priority_for(gap: collect_harness_sample_gaps.SampleGap) -> str:
    if gap.id in config.PRIORITIES:
        return config.PRIORITIES[gap.id]
    if gap.status == "future-work":
        return "P3"
    if gap.area in {"agentic-red-team", "workflow-skills"}:
        return "P2"
    return "P1"


def configured_target_paths() -> tuple[str, ...]:
    targets = set(config.DEDICATED_TARGETS.values())
    targets.add(config.FUTURE_WORK_CONTRACT_TARGET)
    targets.add(config.UPGRADE_DECISION_TARGET)
    targets.add(GENERIC_GAP_TARGET)
    return tuple(sorted(targets))


def validate_review_targets(errors: list[str]) -> None:
    for target in configured_target_paths():
        validate_target_path("target", target, errors)
        if review_commands.review_command_for(target) == "unknown":
            errors.append(f"review command missing for target: {target}")


def validate_active_readiness_routing(
    report: check_harness_burn_in_readiness.ReadinessReport,
    errors: list[str],
) -> None:
    active_capture_gates = active_capture_gate_values(report)
    missing_capture_gates = sorted(set(active_capture_gates) - set(config.CAPTURE_GATES))
    for capture_gate in missing_capture_gates:
        errors.append(f"CAPTURE_GATES: active capture gate missing from choices: {capture_gate}")

    invalid_ledger_actions = sorted({item.ledger_action for item in report.items} - set(config.LEDGER_ACTIONS))
    for ledger_action in invalid_ledger_actions:
        errors.append(f"LEDGER_ACTIONS: active ledger action missing from choices: {ledger_action}")

    invalid_readiness = sorted({item.readiness for item in report.items} - set(READINESS_STATES))
    for readiness in invalid_readiness:
        errors.append(f"READINESS_STATES: active readiness missing from choices: {readiness}")


def validate_focused_capture_gate_commands(
    report: check_harness_burn_in_readiness.ReadinessReport,
    errors: list[str],
) -> None:
    for capture_gate in real_sample_capture_gate_values(report):
        for command in command_coverage.focused_capture_gate_commands(capture_gate):
            if command not in HARNESS_SAMPLE_GAP_COMMANDS:
                errors.append(
                    "HARNESS_SAMPLE_GAP_COMMANDS: missing focused capture-gate command: "
                    f"{capture_gate} -> {command}"
                )


def validate_focused_real_sample_ledger_action_commands(
    report: check_harness_burn_in_readiness.ReadinessReport,
    errors: list[str],
) -> None:
    for ledger_action in real_sample_ledger_action_values(report):
        for command in command_coverage.focused_real_sample_ledger_action_commands(ledger_action):
            if command not in HARNESS_SAMPLE_GAP_COMMANDS:
                errors.append(
                    "HARNESS_SAMPLE_GAP_COMMANDS: missing focused ledger-action command: "
                    f"{ledger_action} -> {command}"
                )


def validate_focused_real_sample_readiness_commands(
    report: check_harness_burn_in_readiness.ReadinessReport,
    errors: list[str],
) -> None:
    for readiness in real_sample_readiness_values(report):
        for command in command_coverage.focused_real_sample_readiness_commands(readiness):
            if command not in HARNESS_SAMPLE_GAP_COMMANDS:
                errors.append(
                    "HARNESS_SAMPLE_GAP_COMMANDS: missing focused readiness command: "
                    f"{readiness} -> {command}"
                )


def validate_focused_real_sample_area_commands(
    report: check_harness_burn_in_readiness.ReadinessReport,
    errors: list[str],
) -> None:
    for area in real_sample_area_values(report):
        for command in command_coverage.focused_real_sample_area_commands(area):
            if command not in HARNESS_SAMPLE_GAP_COMMANDS:
                errors.append(
                    "HARNESS_SAMPLE_GAP_COMMANDS: missing focused area command: "
                    f"{area} -> {command}"
                )


def validate_focused_real_sample_priority_commands(
    report: check_harness_burn_in_readiness.ReadinessReport,
    errors: list[str],
) -> None:
    for priority in real_sample_priority_values(report):
        for command in command_coverage.focused_real_sample_priority_commands(priority):
            if command not in HARNESS_SAMPLE_GAP_COMMANDS:
                errors.append(
                    "HARNESS_SAMPLE_GAP_COMMANDS: missing focused priority command: "
                    f"{priority} -> {command}"
                )


def validate_pending_capture_focus_choices(
    report: check_harness_burn_in_readiness.ReadinessReport,
    errors: list[str],
) -> None:
    errors.extend(command_coverage.pending_capture_focus_choice_errors(report))


def active_capture_gate_values(report: check_harness_burn_in_readiness.ReadinessReport) -> tuple[str, ...]:
    return tuple(sorted({item.capture_gate for item in report.items}))


def real_sample_capture_gate_values(report: check_harness_burn_in_readiness.ReadinessReport) -> tuple[str, ...]:
    return command_coverage.real_sample_capture_gate_values(report)


def real_sample_area_values(report: check_harness_burn_in_readiness.ReadinessReport) -> tuple[str, ...]:
    return command_coverage.real_sample_area_values(report)


def real_sample_priority_values(report: check_harness_burn_in_readiness.ReadinessReport) -> tuple[str, ...]:
    return command_coverage.real_sample_priority_values(report)


def real_sample_ledger_action_values(report: check_harness_burn_in_readiness.ReadinessReport) -> tuple[str, ...]:
    return command_coverage.real_sample_ledger_action_values(report)


def real_sample_readiness_values(report: check_harness_burn_in_readiness.ReadinessReport) -> tuple[str, ...]:
    return command_coverage.real_sample_readiness_values(report)


def validate_target_path(label: str, target: str, errors: list[str]) -> None:
    if not target or target.startswith("/"):
        errors.append(f"{label}: target must be repo-relative: {target}")
        return
    if not (ROOT / target).exists():
        errors.append(f"{label}: target path missing: {target}")


def emit_text(report: CollectionConfigReport) -> None:
    print("Harness collection config audit:")
    print(f"- gaps: {report.gap_count}")
    print(f"- future gaps: {report.future_gap_count}")
    print(f"- dedicated targets: {report.dedicated_target_count}")
    print(f"- priority overrides: {report.priority_override_count}")
    print(f"- triggers: {report.trigger_count}")
    print(f"- configured targets: {report.configured_target_count}")
    print(f"- active capture gates: {report.active_capture_gate_count}")
    print(f"- real-sample capture gates: {report.real_sample_capture_gate_count}")
    print(f"- real-sample areas: {report.real_sample_area_count}")
    print(f"- real-sample priorities: {report.real_sample_priority_count}")
    print(f"- real-sample ledger actions: {report.real_sample_ledger_action_count}")
    print(f"- real-sample readiness states: {report.real_sample_readiness_count}")
    if report.ok:
        print("ERRORS: none")
        return
    print("ERRORS:")
    for error in report.errors:
        print(f"- {error}")


def main() -> int:
    args = parse_args()
    report = audit()
    if args.json:
        payload = asdict(report) | {"ok": report.ok}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        emit_text(report)
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
