#!/usr/bin/env python3

from __future__ import annotations

import argparse
from collections import Counter
import json
from typing import Any

import plan_harness_sample_collection
import summarize_harness_capabilities


LOOP_BOUNDARY = "bounded-loop-triage/no-write"
DEFAULT_LIMIT = 8


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize bounded loop triage candidates.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Maximum next actions to render.")
    return parser.parse_args()


def build_report(limit: int = DEFAULT_LIMIT) -> dict[str, Any]:
    capability = summarize_harness_capabilities.build_summary()
    queue_items = plan_harness_sample_collection.build_queue(
        actionable_only=True,
        pending_state="without-review-ready-pending",
    )
    actions = build_actions(capability, queue_items, limit=max(1, limit))
    return {
        "schema_version": "bounded-loop-triage/v1",
        "loop_boundary": LOOP_BOUNDARY,
        "loop_mode": "read-only-triage",
        "decision": decision_for(actions),
        "no_claims": [
            "no automatic code changes",
            "no ledger writes",
            "no blocking upgrade",
            "no hosted trace/eval claim",
            "no native sandbox claim",
            "no MCP/A2A runtime claim",
            "no external effect without explicit confirmation",
        ],
        "capability_signals": summarize_signals(capability),
        "queue_summary": summarize_queue(queue_items),
        "next_actions": actions,
    }


def build_actions(capability: dict[str, Any], queue_items: list[Any], *, limit: int) -> list[dict[str, Any]]:
    actions = []
    actions.extend(capability_actions(capability))
    actions.extend(queue_actions(queue_items))
    return sorted(actions, key=action_sort_key)[:limit]


def capability_actions(capability: dict[str, Any]) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    task_eval = capability.get("task_eval_pass_rate", {})
    interop = capability.get("verified_interop_coverage", {})
    guardrail = capability.get("high_impact_guardrail_confirmation_coverage", {})
    durability = capability.get("durability_coverage", {})

    if int_from(task_eval.get("latest_outcome_breakdown", {}).get("fail")):
        actions.append(
            action(
                "P0",
                "repair",
                "Review failed task outcome evals",
                "latest task outcome eval has fail results",
                ".codex/hooks/run_with_repo_python.sh scripts/run_task_outcome_eval_dataset.py --dry-run",
                ["scripts/run_task_outcome_eval_dataset.py", "docs/ai/evals/task-outcome-evals.jsonl"],
            )
        )
    if int_from(task_eval.get("blocked_reason_summary", {}).get("blocked_by_resume")):
        actions.append(
            action(
                "P1",
                "resume",
                "Inspect resume-blocked task outcomes",
                "task outcome eval reports resume-related blockers",
                ".codex/hooks/run_with_repo_python.sh scripts/run_task_outcome_eval_dataset.py --dry-run",
                ["docs/ai/evals/README.md", "scripts/run_task_outcome_eval_dataset.py"],
            )
        )
    if int_from(interop.get("verified_remote_reports")) == 0:
        actions.append(
            action(
                "P1",
                "sample",
                "Prepare remote interop capture review",
                "verified remote trace coverage remains zero",
                ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --capture-gate requires-approved-remote-interop --capture-card",
                ["docs/ai/harness-real-sample-watchlist.md", "docs/ai/harness-capability-model.md"],
            )
        )
    if int_from(guardrail.get("accepted_real_confirmation_samples")) < 2:
        actions.append(
            action(
                "P1",
                "sample",
                "Keep high-impact confirmation sample lane visible",
                "accepted real high-impact confirmation coverage is below burn-in target",
                ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --capture-gate requires-user-confirmed-high-impact-action --capture-card",
                ["docs/ai/security/agentic-control-matrix.md", "docs/ai/harness-real-sample-watchlist.md"],
            )
        )
    if int_from(durability.get("blocked_resume_count")):
        actions.append(
            action(
                "P2",
                "resume",
                "Review blocked runtime resume snapshots",
                "latest durability summary includes blocked resume snapshots",
                ".codex/hooks/run_with_repo_python.sh scripts/summarize_harness_capabilities.py",
                ["scripts/summarize_harness_capabilities.py", "docs/ai/checkpoints/README.md"],
            )
        )
    return actions


