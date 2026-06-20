from __future__ import annotations

import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import report_pr_checks  # noqa: E402
import start_pr_repair_worktree  # noqa: E402


class PrRepairWorktreeTest(unittest.TestCase):
    def test_pr_url_token_is_extracted(self) -> None:
        token = start_pr_repair_worktree.pr_token("https://github.com/example/project/pull/42")

        self.assertEqual(token, "42")

    def test_dry_run_prints_plan_without_fetching(self) -> None:
        calls: list[list[str]] = []

        def fake_run(args: list[str], cwd: Path = start_pr_repair_worktree.ROOT) -> CompletedProcess[str]:
            calls.append(args)
            if args[:3] == ["gh", "repo", "view"]:
                return CompletedProcess(args, 0, '{"nameWithOwner":"example/project"}', "")
            if args[:3] == ["gh", "pr", "view"]:
                return CompletedProcess(
                    args,
                    0,
                    (
                        '{"number":42,"url":"https://github.com/example/project/pull/42",'
                        '"headRefName":"codex/fix-ci","baseRefName":"main",'
                        '"headRepository":{"nameWithOwner":"example/project"}}'
                    ),
                    "",
                )
            self.fail(f"unexpected command: {args}")

        output = io.StringIO()
        with patch("start_pr_repair_worktree.run", side_effect=fake_run), redirect_stdout(output):
            exit_code = start_pr_repair_worktree.main(["42", "--dry-run"])

        self.assertEqual(exit_code, 0)
        self.assertIn("git push origin HEAD:codex/fix-ci", output.getvalue())
        self.assertFalse(any(call[:2] == ["git", "fetch"] for call in calls))

    def test_default_target_strips_existing_pr_suffix(self) -> None:
        target = start_pr_repair_worktree.default_target_dir(12, root=Path("D:/repo/project-pr9"))

        self.assertEqual(target, Path("D:/repo/project-pr12"))


class PrChecksReportTest(unittest.TestCase):
    def test_build_report_summarizes_check_rollup(self) -> None:
        def fake_run(args: list[str]) -> CompletedProcess[str]:
            if args[:3] == ["gh", "pr", "view"]:
                return CompletedProcess(
                    args,
                    0,
                    (
                        '{"number":7,"url":"https://github.com/example/project/pull/7",'
                        '"state":"OPEN","isDraft":false,"headRefName":"codex/change",'
                        '"baseRefName":"main","mergeStateStatus":"CLEAN","reviewDecision":"",'
                        '"statusCheckRollup":['
                        '{"name":"governance","status":"COMPLETED","conclusion":"SUCCESS","url":"https://ci/1"},'
                        '{"name":"smoke","status":"COMPLETED","conclusion":"FAILURE","url":"https://ci/2"},'
                        '{"name":"windows-hook-runtime","status":"IN_PROGRESS","conclusion":""}'
                        "]}"
                    ),
                    "",
                )
            self.fail(f"unexpected command: {args}")

        with patch("report_pr_checks.run", side_effect=fake_run):
            report = report_pr_checks.build_report("7", "example/project")

        self.assertTrue(report.checks_available)
        self.assertEqual(report.number, 7)
        self.assertEqual([report_pr_checks.check_bucket(check) for check in report.checks], ["passed", "failed", "pending"])

    def test_permission_limited_check_rollup_falls_back_to_metadata(self) -> None:
        def fake_run(args: list[str]) -> CompletedProcess[str]:
            fields = args[-1]
            if "statusCheckRollup" in fields:
                return CompletedProcess(
                    args,
                    1,
                    "",
                    (
                        "GraphQL: Resource not accessible by integration "
                        "(repository.pullRequest.commits.nodes.0.commit.statusCheckRollup)"
                    ),
                )
            return CompletedProcess(
                args,
                0,
                (
                    '{"number":7,"url":"https://github.com/example/project/pull/7",'
                    '"state":"OPEN","isDraft":true,"headRefName":"codex/change",'
                    '"baseRefName":"main","mergeStateStatus":"UNKNOWN","reviewDecision":""}'
                ),
                "",
            )

        with patch("report_pr_checks.run", side_effect=fake_run):
            report = report_pr_checks.build_report("7", "example/project")

        self.assertFalse(report.checks_available)
        self.assertEqual(report.notes, [report_pr_checks.CHECK_ROLLUP_PERMISSION_NOTE])


if __name__ == "__main__":
    unittest.main()
