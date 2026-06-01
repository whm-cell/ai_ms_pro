#!/usr/bin/env python3

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path
import sys
from urllib.parse import urlparse

import export_agent_trace


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = export_agent_trace.DEFAULT_INPUT
SCHEMA_VERSION = "trace-remote-interop-report/v1"
LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a bounded OTLP remote trace interop probe.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="agent-trace/v1 JSONL input path.")
    parser.add_argument("--endpoint", help="Explicit OTLP HTTP endpoint.")
    parser.add_argument("--send", action="store_true", help="Send one bounded OTLP HTTP JSON probe.")
    parser.add_argument("--output", help="Optional JSON output path.")
    parser.add_argument("--timeout", type=float, default=10.0, help="Network timeout for --send.")
    parser.add_argument(
        "--endpoint-scope",
        choices=["local-capture-server", "external-test-endpoint", "user-confirmed-collector"],
        help="Explicit endpoint scope override.",
    )
    parser.add_argument(
        "--verified-remote",
        action="store_true",
        help="Mark the report as verified-remote only after separate operator review of a successful bounded probe.",
    )
    return parser.parse_args()


def infer_endpoint_scope(endpoint: str | None, explicit: str | None) -> str:
    if explicit:
        return explicit
    if not endpoint:
        return "local-capture-server"
    parsed = urlparse(endpoint)
    if parsed.hostname in LOCAL_HOSTS:
        return "local-capture-server"
    return "external-test-endpoint"


def capability_level(*, send: bool, remote_ok: bool, verified_remote: bool) -> str:
    if not send:
        return "local-only"
    if verified_remote and remote_ok:
        return "verified-remote"
    return "pilot-remote"


def build_report(
    *,
    input_path: Path,
    endpoint: str | None,
    send: bool,
    timeout: float,
    endpoint_scope: str | None,
    verified_remote: bool,
) -> dict[str, object]:
    export_report = export_agent_trace.build_export(
        input_path,
        export_agent_trace.OTLP_HTTP_JSON_FORMAT,
        endpoint=endpoint,
        send=send,
        timeout=timeout,
    )
    remote_ok = bool(export_report.remote_status and export_report.remote_status.get("ok"))
    scope = infer_endpoint_scope(endpoint, endpoint_scope)
    report = {
        "schema_version": SCHEMA_VERSION,
        "recorded_at": datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "input_path": export_report.input_path,
        "export_format": export_report.format,
        "endpoint_scope": scope,
        "capability_level": capability_level(send=send, remote_ok=remote_ok, verified_remote=verified_remote),
        "network_exported": export_report.network_exported,
        "endpoint": endpoint,
        "remote_status": export_report.remote_status or {"ok": False, "http_status": None},
        "trace_mapping": {
            "span_count": export_report.span_count,
            "original_trace_id": first_original_trace_id(export_report.output),
            "otlp_span_count": count_otlp_spans(export_report.output),
        },
        "claim_boundary": "bounded-remote-interop",
        "note": (
            "Bounded OTLP probe only; does not prove OpenAI hosted trace, MCP, A2A, or broad collector interoperability."
        ),
    }
    return report


def first_original_trace_id(output: dict[str, object]) -> str:
    resource_spans = output.get("resourceSpans")
    if not isinstance(resource_spans, list) or not resource_spans:
        return ""
    scope_spans = resource_spans[0].get("scopeSpans")
    if not isinstance(scope_spans, list) or not scope_spans:
        return ""
    spans = scope_spans[0].get("spans")
    if not isinstance(spans, list) or not spans:
        return ""
    attrs = spans[0].get("attributes")
    if not isinstance(attrs, list):
        return ""
    for item in attrs:
        if not isinstance(item, dict):
            continue
        if item.get("key") != "agent.original_trace_id":
            continue
        value = item.get("value")
        if isinstance(value, dict):
            string_value = value.get("stringValue")
            if isinstance(string_value, str):
                return string_value
    return ""


def count_otlp_spans(output: dict[str, object]) -> int:
    resource_spans = output.get("resourceSpans")
    if not isinstance(resource_spans, list):
        return 0
    total = 0
    for resource in resource_spans:
        if not isinstance(resource, dict):
            continue
        scope_spans = resource.get("scopeSpans")
        if not isinstance(scope_spans, list):
            continue
        for scope in scope_spans:
            if not isinstance(scope, dict):
                continue
            spans = scope.get("spans")
            if isinstance(spans, list):
                total += len(spans)
    return total


def main() -> int:
    args = parse_args()
    if args.verified_remote and not args.send:
        print("verify_remote_trace_interop failed: --verified-remote requires --send", file=sys.stderr)
        return 1
    report = build_report(
        input_path=Path(args.input).expanduser(),
        endpoint=args.endpoint,
        send=args.send,
        timeout=args.timeout,
        endpoint_scope=args.endpoint_scope,
        verified_remote=args.verified_remote,
    )
    text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
