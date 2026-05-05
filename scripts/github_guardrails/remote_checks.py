from __future__ import annotations

from pathlib import Path

from .config import EXPECTED_REQUIRED_CHECKS, EXPECTED_WORKFLOWS
from .git_remote import gh_api
from .model import Check


def actions_permissions_check(root: Path, repo: str, can_use_gh: bool) -> Check:
    if not can_use_gh:
        return Check("Actions permissions", "UNKNOWN", "requires authenticated gh API access")
    data, api_check = gh_api(root, f"repos/{repo}/actions/permissions")
    if not isinstance(data, dict):
        return Check("Actions permissions", "UNKNOWN", api_check.detail if api_check else "unavailable")
    enabled = data.get("enabled")
    allowed = data.get("allowed_actions")
    if enabled is False:
        return Check("Actions permissions", "WARN", "GitHub Actions is disabled")
    return Check("Actions permissions", "OK", f"enabled={enabled}; allowed_actions={allowed}")


def required_checks_from_payload(payload: object) -> set[str]:
    checks: set[str] = set()
    if isinstance(payload, dict):
        for key in ("contexts", "checks", "required_status_checks"):
            value = payload.get(key)
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        checks.add(item)
                    elif isinstance(item, dict):
                        checks.update(
                            str(item[name])
                            for name in ("context", "name")
                            if item.get(name)
                        )
        for value in payload.values():
            checks.update(required_checks_from_payload(value))
    elif isinstance(payload, list):
        for item in payload:
            checks.update(required_checks_from_payload(item))
    return checks


def workflow_remote_check(root: Path, repo: str, can_use_gh: bool) -> Check:
    if not can_use_gh:
        return Check("remote workflows", "UNKNOWN", "requires authenticated gh API access")
    data, api_check = gh_api(root, f"repos/{repo}/actions/workflows")
    if not isinstance(data, dict) or not isinstance(data.get("workflows"), list):
        return Check("remote workflows", "UNKNOWN", api_check.detail if api_check else "unavailable")
    paths = {item.get("path") for item in data["workflows"] if isinstance(item, dict)}
    missing = sorted(path for path in EXPECTED_WORKFLOWS if path not in paths)
    if missing:
        return Check("remote workflows", "WARN", f"GitHub does not list: {', '.join(missing)}")
    return Check("remote workflows", "OK", "expected workflows are visible through GitHub API")


def branch_protection_check(root: Path, repo: str, branch: str | None, can_use_gh: bool) -> Check:
    if not branch:
        return Check("branch protection", "UNKNOWN", "default branch is unknown")
    if not can_use_gh:
        return Check("branch protection", "UNKNOWN", "requires authenticated gh API access")
    data, api_check = gh_api(root, f"repos/{repo}/branches/{branch}/protection")
    if not isinstance(data, dict):
        return Check("branch protection", "UNKNOWN", api_check.detail if api_check else "unavailable")
    contexts = required_checks_from_payload(data.get("required_status_checks", {}))
    missing = sorted(EXPECTED_REQUIRED_CHECKS - contexts)
    review = data.get("required_pull_request_reviews") or {}
    conversations = data.get("required_conversation_resolution")
    warnings = []
    if missing:
        warnings.append(f"missing required checks: {', '.join(missing)}")
    if not review:
        warnings.append("pull request review gate not visible")
    elif not review.get("require_code_owner_reviews"):
        warnings.append("CODEOWNERS review not required")
    if not conversations:
        warnings.append("conversation resolution not required")
    if warnings:
        return Check("branch protection", "WARN", "; ".join(warnings))
    return Check("branch protection", "OK", f"required checks include {', '.join(sorted(contexts))}")


def rulesets_check(root: Path, repo: str, can_use_gh: bool) -> Check:
    if not can_use_gh:
        return Check("branch rulesets", "UNKNOWN", "requires authenticated gh API access")
    data, api_check = gh_api(root, f"repos/{repo}/rulesets?targets=branch")
    if not isinstance(data, list):
        return Check("branch rulesets", "UNKNOWN", api_check.detail if api_check else "unavailable")
    if not data:
        return Check("branch rulesets", "WARN", "no branch rulesets returned by GitHub API")
    names: list[str] = []
    required_checks: set[str] = set()
    for item in data:
        if not isinstance(item, dict):
            continue
        names.append(str(item.get("name", "<unnamed>")))
        ruleset_id = item.get("id")
        if ruleset_id:
            detail, _ = gh_api(root, f"repos/{repo}/rulesets/{ruleset_id}")
            required_checks.update(required_checks_from_payload(detail))
    missing = sorted(EXPECTED_REQUIRED_CHECKS - required_checks)
    if missing:
        return Check(
            "branch rulesets",
            "WARN",
            f"rulesets={', '.join(names)}; missing required checks: {', '.join(missing)}",
        )
    return Check("branch rulesets", "OK", f"rulesets={', '.join(names)} include expected checks")
