from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from branch_hygiene_budget import (  # noqa: E402
    BranchHygieneBudget,
    budget_findings,
    load_branch_hygiene_budget,
    pull_request_counts,
)
from check_branch_hygiene import failed_open_pr_findings, failing_checks  # noqa: E402


class BranchHygieneBudgetTest(unittest.TestCase):
    def test_counts_codex_dependabot_and_failed_open_prs(self) -> None:
        records = [
            {"state": "OPEN", "headRefName": "codex/stage-00", "title": "[codex] Stage 00"},
            {
                "state": "OPEN",
                "headRefName": "dependabot/pip/dot-codex/tomli",
                "author": {"login": "app/dependabot"},
            },
            {"state": "CLOSED", "headRefName": "codex/old", "title": "[codex] Old"},
        ]

        counts = pull_request_counts(records, failed_open=1)

        self.assertEqual(counts.open_total, 2)
        self.assertEqual(counts.open_codex, 1)
        self.assertEqual(counts.open_dependabot, 1)
        self.assertEqual(counts.failed_open, 1)

    def test_budget_findings_warn_only_when_count_exceeds_limit(self) -> None:
        counts = pull_request_counts(
            [
                {"state": "OPEN", "headRefName": "codex/a"},
                {"state": "OPEN", "headRefName": "codex/b"},
            ],
            failed_open=0,
        )
        budget = BranchHygieneBudget(
            max_open_total_prs=10,
            max_open_codex_prs=1,
            max_open_dependabot_prs=4,
            max_failed_open_prs=0,
        )

        findings = budget_findings(counts, budget)

        self.assertEqual([finding.name for finding in findings], ["open codex PRs"])
        self.assertEqual(findings[0].count, 2)
        self.assertEqual(findings[0].limit, 1)

    def test_loads_budget_from_harness_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".codex").mkdir()
            (root / ".codex" / "harness.toml").write_text(
                """[branch_hygiene]
max_open_total_prs = 8
max_open_codex_prs = 2
max_open_dependabot_prs = 3
max_failed_open_prs = 0
""",
                encoding="utf-8",
            )

            budget = load_branch_hygiene_budget(root)

        self.assertEqual(budget.max_open_total_prs, 8)
        self.assertEqual(budget.max_open_codex_prs, 2)
        self.assertEqual(budget.max_open_dependabot_prs, 3)
        self.assertEqual(budget.max_failed_open_prs, 0)

    def test_pending_checks_are_not_failed_prs(self) -> None:
        record = {
            "statusCheckRollup": [
                {"name": "governance", "status": "IN_PROGRESS", "conclusion": ""},
                {"name": "smoke", "status": "QUEUED", "conclusion": ""},
            ]
        }

        self.assertEqual(failing_checks(record), [])

    def test_current_pr_self_checks_are_ignored(self) -> None:
        records = [
            {
                "state": "OPEN",
                "number": 9,
                "headRefName": "codex/stage-00",
                "statusCheckRollup": [{"name": "governance", "conclusion": "FAILURE"}],
            },
            {
                "state": "OPEN",
                "number": 10,
                "headRefName": "codex/other",
                "statusCheckRollup": [{"name": "governance", "conclusion": "FAILURE"}],
            },
        ]

        findings = failed_open_pr_findings(records, current_pr=9)

        self.assertEqual([finding.number for finding in findings], [10])


if __name__ == "__main__":
    unittest.main()
