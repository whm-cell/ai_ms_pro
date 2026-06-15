#!/usr/bin/env python3

from __future__ import annotations

from typing import Any

TEMPLATE_STAGE_CHECKPOINT_ID = "CP-2026-05-24-agentic-harness-burnin"


def text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def pending_boundary_blockers_for_record(record: dict[str, Any]) -> tuple[str, ...]:
    if text(record.get("outcome")) != "pending":
        return ()
    return sample_boundary_blockers_for_record(record)


def sample_boundary_blockers_for_record(record: dict[str, Any]) -> tuple[str, ...]:
    schema = text(record.get("schema_version"))
    blockers: list[str] = []
    if schema == "harness-sample-gap-evidence/v1":
        append_gap_evidence_blockers(record, blockers)
    elif schema == "agentic-red-team-sample/v1":
        append_red_team_blockers(record, blockers)
    elif schema == "local-trace-summary-sample/v1":
        append_local_trace_blockers(record, blockers)
    elif schema == "stage-checkpoint-resume-sample/v1":
        append_stage_checkpoint_resume_blockers(record, blockers)
    return tuple(blockers)


def append_gap_evidence_blockers(record: dict[str, Any], blockers: list[str]) -> None:
    source_type = text(record.get("source_type"))
    if record.get("no_external_claim") is not True:
        blockers.append("no_external_claim must stay true for pending shared gap evidence")
    if source_type.startswith("real-") and record.get("local_only") is not False:
        blockers.append("real pending gap evidence must set local_only=false")
    if source_type.startswith("local-") and record.get("local_only") is not True:
        blockers.append("local pending gap evidence must set local_only=true")


def append_red_team_blockers(record: dict[str, Any], blockers: list[str]) -> None:
    if record.get("local_only") is not True:
        blockers.append("red-team pending samples must set local_only=true")
    if record.get("no_external_claim") is not True:
        blockers.append("red-team pending samples must set no_external_claim=true")


def append_local_trace_blockers(record: dict[str, Any], blockers: list[str]) -> None:
    if record.get("no_network") is not True:
        blockers.append("local trace summary pending samples must set no_network=true")
    if record.get("local_only") is not True:
        blockers.append("local trace summary pending samples must set local_only=true")


def append_stage_checkpoint_resume_blockers(record: dict[str, Any], blockers: list[str]) -> None:
    if text(record.get("resume_scope")) != "cross-task":
        blockers.append("stage checkpoint pending samples must set resume_scope=cross-task")
    if text(record.get("checkpoint_id")) == TEMPLATE_STAGE_CHECKPOINT_ID:
        blockers.append("stage checkpoint pending samples must replace the template checkpoint_id")
