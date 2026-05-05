#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_WORKFLOWS = {
    ".github/workflows/governance-and-smoke.yml": {
        "jobs": {"governance", "windows-hook-runtime", "smoke"},
        "permissions": {"contents": "read"},
        "triggers": {"pull_request", "merge_group"},
    },
    ".github/workflows/dependency-review.yml": {
        "jobs": {"dependency-review"},
        "permissions": {"contents": "read", "pull-requests": "read"},
        "triggers": {"pull_request", "merge_group"},
    },
    ".github/workflows/security-evidence.yml": {
        "jobs": {"scorecard", "codeql", "sbom"},
        "permissions": {"contents": "read", "security-events": "write"},
        "triggers": {"pull_request", "push", "schedule", "workflow_dispatch"},
    },
}
EXPECTED_REQUIRED_CHECKS = {"governance", "windows-hook-runtime", "smoke", "dependency-review"}
CONTROL_PLANE_PATHS = (
    "AGENTS.md", ".agents/**", ".codex/**", ".github/CODEOWNERS",
    ".github/pull_request_template.md", ".github/workflows/**",
    "docs/ai/**", "docs/requirements/**", "scripts/check_*",
)


@dataclass(frozen=True)
class Check:
    name: str
    status: str
    detail: str

def run(cmd: list[str], root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(root), capture_output=True, text=True, check=False)

def text_or_stderr(result: subprocess.CompletedProcess[str]) -> str:
    return (result.stderr or result.stdout).strip().replace("\n", " ")

def is_git_repo(root: Path) -> Check:
    result = run(["git", "rev-parse", "--is-inside-work-tree"], root)
    if result.returncode == 0 and result.stdout.strip() == "true":
        return Check("git repository", "OK", "running inside a git work tree")
    return Check("git repository", "WARN", text_or_stderr(result) or "not a git work tree")

def github_origin(root: Path) -> tuple[Check, str | None, str | None]:
    result = run(["git", "remote", "get-url", "origin"], root)
    if result.returncode != 0:
        return Check("GitHub origin", "UNKNOWN", "origin remote is not configured"), None, None
    url = result.stdout.strip()
    match = re.search(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)(?:\.git)?$", url)
    if not match:
        return Check("GitHub origin", "WARN", f"origin is not a GitHub URL: {url}"), None, None
    repo = f"{match.group('owner')}/{match.group('repo')}"
    return Check("GitHub origin", "OK", f"origin={url}; repo={repo}"), url, repo

def gh_available(root: Path) -> Check:
    result = run(["gh", "--version"], root)
    if result.returncode != 0:
        return Check("gh CLI", "UNKNOWN", "gh is not installed or not on PATH")
    first_line = result.stdout.splitlines()[0] if result.stdout.splitlines() else "gh"
    return Check("gh CLI", "OK", first_line)

def gh_auth(root: Path) -> Check:
    result = run(["gh", "auth", "status"], root)
    if result.returncode == 0:
        return Check("gh auth", "OK", "gh reports an authenticated account")
    return Check("gh auth", "UNKNOWN", text_or_stderr(result) or "gh auth status failed")

def gh_api(root: Path, path: str) -> tuple[dict | list | None, Check | None]:
    result = run(["gh", "api", path], root)
    if result.returncode != 0:
        return None, Check("GitHub API", "UNKNOWN", f"{path}: {text_or_stderr(result)}")
    try:
        return json.loads(result.stdout), None
    except json.JSONDecodeError as exc:
        return None, Check("GitHub API", "UNKNOWN", f"{path}: invalid JSON: {exc}")

def local_default_branch(root: Path) -> str | None:
    result = run(["git", "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"], root)
    if result.returncode == 0 and "/" in result.stdout.strip():
        return result.stdout.strip().split("/", 1)[1]
    for candidate in ("main", "master"):
        exists = run(["git", "rev-parse", "--verify", f"origin/{candidate}"], root)
        if exists.returncode == 0:
            return candidate
    return None

