from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_reuse_retirement  # noqa: E402


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def harness_config(body: str) -> str:
    return f"[reuse_retirement]\n{body}\n"


class ReuseRetirementTest(unittest.TestCase):
    def test_missing_config_is_disabled_noop(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = check_reuse_retirement.build_report(Path(tmp), files=("scripts/new_tool.py",))

        self.assertFalse(report.enabled)
        self.assertEqual(report.findings, [])

    def test_invalid_config_reports_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / ".codex" / "harness.toml", "[reuse_retirement]\nenabled = \"yes\"\n")
            report = check_reuse_retirement.build_report(root, files=("scripts/new_tool.py",))

        self.assertIn("reuse_retirement.enabled must be a boolean", report.errors)

    def test_large_new_file_reports_reuse_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / ".codex" / "harness.toml",
                harness_config(
                    "enabled = true\n"
                    'scan_roots = ["scripts"]\n'
                    "new_file_min_lines = 3\n"
                    "reuse_score_threshold = 2\n"
                    "max_candidates = 3\n"
                ),
            )
            write(
                root / "scripts" / "customer_profile_lib.py",
                "def load_customer_profile():\n    return {}\n",
            )
            write(
                root / "scripts" / "check_customer_profile.py",
                "def load_customer_profile():\n    return {}\n\n"
                "def check_customer_profile():\n    return True\n",
            )

            report = check_reuse_retirement.build_report(
                root,
                files=("scripts/check_customer_profile.py",),
            )

        self.assertEqual(report.errors, [])
        self.assertEqual(report.findings[0].code, "reuse-review-candidate")
        self.assertIn("scripts/customer_profile_lib.py", report.findings[0].candidates)

    def test_changed_replacement_reports_retirement_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / ".codex" / "harness.toml",
                harness_config(
                    "enabled = true\n"
                    'scan_roots = ["scripts"]\n'
                    "new_file_min_lines = 50\n"
                    "reuse_score_threshold = 10\n"
                    'retirement_markers = ["legacy", "mock", "old"]\n'
                ),
            )
            write(root / "scripts" / "legacy_customer_profile_mock.py", "def load_customer_profile():\n    return {}\n")
            write(root / "scripts" / "customer_profile_adapter.py", "def load_customer_profile():\n    return {}\n")

            report = check_reuse_retirement.build_report(
                root,
                files=("scripts/customer_profile_adapter.py",),
            )

        self.assertEqual(report.errors, [])
        self.assertEqual(report.findings[0].code, "retirement-review-candidate")
        self.assertIn("scripts/legacy_customer_profile_mock.py", report.findings[0].candidates)

    def test_default_discovery_includes_untracked_code_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(
                ["git", "init"],
                cwd=root,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            write(
                root / ".codex" / "harness.toml",
                harness_config(
                    "enabled = true\n"
                    'scan_roots = ["scripts"]\n'
                    "new_file_min_lines = 3\n"
                    "reuse_score_threshold = 2\n"
                ),
            )
            write(root / "scripts" / "shared_profile_lib.py", "def load_profile():\n    return {}\n")
            write(
                root / "scripts" / "check_profile.py",
                "def load_profile():\n    return {}\n\n"
                "def check_profile():\n    return True\n",
            )

            report = check_reuse_retirement.build_report(root)

        self.assertIn("scripts/check_profile.py", report.changed_files)
        self.assertTrue(any(item.path == "scripts/check_profile.py" for item in report.findings))

    def test_strict_exit_code_only_fails_on_findings_or_errors(self) -> None:
        clean = check_reuse_retirement.ReuseRetirementReport(True, [], 0, [], [])
        dirty = check_reuse_retirement.ReuseRetirementReport(
            True,
            ["scripts/new.py"],
            1,
            [
                check_reuse_retirement.ReuseRetirementFinding(
                    "scripts/new.py",
                    1,
                    "reuse-review-candidate",
                    "review",
                )
            ],
            [],
        )

        self.assertNotIn("REVIEW:", check_reuse_retirement.render_report(clean))
        self.assertIn("REVIEW:", check_reuse_retirement.render_report(dirty))
        self.assertEqual(check_reuse_retirement.exit_code(clean, strict=True), 0)
        self.assertEqual(check_reuse_retirement.exit_code(dirty, strict=False), 0)
        self.assertEqual(check_reuse_retirement.exit_code(dirty, strict=True), 1)


if __name__ == "__main__":
    unittest.main()
