#!/usr/bin/env python3

from __future__ import annotations

import argparse
import ast
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
HOOKS_DIR = ROOT / ".codex" / "hooks"

sys.path.insert(0, str(HOOKS_DIR))
sys.path.insert(0, str(ROOT / "scripts"))

import check_loop_scope_monitor_samples as loop_samples  # noqa: E402
import check_pre_tool_use_preflight_samples as preflight_samples  # noqa: E402
import pre_tool_use_preflight as preflight_hook  # noqa: E402
import stop_loop_scope_monitor as loop_hook  # noqa: E402


NONE_CODE = "none"
PREFLIGHT_HOOK = HOOKS_DIR / "pre_tool_use_preflight.py"
LOOP_HOOK = HOOKS_DIR / "stop_loop_scope_monitor.py"


@dataclass(frozen=True)
class AlignmentReport:
    preflight_hook_codes: tuple[str, ...]
    preflight_emitted_codes: tuple[str, ...]
    preflight_checker_codes: tuple[str, ...]
    loop_hook_codes: tuple[str, ...]
    loop_emitted_codes: tuple[str, ...]
    loop_checker_codes: tuple[str, ...]
    loop_recommendations: tuple[str, ...]
    loop_checker_recommendations: tuple[str, ...]
    errors: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check hook warning codes against burn-in sample checker enums.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def sorted_tuple(values: set[str] | tuple[str, ...] | list[str]) -> tuple[str, ...]:
    return tuple(sorted(values))


def exported_codes(module: object, attribute: str) -> set[str]:
    value = getattr(module, attribute, ())
    if not isinstance(value, tuple):
        return set()
    return {item for item in value if isinstance(item, str) and item}


def checker_codes(values: set[str]) -> set[str]:
    return set(values) - {NONE_CODE}


def literal_codes(path: Path, call_name: str) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    codes: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or node_name(node.func) != call_name:
            continue
        if not node.args or not isinstance(node.args[0], ast.Constant):
            continue
        if isinstance(node.args[0].value, str):
            codes.add(node.args[0].value)
    return codes


def node_name(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def compare_exact(errors: list[str], label: str, left: set[str], right: set[str], right_label: str) -> None:
    missing = sorted(left - right)
    extra = sorted(right - left)
    if missing:
        errors.append(f"{label}: missing from {right_label}: {', '.join(missing)}")
    if extra:
        errors.append(f"{label}: stale in {right_label}: {', '.join(extra)}")


def require_markers(errors: list[str], path: Path, markers: tuple[str, ...]) -> None:
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(ROOT).as_posix()
    for marker in markers:
        if marker not in text:
            errors.append(f"{rel}: missing source marker {marker!r}")


def audit() -> AlignmentReport:
    errors: list[str] = []

    preflight_exported = exported_codes(preflight_hook, "PREFLIGHT_FINDING_CODES")
    preflight_emitted = literal_codes(PREFLIGHT_HOOK, "PreflightFinding")
    preflight_checker = checker_codes(preflight_samples.FINDING_CODES)
    compare_exact(errors, "preflight emitted finding codes", preflight_emitted, preflight_exported, "PREFLIGHT_FINDING_CODES")
    compare_exact(errors, "preflight checker finding codes", preflight_exported, preflight_checker, "FINDING_CODES")

    loop_exported = exported_codes(loop_hook, "LOOP_FINDING_CODES")
    loop_emitted = literal_codes(LOOP_HOOK, "LoopFinding")
    loop_checker = checker_codes(loop_samples.FINDING_CODES)
    compare_exact(errors, "loop emitted finding codes", loop_emitted, loop_exported, "LOOP_FINDING_CODES")
    compare_exact(errors, "loop checker finding codes", loop_exported, loop_checker, "FINDING_CODES")

    recommendation_map = getattr(loop_hook, "RECOMMENDATION_BY_FINDING", {})
    if not isinstance(recommendation_map, dict):
        errors.append("loop recommendation mapping: RECOMMENDATION_BY_FINDING must be a dict")
        recommendation_map = {}
    recommendation_keys = {key for key in recommendation_map if isinstance(key, str)}
    compare_exact(errors, "loop recommendation mapping keys", loop_exported, recommendation_keys, "RECOMMENDATION_BY_FINDING")
    recommendations = {value for value in recommendation_map.values() if isinstance(value, str)}
    checker_recommendations = checker_codes(loop_samples.RECOMMENDATIONS)
    invalid_recommendations = sorted(recommendations - checker_recommendations)
    if invalid_recommendations:
        errors.append(f"loop recommendation mapping values: not accepted by sample checker: {', '.join(invalid_recommendations)}")

    require_markers(
        errors,
        PREFLIGHT_HOOK,
        ("Finding codes:", "Sample capture:", "check_harness_placeholder_replacement.py <candidate-jsonl>"),
    )
    require_markers(
        errors,
        LOOP_HOOK,
        (
            "Finding codes:",
            "Recommended sample actions:",
            "Sample capture:",
            "check_harness_placeholder_replacement.py <candidate-jsonl>",
        ),
    )

    return AlignmentReport(
        sorted_tuple(preflight_exported),
        sorted_tuple(preflight_emitted),
        sorted_tuple(preflight_checker),
        sorted_tuple(loop_exported),
        sorted_tuple(loop_emitted),
        sorted_tuple(loop_checker),
        sorted_tuple(recommendations),
        sorted_tuple(checker_recommendations),
        tuple(errors),
    )


def emit_text(report: AlignmentReport) -> None:
    print("Warning sample code alignment:")
    print(f"- preflight hook codes: {', '.join(report.preflight_hook_codes)}")
    print(f"- preflight emitted codes: {', '.join(report.preflight_emitted_codes)}")
    print(f"- preflight checker codes: {', '.join(report.preflight_checker_codes)}")
    print(f"- loop hook codes: {', '.join(report.loop_hook_codes)}")
    print(f"- loop emitted codes: {', '.join(report.loop_emitted_codes)}")
    print(f"- loop checker codes: {', '.join(report.loop_checker_codes)}")
    print(f"- loop recommendation codes: {', '.join(report.loop_recommendations)}")
    if report.ok:
        print("ERRORS: none")
        return
    print("ERRORS:")
    for error in report.errors:
        print(f"- {error}")


def main() -> int:
    args = parse_args()
    report = audit()
    if args.json:
        payload = asdict(report) | {"ok": report.ok}
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        emit_text(report)
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
