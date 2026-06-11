#!/usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
import sys
from typing import Any
from urllib import error, request

import check_agent_trace_schema


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = check_agent_trace_schema.DEFAULT_SAMPLE
LOCAL_OTEL_FORMAT = "local-otel-json"
OTLP_HTTP_JSON_FORMAT = "otlp-http-json"
DEFAULT_FORMAT = LOCAL_OTEL_FORMAT
TRACE_ID_HEX_LENGTH = 32
SPAN_ID_HEX_LENGTH = 16


@dataclass(frozen=True)
class ExportReport:
    input_path: str
    format: str
    network_exported: bool
    endpoint: str | None
    remote_status: dict[str, Any] | None
    span_count: int
    output: dict[str, Any]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export agent-trace/v1 JSONL to a local adapter format.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="agent-trace/v1 JSONL input path.")
    parser.add_argument("--output", help="Optional output JSON path. Defaults to stdout.")
    parser.add_argument(
        "--format",
        default=DEFAULT_FORMAT,
        choices=[LOCAL_OTEL_FORMAT, OTLP_HTTP_JSON_FORMAT],
        help="Export format. Network export still requires --send and --endpoint.",
    )
    parser.add_argument("--endpoint", help="Explicit OTLP HTTP endpoint. Required with --send.")
    parser.add_argument("--send", action="store_true", help="POST OTLP HTTP JSON to --endpoint.")
    parser.add_argument("--timeout", type=float, default=10.0, help="Network timeout for --send.")
    return parser.parse_args()


def relative(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def build_export(
    input_path: Path,
    export_format: str = DEFAULT_FORMAT,
    *,
    endpoint: str | None = None,
    send: bool = False,
    timeout: float = 10.0,
) -> ExportReport:
    if send and not endpoint:
        raise ValueError("--send requires an explicit --endpoint")
    if send and export_format != OTLP_HTTP_JSON_FORMAT:
        raise ValueError("--send is only supported for otlp-http-json")
    errors = check_agent_trace_schema.validate_trace(check_agent_trace_schema.DEFAULT_SCHEMA, input_path)
    if errors:
        raise ValueError("trace input failed schema validation: " + "; ".join(errors))
    records = check_agent_trace_schema.load_jsonl(input_path)
    output = build_payload(records, export_format, endpoint=endpoint, send=send)
    remote_status = post_otlp_json(output, endpoint, timeout=timeout) if send else None
    payload = {
        **output,
        "network_exported": send,
        "remote_export": remote_export_metadata(export_format, endpoint=endpoint, send=send, status=remote_status),
    }
    return ExportReport(
        input_path=relative(input_path),
        format=export_format,
        network_exported=send,
        endpoint=endpoint,
        remote_status=remote_status,
        span_count=len(records),
        output=payload,
    )


def build_payload(
    records: list[dict[str, Any]],
    export_format: str,
    *,
    endpoint: str | None,
    send: bool,
) -> dict[str, Any]:
    if export_format == LOCAL_OTEL_FORMAT:
        return build_local_otel_payload(records)
    if export_format == OTLP_HTTP_JSON_FORMAT:
        return build_otlp_http_json_payload(records, endpoint=endpoint, send=send)
    raise ValueError(f"unsupported export format: {export_format}")


def build_local_otel_payload(records: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "export_format": LOCAL_OTEL_FORMAT,
        "schema_version": "agent-trace/v1",
        "resource": {
            "service.name": "ai-ms-pro-agent-harness",
            "telemetry.sdk.language": "python",
            "adapter.kind": "local-json",
        },
        "scope": {
            "name": "scripts/export_agent_trace.py",
            "version": "1",
        },
        "spans": [to_local_otel_span(record) for record in records],
    }


def build_otlp_http_json_payload(
    records: list[dict[str, Any]],
    *,
    endpoint: str | None,
    send: bool,
) -> dict[str, Any]:
    return {
        "export_format": OTLP_HTTP_JSON_FORMAT,
        "schema_version": "agent-trace/v1",
        "resourceSpans": [
            {
                "resource": {
                    "attributes": otlp_attributes(
                        {
                            "service.name": "ai-ms-pro-agent-harness",
                            "telemetry.sdk.language": "python",
                            "telemetry.sdk.name": "ai-ms-pro-agent-trace-exporter",
                            "agent.export.network.requested": send,
                            "agent.export.endpoint.configured": bool(endpoint),
                        }
                    )
                },
                "scopeSpans": [
                    {
                        "scope": {"name": "scripts/export_agent_trace.py", "version": "1"},
                        "spans": [to_otlp_span(record) for record in records],
                    }
                ],
            }
        ],
    }


def to_local_otel_span(record: dict[str, Any]) -> dict[str, Any]:
    span = {
        "traceId": record["trace_id"],
        "spanId": record["span_id"],
        "parentSpanId": record.get("parent_span_id"),
        "name": record["name"],
        "kind": "INTERNAL",
        "startTimeUnixNano": timestamp_to_nanos(str(record["start_time"])),
        "endTimeUnixNano": timestamp_to_nanos(str(record["end_time"])),
        "status": {"code": str(record["status"]["code"]).upper()},
        "attributes": trace_attributes(record),
        "links": record.get("links", []),
    }
    if record.get("event"):
        span["events"] = [{"name": record["event"], "timeUnixNano": span["startTimeUnixNano"]}]
    if record.get("error"):
        span["error"] = record["error"]
    return span


def to_otlp_span(record: dict[str, Any]) -> dict[str, Any]:
    span = {
        "traceId": stable_hex_id(record["trace_id"], TRACE_ID_HEX_LENGTH),
        "spanId": stable_hex_id(record["span_id"], SPAN_ID_HEX_LENGTH),
        "name": record["name"],
        "kind": "SPAN_KIND_INTERNAL",
        "startTimeUnixNano": str(timestamp_to_nanos(str(record["start_time"]))),
        "endTimeUnixNano": str(timestamp_to_nanos(str(record["end_time"]))),
        "status": {"code": otlp_status_code(str(record["status"]["code"]))},
        "attributes": otlp_attributes(
            {
                **trace_attributes(record),
                "agent.original_trace_id": record["trace_id"],
                "agent.original_span_id": record["span_id"],
            }
        ),
    }
    if record.get("parent_span_id"):
        span["parentSpanId"] = stable_hex_id(record["parent_span_id"], SPAN_ID_HEX_LENGTH)
    if record.get("event"):
        span["events"] = [
            {
                "name": record["event"],
                "timeUnixNano": span["startTimeUnixNano"],
            }
        ]
    if record.get("links"):
        span["links"] = [{"attributes": otlp_attributes(link)} for link in record["links"]]
    return span


def trace_attributes(record: dict[str, Any]) -> dict[str, Any]:
    attributes: dict[str, Any] = {
        "agent.trace.schema_version": record["schema_version"],
        "agent.kind": record["kind"],
        "agent.name": record["agent"]["name"],
        "agent.role": record["agent"]["role"],
        "agent.redaction.state": record["redaction"]["state"],
    }
    if record.get("requirement_ids"):
        attributes["agent.requirement_ids"] = record["requirement_ids"]
    if record.get("workstream_ids"):
        attributes["agent.workstream_ids"] = record["workstream_ids"]
    for key, value in record.get("attributes", {}).items():
        attributes[f"agent.attr.{key}"] = value
    return attributes


def timestamp_to_nanos(value: str) -> int:
    timestamp = datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    return int(timestamp.timestamp() * 1_000_000_000)


def stable_hex_id(value: str, length: int) -> str:
    return sha256(value.encode("utf-8")).hexdigest()[:length]


def otlp_attributes(attributes: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"key": key, "value": otlp_value(value)} for key, value in sorted(attributes.items())]


