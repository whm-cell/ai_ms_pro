#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import sys


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
        status="pending-local-sample",
        missing_real_scenario="A local capture-server OTLP HTTP JSON export run recorded as explicit interop evidence.",
        target_docs=["docs/ai/standards/agent-trace-schema.md", "docs/ai/tool-contracts/contracts.json"],
        evidence_needed=["endpoint", "network_exported flag", "HTTP status", "redaction state"],
        done_when="The exporter reports network_exported=true only for an explicit endpoint and send action.",
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
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="List real-scenario sample gaps for the agentic harness.")
    parser.add_argument("--area", action="append", default=[], help="Filter by area. Repeatable.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def select_gaps(areas: set[str]) -> list[SampleGap]:
    return [gap for gap in GAPS if not areas or gap.area in areas]


def emit_markdown(gaps: list[SampleGap]) -> None:
    print("# Harness Sample Gaps")
    print()
    print("| ID | Area | Status | Missing scenario | Done when |")
    print("| --- | --- | --- | --- | --- |")
    for gap in gaps:
        print(f"| {gap.id} | {gap.area} | {gap.status} | {gap.missing_real_scenario} | {gap.done_when} |")


def main() -> int:
    args = parse_args()
    gaps = select_gaps(set(args.area))
    if not gaps:
        print("no sample gaps matched the selected filters", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps([asdict(gap) for gap in gaps], ensure_ascii=False, indent=2))
    else:
        emit_markdown(gaps)
    return 0


if __name__ == "__main__":
    sys.exit(main())
