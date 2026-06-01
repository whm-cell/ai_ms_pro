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
    return errors


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
