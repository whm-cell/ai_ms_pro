#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
HIGH_RISK_PATTERNS = (
    "AGENTS.md",
    ".agents/skills/**",
    ".codex/hooks.json",
    ".codex/harness.toml",
    ".github/workflows/**",
    ".github/CODEOWNERS",
    ".github/pull_request_template.md",
    ".github/PULL_REQUEST_TEMPLATE/**",
    ".github/dependabot.yml",
    "scripts/check_*.py",
    "scripts/sync_hooks_config.py",
    "scripts/bootstrap_harness.py",
    "docs/requirements/traceability-matrix.md",
    "docs/requirements/source/**",
    "docs/requirements/normalized/**",
    "docs/requirements/workstreams/**",
    "docs/ai/status/**",
    "docs/ai/adr/**",
)

@dataclass(frozen=True)
class PullRequest:
    number: int
    title: str
    url: str
    head_ref: str
    base_ref: str
    files: tuple[str, ...]

@dataclass(frozen=True)
class Conflict:
    pr_number: int
    title: str
    url: str
    overlap: tuple[str, ...]
    high_risk_overlap: tuple[str, ...]

@dataclass(frozen=True)
class Report:
    status: str
    current_pr: int | None
    base_ref: str
    current_files: tuple[str, ...]
    current_high_risk_files: tuple[str, ...]
    conflicts: tuple[Conflict, ...]
    unknowns: tuple[str, ...]

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check current PR changed files against open PRs.")
    parser.add_argument("--current-pr", type=int, help="Current pull request number.")
    parser.add_argument("--base", help="Base branch. Defaults to PR base or main.")
    parser.add_argument("--repo", help="GitHub repository in owner/name form.")
    parser.add_argument("--current-files-file", help="JSON fixture for current files.")
    parser.add_argument("--open-prs-file", help="JSON fixture for open PRs with files.")
    parser.add_argument("--strict-high-risk", action="store_true", help="Fail on high-risk overlap.")
    parser.add_argument("--strict-any-overlap", action="store_true", help="Fail on any overlap.")
    parser.add_argument("--strict-unknown", action="store_true", help="Fail when GitHub state is unknown.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()

def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True, check=False)

def command_text(result: subprocess.CompletedProcess[str]) -> str:
    return (result.stderr or result.stdout).strip().replace("\n", " ")

def normalize_files(items: Any) -> tuple[str, ...]:
    files: list[str] = []
    if not isinstance(items, list):
        return ()
    for item in items:
        if isinstance(item, str):
            files.append(item)
        elif isinstance(item, dict) and item.get("path"):
            files.append(str(item["path"]))
    return tuple(sorted(set(files)))

def high_risk_files(files: tuple[str, ...]) -> tuple[str, ...]:
    risky = [
        path
        for path in files
        if any(fnmatch.fnmatchcase(path, pattern) for pattern in HIGH_RISK_PATTERNS)
    ]
    return tuple(sorted(risky))

def load_json(path: str) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))

def repo_from_origin() -> str | None:
    result = run(["git", "remote", "get-url", "origin"])
    if result.returncode != 0:
        return None
    url = result.stdout.strip()
    if "github.com:" in url:
        suffix = url.split("github.com:", 1)[1]
    elif "github.com/" in url:
        suffix = url.split("github.com/", 1)[1]
    else:
        return None
    return suffix.removesuffix(".git")

