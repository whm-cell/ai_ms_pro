#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from harness_config import HarnessConfigError, load_harness_config


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "ai" / "prototypes" / "prototype-slice"
PROTOTYPE_PAGE_PATH = ROOT / "app" / "prototype" / "page.tsx"
PROTOTYPE_ROUTE = "/prototype"

REQUIRED_ARTIFACTS = (
    "provenance.md",
    "normalized-prd.md",
    "surface-identity.md",
    "page-map.md",
    "state-matrix.md",
    "constraints.md",
    "artifact-review.md",
)

FORBIDDEN_TOOL_LOCKS = (
    "Open Design",
    "/Volumes/usd/codes/skills",
    "Figma",
)


@dataclass(frozen=True)
class PrototypeArtifactReport:
    artifact_dir: str
    completeness_passed: int
    completeness_total: int
    completeness_rate: float
    errors: list[str]
    warnings: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Prototype Design Brief artifact review package.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--artifact-dir", help="Prototype artifact directory to check.")
    parser.add_argument("--page-path", help="Prototype page source path to check.")
    parser.add_argument(
        "--fixture-path",
        action="append",
        default=None,
        help="Additional prototype fixture/source path to check. Can be repeated.",
    )
    parser.add_argument("--prototype-route", help="Prototype route that must appear in artifacts.")
    parser.add_argument(
        "--required-state",
        action="append",
        default=None,
        help="Required state token that must appear in artifacts. Can be repeated.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Run the configured/default artifact review even when the feature is disabled.",
    )
    return parser.parse_args()


def relative(path: Path, root: Path = ROOT) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def read_if_exists(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def repo_path(root: Path, entry: str | None, default: Path) -> Path:
    if not entry:
        return default
    path = Path(entry)
    return path if path.is_absolute() else root / path


def required_gates(prototype_route: str) -> tuple[tuple[str, re.Pattern[str]], ...]:
    return (
        ("bound_source_truth", re.compile(r"REQ-\d+.*WS-\d+|WS-\d+.*REQ-\d+", re.S)),
        ("prototype_route", re.compile(re.escape(prototype_route))),
        ("canonical_truth_boundary", re.compile(r"does not replace canonical|不替代|不取代", re.I)),
        ("surface_identity", re.compile(r"surface identity|surface|界面|页面", re.I)),
        ("critical_states", re.compile(r"state matrix|critical state|状态矩阵|关键状态", re.I)),
        ("non_production_boundary", re.compile(r"No production API|prototype only|静态原型|不新增生产", re.I)),
        ("review_result", re.compile(r"Review result:\s*(pass|partial pass|fail)", re.I)),
    )


def configured_targets(args: argparse.Namespace) -> tuple[dict[str, object], bool]:
    config = load_harness_config(ROOT).prototype_design_brief
    explicit = any(
        (
            args.artifact_dir,
            args.page_path,
            args.fixture_path,
            args.prototype_route,
            args.required_state,
        )
    )
    if not config.artifact_review_enabled and not explicit and not args.force:
        return {"artifact_dir": config.artifact_dir}, True
    return {
        "artifact_dir": args.artifact_dir or config.artifact_dir or None,
        "page_path": args.page_path or config.prototype_page_path or None,
        "fixture_paths": tuple(args.fixture_path) if args.fixture_path is not None else config.fixture_paths or None,
        "prototype_route": args.prototype_route or config.prototype_route or None,
        "required_states": tuple(args.required_state)
        if args.required_state is not None
        else config.required_states or None,
    }, False


def build_report(
    root: Path = ROOT,
    *,
    artifact_dir: str | None = None,
    page_path: str | None = None,
    fixture_paths: tuple[str, ...] | None = None,
    prototype_route: str | None = None,
    required_states: tuple[str, ...] | None = None,
) -> PrototypeArtifactReport:
    artifact_dir_path = repo_path(root, artifact_dir, root / ARTIFACT_DIR.relative_to(ROOT))
    page_path_obj = repo_path(root, page_path, root / PROTOTYPE_PAGE_PATH.relative_to(ROOT))
    fixture_path_objs = [repo_path(root, path, root / path) for path in fixture_paths or ()]
    route = prototype_route or PROTOTYPE_ROUTE
    states = required_states or ()
    code_paths = [(page_path_obj, "prototype page")]
    code_paths.extend((path, f"prototype fixture {index}") for index, path in enumerate(fixture_path_objs, 1))
    total = len(REQUIRED_ARTIFACTS) + len(states) + len(required_gates(route)) + len(code_paths)
    passed = 0
    errors: list[str] = []
    warnings: list[str] = []
    combined_parts: list[str] = []

    for name in REQUIRED_ARTIFACTS:
        path = artifact_dir_path / name
        if path.exists():
            passed += 1
            combined_parts.append(read_if_exists(path))
        else:
            errors.append(f"missing prototype artifact: {relative(path, root)}")
    for path, label in code_paths:
        if path.exists():
            passed += 1
            combined_parts.append(read_if_exists(path))
        else:
            errors.append(f"missing {label}: {relative(path, root)}")

    combined = "\n".join(combined_parts)
    for state in states:
        if state in combined:
            passed += 1
        else:
            errors.append(f"missing required prototype state: {state}")
    for name, pattern in required_gates(route):
        if pattern.search(combined):
            passed += 1
        else:
            errors.append(f"missing prototype artifact gate: {name}")
    if any(token in combined for token in FORBIDDEN_TOOL_LOCKS):
        errors.append("prototype artifacts must remain tool-agnostic")
    if "Review result: pending implementation" in combined:
        warnings.append("artifact review still marked pending implementation")

    return PrototypeArtifactReport(
        artifact_dir=relative(artifact_dir_path, root),
        completeness_passed=passed,
        completeness_total=total,
        completeness_rate=passed / total if total else 1.0,
        errors=errors,
        warnings=warnings,
    )


def emit_report(report: PrototypeArtifactReport, *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2, sort_keys=True))
        return
    status = "FAILED" if report.errors else "OK"
    print(f"Prototype artifact review check: {status}")
    print(f"Completeness: {report.completeness_passed}/{report.completeness_total} ({report.completeness_rate:.1%})")
    for warning in report.warnings:
        print(f"WARN: {warning}")
    for error in report.errors:
        print(f"ERROR: {error}")


def main() -> int:
    args = parse_args()
    try:
        targets, skipped = configured_targets(args)
    except HarnessConfigError as exc:
        print(f"ERROR: {exc}")
        return 1
    if skipped:
        payload = {**targets, "skipped": True, "reason": "prototype_design_brief.artifact_review_enabled is false"}
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print("Prototype artifact review check: SKIPPED")
            print("Reason: prototype_design_brief.artifact_review_enabled is false")
        return 0
    report = build_report(**targets)
    emit_report(report, as_json=args.json)
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
