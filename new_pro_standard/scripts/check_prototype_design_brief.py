#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from harness_config import HarnessConfigError, load_harness_config


ROOT = Path(__file__).resolve().parents[1]
BRIEF_PATH = ROOT / "docs" / "ai" / "prototypes" / "prototype-design-brief.md"

REQ_RE = re.compile(r"REQ-\d+")
WS_RE = re.compile(r"WS-\d+")
ADR_RE = re.compile(r"ADR-\d+")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

REQUIRED_SECTION_GROUPS = (
    ("Project Metadata", ("Project Metadata",)),
    ("Source Truth", ("Source Truth",)),
    ("Product Scope", ("Product Scope",)),
    ("Target Surfaces", ("Target Surfaces",)),
    ("Page Map", ("Page Map",)),
    ("Critical States", ("Critical States",)),
    ("Boundary Rules", ("Boundary Rules", "Memory Boundary")),
    ("Non-Goals", ("Non-Goals",)),
    ("Prototype Handoff", ("Prototype Handoff",)),
    ("Review And Sync Rules", ("Review And Sync Rules",)),
)

SEMANTIC_GATES = (
    ("prototype_handoff", re.compile(r"prototype|原型|handoff", re.IGNORECASE)),
    ("canonical_truth_boundary", re.compile(r"does not replace canonical|不替代|不取代", re.IGNORECASE)),
    ("traceability_source", re.compile(r"traceability|追踪矩阵|需求追踪", re.IGNORECASE)),
    ("surface_identity", re.compile(r"surface|Surface|界面|页面")),
    ("critical_states", re.compile(r"critical state|状态|blocked|error|failure", re.IGNORECASE)),
    ("scope_or_permission_boundary", re.compile(r"scope|permission|权限|边界|范围", re.IGNORECASE)),
    ("failure_or_blocked_state", re.compile(r"fail-closed|blocked|error|失败|阻断", re.IGNORECASE)),
    ("artifact_review_sync", re.compile(r"artifact review|review result|审查|验收", re.IGNORECASE)),
)


@dataclass(frozen=True)
class PrototypeBriefReport:
    path: str
    completeness_passed: int
    completeness_total: int
    completeness_rate: float
    drift_findings: list[str]
    drift_checked: int
    drift_rate: float
    errors: list[str]
    warnings: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Prototype Design Brief completeness and drift.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--path", help="Brief path to check. Runs even when the feature is disabled.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Run the configured/default brief check even when the feature is disabled.",
    )
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def markdown_sections(text: str) -> set[str]:
    return {match.group(1).strip() for match in re.finditer(r"(?m)^##\s+(.+?)\s*$", text)}


def markdown_section_text(text: str, heading: str) -> str:
    pattern = re.compile(rf"(?ms)^##\s+{re.escape(heading)}\s*$\n(.*?)(?=^##\s+|\Z)")
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def all_ids(text: str, pattern: re.Pattern[str]) -> set[str]:
    return {match.group(0).upper() for match in pattern.finditer(text)}


def traceability_ids(root: Path) -> tuple[set[str], set[str]]:
    path = root / "docs" / "requirements" / "traceability-matrix.md"
    if not path.exists():
        return set(), set()
    text = read_text(path)
    return all_ids(text, REQ_RE), all_ids(text, WS_RE)


def adr_ids(root: Path) -> set[str]:
    directory = root / "docs" / "ai" / "adr"
    ids: set[str] = set()
    if not directory.exists():
        return ids
    for path in directory.glob("*.md"):
        ids.update(all_ids(path.name, ADR_RE))
        ids.update(all_ids(read_text(path), ADR_RE))
    return ids


def link_targets(text: str, base_dir: Path) -> list[tuple[str, Path]]:
    targets: list[tuple[str, Path]] = []
    for match in LINK_RE.finditer(text):
        target = match.group(1).strip()
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        target_without_anchor = target.split("#", 1)[0]
        if target_without_anchor:
            targets.append((target, (base_dir / target_without_anchor).resolve()))
    return targets


