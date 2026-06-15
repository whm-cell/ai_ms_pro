#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import collect_harness_sample_gaps
from harness_sample_boundary import pending_boundary_blockers_for_record


ROOT = Path(__file__).resolve().parents[1]
OUTCOMES = {"accepted", "pending", "rejected"}
RED_TEAM_GAP_BY_RISK = {risk: gap_id for gap_id, risk in collect_harness_sample_gaps.RED_TEAM_RISKS_BY_GAP.items()}
PLACEHOLDER_VALUES = {"", "none", "tbd", "unknown", "<missing>"}


@dataclass(frozen=True)
class LedgerSpec:
    name: str
    path: Path
    schema_version: str
    default_gap_id: str


@dataclass(frozen=True)
class SampleSlot:
    gap_id: str
    sample_id: str
    outcome: str
    source_type: str
    evidence_class: str
    pending_review_state: str
    review_blockers: tuple[str, ...]
    ledger_path: str
    line: int


LEDGERS = (
    LedgerSpec(
        "pretooluse-preflight",
        ROOT / "docs" / "ai" / "standards" / "pre-tool-use-preflight-samples.jsonl",
        "pre-tool-use-preflight-sample/v1",
        "GAP-GUARDRAIL-PREFLIGHT-WARNING",
    ),
    LedgerSpec(
        "loop-scope-monitor",
        ROOT / "docs" / "ai" / "standards" / "loop-scope-monitor-samples.jsonl",
        "loop-scope-monitor-sample/v1",
        "GAP-RUNTIME-LOOP-SCOPE-WARNING",
    ),
    LedgerSpec(
        "stage-checkpoint-resume",
        ROOT / "docs" / "ai" / "checkpoints" / "resume-samples.jsonl",
        "stage-checkpoint-resume-sample/v1",
        "GAP-RUNTIME-STAGE-CHECKPOINT-RESUME",
    ),
    LedgerSpec(
        "local-trace-summary",
        ROOT / "docs" / "ai" / "standards" / "local-trace-summary-samples.jsonl",
        "local-trace-summary-sample/v1",
        "GAP-TRACE-LOCAL-SUMMARY-BURNIN",
    ),
    LedgerSpec(
        "task-profile-audit",
        ROOT / "docs" / "ai" / "standards" / "task-profile-audit-sample.jsonl",
        "task-profile-audit-sample/v1",
        "GAP-WORKFLOW-TASK-PROFILE-AUDIT",
    ),
    LedgerSpec(
        "agentic-red-team",
        ROOT / "docs" / "ai" / "security" / "agentic-red-team-samples.jsonl",
        "agentic-red-team-sample/v1",
        "",
    ),
    LedgerSpec(
        "generic-gap-evidence",
        ROOT / "docs" / "ai" / "standards" / "harness-sample-gap-evidence.jsonl",
        "harness-sample-gap-evidence/v1",
        "",
    ),
)


def load_all_slots(errors: list[str], warnings: list[str]) -> list[SampleSlot]:
    slots: list[SampleSlot] = []
    seen_ids: dict[str, str] = {}
    for spec in LEDGERS:
        slots.extend(load_slots(spec, seen_ids, errors, warnings))
    return slots


