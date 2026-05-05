from __future__ import annotations

from pathlib import Path

from .command import run, text_or_stderr
from .config import CONTROL_PLANE_PATHS, EXPECTED_WORKFLOWS
from .model import Check
from .yaml_tools import has_event_trigger, has_top_key, simple_yaml_jobs, simple_yaml_top_map


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
        missing_meta = [key for key in ("on", "concurrency") if not has_top_key(text, key)]
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


def tracked_gitlinks(root: Path) -> tuple[list[str] | None, Check | None]:
    result = run(["git", "ls-files", "-s"], root)
    if result.returncode != 0:
        return None, Check("tracked gitlinks", "UNKNOWN", text_or_stderr(result) or "git ls-files failed")
    gitlinks: list[str] = []
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 4 and parts[0] == "160000":
            gitlinks.append(parts[3])
    return gitlinks, None


def gitmodules_paths(root: Path) -> set[str]:
    path = root / ".gitmodules"
    if not path.exists():
        return set()
    result = run(["git", "config", "--file", ".gitmodules", "--get-regexp", r"^submodule\..*\.path$"], root)
    if result.returncode != 0:
        return set()
    paths: set[str] = set()
    for line in result.stdout.splitlines():
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            paths.add(parts[1].strip())
    return paths


def orphan_gitlink_check(root: Path) -> Check:
    gitlinks, error = tracked_gitlinks(root)
    if error:
        return error
    assert gitlinks is not None
    if not gitlinks:
        return Check("tracked gitlinks", "OK", "no tracked gitlinks")
    configured = gitmodules_paths(root)
    orphaned = sorted(path for path in gitlinks if path not in configured)
    if orphaned:
        return Check("tracked gitlinks", "WARN", f"missing .gitmodules entries: {', '.join(orphaned)}")
    return Check("tracked gitlinks", "OK", "tracked gitlinks have .gitmodules entries")
