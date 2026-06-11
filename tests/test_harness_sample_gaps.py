from __future__ import annotations

import sys
import unittest
from io import StringIO
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import collect_harness_sample_gaps  # noqa: E402


class HarnessSampleGapsTest(unittest.TestCase):
    def test_filters_by_area(self) -> None:
        gaps = collect_harness_sample_gaps.select_gaps({"workflow-skills"})

        self.assertTrue(gaps)
        self.assertTrue(all(gap.area == "workflow-skills" for gap in gaps))

    def test_markdown_mentions_pending_real_samples(self) -> None:
        with mock.patch("sys.stdout", new=StringIO()) as output:
            collect_harness_sample_gaps.emit_markdown(list(collect_harness_sample_gaps.GAPS))

        text = output.getvalue()
        self.assertIn("GAP-GUARDRAIL-CONFIRMATION", text)
        self.assertIn("Current evidence", text)
        self.assertIn("GAP-GUARDRAIL-PREFLIGHT-WARNING", text)
        self.assertIn("GAP-SEC-CONTROL-MATRIX-BURNIN", text)
        self.assertIn("GAP-WORKFLOW-TASK-PROFILE-AUDIT", text)
        self.assertIn("GAP-RUNTIME-STAGE-CHECKPOINT-RESUME", text)
        self.assertIn("GAP-RUNTIME-LOOP-SCOPE-WARNING", text)
        self.assertIn("GAP-TRACE-OTLP-PILOT-BURNIN", text)
        self.assertIn("GAP-TRACE-LOCAL-SUMMARY-BURNIN", text)
        self.assertIn("pending-real-sample", text)

    def test_runtime_gap_current_evidence_is_sample_backed(self) -> None:
        checkpoint_gap = next(
            gap for gap in collect_harness_sample_gaps.GAPS if gap.id == "GAP-RUNTIME-STAGE-CHECKPOINT-RESUME"
        )
        loop_gap = next(gap for gap in collect_harness_sample_gaps.GAPS if gap.id == "GAP-RUNTIME-LOOP-SCOPE-WARNING")

        checkpoint_evidence = collect_harness_sample_gaps.current_evidence_for(checkpoint_gap)
        loop_evidence = collect_harness_sample_gaps.current_evidence_for(loop_gap)

        self.assertIn("accepted resume samples: 2", checkpoint_evidence)
        self.assertIn("accepted cross-task samples: 0", checkpoint_evidence)
        self.assertIn("accepted real warning samples: 0", loop_evidence)

    def test_json_payload_includes_current_evidence(self) -> None:
        gap = next(gap for gap in collect_harness_sample_gaps.GAPS if gap.id == "GAP-TRACE-LOCAL-SUMMARY-BURNIN")

        payload = collect_harness_sample_gaps.gap_dict(gap)

        self.assertIn("current_evidence", payload)
        self.assertIn("accepted real local reports: 3", payload["current_evidence"])
        self.assertIn("accepted real task classes: 1", payload["current_evidence"])
        self.assertIn("accepted real task-class details: harness-hardening=3", payload["current_evidence"])

    def test_generic_gap_evidence_counts_untracked_gaps(self) -> None:
        security_gap = next(gap for gap in collect_harness_sample_gaps.GAPS if gap.id == "GAP-SEC-SCHEDULED-RUN")
        otlp_gap = next(gap for gap in collect_harness_sample_gaps.GAPS if gap.id == "GAP-TRACE-OTLP-PILOT-BURNIN")
        source_gap = next(gap for gap in collect_harness_sample_gaps.GAPS if gap.id == "GAP-GUARDRAIL-SOURCE-BOUNDARY")
        control_gap = next(gap for gap in collect_harness_sample_gaps.GAPS if gap.id == "GAP-SEC-CONTROL-MATRIX-BURNIN")

        security_evidence = collect_harness_sample_gaps.current_evidence_for(security_gap)
        otlp_evidence = collect_harness_sample_gaps.current_evidence_for(otlp_gap)
        source_evidence = collect_harness_sample_gaps.current_evidence_for(source_gap)
        control_evidence = collect_harness_sample_gaps.current_evidence_for(control_gap)

        self.assertIn("generic ledger records: 0", security_evidence)
        self.assertIn("generic ledger records: 1", otlp_evidence)
        self.assertIn("accepted real/local samples: real=0, local=1", otlp_evidence)
        self.assertIn("generic ledger records: 2", source_evidence)
        self.assertIn("accepted real/local samples: real=2, local=0", source_evidence)
        self.assertIn("generic ledger records: 2", control_evidence)
        self.assertIn("accepted real/local samples: real=2, local=0", control_evidence)
        self.assertEqual("accepted-local-sample", otlp_gap.status)

    def test_agentic_red_team_gap_ids_are_registered(self) -> None:
        gap_ids = {gap.id for gap in collect_harness_sample_gaps.GAPS}

        self.assertIn("GAP-AGENTIC-TOOL-SQUATTING", gap_ids)
        self.assertIn("GAP-AGENTIC-MEMORY-POISONING", gap_ids)
        self.assertIn("GAP-AGENTIC-A2A-HANDOFF", gap_ids)
        self.assertIn("GAP-AGENTIC-CASCADE-STOP", gap_ids)
        self.assertIn("GAP-AGENTIC-SANDBOX-HONESTY", gap_ids)

    def test_agentic_red_team_current_evidence_is_risk_specific(self) -> None:
        cascade_gap = next(gap for gap in collect_harness_sample_gaps.GAPS if gap.id == "GAP-AGENTIC-CASCADE-STOP")
        sandbox_gap = next(gap for gap in collect_harness_sample_gaps.GAPS if gap.id == "GAP-AGENTIC-SANDBOX-HONESTY")

        cascade_evidence = collect_harness_sample_gaps.current_evidence_for(cascade_gap)
        sandbox_evidence = collect_harness_sample_gaps.current_evidence_for(sandbox_gap)

        self.assertIn("accepted real red-team incidents for cascade-autonomy: 0", cascade_evidence)
        self.assertIn("accepted real red-team incidents for sandbox-claim-honesty: 2", sandbox_evidence)

    def test_agentic_red_team_gaps_target_control_matrix(self) -> None:
        gaps = collect_harness_sample_gaps.select_gaps({"agentic-red-team"})

        self.assertEqual(5, len(gaps))
        self.assertTrue(
            all("docs/ai/security/agentic-control-matrix.md" in gap.target_docs for gap in gaps)
        )
        self.assertTrue(
            all("docs/ai/security/agentic-red-team-samples.jsonl" in gap.target_docs for gap in gaps)
        )
        self.assertTrue(all(gap.status in {"pending-real-sample", "pending-more-samples", "future-work"} for gap in gaps))

    def test_runtime_durability_gap_targets_checkpoints(self) -> None:
        gaps = collect_harness_sample_gaps.select_gaps({"runtime-durability"})
        gap_ids = {gap.id for gap in gaps}

        self.assertEqual(2, len(gaps))
        self.assertIn("GAP-RUNTIME-STAGE-CHECKPOINT-RESUME", gap_ids)
        self.assertIn("GAP-RUNTIME-LOOP-SCOPE-WARNING", gap_ids)
        checkpoint_gap = next(gap for gap in gaps if gap.id == "GAP-RUNTIME-STAGE-CHECKPOINT-RESUME")
        loop_gap = next(gap for gap in gaps if gap.id == "GAP-RUNTIME-LOOP-SCOPE-WARNING")
        self.assertIn("docs/ai/checkpoints/stage-checkpoints.jsonl", checkpoint_gap.target_docs)
        self.assertIn("docs/ai/standards/loop-scope-monitor-samples.jsonl", loop_gap.target_docs)

    def test_trace_interop_gaps_include_local_summary_burn_in(self) -> None:
        gaps = collect_harness_sample_gaps.select_gaps({"trace-interop"})
        gap_ids = {gap.id for gap in gaps}

        self.assertIn("GAP-TRACE-LOCAL-SUMMARY-BURNIN", gap_ids)
        summary_gap = next(gap for gap in gaps if gap.id == "GAP-TRACE-LOCAL-SUMMARY-BURNIN")
        self.assertIn("docs/ai/standards/local-trace-summary-samples.jsonl", summary_gap.target_docs)
        self.assertEqual("pending-more-samples", summary_gap.status)


if __name__ == "__main__":
    unittest.main()
