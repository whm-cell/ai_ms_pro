#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from agent_eval_trace_expectations import (
    load_contract_names,
    validate_trace_expectations,
)


ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "docs" / "ai" / "evals" / "agent-harness-evals.jsonl"
CONTRACTS_PATH = ROOT / "docs" / "ai" / "tool-contracts" / "contracts.json"
ID_RE = re.compile(r"^EVAL-\d{3}-[a-z0-9]+(?:-[a-z0-9]+)*$")
TEST_MODULE_RE = re.compile(r"^tests\.test_[a-z0-9_]+$")
TEST_FILE_RE = re.compile(r"^tests/test_[a-z0-9_]+\.py$")

REQUIRED_FIELDS = (
    "id",
    "title",
    "category",
    "task_prompt",
    "expected_artifacts",
    "expected_checks",
    "grading_signals",
    "risk_tags",
    "notes",
)
ALLOWED_CATEGORIES = {
    "simple-code",
    "requirements-traceability",
    "high-impact-guardrail",
    "resume-runtime",
    "skill-harness",
}
ALLOWED_CHECK_OUTCOMES = {"pass", "warn", "review-required"}
ALLOWED_RISK_TAGS = {
    "simple-code",
    "requirements-traceability",
    "high-impact-action",
    "resume-handoff",
    "runtime-reduction",
    "governance-docs",
    "verification-harness",
    "user-confirmation",
    "source-boundary",
    "skill-catalog",
    "skill-broker",
    "context-budget",
    "mixed-stack",
    "docs-impact",
}

@dataclass(frozen=True)
class EvalDatasetReport:
    dataset_path: str
    item_count: int
    errors: list[str]
    warnings: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check the agent harness eval JSONL dataset.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--dataset", default=str(DATASET_PATH), help="Dataset JSONL path.")
    return parser.parse_args()


def relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def load_items(path: Path, errors: list[str]) -> list[tuple[int, dict[str, object]]]:
    if not path.exists():
        errors.append(f"dataset missing: {relative(path)}")
        return []
    items: list[tuple[int, dict[str, object]]] = []
    for line_no, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw_line.strip():
            errors.append(f"blank line is not allowed: line {line_no}")
            continue
        try:
            item = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON on line {line_no}: {exc.msg}")
            continue
        if isinstance(item, dict):
            items.append((line_no, item))
        else:
            errors.append(f"line {line_no} must be a JSON object")
    return items


def has_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def has_text_list(value: object) -> bool:
    return isinstance(value, list) and bool(value) and all(has_text(item) for item in value)


def command_path_exists(command: str) -> bool:
    parts = command.split()
    if len(parts) >= 2 and parts[0] == ".codex/hooks/run_with_repo_python.sh":
        return (ROOT / parts[1]).exists()
    if len(parts) >= 2 and is_python_command(parts[0]):
        if parts[1].startswith("scripts/"):
            return (ROOT / parts[1]).exists()
        if unittest_target_exists(parts[1]):
            return True
    if len(parts) >= 4 and is_python_command(parts[0]) and parts[1:3] == ["-m", "unittest"]:
        return unittest_target_exists(parts[3])
    return False


def is_python_command(value: str) -> bool:
    return value == "python3" or value.endswith("/python") or value.endswith("/python3")


def unittest_target_exists(target: str) -> bool:
    if TEST_MODULE_RE.match(target):
        return (ROOT / (target.replace(".", "/") + ".py")).exists()
    if TEST_FILE_RE.match(target):
        return (ROOT / target).exists()
    return False


def validate_expected_checks(line_no: int, value: object, errors: list[str]) -> None:
    if not isinstance(value, list) or not value:
        errors.append(f"line {line_no}: expected_checks must be a non-empty list")
        return
    for index, check in enumerate(value, 1):
        prefix = f"line {line_no} check {index}"
        if not isinstance(check, dict):
            errors.append(f"{prefix}: expected check must be an object")
            continue
        command = check.get("command")
        outcome = check.get("expected_outcome")
        rationale = check.get("rationale")
        if not has_text(command):
            errors.append(f"{prefix}: command must be non-empty text")
        elif not command_path_exists(str(command)):
            errors.append(f"{prefix}: command is not a plausible repo command: {command}")
        if outcome not in ALLOWED_CHECK_OUTCOMES:
            errors.append(f"{prefix}: expected_outcome must be one of {sorted(ALLOWED_CHECK_OUTCOMES)}")
        if not has_text(rationale):
            errors.append(f"{prefix}: rationale must be non-empty text")


