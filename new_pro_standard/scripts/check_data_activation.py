#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path

import check_mock_data_boundary
from evidence_ref_utils import selector_base_path
from mock_data_boundary_lib import CONFIG_PATH, MockDataFinding, load_config as load_mock_config, load_toml
from mock_data_manifest import normalize_manifest_path, string_field, string_list_field


ROOT = Path(__file__).resolve().parents[1]
VALID_MODES = {"smoke", "shadow-real", "real"}
REAL_MODE_CODES = {
    "fixture-without-scenario-manifest",
    "inline-mock-array",
    "json-mock-data-outside-fixture",
    "large-generated-mock",
    "mock-import-in-runtime-path",
}


@dataclass(frozen=True)
class DataActivationConfig:
    enabled: bool
    mode: str


@dataclass(frozen=True)
class ScenarioRow:
    manifest: str
    line: int
    row: dict[str, object]


@dataclass(frozen=True)
class DataActivationFinding:
    path: str
    line: int
    code: str
    message: str
    doc_ref: str = "docs/ai/standards/mock-data-boundary.md"


@dataclass(frozen=True)
class DataActivationReport:
    enabled: bool
    mode: str
    scenario_count: int
    real_mode_mock_findings: int
    findings: list[DataActivationFinding]
    errors: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check smoke-to-real data activation readiness.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when review findings or errors exist.")
    return parser.parse_args()


def load_activation_config(root: Path, errors: list[str]) -> DataActivationConfig | None:
    config_path = root / CONFIG_PATH
    if not config_path.exists():
        return DataActivationConfig(False, "smoke")
    try:
        table = load_toml(config_path.read_text(encoding="utf-8")).get("data_activation")
    except ValueError as exc:
        errors.append(f"invalid TOML in {CONFIG_PATH}: {exc}")
        return None
    if table is None:
        return DataActivationConfig(False, "smoke")
    if not isinstance(table, dict):
        errors.append("[data_activation] must be a table")
        return None
    enabled = bool_field(table.get("enabled"), default=False, field="data_activation.enabled", errors=errors)
    mode = string_choice(table.get("mode"), default="smoke", field="data_activation.mode", choices=VALID_MODES, errors=errors)
    return None if errors else DataActivationConfig(enabled, mode)


def build_report(root: Path = ROOT) -> DataActivationReport:
    root = root.resolve()
    errors: list[str] = []
    activation = load_activation_config(root, errors)
    if activation is None:
        return DataActivationReport(False, "smoke", 0, 0, [], errors)
    if not activation.enabled:
        return DataActivationReport(False, activation.mode, 0, 0, [], errors)

    mock_config = load_mock_config(root, errors)
    if mock_config is None or not mock_config.enabled:
        errors.append("[mock_data_boundary] must be enabled when [data_activation] is enabled")
        return DataActivationReport(True, activation.mode, 0, 0, [], errors)

    rows = load_scenario_rows(root, mock_config.scenario_manifest_paths, errors)
    findings = activation_findings(root, activation.mode, rows)
    real_mock_findings = 0
    if activation.mode == "real":
        mock_report = check_mock_data_boundary.build_report(root)
        errors.extend(mock_report.errors)
        runtime_findings = [finding for finding in mock_report.findings if finding.code in REAL_MODE_CODES]
        real_mock_findings = len(runtime_findings)
        findings.extend(from_mock_findings(runtime_findings))

    return DataActivationReport(True, activation.mode, len(rows), real_mock_findings, findings, errors)


def load_scenario_rows(root: Path, manifests: tuple[str, ...], errors: list[str]) -> list[ScenarioRow]:
    rows: list[ScenarioRow] = []
    for manifest in manifests:
        manifest_path = root / manifest
        if not manifest_path.exists():
            continue
        for line_no, line in enumerate(manifest_path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"{manifest}:{line_no} invalid JSONL: {exc.msg}")
                continue
            if isinstance(payload, dict):
                rows.append(ScenarioRow(manifest, line_no, payload))
            else:
                errors.append(f"{manifest}:{line_no} manifest row must be an object")
    return rows


