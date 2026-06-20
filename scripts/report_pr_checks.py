#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CHECK_ROLLUP_PERMISSION_NOTE = (
    "PR check rollups are unavailable with the current GitHub token; "
    "inspect the GitHub Actions page or rerun with a token that can read checks."
)


@dataclass(frozen=True)
class CheckSummary:
    name: str
    status: str
    conclusion: str
    url: str


@dataclass(frozen=True)
class PrChecksReport:
    number: int
    url: str
    state: str
    is_draft: bool
    head_ref_name: str
    base_ref_name: str
    merge_state_status: str
    review_decision: str
    checks_available: bool
    checks: list[CheckSummary]
    notes: list[str]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Report PR check status without modifying repository state.")
    parser.add_argument("pr", help="PR number or URL.")
    parser.add_argument("--repo", help="GitHub repository in owner/name form. Defaults to gh repo view.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args(argv)


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)


def run_checked(args: list[str]) -> str:
    result = run(args)
    if result.returncode != 0:
        output = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"{' '.join(args)} failed{f': {output}' if output else ''}")
    return result.stdout.strip()


def resolve_repo(explicit_repo: str | None) -> str:
    if explicit_repo:
        return explicit_repo
    raw = run_checked(["gh", "repo", "view", "--json", "nameWithOwner"])
    repo = json.loads(raw).get("nameWithOwner")
    if not repo:
        raise RuntimeError("Unable to resolve repository from gh repo view.")
    return str(repo)


def pr_token(value: str) -> str:
    match = re.search(r"/pull/(\d+)(?:\D|$)", value)
    return match.group(1) if match else value


def check_rollup_permission_error(message: str) -> bool:
    return "Resource not accessible by integration" in message and (
        "statusCheckRollup" in message or "workflowRun" in message
    )


def pr_view_fields(include_checks: bool) -> str:
    fields = [
        "number",
        "url",
        "state",
        "isDraft",
        "headRefName",
        "baseRefName",
        "mergeStateStatus",
        "reviewDecision",
    ]
    if include_checks:
        fields.append("statusCheckRollup")
    return ",".join(fields)


def load_pr_data(pr: str, repo: str) -> tuple[dict[str, Any], bool, list[str]]:
    args = ["gh", "pr", "view", pr_token(pr), "--repo", repo, "--json", pr_view_fields(include_checks=True)]
    result = run(args)
    if result.returncode == 0:
        return json.loads(result.stdout), True, []
    message = (result.stderr or result.stdout).strip()
    if not check_rollup_permission_error(message):
        raise RuntimeError(message)
    fallback = run_checked(["gh", "pr", "view", pr_token(pr), "--repo", repo, "--json", pr_view_fields(False)])
    return json.loads(fallback), False, [CHECK_ROLLUP_PERMISSION_NOTE]


def normalize_check(raw: dict[str, Any]) -> CheckSummary:
    name = str(raw.get("name") or raw.get("context") or raw.get("workflowName") or "unknown-check")
    status = str(raw.get("status") or "").upper()
    conclusion = str(raw.get("conclusion") or "").upper()
    url = str(raw.get("detailsUrl") or raw.get("url") or "")
    return CheckSummary(name=name, status=status, conclusion=conclusion, url=url)


def build_report(pr: str, repo: str) -> PrChecksReport:
    data, checks_available, notes = load_pr_data(pr, repo)
    raw_checks = data.get("statusCheckRollup") if checks_available else []
    checks = [normalize_check(item) for item in raw_checks if isinstance(item, dict)]
    return PrChecksReport(
        number=int(data["number"]),
        url=str(data["url"]),
        state=str(data.get("state") or ""),
        is_draft=bool(data.get("isDraft")),
        head_ref_name=str(data.get("headRefName") or ""),
        base_ref_name=str(data.get("baseRefName") or ""),
        merge_state_status=str(data.get("mergeStateStatus") or ""),
        review_decision=str(data.get("reviewDecision") or ""),
        checks_available=checks_available,
        checks=checks,
        notes=notes,
    )


def check_bucket(check: CheckSummary) -> str:
    if check.conclusion in {"FAILURE", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED"}:
        return "failed"
    if check.conclusion in {"SUCCESS", "NEUTRAL", "SKIPPED"}:
        return "passed"
    if check.status in {"QUEUED", "IN_PROGRESS", "PENDING", "REQUESTED", "WAITING"}:
        return "pending"
    return "unknown"


def emit_text(report: PrChecksReport) -> None:
    print(f"PR #{report.number}: {report.url}")
    print(f"- state: {report.state}")
    print(f"- draft: {str(report.is_draft).lower()}")
    print(f"- branch: {report.head_ref_name} -> {report.base_ref_name}")
    print(f"- merge_state_status: {report.merge_state_status or 'unknown'}")
    print(f"- review_decision: {report.review_decision or 'unknown'}")
    if not report.checks_available:
        print("- checks: unavailable")
        for note in report.notes:
            print(f"NOTE: {note}")
        return

    counts = Counter(check_bucket(check) for check in report.checks)
    print(
        "- checks: "
        f"{counts['passed']} passed, {counts['pending']} pending, "
        f"{counts['failed']} failed, {counts['unknown']} unknown"
    )
    for bucket in ("failed", "pending", "unknown"):
        matching = [check for check in report.checks if check_bucket(check) == bucket]
        if not matching:
            continue
        print(f"{bucket.upper()}:")
        for check in matching:
            state = check.conclusion or check.status or "UNKNOWN"
            suffix = f" ({check.url})" if check.url else ""
            print(f"  - {check.name}: {state}{suffix}")


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        repo = resolve_repo(args.repo)
        report = build_report(args.pr, repo)
    except RuntimeError as exc:
        print(f"PR checks report failed: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        emit_text(report)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
