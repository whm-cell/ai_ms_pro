from __future__ import annotations

import json
import re
from pathlib import Path

from .command import run, text_or_stderr
from .model import Check


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
