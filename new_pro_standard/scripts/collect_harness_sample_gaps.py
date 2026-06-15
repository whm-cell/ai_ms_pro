#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import sys
from typing import Any


@dataclass(frozen=True)
class SampleGap:
    id: str
    area: str
    status: str
    missing_real_scenario: str
    target_docs: list[str]
    evidence_needed: list[str]
    done_when: str


GAPS: tuple[SampleGap, ...] = (
    SampleGap(
        id="GAP-SEC-SCHEDULED-RUN",
        area="security-evidence",
        status="pending-real-sample",
        missing_real_scenario="A real scheduled or manually dispatched security evidence workflow run.",
        target_docs=["docs/ai/security/security-evidence-triage.md"],
        evidence_needed=["workflow run URL", "artifact names", "triage conclusion"],
        done_when="A real run is linked and its evidence is classified as pass, warn, or fail.",
    ),
    SampleGap(
        id="GAP-SEC-PR-DEPENDENCY",
        area="security-evidence",
        status="pending-real-sample",
        missing_real_scenario="A real PR or release that exercises dependency review, CodeQL, SBOM, or provenance evidence.",
        target_docs=["docs/ai/security/security-evidence-triage.md", "docs/ai/check-registry.md"],
        evidence_needed=["PR or release URL", "check run result", "owner decision"],
        done_when="Security evidence is traceable to the changed artifact and owner action.",
    ),
    SampleGap(
        id="GAP-GUARDRAIL-CONFIRMATION",
        area="ai-guardrail",
        status="pending-real-sample",
        missing_real_scenario="A real high-impact action requiring explicit user confirmation.",
        target_docs=["docs/ai/security/agent-guardrail-samples.md"],
        evidence_needed=["user confirmation", "command/action", "result", "rollback note"],
        done_when="The sample proves the action did not run before confirmation.",
    ),
    SampleGap(
        id="GAP-GUARDRAIL-PREFLIGHT-WARNING",
        area="ai-guardrail",
        status="pending-real-sample",
        missing_real_scenario="A real PreToolUse warning where the operator records bounded output, explicit confirmation, draft, cancellation, or false-positive outcome.",
        target_docs=[
            "docs/ai/standards/pre-tool-use-preflight.md",
            "docs/ai/standards/pre-tool-use-preflight-samples.jsonl",
            "docs/ai/check-registry.md",
        ],
        evidence_needed=[
            "finding code",
            "operator decision",
            "action taken",
            "false-positive classification",
            "bounded evidence ref",
        ],
        done_when="At least one accepted real preflight warning sample shows whether action-before-execution advice changed the command or tool call safely.",
    ),
    SampleGap(
        id="GAP-GUARDRAIL-SOURCE-BOUNDARY",
        area="ai-guardrail",
        status="pending-real-sample",
        missing_real_scenario="A second real source-boundary case from PRD, issue, Slack, web, or pasted user material.",
        target_docs=["docs/requirements/normalized", "docs/ai/security/agent-guardrail-samples.md"],
        evidence_needed=["source type", "normalization target", "boundary decision"],
        done_when="The source boundary is recorded without embedding full external content.",
    ),
    SampleGap(
        id="GAP-SEC-CONTROL-MATRIX-BURNIN",
        area="security-evidence",
        status="pending-real-sample",
        missing_real_scenario="A real security or guardrail sample classified through the agentic control matrix.",
        target_docs=["docs/ai/security/agentic-control-matrix.md", "docs/ai/security/security-evidence-triage.md"],
        evidence_needed=["control id", "evidence link", "owner decision", "blocking upgrade decision"],
        done_when="A real sample is mapped to a control id without upgrading a single advisory run to blocking.",
    ),
    SampleGap(
        id="GAP-WORKFLOW-CROSS-WS",
        area="workflow-skills",
        status="pending-real-sample",
        missing_real_scenario="A cross-workstream task that proves when workflow skills should be loaded.",
        target_docs=["docs/ai/skill-usage-samples.md"],
        evidence_needed=["workstream ids", "skill used or skipped", "resulting artifact"],
        done_when="The sample explains why the skill changed or did not change the outcome.",
    ),
    SampleGap(
        id="GAP-WORKFLOW-SIMPLE-SKIP",
        area="workflow-skills",
        status="pending-real-sample",
        missing_real_scenario="A simple task where workflow skills are explicitly skipped to prove escape-hatch behavior.",
        target_docs=["docs/ai/skill-usage-samples.md"],
        evidence_needed=["task summary", "skip reason", "verification", "process-tax outcome"],
        done_when="The sample proves a simple task was not slowed by Candidate workflow skills.",
    ),
    SampleGap(
        id="GAP-WORKFLOW-TASK-PROFILE-AUDIT",
        area="workflow-skills",
        status="pending-real-sample",
        missing_real_scenario="More real task profile audit records across simple, complex, and business-feature task classes.",
        target_docs=["docs/ai/standards/task-profile-audit.md", "docs/ai/check-registry.md"],
        evidence_needed=["profile", "source_type", "read_files", "changed_files", "verification_commands", "REQ/WS or not-applicable note", "process tax note"],
        done_when="Multiple accepted real samples show whether simple tasks avoid heavy surfaces and complex tasks retain traceability closure.",
    ),
    SampleGap(
        id="GAP-WORKFLOW-PR-OVERLAP",
        area="workflow-skills",
        status="pending-real-sample",
        missing_real_scenario="A real PR overlap or multi-agent edit conflict handled by the team PR conflict skill.",
        target_docs=["docs/ai/skill-usage-samples.md", "docs/ai/status"],
        evidence_needed=["PR or branch names", "overlap files", "decision", "merge outcome"],
        done_when="The pending team-pr-conflict-control samples can be accepted or rejected with evidence.",
    ),
    SampleGap(
        id="GAP-TRACE-OTLP-PILOT-BURNIN",
        area="trace-interop",
        status="pending-real-sample",
        missing_real_scenario="A local capture-server OTLP HTTP JSON export run recorded as explicit interop evidence.",
        target_docs=["docs/ai/standards/agent-trace-schema.md", "docs/ai/tool-contracts/contracts.json"],
        evidence_needed=["endpoint", "network_exported flag", "HTTP status", "redaction state"],
        done_when="The exporter reports network_exported=true only for an explicit endpoint and send action.",
    ),
    SampleGap(
        id="GAP-TRACE-LOCAL-SUMMARY-BURNIN",
        area="trace-interop",
        status="pending-real-sample",
        missing_real_scenario="Additional real no-network Local Trace Summary reports from different task classes.",
        target_docs=[
            "docs/ai/standards/local-trace-summary.md",
            "docs/ai/standards/local-trace-summary-samples.jsonl",
            "docs/ai/check-registry.md",
        ],
        evidence_needed=["summary format", "promotion count", "redaction states", "warning classification", "false-positive note"],
        done_when="Multiple real local reports classify promotion and redaction findings without implying remote interop coverage.",
    ),
    SampleGap(
        id="GAP-RUNTIME-STAGE-CHECKPOINT-RESUME",
        area="runtime-durability",
        status="pending-real-sample",
        missing_real_scenario="A cross-task resume sample outside the current harness-hardening thread that uses stage-checkpoint/v1 to avoid repeated exploration or missed validation.",
        target_docs=[
            "docs/ai/checkpoints/README.md",
            "docs/ai/checkpoints/stage-checkpoints.jsonl",
            "docs/ai/checkpoints/resume-samples.jsonl",
        ],
        evidence_needed=[
            "checkpoint id",
            "resume task",
            "next_action followed",
            "verification delta",
            "missing-field or false-positive note",
        ],
        done_when="A different task class confirms whether checkpoint fields stay sufficient before any ADR, blocking, or always-on upgrade discussion.",
    ),
    SampleGap(
        id="GAP-RUNTIME-LOOP-SCOPE-WARNING",
        area="runtime-durability",
        status="pending-real-sample",
        missing_real_scenario="A real long-session Stop loop/scope warning with bounded outcome and false-positive classification.",
        target_docs=[
            "docs/ai/standards/loop-scope-monitor.md",
            "docs/ai/standards/loop-scope-monitor-samples.jsonl",
            "docs/ai/check-registry.md",
        ],
        evidence_needed=[
            "finding code",
            "monitor recommendation",
            "action taken",
            "false-positive classification",
            "bounded evidence ref",
        ],
        done_when="At least one accepted real warning sample shows whether checkpoint, new-session, or narrower validation advice was useful.",
    ),
    SampleGap(
        id="GAP-TRACE-REMOTE-INTEROP",
        area="trace-interop",
        status="future-work",
        missing_real_scenario="OpenAI, OTLP, MCP, or A2A remote interoperability with real auth and endpoint constraints.",
        target_docs=["docs/ai/standards/agentic-harness-crosswalk.md", "docs/ai/harness-open-items.md"],
        evidence_needed=["endpoint", "auth model", "redaction model", "failure mode", "cost boundary"],
        done_when="A separate contract and ADR prove what was exported and what data was withheld.",
    ),
    SampleGap(
        id="GAP-AGENTIC-TOOL-SQUATTING",
        area="agentic-red-team",
        status="pending-real-sample",
        missing_real_scenario="A real tool or skill squatting attempt with similar name, changed provenance, or unexpected permissions.",
        target_docs=["docs/ai/security/agentic-control-matrix.md", "docs/ai/security/agentic-red-team-samples.jsonl", "docs/ai/skill-usage-samples.md"],
        evidence_needed=["skill or tool id", "provenance", "permission delta", "review decision"],
        done_when="A real sample proves catalog and lock review blocked or accepted the dependency intentionally.",
    ),
    SampleGap(
        id="GAP-AGENTIC-MEMORY-POISONING",
        area="agentic-red-team",
        status="pending-real-sample",
        missing_real_scenario="A real poisoned memory, runtime session, or recovered handoff that contains instruction-like content.",
        target_docs=["docs/ai/security/agentic-control-matrix.md", "docs/ai/security/agentic-red-team-samples.jsonl", "docs/ai/handoffs/active"],
        evidence_needed=["source type", "poisoning pattern", "boundary decision", "promoted summary"],
        done_when="The sample shows poisoned context was bounded and did not become canonical instructions.",
    ),
    SampleGap(
        id="GAP-AGENTIC-A2A-HANDOFF",
        area="agentic-red-team",
        status="pending-real-sample",
        missing_real_scenario="A real multi-agent handoff or A2A confusion case where authority, identity, or file scope is ambiguous.",
        target_docs=["docs/ai/security/agentic-control-matrix.md", "docs/ai/security/agentic-red-team-samples.jsonl", "docs/ai/status"],
        evidence_needed=["worker identity", "claimed authority", "allowed scope", "main-agent decision"],
        done_when="The sample records how untrusted handoff claims were verified before canonical writes or high-impact actions.",
    ),
    SampleGap(
        id="GAP-AGENTIC-CASCADE-STOP",
        area="agentic-red-team",
        status="future-work",
        missing_real_scenario="A real rogue or cascading agent loop with explicit stop-condition evidence.",
        target_docs=["docs/ai/security/agentic-control-matrix.md", "docs/ai/security/agentic-red-team-samples.jsonl", "docs/ai/harness-open-items.md"],
        evidence_needed=["loop trigger", "stop condition", "open loop", "user or owner decision"],
        done_when="The sample proves the harness stopped delegation or retries without expanding authority or context unboundedly.",
    ),
    SampleGap(
        id="GAP-AGENTIC-SANDBOX-HONESTY",
        area="agentic-red-team",
        status="pending-real-sample",
        missing_real_scenario="A real resume or sandbox-boundary task where claims must distinguish verified checks from inferred context.",
        target_docs=["docs/ai/security/agentic-control-matrix.md", "docs/ai/security/agentic-red-team-samples.jsonl", "docs/ai/security/agent-harness-security.md"],
        evidence_needed=["verified command", "inferred fact", "sandbox boundary", "final claim wording"],
        done_when="The sample proves final reporting did not claim sandbox, remote, test, or real-sample coverage beyond evidence.",
    ),
)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="List real-scenario sample gaps for the agentic harness.")
    parser.add_argument("--area", action="append", default=[], help="Filter by area. Repeatable.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()

def select_gaps(areas: set[str]) -> list[SampleGap]:
    return [gap for gap in GAPS if not areas or gap.area in areas]

def current_evidence_for(gap: SampleGap) -> list[str]:
    try:
        if gap.id == "GAP-GUARDRAIL-PREFLIGHT-WARNING":
            import check_pre_tool_use_preflight_samples as preflight

            report = preflight.build_report()
            return [
                f"accepted real warning samples: {report.accepted_real_warning_sample_count}",
                f"accepted real samples: {report.accepted_real_sample_count}",
            ]
        if gap.id == "GAP-RUNTIME-LOOP-SCOPE-WARNING":
            import check_loop_scope_monitor_samples as loop_scope

            report = loop_scope.build_report()
            return [
                f"accepted real warning samples: {report.accepted_warning_sample_count}",
                f"accepted real samples: {report.accepted_real_sample_count}",
            ]
        if gap.id == "GAP-RUNTIME-STAGE-CHECKPOINT-RESUME":
            import check_stage_checkpoints as checkpoints

            report = checkpoints.build_report()
            return [
                f"accepted resume samples: {report.accepted_sample_count}",
                f"accepted cross-task samples: {report.accepted_cross_task_sample_count}",
            ]
        if gap.id == "GAP-TRACE-LOCAL-SUMMARY-BURNIN":
            import check_local_trace_summary_samples as local_trace

            report = local_trace.build_report()
            task_classes = ", ".join(f"{key}={value}" for key, value in sorted(report.accepted_real_task_classes.items()))
            return [
                f"accepted real local reports: {report.accepted_real_report_count}",
                f"accepted real task classes: {report.accepted_real_task_class_count}",
                f"accepted real task-class details: {task_classes or 'none'}",
                f"real local reports: {report.real_report_count}",
            ]
        if gap.id == "GAP-WORKFLOW-TASK-PROFILE-AUDIT":
            import check_task_profile_audit as task_profile

            report = task_profile.build_report()
            profiles = ", ".join(f"{key}={value}" for key, value in sorted(report.accepted_real_profiles.items()))
            return [
                f"accepted real task-profile samples: {report.accepted_real_sample_count}",
                f"accepted real profiles: {profiles or 'none'}",
            ]
        risk = RED_TEAM_RISKS_BY_GAP.get(gap.id)
        if risk:
            import check_agentic_red_team_samples as red_team

            report = red_team.build_report()
            return [
                f"accepted local-replay or real samples for {risk}: {report.accepted_by_risk.get(risk, 0)}",
                f"accepted real red-team incidents for {risk}: {report.accepted_real_by_risk.get(risk, 0)}",
            ]
        import check_harness_sample_gap_evidence as gap_evidence

        report = gap_evidence.build_report()
        return [
            f"generic ledger records: {report.records_by_gap.get(gap.id, 0)}",
            "accepted real/local samples: "
            f"real={report.accepted_real_by_gap.get(gap.id, 0)}, local={report.accepted_local_by_gap.get(gap.id, 0)}",
        ]
    except Exception as exc:
        return [f"current evidence unavailable: {exc.__class__.__name__}"]

RED_TEAM_RISKS_BY_GAP = {
    "GAP-AGENTIC-TOOL-SQUATTING": "skill-squatting",
    "GAP-AGENTIC-MEMORY-POISONING": "memory-poisoning",
    "GAP-AGENTIC-A2A-HANDOFF": "a2a-handoff-confusion",
    "GAP-AGENTIC-CASCADE-STOP": "cascade-autonomy",
    "GAP-AGENTIC-SANDBOX-HONESTY": "sandbox-claim-honesty",
}

def gap_dict(gap: SampleGap) -> dict[str, Any]:
    payload = asdict(gap)
    payload["current_evidence"] = current_evidence_for(gap)
    return payload

def emit_markdown(gaps: list[SampleGap]) -> None:
    print("# Harness Sample Gaps")
    print()
    print("| ID | Area | Status | Current evidence | Missing scenario | Done when |")
    print("| --- | --- | --- | --- | --- | --- |")
    for gap in gaps:
        current = "; ".join(current_evidence_for(gap)) or "not tracked by a sample checker yet"
        print(f"| {gap.id} | {gap.area} | {gap.status} | {current} | {gap.missing_real_scenario} | {gap.done_when} |")

def main() -> int:
    args = parse_args()
    gaps = select_gaps(set(args.area))
    if not gaps:
        print("no sample gaps matched the selected filters", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps([gap_dict(gap) for gap in gaps], ensure_ascii=False, indent=2))
    else:
        emit_markdown(gaps)
    return 0

if __name__ == "__main__":
    sys.exit(main())