def load_slots(
    spec: LedgerSpec,
    seen_ids: dict[str, str],
    errors: list[str],
    warnings: list[str],
) -> list[SampleSlot]:
    if not spec.path.exists():
        errors.append(f"{relative(spec.path)}: sample ledger missing")
        return []
    slots: list[SampleSlot] = []
    for line_no, raw_line in enumerate(spec.path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw_line.strip():
            errors.append(f"{relative(spec.path)}:{line_no}: blank line is not allowed")
            continue
        try:
            record = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            errors.append(f"{relative(spec.path)}:{line_no}: invalid JSON: {exc.msg}")
            continue
        if not isinstance(record, dict):
            errors.append(f"{relative(spec.path)}:{line_no}: sample must be a JSON object")
            continue
        sample_id = text(record.get("id"))
        if sample_id:
            previous = seen_ids.get(sample_id)
            if previous:
                errors.append(f"{relative(spec.path)}:{line_no}: duplicate sample id also seen at {previous}: {sample_id}")
            seen_ids[sample_id] = f"{relative(spec.path)}:{line_no}"
        else:
            errors.append(f"{relative(spec.path)}:{line_no}: id must be non-empty text")
        schema = text(record.get("schema_version"))
        if schema != spec.schema_version:
            errors.append(f"{relative(spec.path)}:{line_no}: schema_version must be {spec.schema_version}")
        outcome = text(record.get("outcome"))
        if outcome not in OUTCOMES:
            errors.append(f"{relative(spec.path)}:{line_no}: outcome must be one of {sorted(OUTCOMES)}")
        explicit_gap_id = text(record.get("gap_id"))
        if explicit_gap_id and spec.default_gap_id and explicit_gap_id != spec.default_gap_id:
            errors.append(f"{relative(spec.path)}:{line_no}: gap_id must be {spec.default_gap_id}")
        gap_id = gap_for_record(spec, record)
        if not gap_id:
            warnings.append(f"{relative(spec.path)}:{line_no}: sample is not mapped to a roadmap gap")
        slots.append(
            SampleSlot(
                gap_id=gap_id or "<unmapped>",
                sample_id=sample_id or "<missing>",
                outcome=outcome or "<missing>",
                source_type=text(record.get("source_type")) or "<missing>",
                evidence_class=evidence_class_for_record(record),
                pending_review_state=pending_review_state_for_record(record),
                review_blockers=pending_review_blockers_for_record(record),
                ledger_path=relative(spec.path),
                line=line_no,
            )
        )
    return slots


def gap_for_record(spec: LedgerSpec, record: dict[str, Any]) -> str:
    explicit_gap_id = text(record.get("gap_id"))
    if explicit_gap_id:
        return explicit_gap_id
    if spec.schema_version == "harness-sample-gap-evidence/v1":
        return ""
    if spec.schema_version == "agentic-red-team-sample/v1":
        risk = text(record.get("risk_family"))
        return RED_TEAM_GAP_BY_RISK.get(risk, f"risk:{risk}" if risk else "")
    return spec.default_gap_id


def evidence_class_for_record(record: dict[str, Any]) -> str:
    source_type = text(record.get("source_type"))
    if text(record.get("schema_version")) == "stage-checkpoint-resume-sample/v1":
        return "real"
    if source_type in {"synthetic-regression", "synthetic"}:
        return "synthetic"
    if source_type == "local-replay":
        return "local-replay"
    if source_type.startswith("local-"):
        return "local-only"
    if source_type.startswith("real-") or source_type == "real-task":
        return "real"
    if source_type == "manual-review":
        return "manual-review"
    return "unknown"


def pending_review_state_for_record(record: dict[str, Any]) -> str:
    if text(record.get("outcome")) != "pending":
        return "not-pending"
    schema = text(record.get("schema_version"))
    if schema == "pre-tool-use-preflight-sample/v1":
        return review_ready_or_placeholder(
            record,
            required_lists=("triggered_findings", "operator_decisions", "action_taken"),
            required_fields=("hook_result",),
        )
    if schema == "loop-scope-monitor-sample/v1":
        return review_ready_or_placeholder(
            record,
            required_lists=("triggered_findings", "monitor_recommendations", "action_taken"),
        )
    if schema == "local-trace-summary-sample/v1":
        if any(int_value(record.get(field)) > 0 for field in ("observation_count", "trace_record_count", "trace_count")):
            return review_ready_or_placeholder(record, required_lists=("key_findings", "action_taken"))
        return "placeholder"
    if schema == "stage-checkpoint-resume-sample/v1":
        return review_ready_or_placeholder(record, required_lists=("avoided_rework", "missed_validation_prevented"))
    if schema == "task-profile-audit-sample/v1":
        return review_ready_or_placeholder(record, required_lists=("verification_commands",), required_fields=("profile",))
    if schema == "agentic-red-team-sample/v1":
        return review_ready_or_placeholder(record, required_lists=("action_taken",), required_fields=("decision",))
    if schema == "harness-sample-gap-evidence/v1":
        return review_ready_or_placeholder(record, required_lists=("action_taken",), required_fields=("sample_summary", "decision"))
    return "unknown"


def pending_review_blockers_for_record(record: dict[str, Any]) -> tuple[str, ...]:
    if text(record.get("outcome")) != "pending":
        return ()
    schema = text(record.get("schema_version"))
    if schema == "pre-tool-use-preflight-sample/v1":
        return review_blockers(
            record,
            required_lists=("triggered_findings", "operator_decisions", "action_taken"),
            required_fields=("hook_result",),
        )
    if schema == "loop-scope-monitor-sample/v1":
        return review_blockers(
            record,
            required_lists=("triggered_findings", "monitor_recommendations", "action_taken"),
        )
    if schema == "local-trace-summary-sample/v1":
        if not any(int_value(record.get(field)) > 0 for field in ("observation_count", "trace_record_count", "trace_count")):
            return ("observation_count/trace_record_count/trace_count must include real report counts",)
        return review_blockers(record, required_lists=("key_findings", "action_taken"))
    if schema == "stage-checkpoint-resume-sample/v1":
        return review_blockers(record, required_lists=("avoided_rework", "missed_validation_prevented"))
    if schema == "task-profile-audit-sample/v1":
        return review_blockers(record, required_lists=("verification_commands",), required_fields=("profile",))
    if schema == "agentic-red-team-sample/v1":
        return review_blockers(record, required_lists=("action_taken",), required_fields=("decision",))
    if schema == "harness-sample-gap-evidence/v1":
        return review_blockers(record, required_lists=("action_taken",), required_fields=("sample_summary", "decision"))
    return ("schema_version is not supported by pending review-state audit",)


def review_blockers(
    record: dict[str, Any],
    *,
    required_lists: tuple[str, ...] = (),
    required_fields: tuple[str, ...] = (),
) -> tuple[str, ...]:
    blockers: list[str] = list(pending_boundary_blockers_for_record(record))
    for field in required_fields:
        if not meaningful_text(record.get(field)):
            blockers.append(f"{field} must be meaningful text")
    for field in required_lists:
        if not meaningful_list(record.get(field)):
            blockers.append(f"{field} must include a meaningful value")
    return tuple(blockers)


def review_ready_or_placeholder(
    record: dict[str, Any],
    *,
    required_lists: tuple[str, ...] = (),
    required_fields: tuple[str, ...] = (),
) -> str:
    if review_blockers(record, required_lists=required_lists, required_fields=required_fields):
        return "placeholder"
    return "review-ready"


def meaningful_list(value: Any) -> bool:
    if not isinstance(value, list):
        return False
    return any(meaningful_text(item) for item in value)


def meaningful_text(value: Any) -> bool:
    normalized = text(value).lower()
    return normalized not in PLACEHOLDER_VALUES and not normalized.startswith("tbd:")


def int_value(value: Any) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def pending_gap_ids(review_state: str | None = None) -> set[str]:
    errors: list[str] = []
    warnings: list[str] = []
    return {
        slot.gap_id
        for slot in load_all_slots(errors, warnings)
        if slot.outcome == "pending" and (review_state is None or slot.pending_review_state == review_state)
    }


def count_by_outcome(slots: list[SampleSlot]) -> dict[str, int]:
    counts = {outcome: 0 for outcome in sorted(OUTCOMES)}
    for slot in slots:
        if slot.outcome in counts:
            counts[slot.outcome] += 1
    return counts


def count_by_gap(slots: list[SampleSlot], outcome: str, evidence_class: str | None = None) -> dict[str, int]:
    counts: dict[str, int] = {}
    for slot in slots:
        if slot.outcome != outcome:
            continue
        if evidence_class is not None and slot.evidence_class != evidence_class:
            continue
        counts[slot.gap_id] = counts.get(slot.gap_id, 0) + 1
    return dict(sorted(counts.items()))


def count_by_evidence_class(slots: list[SampleSlot], outcome: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for slot in slots:
        if slot.outcome != outcome:
            continue
        counts[slot.evidence_class] = counts.get(slot.evidence_class, 0) + 1
    return dict(sorted(counts.items()))


def count_pending_by_review_state(slots: list[SampleSlot]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for slot in slots:
        if slot.outcome != "pending":
            continue
        counts[slot.pending_review_state] = counts.get(slot.pending_review_state, 0) + 1
    return dict(sorted(counts.items()))


def count_pending_by_gap_and_review_state(slots: list[SampleSlot], review_state: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for slot in slots:
        if slot.outcome != "pending" or slot.pending_review_state != review_state:
            continue
        counts[slot.gap_id] = counts.get(slot.gap_id, 0) + 1
    return dict(sorted(counts.items()))


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""
