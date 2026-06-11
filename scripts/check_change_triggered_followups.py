#!/usr/bin/env python3

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from change_triggered_followup_rules import RULES

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Followup:
    name: str
    level: str
    ci_coverage: str
    matched_files: tuple[str, ...]
    commands: tuple[str, ...]
    references: tuple[str, ...]
    reason: str
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Suggest follow-up checks from changed files without expanding AGENTS.md.")
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
        patterns = tuple(str(pattern) for pattern in rule["patterns"])
        matched = tuple(path for path in files if any(matches(pattern, path) for pattern in patterns))
        if matched:
            followups.append(
                Followup(
                    name=str(rule["name"]),
                    level=str(rule["level"]),
                    ci_coverage=str(rule["ci_coverage"]),
                    matched_files=matched,
                    commands=tuple(str(command) for command in rule["commands"]),
                    references=tuple(str(reference) for reference in rule["references"]),
                    reason=str(rule["reason"]),
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
        print(f"  level: {item.level}")
        print(f"  ci coverage: {item.ci_coverage}")
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
        lines.extend(
            [
                "",
                "| Follow-up | Level | CI coverage | Reason | Matched files | Commands | References |",
                "| --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        lines.extend(
            f"| `{item.name}` | `{item.level}` | {item.ci_coverage} | {item.reason} | {markdown_list(item.matched_files)} | "
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
