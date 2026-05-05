from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_pr_touch_conflicts  # noqa: E402


class PrTouchConflictsTest(unittest.TestCase):
    def test_high_risk_overlap_blocks(self) -> None:
        conflicts = check_pr_touch_conflicts.compare_prs(
            current_pr=1,
            current_files=("AGENTS.md", "apps/site/home.tsx"),
            open_prs=(
                check_pr_touch_conflicts.PullRequest(
                    number=2,
                    title="Other governance edit",
                    url="https://example.test/pr/2",
                    head_ref="other",
                    base_ref="main",
                    files=("AGENTS.md",),
                ),
            ),
        )

        self.assertEqual(check_pr_touch_conflicts.report_status(conflicts, []), "BLOCK")
        self.assertEqual(conflicts[0].high_risk_overlap, ("AGENTS.md",))

    def test_ordinary_overlap_warns(self) -> None:
        conflicts = check_pr_touch_conflicts.compare_prs(
            current_pr=1,
            current_files=("apps/site/home.tsx",),
            open_prs=(
                check_pr_touch_conflicts.PullRequest(
                    number=2,
                    title="Other page edit",
                    url="https://example.test/pr/2",
                    head_ref="other",
                    base_ref="main",
                    files=("apps/site/home.tsx",),
                ),
            ),
        )

        self.assertEqual(check_pr_touch_conflicts.report_status(conflicts, []), "WARN")
        self.assertEqual(conflicts[0].high_risk_overlap, ())

    def test_current_pr_is_ignored(self) -> None:
        conflicts = check_pr_touch_conflicts.compare_prs(
            current_pr=1,
            current_files=("AGENTS.md",),
            open_prs=(
                check_pr_touch_conflicts.PullRequest(
                    number=1,
                    title="Current PR",
                    url="https://example.test/pr/1",
                    head_ref="current",
                    base_ref="main",
                    files=("AGENTS.md",),
                ),
            ),
        )

        self.assertEqual(conflicts, ())
        self.assertEqual(check_pr_touch_conflicts.report_status(conflicts, []), "OK")

    def test_unknown_without_overlap_is_unknown(self) -> None:
        self.assertEqual(check_pr_touch_conflicts.report_status((), ["gh unavailable"]), "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
