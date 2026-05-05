#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path

from github_guardrails import (
    CONTROL_PLANE_PATHS,
    EXPECTED_REQUIRED_CHECKS,
    EXPECTED_WORKFLOWS,
    Check,
    actions_permissions_check,
    branch_protection_check,
    codeowners_check,
    collect_checks,
    default_branch,
    dependabot_check,
    emit_text,
    gitmodules_paths,
    gh_api,
    gh_auth,
    gh_available,
    github_origin,
    has_event_trigger,
    has_top_key,
    is_git_repo,
    local_default_branch,
    orphan_gitlink_check,
    pr_template_check,
    pr_touch_conflict_check,
    recommended_actions,
    required_checks_from_payload,
    rulesets_check,
    run,
    run_cli,
    simple_yaml_jobs,
    simple_yaml_top_map,
    text_or_stderr,
    tracked_gitlinks,
    workflow_checks,
    workflow_remote_check,
)


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    return run_cli(ROOT)


if __name__ == "__main__":
    sys.exit(main())