def validate_grading_signals(line_no: int, value: object, errors: list[str]) -> None:
    if not isinstance(value, dict):
        errors.append(f"line {line_no}: grading_signals must be an object")
        return
    for key in ("pass", "warn", "fail"):
        if not has_text_list(value.get(key)):
            errors.append(f"line {line_no}: grading_signals.{key} must be a non-empty text list")


def validate_item(
    line_no: int,
    item: dict[str, object],
    seen_ids: set[str],
    contract_names: set[str],
    errors: list[str],
) -> None:
    missing = [field for field in REQUIRED_FIELDS if field not in item]
    if missing:
        errors.append(f"line {line_no}: missing required fields: {', '.join(missing)}")
        return
    identifier = item["id"]
    if not has_text(identifier) or not ID_RE.match(str(identifier)):
        errors.append(f"line {line_no}: id must match {ID_RE.pattern}")
    elif str(identifier) in seen_ids:
        errors.append(f"line {line_no}: duplicate id: {identifier}")
    else:
        seen_ids.add(str(identifier))
    if item["category"] not in ALLOWED_CATEGORIES:
        errors.append(f"line {line_no}: unsupported category: {item['category']}")
    for field in ("title", "task_prompt", "notes"):
        if not has_text(item[field]):
            errors.append(f"line {line_no}: {field} must be non-empty text")
    if not has_text_list(item["expected_artifacts"]):
        errors.append(f"line {line_no}: expected_artifacts must be a non-empty text list")
    validate_expected_checks(line_no, item["expected_checks"], errors)
    validate_grading_signals(line_no, item["grading_signals"], errors)
    validate_risk_tags(line_no, item["risk_tags"], errors)
    if "trace_expectations" in item:
        validate_trace_expectations(
            line_no,
            item["trace_expectations"],
            contract_names,
            errors,
            has_text,
            has_text_list,
        )


def validate_risk_tags(line_no: int, value: object, errors: list[str]) -> None:
    if not has_text_list(value):
        errors.append(f"line {line_no}: risk_tags must be a non-empty text list")
        return
    unknown = sorted({str(tag) for tag in value if tag not in ALLOWED_RISK_TAGS})
    if unknown:
        errors.append(f"line {line_no}: unknown risk tags: {', '.join(unknown)}")


def build_report(dataset_path: Path = DATASET_PATH) -> EvalDatasetReport:
    errors: list[str] = []
    warnings: list[str] = []
    contract_names = load_contract_names(CONTRACTS_PATH, errors, relative, has_text)
    items = load_items(dataset_path, errors)
    seen_ids: set[str] = set()
    categories: set[str] = set()
    for line_no, item in items:
        category = item.get("category")
        if isinstance(category, str):
            categories.add(category)
        validate_item(line_no, item, seen_ids, contract_names, errors)
    missing_categories = sorted(ALLOWED_CATEGORIES - categories)
    for category in missing_categories:
        warnings.append(f"dataset has no case for category: {category}")
    return EvalDatasetReport(
        dataset_path=relative(dataset_path),
        item_count=len(items),
        errors=errors,
        warnings=warnings,
    )


def emit_text(report: EvalDatasetReport) -> None:
    print("Agent harness eval dataset check:")
    print(f"- dataset: {report.dataset_path}")
    print(f"- items: {report.item_count}")
    for warning in report.warnings:
        print(f"WARN: {warning}")
    for error in report.errors:
        print(f"ERROR: {error}")


def main() -> int:
    args = parse_args()
    report = build_report(Path(args.dataset))
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        emit_text(report)
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
