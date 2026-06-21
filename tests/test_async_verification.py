from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import start_async_verification  # noqa: E402


class AsyncVerificationTest(unittest.TestCase):
    def test_list_prints_presets(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = start_async_verification.main(["--list"])

        self.assertEqual(exit_code, 0)
        self.assertIn("active-browser-smoke", output.getvalue())

    def test_dry_run_prints_commands_without_running(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = start_async_verification.main(["active-static-contracts", "--dry-run"])

        self.assertEqual(exit_code, 0)
        self.assertIn("threejs-snake-contract", output.getvalue())
        self.assertIn("check_ai_governance.py", output.getvalue())

    def test_status_payload_uses_bounded_schema(self) -> None:
        payload = start_async_verification.status_payload(
            preset="demo",
            run_id="run-1",
            state="queued",
            started_at=None,
            finished_at=None,
        )

        self.assertEqual(payload["schema_version"], "async-verification/v1")
        self.assertEqual(payload["state"], "queued")

    def test_foreground_run_writes_passed_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime_root = Path(tmp) / "async-verification"
            command = start_async_verification.CommandSpec(
                "ok",
                (sys.executable, "-c", "print('async ok')"),
            )
            with (
                mock.patch.object(start_async_verification, "RUNTIME_ROOT", runtime_root),
                mock.patch.dict(start_async_verification.PRESETS, {"unit": (command,)}, clear=True),
            ):
                exit_code = start_async_verification.run_preset("unit", "run-1", foreground=False)

            status = json.loads((runtime_root / "run-1" / "status.json").read_text(encoding="utf-8"))
            log_text = (runtime_root / "run-1" / "verification.log").read_text(encoding="utf-8")

        self.assertEqual(exit_code, 0)
        self.assertEqual(status["state"], "passed")
        self.assertEqual(status["command_results"][0]["label"], "ok")
        self.assertIn("async ok", log_text)


if __name__ == "__main__":
    unittest.main()
