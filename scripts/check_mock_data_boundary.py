#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import posixpath
from pathlib import Path
import re

from mock_data_boundary_lib import (
    MockDataBoundaryConfig,
    MockDataBoundaryReport,
    MockDataFinding,
    is_fixture_path,
    iter_scan_files,
    load_config,
    matches_any,
    relative,
)
from mock_data_fixture_checks import scan_fixture_file
from mock_data_manifest import SUGGESTED_SCENARIO_PATHS, load_manifest_index, normalize_manifest_path


ROOT = Path(__file__).resolve().parents[1]
MOCKISH_RE = re.compile(r"(mock|fixture|fake|sample|dummy|seed|demo)", re.IGNORECASE)
ARRAY_ASSIGN_RE = re.compile(
    r"(?P<prefix>(?:export\s+)?(?:const|let|var)\s+)(?P<name>[A-Za-z_$][\w$]*)(?:\s*:\s*[^=]+)?\s*=\s*\[",
    re.MULTILINE,
)
ARRAY_FROM_RE = re.compile(
    r"(?:const|let|var)\s+(?P<name>[A-Za-z_$][\w$]*)(?:\s*:\s*[^=]+)?\s*=\s*Array\.from\(\s*\{\s*length\s*:\s*(?P<count>\d+)",
    re.MULTILINE,
)
IMPORT_RE = re.compile(
    r"\bfrom\s+['\"](?P<target>[^'\"]+)['\"]|require\(\s*['\"](?P<require>[^'\"]+)['\"]\s*\)|import\(\s*['\"](?P<dynamic>[^'\"]+)['\"]\s*\)"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check frontend mock data boundaries.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when review findings exist.")
    return parser.parse_args()


def build_report(root: Path = ROOT) -> MockDataBoundaryReport:
    root = root.resolve()
    errors: list[str] = []
    config = load_config(root, errors)
    if config is None or not config.enabled:
        return MockDataBoundaryReport(False, [], [], errors)

    manifest_paths, manifest_findings = load_manifest_index(root, config, errors)
    findings: list[MockDataFinding] = list(manifest_findings)
    files = iter_scan_files(root, config, errors)
    for path in files:
        rel_path = relative(path, root)
        text = path.read_text(encoding="utf-8")
        if is_fixture_path(rel_path, config):
            findings.extend(scan_fixture_file(root, path, text, config, manifest_paths))
            continue
        findings.extend(scan_inline_arrays(root, path, text, config))
        findings.extend(scan_array_from(root, path, text, config))
        findings.extend(scan_mock_imports(root, path, text, config))
        findings.extend(scan_json_file(root, path, text, config))
    return MockDataBoundaryReport(
        enabled=True,
        scanned_files=[relative(path, root) for path in files],
        findings=findings,
        errors=errors,
    )


def scan_inline_arrays(
    root: Path,
    path: Path,
    text: str,
    config: MockDataBoundaryConfig,
) -> list[MockDataFinding]:
    findings: list[MockDataFinding] = []
    for match in ARRAY_ASSIGN_RE.finditer(text):
        name = match.group("name")
        block = bracket_block(text, match.end() - 1)
        if not block:
            continue
        object_count = count_object_items(block)
        line_count = block.count("\n") + 1
        if not MOCKISH_RE.search(name) and object_count <= config.max_inline_object_items * 3:
            continue
        if object_count > config.max_inline_object_items or line_count > config.max_inline_lines:
            findings.append(
                finding(
                    root,
                    path,
                    text,
                    match.start("name"),
                    "inline-mock-array",
                    f"move inline mock-like data `{name}` to a network handler, scenario factory, or fixture",
                    suggested_layer="scenario-factory",
                    suggested_paths=SUGGESTED_SCENARIO_PATHS,
                )
            )
    return findings


def scan_array_from(
    root: Path,
    path: Path,
    text: str,
    config: MockDataBoundaryConfig,
) -> list[MockDataFinding]:
    findings: list[MockDataFinding] = []
    for match in ARRAY_FROM_RE.finditer(text):
        name = match.group("name")
        count = int(match.group("count"))
        if count <= config.max_inline_array_from_length:
            continue
        if not MOCKISH_RE.search(name):
            continue
        findings.append(
            finding(
                root,
                path,
                text,
                match.start("name"),
                "large-generated-mock",
                f"move generated mock-like collection `{name}` length {count} to a deterministic scenario factory",
                suggested_layer="deterministic-scenario-factory",
                suggested_paths=SUGGESTED_SCENARIO_PATHS,
            )
        )
    return findings


def scan_mock_imports(
    root: Path,
    path: Path,
    text: str,
    config: MockDataBoundaryConfig,
) -> list[MockDataFinding]:
    rel_path = relative(path, root)
    if matches_any(rel_path, config.allowed_mock_consumer_paths):
        return []
    findings: list[MockDataFinding] = []
    for match in IMPORT_RE.finditer(text):
        target = match.group("target") or match.group("require") or match.group("dynamic") or ""
        resolved = resolve_import_target(rel_path, target, config)
        denied = resolved and matches_any(resolved, config.runtime_import_denied_paths)
        if denied or MOCKISH_RE.search(target):
            detail = f"`{target}`"
            if resolved:
                detail = f"`{target}` -> `{resolved}`"
            findings.append(
                finding(
                    root,
                    path,
                    text,
                    match.start(),
                    "mock-import-in-runtime-path",
                    f"runtime path imports mock/fixture boundary {detail}; prefer adapter or network handler indirection",
                    suggested_layer="network-handler-or-adapter",
                    suggested_paths=("mocks/", "mock-data/scenarios.jsonl"),
                )
            )
    return findings


def scan_json_file(
    root: Path,
    path: Path,
    text: str,
    config: MockDataBoundaryConfig,
) -> list[MockDataFinding]:
    if path.suffix != ".json":
        return []
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return []
    if isinstance(value, list) and len(value) > config.max_inline_object_items and not is_fixture_path(
        relative(path, root), config
    ):
        return [
            MockDataFinding(
                path=relative(path, root),
                line=1,
                code="json-mock-data-outside-fixture",
                message="large JSON data belongs under a declared fixture path",
                suggested_layer="fixture",
                suggested_paths=("fixtures/", "mock-data/"),
            )
        ]
    return []


def resolve_import_target(rel_path: str, target: str, config: MockDataBoundaryConfig) -> str:
    if target.startswith("."):
        return normalize_manifest_path(posixpath.join(posixpath.dirname(rel_path), target))
    for prefix in config.import_alias_prefixes:
        if target.startswith(prefix):
            return normalize_manifest_path(target[len(prefix) :])
    return normalize_manifest_path(target)


def bracket_block(text: str, start: int) -> str:
    depth = 0
    in_string: str | None = None
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == in_string:
                in_string = None
            continue
        if char in {"'", '"', "`"}:
            in_string = char
            continue
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return ""


def count_object_items(block: str) -> int:
    return sum(1 for line in block.splitlines() if line.strip().startswith("{"))


def finding(
    root: Path,
    path: Path,
    text: str,
    offset: int,
    code: str,
    message: str,
    *,
    suggested_layer: str = "",
    suggested_paths: tuple[str, ...] = (),
) -> MockDataFinding:
    return MockDataFinding(
        path=relative(path, root),
        line=text.count("\n", 0, offset) + 1,
        code=code,
        message=message,
        suggested_layer=suggested_layer,
        suggested_paths=suggested_paths,
    )


def render_report(report: MockDataBoundaryReport) -> str:
    lines = ["Mock data boundary check"]
    if not report.enabled:
        lines.append("Disabled")
        return "\n".join(lines)
    lines.append(f"Scanned files: {len(report.scanned_files)}")
    lines.extend(f"ERROR: {message}" for message in report.errors)
    for item in report.findings:
        suggestion = ""
        if item.suggested_layer:
            paths = ", ".join(item.suggested_paths) if item.suggested_paths else "(none)"
            suggestion = f" [layer: {item.suggested_layer}; suggested: {paths}; doc: {item.doc_ref}]"
        lines.append(f"REVIEW: {item.path}:{item.line} {item.code}: {item.message}{suggestion}")
    if not report.errors and not report.findings:
        lines.append("OK")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    report = build_report()
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print(render_report(report))
    if report.errors or (args.strict and report.findings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
