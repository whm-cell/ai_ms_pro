#!/usr/bin/env python3

from __future__ import annotations

from typing import Protocol

import collect_harness_sample_gaps
import harness_upgrade_decision_status


class SampleTemplateItem(Protocol):
    gap_id: str
    area: str
    readiness: str
    source_metric: str
    accepted_count: int
    upgrade_discussion_target: int
    boundary: str
    ledger_action: str
    next_evidence_needed: list[str]
    pending_slot_refs: tuple[str, ...]
    contract_blocker_state: object | None


def existing_placeholder_sample_id(item: SampleTemplateItem) -> str:
    if item.ledger_action != "fill-existing-placeholder":
        return ""
    if not item.pending_slot_refs:
        return ""
    return item.pending_slot_refs[0].split(" @ ", 1)[0].strip()


def sample_id_for_placeholder_or_new(
    item: SampleTemplateItem,
    *,
    prefix: str,
    slug: str,
    sampled_at: str,
) -> str:
    existing_sample_id = existing_placeholder_sample_id(item)
    if existing_sample_id:
        return existing_sample_id
    return f"{prefix}-{sampled_at}-{slug}"


def note_for_placeholder_or_new(item: SampleTemplateItem, default_note: str) -> str:
    existing_sample_id = existing_placeholder_sample_id(item)
    if not existing_sample_id:
        return default_note
    return (
        f"Fill existing pending placeholder row {existing_sample_id}; do not append a duplicate row. "
        "Replace TBD fields after a real event before accepting."
    )


def preflight_template(item: SampleTemplateItem, slug: str, sampled_at: str) -> dict[str, object]:
    return {
        "schema_version": "pre-tool-use-preflight-sample/v1",
        "id": sample_id_for_placeholder_or_new(item, prefix="PRE-SAMPLE", slug=slug, sampled_at=sampled_at),
        "gap_id": item.gap_id,
        "sampled_at": sampled_at,
        "source_type": "real-tool-call",
        "task_summary": "TBD: bounded task summary; no prompt, cwd, command, or raw output.",
        "risk_summary": "TBD: why the preflight warning mattered.",
        "hook_result": "warned",
        "triggered_findings": ["unbounded-large-output"],
        "operator_decisions": ["bounded-output"],
        "outcome": "pending",
        "false_positive": False,
        "action_taken": ["none"],
        "evidence_refs": ["docs/ai/standards/pre-tool-use-preflight.md"],
        "note": note_for_placeholder_or_new(
            item,
            "Template only; replace TBD fields after a real warning before accepting.",
        ),
    }


def loop_scope_template(item: SampleTemplateItem, slug: str, sampled_at: str) -> dict[str, object]:
    return {
        "schema_version": "loop-scope-monitor-sample/v1",
        "id": sample_id_for_placeholder_or_new(item, prefix="LOOP-SAMPLE", slug=slug, sampled_at=sampled_at),
        "gap_id": item.gap_id,
        "sampled_at": sampled_at,
        "source_type": "real-session",
        "task_summary": "TBD: bounded long-session summary; no transcript or raw runtime path.",
        "triggered_findings": ["repeated-command"],
        "monitor_recommendations": ["inspect-repeated-command"],
        "outcome": "pending",
        "false_positive": False,
        "action_taken": ["none"],
        "evidence_refs": ["docs/ai/standards/loop-scope-monitor.md"],
        "note": note_for_placeholder_or_new(
            item,
            "Template only; replace TBD fields after reviewing a real Stop warning.",
        ),
    }


def checkpoint_resume_template(gap_id: str, slug: str, sampled_at: str) -> dict[str, object]:
    return {
        "schema_version": "stage-checkpoint-resume-sample/v1",
        "id": f"CP-SAMPLE-{sampled_at}-{slug}",
        "gap_id": gap_id,
        "checkpoint_id": "CP-2026-06-15-starter-template",
        "resumed_at": sampled_at,
        "task_summary": "TBD: bounded cross-task resume summary.",
        "resume_scope": "cross-task",
        "used_checkpoint": True,
        "outcome": "pending",
        "avoided_rework": ["none"],
        "missed_validation_prevented": ["none"],
        "missing_fields": ["none"],
        "false_positive_notes": ["none"],
        "evidence_refs": ["docs/ai/checkpoints/README.md"],
        "note": "Template only; replace checkpoint_id and evidence refs for the actual resumed task.",
    }


def local_trace_template(gap_id: str, slug: str, sampled_at: str) -> dict[str, object]:
    return {
        "schema_version": "local-trace-summary-sample/v1",
        "id": f"TRACE-SUMMARY-SAMPLE-{sampled_at}-{slug}",
        "gap_id": gap_id,
        "sampled_at": sampled_at,
        "source_type": "real-local-report",
        "outcome": "pending",
        "summary_format": "json",
        "no_network": True,
        "local_only": True,
        "false_positive": False,
        "task_class": "TBD",
        "task_summary": "TBD: bounded task class summary.",
        "observation_count": 0,
        "trace_record_count": 0,
        "trace_count": 0,
        "promotion_needed_count": 0,
        "warning_count": 0,
        "redaction_states": ["unknown"],
        "key_findings": ["none"],
        "action_taken": ["none"],
        "evidence_refs": ["docs/ai/standards/local-trace-summary.md"],
        "note": "Template only; fill counts from a real local summary report.",
    }


