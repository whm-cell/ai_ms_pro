#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from branch_hygiene_budget import (
    BranchHygieneBudget,
    BudgetFinding,
    PullRequestCounts,
    budget_findings,
    load_branch_hygiene_budget,
    pull_request_counts,
)
from branch_hygiene_output import emit_markdown, emit_text


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class BranchFinding:
    branch: str
    kind: str
    reason: str
    action: str


@dataclass(frozen=True)
class OpenPrFinding:
    number: int
    title: str
    branch: str
    author: str
    url: str
    failing_checks: list[str]
    action: str


@dataclass(frozen=True)
class BranchHygieneReport:
    repository: str
    default_branch: str
    delete_branch_on_merge: bool
    budget: BranchHygieneBudget
    pr_counts: PullRequestCounts
    budget_findings: list[BudgetFinding]
    open_pr_branches: list[str]
    failed_open_prs: list[OpenPrFinding]
    stale_remote_branches: list[BranchFinding]
    stale_local_branches: list[BranchFinding]
    unmanaged_remote_branches: list[BranchFinding]
    warnings: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit GitHub branch hygiene.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--markdown", action="store_true", help="Emit GitHub Actions summary markdown.")
    parser.add_argument("--strict", action="store_true", help="Fail when cleanup findings exist.")
    parser.add_argument(
        "--current-pr",
        type=int,
        default=0,
        help="Ignore the current PR's own check rollup when auditing failed open PRs.",
    )
    parser.add_argument("--delete-remote-stale", action="store_true", help="Delete remote branches whose PR is merged or closed.")
    parser.add_argument("--delete-local-stale", action="store_true", help="Delete local branches whose PR is merged or closed.")
    parser.add_argument(
        "--close-failed-dependabot-prs",
        action="store_true",
        help="Close open Dependabot PRs with failing checks and delete their branches.",
    )
    return parser.parse_args()


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)


def run_checked(args: list[str]) -> str:
    result = run(args)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout


def prune_remote_refs() -> None:
    run(["git", "fetch", "--prune", "origin"])


def repository_name() -> str:
    remote = run_checked(["git", "remote", "get-url", "origin"]).strip()
    if remote.startswith("git@github.com:"):
        return remote.removeprefix("git@github.com:").removesuffix(".git")
    if remote.startswith("https://github.com/"):
        return remote.removeprefix("https://github.com/").removesuffix(".git")
    raise RuntimeError(f"Unsupported GitHub origin URL: {remote}")


def repo_metadata(repo: str) -> tuple[str, bool]:
    data = json.loads(run_checked(["gh", "api", f"repos/{repo}"]))
    return str(data.get("default_branch") or "main"), bool(data.get("delete_branch_on_merge"))


def pr_records() -> list[dict[str, object]]:
    text = run_checked(
        [
            "gh",
            "pr",
            "list",
            "--state",
            "all",
            "--limit",
            "200",
            "--json",
            "number,title,state,headRefName,url,author,statusCheckRollup",
        ]
    )
    data = json.loads(text)
    return data if isinstance(data, list) else []


def remote_branches() -> list[str]:
    text = run_checked(["git", "for-each-ref", "--format=%(refname:strip=3)", "refs/remotes/origin"])
    return sorted(
        branch for branch in text.splitlines()
        if branch and branch != "HEAD" and not is_github_synthetic_ref(branch)
    )


def is_github_synthetic_ref(branch: str) -> bool:
    return branch.startswith("pull/")


def local_branches() -> list[str]:
    text = run_checked(["git", "branch", "--format=%(refname:short)"])
    return sorted(branch for branch in text.splitlines() if branch)


def current_branch() -> str:
    return run_checked(["git", "branch", "--show-current"]).strip()


def branch_pr_states(records: list[dict[str, object]]) -> dict[str, list[str]]:
    states: dict[str, list[str]] = {}
    for record in records:
        branch = str(record.get("headRefName") or "")
        state = str(record.get("state") or "")
        if branch and state:
            states.setdefault(branch, []).append(state)
    return states


def author_login(record: dict[str, object]) -> str:
    author = record.get("author")
    if isinstance(author, dict):
        return str(author.get("login") or "")
    return ""