def current_pr_from_event() -> int | None:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        return None
    try:
        payload = json.loads(Path(event_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    number = payload.get("pull_request", {}).get("number") or payload.get("number")
    return int(number) if number else None

def gh_json(args: list[str]) -> tuple[Any | None, str | None]:
    result = run(["gh", *args])
    if result.returncode != 0:
        return None, command_text(result) or "gh command failed"
    try:
        return json.loads(result.stdout), None
    except json.JSONDecodeError as exc:
        return None, f"invalid gh JSON: {exc}"

def pr_from_payload(payload: dict[str, Any]) -> PullRequest:
    return PullRequest(
        number=int(payload.get("number", 0)),
        title=str(payload.get("title", "")),
        url=str(payload.get("url", "")),
        head_ref=str(payload.get("headRefName", "")),
        base_ref=str(payload.get("baseRefName", "")),
        files=normalize_files(payload.get("files", [])),
    )

def load_current_pr(number: int, repo: str | None) -> tuple[PullRequest | None, str | None]:
    cmd = ["pr", "view", str(number), "--json", "number,title,url,headRefName,baseRefName,files"]
    if repo:
        cmd.extend(["--repo", repo])
    payload, error = gh_json(cmd)
    if not isinstance(payload, dict):
        return None, error or "current PR is unavailable"
    return pr_from_payload(payload), None

def local_changed_files(base: str) -> tuple[tuple[str, ...], str | None]:
    result = run(["git", "diff", "--name-only", "--diff-filter=ACMR", f"origin/{base}...HEAD"])
    if result.returncode != 0:
        return (), command_text(result) or "local diff failed"
    return tuple(sorted(line for line in result.stdout.splitlines() if line.strip())), None

def load_open_prs(base: str, repo: str | None) -> tuple[tuple[PullRequest, ...], str | None]:
    cmd = ["pr", "list", "--state", "open", "--base", base, "--json", "number,title,url,headRefName,baseRefName"]
    if repo:
        cmd.extend(["--repo", repo])
    payload, error = gh_json(cmd)
    if not isinstance(payload, list):
        return (), error or "open PR list is unavailable"
    prs: list[PullRequest] = []
    for item in payload:
        if not isinstance(item, dict) or not item.get("number"):
            continue
        pr, pr_error = load_current_pr(int(item["number"]), repo)
        if pr_error:
            return (), pr_error
        if pr:
            prs.append(pr)
    return tuple(prs), None

def fixture_prs(path: str) -> tuple[PullRequest, ...]:
    payload = load_json(path)
    prs = payload if isinstance(payload, list) else payload.get("pull_requests", [])
    return tuple(pr_from_payload(item) for item in prs if isinstance(item, dict))

def build_report(args: argparse.Namespace) -> Report:
    unknowns: list[str] = []
    repo = args.repo or repo_from_origin()
    current_pr_number = args.current_pr or current_pr_from_event()
    base_ref = args.base or "main"

    if args.current_files_file:
        current_files = normalize_files(load_json(args.current_files_file))
    elif current_pr_number:
        current_pr, error = load_current_pr(current_pr_number, repo)
        if error or not current_pr:
            unknowns.append(f"current PR files unavailable: {error}")
            current_files = ()
        else:
            base_ref = args.base or current_pr.base_ref or base_ref
            current_files = current_pr.files
    else:
        current_files, error = local_changed_files(base_ref)
        if error:
            unknowns.append(f"local changed files unavailable: {error}")

    if args.open_prs_file:
        open_prs = fixture_prs(args.open_prs_file)
    else:
        open_prs, error = load_open_prs(base_ref, repo)
        if error:
            unknowns.append(f"open PR files unavailable: {error}")

    conflicts = compare_prs(current_pr_number, current_files, open_prs)
    status = report_status(conflicts, unknowns)
    return Report(
        status=status,
        current_pr=current_pr_number,
        base_ref=base_ref,
        current_files=current_files,
        current_high_risk_files=high_risk_files(current_files),
        conflicts=conflicts,
        unknowns=tuple(unknowns),
    )

def compare_prs(
    current_pr: int | None,
    current_files: tuple[str, ...],
    open_prs: tuple[PullRequest, ...],
) -> tuple[Conflict, ...]:
    conflicts: list[Conflict] = []
    current_set = set(current_files)
    for pr in open_prs:
        if current_pr and pr.number == current_pr:
            continue
        overlap = tuple(sorted(current_set.intersection(pr.files)))
        if not overlap:
            continue
        conflicts.append(
            Conflict(
                pr_number=pr.number,
                title=pr.title,
                url=pr.url,
                overlap=overlap,
                high_risk_overlap=high_risk_files(overlap),
            )
        )
    return tuple(conflicts)

def report_status(conflicts: tuple[Conflict, ...], unknowns: list[str]) -> str:
    if any(conflict.high_risk_overlap for conflict in conflicts):
        return "BLOCK"
    if conflicts:
        return "WARN"
    if unknowns:
        return "UNKNOWN"
    return "OK"

def emit_text(report: Report) -> None:
    print("PR touch conflict check:")
    print(f"- status: {report.status}")
    print(f"- current_pr: {report.current_pr or '-'}")
    print(f"- base_ref: {report.base_ref}")
    print(f"- current_files: {len(report.current_files)}")
    print(f"- current_high_risk_files: {len(report.current_high_risk_files)}")
    for path in report.current_high_risk_files:
        print(f"  HIGH_RISK: {path}")
    for conflict in report.conflicts:
        print(f"- overlap with PR #{conflict.pr_number}: {conflict.title} {conflict.url}")
        for path in conflict.overlap:
            prefix = "HIGH_RISK_OVERLAP" if path in conflict.high_risk_overlap else "OVERLAP"
            print(f"  {prefix}: {path}")
    for unknown in report.unknowns:
        print(f"UNKNOWN: {unknown}")

def exit_code(report: Report, args: argparse.Namespace) -> int:
    if args.strict_unknown and report.unknowns:
        return 1
    if args.strict_high_risk and any(conflict.high_risk_overlap for conflict in report.conflicts):
        return 1
    if args.strict_any_overlap and report.conflicts:
        return 1
    return 0

def main() -> int:
    args = parse_args()
    report = build_report(args)
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        emit_text(report)
    return exit_code(report, args)

if __name__ == "__main__":
    sys.exit(main())
