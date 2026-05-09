from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PR_LIST_FIELDS = "number,title,state,headRefName,url,author"
PR_LIST_FIELDS_WITH_CHECKS = f"{PR_LIST_FIELDS},statusCheckRollup"
CHECK_ROLLUP_PERMISSION_NOTE = (
    "PR check rollups are unavailable with the current GitHub token; "
    "failed-open-PR audit was skipped for this run."
)


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)


def parse_pr_records(text: str) -> list[dict[str, object]]:
    data = json.loads(text)
    return data if isinstance(data, list) else []


def status_check_rollup_permission_error(message: str) -> bool:
    return "Resource not accessible by integration" in message and (
        "statusCheckRollup" in message or "workflowRun" in message
    )


def list_pr_records(fields: str) -> subprocess.CompletedProcess[str]:
    return run(["gh", "pr", "list", "--state", "all", "--limit", "200", "--json", fields])


def pr_records() -> tuple[list[dict[str, object]], bool, list[str]]:
    result = list_pr_records(PR_LIST_FIELDS_WITH_CHECKS)
    if result.returncode == 0:
        return parse_pr_records(result.stdout), True, []

    message = result.stderr.strip() or result.stdout.strip()
    if not status_check_rollup_permission_error(message):
        raise RuntimeError(message)

    fallback = list_pr_records(PR_LIST_FIELDS)
    if fallback.returncode != 0:
        raise RuntimeError(fallback.stderr.strip() or fallback.stdout.strip())
    return parse_pr_records(fallback.stdout), False, [CHECK_ROLLUP_PERMISSION_NOTE]
