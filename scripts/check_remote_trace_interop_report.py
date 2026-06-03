#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLE = ROOT / "docs" / "ai" / "standards" / "trace-remote-interop-report.sample.json"
SCHEMA_VERSION = "trace-remote-interop-report/v1"
ALLOWED_SCOPES = {"local-capture-server", "external-test-endpoint", "user-confirmed-collector"}
ALLOWED_LEVELS = {"local-only", "pilot-remote", "verified-remote"}
ALLOWED_FAILURE_MODES = {"not-sent", "none", "remote-status-missing", "remote-error", "http-error", "remote-status-not-ok"}
REQUIRED_WITHHELD_PAYLOADS = {"raw_trace_payload", "request_body", "response_body", "prompt", "transcript", "secret"}
FORBIDDEN_RAW_PAYLOAD_KEYS = {"request_body", "response_body", "raw_payload", "raw_trace_payload", "prompt", "transcript", "secret"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate bounded remote trace interop report shape.")
    parser.add_argument("--report", default=str(DEFAULT_SAMPLE), help=f"Report path. Default: {DEFAULT_SAMPLE}")
    return parser.parse_args()


def validate_report(report: dict[str, Any], path: Path) -> list[str]:
    errors: list[str] = []
    if report.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"{path}: schema_version must be {SCHEMA_VERSION}")
    for field in ("recorded_at", "input_path", "export_format", "endpoint_scope", "capability_level", "claim_boundary", "note"):
        if not isinstance(report.get(field), str) or not str(report[field]).strip():
            errors.append(f"{path}: {field} must be a non-empty string")
    if report.get("endpoint_scope") not in ALLOWED_SCOPES:
        errors.append(f"{path}: endpoint_scope must be one of {sorted(ALLOWED_SCOPES)}")
    if report.get("capability_level") not in ALLOWED_LEVELS:
        errors.append(f"{path}: capability_level must be one of {sorted(ALLOWED_LEVELS)}")
    validate_structured_evidence(report, path, errors)
    validate_no_raw_payload_keys(report, path, errors)
    if not isinstance(report.get("network_exported"), bool):
        errors.append(f"{path}: network_exported must be a boolean")
    remote_status = report.get("remote_status")
    if not isinstance(remote_status, dict):
        errors.append(f"{path}: remote_status must be an object")
    else:
        if not isinstance(remote_status.get("ok"), bool):
            errors.append(f"{path}: remote_status.ok must be a boolean")
        http_status = remote_status.get("http_status")
        if http_status is not None and not isinstance(http_status, int):
            errors.append(f"{path}: remote_status.http_status must be an integer or null")
    trace_mapping = report.get("trace_mapping")
    if not isinstance(trace_mapping, dict):
        errors.append(f"{path}: trace_mapping must be an object")
    else:
        for field in ("span_count", "otlp_span_count"):
            if not isinstance(trace_mapping.get(field), int):
                errors.append(f"{path}: trace_mapping.{field} must be an integer")
        if not isinstance(trace_mapping.get("original_trace_id"), str):
            errors.append(f"{path}: trace_mapping.original_trace_id must be a string")
    capability = report.get("capability_level")
    if capability == "local-only" and report.get("network_exported") is True:
        errors.append(f"{path}: local-only report cannot set network_exported=true")
    if capability == "verified-remote":
        if report.get("network_exported") is not True:
            errors.append(f"{path}: verified-remote requires network_exported=true")
        if not isinstance(remote_status, dict) or remote_status.get("ok") is not True:
            errors.append(f"{path}: verified-remote requires remote_status.ok=true")
        if report.get("endpoint_scope") == "local-capture-server":
            errors.append(f"{path}: verified-remote cannot use local-capture-server scope")
        claim_evidence = report.get("claim_evidence")
        if not isinstance(claim_evidence, dict) or claim_evidence.get("operator_review_confirmed") is not True:
            errors.append(f"{path}: verified-remote requires claim_evidence.operator_review_confirmed=true")
    return errors


def validate_structured_evidence(report: dict[str, Any], path: Path, errors: list[str]) -> None:
    export_attempt = report.get("export_attempt")
    if export_attempt is not None:
        if not isinstance(export_attempt, dict):
            errors.append(f"{path}: export_attempt must be an object")
        else:
            for field in ("send", "network_exported"):
                if not isinstance(export_attempt.get(field), bool):
                    errors.append(f"{path}: export_attempt.{field} must be a boolean")
            if not isinstance(export_attempt.get("timeout_seconds"), (int, float)):
                errors.append(f"{path}: export_attempt.timeout_seconds must be a number")
            if not isinstance(export_attempt.get("export_format"), str) or not export_attempt["export_format"].strip():
                errors.append(f"{path}: export_attempt.export_format must be a non-empty string")
    endpoint_evidence = report.get("endpoint_evidence")
    if endpoint_evidence is not None:
        if not isinstance(endpoint_evidence, dict):
            errors.append(f"{path}: endpoint_evidence must be an object")
        else:
            if endpoint_evidence.get("endpoint_scope") not in ALLOWED_SCOPES:
                errors.append(f"{path}: endpoint_evidence.endpoint_scope must be one of {sorted(ALLOWED_SCOPES)}")
            if endpoint_evidence.get("failure_mode") not in ALLOWED_FAILURE_MODES:
                errors.append(f"{path}: endpoint_evidence.failure_mode must be one of {sorted(ALLOWED_FAILURE_MODES)}")
            for field in ("endpoint_configured", "localhost_endpoint"):
                if not isinstance(endpoint_evidence.get(field), bool):
                    errors.append(f"{path}: endpoint_evidence.{field} must be a boolean")
    claim_evidence = report.get("claim_evidence")
    if claim_evidence is not None:
        if not isinstance(claim_evidence, dict):
            errors.append(f"{path}: claim_evidence must be an object")
        else:
            for field in ("operator_review_required", "operator_review_confirmed"):
                if not isinstance(claim_evidence.get(field), bool):
                    errors.append(f"{path}: claim_evidence.{field} must be a boolean")
            if claim_evidence.get("claim_boundary") != "bounded-remote-interop":
                errors.append(f"{path}: claim_evidence.claim_boundary must be bounded-remote-interop")
    withheld_payloads = report.get("withheld_payloads")
    if withheld_payloads is not None:
        if not isinstance(withheld_payloads, list) or not all(isinstance(item, str) for item in withheld_payloads):
            errors.append(f"{path}: withheld_payloads must be a list of strings")
        elif not REQUIRED_WITHHELD_PAYLOADS.issubset(set(withheld_payloads)):
            errors.append(f"{path}: withheld_payloads must include {sorted(REQUIRED_WITHHELD_PAYLOADS)}")


def validate_no_raw_payload_keys(value: Any, path: Path, errors: list[str], prefix: str = "report") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key in FORBIDDEN_RAW_PAYLOAD_KEYS and prefix != "report.withheld_payloads":
                errors.append(f"{path}: {prefix}.{key} must not be present; record only withheld payload classes")
            validate_no_raw_payload_keys(child, path, errors, f"{prefix}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            validate_no_raw_payload_keys(child, path, errors, f"{prefix}[{index}]")


def main() -> int:
    args = parse_args()
    path = Path(args.report).expanduser()
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"remote trace interop report check failed: report not found: {path}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"remote trace interop report check failed: invalid JSON: {exc}", file=sys.stderr)
        return 1
    if not isinstance(report, dict):
        print("remote trace interop report check failed: report must be a JSON object", file=sys.stderr)
        return 1
    errors = validate_report(report, path)
    if errors:
        print("remote trace interop report check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("remote trace interop report check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
