#!/usr/bin/env python3

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXECUTION_SNAPSHOT_DIR = ROOT / ".codex" / "runtime" / "execution-snapshots"
TRACE_INTEROP_REPORT_DIR = ROOT / ".codex" / "runtime" / "trace-interop"
TASK_OUTCOME_RESULT_DIR = ROOT / ".codex" / "runtime" / "task-outcome-evals"
GAP_EVIDENCE_PATH = ROOT / "docs" / "ai" / "standards" / "harness-sample-gap-evidence.jsonl"
REDTEAM_PATH = ROOT / "docs" / "ai" / "security" / "agentic-red-team-samples.jsonl"
SUMMARY_BOUNDARY = "artifact-backed-local-runtime"
LATEST_SELECTION_POLICY = "recorded_at-then-file-mtime"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize the current harness capability surfaces.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        value = json.loads(raw)
        if isinstance(value, dict):
            rows.append(value)
    return rows


def latest_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    value = json.loads(path.read_text(encoding="utf-8"))
    return value if isinstance(value, dict) else None


def parse_recorded_at(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def load_records(directory: Path) -> list[tuple[Path, dict[str, Any]]]:
    if not directory.exists():
        return []
    records: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted(directory.rglob("*.json")):
        if not path.is_file():
            continue
        value = latest_json(path)
        if isinstance(value, dict):
            records.append((path, value))
    return records


def record_sort_key(record: tuple[Path, dict[str, Any]]) -> tuple[int, float, str]:
    path, value = record
    recorded_at = parse_recorded_at(value.get("recorded_at"))
    if recorded_at is not None:
        return (1, recorded_at.timestamp(), path.name)
    return (0, path.stat().st_mtime, path.name)


def latest_record(directory: Path) -> tuple[Path, dict[str, Any]] | None:
    records = load_records(directory)
    if not records:
        return None
    return max(records, key=record_sort_key)


def build_summary() -> dict[str, Any]:
    snapshot_records = load_records(EXECUTION_SNAPSHOT_DIR)
    latest_snapshot_record = latest_record(EXECUTION_SNAPSHOT_DIR)
    latest_snapshot = latest_snapshot_record[1] if latest_snapshot_record else None
    interop_records = load_records(TRACE_INTEROP_REPORT_DIR)
    interop_reports = [value for _, value in interop_records]
    latest_interop_record = latest_record(TRACE_INTEROP_REPORT_DIR)
    latest_interop = latest_interop_record[1] if latest_interop_record else None
    gap_rows = load_jsonl(GAP_EVIDENCE_PATH)
    redteam_rows = load_jsonl(REDTEAM_PATH)
    latest_task_result_record = latest_record(TASK_OUTCOME_RESULT_DIR)
    task_result = latest_task_result_record[1] if latest_task_result_record else None

    local_otlp = sum(1 for item in gap_rows if item.get("gap_id") == "GAP-TRACE-OTLP-PILOT-BURNIN")
    high_impact_confirmation = sum(
        1
        for item in redteam_rows
        if item.get("risk_family") == "human-confirmation"
        and item.get("source_type") == "real-incident"
        and item.get("outcome") == "accepted"
    )

    return {
        "summary_boundary": SUMMARY_BOUNDARY,
        "latest_selection_policy": LATEST_SELECTION_POLICY,
        "durability_coverage": summarize_durability(snapshot_records, latest_snapshot),
        "verified_interop_coverage": summarize_interop(interop_reports, latest_interop, local_otlp),
        "task_eval_pass_rate": summarize_task_eval(task_result),
        "high_impact_guardrail_confirmation_coverage": {
            "accepted_real_confirmation_samples": high_impact_confirmation,
        },
    }


def summarize_durability(
    snapshot_records: list[tuple[Path, dict[str, Any]]],
    latest_snapshot: dict[str, Any] | None,
) -> dict[str, Any]:
    latest_blockers = latest_snapshot.get("resume_blockers") if isinstance(latest_snapshot, dict) else []
    return {
        "snapshot_count": len(snapshot_records),
        "latest_state": latest_snapshot.get("state") if isinstance(latest_snapshot, dict) else "none",
        "latest_recorded_at": latest_snapshot.get("recorded_at") if isinstance(latest_snapshot, dict) else "none",
        "resume_ready_count": sum(1 for _, item in snapshot_records if item.get("resume_ready") is True),
        "blocked_resume_count": sum(1 for _, item in snapshot_records if item.get("resume_ready") is False),
        "latest_blockers": latest_blockers if isinstance(latest_blockers, list) else [],
    }


def summarize_interop(
    interop_reports: list[dict[str, Any]],
    latest_interop: dict[str, Any] | None,
    local_otlp: int,
) -> dict[str, Any]:
    return {
        "local_only_reports": count_level(interop_reports, "local-only"),
        "verified_remote_reports": count_level(interop_reports, "verified-remote"),
        "pilot_remote_reports": count_level(interop_reports, "pilot-remote"),
        "local_otlp_burn_in_samples": local_otlp,
        "latest_capability_level": latest_interop.get("capability_level") if isinstance(latest_interop, dict) else "none",
        "latest_recorded_at": latest_interop.get("recorded_at") if isinstance(latest_interop, dict) else "none",
        "latest_endpoint_scope": endpoint_scope(latest_interop),
        "latest_failure_mode": failure_mode(latest_interop),
    }


def count_level(reports: list[dict[str, Any]], level: str) -> int:
    return sum(1 for item in reports if item.get("capability_level") == level)


def summarize_task_eval(task_result: dict[str, Any] | None) -> dict[str, Any]:
    outcome_breakdown = {"pass": 0, "warn": 0, "review-required": 0, "fail": 0, "not-run": 0}
    blocked_reason_summary = {"blocked_by_resume": 0, "blocked_by_guardrail": 0}
    latest_benchmark_group = "none"
    result_count = 0
    if isinstance(task_result, dict) and isinstance(task_result.get("results"), list):
        for item in task_result["results"]:
            if not isinstance(item, dict):
                continue
            result_count += 1
            latest_benchmark_group = str(item.get("benchmark_group") or latest_benchmark_group)
            update_outcome_counts(item, outcome_breakdown, blocked_reason_summary)
    return {
        "latest_result_pass_rate": f"{outcome_breakdown['pass']}/{result_count}" if result_count else "0/0",
        "latest_outcome_breakdown": outcome_breakdown,
        "latest_recorded_at": task_result.get("recorded_at") if isinstance(task_result, dict) else "none",
        "latest_benchmark_group": latest_benchmark_group,
        "blocked_reason_summary": blocked_reason_summary,
    }


def update_outcome_counts(
    item: dict[str, Any],
    outcome_breakdown: dict[str, int],
    blocked_reason_summary: dict[str, int],
) -> None:
    outcome = item.get("task_outcome")
    if isinstance(outcome, str) and outcome in outcome_breakdown:
        outcome_breakdown[outcome] += 1
    if outcome in {"fail", "review-required"} and item.get("resume_stability") == "required":
        blocked_reason_summary["blocked_by_resume"] += 1
    if outcome in {"fail", "review-required"} and item.get("guardrail_posture") in {
        "review-required",
        "confirmation-gated",
    }:
        blocked_reason_summary["blocked_by_guardrail"] += 1


def endpoint_scope(report: dict[str, Any] | None) -> str:
    if not isinstance(report, dict):
        return "none"
    evidence = report.get("endpoint_evidence")
    if isinstance(evidence, dict) and isinstance(evidence.get("endpoint_scope"), str):
        return evidence["endpoint_scope"]
    value = report.get("endpoint_scope")
    return value if isinstance(value, str) and value else "none"


def failure_mode(report: dict[str, Any] | None) -> str:
    if not isinstance(report, dict):
        return "none"
    evidence = report.get("endpoint_evidence")
    if isinstance(evidence, dict) and isinstance(evidence.get("failure_mode"), str):
        return evidence["failure_mode"]
    remote_status = report.get("remote_status")
    if report.get("network_exported") is not True:
        return "not-sent"
    if isinstance(remote_status, dict) and remote_status.get("ok") is True:
        return "none"
    return "remote-status-not-ok"


def render_markdown(summary: dict[str, Any]) -> str:
    durability = summary["durability_coverage"]
    interop = summary["verified_interop_coverage"]
    task_eval = summary["task_eval_pass_rate"]
    guardrail = summary["high_impact_guardrail_confirmation_coverage"]
    return "\n".join(
        [
            "# Harness Capability Summary",
            "",
            f"- summary boundary: {summary['summary_boundary']} | latest selection: {summary['latest_selection_policy']}",
            f"- durability coverage: snapshots={durability['snapshot_count']} latest_state={durability['latest_state']} resume_ready={durability['resume_ready_count']} blocked_resume={durability['blocked_resume_count']} latest_blockers={durability['latest_blockers']} latest_recorded_at={durability['latest_recorded_at']}",
            f"- verified interop coverage: local_only={interop['local_only_reports']} pilot_remote={interop['pilot_remote_reports']} verified_remote={interop['verified_remote_reports']} latest_level={interop['latest_capability_level']} latest_endpoint_scope={interop['latest_endpoint_scope']} latest_failure_mode={interop['latest_failure_mode']} local_otlp_burn_in={interop['local_otlp_burn_in_samples']} latest_recorded_at={interop['latest_recorded_at']}",
            f"- task eval pass rate: {task_eval['latest_result_pass_rate']} breakdown={task_eval['latest_outcome_breakdown']} latest_group={task_eval['latest_benchmark_group']} blocked={task_eval['blocked_reason_summary']} latest_recorded_at={task_eval['latest_recorded_at']}",
            f"- high-impact guardrail confirmation coverage: accepted_real={guardrail['accepted_real_confirmation_samples']}",
        ]
    )


def main() -> int:
    args = parse_args()
    summary = build_summary()
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
