from __future__ import annotations

import json
import tempfile
import sys
import unittest
from unittest.mock import patch
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import summarize_harness_capabilities  # noqa: E402


class SummarizeHarnessCapabilitiesTest(unittest.TestCase):
    def test_summary_contains_expected_top_level_metrics(self) -> None:
        summary = summarize_harness_capabilities.build_summary()

        self.assertIn("durability_coverage", summary)
        self.assertIn("verified_interop_coverage", summary)
        self.assertIn("task_eval_pass_rate", summary)
        self.assertIn("high_impact_guardrail_confirmation_coverage", summary)

    def test_summary_uses_recorded_at_for_latest_artifact_selection(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            snapshot_dir = root / "execution-snapshots"
            trace_dir = root / "trace-interop"
            task_dir = root / "task-outcome-evals"
            gap_path = root / "gap.jsonl"
            redteam_path = root / "redteam.jsonl"
            snapshot_dir.mkdir()
            trace_dir.mkdir()
            task_dir.mkdir()
            (task_dir / "nested").mkdir()
            gap_path.write_text("", encoding="utf-8")
            redteam_path.write_text(
                json.dumps(
                    {
                        "schema_version": "agentic-red-team-sample/v1",
                        "id": "REDTEAM-SAMPLE-2026-06-01-human-confirmation-real",
                        "sampled_at": "2026-06-01",
                        "risk_family": "human-confirmation",
                        "source_type": "real-incident",
                        "outcome": "accepted",
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )

            (snapshot_dir / "zzz-old.json").write_text(
                json.dumps({"recorded_at": "2026-06-01T00:00:00Z", "state": "resumable"}, ensure_ascii=False),
                encoding="utf-8",
            )
            (snapshot_dir / "aaa-new.json").write_text(
                json.dumps(
                    {
                        "recorded_at": "2026-06-01T01:00:00Z",
                        "state": "paused",
                        "resume_ready": False,
                        "resume_blockers": ["missing-transcript-reference"],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (trace_dir / "old.json").write_text(
                json.dumps({"recorded_at": "2026-06-01T00:00:00Z", "capability_level": "local-only"}, ensure_ascii=False),
                encoding="utf-8",
            )
            (trace_dir / "new.json").write_text(
                json.dumps(
                    {
                        "recorded_at": "2026-06-01T02:00:00Z",
                        "capability_level": "pilot-remote",
                        "endpoint_scope": "external-test-endpoint",
                        "network_exported": True,
                        "remote_status": {"ok": False, "http_status": 503},
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (task_dir / "nested" / "task.json").write_text(
                json.dumps(
                    {
                        "recorded_at": "2026-06-01T03:00:00Z",
                        "results": [
                            {"task_outcome": "pass"},
                            {
                                "task_outcome": "review-required",
                                "benchmark_group": "resume-durability",
                                "resume_stability": "required",
                                "guardrail_posture": "review-required",
                            },
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            with (
                patch.object(summarize_harness_capabilities, "EXECUTION_SNAPSHOT_DIR", snapshot_dir),
                patch.object(summarize_harness_capabilities, "TRACE_INTEROP_REPORT_DIR", trace_dir),
                patch.object(summarize_harness_capabilities, "TASK_OUTCOME_RESULT_DIR", task_dir),
                patch.object(summarize_harness_capabilities, "GAP_EVIDENCE_PATH", gap_path),
                patch.object(summarize_harness_capabilities, "REDTEAM_PATH", redteam_path),
            ):
                summary = summarize_harness_capabilities.build_summary()

        self.assertEqual(summary["durability_coverage"]["latest_state"], "paused")
        self.assertEqual(summary["durability_coverage"]["blocked_resume_count"], 1)
        self.assertEqual(summary["durability_coverage"]["latest_blockers"], ["missing-transcript-reference"])
        self.assertEqual(summary["verified_interop_coverage"]["latest_capability_level"], "pilot-remote")
        self.assertEqual(summary["verified_interop_coverage"]["latest_endpoint_scope"], "external-test-endpoint")
        self.assertEqual(summary["verified_interop_coverage"]["latest_failure_mode"], "remote-status-not-ok")
        self.assertEqual(summary["task_eval_pass_rate"]["latest_result_pass_rate"], "1/2")
        self.assertEqual(summary["task_eval_pass_rate"]["latest_outcome_breakdown"]["review-required"], 1)
        self.assertEqual(summary["task_eval_pass_rate"]["blocked_reason_summary"]["blocked_by_resume"], 1)
        self.assertEqual(
            summary["high_impact_guardrail_confirmation_coverage"]["accepted_real_confirmation_samples"],
            1,
        )


if __name__ == "__main__":
    unittest.main()
