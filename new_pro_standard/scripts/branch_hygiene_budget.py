from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback
    import tomli as tomllib  # type: ignore[no-redef]


@dataclass(frozen=True)
class BranchHygieneBudget:
    max_open_total_prs: int = 10
    max_open_codex_prs: int = 3
    max_open_dependabot_prs: int = 4
    max_failed_open_prs: int = 0


@dataclass(frozen=True)
class PullRequestCounts:
    open_total: int
    open_codex: int
    open_dependabot: int
    failed_open: int


@dataclass(frozen=True)
class BudgetFinding:
    name: str
    count: int
    limit: int
    action: str


def is_open_pr(record: dict[str, object]) -> bool:
    return str(record.get("state") or "").upper() == "OPEN"


def is_dependabot_pr(record: dict[str, object]) -> bool:
    branch = str(record.get("headRefName") or "")
    author = record.get("author")
    login = str(author.get("login") or "") if isinstance(author, dict) else ""
    return login == "app/dependabot" or branch.startswith("dependabot/")


def is_codex_pr(record: dict[str, object]) -> bool:
    branch = str(record.get("headRefName") or "")
    title = str(record.get("title") or "")
    return branch.startswith("codex/") or title.startswith("[codex]")


def load_branch_hygiene_budget(root: Path) -> BranchHygieneBudget:
    path = root / ".codex" / "harness.toml"
    if not path.exists():
        return BranchHygieneBudget()
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    raw_section = data.get("branch_hygiene", {})
    section = raw_section if isinstance(raw_section, dict) else {}
    return BranchHygieneBudget(
        max_open_total_prs=positive_int(section, "max_open_total_prs", BranchHygieneBudget.max_open_total_prs),
        max_open_codex_prs=positive_int(section, "max_open_codex_prs", BranchHygieneBudget.max_open_codex_prs),
        max_open_dependabot_prs=positive_int(
            section,
            "max_open_dependabot_prs",
            BranchHygieneBudget.max_open_dependabot_prs,
        ),
        max_failed_open_prs=non_negative_int(
            section,
            "max_failed_open_prs",
            BranchHygieneBudget.max_failed_open_prs,
        ),
    )


def positive_int(section: dict[str, Any], key: str, default: int) -> int:
    value = section.get(key, default)
    if not isinstance(value, int) or value < 1:
        return default
    return value


def non_negative_int(section: dict[str, Any], key: str, default: int) -> int:
    value = section.get(key, default)
    if not isinstance(value, int) or value < 0:
        return default
    return value


def pull_request_counts(records: list[dict[str, object]], failed_open: int) -> PullRequestCounts:
    open_records = [record for record in records if is_open_pr(record)]
    return PullRequestCounts(
        open_total=len(open_records),
        open_codex=sum(1 for record in open_records if is_codex_pr(record)),
        open_dependabot=sum(1 for record in open_records if is_dependabot_pr(record)),
        failed_open=failed_open,
    )


def budget_findings(counts: PullRequestCounts, budget: BranchHygieneBudget) -> list[BudgetFinding]:
    checks = [
        (
            "open total PRs",
            counts.open_total,
            budget.max_open_total_prs,
            "merge or close stale PRs before opening new automated work",
        ),
        (
            "open codex PRs",
            counts.open_codex,
            budget.max_open_codex_prs,
            "reuse the active Codex PR for the same stage or close stale Codex PRs",
        ),
        (
            "open Dependabot PRs",
            counts.open_dependabot,
            budget.max_open_dependabot_prs,
            "group dependency updates or close stale Dependabot PRs",
        ),
        (
            "failed open PRs",
            counts.failed_open,
            budget.max_failed_open_prs,
            "fix or close failed PRs before continuing automated PR creation",
        ),
    ]
    return [
        BudgetFinding(name=name, count=count, limit=limit, action=action)
        for name, count, limit, action in checks
        if count > limit
    ]
