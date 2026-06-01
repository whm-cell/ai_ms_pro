from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ai_governance_next_best_work as next_best_work  # noqa: E402


class NextBestWorkReviewTest(unittest.TestCase):
    def warning_for(self, text: str) -> list[str]:
        with tempfile.TemporaryDirectory() as tempdir:
            path = Path(tempdir) / "handoff.md"
            path.write_text(text, encoding="utf-8")
            return next_best_work.next_best_work_review_warnings([path])

    def test_completed_doc_without_review_warns(self) -> None:
        warnings = self.warning_for("# Handoff\n\n状态：完成\n")

        self.assertEqual(len(warnings), 1)
        self.assertIn("Next Best Work Review", warnings[0])

    def test_completed_doc_with_review_does_not_warn(self) -> None:
        warnings = self.warning_for("# Handoff\n\n状态：完成\n\n## 下一步选择判断\n\n- Decision：continue\n")

        self.assertEqual(warnings, [])

    def test_in_progress_doc_without_review_does_not_warn(self) -> None:
        warnings = self.warning_for("# Handoff\n\n状态：接力中\n\n## 当前未完成项\n\n- Continue.\n")

        self.assertEqual(warnings, [])

    def test_scope_change_signal_without_review_warns(self) -> None:
        warnings = self.warning_for("# Status\n\n状态：进行中\n\nDecision: pivot because planned work is stale.\n")

        self.assertEqual(len(warnings), 1)


if __name__ == "__main__":
    unittest.main()
