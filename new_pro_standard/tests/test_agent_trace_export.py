from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import sys
from threading import Thread
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import export_agent_trace  # noqa: E402


class AgentTraceExportTest(unittest.TestCase):
    def test_default_sample_exports_to_local_otel_json(self) -> None:
        report = export_agent_trace.build_export(export_agent_trace.DEFAULT_INPUT)

        self.assertEqual(report.format, "local-otel-json")
        self.assertFalse(report.network_exported)
        self.assertGreater(report.span_count, 0)
        self.assertFalse(report.output["remote_export"]["enabled"])
        self.assertEqual(len(report.output["spans"]), report.span_count)

    def test_span_preserves_trace_identity_and_safe_attributes(self) -> None:
        report = export_agent_trace.build_export(export_agent_trace.DEFAULT_INPUT)
        span = report.output["spans"][0]

        self.assertIn("traceId", span)
        self.assertIn("spanId", span)
        self.assertIn("agent.trace.schema_version", span["attributes"])
        self.assertIn("agent.redaction.state", span["attributes"])

    def test_otlp_http_json_dry_run_does_not_export_network(self) -> None:
        report = export_agent_trace.build_export(
            export_agent_trace.DEFAULT_INPUT,
            export_agent_trace.OTLP_HTTP_JSON_FORMAT,
            endpoint="http://127.0.0.1:4318/v1/traces",
            send=False,
        )

        self.assertEqual(report.format, "otlp-http-json")
        self.assertFalse(report.network_exported)
        self.assertFalse(report.output["remote_export"]["enabled"])
        self.assertIn("resourceSpans", report.output)
        span = report.output["resourceSpans"][0]["scopeSpans"][0]["spans"][0]
        self.assertEqual(len(span["traceId"]), 32)
        self.assertEqual(len(span["spanId"]), 16)

    def test_otlp_http_json_send_requires_explicit_endpoint_and_records_status(self) -> None:
        with local_capture_server() as server:
            endpoint = f"http://127.0.0.1:{server.server_port}/v1/traces"
            report = export_agent_trace.build_export(
                export_agent_trace.DEFAULT_INPUT,
                export_agent_trace.OTLP_HTTP_JSON_FORMAT,
                endpoint=endpoint,
                send=True,
                timeout=5,
            )

        self.assertTrue(report.network_exported)
        self.assertEqual(report.endpoint, endpoint)
        self.assertEqual(report.remote_status, {"http_status": 200, "ok": True})
        self.assertEqual(CaptureHandler.last_path, "/v1/traces")
        self.assertIn("resourceSpans", CaptureHandler.last_json)

    def test_network_send_without_endpoint_fails(self) -> None:
        with self.assertRaises(ValueError):
            export_agent_trace.build_export(
                export_agent_trace.DEFAULT_INPUT,
                export_agent_trace.OTLP_HTTP_JSON_FORMAT,
                send=True,
            )


class CaptureHandler(BaseHTTPRequestHandler):
    last_path = ""
    last_json: dict[str, object] = {}

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length)
        type(self).last_path = self.path
        type(self).last_json = json.loads(body.decode("utf-8"))
        self.send_response(200)
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return


class local_capture_server:
    def __enter__(self) -> HTTPServer:
        CaptureHandler.last_path = ""
        CaptureHandler.last_json = {}
        self.server = HTTPServer(("127.0.0.1", 0), CaptureHandler)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        return self.server

    def __exit__(self, *_exc: object) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