def default_branch(root: Path, repo: str | None, can_use_gh: bool) -> tuple[Check, str | None]:
    if repo and can_use_gh:
        data, api_check = gh_api(root, f"repos/{repo}")
        if isinstance(data, dict) and data.get("default_branch"):
            branch = str(data["default_branch"])
            return Check("default branch", "OK", f"GitHub default branch is {branch}"), branch
        if api_check:
            fallback = local_default_branch(root)
            detail = f"{api_check.detail}; local fallback={fallback or 'unavailable'}"
            return Check("default branch", "UNKNOWN", detail), fallback
    fallback = local_default_branch(root)
    if fallback:
        return Check("default branch", "UNKNOWN", f"using local origin/HEAD fallback: {fallback}"), fallback
    return Check("default branch", "UNKNOWN", "could not determine default branch"), None

def simple_yaml_top_map(text: str, key: str) -> dict[str, str]:
    lines = text.splitlines()
    values: dict[str, str] = {}
    in_block = False
    for line in lines:
        if not in_block:
            in_block = line.strip() == f"{key}:"
            continue
        if line and not line.startswith(" "):
            break
        match = re.match(r"\s{2}([A-Za-z0-9_-]+):\s*(.+?)\s*$", line)
        if match:
            values[match.group(1)] = match.group(2).strip("'\"")
    return values


def simple_yaml_jobs(text: str) -> set[str]:
    lines = text.splitlines()
    jobs: set[str] = set()
    in_jobs = False
    for line in lines:
        if not in_jobs:
            in_jobs = line.strip() == "jobs:"
            continue
        if line and not line.startswith(" "):
            break
        match = re.match(r"\s{2}([A-Za-z0-9_-]+):\s*$", line)
        if match:
            jobs.add(match.group(1))
    return jobs


def has_top_key(text: str, key: str) -> bool:
    return any(line.strip() == f"{key}:" for line in text.splitlines())


def has_event_trigger(text: str, event: str) -> bool:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("on:") and event in stripped:
            return True
        if stripped != "on:":
            continue
        for nested in lines[index + 1:]:
            if nested and not nested.startswith(" "):
                break
            if re.match(rf"\s{{2}}{re.escape(event)}\s*:", nested):
                return True
    return False


def workflow_checks(root: Path) -> list[Check]:
    checks: list[Check] = []
    workflow_dir = root / ".github" / "workflows"
    if not workflow_dir.exists():
        return [Check("workflow files", "WARN", ".github/workflows is missing")]
    for rel_path, expected in EXPECTED_WORKFLOWS.items():
        path = root / rel_path
        if not path.exists():
            checks.append(Check(f"workflow {rel_path}", "WARN", "expected workflow is missing"))
            continue
        text = path.read_text(encoding="utf-8")
        missing_jobs = sorted(expected["jobs"] - simple_yaml_jobs(text))
        permissions = simple_yaml_top_map(text, "permissions")
        missing_permissions = {
            key: value
            for key, value in expected["permissions"].items()
            if permissions.get(key) != value
        }
        missing_meta = [
            key for key in ("on", "concurrency") if not has_top_key(text, key)
        ]
        missing_triggers = sorted(
            trigger for trigger in expected.get("triggers", set())
            if not has_event_trigger(text, trigger)
        )
        if missing_jobs or missing_permissions or missing_meta or missing_triggers:
            detail = []
            if missing_jobs:
                detail.append(f"missing jobs={','.join(missing_jobs)}")
            if missing_permissions:
                detail.append(f"permission mismatch={missing_permissions}")
            if missing_meta:
                detail.append(f"missing top-level keys={','.join(missing_meta)}")
            if missing_triggers:
                detail.append(f"missing triggers={','.join(missing_triggers)}")
            checks.append(Check(f"workflow {rel_path}", "WARN", "; ".join(detail)))
        else:
            checks.append(Check(f"workflow {rel_path}", "OK", "expected jobs and metadata found"))
    return checks


def codeowners_check(root: Path) -> Check:
    path = root / ".github" / "CODEOWNERS"
    if not path.exists():
        return Check("CODEOWNERS", "WARN", ".github/CODEOWNERS is missing")
    text = path.read_text(encoding="utf-8")
    missing = [pattern for pattern in CONTROL_PLANE_PATHS if pattern not in text]
    if missing:
        return Check("CODEOWNERS", "WARN", f"missing control-plane patterns: {', '.join(missing)}")
    return Check("CODEOWNERS", "OK", "control-plane ownership patterns are present")


