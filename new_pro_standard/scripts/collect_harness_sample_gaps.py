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
    trigger: str
    missing_real_scenario: str
    evidence_needed: list[str]
    done_when: str


GAPS: tuple[SampleGap, ...] = (
    SampleGap(
        id="GAP-STARTER-HIGH-IMPACT-ACTION",
        area="agent-guardrail",
        status="pending-real-sample",
        trigger="A real destructive, externally visible, permission-changing, secret/env, deploy, or release action.",
        missing_real_scenario="A real high-impact action where the operator confirms or cancels before execution.",
        evidence_needed=["bounded action summary", "operator decision", "result or cancellation", "false-positive note"],
        done_when="The sample proves the action did not run before explicit confirmation.",
    ),
    SampleGap(
        id="GAP-STARTER-PRETOOL-WARNING",
        area="agent-guardrail",
        status="pending-real-sample",
        trigger="A real pre-tool warning from the new project's hook or review process.",
        missing_real_scenario="A warning before risky, large-output, remote-write, or destructive work.",
        evidence_needed=["finding code", "operator decision", "action taken", "bounded evidence ref"],
        done_when="The warning outcome is classified without storing raw prompt, transcript, or tool output.",
    ),
    SampleGap(
        id="GAP-STARTER-STOP-WARNING",
        area="runtime-durability",
        status="pending-real-sample",
        trigger="A real Stop-time warning about loop, scope churn, repeated failures, or token pressure.",
        missing_real_scenario="A long or noisy session where the operator records whether the warning helped.",
        evidence_needed=["warning kind", "recommendation", "action taken", "false-positive note"],
        done_when="The bounded sample shows whether checkpoint, pause, or narrowed validation advice was useful.",
    ),
    SampleGap(
        id="GAP-STARTER-CROSS-TASK-RESUME",
        area="runtime-durability",
        status="pending-real-sample",
        trigger="A later task resumes from handoff, checkpoint, status, or compressed context.",
        missing_real_scenario="A cross-task resume that avoids repeated exploration or missed verification.",
        evidence_needed=["resume source", "task class", "verification delta", "missing-field note"],
        done_when="The sample shows which recovery surface helped and what still had to be rediscovered.",
    ),
    SampleGap(
        id="GAP-STARTER-SECURITY-EVIDENCE",
        area="security-evidence",
        status="pending-real-sample",
        trigger="A real security workflow, dependency update, release, CodeQL, SBOM, or provenance event.",
        missing_real_scenario="A real event where advisory security evidence is triaged by an owner.",
        evidence_needed=["workflow or PR ref", "artifact names", "owner decision", "follow-up state"],
        done_when="The evidence is traceable to a real changed artifact and an explicit owner decision.",
    ),
    SampleGap(
        id="GAP-STARTER-WORKFLOW-SKILL",
        area="workflow-skills",
        status="pending-real-sample",
        trigger="A real task where a workflow skill is used, skipped, or compared with an alternative path.",
        missing_real_scenario="A task proving whether a candidate workflow skill changed the outcome or added process tax.",
        evidence_needed=["skill name", "use or skip reason", "verification", "process-tax outcome"],
        done_when="The sample explains why the skill should stay candidate, be promoted, or be removed.",
    ),
    SampleGap(
        id="GAP-STARTER-PR-OVERLAP",
        area="team-coordination",
        status="pending-real-sample",
        trigger="A real multi-person or multi-agent PR overlap with shared high-risk files.",
        missing_real_scenario="A conflict-control event where ownership or merge order had to be decided.",
        evidence_needed=["PR or branch refs", "overlap files", "decision", "merge outcome"],
        done_when="The sample proves whether the PR overlap guardrail prevented a coordination failure.",
    ),
    SampleGap(
        id="GAP-STARTER-REMOTE-INTEROP",
        area="trace-interop",
        status="future-work",
        trigger="A project-approved remote trace, eval, MCP, A2A, or external-provider interop probe.",
        missing_real_scenario="Remote interop with explicit auth, endpoint, redaction, and cost boundaries.",
        evidence_needed=["endpoint scope", "auth model", "redaction model", "status", "cost boundary"],
        done_when="A separate ADR or contract defines what was exported and what data was withheld.",
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="List starter-safe real-scenario sample gaps.")
    parser.add_argument("--area", action="append", default=[], help="Filter by area. Repeatable.")
    parser.add_argument("--include-future", action="store_true", help="Include future-work gaps.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def select_gaps(areas: set[str], include_future: bool = False) -> list[SampleGap]:
    return [
        gap
        for gap in GAPS
        if (include_future or gap.status != "future-work") and (not areas or gap.area in areas)
    ]


def gap_dict(gap: SampleGap) -> dict[str, Any]:
    payload = asdict(gap)
    payload["current_evidence"] = ["starter ledger is empty by design"]
    return payload


def emit_markdown(gaps: list[SampleGap]) -> None:
    print("# Harness Sample Gaps")
    print()
    print("| ID | Area | Status | Trigger | Missing scenario | Done when |")
    print("| --- | --- | --- | --- | --- | --- |")
    for gap in gaps:
        print(
            f"| {gap.id} | {gap.area} | {gap.status} | {gap.trigger} | "
            f"{gap.missing_real_scenario} | {gap.done_when} |"
        )


def main() -> int:
    args = parse_args()
    gaps = select_gaps(set(args.area), include_future=args.include_future)
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
