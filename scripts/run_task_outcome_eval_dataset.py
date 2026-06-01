#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import shlex
import subprocess
import sys
from typing import Any

import check_task_outcome_eval_dataset


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = check_task_outcome_eval_dataset.DEFAULT_DATASET
DEFAULT_TIMEOUT = 180


@dataclass(frozen=True)
class CheckResult:
    command: str
    expected_outcome: str
    returncode: int | None
    grade: str


@dataclass(frozen=True)
class OutcomeResult:
    id: str
    title: str
    benchmark_group: str
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
        return CheckResult(command=command, expected_outcome=expected_outcome, returncode=None, grade="not-run")
    try:
        completed = subprocess.run(
            shlex.split(command),
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        if completed.returncode != 0:
            grade = "fail"
        elif expected_outcome == "review-required":
            grade = "review-required"
        elif expected_outcome == "warn":
            grade = "warn"
        else:
            grade = "pass"
        return CheckResult(command=command, expected_outcome=expected_outcome, returncode=completed.returncode, grade=grade)
    except (OSError, subprocess.TimeoutExpired):
        return CheckResult(command=command, expected_outcome=expected_outcome, returncode=None, grade="fail")


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
        task_outcome=aggregate_outcome(checks, dry_run),
        overreach=overreach,
        resume_stability=str(scorecard.get("resume_stability", "not-applicable")),
        guardrail_posture=str(scorecard.get("guardrail_posture", "not-expected")),
        command_count=len(checks),
        timeout_budget_seconds=len(checks) * timeout,
        checks=checks,
    )


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
        "dry_run": args.dry_run,
        "selected_count": len(results),
        "results": [asdict(item) for item in results],
    }
    if args.output:
        Path(args.output).write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for result in results:
            print(f"{result.id}: {result.task_outcome} | commands={result.command_count} | timeout_budget_seconds={result.timeout_budget_seconds} | overreach={result.overreach} | resume={result.resume_stability} | guardrail={result.guardrail_posture}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
