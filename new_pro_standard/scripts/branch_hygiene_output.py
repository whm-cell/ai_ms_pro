from __future__ import annotations

from typing import Any


def emit_text(report: Any) -> None:
    print("Branch hygiene check:")
    print(f"- repository: {report.repository}")
    print(f"- default branch: {report.default_branch}")
    print(f"- delete_branch_on_merge: {str(report.delete_branch_on_merge).lower()}")
    print(f"- open PR branches: {len(report.open_pr_branches)}")
    print(f"- open total PRs: {report.pr_counts.open_total} / {report.budget.max_open_total_prs}")
    print(f"- open Codex PRs: {report.pr_counts.open_codex} / {report.budget.max_open_codex_prs}")
    print(f"- open Dependabot PRs: {report.pr_counts.open_dependabot} / {report.budget.max_open_dependabot_prs}")
    print(f"- failed open PRs: {len(report.failed_open_prs)} / {report.budget.max_failed_open_prs}")
    for finding in report.budget_findings:
        print(f"  - budget exceeded: {finding.name} {finding.count}/{finding.limit}; action={finding.action}")
    for finding in report.failed_open_prs:
        checks = ", ".join(finding.failing_checks)
        print(
            f"  - PR #{finding.number} {finding.branch}: checks={checks}; "
            f"action={finding.action}; url={finding.url}"
        )
    for title, findings in (
        ("stale remote branches", report.stale_remote_branches),
        ("stale local branches", report.stale_local_branches),
        ("unmanaged remote branches", report.unmanaged_remote_branches),
    ):
        print(f"- {title}: {len(findings)}")
        for finding in findings:
            print(f"  - {finding.branch}: {finding.reason}; action={finding.action}")
    for warning in report.warnings:
        print(f"WARN: {warning}")


def emit_markdown(report: Any) -> None:
    print("### Branch hygiene")
    print("")
    print(f"- Repository: `{report.repository}`")
    print(f"- Default branch: `{report.default_branch}`")
    print(f"- Delete branch on merge: `{str(report.delete_branch_on_merge).lower()}`")
    print(f"- Open PR branches: `{len(report.open_pr_branches)}`")
    print(f"- Open total PRs: `{report.pr_counts.open_total} / {report.budget.max_open_total_prs}`")
    print(f"- Open Codex PRs: `{report.pr_counts.open_codex} / {report.budget.max_open_codex_prs}`")
    print(f"- Open Dependabot PRs: `{report.pr_counts.open_dependabot} / {report.budget.max_open_dependabot_prs}`")
    print(f"- Stale remote branches: `{len(report.stale_remote_branches)}`")
    print(f"- Stale local branches: `{len(report.stale_local_branches)}`")
    print(f"- Failed open PRs: `{len(report.failed_open_prs)} / {report.budget.max_failed_open_prs}`")
    if report.budget_findings:
        print("")
        print("| Budget | Count | Limit | Required action |")
        print("| --- | --- | --- | --- |")
        for finding in report.budget_findings:
            print(f"| {finding.name} | `{finding.count}` | `{finding.limit}` | {finding.action} |")
    if report.failed_open_prs:
        print("")
        print("| PR | Branch | Failed checks | Suggested action |")
        print("| --- | --- | --- | --- |")
        for finding in report.failed_open_prs:
            checks = ", ".join(f"`{check}`" for check in finding.failing_checks)
            print(
                f"| [#{finding.number}]({finding.url}) | `{finding.branch}` | "
                f"{checks} | {finding.action} |"
            )
    if report.warnings:
        print("")
        for warning in report.warnings:
            print(f"- WARN: {warning}")