def task_profile_template(gap_id: str, slug: str) -> dict[str, object]:
    return {
        "schema_version": "task-profile-audit-sample/v1",
        "id": f"SAMPLE-TASK-PROFILE-{slug}",
        "gap_id": gap_id,
        "source_type": "real-task",
        "outcome": "pending",
        "profile": "simple",
        "task_summary": "TBD: bounded task summary.",
        "read_files": ["docs/ai/index.md", "docs/ai/working-context.md"],
        "changed_files": [],
        "verification_commands": ["TBD: verification command"],
        "requirement_ids": [],
        "workstream_ids": [],
        "traceability_note": "not-applicable: pending template",
        "false_positive": False,
        "process_tax_note": "TBD: did scoped governance reduce or add process tax?",
        "evidence_refs": ["docs/ai/standards/task-profile-audit.md"],
    }


def upgrade_decision_template(item: SampleTemplateItem, slug: str, sampled_at: str) -> dict[str, object]:
    existing_decision_id = upgrade_decision_id(item, slug, sampled_at)
    return {
        "schema_version": "harness-upgrade-decision/v1",
        "id": existing_decision_id,
        "gap_id": item.gap_id,
        "decision": "defer-until-more-evidence",
        "decided_at": sampled_at,
        "readiness_at_decision": "ready-for-upgrade-discussion",
        "source_metric": item.source_metric,
        "accepted_count": item.accepted_count,
        "upgrade_discussion_target": item.upgrade_discussion_target,
        "false_positive_review": "TBD: summarize false-positive review before changing decision.",
        "repair_path": "TBD: describe the bounded repair path if the check misclassifies a task.",
        "cost_review": "TBD: describe CI/runtime cost before promoting or deferring.",
        "reviewer_burden": "TBD: describe reviewer burden before changing advisory status.",
        "rationale": "Draft only. Review the existing upgrade decision before collecting more samples.",
        "decision_ref": "docs/ai/harness-open-items.md",
        "evidence_refs": upgrade_decision_evidence_refs(item),
        "next_evidence_needed": upgrade_decision_next_evidence_needed(item),
        "no_raw_runtime": True,
    }


def upgrade_decision_evidence_refs(item: SampleTemplateItem) -> list[str]:
    if item.gap_id == "GAP-WORKFLOW-TASK-PROFILE-AUDIT":
        return [
            "docs/ai/standards/task-profile-audit-sample.jsonl",
            "docs/ai/standards/task-profile-audit.md",
            "docs/ai/agentic-harness-gap-roadmap.md",
        ]
    if item.area == "agentic-red-team":
        return [
            "docs/ai/security/agentic-red-team-samples.jsonl",
            "docs/ai/security/agentic-red-team-samples.md",
            "docs/ai/agentic-harness-gap-roadmap.md",
        ]
    return ["docs/ai/agentic-harness-gap-roadmap.md", "docs/ai/harness-open-items.md"]


def upgrade_decision_next_evidence_needed(item: SampleTemplateItem) -> list[str]:
    if item.next_evidence_needed:
        return list(item.next_evidence_needed)
    if item.gap_id == "GAP-WORKFLOW-TASK-PROFILE-AUDIT":
        return [
            "more real tasks outside the initial simple/complex/0-1-stage profile set",
            "false-positive review for profile selection disputes",
        ]
    if item.gap_id == "GAP-AGENTIC-SANDBOX-HONESTY":
        return [
            "real incidents beyond local continuation honesty cases",
            "native sandbox, hosted trace, MCP, A2A, or external-provider boundary evidence before promotion",
        ]
    if item.gap_id == "GAP-GUARDRAIL-SOURCE-BOUNDARY":
        return [
            "source-boundary samples from PRD, issue, web, Slack, or pasted-source inputs",
            "false-positive review for harmless source-priority corrections",
        ]
    if item.gap_id == "GAP-SEC-CONTROL-MATRIX-BURNIN":
        return [
            "control-matrix samples from external source types or multi-control mappings",
            "reviewer cost evidence before making control mapping checks blocking",
        ]
    return ["more diverse real samples and false-positive review before promotion"]


def upgrade_decision_id(item: SampleTemplateItem, slug: str, sampled_at: str) -> str:
    decisions, _warnings = harness_upgrade_decision_status.load_upgrade_decisions()
    snapshot = decisions.get(item.gap_id)
    if snapshot and snapshot.decision_id:
        return snapshot.decision_id
    return f"HUD-DRAFT-{sampled_at}-{slug}"


