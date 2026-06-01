from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import sys
import tempfile
from threading import Thread
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_remote_trace_interop_report  # noqa: E402
import verify_remote_trace_interop  # noqa: E402


class RemoteTraceInteropTest(unittest.TestCase):
    def test_local_only_report_without_send(self) -> None:
        report = verify_remote_trace_interop.build_report(
            input_path=verify_remote_trace_interop.DEFAULT_INPUT,
            endpoint=None,
            send=False,
            timeout=5,
            endpoint_scope=None,
            verified_remote=False,
        )

        self.assertEqual(report["capability_level"], "local-only")
        self.assertFalse(report["network_exported"])

    def test_pilot_remote_report_with_local_capture_server(self) -> None:
        with local_capture_server() as server:
            endpoint = f"http://127.0.0.1:{server.server_port}/v1/traces"
            report = verify_remote_trace_interop.build_report(
                input_path=verify_remote_trace_interop.DEFAULT_INPUT,
                endpoint=endpoint,
                send=True,
                timeout=5,
                endpoint_scope="external-test-endpoint",
                verified_remote=False,
            )

        self.assertEqual(report["capability_level"], "pilot-remote")
        self.assertTrue(report["network_exported"])
        self.assertEqual(report["remote_status"], {"http_status": 200, "ok": True})

    def test_report_validator_rejects_verified_remote_for_local_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "report.json"
            path.write_text(
                json.dumps(
                    {
                        "schema_version": "trace-remote-interop-report/v1",
                        "recorded_at": "2026-06-01T00:00:00Z",
                        "input_path": "docs/ai/standards/agent-trace-sample.jsonl",
                        "export_format": "otlp-http-json",
                        "endpoint_scope": "local-capture-server",
                        "capability_level": "verified-remote",
                        "network_exported": True,
                        "endpoint": "http://127.0.0.1:4318/v1/traces",
                        "remote_status": {"http_status": 200, "ok": True},
                        "trace_mapping": {
                            "span_count": 1,
                            "original_trace_id": "trace-stop-observation-sample",
                            "otlp_span_count": 1,
                        },
                        "claim_boundary": "bounded-remote-interop",
                        "note": "invalid test report",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            report = json.loads(path.read_text(encoding="utf-8"))
            errors = check_remote_trace_interop_report.validate_report(report, path)

        self.assertTrue(any("verified-remote cannot use local-capture-server scope" in item for item in errors))


class CaptureHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        self.rfile.read(length)
        self.send_response(200)
        self.end_headers()

    def log_message(self, format: str, *args: object) -> None:
        return


class local_capture_server:
    def __enter__(self) -> HTTPServer:
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
