from __future__ import annotations

import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_warning_sample_code_alignment as alignment  # noqa: E402


class WarningSampleCodeAlignmentTest(unittest.TestCase):
    def test_repository_alignment_is_valid(self) -> None:
        report = alignment.audit()

        self.assertTrue(report.ok, "\n".join(report.errors))
        self.assertEqual(report.preflight_hook_codes, report.preflight_emitted_codes)
        self.assertEqual(report.preflight_hook_codes, report.preflight_checker_codes)
        self.assertEqual(report.loop_hook_codes, report.loop_emitted_codes)
        self.assertEqual(report.loop_hook_codes, report.loop_checker_codes)
        self.assertIn("checkpoint", report.loop_recommendations)
        self.assertIn("inspect-repeated-command", report.loop_recommendations)

    def test_missing_preflight_checker_code_is_reported(self) -> None:
        with patch.object(
            alignment.preflight_samples,
            "FINDING_CODES",
            {"none", "destructive-command"},
        ):
            report = alignment.audit()

        self.assertFalse(report.ok)
        self.assertIn("preflight checker finding codes: missing from FINDING_CODES", "\n".join(report.errors))
        self.assertIn("external-tool-send", "\n".join(report.errors))

    def test_loop_recommendation_mapping_must_cover_each_finding(self) -> None:
        with patch.object(
            alignment.loop_hook,
            "RECOMMENDATION_BY_FINDING",
            {"repeated-command": "inspect-repeated-command"},
        ):
            report = alignment.audit()

        self.assertFalse(report.ok)
        self.assertIn("loop recommendation mapping keys: missing from RECOMMENDATION_BY_FINDING", "\n".join(report.errors))
        self.assertIn("repeated-failure", "\n".join(report.errors))

    def test_invalid_loop_recommendation_is_reported(self) -> None:
        with patch.object(
            alignment.loop_hook,
            "RECOMMENDATION_BY_FINDING",
            {
                "repeated-command": "inspect-repeated-command",
                "repeated-failure": "bad-action",
                "validation-loop": "shrink-validation",
                "prompt-churn": "narrow-task",
            },
        ):
            report = alignment.audit()

        self.assertFalse(report.ok)
        self.assertIn("not accepted by sample checker: bad-action", "\n".join(report.errors))

    def test_text_output_lists_no_errors_for_current_repo(self) -> None:
        output = io.StringIO()

        with redirect_stdout(output):
            alignment.emit_text(alignment.audit())

        text = output.getvalue()
        self.assertIn("Warning sample code alignment:", text)
        self.assertIn("ERRORS: none", text)


if __name__ == "__main__":
    unittest.main()
