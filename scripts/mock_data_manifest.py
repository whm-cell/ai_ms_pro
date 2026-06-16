from __future__ import annotations

import json
import posixpath
from pathlib import Path

from mock_data_boundary_lib import MockDataBoundaryConfig, MockDataFinding


SUGGESTED_SCENARIO_PATHS = ("mock-data/scenarios.jsonl", "mocks/scenarios.jsonl")
VALID_MANIFEST_SURFACES = {"dev", "test", "story", "demo", "contract-sample"}
VALID_MANIFEST_ADAPTERS = {
    "fixture",
    "scenario-factory",
    "msw-handler",
    "playwright-route",
    "openapi-example",
    "manual-seed",
}


def load_manifest_index(
    root: Path,
    config: MockDataBoundaryConfig,
    errors: list[str],
) -> tuple[set[str], list[MockDataFinding]]:
    data_paths: set[str] = set()
    findings: list[MockDataFinding] = []
    seen_ids: dict[str, tuple[str, int]] = {}
    seen_paths: dict[str, tuple[str, int]] = {}
    for manifest in config.scenario_manifest_paths:
        manifest_path = root / manifest
        if not manifest_path.exists():
            continue
        for line_no, line in enumerate(manifest_path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"{manifest}:{line_no} invalid JSONL: {exc.msg}")
                continue
            findings.extend(validate_manifest_row(root, manifest, line_no, row, seen_ids, seen_paths, data_paths))
    return data_paths, findings


def validate_manifest_row(
    root: Path,
    manifest: str,
    line_no: int,
    row: object,
    seen_ids: dict[str, tuple[str, int]],
    seen_paths: dict[str, tuple[str, int]],
    data_paths: set[str],
) -> list[MockDataFinding]:
    if not isinstance(row, dict):
        return [manifest_finding(manifest, line_no, "invalid-scenario-manifest-row", "manifest row must be an object")]
    findings = validate_manifest_enums(manifest, line_no, row)
    findings.extend(validate_manifest_required_strings(manifest, line_no, row))
    findings.extend(validate_manifest_id(manifest, line_no, string_field(row, "id"), seen_ids))
    paths = string_list_field(row, "data_paths")
    if not paths:
        findings.append(manifest_finding(manifest, line_no, "invalid-scenario-manifest-row", "`data_paths` is required"))
    for data_path in paths:
        findings.extend(validate_manifest_data_path(root, manifest, line_no, data_path, seen_paths))
        data_paths.add(normalize_manifest_path(data_path))
    return findings


def validate_manifest_enums(manifest: str, line_no: int, row: dict[str, object]) -> list[MockDataFinding]:
    findings: list[MockDataFinding] = []
    if string_field(row, "schema") != "mock-data-scenario/v1":
        findings.append(
            manifest_finding(manifest, line_no, "invalid-scenario-manifest-row", "`schema` must be `mock-data-scenario/v1`")
        )
    surface = string_field(row, "surface")
    if surface not in VALID_MANIFEST_SURFACES:
        allowed = ", ".join(sorted(VALID_MANIFEST_SURFACES))
        findings.append(
            manifest_finding(manifest, line_no, "invalid-scenario-manifest-row", f"`surface` must be one of {allowed}")
        )
    adapter = string_field(row, "adapter")
    if adapter not in VALID_MANIFEST_ADAPTERS:
        allowed = ", ".join(sorted(VALID_MANIFEST_ADAPTERS))
        findings.append(
            manifest_finding(manifest, line_no, "invalid-scenario-manifest-row", f"`adapter` must be one of {allowed}")
        )
    return findings


def validate_manifest_required_strings(
    manifest: str,
    line_no: int,
    row: dict[str, object],
) -> list[MockDataFinding]:
    findings: list[MockDataFinding] = []
    for field in ("source_truth", "owner", "expires_at"):
        if not string_field(row, field):
            findings.append(manifest_finding(manifest, line_no, "invalid-scenario-manifest-row", f"`{field}` is required"))
    return findings


def validate_manifest_id(
    manifest: str,
    line_no: int,
    row_id: str,
    seen_ids: dict[str, tuple[str, int]],
) -> list[MockDataFinding]:
    if not row_id:
        return [manifest_finding(manifest, line_no, "invalid-scenario-manifest-row", "`id` is required")]
    if row_id not in seen_ids:
        seen_ids[row_id] = (manifest, line_no)
        return []
    prev_manifest, prev_line = seen_ids[row_id]
    return [
        manifest_finding(
            manifest,
            line_no,
            "duplicate-scenario-manifest-id",
            f"`id` {row_id} duplicates {prev_manifest}:{prev_line}",
        )
    ]


def validate_manifest_data_path(
    root: Path,
    manifest: str,
    line_no: int,
    data_path: str,
    seen_paths: dict[str, tuple[str, int]],
) -> list[MockDataFinding]:
    findings: list[MockDataFinding] = []
    normalized = normalize_manifest_path(data_path)
    if not (root / normalized).exists():
        findings.append(
            manifest_finding(
                manifest,
                line_no,
                "missing-scenario-data-path",
                f"`data_paths` entry `{normalized}` does not exist",
            )
        )
    if normalized in seen_paths:
        prev_manifest, prev_line = seen_paths[normalized]
        findings.append(
            manifest_finding(
                manifest,
                line_no,
                "duplicate-scenario-data-path",
                f"`data_paths` entry `{normalized}` duplicates {prev_manifest}:{prev_line}",
            )
        )
    else:
        seen_paths[normalized] = (manifest, line_no)
    return findings


def string_field(row: dict[str, object], field: str) -> str:
    value = row.get(field)
    return value if isinstance(value, str) and value.strip() else ""


def string_list_field(row: dict[str, object], field: str) -> list[str]:
    value = row.get(field)
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, str) and item.strip()]


def manifest_finding(manifest: str, line: int, code: str, message: str) -> MockDataFinding:
    return MockDataFinding(
        path=manifest,
        line=line,
        code=code,
        message=message,
        suggested_layer="scenario-manifest",
        suggested_paths=(manifest,),
    )


def normalize_manifest_path(path: str) -> str:
    normalized = posixpath.normpath(path.replace("\\", "/"))
    if normalized == ".":
        return ""
    return normalized.removeprefix("./")