def otlp_value(value: Any) -> dict[str, Any]:
    if isinstance(value, bool):
        return {"boolValue": value}
    if isinstance(value, int) and not isinstance(value, bool):
        return {"intValue": str(value)}
    if isinstance(value, float):
        return {"doubleValue": value}
    if isinstance(value, list):
        return {"arrayValue": {"values": [otlp_value(item) for item in value]}}
    if isinstance(value, dict):
        return {"kvlistValue": {"values": otlp_attributes(value)}}
    if value is None:
        return {"stringValue": ""}
    return {"stringValue": str(value)}


def otlp_status_code(code: str) -> str:
    if code.lower() == "ok":
        return "STATUS_CODE_OK"
    if code.lower() == "error":
        return "STATUS_CODE_ERROR"
    return "STATUS_CODE_UNSET"


def remote_export_metadata(
    export_format: str,
    *,
    endpoint: str | None,
    send: bool,
    status: dict[str, Any] | None,
) -> dict[str, Any]:
    if export_format != OTLP_HTTP_JSON_FORMAT:
        return {
            "enabled": False,
            "reason": "Local adapter only; OpenAI, OTLP, MCP, and A2A interoperability remain future work.",
        }
    return {
        "enabled": send,
        "endpoint": endpoint,
        "network_exported": send,
        "status": status,
        "reason": "OTLP HTTP JSON pilot; network export only runs when --send and --endpoint are explicit.",
    }


def post_otlp_json(payload: dict[str, Any], endpoint: str | None, *, timeout: float) -> dict[str, Any]:
    if endpoint is None:
        raise ValueError("--send requires an explicit --endpoint")
    data = json.dumps(otlp_wire_payload(payload), ensure_ascii=False).encode("utf-8")
    http_request = request.Request(
        endpoint,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with request.urlopen(http_request, timeout=timeout) as response:
            return {"http_status": response.status, "ok": 200 <= response.status < 300}
    except error.URLError as exc:
        raise ValueError(f"OTLP HTTP export failed: {exc}") from exc


def otlp_wire_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {"resourceSpans": payload.get("resourceSpans", [])}


def write_report(report: ExportReport, output_path: Path | None) -> None:
    data = json.dumps(asdict(report), ensure_ascii=False, indent=2)
    if output_path is None:
        print(data)
        return
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(data + "\n", encoding="utf-8")
    print(f"wrote local trace export: {relative(output_path)}")


def main() -> int:
    args = parse_args()
    try:
        report = build_export(
            Path(args.input),
            args.format,
            endpoint=args.endpoint,
            send=args.send,
            timeout=args.timeout,
        )
    except (ValueError, check_agent_trace_schema.ValidationError) as exc:
        print(f"agent trace export failed: {exc}", file=sys.stderr)
        return 1
    write_report(report, Path(args.output) if args.output else None)
    return 0


if __name__ == "__main__":
    sys.exit(main())