def queue_actions(queue_items: list[Any]) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    for item in queue_items:
        gap_id = str(getattr(item, "gap_id", "unknown-gap"))
        priority = str(getattr(item, "priority", "P2"))
        readiness = str(getattr(item, "readiness", "unknown"))
        capture_gate = str(getattr(item, "capture_gate", "unknown"))
        ledger_action = str(getattr(item, "ledger_action", "unknown"))
        actions.append(
            action(
                priority,
                "sample",
                f"Review next capture lane for {gap_id}",
                f"{readiness}; {capture_gate}; {ledger_action}",
                f".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py --gap-id {gap_id} --capture-card",
                [str(getattr(item, "target_artifact", "docs/ai/harness-real-sample-watchlist.md"))],
            )
        )
    return actions


def action(
    priority: str,
    loop_stage: str,
    title: str,
    reason: str,
    recommended_command: str,
    sources: list[str],
) -> dict[str, Any]:
    return {
        "priority": priority,
        "loop_stage": loop_stage,
        "title": title,
        "reason": reason,
        "recommended_command": recommended_command,
        "boundary": "operator-reviewed; no automatic write or external send",
        "sources": sources,
    }


def summarize_signals(capability: dict[str, Any]) -> dict[str, Any]:
    return {
        "durability": capability.get("durability_coverage", {}),
        "interop": capability.get("verified_interop_coverage", {}),
        "task_eval": capability.get("task_eval_pass_rate", {}),
        "high_impact_guardrail": capability.get("high_impact_guardrail_confirmation_coverage", {}),
    }


def summarize_queue(queue_items: list[Any]) -> dict[str, Any]:
    return {
        "actionable_without_review_ready_pending": len(queue_items),
        "by_priority": dict(sorted(count_attr(queue_items, "priority").items())),
        "by_readiness": dict(sorted(count_attr(queue_items, "readiness").items())),
        "by_ledger_action": dict(sorted(count_attr(queue_items, "ledger_action").items())),
        "by_capture_gate": dict(sorted(count_attr(queue_items, "capture_gate").items())),
    }


def count_attr(items: list[Any], name: str) -> Counter[str]:
    return Counter(str(getattr(item, name, "unknown")) for item in items)


def action_sort_key(item: dict[str, Any]) -> tuple[int, str, str]:
    priority_order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    return (priority_order.get(str(item.get("priority")), 9), str(item.get("loop_stage")), str(item.get("title")))


def decision_for(actions: list[dict[str, Any]]) -> str:
    if any(item.get("priority") == "P0" for item in actions):
        return "needs-operator-selection"
    if actions:
        return "monitor-and-select-next-loop"
    return "monitor-only"


def int_from(value: Any) -> int:
    return value if isinstance(value, int) else 0


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Bounded Loop Triage",
        "",
        f"- boundary: {report['loop_boundary']}",
        f"- mode: {report['loop_mode']}",
        f"- decision: {report['decision']}",
        f"- no claims: {', '.join(report['no_claims'])}",
        "",
        "## Queue Summary",
        "",
    ]
    queue = report["queue_summary"]
    lines.extend(
        [
            f"- actionable without review-ready pending: {queue['actionable_without_review_ready_pending']}",
            f"- by priority: {queue['by_priority']}",
            f"- by readiness: {queue['by_readiness']}",
            f"- by ledger action: {queue['by_ledger_action']}",
            f"- by capture gate: {queue['by_capture_gate']}",
            "",
            "## Next Actions",
            "",
        ]
    )
    if not report["next_actions"]:
        lines.append("- none")
    for item in report["next_actions"]:
        lines.append(
            f"- [{item['priority']}] {item['title']} | stage={item['loop_stage']} | reason={item['reason']} | command=`{item['recommended_command']}`"
        )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    report = build_report(limit=args.limit)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