def dependabot_check(root: Path) -> Check:
    path = root / ".github" / "dependabot.yml"
    if not path.exists():
        return Check("Dependabot", "WARN", ".github/dependabot.yml is missing")
    text = path.read_text(encoding="utf-8")
    missing = [token for token in ("github-actions", "pip", "npm") if token not in text]
    if missing:
        return Check("Dependabot", "WARN", f"missing ecosystems: {', '.join(missing)}")
    return Check("Dependabot", "OK", "github-actions, pip, and npm update entries are present")


def pr_template_check(root: Path) -> Check:
    paths = [
        root / ".github" / "pull_request_template.md",
        root / ".github" / "PULL_REQUEST_TEMPLATE" / "pull_request_template.md",
    ]
    existing = next((path for path in paths if path.exists()), None)
    if not existing:
        return Check("PR template", "WARN", "pull request template is missing")
    text = existing.read_text(encoding="utf-8")
    required = (
        "Requirement / Workstream",
        "Touch Set",
        "Parallel PR Conflict Check",
        "Verification",
        "Governance Impact",
    )
    missing = [section for section in required if section not in text]
    if missing:
        return Check("PR template", "WARN", f"missing sections: {', '.join(missing)}")
    return Check("PR template", "OK", f"template present at {existing.relative_to(root)}")


def pr_touch_conflict_check(root: Path) -> Check:
    path = root / "scripts" / "check_pr_touch_conflicts.py"
    if not path.exists():
        return Check("PR touch conflict checker", "WARN", "scripts/check_pr_touch_conflicts.py is missing")
    text = path.read_text(encoding="utf-8")
    required = ("--strict-high-risk", "HIGH_RISK_PATTERNS", "gh", "pr", "list")
    missing = [token for token in required if token not in text]
    if missing:
        return Check("PR touch conflict checker", "WARN", f"missing expected tokens: {', '.join(missing)}")
    return Check("PR touch conflict checker", "OK", "checker exists with high-risk and gh PR support")


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


def recommended_actions(checks: list[Check]) -> list[str]:
    actions: list[str] = []
    for check in checks:
        if check.name == "branch protection" and check.status == "UNKNOWN":
            actions.append(
                "Remote branch protection could not be proven. Configure GitHub branch protection or rulesets when the plan/repo visibility allows it."
            )
        elif check.name == "branch protection" and check.status == "WARN":
            actions.append(
                "Update branch protection to require PR review, CODEOWNERS review, conversation resolution, and expected required checks."
            )
        elif check.name == "branch rulesets" and check.status == "UNKNOWN":
            actions.append(
                "Remote branch rulesets could not be proven. Keep OPEN-01 blocked instead of claiming main is protected."
            )
        elif check.name == "branch rulesets" and check.status == "WARN":
            actions.append(
                "Update branch rulesets so required checks include governance, windows-hook-runtime, smoke, and dependency-review."
            )
    return actions


def emit_text(checks: list[Check]) -> None:
    print("GitHub guardrails check:")
    for check in checks:
        print(f"[{check.status}] {check.name}: {check.detail}")
    counts = {status: sum(1 for check in checks if check.status == status) for status in ("OK", "WARN", "UNKNOWN")}
    print(f"Summary: OK={counts['OK']} WARN={counts['WARN']} UNKNOWN={counts['UNKNOWN']}")
    actions = recommended_actions(checks)
    if actions:
        print("Recommended actions:")
        for action in actions:
            print(f"- {action}")


def main() -> int:
    root = ROOT
    checks: list[Check] = []

    git_check = is_git_repo(root)
    checks.append(git_check)
    if git_check.status == "WARN":
        emit_text(checks)
        return 0

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
    checks.extend([codeowners_check(root), dependabot_check(root), pr_template_check(root), pr_touch_conflict_check(root)])
    if repo:
        checks.extend(
            [
                actions_permissions_check(root, repo, authenticated_gh),
                workflow_remote_check(root, repo, authenticated_gh),
                branch_protection_check(root, repo, branch, authenticated_gh),
                rulesets_check(root, repo, authenticated_gh),
            ]
        )

    emit_text(checks)
    return 0


if __name__ == "__main__":
    sys.exit(main())