def completeness_errors(text: str) -> tuple[int, int, list[str]]:
    sections = markdown_sections(text)
    errors: list[str] = []
    passed = 0
    total = len(REQUIRED_SECTION_GROUPS) + len(SEMANTIC_GATES)
    for label, names in REQUIRED_SECTION_GROUPS:
        if any(name in sections for name in names):
            passed += 1
        else:
            errors.append(f"missing required section: {label}")
    for name, pattern in SEMANTIC_GATES:
        if pattern.search(text):
            passed += 1
        else:
            errors.append(f"missing semantic gate: {name}")
    return passed, total, errors


def drift_findings(text: str, brief: Path, root: Path) -> tuple[list[str], int]:
    matrix_reqs, matrix_ws = traceability_ids(root)
    known_adrs = adr_ids(root)
    findings: list[str] = []
    checked = 0
    for req_id in sorted(all_ids(text, REQ_RE)):
        checked += 1
        if req_id not in matrix_reqs:
            findings.append(f"{req_id} is not present in traceability matrix")
    for ws_id in sorted(all_ids(text, WS_RE)):
        checked += 1
        if ws_id not in matrix_ws:
            findings.append(f"{ws_id} is not present in traceability matrix")
    for adr_id in sorted(all_ids(text, ADR_RE)):
        checked += 1
        if adr_id not in known_adrs:
            findings.append(f"{adr_id} does not resolve to an ADR document")
    for target, resolved in link_targets(text, brief.parent):
        checked += 1
        if not resolved.exists():
            findings.append(f"link target missing: {target}")
    return findings, checked


def build_report(root: Path = ROOT, brief_path: Path | None = None) -> PrototypeBriefReport:
    brief = brief_path or BRIEF_PATH
    if not brief.exists():
        return PrototypeBriefReport(
            path=relative(brief, root),
            completeness_passed=0,
            completeness_total=len(REQUIRED_SECTION_GROUPS) + len(SEMANTIC_GATES),
            completeness_rate=0.0,
            drift_findings=[f"missing brief file: {relative(brief, root)}"],
            drift_checked=1,
            drift_rate=1.0,
            errors=[f"missing Prototype Design Brief: {relative(brief, root)}"],
            warnings=[],
        )

    text = read_text(brief)
    passed, total, errors = completeness_errors(text)
    source_truth = markdown_section_text(text, "Source Truth")
    if "未绑定" in source_truth:
        errors.append("Source Truth must not declare unbound requirement, workstream, or ADR inputs")

    findings, checked = drift_findings(text, brief, root)
    errors.extend(findings)
    drift_rate = (len(findings) / checked) if checked else 0.0
    return PrototypeBriefReport(
        path=relative(brief, root),
        completeness_passed=passed,
        completeness_total=total,
        completeness_rate=passed / total if total else 1.0,
        drift_findings=findings,
        drift_checked=checked,
        drift_rate=drift_rate,
        errors=errors,
        warnings=[],
    )


def configured_brief_path(args: argparse.Namespace) -> tuple[Path | None, bool, str]:
    config = load_harness_config(ROOT).prototype_design_brief
    if not config.enabled and not args.path and not args.force:
        return None, True, config.brief_path
    path = Path(args.path or config.brief_path or BRIEF_PATH)
    if not path.is_absolute():
        path = ROOT / path
    return path, False, config.brief_path


def emit_report(report: PrototypeBriefReport, *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2, sort_keys=True))
        return
    status = "FAILED" if report.errors else "OK"
    print(f"Prototype Design Brief check: {status}")
    print(f"Completeness: {report.completeness_passed}/{report.completeness_total} ({report.completeness_rate:.1%})")
    print(f"Drift rate: {len(report.drift_findings)}/{report.drift_checked} ({report.drift_rate:.1%})")
    for warning in report.warnings:
        print(f"WARN: {warning}")
    for error in report.errors:
        print(f"ERROR: {error}")


def main() -> int:
    args = parse_args()
    try:
        brief_path, skipped, configured_path = configured_brief_path(args)
    except HarnessConfigError as exc:
        print(f"ERROR: {exc}")
        return 1
    if skipped:
        payload = {"path": configured_path, "skipped": True, "reason": "prototype_design_brief.enabled is false"}
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print("Prototype Design Brief check: SKIPPED")
            print("Reason: prototype_design_brief.enabled is false")
        return 0
    report = build_report(brief_path=brief_path)
    emit_report(report, as_json=args.json)
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
