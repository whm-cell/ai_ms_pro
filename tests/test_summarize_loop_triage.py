from __future__ import annotations

from types import SimpleNamespace
import sys
import unittest
from unittest.mock import patch
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import summarize_loop_triage  # noqa: E402


def capability_summary(
    *,
    failed_task_outcomes: int = 0,
    blocked_by_resume: int = 0,
    verified_remote_reports: int = 0,
    high_impact_samples: int = 0,
    blocked_resume_count: int = 0,
) -> dict[str, object]:
    return {
        "summary_boundary": "artifact-backed-local-runtime",
        "durability_coverage": {
            "snapshot_count": 2,
            "blocked_resume_count": blocked_resume_count,
        },
        "verified_interop_coverage": {
            "verified_remote_reports": verified_remote_reports,
        },
        "task_eval_pass_rate": {
            "latest_outcome_breakdown": {"fail": failed_task_outcomes},
            "blocked_reason_summary": {"blocked_by_resume": blocked_by_resume},
        },
        "high_impact_guardrail_confirmation_coverage": {
            "accepted_real_confirmation_samples": high_impact_samples,
        },
    }


class SummarizeLoopTriageTest(unittest.TestCase):
    def test_report_declares_no_write_loop_boundary(self) -> None:
        with (
            patch.object(
                summarize_loop_triage.summarize_harness_capabilities,
                "build_summary",
                return_value=capability_summary(verified_remote_reports=1, high_impact_samples=2),
            ),
            patch.object(summarize_loop_triage.plan_harness_sample_collection, "build_queue", return_value=[]),
        ):
            report = summarize_loop_triage.build_report()

        self.assertEqual(report["schema_version"], "bounded-loop-triage/v1")
        self.assertEqual(report["loop_mode"], "read-only-triage")
        self.assertEqual(report["decision"], "monitor-only")
        self.assertIn("no automatic code changes", report["no_claims"])
        self.assertIn("no external effect without explicit confirmation", report["no_claims"])

    def test_capability_signals_create_prioritized_actions(self) -> None:
        with (
            patch.object(
                summarize_loop_triage.summarize_harness_capabilities,
                "build_summary",
                return_value=capability_summary(
                    failed_task_outcomes=1,
                    blocked_by_resume=1,
                    verified_remote_reports=0,
                    high_impact_samples=1,
                ),
            ),
            patch.object(summarize_loop_triage.plan_harness_sample_collection, "build_queue", return_value=[]),
        ):
            report = summarize_loop_triage.build_report(limit=10)

        self.assertEqual(report["decision"], "needs-operator-selection")
        titles = [item["title"] for item in report["next_actions"]]
        self.assertIn("Review failed task outcome evals", titles)
        self.assertIn("Prepare remote interop capture review", titles)
        self.assertIn("Keep high-impact confirmation sample lane visible", titles)

    def test_queue_items_become_capture_lane_actions(self) -> None:
        queue_item = SimpleNamespace(
            gap_id="GAP-RUNTIME-STAGE-CHECKPOINT-RESUME",
            priority="P1",
            readiness="needs-more-real-samples",
            capture_gate="requires-cross-task-resume",
            ledger_action="append-new-pending-slot",
            target_artifact="docs/ai/checkpoints/resume-samples.jsonl",
        )
        with (
            patch.object(
                summarize_loop_triage.summarize_harness_capabilities,
                "build_summary",
                return_value=capability_summary(verified_remote_reports=1, high_impact_samples=2),
            ),
            patch.object(summarize_loop_triage.plan_harness_sample_collection, "build_queue", return_value=[queue_item]),
        ):
            report = summarize_loop_triage.build_report(limit=5)

        self.assertEqual(report["queue_summary"]["actionable_without_review_ready_pending"], 1)
        self.assertEqual(report["queue_summary"]["by_capture_gate"], {"requires-cross-task-resume": 1})
        action = report["next_actions"][0]
        self.assertEqual(action["priority"], "P1")
        self.assertIn("GAP-RUNTIME-STAGE-CHECKPOINT-RESUME", action["recommended_command"])
        self.assertEqual(action["boundary"], "operator-reviewed; no automatic write or external send")


if __name__ == "__main__":
    unittest.main()
