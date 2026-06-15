from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import check_harness_placeholder_replacement
import harness_sample_slots
from harness_sample_boundary import sample_boundary_blockers_for_record


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MUTABLE_OUTCOME_FIELDS = {"outcome"}
MUTABLE_OUTCOME_FIELDS_BY_SCHEMA = {
    "harness-sample-gap-evidence/v1": {
        "outcome",
        "decision",
        "action_taken",
        "evidence_refs",
        "checker_refs",
        "false_positive",
    },
    "agentic-red-team-sample/v1": {
        "outcome",
        "decision",
        "action_taken",
        "evidence_refs",
        "checker_refs",
        "upgrade_signal",
        "false_positive",
        "false_positive_rule",
        "note",
    },
    "local-trace-summary-sample/v1": {
        "outcome",
        "action_taken",
        "evidence_refs",
        "key_findings",
        "false_positive",
        "note",
    },
    "pre-tool-use-preflight-sample/v1": {
        "outcome",
        "action_taken",
        "evidence_refs",
        "false_positive",
        "note",
    },
    "loop-scope-monitor-sample/v1": {
        "outcome",
        "action_taken",
        "evidence_refs",
        "false_positive",
        "note",
    },
    "stage-checkpoint-resume-sample/v1": {
        "outcome",
        "avoided_rework",
        "missed_validation_prevented",
        "missing_fields",
        "false_positive_notes",
        "evidence_refs",
        "note",
    },
    "task-profile-audit-sample/v1": {
        "outcome",
        "verification_commands",
        "traceability_note",
        "false_positive",
        "process_tax_note",
        "evidence_refs",
    },
}


def validate_candidate_matches_slot(
    candidate: dict[str, Any],
    slot: harness_sample_slots.SampleSlot,
    errors: list[str],
) -> None:
    target_schema = check_harness_placeholder_replacement.schema_for_ledger(slot.ledger_path)
    candidate_schema = text(candidate.get("schema_version"))
    if target_schema and candidate_schema != target_schema:
        errors.append(f"candidate schema_version {candidate_schema or '<missing>'} does not match target ledger schema {target_schema}")

    candidate_gap = candidate_gap_for_slot(candidate, slot.ledger_path)
    if not candidate_gap:
        errors.append("candidate gap_id must be non-empty text or derivable from its target ledger")
    elif candidate_gap != slot.gap_id:
        errors.append(f"candidate gap_id {candidate_gap} does not match pending row gap {slot.gap_id}")

    candidate_source_type = text(candidate.get("source_type"))
    if candidate_source_type != slot.source_type:
        errors.append(f"candidate source_type {candidate_source_type or '<missing>'} does not match pending row source_type {slot.source_type}")


def validate_candidate_boundary(candidate: dict[str, Any], errors: list[str]) -> None:
    for blocker in sample_boundary_blockers_for_record(candidate):
        errors.append(f"outcome candidate boundary invalid: {blocker}")


def load_target_record(slot: harness_sample_slots.SampleSlot, errors: list[str]) -> dict[str, Any]:
    ledger = ROOT / slot.ledger_path
    ledger_ref = f"{slot.ledger_path}:{slot.line}"
    if not ledger.exists():
        errors.append(f"target pending ledger row is unavailable: {ledger_ref}")
        return {}
    lines = ledger.read_text(encoding="utf-8").splitlines()
    if slot.line < 1 or slot.line > len(lines):
        errors.append(f"target pending ledger row is unavailable: {ledger_ref}")
        return {}
    try:
        record = json.loads(lines[slot.line - 1])
    except json.JSONDecodeError as exc:
        errors.append(f"{ledger_ref}: invalid target pending JSON: {exc.msg}")
        return {}
    if not isinstance(record, dict):
        errors.append(f"{ledger_ref}: target pending row must be a JSON object")
        return {}
    return record


def validate_stable_fields(candidate: dict[str, Any], original: dict[str, Any], errors: list[str]) -> None:
    if not original:
        return
    schema_version = text(candidate.get("schema_version"))
    mutable_fields = MUTABLE_OUTCOME_FIELDS_BY_SCHEMA.get(schema_version, DEFAULT_MUTABLE_OUTCOME_FIELDS)
    for field in sorted(set(original) | set(candidate)):
        if field in mutable_fields:
            continue
        if original.get(field) != candidate.get(field):
            errors.append(f"outcome candidate changed stable evidence field {field}")


def candidate_gap_for_slot(candidate: dict[str, Any], ledger_path: str) -> str:
    explicit_gap = text(candidate.get("gap_id"))
    if explicit_gap:
        return explicit_gap
    for spec in harness_sample_slots.LEDGERS:
        if harness_sample_slots.relative(spec.path) == ledger_path:
            return harness_sample_slots.gap_for_record(spec, candidate)
    return ""


def text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""
