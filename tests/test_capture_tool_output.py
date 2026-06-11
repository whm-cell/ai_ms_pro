from __future__ import annotations

import gc
import json
import sys
import tempfile
import unittest
import warnings
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import capture_tool_output  # noqa: E402


class CaptureToolOutputTest(unittest.TestCase):
    def test_successful_command_writes_artifacts_and_bounded_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "tool-outputs"
            result = capture_tool_output.capture_command(
                [
                    sys.executable,
                    "-c",
                    "print('Error: first line'); print('SECRET_SHOULD_NOT_APPEAR_' + 'x' * 5000)",
                ],
                slug="success",
                output_dir=output_dir,
            )
            report = capture_tool_output.render_capture_report(result, max_output_chars=1000)

            artifact = output_dir / Path(result.artifact_path).name
            metadata = output_dir / Path(result.metadata_path).name

            self.assertEqual(result.exit_code, 0)
            self.assertTrue(artifact.exists())
            self.assertTrue(metadata.exists())
            self.assertIn("Captured Tool Output", report)
            self.assertIn("Tool output summary truncated", report)
            self.assertNotIn("x" * 1000, report)
            payload = json.loads(metadata.read_text(encoding="utf-8"))
            self.assertEqual(payload["exit_code"], 0)
            self.assertEqual(payload["command"][0], sys.executable)

    def test_failing_command_preserves_exit_code_and_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "tool-outputs"
            result = capture_tool_output.capture_command(
                [sys.executable, "-c", "import sys; print('FAILED case'); sys.exit(7)"],
                slug="failure",
                output_dir=output_dir,
            )
            report = capture_tool_output.render_capture_report(result, max_output_chars=1200)
            metadata = output_dir / Path(result.metadata_path).name

            self.assertEqual(result.exit_code, 7)
            self.assertIn("exit code: 7", report)
            self.assertTrue(metadata.exists())
            self.assertEqual(json.loads(metadata.read_text(encoding="utf-8"))["exit_code"], 7)

    def test_capture_closes_subprocess_stdout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "tool-outputs"
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always", ResourceWarning)
                capture_tool_output.capture_command(
                    [sys.executable, "-c", "print('closed pipe')"],
                    slug="close",
                    output_dir=output_dir,
                )
                gc.collect()

        self.assertFalse([item for item in caught if issubclass(item.category, ResourceWarning)])


if __name__ == "__main__":
    unittest.main()
