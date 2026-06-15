from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_sandboxed_command  # noqa: E402


class LocalExecutionPolicyWrapperTest(unittest.TestCase):
    def test_successful_command_enforces_repo_root_and_writes_bounded_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "tool-outputs"
            result = run_sandboxed_command.run_policy_command(
                [
                    sys.executable,
                    "-c",
                    (
                        "import os, sys; "
                        "print('cwd=' + os.getcwd()); "
                        "print('X' * 5000); "
                        "print('stderr-line', file=sys.stderr)"
                    ),
                ],
                output_dir=output_dir,
                slug="success",
            )
            report = run_sandboxed_command.render_run_report(result, max_summary_chars=1800)

            raw_artifact = ROOT / result.artifact_path
            stdout_artifact = ROOT / result.stdout_artifact_path
            stderr_artifact = ROOT / result.stderr_artifact_path
            metadata = ROOT / result.metadata_path

            self.assertEqual(result.exit_code, 0)
            self.assertFalse(result.timed_out)
            self.assertEqual(result.cwd, ".")
            self.assertEqual(output_dir, raw_artifact.parent)
            self.assertTrue(raw_artifact.exists())
            self.assertTrue(stdout_artifact.exists())
            self.assertTrue(stderr_artifact.exists())
            self.assertIn(f"cwd={ROOT}", stdout_artifact.read_text(encoding="utf-8"))
            self.assertIn("X" * 5000, stdout_artifact.read_text(encoding="utf-8"))
            self.assertIn("stderr-line", stderr_artifact.read_text(encoding="utf-8"))
            self.assertIn("# Local Execution Policy Wrapper Result", report)
            self.assertIn("- native sandbox: `false`", report)
            self.assertIn("- execution policy: `argv_only=true shell=false reduced_env=true`", report)
            self.assertIn("## Stdout Summary", report)
            self.assertIn("## Stderr Summary", report)
            self.assertNotIn("X" * 1000, report)

            payload = json.loads(metadata.read_text(encoding="utf-8"))
            self.assertFalse(payload["policy"]["native_sandbox"])
            self.assertTrue(payload["policy"]["argv_only"])
            self.assertFalse(payload["policy"]["shell"])
            self.assertEqual(payload["policy"]["cwd_enforced"], ".")

    def test_cli_requires_argv_separator_after_options(self) -> None:
        stderr = StringIO()
        with redirect_stderr(stderr):
            exit_code = run_sandboxed_command.main([sys.executable, "-c", "print('missing separator')"])

        self.assertEqual(exit_code, 2)
        self.assertIn("required after --", stderr.getvalue())

    def test_command_arguments_are_not_interpreted_by_a_shell(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "tool-outputs"
            sentinel = Path(tmp) / "sentinel"
            result = run_sandboxed_command.run_policy_command(
                [
                    sys.executable,
                    "-c",
                    "import sys; print(sys.argv[1:])",
                    ";",
                    sys.executable,
                    "-c",
                    f"from pathlib import Path; Path({str(sentinel)!r}).write_text('bad')",
                ],
                output_dir=output_dir,
                slug="argv-only",
            )

            self.assertEqual(result.exit_code, 0)
            self.assertFalse(sentinel.exists())
            stdout_text = (ROOT / result.stdout_artifact_path).read_text(encoding="utf-8")
            self.assertIn("';'", stdout_text)

    def test_environment_is_reduced_to_allowlist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "tool-outputs"
            command = [
                sys.executable,
                "-c",
                (
                    "import json, os; "
                    "print(json.dumps({"
                    "'has_path': 'PATH' in os.environ, "
                    "'secret': os.environ.get('SECRET_TOKEN'), "
                    "'keys': sorted(os.environ)"
                    "}))"
                ),
            ]
            with mock.patch.dict(os.environ, {"SECRET_TOKEN": "should-not-pass"}, clear=False):
                result = run_sandboxed_command.run_policy_command(command, output_dir=output_dir, slug="env")

            payload = json.loads((ROOT / result.stdout_artifact_path).read_text(encoding="utf-8"))
            self.assertTrue(payload["has_path"])
            self.assertIsNone(payload["secret"])
            self.assertLessEqual(set(payload["keys"]), set(run_sandboxed_command.ALLOWED_ENV_KEYS))

    def test_destructive_command_is_refused_without_human_confirmation(self) -> None:
        with self.assertRaises(run_sandboxed_command.PolicyRefusal) as caught:
            run_sandboxed_command.run_policy_command(["rm", "-rf", "build/cache"])

        self.assertEqual(["destructive-command"], [finding.code for finding in caught.exception.findings])
        self.assertIn("Refused Command", run_sandboxed_command.render_refusal(caught.exception))

    def test_external_send_command_is_refused_without_human_confirmation(self) -> None:
        with self.assertRaises(run_sandboxed_command.PolicyRefusal) as caught:
            run_sandboxed_command.run_policy_command(["gh", "pr", "comment", "1", "--body", "ship it"])

        self.assertEqual(["externally-visible-command"], [finding.code for finding in caught.exception.findings])

    def test_sensitive_command_can_run_with_human_confirmation_ref(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "tool-outputs"
            result = run_sandboxed_command.run_policy_command(
                ["env"],
                output_dir=output_dir,
                slug="confirmed-env",
                human_confirmation_ref="manual-review:TEST-123",
            )

            self.assertEqual(result.exit_code, 0)
            self.assertEqual(["sensitive-output"], result.blocking_findings)
            self.assertEqual("manual-review:TEST-123", result.human_confirmation_ref)

    def test_timeout_kills_process_and_preserves_partial_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "tool-outputs"
            result = run_sandboxed_command.run_policy_command(
                [
                    sys.executable,
                    "-c",
                    "import time; print('before-timeout', flush=True); time.sleep(5)",
                ],
                output_dir=output_dir,
                slug="timeout",
                timeout_seconds=1,
            )

            self.assertEqual(result.exit_code, run_sandboxed_command.TIMEOUT_EXIT_CODE)
            self.assertTrue(result.timed_out)
            self.assertIn("before-timeout", (ROOT / result.stdout_artifact_path).read_text(encoding="utf-8"))

    def test_cli_returns_refusal_code_for_blocked_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "run_sandboxed_command.py"),
                    "--output-dir",
                    str(Path(tmp) / "tool-outputs"),
                    "--",
                    "rm",
                    "-rf",
                    "build/cache",
                ],
                cwd=Path(tmp),
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, run_sandboxed_command.REFUSED_EXIT_CODE)
            self.assertIn("Local Execution Policy Wrapper Refused Command", result.stdout)
            self.assertIn("execution: not run", result.stdout)


if __name__ == "__main__":
    unittest.main()