def activation_findings(root: Path, mode: str, rows: list[ScenarioRow]) -> list[DataActivationFinding]:
    findings: list[DataActivationFinding] = []
    for scenario in rows:
        surface = string_field(scenario.row, "surface")
        if surface not in {"dev", "demo"}:
            continue
        state = string_field(scenario.row, "activation_state") or "smoke"
        if state not in {"smoke", "shadow-real", "retired"}:
            findings.append(finding(scenario, "invalid-activation-state", "`activation_state` must be smoke, shadow-real, or retired"))
            continue
        if mode == "shadow-real" and state != "retired":
            findings.extend(required_real_link_findings(root, scenario, require_evidence=False))
        if mode == "real":
            if state != "retired":
                findings.append(finding(scenario, "scenario-not-retired-for-real-mode", "dev/demo scenario must be retired before real mode"))
            findings.extend(required_real_link_findings(root, scenario, require_evidence=True))
    return findings


def required_real_link_findings(root: Path, scenario: ScenarioRow, *, require_evidence: bool) -> list[DataActivationFinding]:
    findings: list[DataActivationFinding] = []
    adapter = string_field(scenario.row, "real_adapter_path")
    retire_when = string_field(scenario.row, "retire_when")
    if not adapter:
        findings.append(finding(scenario, "missing-real-adapter-path", "`real_adapter_path` is required for data activation"))
    elif not repo_relative_path_exists(root, adapter):
        findings.append(finding(scenario, "missing-real-adapter-path", f"`real_adapter_path` does not exist: {adapter}"))
    if not retire_when:
        findings.append(finding(scenario, "missing-retire-when", "`retire_when` is required for data activation"))
    evidence_refs = string_list_field(scenario.row, "activation_evidence_refs")
    if require_evidence and not evidence_refs:
        findings.append(finding(scenario, "missing-activation-evidence", "`activation_evidence_refs` is required in real mode"))
    for ref in evidence_refs:
        if not repo_relative_path_exists(root, selector_base_path(ref)):
            findings.append(finding(scenario, "missing-activation-evidence", f"`activation_evidence_refs` item does not exist: {ref}"))
    return findings


def from_mock_findings(items: list[MockDataFinding]) -> list[DataActivationFinding]:
    return [
        DataActivationFinding(
            path=item.path,
            line=item.line,
            code=item.code,
            message=f"real mode requires runtime data through real adapters: {item.message}",
            doc_ref=item.doc_ref,
        )
        for item in items
    ]


def repo_relative_path_exists(root: Path, path: str) -> bool:
    if not path or "://" in path or path.startswith("/"):
        return False
    candidate = (root / normalize_manifest_path(path)).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return False
    return candidate.exists()


def finding(scenario: ScenarioRow, code: str, message: str) -> DataActivationFinding:
    return DataActivationFinding(path=scenario.manifest, line=scenario.line, code=code, message=message)


def bool_field(value: object, *, default: bool, field: str, errors: list[str]) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    errors.append(f"{field} must be a boolean")
    return default


def string_choice(value: object, *, default: str, field: str, choices: set[str], errors: list[str]) -> str:
    if value is None:
        return default
    if isinstance(value, str) and value in choices:
        return value
    errors.append(f"{field} must be one of {', '.join(sorted(choices))}")
    return default


def render_report(report: DataActivationReport) -> str:
    if not report.enabled and not report.errors:
        return "OK: data activation gate disabled"
    lines = [
        f"Data Activation Gate: mode={report.mode}",
        f"Scenario rows scanned: {report.scenario_count}",
    ]
    if report.errors:
        lines.append("ERROR:")
        lines.extend(f"- {error}" for error in report.errors)
    if report.findings:
        lines.append("REVIEW:")
        lines.extend(f"- {item.path}:{item.line} [{item.code}] {item.message}" for item in report.findings)
    if not report.errors and not report.findings:
        lines.append("OK: no data activation findings")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    report = build_report(ROOT)
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print(render_report(report))
    return 1 if args.strict and (report.errors or report.findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
