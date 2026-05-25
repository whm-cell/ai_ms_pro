#!/usr/bin/env python3

from __future__ import annotations

from datetime import date
import json

from harness_sample_template_records import SampleTemplateItem
from harness_sample_template_records import checkpoint_resume_template
from harness_sample_template_records import future_work_contract_template
from harness_sample_template_records import generic_gap_template
from harness_sample_template_records import local_trace_template
from harness_sample_template_records import loop_scope_template
from harness_sample_template_records import preflight_template
from harness_sample_template_records import red_team_template
from harness_sample_template_records import task_profile_template
from harness_sample_template_records import upgrade_decision_template
from harness_sample_outcome_templates import outcome_candidate_template


def emit_sample_templates(items: list[SampleTemplateItem]) -> None:
    today = default_sampled_at()
    for item in items:
        if not should_emit_sample_template(item):
            continue
        print(json.dumps(sample_template(item, today), ensure_ascii=False, separators=(",", ":")))


def default_sampled_at() -> str:
    return date.today().isoformat()


def should_emit_sample_template(item: SampleTemplateItem) -> bool:
    return item.ledger_action != "no-sample-collection"


def sample_template(item: SampleTemplateItem, sampled_at: str) -> dict[str, object]:
    slug = item.gap_id.lower().removeprefix("gap-")
    if item.ledger_action == "review-existing-pending-slot":
        return outcome_candidate_template(item)
    if item.ledger_action == "review-upgrade-decision":
        return upgrade_decision_template(item, slug, sampled_at)
    if item.readiness == "needs-contract-or-adr-first":
        return future_work_contract_template(item, slug, sampled_at)
    if item.gap_id == "GAP-GUARDRAIL-PREFLIGHT-WARNING":
        return preflight_template(item, slug, sampled_at)
    if item.gap_id == "GAP-RUNTIME-LOOP-SCOPE-WARNING":
        return loop_scope_template(item, slug, sampled_at)
    if item.gap_id == "GAP-RUNTIME-STAGE-CHECKPOINT-RESUME":
        return checkpoint_resume_template(item.gap_id, slug, sampled_at)
    if item.gap_id == "GAP-TRACE-LOCAL-SUMMARY-BURNIN":
        return local_trace_template(item.gap_id, slug, sampled_at)
    if item.gap_id == "GAP-WORKFLOW-TASK-PROFILE-AUDIT":
        return task_profile_template(item.gap_id, slug)
    if item.gap_id.startswith("GAP-AGENTIC-"):
        return red_team_template(item, slug, sampled_at)
    return generic_gap_template(item, slug, sampled_at)
