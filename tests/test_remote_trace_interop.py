from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import sys
import tempfile
from threading import Thread
import unittest
from unittest.mock import patch
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
        self.assertEqual(report["export_attempt"]["send"], False)
        self.assertEqual(report["endpoint_evidence"]["failure_mode"], "not-sent")
        self.assertIn("request_body", report["withheld_payloads"])

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
        self.assertEqual(report["endpoint_scope"], "local-capture-server")
        self.assertEqual(report["endpoint_evidence"]["endpoint_scope"], "local-capture-server")
        self.assertTrue(report["endpoint_evidence"]["localhost_endpoint"])
        self.assertEqual(report["endpoint_evidence"]["failure_mode"], "none")

    def test_verified_remote_loopback_scope_override_downgrades_to_pilot(self) -> None:
        with local_capture_server() as server:
            endpoint = f"http://127.0.0.1:{server.server_port}/v1/traces"
            report = verify_remote_trace_interop.build_report(
                input_path=verify_remote_trace_interop.DEFAULT_INPUT,
                endpoint=endpoint,
                send=True,
                timeout=5,
                endpoint_scope="user-confirmed-collector",
                verified_remote=True,
            )

        self.assertEqual(report["capability_level"], "pilot-remote")
        self.assertEqual(report["endpoint_scope"], "local-capture-server")
        self.assertEqual(report["endpoint_evidence"]["endpoint_scope"], "local-capture-server")
        self.assertTrue(report["endpoint_evidence"]["localhost_endpoint"])
        self.assertTrue(report["claim_evidence"]["operator_review_required"])
        self.assertFalse(report["claim_evidence"]["operator_review_confirmed"])
        self.assertEqual(check_remote_trace_interop_report.validate_report(report, Path("report.json")), [])

    def test_cli_verified_remote_loopback_scope_override_outputs_pilot(self) -> None:
        with local_capture_server() as server:
            endpoint = f"http://127.0.0.1:{server.server_port}/v1/traces"
            stdout = io.StringIO()
            argv = [
                "verify_remote_trace_interop.py",
                "--input",
                str(verify_remote_trace_interop.DEFAULT_INPUT),
                "--endpoint",
                endpoint,
                "--send",
                "--endpoint-scope",
                "user-confirmed-collector",
                "--verified-remote",
            ]

            with patch.object(sys, "argv", argv), redirect_stdout(stdout):
                exit_code = verify_remote_trace_interop.main()

        report = json.loads(stdout.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(report["capability_level"], "pilot-remote")
        self.assertEqual(report["endpoint_scope"], "local-capture-server")
        self.assertFalse(report["claim_evidence"]["operator_review_confirmed"])

    def test_loopback_endpoint_scope_override_is_forced_local(self) -> None:
        for endpoint in (
            "http://localhost:4318/v1/traces",
            "http://localhost.:4318/v1/traces",
            "http://127.42.0.1:4318/v1/traces",
            "http://[::1]:4318/v1/traces",
        ):
            with self.subTest(endpoint=endpoint):
                self.assertEqual(
                    verify_remote_trace_interop.infer_endpoint_scope(endpoint, "user-confirmed-collector"),
                    "local-capture-server",
                )

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

    def test_report_validator_rejects_verified_remote_for_loopback_scope_override(self) -> None:
        report = {
            "schema_version": "trace-remote-interop-report/v1",
            "recorded_at": "2026-06-01T00:00:00Z",
            "input_path": "docs/ai/standards/agent-trace-sample.jsonl",
            "export_format": "otlp-http-json",
            "endpoint_scope": "user-confirmed-collector",
            "capability_level": "verified-remote",
            "network_exported": True,
            "endpoint": "http://localhost:4318/v1/traces",
            "remote_status": {"http_status": 200, "ok": True},
            "trace_mapping": {
                "span_count": 1,
                "original_trace_id": "trace-stop-observation-sample",
                "otlp_span_count": 1,
            },
            "endpoint_evidence": {
                "endpoint_scope": "user-confirmed-collector",
                "endpoint_configured": True,
                "localhost_endpoint": False,
                "failure_mode": "none",
            },
            "claim_evidence": {
                "operator_review_required": True,
                "operator_review_confirmed": True,
                "claim_boundary": "bounded-remote-interop",
            },
            "claim_boundary": "bounded-remote-interop",
            "note": "invalid test report",
        }

        errors = check_remote_trace_interop_report.validate_report(report, Path("report.json"))

        self.assertTrue(
            any("localhost/loopback endpoint must use endpoint_scope=local-capture-server" in item for item in errors)
        )
        self.assertTrue(any("verified-remote cannot use localhost/loopback endpoint" in item for item in errors))

    def test_report_validator_rejects_raw_payload_body(self) -> None:
        report = verify_remote_trace_interop.build_report(
            input_path=verify_remote_trace_interop.DEFAULT_INPUT,
            endpoint=None,
            send=False,
            timeout=5,
            endpoint_scope=None,
            verified_remote=False,
        )
        report["request_body"] = {"raw": "payload"}

        errors = check_remote_trace_interop_report.validate_report(report, Path("report.json"))

        self.assertTrue(any("must not be present" in item for item in errors))

    def test_write_report_creates_parent_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            output_path = Path(tempdir) / "nested" / "report.json"
            report = {"schema_version": "trace-remote-interop-report/v1"}

            verify_remote_trace_interop.write_report(
                str(output_path),
                json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            )

            self.assertTrue(output_path.exists())
            self.assertEqual(json.loads(output_path.read_text(encoding="utf-8")), report)


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
