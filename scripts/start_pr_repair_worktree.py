#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REMOTE = "origin"


@dataclass(frozen=True)
class PrInfo:
    number: int
    url: str
    head_ref_name: str
    base_ref_name: str
    head_repo: str


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or reuse a detached sibling worktree for fixing an open PR.",
    )
    parser.add_argument("pr", help="PR number or URL.")
    parser.add_argument("--dir", dest="target_dir", help="Worktree directory. Defaults to ../<repo>-pr<PR>.")
    parser.add_argument("--repo", help="GitHub repository in owner/name form. Defaults to gh repo view.")
    parser.add_argument("--remote", default=DEFAULT_REMOTE, help="Git remote to fetch/push. Defaults to origin.")
    parser.add_argument("--dry-run", action="store_true", help="Print the plan without creating a worktree.")
    return parser.parse_args(argv)


def run(args: list[str], cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)


def run_checked(args: list[str], cwd: Path = ROOT) -> str:
    result = run(args, cwd=cwd)
    if result.returncode != 0:
        output = (result.stderr or result.stdout).strip()
        raise RuntimeError(f"{' '.join(args)} failed{f': {output}' if output else ''}")
    return result.stdout.strip()


def resolve_repo(explicit_repo: str | None) -> str:
    if explicit_repo:
        return explicit_repo
    raw = run_checked(["gh", "repo", "view", "--json", "nameWithOwner"])
    repo = json.loads(raw).get("nameWithOwner")
    if not repo:
        raise RuntimeError("Unable to resolve repository from gh repo view.")
    return str(repo)


def pr_token(value: str) -> str:
    match = re.search(r"/pull/(\d+)(?:\D|$)", value)
    return match.group(1) if match else value


def resolve_pr(pr: str, repo: str) -> PrInfo:
    raw = run_checked(
        [
            "gh",
            "pr",
            "view",
            pr_token(pr),
            "--repo",
            repo,
            "--json",
            "number,url,headRefName,baseRefName,headRepository",
        ]
    )
    data = json.loads(raw)
    head_repo_data = data.get("headRepository") if isinstance(data.get("headRepository"), dict) else {}
    head_repo = str(head_repo_data.get("nameWithOwner") or repo)
    return PrInfo(
        number=int(data["number"]),
        url=str(data["url"]),
        head_ref_name=str(data["headRefName"]),
        base_ref_name=str(data.get("baseRefName") or ""),
        head_repo=head_repo,
    )


def default_target_dir(pr_number: int, root: Path = ROOT) -> Path:
    repo_dir_name = re.sub(r"-pr\d+$", "", root.name)
    return root.parent / f"{repo_dir_name}-pr{pr_number}"


def print_plan(pr_info: PrInfo, repo: str, remote: str, target_dir: Path) -> None:
    print(f"PR: {pr_info.url}")
    print(f"Repo: {repo}")
    print(f"Head branch: {pr_info.head_ref_name}")
    print(f"Base branch: {pr_info.base_ref_name}")
    print(f"Target worktree: {target_dir}")
    if pr_info.head_repo != repo:
        print("")
        print(f"WARNING: PR head repository is {pr_info.head_repo}; verify push access before committing fixes.")
    print("")
    print("After fixing and committing inside the repair worktree, push with:")
    print(f"  git push {remote} HEAD:{pr_info.head_ref_name}")


def ensure_existing_worktree(target_dir: Path) -> bool:
    if not target_dir.exists():
        return False
    result = run(["git", "-C", str(target_dir), "rev-parse", "--git-dir"])
    if result.returncode != 0:
        raise RuntimeError(f"Target exists but is not a git worktree: {target_dir}")
    print(f"Target worktree already exists: {target_dir}")
    status = run_checked(["git", "-C", str(target_dir), "status", "--short", "--branch"])
    print(status)
    return True


def create_worktree(pr_info: PrInfo, remote: str, target_dir: Path) -> None:
    remote_ref = f"refs/remotes/{remote}/{pr_info.head_ref_name}"
    run_checked(["git", "fetch", remote, f"{pr_info.head_ref_name}:{remote_ref}"])
    run_checked(["git", "worktree", "add", "--detach", str(target_dir), remote_ref])
    print("")
    print("Created repair worktree.")
    status = run_checked(["git", "-C", str(target_dir), "status", "--short", "--branch"])
    print(status)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        repo = resolve_repo(args.repo)
        pr_info = resolve_pr(args.pr, repo)
        target_dir = Path(args.target_dir).resolve() if args.target_dir else default_target_dir(pr_info.number).resolve()
        print_plan(pr_info, repo, args.remote, target_dir)
        if args.dry_run:
            return 0
        if ensure_existing_worktree(target_dir):
            return 0
        create_worktree(pr_info, args.remote, target_dir)
    except RuntimeError as exc:
        print(f"PR repair worktree setup failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
