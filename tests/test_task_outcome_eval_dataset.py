from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_task_outcome_eval_dataset  # noqa: E402
import run_task_outcome_eval_dataset  # noqa: E402


class TaskOutcomeEvalDatasetTest(unittest.TestCase):
    def test_repository_dataset_is_valid(self) -> None:
        errors: list[str] = []
        items = check_task_outcome_eval_dataset.load_items(check_task_outcome_eval_dataset.DEFAULT_DATASET, errors)
        for line_no, item in items:
            check_task_outcome_eval_dataset.validate_item(line_no, item, errors)
        self.assertEqual(errors, [])

    def test_runner_dry_run_reports_cost_proxies(self) -> None:
        items, errors = run_task_outcome_eval_dataset.load_items(run_task_outcome_eval_dataset.DEFAULT_DATASET)
        self.assertEqual(errors, [])
        result = run_task_outcome_eval_dataset.run_item(items[0], dry_run=True, timeout=30)

        self.assertEqual(result.task_outcome, "not-run")
        self.assertGreater(result.command_count, 0)
        self.assertEqual(result.timeout_budget_seconds, result.command_count * 30)
        self.assertEqual(result.overreach, "bounded")
        self.assertEqual(result.checks[0].observed_signal, "not-run")
        self.assertTrue(result.expected_changed_surface)
        self.assertTrue(result.expected_command_class)

    def test_runner_downgrades_pass_when_output_contains_warning_signal(self) -> None:
        with patch.object(
            run_task_outcome_eval_dataset.subprocess,
            "run",
            return_value=subprocess.CompletedProcess(
                args=["fake-check"],
                returncode=0,
                stdout="Warnings:\n- bounded context warning\n",
                stderr="",
            ),
        ):
            result = run_task_outcome_eval_dataset.run_check(
                "python3 fake_check.py",
                "pass",
                dry_run=False,
                timeout=30,
            )

        self.assertEqual(result.observed_signal, "warn")
        self.assertEqual(result.grade, "warn")

    def test_runner_detects_review_signal_from_stderr_list_item(self) -> None:
        with patch.object(
            run_task_outcome_eval_dataset.subprocess,
            "run",
            return_value=subprocess.CompletedProcess(
                args=["fake-check"],
                returncode=0,
                stdout="",
                stderr="- REVIEW REQUIRED: confirm remote boundary\n",
            ),
        ):
            result = run_task_outcome_eval_dataset.run_check(
                "python3 fake_check.py",
                "pass",
                dry_run=False,
                timeout=30,
            )

        self.assertEqual(result.observed_signal, "review-required")
        self.assertEqual(result.grade, "review-required")

    def test_runner_detects_multiple_warning_signal_forms(self) -> None:
        with patch.object(
            run_task_outcome_eval_dataset.subprocess,
            "run",
            return_value=subprocess.CompletedProcess(
                args=["fake-check"],
                returncode=0,
                stdout="warning-only: context budget\nWARN: trace boundary\n",
                stderr="",
            ),
        ):
            result = run_task_outcome_eval_dataset.run_check(
                "python3 fake_check.py",
                "pass",
                dry_run=False,
                timeout=30,
            )

        self.assertEqual(result.observed_signal, "warn")
        self.assertEqual(result.grade, "warn")

    def test_runner_write_output_creates_parent_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            output_path = Path(tempdir) / "nested" / "result.json"
            payload = {
                "dataset_path": "docs/ai/evals/task-outcome-evals.jsonl",
                "recorded_at": "2026-06-01T00:00:00Z",
                "dry_run": False,
                "selected_count": 1,
                "results": [],
            }

            run_task_outcome_eval_dataset.write_output(str(output_path), payload)

            self.assertTrue(output_path.exists())
            self.assertEqual(json.loads(output_path.read_text(encoding="utf-8")), payload)

    def test_runner_does_not_treat_plain_result_fields_as_review_signal(self) -> None:
        with patch.object(
            run_task_outcome_eval_dataset.subprocess,
            "run",
            return_value=subprocess.CompletedProcess(
                args=["fake-runner"],
                returncode=0,
                stdout='TOE-003: pass | guardrail=review-required | resume=not-applicable\n',
                stderr="",
            ),
        ):
            result = run_task_outcome_eval_dataset.run_check(
                "python3 fake_runner.py",
                "pass",
                dry_run=False,
                timeout=30,
            )

        self.assertEqual(result.observed_signal, "pass")
        self.assertEqual(result.grade, "pass")

    def test_dataset_validator_rejects_unknown_expected_outcome(self) -> None:
        errors: list[str] = []
        item = {
            "id": "TOE-999-invalid",
            "title": "Invalid outcome",
            "benchmark_group": "simple-fix",
            "task_prompt": "invalid",
            "expected_artifacts": ["scripts/check_task_outcome_eval_dataset.py"],
            "expected_changed_surface": ["scripts"],
            "expected_command_class": "eval-check",
            "overreach_expectation": "bounded",
            "resume_stability_expectation": "not-applicable",
            "guardrail_posture_expectation": "not-expected",
            "expected_checks": [
                {
                    "command": "python3 tests/test_task_outcome_eval_dataset.py",
                    "expected_outcome": "maybe",
                    "rationale": "invalid outcome",
                }
            ],
            "scorecard": {
                "resume_stability": "not-applicable",
                "guardrail_posture": "not-expected",
                "overreach_must_stay_bounded": True,
            },
            "risk_tags": ["verification-harness"],
            "notes": "invalid",
        }

        check_task_outcome_eval_dataset.validate_item(1, item, errors)

        self.assertTrue(any("expected_outcome must be one of" in error for error in errors))

    def test_dataset_validator_allows_repo_local_python_interpreter(self) -> None:
        errors: list[str] = []

        check_task_outcome_eval_dataset.validate_command(
            ".codex/.venv/bin/python tests/test_task_outcome_eval_dataset.py",
            "demo command",
            errors,
        )

        self.assertEqual([], errors)

    def test_runner_payload_aggregate_counts_blocks_resume_and_guardrail(self) -> None:
        results = [
            run_task_outcome_eval_dataset.OutcomeResult(
                id="TOE-pass",
                title="pass",
                benchmark_group="simple-fix",
                expected_command_class="focused-regression",
                expected_changed_surface=["scripts"],
                task_outcome="pass",
                overreach="bounded",
                resume_stability="not-applicable",
                guardrail_posture="not-expected",
                command_count=1,
                timeout_budget_seconds=30,
                checks=[],
            ),
            run_task_outcome_eval_dataset.OutcomeResult(
                id="TOE-review",
                title="review",
                benchmark_group="resume-durability",
                expected_command_class="runtime-check",
                expected_changed_surface=["runtime"],
                task_outcome="review-required",
                overreach="bounded",
                resume_stability="required",
                guardrail_posture="review-required",
                command_count=1,
                timeout_budget_seconds=30,
                checks=[],
            ),
        ]

        counts = run_task_outcome_eval_dataset.aggregate_counts(results)

        self.assertEqual(counts["pass_count"], 1)
        self.assertEqual(counts["review_required_count"], 1)
        self.assertEqual(counts["blocked_by_resume"], 1)
        self.assertEqual(counts["blocked_by_guardrail"], 1)


if __name__ == "__main__":
    unittest.main()
