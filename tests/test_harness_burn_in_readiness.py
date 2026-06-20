from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_harness_burn_in_readiness as readiness  # noqa: E402
import collect_harness_sample_gaps  # noqa: E402
import harness_burn_in_readiness_routing as readiness_routing  # noqa: E402


class HarnessBurnInReadinessTest(unittest.TestCase):
    def by_gap(self, *, include_future: bool = False, include_accepted: bool = False):
        report = readiness.build_report(include_future=include_future, include_accepted=include_accepted)
        self.assertEqual([], report.errors)
        return {item.gap_id: item for item in report.items}

    def gap(self, gap_id: str) -> collect_harness_sample_gaps.SampleGap:
        return next(gap for gap in collect_harness_sample_gaps.GAPS if gap.id == gap_id)

    def test_preflight_is_ready_for_upgrade_and_loop_needs_first_warning_sample(self) -> None:
        by_gap = self.by_gap()

        self.assertEqual("ready-for-upgrade-discussion", by_gap["GAP-GUARDRAIL-PREFLIGHT-WARNING"].readiness)
        self.assertEqual(2, by_gap["GAP-GUARDRAIL-PREFLIGHT-WARNING"].accepted_count)
        self.assertEqual("upgrade-decision-review", by_gap["GAP-GUARDRAIL-PREFLIGHT-WARNING"].capture_gate)
        self.assertIn("bounded keep/promote/defer", by_gap["GAP-GUARDRAIL-PREFLIGHT-WARNING"].capture_gate_detail)
        self.assertEqual("review-upgrade-decision", by_gap["GAP-GUARDRAIL-PREFLIGHT-WARNING"].ledger_action)
        self.assertIn(
            "scripts/plan_harness_sample_collection.py --gap-id GAP-GUARDRAIL-PREFLIGHT-WARNING "
            "--ledger-action review-upgrade-decision --capture-card",
            by_gap["GAP-GUARDRAIL-PREFLIGHT-WARNING"].planner_command,
        )
        self.assertIn(
            "scripts/build_harness_sample_intake_bundle.py --gap-id GAP-GUARDRAIL-PREFLIGHT-WARNING "
            "--ledger-action review-upgrade-decision --summary",
            by_gap["GAP-GUARDRAIL-PREFLIGHT-WARNING"].intake_command,
        )
        self.assertIn(
            "scripts/check_harness_upgrade_decision_candidate.py <candidate-jsonl>",
            by_gap["GAP-GUARDRAIL-PREFLIGHT-WARNING"].lane_review_command,
        )
        self.assertEqual("needs-first-real-sample", by_gap["GAP-RUNTIME-LOOP-SCOPE-WARNING"].readiness)
        self.assertEqual("replace-placeholder-after-real-event", by_gap["GAP-RUNTIME-LOOP-SCOPE-WARNING"].capture_gate)

    def test_readiness_routing_uses_lane_specific_review_pending_intake(self) -> None:
        command = readiness_routing.intake_command_for(
            self.gap("GAP-GUARDRAIL-PREFLIGHT-WARNING"),
            "review-existing-pending-slot",
        )

        self.assertIn("--ledger-action review-existing-pending-slot", command)
        self.assertIn("--pending-state with-review-ready-pending", command)

    def test_local_trace_has_real_reports_but_still_needs_more_task_classes(self) -> None:
        item = self.by_gap()["GAP-TRACE-LOCAL-SUMMARY-BURNIN"]

        self.assertEqual("accepted real local trace summary task classes", item.source_metric)
        self.assertEqual(1, item.accepted_count)
        self.assertEqual(3, item.upgrade_discussion_target)
        self.assertEqual("needs-more-real-samples", item.readiness)
        self.assertEqual("requires-distinct-task-class-report", item.capture_gate)

    def test_task_profile_reaches_upgrade_discussion_profile_coverage(self) -> None:
        item = self.by_gap()["GAP-WORKFLOW-TASK-PROFILE-AUDIT"]

        self.assertEqual("accepted real task-profile classes", item.source_metric)
        self.assertEqual(3, item.accepted_count)
        self.assertEqual(3, item.upgrade_discussion_target)
        self.assertEqual("ready-for-upgrade-discussion", item.readiness)
        self.assertEqual("keep-advisory", item.upgrade_decision)
        self.assertEqual("upgrade-decision-review", item.capture_gate)
        self.assertEqual(
            "docs/ai/standards/harness-upgrade-decisions.jsonl:1",
            item.upgrade_decision_ref,
        )
        self.assertIn("more real tasks outside", "\n".join(item.next_evidence_needed))
        self.assertIn("Upgrade decision recorded as keep-advisory", item.next_action)
        self.assertEqual("review-upgrade-decision", item.ledger_action)
        self.assertEqual("docs/ai/standards/harness-upgrade-decisions.jsonl", item.target_artifact)
        self.assertIn("--ledger-action review-upgrade-decision", item.planner_command)
        self.assertIn("--ledger-action review-upgrade-decision", item.intake_command)
        self.assertIn("scripts/check_harness_upgrade_decision_candidate.py <candidate-jsonl>", item.lane_review_command)

    def test_include_flags_expose_local_and_future_boundaries(self) -> None:
        by_gap = self.by_gap(include_future=True, include_accepted=True)

        self.assertEqual("local-sample-only", by_gap["GAP-TRACE-OTLP-PILOT-BURNIN"].readiness)
        self.assertIn("do not claim", by_gap["GAP-TRACE-OTLP-PILOT-BURNIN"].next_action)
        self.assertEqual("no-sample-collection", by_gap["GAP-TRACE-OTLP-PILOT-BURNIN"].ledger_action)
        self.assertEqual("not-applicable", by_gap["GAP-TRACE-OTLP-PILOT-BURNIN"].planner_command)
        self.assertEqual("not-applicable", by_gap["GAP-TRACE-OTLP-PILOT-BURNIN"].lane_review_command)
        self.assertEqual("needs-first-real-sample", by_gap["GAP-TRACE-REMOTE-INTEROP"].readiness)
        self.assertEqual("requires-approved-remote-interop", by_gap["GAP-TRACE-REMOTE-INTEROP"].capture_gate)
        self.assertEqual("append-new-pending-slot", by_gap["GAP-TRACE-REMOTE-INTEROP"].ledger_action)
        self.assertIn("--ledger-action append-new-pending-slot", by_gap["GAP-TRACE-REMOTE-INTEROP"].planner_command)
        self.assertIn("--ledger-action append-new-pending-slot", by_gap["GAP-TRACE-REMOTE-INTEROP"].intake_command)
        self.assertEqual(
            "docs/ai/standards/harness-sample-gap-evidence.jsonl",
            by_gap["GAP-TRACE-REMOTE-INTEROP"].target_artifact,
        )
        self.assertIn(
            "scripts/check_harness_sample_append.py <candidate-jsonl>",
            by_gap["GAP-TRACE-REMOTE-INTEROP"].lane_review_command,
        )
        self.assertIn("ADR-017", by_gap["GAP-TRACE-REMOTE-INTEROP"].capture_gate_detail)
        self.assertIn(
            "future-work contract status: approved-for-sampling",
            by_gap["GAP-TRACE-REMOTE-INTEROP"].current_evidence,
        )
        self.assertIn("future-work missing ADR refs: false", by_gap["GAP-TRACE-REMOTE-INTEROP"].current_evidence)
        remote_evidence = by_gap["GAP-TRACE-REMOTE-INTEROP"].current_evidence
        self.assertTrue(
            any("Allowed by contract record" in evidence for evidence in remote_evidence)
        )
        self.assertIn("remote interoperability", by_gap["GAP-TRACE-REMOTE-INTEROP"].next_action)
        self.assertEqual("needs-first-real-sample", by_gap["GAP-AGENTIC-CASCADE-STOP"].readiness)
        self.assertEqual("requires-approved-bounded-incident", by_gap["GAP-AGENTIC-CASCADE-STOP"].capture_gate)
        self.assertIn(
            "future-work contract status: approved-for-sampling",
            by_gap["GAP-AGENTIC-CASCADE-STOP"].current_evidence,
        )
        self.assertIn(
            "future-work missing ADR refs: false",
            by_gap["GAP-AGENTIC-CASCADE-STOP"].current_evidence,
        )
        self.assertEqual("ready-for-upgrade-discussion", by_gap["GAP-AGENTIC-SANDBOX-HONESTY"].readiness)
        self.assertEqual(2, by_gap["GAP-AGENTIC-SANDBOX-HONESTY"].accepted_count)
        self.assertEqual("keep-advisory", by_gap["GAP-AGENTIC-SANDBOX-HONESTY"].upgrade_decision)
        self.assertEqual("review-upgrade-decision", by_gap["GAP-AGENTIC-SANDBOX-HONESTY"].ledger_action)
        self.assertEqual(
            "docs/ai/standards/harness-upgrade-decisions.jsonl",
            by_gap["GAP-AGENTIC-SANDBOX-HONESTY"].target_artifact,
        )
        self.assertIn(
            "scripts/check_harness_upgrade_decision_candidate.py <candidate-jsonl>",
            by_gap["GAP-AGENTIC-SANDBOX-HONESTY"].lane_review_command,
        )
        self.assertEqual(
            "docs/ai/standards/harness-upgrade-decisions.jsonl:2",
            by_gap["GAP-AGENTIC-SANDBOX-HONESTY"].upgrade_decision_ref,
        )
        self.assertIn(
            "external-provider boundary evidence",
            "\n".join(by_gap["GAP-AGENTIC-SANDBOX-HONESTY"].next_evidence_needed),
        )
        self.assertIn(
            "accepted real red-team incidents for sandbox-claim-honesty: 2",
            by_gap["GAP-AGENTIC-SANDBOX-HONESTY"].current_evidence,
        )
        self.assertEqual("ready-for-upgrade-discussion", by_gap["GAP-GUARDRAIL-SOURCE-BOUNDARY"].readiness)
        self.assertEqual(2, by_gap["GAP-GUARDRAIL-SOURCE-BOUNDARY"].accepted_count)
        self.assertEqual("keep-advisory", by_gap["GAP-GUARDRAIL-SOURCE-BOUNDARY"].upgrade_decision)
        self.assertEqual(
            "docs/ai/standards/harness-upgrade-decisions.jsonl:3",
            by_gap["GAP-GUARDRAIL-SOURCE-BOUNDARY"].upgrade_decision_ref,
        )
        self.assertIn(
            "accepted real/local samples: real=2, local=0",
            by_gap["GAP-GUARDRAIL-SOURCE-BOUNDARY"].current_evidence,
        )
        self.assertEqual("ready-for-upgrade-discussion", by_gap["GAP-SEC-CONTROL-MATRIX-BURNIN"].readiness)
        self.assertEqual(2, by_gap["GAP-SEC-CONTROL-MATRIX-BURNIN"].accepted_count)
        self.assertEqual("keep-advisory", by_gap["GAP-SEC-CONTROL-MATRIX-BURNIN"].upgrade_decision)
        self.assertEqual(
            "docs/ai/standards/harness-upgrade-decisions.jsonl:4",
            by_gap["GAP-SEC-CONTROL-MATRIX-BURNIN"].upgrade_decision_ref,
        )
        self.assertIn(
            "accepted real/local samples: real=2, local=0",
            by_gap["GAP-SEC-CONTROL-MATRIX-BURNIN"].current_evidence,
        )

    def test_report_summarizes_not_ready_counts(self) -> None:
        report = readiness.build_report()

        self.assertGreater(report.needs_first_real_sample, 0)
        self.assertGreater(report.needs_more_real_samples, 0)
        self.assertEqual(6, report.ready_for_upgrade_discussion)
        self.assertEqual({"keep-advisory": 6}, report.upgrade_decision_counts)
        self.assertEqual(report.item_count, sum(report.capture_gate_counts.values()))
        self.assertEqual(1, report.capture_gate_counts["replace-placeholder-after-real-event"])
        self.assertEqual(6, report.capture_gate_counts["upgrade-decision-review"])
        self.assertEqual(
            {
                "GAP-RUNTIME-STAGE-CHECKPOINT-RESUME": (
                    "ledger accepted real=2; accepted cross-task resume samples=0/2"
                ),
                "GAP-TRACE-LOCAL-SUMMARY-BURNIN": (
                    "ledger accepted real=3; accepted real local trace summary task classes=1/3"
                ),
            },
            report.accepted_real_readiness_metric_deltas,
        )
        self.assertIn("GAP-GUARDRAIL-PREFLIGHT-WARNING", report.readiness_gap_ids["ready-for-upgrade-discussion"])
        self.assertEqual(
            ["GAP-GUARDRAIL-CONFIRMATION", "GAP-TRACE-LOCAL-SUMMARY-BURNIN"],
            report.readiness_gap_ids["needs-more-real-samples"],
        )
        self.assertIn("GAP-WORKFLOW-TASK-PROFILE-AUDIT", report.readiness_gap_ids["ready-for-upgrade-discussion"])
        self.assertIn("GAP-WORKFLOW-SIMPLE-SKIP", report.readiness_gap_ids["ready-for-upgrade-discussion"])
        self.assertIn("GAP-GUARDRAIL-PREFLIGHT-WARNING", report.capture_gate_gap_ids["upgrade-decision-review"])
        self.assertIn("GAP-RUNTIME-LOOP-SCOPE-WARNING", report.capture_gate_gap_ids["replace-placeholder-after-real-event"])
        self.assertIn("GAP-WORKFLOW-TASK-PROFILE-AUDIT", report.capture_gate_gap_ids["upgrade-decision-review"])
        self.assertIn("GAP-WORKFLOW-TASK-PROFILE-AUDIT", report.ready_next_evidence_needed_by_gap)
        self.assertIn(
            "profile selection disputes",
            "\n".join(report.ready_next_evidence_needed_by_gap["GAP-WORKFLOW-TASK-PROFILE-AUDIT"]),
        )
        self.assertEqual([], report.ready_without_upgrade_decision)
        self.assertTrue(any("GAP-RUNTIME-LOOP-SCOPE-WARNING" in warning for warning in report.warnings))

    def test_capture_gate_filter_limits_readiness_items(self) -> None:
        report = readiness.build_report(
            include_future=True,
            include_accepted=True,
            capture_gates={"requires-approved-remote-interop"},
        )

        self.assertEqual([], report.errors)
        self.assertEqual(("requires-approved-remote-interop",), report.capture_gate_filter)
        self.assertEqual(1, report.item_count)
        self.assertEqual({"requires-approved-remote-interop": 1}, report.capture_gate_counts)
        self.assertEqual({"requires-approved-remote-interop": ["GAP-TRACE-REMOTE-INTEROP"]}, report.capture_gate_gap_ids)
        self.assertEqual({"needs-first-real-sample": ["GAP-TRACE-REMOTE-INTEROP"]}, report.readiness_gap_ids)
        self.assertEqual("GAP-TRACE-REMOTE-INTEROP", report.items[0].gap_id)
        self.assertEqual("P3", report.items[0].priority)
        self.assertEqual("needs-first-real-sample", report.items[0].readiness)
        self.assertIn("check_harness_sample_append.py", report.items[0].lane_review_command)

    def test_readiness_filter_limits_readiness_items(self) -> None:
        report = readiness.build_report(
            include_future=True,
            include_accepted=True,
            readinesses={"needs-first-real-sample"},
        )

        self.assertEqual([], report.errors)
        self.assertEqual(("needs-first-real-sample",), report.readiness_filter)
        self.assertEqual(report.item_count, report.needs_first_real_sample)
        self.assertEqual(11, report.item_count)
        self.assertEqual(0, report.ready_for_upgrade_discussion)
        self.assertEqual(0, report.needs_more_real_samples)
        self.assertTrue(all(item.readiness == "needs-first-real-sample" for item in report.items))

    def test_readiness_filter_combines_with_area_filter(self) -> None:
        report = readiness.build_report(
            include_future=True,
            include_accepted=True,
            areas={"trace-interop"},
            readinesses={"needs-first-real-sample"},
        )

        self.assertEqual([], report.errors)
        self.assertEqual(("trace-interop",), report.area_filter)
        self.assertEqual(("needs-first-real-sample",), report.readiness_filter)
        self.assertEqual(1, report.item_count)
        self.assertEqual("GAP-TRACE-REMOTE-INTEROP", report.items[0].gap_id)

    def test_gap_id_filter_limits_readiness_items(self) -> None:
        report = readiness.build_report(
            include_future=True,
            include_accepted=True,
            gap_ids={"GAP-TRACE-REMOTE-INTEROP"},
        )

        self.assertEqual([], report.errors)
        self.assertEqual(("GAP-TRACE-REMOTE-INTEROP",), report.gap_id_filter)
        self.assertEqual(1, report.item_count)
        self.assertEqual("GAP-TRACE-REMOTE-INTEROP", report.items[0].gap_id)
        self.assertEqual({"requires-approved-remote-interop": 1}, report.capture_gate_counts)

    def test_area_and_priority_filters_limit_readiness_items(self) -> None:
        report = readiness.build_report(
            include_future=True,
            include_accepted=True,
            areas={"trace-interop"},
            priorities={"P3"},
        )

        self.assertEqual([], report.errors)
        self.assertEqual(("trace-interop",), report.area_filter)
        self.assertEqual(("P3",), report.priority_filter)
        self.assertEqual(1, report.item_count)
        self.assertEqual({"trace-interop": 1}, report.area_counts)
        self.assertEqual({"P3": 1}, report.priority_counts)
        self.assertEqual("GAP-TRACE-REMOTE-INTEROP", report.items[0].gap_id)

    def test_gap_id_filter_can_return_empty_scope(self) -> None:
        report = readiness.build_report(gap_ids={"GAP-DOES-NOT-EXIST"})

        self.assertEqual([], report.errors)
        self.assertEqual(("GAP-DOES-NOT-EXIST",), report.gap_id_filter)
        self.assertEqual(0, report.item_count)
        self.assertEqual({}, report.capture_gate_counts)
        self.assertEqual({}, report.capture_gate_gap_ids)
        self.assertEqual({}, report.readiness_gap_ids)
        self.assertEqual([], report.warnings)

    def test_readiness_filter_can_return_empty_scope(self) -> None:
        report = readiness.build_report(readinesses={"local-sample-only"})

        self.assertEqual([], report.errors)
        self.assertEqual(("local-sample-only",), report.readiness_filter)
        self.assertEqual(0, report.item_count)
        self.assertEqual({}, report.area_counts)
        self.assertEqual({}, report.capture_gate_gap_ids)
        self.assertEqual({}, report.readiness_gap_ids)


if __name__ == "__main__":
    unittest.main()
