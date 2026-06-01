#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXECUTION_SNAPSHOT_DIR = ROOT / ".codex" / "runtime" / "execution-snapshots"
TRACE_INTEROP_REPORT_DIR = ROOT / ".codex" / "runtime" / "trace-interop"
TASK_OUTCOME_RESULT_DIR = ROOT / ".codex" / "runtime" / "task-outcome-evals"
GAP_EVIDENCE_PATH = ROOT / "docs" / "ai" / "standards" / "harness-sample-gap-evidence.jsonl"
REDTEAM_PATH = ROOT / "docs" / "ai" / "security" / "agentic-red-team-samples.jsonl"


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


def latest_result() -> dict[str, Any] | None:
    if not TASK_OUTCOME_RESULT_DIR.exists():
        return None
    files = sorted(path for path in TASK_OUTCOME_RESULT_DIR.glob("*.json") if path.is_file())
    if not files:
        return None
    return latest_json(files[-1])


def build_summary() -> dict[str, Any]:
    snapshots = sorted(EXECUTION_SNAPSHOT_DIR.glob("*.json")) if EXECUTION_SNAPSHOT_DIR.exists() else []
    latest_snapshot = latest_json(snapshots[-1]) if snapshots else None
    interop_reports = [
        latest_json(path)
        for path in sorted(TRACE_INTEROP_REPORT_DIR.glob("*.json"))
    ] if TRACE_INTEROP_REPORT_DIR.exists() else []
    interop_reports = [item for item in interop_reports if isinstance(item, dict)]
    gap_rows = load_jsonl(GAP_EVIDENCE_PATH)
    redteam_rows = load_jsonl(REDTEAM_PATH)
    task_result = latest_result()

    verified_remote = sum(1 for item in interop_reports if item.get("capability_level") == "verified-remote")
    pilot_remote = sum(1 for item in interop_reports if item.get("capability_level") == "pilot-remote")
    local_otlp = sum(1 for item in gap_rows if item.get("gap_id") == "GAP-TRACE-OTLP-PILOT-BURNIN")
    high_impact_confirmation = sum(
        1
        for item in redteam_rows
        if item.get("risk_family") == "human-agent-trust-confirmation" and item.get("outcome") == "accepted"
    )

    pass_rate = "0/0"
    if isinstance(task_result, dict):
        results = task_result.get("results")
        if isinstance(results, list) and results:
            passed = sum(1 for item in results if isinstance(item, dict) and item.get("task_outcome") == "pass")
            pass_rate = f"{passed}/{len(results)}"

    return {
        "durability_coverage": {
            "snapshot_count": len(snapshots),
            "latest_state": latest_snapshot.get("state") if isinstance(latest_snapshot, dict) else "none",
        },
        "verified_interop_coverage": {
            "verified_remote_reports": verified_remote,
            "pilot_remote_reports": pilot_remote,
            "local_otlp_burn_in_samples": local_otlp,
        },
        "task_eval_pass_rate": {
            "latest_result_pass_rate": pass_rate,
        },
        "high_impact_guardrail_confirmation_coverage": {
            "accepted_real_confirmation_samples": high_impact_confirmation,
        },
    }


def render_markdown(summary: dict[str, Any]) -> str:
    durability = summary["durability_coverage"]
    interop = summary["verified_interop_coverage"]
    task_eval = summary["task_eval_pass_rate"]
    guardrail = summary["high_impact_guardrail_confirmation_coverage"]
    return "\n".join(
        [
            "# Harness Capability Summary",
            "",
            f"- durability coverage: snapshots={durability['snapshot_count']} latest_state={durability['latest_state']}",
            f"- verified interop coverage: verified_remote={interop['verified_remote_reports']} pilot_remote={interop['pilot_remote_reports']} local_otlp_burn_in={interop['local_otlp_burn_in_samples']}",
            f"- task eval pass rate: {task_eval['latest_result_pass_rate']}",
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
