#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys
from typing import Any

import check_task_outcome_eval_dataset


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = check_task_outcome_eval_dataset.DEFAULT_DATASET
DEFAULT_TIMEOUT = 180
SEVERITY_ORDER = {
    "not-run": 0,
    "pass": 1,
    "warn": 2,
    "review-required": 3,
    "fail": 4,
}
REVIEW_REQUIRED_LINE_RE = re.compile(
    r"^\s*(?:[-*]\s*)?(?:review-required|review required|confirmation-gated|confirmation gated)(?:\b|:)",
    re.IGNORECASE | re.MULTILINE,
)
WARNING_LINE_RE = re.compile(
    r"^\s*(?:[-*]\s*)?(?:warn:|warnings:|warning:|warning-only\b|warning only\b)",
    re.IGNORECASE | re.MULTILINE,
)


@dataclass(frozen=True)
class CheckResult:
    command: str
    expected_outcome: str
    returncode: int | None
    observed_signal: str
    grade: str


@dataclass(frozen=True)
class OutcomeResult:
    id: str
    title: str
    benchmark_group: str
    expected_command_class: str
    expected_changed_surface: list[str]
    task_outcome: str
    overreach: str
    resume_stability: str
    guardrail_posture: str
    command_count: int
    timeout_budget_seconds: int
    checks: list[CheckResult]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run repo-local task outcome eval dataset.")
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET), help=f"Dataset path. Default: {DEFAULT_DATASET}")
    parser.add_argument("--id", action="append", default=[], help="Only run one eval id. Repeatable.")
    parser.add_argument("--dry-run", action="store_true", help="List checks without executing them.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--output", help="Optional JSON output path.")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Per-command timeout seconds.")
    return parser.parse_args()


def load_items(dataset_path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    items = [item for _, item in check_task_outcome_eval_dataset.load_items(dataset_path, errors)]
    for index, item in enumerate(items, start=1):
        check_task_outcome_eval_dataset.validate_item(index, item, errors)
    return items, errors


def selected(item: dict[str, Any], ids: set[str]) -> bool:
    return not ids or item.get("id") in ids


def run_check(command: str, expected_outcome: str, *, dry_run: bool, timeout: int) -> CheckResult:
    if dry_run:
        return CheckResult(
            command=command,
            expected_outcome=expected_outcome,
            returncode=None,
            observed_signal="not-run",
            grade="not-run",
        )
    try:
        completed = subprocess.run(
            shlex.split(command),
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        observed_signal = detect_observed_signal(completed)
        grade = stricter_signal(expected_outcome, observed_signal)
        return CheckResult(
            command=command,
            expected_outcome=expected_outcome,
            returncode=completed.returncode,
            observed_signal=observed_signal,
            grade=grade,
        )
    except (OSError, subprocess.TimeoutExpired):
        return CheckResult(
            command=command,
            expected_outcome=expected_outcome,
            returncode=None,
            observed_signal="fail",
            grade="fail",
        )


def detect_observed_signal(completed: subprocess.CompletedProcess[str]) -> str:
    if completed.returncode != 0:
        return "fail"
    combined = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
    if REVIEW_REQUIRED_LINE_RE.search(combined):
        return "review-required"
    if WARNING_LINE_RE.search(combined):
        return "warn"
    return "pass"


def stricter_signal(expected_outcome: str, observed_signal: str) -> str:
    expected_rank = SEVERITY_ORDER.get(expected_outcome, SEVERITY_ORDER["pass"])
    observed_rank = SEVERITY_ORDER.get(observed_signal, SEVERITY_ORDER["pass"])
    if observed_rank > expected_rank:
        return observed_signal
    return expected_outcome if expected_outcome in SEVERITY_ORDER else observed_signal


def aggregate_outcome(checks: list[CheckResult], dry_run: bool) -> str:
    grades = {check.grade for check in checks}
    if "fail" in grades:
        return "fail"
    if dry_run:
        return "not-run"
    if "review-required" in grades:
        return "review-required"
    if "warn" in grades:
        return "warn"
    return "pass"


def run_item(item: dict[str, Any], *, dry_run: bool, timeout: int) -> OutcomeResult:
    checks = [
        run_check(str(check["command"]), str(check["expected_outcome"]), dry_run=dry_run, timeout=timeout)
        for check in item.get("expected_checks", [])
        if isinstance(check, dict)
    ]
    scorecard = item.get("scorecard", {}) if isinstance(item.get("scorecard"), dict) else {}
    overreach = "bounded" if scorecard.get("overreach_must_stay_bounded") else "unspecified"
    return OutcomeResult(
        id=str(item["id"]),
        title=str(item["title"]),
        benchmark_group=str(item["benchmark_group"]),
        expected_command_class=str(item["expected_command_class"]),
        expected_changed_surface=[str(value) for value in item.get("expected_changed_surface", [])],
        task_outcome=aggregate_outcome(checks, dry_run),
        overreach=overreach,
        resume_stability=str(scorecard.get("resume_stability", "not-applicable")),
        guardrail_posture=str(scorecard.get("guardrail_posture", "not-expected")),
        command_count=len(checks),
        timeout_budget_seconds=len(checks) * timeout,
        checks=checks,
    )


def aggregate_counts(results: list[OutcomeResult]) -> dict[str, int]:
    counts = {
        "pass_count": 0,
        "warn_count": 0,
        "review_required_count": 0,
        "fail_count": 0,
        "not_run_count": 0,
        "blocked_by_resume": 0,
        "blocked_by_guardrail": 0,
    }
    for result in results:
        if result.task_outcome == "pass":
            counts["pass_count"] += 1
        elif result.task_outcome == "warn":
            counts["warn_count"] += 1
        elif result.task_outcome == "review-required":
            counts["review_required_count"] += 1
        elif result.task_outcome == "fail":
            counts["fail_count"] += 1
        elif result.task_outcome == "not-run":
            counts["not_run_count"] += 1
        if result.task_outcome in {"fail", "review-required"} and result.resume_stability == "required":
            counts["blocked_by_resume"] += 1
        if result.task_outcome in {"fail", "review-required"} and result.guardrail_posture in {
            "review-required",
            "confirmation-gated",
        }:
            counts["blocked_by_guardrail"] += 1
    return counts


def write_output(path_text: str, payload: dict[str, Any]) -> None:
    path = Path(path_text).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    dataset_path = Path(args.dataset).expanduser()
    items, errors = load_items(dataset_path)
    if errors:
        print("task outcome eval runner failed dataset validation:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    results = [run_item(item, dry_run=args.dry_run, timeout=args.timeout) for item in items if selected(item, set(args.id))]
    if not results:
        print("task outcome eval runner failed: no matching eval items", file=sys.stderr)
        return 1
    payload = {
        "dataset_path": str(dataset_path.relative_to(ROOT)),
        "recorded_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "dry_run": args.dry_run,
        "selected_count": len(results),
        **aggregate_counts(results),
        "results": [asdict(item) for item in results],
    }
    if args.output:
        write_output(args.output, payload)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for result in results:
            print(f"{result.id}: {result.task_outcome} | commands={result.command_count} | timeout_budget_seconds={result.timeout_budget_seconds} | overreach={result.overreach} | resume={result.resume_stability} | guardrail={result.guardrail_posture}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
