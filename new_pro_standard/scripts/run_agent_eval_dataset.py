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

import check_agent_eval_dataset
from agent_eval_trace_evidence import TraceEvidence, collect_trace_evidence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = check_agent_eval_dataset.DATASET_PATH
DEFAULT_TIMEOUT_SECONDS = 180
TAIL_LIMIT = 1200
REVIEW_GRADES = {"warn", "review-required"}


@dataclass(frozen=True)
class CheckResult:
    command: str
    expected_outcome: str
    returncode: int | None
    grade: str
    rationale: str
    stdout_tail: str
    stderr_tail: str


@dataclass(frozen=True)
class EvalResult:
    id: str
    title: str
    category: str
    grade: str
    checks: list[CheckResult]
    trace_evidence: TraceEvidence | None
    grading_signals: dict[str, list[str]]
    risk_tags: list[str]


@dataclass(frozen=True)
class RunReport:
    dataset_path: str
    dry_run: bool
    selected_count: int
    grade: str
    errors: list[str]
    evals: list[EvalResult]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run repo-local agent harness eval checks.")
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET), help="Eval JSONL dataset path.")
    parser.add_argument("--id", action="append", default=[], help="Only run one eval id. Repeatable.")
    parser.add_argument("--category", action="append", default=[], help="Only run one category. Repeatable.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and list checks without executing them.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS, help="Per-command timeout seconds.")
    return parser.parse_args()


def load_valid_items(dataset_path: Path) -> tuple[list[tuple[int, dict[str, Any]]], list[str]]:
    report = check_agent_eval_dataset.build_report(dataset_path)
    if report.errors:
        return [], report.errors
    errors: list[str] = []
    items = check_agent_eval_dataset.load_items(dataset_path, errors)
    return [(line_no, item) for line_no, item in items if isinstance(item, dict)], errors


def selected(item: dict[str, Any], ids: set[str], categories: set[str]) -> bool:
    if ids and item.get("id") not in ids:
        return False
    if categories and item.get("category") not in categories:
        return False
    return True


def build_report(
    dataset_path: Path,
    *,
    ids: set[str],
    categories: set[str],
    dry_run: bool,
    timeout: int,
) -> RunReport:
    items, errors = load_valid_items(dataset_path)
    evals: list[EvalResult] = []
    for _, item in items:
        if not selected(item, ids, categories):
            continue
        evals.append(run_eval(item, dry_run=dry_run, timeout=timeout))
    if not evals and not errors:
        errors.append("no eval items matched the selected filters")
    return RunReport(
        dataset_path=check_agent_eval_dataset.relative(dataset_path),
        dry_run=dry_run,
        selected_count=len(evals),
        grade=aggregate_eval_grades(evals, errors=errors, dry_run=dry_run),
        errors=errors,
        evals=evals,
    )


def run_eval(item: dict[str, Any], *, dry_run: bool, timeout: int) -> EvalResult:
    checks = [
        run_check(check, dry_run=dry_run, timeout=timeout)
        for check in item.get("expected_checks", [])
        if isinstance(check, dict)
    ]
    trace_evidence = collect_trace_evidence(item.get("trace_expectations"), dry_run=dry_run)
    return EvalResult(
        id=str(item["id"]),
        title=str(item["title"]),
        category=str(item["category"]),
        grade=aggregate_check_grades(checks, trace_evidence=trace_evidence, dry_run=dry_run),
        checks=checks,
        trace_evidence=trace_evidence,
        grading_signals=normalise_signals(item.get("grading_signals", {})),
        risk_tags=[str(tag) for tag in item.get("risk_tags", [])],
    )


def run_check(check: dict[str, Any], *, dry_run: bool, timeout: int) -> CheckResult:
    command = str(check["command"])
    expected = str(check["expected_outcome"])
    rationale = str(check["rationale"])
    if dry_run:
        return CheckResult(command, expected, None, "not-run", rationale, "", "")
    try:
        completed = subprocess.run(
            shlex.split(command),
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return CheckResult(
            command=command,
            expected_outcome=expected,
            returncode=completed.returncode,
            grade=grade_check(expected, completed.returncode),
            rationale=rationale,
            stdout_tail=tail(completed.stdout),
            stderr_tail=tail(completed.stderr),
        )
    except subprocess.TimeoutExpired as exc:
        return CheckResult(command, expected, None, "fail", f"{rationale} timed out after {timeout}s", tail(exc.stdout), tail(exc.stderr))
    except OSError as exc:
        return CheckResult(command, expected, None, "fail", f"{rationale} failed to start: {exc}", "", "")


def grade_check(expected_outcome: str, returncode: int) -> str:
    if returncode != 0:
        return "fail"
    if expected_outcome in REVIEW_GRADES:
        return expected_outcome
    return "pass"


def aggregate_check_grades(
    checks: list[CheckResult],
    *,
    trace_evidence: TraceEvidence | None,
    dry_run: bool,
) -> str:
    if not checks:
        return "fail"
    grades = {check.grade for check in checks}
    if trace_evidence is not None:
        grades.add(trace_evidence.grade)
    if "fail" in grades:
        return "fail"
    if dry_run:
        return "not-run"
    if grades & REVIEW_GRADES:
        return "review-required" if "review-required" in grades else "warn"
    return "pass"


def aggregate_eval_grades(evals: list[EvalResult], *, errors: list[str], dry_run: bool) -> str:
    if errors:
        return "fail"
    grades = {item.grade for item in evals}
    if "fail" in grades:
        return "fail"
    if dry_run:
        return "not-run"
    if grades & REVIEW_GRADES:
        return "review-required" if "review-required" in grades else "warn"
    return "pass"


def normalise_signals(value: object) -> dict[str, list[str]]:
    if not isinstance(value, dict):
        return {"pass": [], "warn": [], "fail": []}
    return {
        key: [str(item) for item in value.get(key, []) if isinstance(item, str)]
        for key in ("pass", "warn", "fail")
    }


def tail(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    value = value.strip()
    if len(value) <= TAIL_LIMIT:
        return value
    return value[-TAIL_LIMIT:]


def emit_text(report: RunReport) -> None:
    print("Agent harness eval run:")
    print(f"- dataset: {report.dataset_path}")
    print(f"- mode: {'dry-run' if report.dry_run else 'execute'}")
    print(f"- selected: {report.selected_count}")
    print(f"- grade: {report.grade}")
    for error in report.errors:
        print(f"ERROR: {error}")
    for item in report.evals:
        print(f"\n{item.id} [{item.grade}] {item.title}")
        for check in item.checks:
            code = "not-run" if check.returncode is None else str(check.returncode)
            print(f"- {check.grade}: rc={code} expected={check.expected_outcome} command={check.command}")
        if item.trace_evidence is not None:
            trace = item.trace_evidence
            print(
                f"- trace-evidence {trace.grade}: event={trace.required_event} "
                f"matched={trace.matched_records} artifacts={','.join(trace.trace_artifacts) or '-'} "
                f"trace_ids={','.join(trace.trace_ids) or '-'} "
                f"redaction={','.join(trace.redaction_states) or '-'}"
            )
            for error in trace.errors:
                print(f"  TRACE ERROR: {error}")


def main() -> int:
    args = parse_args()
    report = build_report(
        Path(args.dataset),
        ids=set(args.id),
        categories=set(args.category),
        dry_run=args.dry_run,
        timeout=args.timeout,
    )
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        emit_text(report)
    return 1 if report.grade == "fail" else 0


if __name__ == "__main__":
    sys.exit(main())
