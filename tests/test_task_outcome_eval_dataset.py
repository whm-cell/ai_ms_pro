from __future__ import annotations

import sys
import unittest
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


if __name__ == "__main__":
    unittest.main()