def red_team_template(item: SampleTemplateItem, slug: str, sampled_at: str) -> dict[str, object]:
    risk = collect_harness_sample_gaps.RED_TEAM_RISKS_BY_GAP.get(item.gap_id, "prompt-injection")
    return {
        "schema_version": "agentic-red-team-sample/v1",
        "id": f"REDTEAM-SAMPLE-{sampled_at}-{slug}",
        "sampled_at": sampled_at,
        "risk_family": risk,
        "source_type": "real-incident",
        "outcome": "pending",
        "upgrade_signal": "none",
        "local_only": True,
        "no_external_claim": True,
        "false_positive": False,
        "adversarial_summary": "TBD: bounded incident summary; no prompt, transcript, secret, or raw output.",
        "control_ids": ["AC-01"],
        "decision": "TBD: accepted, rejected, or pending decision.",
        "action_taken": ["none"],
        "evidence_refs": ["docs/ai/security/agentic-red-team-samples.md"],
        "checker_refs": ["scripts/check_agentic_red_team_samples.py"],
        "replay_commands": ["none"],
        "false_positive_rule": "TBD: what would make this a false positive?",
        "note": "Template only; real incident evidence must stay bounded.",
    }


def future_work_contract_template(item: SampleTemplateItem, slug: str, sampled_at: str) -> dict[str, object]:
    return {
        "schema_version": "harness-future-work-contract/v1",
        "id": future_work_contract_id(item, slug, sampled_at),
        "gap_id": item.gap_id,
        "status": "needs-adr",
        "contract_kind": future_work_contract_kind(item),
        "adr_required": True,
        "adr_refs": ["none"],
        "sample_collection_allowed": False,
        "no_external_claim": True,
        "auth_model": "TBD: no credential, token, account, or authority boundary is approved yet.",
        "endpoint_or_authority_scope": "TBD: no endpoint, hosted service, delegation path, or external authority is approved yet.",
        "redaction_or_boundary_model": "TBD: no remote redaction or bounded-evidence contract is approved yet.",
        "cost_or_stop_boundary": "TBD: no runtime, rate-limit, cost, cascade, or stop boundary is approved yet.",
        "decision": "Draft only. Do not collect samples before ADR or contract approval allows sampling.",
        "evidence_refs": ["docs/ai/agentic-harness-gap-roadmap.md", "docs/ai/standards/harness-future-work-contracts.jsonl"],
        "note": (
            "Template only; replace the existing future-work contract row, do not append a duplicate row. "
            f"Contract precondition draft, not sample evidence. Boundary: {item.boundary}"
        ),
    }


def future_work_contract_id(item: SampleTemplateItem, slug: str, sampled_at: str) -> str:
    state = getattr(item, "contract_blocker_state", None)
    contract_id = getattr(state, "contract_id", "")
    if isinstance(contract_id, str) and contract_id and contract_id != "missing":
        return contract_id
    return f"FWC-DRAFT-{sampled_at}-{slug}"


def future_work_contract_kind(item: SampleTemplateItem) -> str:
    if item.area == "trace-interop":
        return "remote-interop"
    return "agentic-control"


def generic_gap_template(item: SampleTemplateItem, slug: str, sampled_at: str) -> dict[str, object]:
    source_type = generic_source_type(item)
    endpoint_scope = "external-test-endpoint" if item.gap_id == "GAP-TRACE-REMOTE-INTEROP" else "none"
    remote_status = "not-sent" if item.gap_id == "GAP-TRACE-REMOTE-INTEROP" else "none"
    return {
        "schema_version": "harness-sample-gap-evidence/v1",
        "id": f"GAP-SAMPLE-{sampled_at}-{slug}",
        "gap_id": item.gap_id,
        "sampled_at": sampled_at,
        "source_type": source_type,
        "outcome": "pending",
        "local_only": source_type.startswith("local-"),
        "no_external_claim": True,
        "false_positive": False,
        "network_exported": False,
        "endpoint_scope": endpoint_scope,
        "remote_status": remote_status,
        "sample_summary": "TBD: bounded sample summary.",
        "decision": "TBD: owner/operator decision.",
        "boundary_note": item.boundary,
        "action_taken": ["none"],
        "evidence_refs": ["docs/ai/standards/harness-sample-gap-evidence.md"],
        "checker_refs": ["scripts/check_harness_sample_gap_evidence.py"],
    }


def generic_source_type(item: SampleTemplateItem) -> str:
    if item.gap_id == "GAP-TRACE-REMOTE-INTEROP":
        return "real-interop-run"
    if item.gap_id == "GAP-TRACE-OTLP-PILOT-BURNIN":
        return "local-interop-run"
    if item.gap_id == "GAP-SEC-SCHEDULED-RUN":
        return "real-workflow-run"
    if item.gap_id == "GAP-SEC-PR-DEPENDENCY":
        return "real-pr-or-release"
    if item.gap_id == "GAP-GUARDRAIL-CONFIRMATION":
        return "real-user-action"
    if item.gap_id == "GAP-GUARDRAIL-SOURCE-BOUNDARY":
        return "real-source-boundary"
    if item.area == "workflow-skills":
        return "real-workflow-task"
    if item.area == "agentic-red-team":
        return "real-incident"
    return "manual-review" if item.readiness == "needs-contract-or-adr-first" else "real-incident"
