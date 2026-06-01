#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shlex
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = ROOT / "docs" / "ai" / "evals" / "task-outcome-evals.jsonl"
ALLOWED_GROUPS = {"simple-fix", "cross-file", "docs-sync", "risk-judgment", "tool-selection"}
ALLOWED_RESUME = {"not-applicable", "required"}
ALLOWED_GUARDRAIL = {"not-expected", "review-required", "confirmation-gated"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate task outcome eval dataset shape.")
    parser.add_argument("--dataset", default=str(DEFAULT_DATASET), help=f"Dataset path. Default: {DEFAULT_DATASET}")
    return parser.parse_args()


def load_items(path: Path, errors: list[str]) -> list[tuple[int, dict[str, Any]]]:
    items: list[tuple[int, dict[str, Any]]] = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            item = json.loads(raw)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}:{line_no}: invalid JSON: {exc}")
            continue
        if not isinstance(item, dict):
            errors.append(f"{path}:{line_no}: record must be an object")
            continue
        items.append((line_no, item))
    if not items:
        errors.append(f"{path}: dataset must contain at least one record")
    return items


def validate_item(line_no: int, item: dict[str, Any], errors: list[str]) -> None:
    prefix = f"{DEFAULT_DATASET}:{line_no}"
    for field in ("id", "title", "benchmark_group", "task_prompt", "notes"):
        if not isinstance(item.get(field), str) or not str(item[field]).strip():
            errors.append(f"{prefix}: {field} must be a non-empty string")
    if item.get("benchmark_group") not in ALLOWED_GROUPS:
        errors.append(f"{prefix}: benchmark_group must be one of {sorted(ALLOWED_GROUPS)}")
    string_list(item.get("expected_artifacts"), f"{prefix}: expected_artifacts", errors)
    checks = item.get("expected_checks")
    if not isinstance(checks, list) or not checks:
        errors.append(f"{prefix}: expected_checks must be a non-empty list")
    else:
        for index, check in enumerate(checks):
            if not isinstance(check, dict):
                errors.append(f"{prefix}: expected_checks[{index}] must be an object")
                continue
            for field in ("command", "expected_outcome", "rationale"):
                if not isinstance(check.get(field), str) or not str(check[field]).strip():
                    errors.append(f"{prefix}: expected_checks[{index}].{field} must be a non-empty string")
            command = check.get("command")
            if isinstance(command, str):
                validate_command(command, f"{prefix}: expected_checks[{index}].command", errors)
    scorecard = item.get("scorecard")
    if not isinstance(scorecard, dict):
        errors.append(f"{prefix}: scorecard must be an object")
    else:
        if scorecard.get("resume_stability") not in ALLOWED_RESUME:
            errors.append(f"{prefix}: scorecard.resume_stability must be one of {sorted(ALLOWED_RESUME)}")
        if scorecard.get("guardrail_posture") not in ALLOWED_GUARDRAIL:
            errors.append(f"{prefix}: scorecard.guardrail_posture must be one of {sorted(ALLOWED_GUARDRAIL)}")
        if not isinstance(scorecard.get("overreach_must_stay_bounded"), bool):
            errors.append(f"{prefix}: scorecard.overreach_must_stay_bounded must be a boolean")
    tags = item.get("risk_tags")
    if not isinstance(tags, list) or not tags or not all(isinstance(tag, str) and tag.strip() for tag in tags):
        errors.append(f"{prefix}: risk_tags must be a non-empty list of strings")


def string_list(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append(f"{label} must be a non-empty list")
        return
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{label}[{index}] must be a non-empty string")


def validate_command(command: str, prefix: str, errors: list[str]) -> None:
    try:
        parts = shlex.split(command)
    except ValueError as exc:
        errors.append(f"{prefix}: command is not shell-parseable: {exc}")
        return
    for part in parts:
        if part.startswith(("scripts/", "tests/", ".codex/")) and not (ROOT / part).exists():
            errors.append(f"{prefix}: command references missing path {part}")


def main() -> int:
    args = parse_args()
    path = Path(args.dataset).expanduser()
    errors: list[str] = []
    try:
        items = load_items(path, errors)
    except FileNotFoundError:
        print(f"task outcome eval dataset check failed: dataset not found: {path}", file=sys.stderr)
        return 1
    for line_no, item in items:
        validate_item(line_no, item, errors)
    if errors:
        print("task outcome eval dataset check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("task outcome eval dataset check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
