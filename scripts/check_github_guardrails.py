#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path

from github_guardrails import (
    CONTROL_PLANE_PATHS as CONTROL_PLANE_PATHS,
    EXPECTED_REQUIRED_CHECKS as EXPECTED_REQUIRED_CHECKS,
    EXPECTED_WORKFLOWS as EXPECTED_WORKFLOWS,
    Check as Check,
    actions_permissions_check as actions_permissions_check,
    branch_protection_check as branch_protection_check,
    codeowners_check as codeowners_check,
    collect_checks as collect_checks,
    default_branch as default_branch,
    dependabot_check as dependabot_check,
    emit_text as emit_text,
    gitmodules_paths as gitmodules_paths,
    gh_api as gh_api,
    gh_auth as gh_auth,
    gh_available as gh_available,
    github_origin as github_origin,
    has_event_trigger as has_event_trigger,
    has_top_key as has_top_key,
    is_git_repo as is_git_repo,
    local_default_branch as local_default_branch,
    orphan_gitlink_check as orphan_gitlink_check,
    pr_template_check as pr_template_check,
    pr_touch_conflict_check as pr_touch_conflict_check,
    recommended_actions as recommended_actions,
    required_checks_from_payload as required_checks_from_payload,
    rulesets_check as rulesets_check,
    run as run,
    run_cli,
    simple_yaml_jobs as simple_yaml_jobs,
    simple_yaml_top_map as simple_yaml_top_map,
    text_or_stderr as text_or_stderr,
    tracked_gitlinks as tracked_gitlinks,
    workflow_checks as workflow_checks,
    workflow_remote_check as workflow_remote_check,
)


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    return run_cli(ROOT)


if __name__ == "__main__":
    sys.exit(main())