def failing_checks(record: dict[str, object]) -> list[str]:
    checks = record.get("statusCheckRollup")
    if not isinstance(checks, list):
        return []
    failed: list[str] = []
    for check in checks:
        if not isinstance(check, dict):
            continue
        conclusion = str(check.get("conclusion") or "").upper()
        status = str(check.get("status") or "").upper()
        name = str(check.get("name") or check.get("context") or "unknown-check")
        if conclusion in {"FAILURE", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED"}:
            failed.append(name)
    return sorted(set(failed))


def record_number(record: dict[str, object]) -> int:
    number_value = record.get("number")
    try:
        return int(number_value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0


def failed_open_pr_findings(records: list[dict[str, object]], current_pr: int = 0) -> list[OpenPrFinding]:
    findings: list[OpenPrFinding] = []
    for record in records:
        if str(record.get("state") or "") != "OPEN":
            continue
        number = record_number(record)
        if current_pr and number == current_pr:
            continue
        failed = failing_checks(record)
        if not failed:
            continue
        branch = str(record.get("headRefName") or "")
        author = author_login(record)
        action = "review, fix, close PR, or delete branch after PR close"
        if author == "app/dependabot" or branch.startswith("dependabot/"):
            action = "close stale/failing Dependabot PR or let Dependabot recreate after base branch changes"
        findings.append(
            OpenPrFinding(
                number=number,
                title=str(record.get("title") or ""),
                branch=branch,
                author=author,
                url=str(record.get("url") or ""),
                failing_checks=failed,
                action=action,
            )
        )
    return sorted(findings, key=lambda finding: finding.number)


def build_report(current_pr: int = 0) -> BranchHygieneReport:
    prune_remote_refs()
    repo = repository_name()
    default_branch, delete_on_merge = repo_metadata(repo)
    budget = load_branch_hygiene_budget(ROOT)
    records = pr_records()
    states = branch_pr_states(records)
    open_pr_branches = sorted(branch for branch, values in states.items() if "OPEN" in values)
    failed_prs = failed_open_pr_findings(records, current_pr=current_pr)
    counts = pull_request_counts(records, failed_open=len(failed_prs))
    pr_budget_findings = budget_findings(counts, budget)
    protected = {default_branch, current_branch()}

    stale_remote: list[BranchFinding] = []
    unmanaged_remote: list[BranchFinding] = []
    for branch in remote_branches():
        if branch in protected or branch in open_pr_branches:
            continue
        values = states.get(branch, [])
        if any(state in {"MERGED", "CLOSED"} for state in values):
            stale_remote.append(
                BranchFinding(branch, "remote", "PR is merged or closed and no open PR owns the branch", "delete remote branch")
            )
        else:
            unmanaged_remote.append(
                BranchFinding(branch, "remote", "remote branch has no matching PR record", "review owner or delete manually")
            )

    stale_local: list[BranchFinding] = []
    for branch in local_branches():
        if branch in protected or branch in open_pr_branches:
            continue
        values = states.get(branch, [])
        if any(state in {"MERGED", "CLOSED"} for state in values):
            stale_local.append(
                BranchFinding(branch, "local", "PR is merged or closed and no open PR owns the branch", "delete local branch")
            )

    warnings: list[str] = []
    if not delete_on_merge:
        warnings.append("GitHub delete_branch_on_merge is disabled.")
    if stale_remote:
        warnings.append(f"{len(stale_remote)} stale remote branch(es) can be deleted.")
    if stale_local:
        warnings.append(f"{len(stale_local)} stale local branch(es) can be deleted.")
    if unmanaged_remote:
        warnings.append(f"{len(unmanaged_remote)} unmanaged remote branch(es) need owner review.")
    if failed_prs:
        warnings.append(f"{len(failed_prs)} open PR(s) have failing or pending checks.")
    for finding in pr_budget_findings:
        warnings.append(f"{finding.name} budget exceeded: {finding.count}/{finding.limit}.")

    return BranchHygieneReport(
        repository=repo,
        default_branch=default_branch,
        delete_branch_on_merge=delete_on_merge,
        budget=budget,
        pr_counts=counts,
        budget_findings=pr_budget_findings,
        open_pr_branches=open_pr_branches,
        failed_open_prs=failed_prs,
        stale_remote_branches=stale_remote,
        stale_local_branches=stale_local,
        unmanaged_remote_branches=unmanaged_remote,
        warnings=warnings,
    )


def delete_findings(findings: list[BranchFinding], remote: bool) -> None:
    for finding in findings:
        if remote:
            result = run(["git", "push", "origin", "--delete", finding.branch])
        else:
            result = run(["git", "branch", "-d", finding.branch])
        if result.returncode != 0:
            if remote and "remote ref does not exist" in result.stderr:
                continue
            raise RuntimeError(result.stderr.strip() or result.stdout.strip())


def close_failed_dependabot_prs(findings: list[OpenPrFinding]) -> None:
    for finding in findings:
        if finding.author != "app/dependabot" and not finding.branch.startswith("dependabot/"):
            continue
        comment = (
            "Closing this failing Dependabot PR to keep the active branch list clean. "
            "Dependabot can recreate a fresh PR after the base branch and workflow guardrails settle."
        )
        result = run(
            [
                "gh",
                "pr",
                "close",
                str(finding.number),
                "--delete-branch",
                "--comment",
                comment,
            ]
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip())


def main() -> int:
    args = parse_args()
    try:
        report = build_report(current_pr=args.current_pr)
        if args.close_failed_dependabot_prs:
            close_failed_dependabot_prs(report.failed_open_prs)
        if args.delete_remote_stale:
            delete_findings(report.stale_remote_branches, remote=True)
        if args.delete_local_stale:
            delete_findings(report.stale_local_branches, remote=False)
        if args.delete_remote_stale or args.delete_local_stale or args.close_failed_dependabot_prs:
            report = build_report(current_pr=args.current_pr)
    except RuntimeError as exc:
        print(f"Branch hygiene check: FAILED\nERROR: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    elif args.markdown:
        emit_markdown(report)
    else:
        emit_text(report)
    return 1 if args.strict and report.warnings else 0


if __name__ == "__main__":
    sys.exit(main())
