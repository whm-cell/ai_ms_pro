#!/usr/bin/env python3

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class FollowupRule:
    name: str
    patterns: tuple[str, ...]
    commands: tuple[str, ...]
    references: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class Followup:
    name: str
    matched_files: tuple[str, ...]
    commands: tuple[str, ...]
    references: tuple[str, ...]
    reason: str


RULES: tuple[FollowupRule, ...] = (
    FollowupRule(
        name="governance-surface",
        patterns=(
            "AGENTS.md",
            "docs/ai/**",
            "docs/requirements/**",
            ".codex/harness.toml",
        ),
        commands=(".codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py",),
        references=(".agents/skills/repo-governed-coding/references/governance-checklist.md",),
        reason="Shared governance truth changed.",
    ),
    FollowupRule(
        name="default-context-budget",
        patterns=(
            "AGENTS.md",
            "docs/ai/index.md",
            "docs/ai/working-context.md",
            "docs/ai/status/**",
            "docs/ai/adr/**",
            ".agents/skills/**",
        ),
        commands=(".codex/hooks/run_with_repo_python.sh scripts/check_context_budget.py",),
        references=(".agents/skills/harness-maintenance/references/verification-commands.md",),
        reason="Default context or skill surface changed.",
    ),
    FollowupRule(
        name="repo-local-skills",
        patterns=(".agents/skills/**",),
        commands=(".codex/hooks/run_with_repo_python.sh scripts/check_repo_skills.py",),
        references=("python3 /Users/coolm/.codex/skills/.system/skill-creator/scripts/quick_validate.py <changed-skill-dir>",),
        reason="Repo-local skill structure or discoverability may have changed.",
    ),
    FollowupRule(
        name="requirements-traceability",
        patterns=("docs/requirements/**",),
        commands=(".codex/hooks/run_with_repo_python.sh scripts/check_requirements_shape.py",),
        references=(".agents/skills/requirements-traceability-maintenance/",),
        reason="Requirement, workstream, matrix, or technical-assumption shape may have changed.",
    ),
    FollowupRule(
        name="candidate-skill-eval",
        patterns=(
            "docs/ai/skill-usage-samples.md",
            "docs/ai/skill-evals/**",
            ".agents/skills/progressive-feature-development/**",
            ".agents/skills/prd-to-project-skills/**",
        ),
        commands=(".codex/hooks/run_with_repo_python.sh scripts/check_skill_usage_samples.py",),
        references=("docs/ai/skill-evals/README.md",),
        reason="Candidate skill evidence or eval protocol changed.",
    ),
    FollowupRule(
        name="github-guardrails",
        patterns=(
            ".github/**",
            "scripts/check_github_guardrails.py",
            "scripts/check_pr_touch_conflicts.py",
        ),
        commands=(".codex/hooks/run_with_repo_python.sh scripts/check_github_guardrails.py",),
        references=(
            ".agents/skills/harness-maintenance/references/github-guardrails.md",
            ".agents/skills/team-pr-conflict-control/",
        ),
        reason="GitHub workflow, ownership, remote guardrail, or PR overlap surface changed.",
    ),
    FollowupRule(
        name="harness-code-shape",
        patterns=(
            "scripts/*.py",
            ".codex/hooks/*.py",
            ".codex/hooks/**/*.py",
            "tests/*.py",
        ),
        commands=(".codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --staged",),
        references=(".agents/skills/harness-maintenance/references/code-shape-budget.md",),
        reason="Harness Python or test code changed.",
    ),
    FollowupRule(
        name="handoff-compression",
        patterns=(
            "docs/ai/handoffs/active/**",
            "docs/ai/status/**",
            "docs/ai/working-context.md",
        ),
        commands=(".codex/hooks/run_with_repo_python.sh scripts/check_archive_candidates.py",),
        references=(".agents/skills/harness-maintenance/references/runtime-governance-compression.md",),
        reason="Active recovery surface changed; archive candidates may need review.",
    ),
    FollowupRule(
        name="starter-sync",
        patterns=("new_pro_standard/**",),
        commands=(
            "cd new_pro_standard && python3 -m unittest discover -s tests",
            "cd new_pro_standard && python3 scripts/check_ai_governance.py",
            "cd new_pro_standard && python3 scripts/check_context_budget.py",
            "cd new_pro_standard && python3 scripts/check_repo_skills.py",
        ),
        references=("new_pro_standard/docs/ai/harness-portability-guide.md",),
        reason="Starter mechanism layer changed; validate the starter from its own root.",
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Suggest follow-up checks from changed files without expanding AGENTS.md.",
    )
    parser.add_argument("--root", default=str(ROOT), help="Repository root to inspect.")
    parser.add_argument("--files", nargs="*", help="Explicit changed-file list, useful for tests.")
    parser.add_argument("--staged", action="store_true", help="Inspect staged changes only.")
    parser.add_argument("--base", help="Inspect changes against a git base, for example origin/main.")
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    output.add_argument("--markdown", action="store_true", help="Emit GitHub Actions summary markdown.")
    parser.add_argument("--strict", action="store_true", help="Exit 1 when any follow-up is suggested.")
    return parser.parse_args()


def run_git(root: Path, args: list[str]) -> list[str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git command failed")
    return [line.rstrip() for line in proc.stdout.splitlines() if line.strip()]


def parse_status_line(line: str) -> str | None:
    if len(line) < 4:
        return None
    path = line[3:]
    if " -> " in path:
        path = path.rsplit(" -> ", 1)[1]
    return path.strip().strip('"') or None


def changed_files(root: Path, args: argparse.Namespace) -> tuple[str, ...]:
    if args.files is not None:
        return tuple(sorted({normalize(path) for path in args.files if path}))
    if args.staged:
        files = run_git(root, ["diff", "--name-only", "--cached", "--diff-filter=ACMR"])
        return tuple(sorted({normalize(path) for path in files}))
    if args.base:
        files = run_git(root, ["diff", "--name-only", "--diff-filter=ACMR", f"{args.base}...HEAD"])
        return tuple(sorted({normalize(path) for path in files}))

    status_lines = run_git(root, ["status", "--short", "--untracked-files=all"])
    files = [path for line in status_lines if (path := parse_status_line(line))]
    return tuple(sorted({normalize(path) for path in files}))


def normalize(path: str) -> str:
    normalized = path.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def matches(pattern: str, path: str) -> bool:
    if pattern.endswith("/**"):
        return path == pattern[:-3].rstrip("/") or path.startswith(pattern[:-3])
    return fnmatch.fnmatch(path, pattern)


def build_followups(files: tuple[str, ...]) -> tuple[Followup, ...]:
    followups: list[Followup] = []
    for rule in RULES:
        matched = tuple(path for path in files if any(matches(pattern, path) for pattern in rule.patterns))
        if matched:
            followups.append(
                Followup(
                    name=rule.name,
                    matched_files=matched,
                    commands=rule.commands,
                    references=rule.references,
                    reason=rule.reason,
                )
            )
    return tuple(followups)


def emit_text(files: tuple[str, ...], followups: tuple[Followup, ...]) -> None:
    print("Change-triggered follow-up suggestions:")
    print(f"- Changed files: {len(files)}")
    if files:
        for path in files:
            print(f"  - {path}")
    if not followups:
        print("- No specialized follow-up checks suggested.")
        return

    print("\nSuggested follow-ups:")
    for item in followups:
        print(f"- {item.name}: {item.reason}")
        print(f"  matched: {', '.join(item.matched_files)}")
        print("  commands:")
        for command in item.commands:
            print(f"    - {command}")
        print("  references:")
        for reference in item.references:
            print(f"    - {reference}")

    print("\nThis checker is advisory. It suggests missing follow-up surfaces; it does not prove commands have already run.")


def markdown_list(values: tuple[str, ...]) -> str:
    return "<br>".join(f"`{value}`" for value in values)


def emit_markdown(files: tuple[str, ...], followups: tuple[Followup, ...]) -> None:
    lines = ["### Change-triggered follow-up suggestions", "", f"- Changed files: {len(files)}"]
    if files:
        lines.extend(["", "Changed files:", *(f"- `{path}`" for path in files)])
    if followups:
        lines.extend(["", "| Follow-up | Reason | Matched files | Commands | References |", "| --- | --- | --- | --- | --- |"])
        lines.extend(
            f"| `{item.name}` | {item.reason} | {markdown_list(item.matched_files)} | "
            f"{markdown_list(item.commands)} | {markdown_list(item.references)} |"
            for item in followups
        )
    else:
        lines.extend(["", "No specialized follow-up checks suggested."])
    lines.extend(["", "> Advisory only: this checker maps changed files to follow-up surfaces; it does not prove commands have already run."])
    print("\n".join(lines))


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    try:
        files = changed_files(root, args)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    followups = build_followups(files)
    if args.json:
        payload = {"changed_files": files, "followups": [asdict(item) for item in followups], "ok": not followups}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    elif args.markdown:
        emit_markdown(files, followups)
    else:
        emit_text(files, followups)
    return 1 if args.strict and followups else 0


if __name__ == "__main__":
    sys.exit(main())
