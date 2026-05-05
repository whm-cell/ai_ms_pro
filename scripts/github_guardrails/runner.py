from __future__ import annotations

from pathlib import Path

from .git_remote import default_branch, gh_auth, gh_available, github_origin, is_git_repo
from .local_checks import (
    codeowners_check,
    dependabot_check,
    orphan_gitlink_check,
    pr_template_check,
    pr_touch_conflict_check,
    workflow_checks,
)
from .model import Check
from .remote_checks import actions_permissions_check, branch_protection_check, rulesets_check, workflow_remote_check
from .reporting import emit_text


def collect_checks(root: Path) -> list[Check]:
    checks: list[Check] = []

    git_check = is_git_repo(root)
    checks.append(git_check)
    if git_check.status == "WARN":
        return checks

    origin_check, _, repo = github_origin(root)
    gh_check = gh_available(root)
    checks.extend([origin_check, gh_check])
    authenticated_gh = False
    if gh_check.status == "OK":
        auth_check = gh_auth(root)
        checks.append(auth_check)
        authenticated_gh = auth_check.status == "OK"

    branch_check, branch = default_branch(root, repo, authenticated_gh)
    checks.append(branch_check)
    checks.extend(workflow_checks(root))
    checks.extend(
        [
            codeowners_check(root),
            dependabot_check(root),
            pr_template_check(root),
            pr_touch_conflict_check(root),
            orphan_gitlink_check(root),
        ]
    )
    if repo:
        checks.extend(
            [
                actions_permissions_check(root, repo, authenticated_gh),
                workflow_remote_check(root, repo, authenticated_gh),
                branch_protection_check(root, repo, branch, authenticated_gh),
                rulesets_check(root, repo, authenticated_gh),
            ]
        )
    return checks


def run_cli(root: Path) -> int:
    emit_text(collect_checks(root))
    return 0
