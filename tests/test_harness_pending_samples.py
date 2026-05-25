from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_harness_pending_samples as pending_samples  # noqa: E402
import harness_collection_lane_commands  # noqa: E402
import harness_pending_review_cards  # noqa: E402
import harness_sample_review_commands  # noqa: E402
import harness_sample_slots  # noqa: E402


DEFAULT_HIDDEN_CAPTURE_FOCUS_GAP_IDS = (
    "GAP-SEC-SCHEDULED-RUN",
    "GAP-TRACE-LOCAL-SUMMARY-BURNIN",
    "GAP-AGENTIC-A2A-HANDOFF",
    "GAP-AGENTIC-CASCADE-STOP",
    "GAP-AGENTIC-MEMORY-POISONING",
    "GAP-AGENTIC-TOOL-SQUATTING",
    "GAP-WORKFLOW-CROSS-WS",
    "GAP-WORKFLOW-PR-OVERLAP",
    "GAP-WORKFLOW-SIMPLE-SKIP",
    "GAP-TRACE-REMOTE-INTEROP",
)


class HarnessPendingSamplesTest(unittest.TestCase):
    def test_repository_report_tracks_existing_pending_slots(self) -> None:
        report = pending_samples.build_report()

        self.assertEqual([], report.errors)
        self.assertEqual((), report.scope_gap_ids)
        self.assertEqual("any", report.pending_review_state_filter)
        self.assertEqual(7, report.ledger_count)
        self.assertEqual(2, report.outcome_counts["pending"])
        self.assertEqual({"placeholder": 2}, report.pending_review_state_counts)
        self.assertEqual({}, report.pending_review_ready_by_gap)
        self.assertEqual(
            {"GAP-GUARDRAIL-PREFLIGHT-WARNING": 1, "GAP-RUNTIME-LOOP-SCOPE-WARNING": 1},
            report.pending_placeholder_by_gap,
        )
        self.assertEqual({"local-only": 1, "local-replay": 8, "real": 14, "synthetic": 5}, report.accepted_evidence_class_counts)
        self.assertEqual(2, report.accepted_real_by_gap["GAP-GUARDRAIL-SOURCE-BOUNDARY"])
        self.assertEqual(2, report.accepted_real_by_gap["GAP-SEC-CONTROL-MATRIX-BURNIN"])
        self.assertEqual(2, report.accepted_real_by_gap["GAP-RUNTIME-STAGE-CHECKPOINT-RESUME"])
        self.assertEqual(3, report.accepted_real_by_gap["GAP-TRACE-LOCAL-SUMMARY-BURNIN"])
        self.assertEqual(3, report.accepted_real_by_gap["GAP-WORKFLOW-TASK-PROFILE-AUDIT"])
        self.assertEqual(2, report.accepted_real_by_gap["GAP-AGENTIC-SANDBOX-HONESTY"])
        self.assertNotIn("GAP-GUARDRAIL-PREFLIGHT-WARNING", report.accepted_real_by_gap)
        checkpoint_metric = report.queued_readiness_metrics_by_gap["GAP-RUNTIME-STAGE-CHECKPOINT-RESUME"]
        self.assertEqual("accepted cross-task resume samples", checkpoint_metric.source_metric)
        self.assertEqual(0, checkpoint_metric.accepted_count)
        self.assertEqual("0/2", checkpoint_metric.current_to_target)
        self.assertEqual(2, checkpoint_metric.ledger_accepted_real_count)
        self.assertEqual(
            "ledger accepted real=2; accepted cross-task resume samples=0/2",
            report.accepted_real_readiness_metric_deltas["GAP-RUNTIME-STAGE-CHECKPOINT-RESUME"],
        )
        self.assertEqual(
            "ledger accepted real=3; accepted real local trace summary task classes=1/3",
            report.accepted_real_readiness_metric_deltas["GAP-TRACE-LOCAL-SUMMARY-BURNIN"],
        )
        self.assertNotIn("GAP-TRACE-OTLP-PILOT-BURNIN", report.accepted_real_readiness_metric_deltas)
        self.assertEqual(1, report.accepted_synthetic_by_gap["GAP-GUARDRAIL-PREFLIGHT-WARNING"])
        self.assertEqual(1, report.accepted_local_only_by_gap["GAP-TRACE-OTLP-PILOT-BURNIN"])
        self.assertEqual(1, report.pending_by_gap["GAP-GUARDRAIL-PREFLIGHT-WARNING"])
        self.assertEqual(1, report.pending_by_gap["GAP-RUNTIME-LOOP-SCOPE-WARNING"])
        self.assertIn("GAP-GUARDRAIL-PREFLIGHT-WARNING", report.queued_with_pending)
        self.assertIn("GAP-RUNTIME-LOOP-SCOPE-WARNING", report.queued_with_pending)
        self.assertIn("GAP-TRACE-LOCAL-SUMMARY-BURNIN", report.queued_without_pending)
        self.assertIn("GAP-RUNTIME-STAGE-CHECKPOINT-RESUME", report.queued_without_pending)
        self.assertEqual(
            {"append-new-pending-slot": 13, "fill-existing-placeholder": 2, "review-upgrade-decision": 4},
            report.queued_ledger_action_counts,
        )
        self.assertEqual(
            ["GAP-GUARDRAIL-PREFLIGHT-WARNING", "GAP-RUNTIME-LOOP-SCOPE-WARNING"],
            report.queued_ledger_action_gaps["fill-existing-placeholder"],
        )
        self.assertEqual(0, report.queued_with_review_ready_pending_count)
        self.assertEqual(19, report.queued_without_review_ready_pending_count)
        self.assertEqual([], report.queued_with_review_ready_pending)
        self.assertEqual(15, report.actionable_sample_gap_count)
        self.assertEqual(
            {"append-new-pending-slot": 13, "fill-existing-placeholder": 2},
            report.actionable_ledger_action_counts,
        )
        self.assertIn("GAP-TRACE-LOCAL-SUMMARY-BURNIN", report.actionable_ledger_action_gaps["append-new-pending-slot"])
        self.assertIn("GAP-AGENTIC-CASCADE-STOP", report.actionable_ledger_action_gaps["append-new-pending-slot"])
        self.assertEqual(2, report.actionable_with_pending_count)
        self.assertEqual(0, report.actionable_with_review_ready_pending_count)
        self.assertEqual(2, report.actionable_with_placeholder_pending_count)
        self.assertEqual(13, report.actionable_without_pending_count)
        self.assertEqual(15, report.actionable_without_review_ready_pending_count)
        self.assertEqual([], report.actionable_with_review_ready_pending)
        self.assertEqual(
            ["GAP-GUARDRAIL-PREFLIGHT-WARNING", "GAP-RUNTIME-LOOP-SCOPE-WARNING"],
            report.actionable_with_placeholder_pending,
        )
        self.assertEqual(
            ["fill-existing-placeholder", "append-new-pending-slot", "review-upgrade-decision"],
            [lane.ledger_action for lane in report.next_collection_lane_commands],
        )
        self.assertEqual(5, len(report.next_capture_focus))
        self.assertEqual(5, report.next_capture_focus_count)
        self.assertEqual(15, report.next_capture_focus_available_count)
        self.assertEqual(5, report.next_capture_focus_limit)
        self.assertTrue(report.next_capture_focus_truncated)
        self.assertEqual(DEFAULT_HIDDEN_CAPTURE_FOCUS_GAP_IDS, report.next_capture_focus_hidden_gap_ids)
        self.assertEqual((), report.next_capture_focus_area_filter)
        self.assertEqual((), report.next_capture_focus_priority_filter)
        self.assertEqual((), report.next_capture_focus_ledger_action_filter)
        self.assertEqual((), report.next_capture_focus_capture_gate_filter)
        self.assertEqual((), report.next_capture_focus_readiness_filter)
        self.assertEqual({"P0": 1, "P1": 4}, report.next_capture_focus_shown_priority_counts)
        self.assertEqual(
            {"P0": 1, "P1": 6, "P2": 7, "P3": 1},
            report.next_capture_focus_available_priority_counts,
        )
        self.assertEqual(
            {"ai-guardrail": 2, "runtime-durability": 2, "security-evidence": 1},
            report.next_capture_focus_shown_area_counts,
        )
        self.assertEqual(
            {
                "agentic-red-team": 4,
                "ai-guardrail": 2,
                "runtime-durability": 2,
                "security-evidence": 2,
                "trace-interop": 2,
                "workflow-skills": 3,
            },
            report.next_capture_focus_available_area_counts,
        )
        self.assertEqual(
            {"append-new-pending-slot": 3, "fill-existing-placeholder": 2},
            report.next_capture_focus_shown_ledger_action_counts,
        )
        self.assertEqual(
            {"append-new-pending-slot": 13, "fill-existing-placeholder": 2},
            report.next_capture_focus_available_ledger_action_counts,
        )
        self.assertEqual(
            {
                "replace-placeholder-after-real-event": 2,
                "requires-cross-task-resume": 1,
                "requires-security-workflow-event": 1,
                "requires-user-confirmed-high-impact-action": 1,
            },
            report.next_capture_focus_shown_capture_gate_counts,
        )
        self.assertEqual(
            {
                "replace-placeholder-after-real-event": 2,
                "requires-approved-bounded-incident": 1,
                "requires-approved-remote-interop": 1,
                "requires-bounded-real-incident": 3,
                "requires-cross-task-resume": 1,
                "requires-distinct-task-class-report": 1,
                "requires-security-workflow-event": 2,
                "requires-user-confirmed-high-impact-action": 1,
                "requires-workflow-task-event": 3,
            },
            report.next_capture_focus_available_capture_gate_counts,
        )
        self.assertEqual({"needs-first-real-sample": 5}, report.next_capture_focus_shown_readiness_counts)
        self.assertEqual(
            {"needs-first-real-sample": 14, "needs-more-real-samples": 1},
            report.next_capture_focus_available_readiness_counts,
        )
        self.assertEqual(
            [
                "GAP-GUARDRAIL-PREFLIGHT-WARNING",
                "GAP-GUARDRAIL-CONFIRMATION",
                "GAP-RUNTIME-LOOP-SCOPE-WARNING",
                "GAP-RUNTIME-STAGE-CHECKPOINT-RESUME",
                "GAP-SEC-PR-DEPENDENCY",
            ],
            [item.gap_id for item in report.next_capture_focus],
        )
        self.assertEqual("P0", report.next_capture_focus[0].priority)
        self.assertEqual("fill-existing-placeholder", report.next_capture_focus[0].ledger_action)
        self.assertEqual(
            ("PRE-SAMPLE-2026-05-24-real-tool-call-pending (docs/ai/standards/pre-tool-use-preflight-samples.jsonl:2)",),
            report.next_capture_focus[0].pending_slot_refs,
        )
        self.assertIn(
            "triggered_findings must include a meaningful value",
            report.next_capture_focus[0].pending_review_blockers[0],
        )
        self.assertEqual(
            [
                "finding code",
                "operator decision",
                "action taken",
                "false-positive classification",
                "bounded evidence ref",
            ],
            report.next_capture_focus[0].evidence_needed,
        )
        self.assertIn("check_harness_placeholder_replacement.py", report.next_capture_focus[0].lane_review_command)
        self.assertIn("--gap-id GAP-GUARDRAIL-PREFLIGHT-WARNING", report.next_capture_focus[0].planner_command)
        self.assertIn("--ledger-action fill-existing-placeholder", report.next_capture_focus[0].planner_command)
        self.assertIn("--gap-id GAP-GUARDRAIL-PREFLIGHT-WARNING", report.next_capture_focus[0].intake_command)
        self.assertIn("--ledger-action fill-existing-placeholder", report.next_capture_focus[0].intake_command)
        self.assertEqual("replace-placeholder-after-real-event", report.next_capture_focus[0].capture_gate)
        self.assertIn("matching real event", report.next_capture_focus[0].capture_gate_detail)
        self.assertEqual("append-new-pending-slot", report.next_capture_focus[1].ledger_action)
        self.assertEqual((), report.next_capture_focus[1].pending_slot_refs)
        self.assertEqual((), report.next_capture_focus[1].pending_review_blockers)
        self.assertEqual("requires-user-confirmed-high-impact-action", report.next_capture_focus[1].capture_gate)
        self.assertIn("user confirmation", report.next_capture_focus[1].evidence_needed)
        self.assertIn("check_harness_sample_append.py", report.next_capture_focus[1].lane_review_command)
        self.assertIn("--ledger-action append-new-pending-slot", report.next_capture_focus[1].planner_command)
        self.assertIn("--ledger-action append-new-pending-slot", report.next_capture_focus[1].intake_command)
        checkpoint_focus = report.next_capture_focus[3]
        self.assertEqual("GAP-RUNTIME-STAGE-CHECKPOINT-RESUME", checkpoint_focus.gap_id)
        self.assertEqual("accepted cross-task resume samples", checkpoint_focus.source_metric)
        self.assertEqual("0/2", checkpoint_focus.current_to_target)
        self.assertEqual(
            "ledger accepted real=2; accepted cross-task resume samples=0/2",
            checkpoint_focus.readiness_metric_delta,
        )
        self.assertEqual("requires-cross-task-resume", checkpoint_focus.capture_gate)
        fill_lane = report.next_collection_lane_commands[0]
        self.assertEqual(2, fill_lane.gap_count)
        self.assertIn("GAP-GUARDRAIL-PREFLIGHT-WARNING", fill_lane.gap_ids)
        self.assertIn("do not append a duplicate row", fill_lane.boundary)
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
            "--ledger-action fill-existing-placeholder --capture-card",
            fill_lane.commands,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
            "--review-state placeholder --review-cards",
            fill_lane.commands,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_placeholder_replacement.py <candidate-jsonl>",
            fill_lane.commands,
        )
        append_lane = report.next_collection_lane_commands[1]
        self.assertEqual(13, append_lane.gap_count)
        self.assertIn("GAP-TRACE-LOCAL-SUMMARY-BURNIN", append_lane.gap_ids)
        self.assertIn("GAP-TRACE-REMOTE-INTEROP", append_lane.gap_ids)
        self.assertIn("GAP-AGENTIC-CASCADE-STOP", append_lane.gap_ids)
        self.assertIn("templates are not accepted evidence", append_lane.boundary)
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
            "--ledger-action append-new-pending-slot --summary",
            append_lane.commands,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_append.py <candidate-jsonl>",
            append_lane.commands,
        )
        review_lane = report.next_collection_lane_commands[2]
        self.assertEqual(4, review_lane.gap_count)
        self.assertEqual(
            (
                "GAP-AGENTIC-SANDBOX-HONESTY",
                "GAP-GUARDRAIL-SOURCE-BOUNDARY",
                "GAP-SEC-CONTROL-MATRIX-BURNIN",
                "GAP-WORKFLOW-TASK-PROFILE-AUDIT",
            ),
            review_lane.gap_ids,
        )
        self.assertIn("do not append another sample", review_lane.boundary)
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
            "--ledger-action review-upgrade-decision --summary",
            review_lane.commands,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh "
            "scripts/check_harness_upgrade_decision_candidate.py <candidate-jsonl>",
            review_lane.commands,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_upgrade_decisions.py",
            review_lane.commands,
        )
        self.assertIn("GAP-GUARDRAIL-PREFLIGHT-WARNING", report.actionable_without_review_ready_pending)
        self.assertIn("GAP-RUNTIME-LOOP-SCOPE-WARNING", report.actionable_without_review_ready_pending)
        self.assertIn("GAP-TRACE-LOCAL-SUMMARY-BURNIN", report.actionable_without_pending)
        self.assertIn("GAP-TRACE-LOCAL-SUMMARY-BURNIN", report.actionable_without_review_ready_pending)
        self.assertIn("GAP-TRACE-REMOTE-INTEROP", report.actionable_without_pending)
        self.assertIn("GAP-TRACE-REMOTE-INTEROP", report.actionable_without_review_ready_pending)
        self.assertIn("GAP-AGENTIC-CASCADE-STOP", report.actionable_without_pending)
        self.assertIn("GAP-AGENTIC-CASCADE-STOP", report.actionable_without_review_ready_pending)
        self.assertEqual(
            [
                "GAP-AGENTIC-SANDBOX-HONESTY",
                "GAP-GUARDRAIL-SOURCE-BOUNDARY",
                "GAP-SEC-CONTROL-MATRIX-BURNIN",
                "GAP-WORKFLOW-TASK-PROFILE-AUDIT",
            ],
            report.ready_upgrade_decision_gaps,
        )
        self.assertIn(
            "native sandbox, hosted trace, MCP, A2A, or external-provider boundary evidence before promotion",
            "\n".join(report.ready_upgrade_decision_next_evidence_by_gap["GAP-AGENTIC-SANDBOX-HONESTY"]),
        )
        self.assertIn(
            "more real tasks outside the initial simple/complex/0-1-stage profile set",
            "\n".join(report.ready_upgrade_decision_next_evidence_by_gap["GAP-WORKFLOW-TASK-PROFILE-AUDIT"]),
        )
        self.assertEqual([], report.contract_blocked_gaps)
        self.assertEqual([], report.local_only_gaps)
        self.assertEqual(2, len(report.review_cards))

    def test_capture_focus_limit_zero_expands_all_actionable_capture_lanes(self) -> None:
        report = pending_samples.build_report(capture_focus_limit=0)
        focus_gap_ids = [item.gap_id for item in report.next_capture_focus]

        self.assertEqual(report.actionable_without_review_ready_pending_count, len(report.next_capture_focus))
        self.assertEqual(15, report.next_capture_focus_count)
        self.assertEqual(15, report.next_capture_focus_available_count)
        self.assertEqual(0, report.next_capture_focus_limit)
        self.assertFalse(report.next_capture_focus_truncated)
        self.assertEqual((), report.next_capture_focus_hidden_gap_ids)
        self.assertEqual(report.next_capture_focus_available_priority_counts, report.next_capture_focus_shown_priority_counts)
        self.assertEqual(
            report.next_capture_focus_available_ledger_action_counts,
            report.next_capture_focus_shown_ledger_action_counts,
        )
        self.assertEqual(report.next_capture_focus_available_area_counts, report.next_capture_focus_shown_area_counts)
        self.assertEqual(
            report.next_capture_focus_available_capture_gate_counts,
            report.next_capture_focus_shown_capture_gate_counts,
        )
        self.assertEqual(
            report.next_capture_focus_available_readiness_counts,
            report.next_capture_focus_shown_readiness_counts,
        )
        self.assertIn("GAP-TRACE-REMOTE-INTEROP", focus_gap_ids)
        self.assertIn("GAP-AGENTIC-CASCADE-STOP", focus_gap_ids)
        self.assertNotIn("GAP-AGENTIC-SANDBOX-HONESTY", focus_gap_ids)
        self.assertNotIn("GAP-WORKFLOW-TASK-PROFILE-AUDIT", focus_gap_ids)
        self.assertNotIn("GAP-TRACE-OTLP-PILOT-BURNIN", focus_gap_ids)
        focus_by_gap = {item.gap_id: item for item in report.next_capture_focus}
        self.assertEqual(
            "ledger accepted real=3; accepted real local trace summary task classes=1/3",
            focus_by_gap["GAP-TRACE-LOCAL-SUMMARY-BURNIN"].readiness_metric_delta,
        )

    def test_capture_focus_priority_filter_limits_focus_metadata(self) -> None:
        report = pending_samples.build_report(capture_focus_priorities={"P2"}, capture_focus_limit=0)
        focus_gap_ids = [item.gap_id for item in report.next_capture_focus]

        self.assertEqual((), report.next_capture_focus_area_filter)
        self.assertEqual(("P2",), report.next_capture_focus_priority_filter)
        self.assertEqual((), report.next_capture_focus_ledger_action_filter)
        self.assertEqual((), report.next_capture_focus_capture_gate_filter)
        self.assertEqual((), report.next_capture_focus_readiness_filter)
        self.assertEqual(7, report.next_capture_focus_count)
        self.assertEqual(7, report.next_capture_focus_available_count)
        self.assertEqual(0, report.next_capture_focus_limit)
        self.assertFalse(report.next_capture_focus_truncated)
        self.assertEqual((), report.next_capture_focus_hidden_gap_ids)
        self.assertEqual({"P2": 7}, report.next_capture_focus_shown_priority_counts)
        self.assertEqual({"P2": 7}, report.next_capture_focus_available_priority_counts)
        self.assertEqual(
            {"agentic-red-team": 4, "workflow-skills": 3},
            report.next_capture_focus_shown_area_counts,
        )
        self.assertEqual(
            {"agentic-red-team": 4, "workflow-skills": 3},
            report.next_capture_focus_available_area_counts,
        )
        self.assertEqual({"append-new-pending-slot": 7}, report.next_capture_focus_shown_ledger_action_counts)
        self.assertEqual({"append-new-pending-slot": 7}, report.next_capture_focus_available_ledger_action_counts)
        self.assertEqual(
            {"requires-approved-bounded-incident": 1, "requires-bounded-real-incident": 3, "requires-workflow-task-event": 3},
            report.next_capture_focus_shown_capture_gate_counts,
        )
        self.assertTrue(all(item.priority == "P2" for item in report.next_capture_focus))
        self.assertIn("GAP-AGENTIC-CASCADE-STOP", focus_gap_ids)
        self.assertIn("GAP-WORKFLOW-SIMPLE-SKIP", focus_gap_ids)
        self.assertNotIn("GAP-GUARDRAIL-CONFIRMATION", focus_gap_ids)
        self.assertNotIn("GAP-TRACE-REMOTE-INTEROP", focus_gap_ids)

    def test_capture_focus_area_filter_limits_focus_metadata(self) -> None:
        report = pending_samples.build_report(capture_focus_areas={"agentic-red-team"}, capture_focus_limit=0)
        focus_gap_ids = [item.gap_id for item in report.next_capture_focus]

        self.assertEqual(("agentic-red-team",), report.next_capture_focus_area_filter)
        self.assertEqual((), report.next_capture_focus_priority_filter)
        self.assertEqual((), report.next_capture_focus_ledger_action_filter)
        self.assertEqual((), report.next_capture_focus_capture_gate_filter)
        self.assertEqual((), report.next_capture_focus_readiness_filter)
        self.assertEqual(4, report.next_capture_focus_count)
        self.assertEqual(4, report.next_capture_focus_available_count)
        self.assertEqual(0, report.next_capture_focus_limit)
        self.assertFalse(report.next_capture_focus_truncated)
        self.assertEqual((), report.next_capture_focus_hidden_gap_ids)
        self.assertEqual({"P2": 4}, report.next_capture_focus_shown_priority_counts)
        self.assertEqual({"P2": 4}, report.next_capture_focus_available_priority_counts)
        self.assertEqual({"agentic-red-team": 4}, report.next_capture_focus_shown_area_counts)
        self.assertEqual({"agentic-red-team": 4}, report.next_capture_focus_available_area_counts)
        self.assertEqual({"append-new-pending-slot": 4}, report.next_capture_focus_shown_ledger_action_counts)
        self.assertEqual({"append-new-pending-slot": 4}, report.next_capture_focus_available_ledger_action_counts)
        self.assertEqual(
            {"requires-approved-bounded-incident": 1, "requires-bounded-real-incident": 3},
            report.next_capture_focus_shown_capture_gate_counts,
        )
        self.assertTrue(all(item.area == "agentic-red-team" for item in report.next_capture_focus))
        self.assertIn("GAP-AGENTIC-CASCADE-STOP", focus_gap_ids)
        self.assertIn("GAP-AGENTIC-TOOL-SQUATTING", focus_gap_ids)
        self.assertNotIn("GAP-WORKFLOW-SIMPLE-SKIP", focus_gap_ids)
        self.assertNotIn("GAP-TRACE-REMOTE-INTEROP", focus_gap_ids)

    def test_capture_focus_ledger_action_filter_limits_focus_metadata(self) -> None:
        report = pending_samples.build_report(
            capture_focus_ledger_actions={"fill-existing-placeholder"},
            capture_focus_limit=0,
        )
        focus_gap_ids = [item.gap_id for item in report.next_capture_focus]

        self.assertEqual((), report.next_capture_focus_area_filter)
        self.assertEqual((), report.next_capture_focus_priority_filter)
        self.assertEqual(("fill-existing-placeholder",), report.next_capture_focus_ledger_action_filter)
        self.assertEqual((), report.next_capture_focus_capture_gate_filter)
        self.assertEqual((), report.next_capture_focus_readiness_filter)
        self.assertEqual(2, report.next_capture_focus_count)
        self.assertEqual(2, report.next_capture_focus_available_count)
        self.assertEqual(0, report.next_capture_focus_limit)
        self.assertFalse(report.next_capture_focus_truncated)
        self.assertEqual((), report.next_capture_focus_hidden_gap_ids)
        self.assertEqual({"P0": 1, "P1": 1}, report.next_capture_focus_shown_priority_counts)
        self.assertEqual({"P0": 1, "P1": 1}, report.next_capture_focus_available_priority_counts)
        self.assertEqual(
            {"ai-guardrail": 1, "runtime-durability": 1},
            report.next_capture_focus_shown_area_counts,
        )
        self.assertEqual(
            {"ai-guardrail": 1, "runtime-durability": 1},
            report.next_capture_focus_available_area_counts,
        )
        self.assertEqual({"fill-existing-placeholder": 2}, report.next_capture_focus_shown_ledger_action_counts)
        self.assertEqual({"fill-existing-placeholder": 2}, report.next_capture_focus_available_ledger_action_counts)
        self.assertEqual(
            {"replace-placeholder-after-real-event": 2},
            report.next_capture_focus_shown_capture_gate_counts,
        )
        self.assertTrue(all(item.ledger_action == "fill-existing-placeholder" for item in report.next_capture_focus))
        self.assertEqual(
            ["GAP-GUARDRAIL-PREFLIGHT-WARNING", "GAP-RUNTIME-LOOP-SCOPE-WARNING"],
            focus_gap_ids,
        )

    def test_capture_focus_capture_gate_filter_limits_focus_metadata(self) -> None:
        report = pending_samples.build_report(
            capture_focus_gates={"requires-approved-remote-interop"},
            capture_focus_limit=0,
        )

        self.assertEqual((), report.next_capture_focus_area_filter)
        self.assertEqual((), report.next_capture_focus_priority_filter)
        self.assertEqual((), report.next_capture_focus_ledger_action_filter)
        self.assertEqual(("requires-approved-remote-interop",), report.next_capture_focus_capture_gate_filter)
        self.assertEqual((), report.next_capture_focus_readiness_filter)
        self.assertEqual(1, report.next_capture_focus_count)
        self.assertEqual(1, report.next_capture_focus_available_count)
        self.assertEqual(0, report.next_capture_focus_limit)
        self.assertFalse(report.next_capture_focus_truncated)
        self.assertEqual((), report.next_capture_focus_hidden_gap_ids)
        self.assertEqual(["GAP-TRACE-REMOTE-INTEROP"], [item.gap_id for item in report.next_capture_focus])
        self.assertEqual({"P3": 1}, report.next_capture_focus_shown_priority_counts)
        self.assertEqual({"trace-interop": 1}, report.next_capture_focus_shown_area_counts)
        self.assertEqual({"append-new-pending-slot": 1}, report.next_capture_focus_shown_ledger_action_counts)
        self.assertEqual(
            {"requires-approved-remote-interop": 1},
            report.next_capture_focus_shown_capture_gate_counts,
        )
        self.assertEqual(
            {"requires-approved-remote-interop": 1},
            report.next_capture_focus_available_capture_gate_counts,
        )

    def test_capture_focus_readiness_filter_limits_focus_metadata(self) -> None:
        report = pending_samples.build_report(
            capture_focus_readinesses={"needs-more-real-samples"},
            capture_focus_limit=0,
        )

        self.assertEqual((), report.next_capture_focus_area_filter)
        self.assertEqual((), report.next_capture_focus_priority_filter)
        self.assertEqual((), report.next_capture_focus_ledger_action_filter)
        self.assertEqual((), report.next_capture_focus_capture_gate_filter)
        self.assertEqual(("needs-more-real-samples",), report.next_capture_focus_readiness_filter)
        self.assertEqual(1, report.next_capture_focus_count)
        self.assertEqual(1, report.next_capture_focus_available_count)
        self.assertEqual(0, report.next_capture_focus_limit)
        self.assertFalse(report.next_capture_focus_truncated)
        self.assertEqual((), report.next_capture_focus_hidden_gap_ids)
        self.assertEqual(["GAP-TRACE-LOCAL-SUMMARY-BURNIN"], [item.gap_id for item in report.next_capture_focus])
        self.assertEqual({"P1": 1}, report.next_capture_focus_shown_priority_counts)
        self.assertEqual({"trace-interop": 1}, report.next_capture_focus_shown_area_counts)
        self.assertEqual({"append-new-pending-slot": 1}, report.next_capture_focus_shown_ledger_action_counts)
        self.assertEqual(
            {"requires-distinct-task-class-report": 1},
            report.next_capture_focus_shown_capture_gate_counts,
        )
        self.assertEqual({"needs-more-real-samples": 1}, report.next_capture_focus_shown_readiness_counts)
        self.assertEqual({"needs-more-real-samples": 1}, report.next_capture_focus_available_readiness_counts)
        self.assertEqual("needs-more-real-samples", report.next_capture_focus[0].readiness)

    def test_gap_id_filter_focuses_counts_and_review_cards(self) -> None:
        report = pending_samples.build_report(gap_ids={"GAP-GUARDRAIL-PREFLIGHT-WARNING"})

        self.assertEqual(("GAP-GUARDRAIL-PREFLIGHT-WARNING",), report.scope_gap_ids)
        self.assertEqual(2, report.record_count)
        self.assertEqual({"accepted": 1, "pending": 1, "rejected": 0}, report.outcome_counts)
        self.assertEqual({"GAP-GUARDRAIL-PREFLIGHT-WARNING": 1}, report.pending_by_gap)
        self.assertEqual({"placeholder": 1}, report.pending_review_state_counts)
        self.assertEqual({"GAP-GUARDRAIL-PREFLIGHT-WARNING": 1}, report.pending_placeholder_by_gap)
        self.assertEqual(1, report.queued_gap_count)
        self.assertEqual({"fill-existing-placeholder": 1}, report.queued_ledger_action_counts)
        self.assertEqual(1, report.actionable_sample_gap_count)
        self.assertEqual({"fill-existing-placeholder": 1}, report.actionable_ledger_action_counts)
        self.assertEqual(1, report.actionable_with_placeholder_pending_count)
        self.assertEqual(1, report.actionable_without_review_ready_pending_count)
        self.assertEqual(1, len(report.pending_slots))
        self.assertEqual(1, len(report.review_cards))
        self.assertEqual("GAP-GUARDRAIL-PREFLIGHT-WARNING", report.review_cards[0].gap_id)
        self.assertEqual(1, len(report.next_collection_lane_commands))
        self.assertIn(
            "--gap-id GAP-GUARDRAIL-PREFLIGHT-WARNING --ledger-action fill-existing-placeholder",
            report.next_collection_lane_commands[0].commands[0],
        )
        self.assertIn(
            "--gap-id GAP-GUARDRAIL-PREFLIGHT-WARNING --review-state placeholder --review-cards",
            report.next_collection_lane_commands[0].commands[3],
        )
        self.assertEqual(1, len(report.next_capture_focus))
        self.assertEqual(1, report.next_capture_focus_count)
        self.assertEqual(1, report.next_capture_focus_available_count)
        self.assertEqual(5, report.next_capture_focus_limit)
        self.assertFalse(report.next_capture_focus_truncated)
        self.assertEqual((), report.next_capture_focus_area_filter)
        self.assertEqual((), report.next_capture_focus_priority_filter)
        self.assertEqual((), report.next_capture_focus_ledger_action_filter)
        self.assertEqual((), report.next_capture_focus_capture_gate_filter)
        self.assertEqual((), report.next_capture_focus_readiness_filter)
        self.assertEqual({"P0": 1}, report.next_capture_focus_shown_priority_counts)
        self.assertEqual({"P0": 1}, report.next_capture_focus_available_priority_counts)
        self.assertEqual({"ai-guardrail": 1}, report.next_capture_focus_shown_area_counts)
        self.assertEqual({"ai-guardrail": 1}, report.next_capture_focus_available_area_counts)
        self.assertEqual({"fill-existing-placeholder": 1}, report.next_capture_focus_shown_ledger_action_counts)
        self.assertEqual({"fill-existing-placeholder": 1}, report.next_capture_focus_available_ledger_action_counts)
        self.assertEqual(
            {"replace-placeholder-after-real-event": 1},
            report.next_capture_focus_shown_capture_gate_counts,
        )
        self.assertEqual("GAP-GUARDRAIL-PREFLIGHT-WARNING", report.next_capture_focus[0].gap_id)
        self.assertIn("placeholder pending row", report.next_capture_focus[0].reason)

    def test_review_state_filter_limits_pending_rows_without_changing_counts(self) -> None:
        report = pending_samples.build_report(review_state="review-ready")

        self.assertEqual("review-ready", report.pending_review_state_filter)
        self.assertEqual({"placeholder": 2}, report.pending_review_state_counts)
        self.assertEqual([], report.pending_slots)
        self.assertEqual([], report.review_cards)

    def test_include_future_and_accepted_expands_queue_comparison(self) -> None:
        report = pending_samples.build_report(include_future=True, include_accepted=True)

        self.assertEqual([], report.errors)
        self.assertIn("GAP-TRACE-REMOTE-INTEROP", report.queued_without_pending)
        self.assertIn("GAP-TRACE-OTLP-PILOT-BURNIN", report.queued_without_pending)
        self.assertEqual(15, report.actionable_sample_gap_count)
        self.assertEqual(0, report.actionable_with_review_ready_pending_count)
        self.assertEqual(2, report.actionable_with_placeholder_pending_count)
        self.assertEqual(13, report.actionable_without_pending_count)
        self.assertEqual(15, report.actionable_without_review_ready_pending_count)
        self.assertEqual(
            {
                "append-new-pending-slot": 13,
                "fill-existing-placeholder": 2,
                "no-sample-collection": 1,
                "review-upgrade-decision": 4,
            },
            report.queued_ledger_action_counts,
        )
        self.assertEqual(
            {"append-new-pending-slot": 13, "fill-existing-placeholder": 2},
            report.actionable_ledger_action_counts,
        )
        self.assertNotIn("GAP-AGENTIC-SANDBOX-HONESTY", report.actionable_without_pending)
        self.assertNotIn("GAP-GUARDRAIL-SOURCE-BOUNDARY", report.actionable_without_pending)
        self.assertNotIn("GAP-SEC-CONTROL-MATRIX-BURNIN", report.actionable_without_pending)
        self.assertNotIn("GAP-WORKFLOW-TASK-PROFILE-AUDIT", report.actionable_without_pending)
        self.assertIn("GAP-GUARDRAIL-PREFLIGHT-WARNING", report.actionable_without_review_ready_pending)
        self.assertIn("GAP-TRACE-LOCAL-SUMMARY-BURNIN", report.actionable_without_pending)
        self.assertIn("GAP-TRACE-LOCAL-SUMMARY-BURNIN", report.actionable_without_review_ready_pending)
        self.assertIn("GAP-AGENTIC-CASCADE-STOP", report.actionable_without_pending)
        self.assertIn("GAP-AGENTIC-CASCADE-STOP", report.actionable_without_review_ready_pending)
        self.assertIn("GAP-TRACE-REMOTE-INTEROP", report.actionable_without_pending)
        self.assertIn("GAP-TRACE-REMOTE-INTEROP", report.actionable_without_review_ready_pending)
        self.assertEqual(
            [
                "GAP-AGENTIC-SANDBOX-HONESTY",
                "GAP-GUARDRAIL-SOURCE-BOUNDARY",
                "GAP-SEC-CONTROL-MATRIX-BURNIN",
                "GAP-WORKFLOW-TASK-PROFILE-AUDIT",
            ],
            report.ready_upgrade_decision_gaps,
        )
        self.assertEqual(
            [
                "GAP-AGENTIC-SANDBOX-HONESTY",
                "GAP-GUARDRAIL-SOURCE-BOUNDARY",
                "GAP-SEC-CONTROL-MATRIX-BURNIN",
                "GAP-WORKFLOW-TASK-PROFILE-AUDIT",
            ],
            list(report.ready_upgrade_decision_next_evidence_by_gap),
        )
        self.assertEqual([], report.contract_blocked_gaps)
        self.assertEqual([], report.contract_blocker_states)
        self.assertEqual(["GAP-TRACE-OTLP-PILOT-BURNIN"], report.local_only_gaps)
        self.assertEqual(["GAP-TRACE-OTLP-PILOT-BURNIN"], report.queued_ledger_action_gaps["no-sample-collection"])
        self.assertEqual(
            [
                "fill-existing-placeholder",
                "append-new-pending-slot",
                "review-upgrade-decision",
            ],
            [lane.ledger_action for lane in report.next_collection_lane_commands],
        )
        review_lane = report.next_collection_lane_commands[2]
        self.assertEqual(
            (
                "GAP-AGENTIC-SANDBOX-HONESTY",
                "GAP-GUARDRAIL-SOURCE-BOUNDARY",
                "GAP-SEC-CONTROL-MATRIX-BURNIN",
                "GAP-WORKFLOW-TASK-PROFILE-AUDIT",
            ),
            review_lane.gap_ids,
        )
        self.assertIn("check_harness_upgrade_decision_candidate.py", "\n".join(review_lane.commands))
        self.assertIn("check_harness_upgrade_decisions.py", "\n".join(review_lane.commands))

    def test_red_team_local_replay_without_roadmap_gap_is_kept_as_risk_bucket(self) -> None:
        report = pending_samples.build_report()

        self.assertFalse(any("sample is not mapped to a roadmap gap" in warning for warning in report.warnings))
        self.assertIn("risk:prompt-injection", report.accepted_by_gap)
        self.assertIn("risk:prompt-injection", report.accepted_local_replay_by_gap)
        self.assertNotIn("risk:prompt-injection", report.accepted_real_by_gap)
        self.assertNotIn("<unmapped>", report.pending_by_gap)

    def test_review_cards_bind_pending_slots_to_checker_and_readiness(self) -> None:
        report = pending_samples.build_report()
        cards = {card.gap_id: card for card in report.review_cards}
        preflight_card = cards["GAP-GUARDRAIL-PREFLIGHT-WARNING"]

        self.assertEqual("PRE-SAMPLE-2026-05-24-real-tool-call-pending", preflight_card.sample_id)
        self.assertEqual("real", preflight_card.evidence_class)
        self.assertEqual("placeholder", preflight_card.pending_review_state)
        self.assertEqual(
            (
                "triggered_findings must include a meaningful value",
                "operator_decisions must include a meaningful value",
                "action_taken must include a meaningful value",
            ),
            preflight_card.review_blockers,
        )
        self.assertEqual("needs-first-real-sample", preflight_card.readiness)
        self.assertEqual("fill-existing-placeholder", preflight_card.ledger_action)
        self.assertEqual("0/2", preflight_card.current_to_target)
        self.assertEqual("replace-placeholder-after-real-event", preflight_card.capture_gate)
        self.assertIn("matching real event", preflight_card.capture_gate_detail)
        self.assertIn("real PreToolUse warning", preflight_card.trigger)
        self.assertEqual(
            (
                "finding code",
                "operator decision",
                "action taken",
                "false-positive classification",
                "bounded evidence ref",
            ),
            preflight_card.evidence_needed,
        )
        self.assertIn("check_pre_tool_use_preflight_samples.py", preflight_card.review_command)
        self.assertIn("check_harness_placeholder_replacement.py", preflight_card.replacement_review_command)
        self.assertIn("<candidate-jsonl>", preflight_card.replacement_review_command)
        self.assertEqual("not-applicable", preflight_card.outcome_review_command)
        self.assertIn("Pending samples stay unaccepted", preflight_card.review_boundary)

    def test_review_card_cli_output_is_read_only(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_harness_pending_samples.py"), "--review-cards"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("# Pending Harness Sample Review Cards", result.stdout)
        self.assertIn("Review cards are read-only", result.stdout)
        self.assertIn("Scope gaps: all", result.stdout)
        self.assertIn("Review-state filter: any", result.stdout)
        self.assertIn("Evidence class", result.stdout)
        self.assertIn("Review state", result.stdout)
        self.assertIn("Review blockers", result.stdout)
        self.assertIn("Ledger action", result.stdout)
        self.assertIn("Capture gate", result.stdout)
        self.assertIn("Gate detail", result.stdout)
        self.assertIn("Evidence needed", result.stdout)
        self.assertIn("replace-placeholder-after-real-event", result.stdout)
        self.assertIn("finding code; operator decision; action taken", result.stdout)

    def test_capture_focus_cli_output_is_read_only(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_harness_pending_samples.py"), "--capture-focus"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("# Pending Harness Next Capture Focus", result.stdout)
        self.assertIn("Capture focus is read-only", result.stdout)
        self.assertIn("Scope gaps: all", result.stdout)
        self.assertIn("Focus area filter: all", result.stdout)
        self.assertIn("Focus priority filter: all", result.stdout)
        self.assertIn("Focus ledger-action filter: all", result.stdout)
        self.assertIn("Focus capture-gate filter: all", result.stdout)
        self.assertIn("Focus readiness filter: all", result.stdout)
        self.assertIn("Focus entries: 5/15", result.stdout)
        self.assertIn("Focus limit: 5", result.stdout)
        self.assertIn("Focus truncated: true", result.stdout)
        self.assertIn("Focus shown priorities: {'P0': 1, 'P1': 4}", result.stdout)
        self.assertIn("Focus available priorities: {'P0': 1, 'P1': 6, 'P2': 7, 'P3': 1}", result.stdout)
        self.assertIn("Focus shown areas: {'ai-guardrail': 2, 'runtime-durability': 2, 'security-evidence': 1}", result.stdout)
        self.assertIn("Focus available areas: {'agentic-red-team': 4", result.stdout)
        self.assertIn("Focus shown ledger actions: {'append-new-pending-slot': 3, 'fill-existing-placeholder': 2}", result.stdout)
        self.assertIn(
            "Focus available ledger actions: {'append-new-pending-slot': 13, 'fill-existing-placeholder': 2}",
            result.stdout,
        )
        self.assertIn("Focus shown capture gates: {'replace-placeholder-after-real-event': 2", result.stdout)
        self.assertIn("Focus available capture gates: {'replace-placeholder-after-real-event': 2", result.stdout)
        self.assertIn("Focus shown readiness: {'needs-first-real-sample': 5}", result.stdout)
        self.assertIn(
            "Focus available readiness: {'needs-first-real-sample': 14, 'needs-more-real-samples': 1}",
            result.stdout,
        )
        self.assertIn(f"Focus hidden gap ids: {', '.join(DEFAULT_HIDDEN_CAPTURE_FOCUS_GAP_IDS)}", result.stdout)
        self.assertIn("## P0 GAP-GUARDRAIL-PREFLIGHT-WARNING", result.stdout)
        self.assertIn("Area: `ai-guardrail`", result.stdout)
        self.assertIn("Metric: accepted real preflight warning samples", result.stdout)
        self.assertIn("Current / target: 0/2", result.stdout)
        self.assertIn("Pending refs: PRE-SAMPLE-2026-05-24-real-tool-call-pending", result.stdout)
        self.assertIn("Pending blockers: PRE-SAMPLE-2026-05-24-real-tool-call-pending", result.stdout)
        self.assertIn("Capture gate: `replace-placeholder-after-real-event`", result.stdout)
        self.assertIn("Gate detail: Wait for the matching real event", result.stdout)
        self.assertIn("Target checker", result.stdout)
        self.assertIn("Evidence needed: finding code; operator decision; action taken", result.stdout)
        self.assertIn("scripts/check_pre_tool_use_preflight_samples.py", result.stdout)
        self.assertIn("scripts/plan_harness_sample_collection.py --gap-id GAP-GUARDRAIL-PREFLIGHT-WARNING", result.stdout)
        self.assertIn("scripts/check_harness_placeholder_replacement.py <candidate-jsonl>", result.stdout)
        self.assertIn("## P1 GAP-RUNTIME-STAGE-CHECKPOINT-RESUME", result.stdout)
        self.assertIn("Metric: accepted cross-task resume samples", result.stdout)
        self.assertIn(
            "Readiness metric delta: ledger accepted real=2; accepted cross-task resume samples=0/2",
            result.stdout,
        )
        self.assertIn("Capture gate: `requires-cross-task-resume`", result.stdout)

    def test_capture_focus_cli_empty_scope_is_explicit(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "check_harness_pending_samples.py"),
                "--gap-id",
                "GAP-WORKFLOW-TASK-PROFILE-AUDIT",
                "--capture-focus",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("# Pending Harness Next Capture Focus", result.stdout)
        self.assertIn("Scope gaps: GAP-WORKFLOW-TASK-PROFILE-AUDIT", result.stdout)
        self.assertIn("Focus area filter: all", result.stdout)
        self.assertIn("Focus priority filter: all", result.stdout)
        self.assertIn("Focus ledger-action filter: all", result.stdout)
        self.assertIn("Focus capture-gate filter: all", result.stdout)
        self.assertIn("Focus readiness filter: all", result.stdout)
        self.assertIn("Focus entries: 0/0", result.stdout)
        self.assertIn("Focus limit: 5", result.stdout)
        self.assertIn("Focus truncated: false", result.stdout)
        self.assertIn("Focus shown priorities: {}", result.stdout)
        self.assertIn("Focus available priorities: {}", result.stdout)
        self.assertIn("Focus shown areas: {}", result.stdout)
        self.assertIn("Focus available areas: {}", result.stdout)
        self.assertIn("Focus shown ledger actions: {}", result.stdout)
        self.assertIn("Focus available ledger actions: {}", result.stdout)
        self.assertIn("Focus shown capture gates: {}", result.stdout)
        self.assertIn("Focus available capture gates: {}", result.stdout)
        self.assertIn("Focus shown readiness: {}", result.stdout)
        self.assertIn("Focus available readiness: {}", result.stdout)
        self.assertIn("Focus hidden gap ids: <none>", result.stdout)
        self.assertIn("No next capture focus entries matched the selected scope/filter.", result.stdout)

    def test_capture_focus_cli_limit_zero_expands_all_matching_lanes(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "check_harness_pending_samples.py"),
                "--capture-focus",
                "--capture-focus-limit",
                "0",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("Focus entries: 15/15", result.stdout)
        self.assertIn("Focus limit: all", result.stdout)
        self.assertIn("Focus truncated: false", result.stdout)
        self.assertIn("Focus shown priorities: {'P0': 1, 'P1': 6, 'P2': 7, 'P3': 1}", result.stdout)
        self.assertIn("Focus shown areas: {'agentic-red-team': 4", result.stdout)
        self.assertIn(
            "Focus shown ledger actions: {'append-new-pending-slot': 13, 'fill-existing-placeholder': 2}",
            result.stdout,
        )
        self.assertIn("Focus shown capture gates: {'replace-placeholder-after-real-event': 2", result.stdout)
        self.assertIn(
            "Focus shown readiness: {'needs-first-real-sample': 14, 'needs-more-real-samples': 1}",
            result.stdout,
        )
        self.assertIn("Focus hidden gap ids: <none>", result.stdout)
        self.assertIn("## P3 GAP-TRACE-REMOTE-INTEROP", result.stdout)
        self.assertIn("## P2 GAP-AGENTIC-CASCADE-STOP", result.stdout)
        self.assertNotIn("## P2 GAP-WORKFLOW-TASK-PROFILE-AUDIT", result.stdout)

    def test_capture_focus_cli_area_filter_limits_matching_lanes(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "check_harness_pending_samples.py"),
                "--capture-focus",
                "--capture-focus-area",
                "agentic-red-team",
                "--capture-focus-limit",
                "0",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("Focus area filter: agentic-red-team", result.stdout)
        self.assertIn("Focus priority filter: all", result.stdout)
        self.assertIn("Focus ledger-action filter: all", result.stdout)
        self.assertIn("Focus readiness filter: all", result.stdout)
        self.assertIn("Focus entries: 4/4", result.stdout)
        self.assertIn("Focus available areas: {'agentic-red-team': 4}", result.stdout)
        self.assertIn("## P2 GAP-AGENTIC-CASCADE-STOP", result.stdout)
        self.assertIn("Area: `agentic-red-team`", result.stdout)
        self.assertNotIn("## P2 GAP-WORKFLOW-SIMPLE-SKIP", result.stdout)
        self.assertNotIn("## P3 GAP-TRACE-REMOTE-INTEROP", result.stdout)

    def test_capture_focus_cli_priority_filter_limits_matching_lanes(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "check_harness_pending_samples.py"),
                "--capture-focus",
                "--capture-focus-priority",
                "P2",
                "--capture-focus-limit",
                "0",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("Focus priority filter: P2", result.stdout)
        self.assertIn("Focus area filter: all", result.stdout)
        self.assertIn("Focus ledger-action filter: all", result.stdout)
        self.assertIn("Focus readiness filter: all", result.stdout)
        self.assertIn("Focus entries: 7/7", result.stdout)
        self.assertIn("Focus available areas: {'agentic-red-team': 4, 'workflow-skills': 3}", result.stdout)
        self.assertIn("Focus available priorities: {'P2': 7}", result.stdout)
        self.assertIn("## P2 GAP-AGENTIC-CASCADE-STOP", result.stdout)
        self.assertIn("## P2 GAP-WORKFLOW-SIMPLE-SKIP", result.stdout)
        self.assertNotIn("## P1 ", result.stdout)
        self.assertNotIn("## P3 ", result.stdout)

    def test_capture_focus_cli_ledger_action_filter_limits_matching_lanes(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "check_harness_pending_samples.py"),
                "--capture-focus",
                "--capture-focus-ledger-action",
                "fill-existing-placeholder",
                "--capture-focus-limit",
                "0",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("Focus area filter: all", result.stdout)
        self.assertIn("Focus priority filter: all", result.stdout)
        self.assertIn("Focus ledger-action filter: fill-existing-placeholder", result.stdout)
        self.assertIn("Focus capture-gate filter: all", result.stdout)
        self.assertIn("Focus readiness filter: all", result.stdout)
        self.assertIn("Focus entries: 2/2", result.stdout)
        self.assertIn("Focus available areas: {'ai-guardrail': 1, 'runtime-durability': 1}", result.stdout)
        self.assertIn("Focus available ledger actions: {'fill-existing-placeholder': 2}", result.stdout)
        self.assertIn("## P0 GAP-GUARDRAIL-PREFLIGHT-WARNING", result.stdout)
        self.assertIn("## P1 GAP-RUNTIME-LOOP-SCOPE-WARNING", result.stdout)
        self.assertNotIn("append-new-pending-slot", result.stdout)

    def test_capture_focus_cli_capture_gate_filter_limits_matching_lanes(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "check_harness_pending_samples.py"),
                "--capture-focus",
                "--capture-focus-gate",
                "requires-approved-remote-interop",
                "--capture-focus-limit",
                "0",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("Focus area filter: all", result.stdout)
        self.assertIn("Focus priority filter: all", result.stdout)
        self.assertIn("Focus ledger-action filter: all", result.stdout)
        self.assertIn("Focus capture-gate filter: requires-approved-remote-interop", result.stdout)
        self.assertIn("Focus readiness filter: all", result.stdout)
        self.assertIn("Focus entries: 1/1", result.stdout)
        self.assertIn("Focus available capture gates: {'requires-approved-remote-interop': 1}", result.stdout)
        self.assertIn("## P3 GAP-TRACE-REMOTE-INTEROP", result.stdout)
        self.assertIn("Capture gate: `requires-approved-remote-interop`", result.stdout)
        self.assertNotIn("GAP-RUNTIME-STAGE-CHECKPOINT-RESUME", result.stdout)

    def test_capture_focus_cli_readiness_filter_limits_matching_lanes(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "check_harness_pending_samples.py"),
                "--capture-focus",
                "--capture-focus-readiness",
                "needs-more-real-samples",
                "--capture-focus-limit",
                "0",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("Focus readiness filter: needs-more-real-samples", result.stdout)
        self.assertIn("Focus entries: 1/1", result.stdout)
        self.assertIn("Focus shown readiness: {'needs-more-real-samples': 1}", result.stdout)
        self.assertIn("Focus available readiness: {'needs-more-real-samples': 1}", result.stdout)
        self.assertIn("## P1 GAP-TRACE-LOCAL-SUMMARY-BURNIN", result.stdout)
        self.assertIn("Readiness: `needs-more-real-samples`", result.stdout)
        self.assertNotIn("## P3 GAP-TRACE-REMOTE-INTEROP", result.stdout)

    def test_cli_lists_ready_upgrade_decision_gaps_separately(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "check_harness_pending_samples.py"),
                "--include-future",
                "--include-accepted",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn(
            "- ready upgrade-decision gaps: ['GAP-AGENTIC-SANDBOX-HONESTY', 'GAP-GUARDRAIL-SOURCE-BOUNDARY', "
            "'GAP-SEC-CONTROL-MATRIX-BURNIN', 'GAP-WORKFLOW-TASK-PROFILE-AUDIT']",
            result.stdout,
        )
        self.assertIn("- ready upgrade-decision next evidence by gap:", result.stdout)
        self.assertIn("native sandbox, hosted trace, MCP, A2A, or external-provider boundary evidence", result.stdout)
        self.assertIn("- queued readiness metric rows: 20", result.stdout)
        self.assertIn(
            "- accepted real/readiness metric deltas: {'GAP-RUNTIME-STAGE-CHECKPOINT-RESUME': "
            "'ledger accepted real=2; accepted cross-task resume samples=0/2'",
            result.stdout,
        )
        self.assertIn("- next capture focus:", result.stdout)
        self.assertIn(f"hidden gap ids: {', '.join(DEFAULT_HIDDEN_CAPTURE_FOCUS_GAP_IDS)}", result.stdout)
        self.assertIn("P0 GAP-GUARDRAIL-PREFLIGHT-WARNING", result.stdout)
        self.assertIn(
            "planner: `.codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
            "--gap-id GAP-GUARDRAIL-PREFLIGHT-WARNING --ledger-action fill-existing-placeholder --capture-card`",
            result.stdout,
        )
        self.assertIn(
            "intake: `.codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
            "--gap-id GAP-GUARDRAIL-PREFLIGHT-WARNING --ledger-action fill-existing-placeholder --summary`",
            result.stdout,
        )
        self.assertIn(
            "evidence needed: finding code; operator decision; action taken",
            result.stdout,
        )

    def test_cli_json_output_is_stable(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_harness_pending_samples.py"), "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn('"pending_by_gap"', result.stdout)
        self.assertIn('"scope_gap_ids"', result.stdout)
        self.assertIn('"pending_review_state_filter": "any"', result.stdout)
        self.assertIn('"pending_review_state_counts"', result.stdout)
        self.assertIn('"queued_ledger_action_counts"', result.stdout)
        self.assertIn('"actionable_ledger_action_counts"', result.stdout)
        self.assertIn('"actionable_with_placeholder_pending_count": 2', result.stdout)
        self.assertIn('"ready_upgrade_decision_gaps"', result.stdout)
        self.assertIn('"ready_upgrade_decision_next_evidence_by_gap"', result.stdout)
        self.assertIn('"GAP-WORKFLOW-TASK-PROFILE-AUDIT"', result.stdout)
        self.assertIn('"false-positive review for profile selection disputes"', result.stdout)
        self.assertIn('"accepted_real_by_gap"', result.stdout)
        self.assertIn('"queued_readiness_metrics_by_gap"', result.stdout)
        self.assertIn('"ledger_accepted_real_count": 2', result.stdout)
        self.assertIn('"accepted_real_readiness_metric_deltas"', result.stdout)
        self.assertIn('"ledger accepted real=2; accepted cross-task resume samples=0/2"', result.stdout)
        self.assertIn('"accepted_local_replay_by_gap"', result.stdout)
        self.assertIn('"review_cards"', result.stdout)
        self.assertIn('"next_capture_focus_count": 5', result.stdout)
        self.assertIn('"next_capture_focus_area_filter": []', result.stdout)
        self.assertIn('"next_capture_focus_priority_filter": []', result.stdout)
        self.assertIn('"next_capture_focus_ledger_action_filter": []', result.stdout)
        self.assertIn('"next_capture_focus_capture_gate_filter": []', result.stdout)
        self.assertIn('"next_capture_focus_readiness_filter": []', result.stdout)
        self.assertIn('"next_capture_focus_available_count": 15', result.stdout)
        self.assertIn('"next_capture_focus_limit": 5', result.stdout)
        self.assertIn('"next_capture_focus_truncated": true', result.stdout)
        self.assertIn('"next_capture_focus_hidden_gap_ids"', result.stdout)
        self.assertIn('"GAP-TRACE-REMOTE-INTEROP"', result.stdout)
        self.assertIn('"next_capture_focus_shown_priority_counts"', result.stdout)
        self.assertIn('"next_capture_focus_available_priority_counts"', result.stdout)
        self.assertIn('"next_capture_focus_shown_area_counts"', result.stdout)
        self.assertIn('"next_capture_focus_available_area_counts"', result.stdout)
        self.assertIn('"next_capture_focus_shown_ledger_action_counts"', result.stdout)
        self.assertIn('"next_capture_focus_available_ledger_action_counts"', result.stdout)
        self.assertIn('"next_capture_focus_shown_capture_gate_counts"', result.stdout)
        self.assertIn('"next_capture_focus_available_capture_gate_counts"', result.stdout)
        self.assertIn('"next_capture_focus_shown_readiness_counts"', result.stdout)
        self.assertIn('"next_capture_focus_available_readiness_counts"', result.stdout)
        self.assertIn('"next_capture_focus"', result.stdout)
        self.assertIn('"pending_slot_refs"', result.stdout)
        self.assertIn('"PRE-SAMPLE-2026-05-24-real-tool-call-pending', result.stdout)
        self.assertIn('"pending_review_blockers"', result.stdout)
        self.assertIn('"current_to_target": "0/2"', result.stdout)
        self.assertIn('"readiness_metric_delta"', result.stdout)
        self.assertIn('"ledger accepted real=2; accepted cross-task resume samples=0/2"', result.stdout)
        self.assertIn('"capture_gate": "replace-placeholder-after-real-event"', result.stdout)
        self.assertIn('"capture_gate_detail"', result.stdout)
        self.assertIn('"planner_command"', result.stdout)
        self.assertIn('"area": "ai-guardrail"', result.stdout)
        self.assertIn('"intake_command"', result.stdout)
        self.assertIn('"lane_review_command"', result.stdout)
        self.assertIn('"evidence_needed"', result.stdout)
        self.assertIn('"operator decision"', result.stdout)
        self.assertIn('"review_blockers"', result.stdout)
        self.assertIn('"replacement_review_command"', result.stdout)
        self.assertIn('"outcome_review_command"', result.stdout)
        self.assertIn("scripts/check_harness_placeholder_replacement.py <candidate-jsonl>", result.stdout)
        self.assertIn('"queued_with_pending_count": 2', result.stdout)
        self.assertIn('"actionable_without_pending_count": 13', result.stdout)
        self.assertIn('"queued_without_review_ready_pending_count": 19', result.stdout)
        self.assertIn('"actionable_without_review_ready_pending_count": 15', result.stdout)
        self.assertIn('"next_collection_lane_commands"', result.stdout)
        self.assertIn('"ledger_action": "fill-existing-placeholder"', result.stdout)
        self.assertIn("scripts/check_harness_placeholder_replacement.py <candidate-jsonl>", result.stdout)
        self.assertIn("scripts/check_harness_sample_append.py <candidate-jsonl>", result.stdout)
        self.assertIn("scripts/check_harness_pending_samples.py --review-state placeholder --review-cards", result.stdout)

    def test_cli_json_shows_approved_remote_interop_in_append_lane(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "check_harness_pending_samples.py"),
                "--include-future",
                "--include-accepted",
                "--json",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn('"contract_blocker_states": []', result.stdout)
        self.assertIn('"GAP-TRACE-REMOTE-INTEROP"', result.stdout)
        self.assertIn('"append-new-pending-slot"', result.stdout)
        self.assertIn('"actionable_sample_gap_count": 15', result.stdout)

    def test_cli_json_records_capture_focus_filters(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "check_harness_pending_samples.py"),
                "--json",
                "--capture-focus-area",
                "agentic-red-team",
                "--capture-focus-priority",
                "P2",
                "--capture-focus-ledger-action",
                "append-new-pending-slot",
                "--capture-focus-readiness",
                "needs-first-real-sample",
                "--capture-focus-limit",
                "0",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn('"next_capture_focus_area_filter": [', result.stdout)
        self.assertIn('"agentic-red-team"', result.stdout)
        self.assertIn('"next_capture_focus_priority_filter": [', result.stdout)
        self.assertIn('"P2"', result.stdout)
        self.assertIn('"next_capture_focus_ledger_action_filter": [', result.stdout)
        self.assertIn('"append-new-pending-slot"', result.stdout)
        self.assertIn('"next_capture_focus_readiness_filter": [', result.stdout)
        self.assertIn('"needs-first-real-sample"', result.stdout)
        self.assertIn('"next_capture_focus_count": 4', result.stdout)
        self.assertIn('"next_capture_focus_available_count": 4', result.stdout)

    def test_cli_json_records_capture_focus_gate_filter(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "check_harness_pending_samples.py"),
                "--json",
                "--capture-focus-gate",
                "requires-approved-remote-interop",
                "--capture-focus-limit",
                "0",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn('"next_capture_focus_capture_gate_filter": [', result.stdout)
        self.assertIn('"requires-approved-remote-interop"', result.stdout)
        self.assertIn('"next_capture_focus_count": 1', result.stdout)
        self.assertIn('"next_capture_focus_available_count": 1', result.stdout)
        self.assertIn('"GAP-TRACE-REMOTE-INTEROP"', result.stdout)

    def test_cli_json_records_capture_focus_readiness_filter(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "check_harness_pending_samples.py"),
                "--json",
                "--capture-focus-readiness",
                "needs-more-real-samples",
                "--capture-focus-limit",
                "0",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn('"next_capture_focus_readiness_filter": [', result.stdout)
        self.assertIn('"needs-more-real-samples"', result.stdout)
        self.assertIn('"next_capture_focus_count": 1', result.stdout)
        self.assertIn('"next_capture_focus_available_count": 1', result.stdout)
        self.assertIn('"next_capture_focus_shown_readiness_counts"', result.stdout)
        self.assertIn('"next_capture_focus_available_readiness_counts"', result.stdout)
        self.assertIn('"GAP-TRACE-LOCAL-SUMMARY-BURNIN"', result.stdout)

    def test_cli_text_shows_no_contract_blockers_after_remote_interop_approval(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "check_harness_pending_samples.py"),
                "--include-future",
                "--include-accepted",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("- contract-blocked gaps: []", result.stdout)
        self.assertIn("GAP-TRACE-REMOTE-INTEROP", result.stdout)
        self.assertIn("append-new-pending-slot", result.stdout)

    def test_review_ready_lane_routes_to_outcome_review_gate(self) -> None:
        commands = harness_collection_lane_commands.review_existing_pending_slot_commands(
            {"GAP-GUARDRAIL-PREFLIGHT-WARNING"}
        )

        self.assertIn("--ledger-action review-existing-pending-slot", commands[0])
        self.assertIn("--ledger-action review-existing-pending-slot", commands[1])
        self.assertIn("--pending-state with-review-ready-pending", commands[1])
        self.assertIn("--review-state review-ready --review-cards", commands[2])
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_outcome.py <candidate-jsonl>",
            commands,
        )

    def test_review_ready_slot_gets_outcome_review_command(self) -> None:
        slot = harness_sample_slots.SampleSlot(
            gap_id="GAP-SEC-SCHEDULED-RUN",
            sample_id="GAP-SAMPLE-2026-05-24-sec-scheduled-run-real",
            outcome="pending",
            source_type="real-workflow-run",
            evidence_class="real",
            pending_review_state="review-ready",
            review_blockers=(),
            ledger_path="docs/ai/standards/harness-sample-gap-evidence.jsonl",
            line=2,
        )

        self.assertIn("check_harness_sample_outcome.py", harness_pending_review_cards.outcome_review_command(slot))

    def test_cli_gap_filter_outputs_single_review_card(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "check_harness_pending_samples.py"),
                "--gap-id",
                "GAP-GUARDRAIL-PREFLIGHT-WARNING",
                "--review-cards",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("Scope gaps: GAP-GUARDRAIL-PREFLIGHT-WARNING", result.stdout)
        self.assertIn("GAP-GUARDRAIL-PREFLIGHT-WARNING", result.stdout)
        self.assertNotIn("GAP-RUNTIME-LOOP-SCOPE-WARNING", result.stdout)

    def test_cli_text_reports_empty_filtered_scope(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "check_harness_pending_samples.py"),
                "--gap-id",
                "GAP-DOES-NOT-EXIST",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("scope gaps: ['GAP-DOES-NOT-EXIST']", result.stdout)
        self.assertIn(
            "No pending sample records or collection queue entries matched the selected scope/filter.",
            result.stdout,
        )
        self.assertIn("Empty pending-sample scope does not collect samples", result.stdout)
        self.assertIn("ERRORS: none", result.stdout)

    def test_cli_text_does_not_mark_approved_future_gap_as_empty(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "check_harness_pending_samples.py"),
                "--include-future",
                "--gap-id",
                "GAP-TRACE-REMOTE-INTEROP",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("- queued gaps: 1", result.stdout)
        self.assertIn("- contract-blocked gaps: []", result.stdout)
        self.assertIn("- actionable sample gaps: 1", result.stdout)
        self.assertIn("append-new-pending-slot", result.stdout)
        self.assertNotIn("No pending sample records or collection queue entries matched", result.stdout)

    def test_review_card_cli_output_reports_empty_filtered_scope(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "check_harness_pending_samples.py"),
                "--review-state",
                "review-ready",
                "--review-cards",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn("Review-state filter: review-ready", result.stdout)
        self.assertIn("No pending sample review cards matched the selected scope/filter.", result.stdout)
        self.assertIn("Pending rows remain unaccepted", result.stdout)

    def test_review_command_mapping_is_shared_for_sample_ledgers(self) -> None:
        self.assertIn(
            "check_harness_sample_gap_evidence.py",
            harness_sample_review_commands.review_command_for("docs/ai/standards/harness-sample-gap-evidence.jsonl"),
        )
        self.assertIn(
            "check_agentic_red_team_samples.py",
            harness_sample_review_commands.review_command_for("docs/ai/security/agentic-red-team-samples.jsonl"),
        )
        self.assertIn(
            "check_harness_future_work_contracts.py",
            harness_sample_review_commands.review_command_for("docs/ai/standards/harness-future-work-contracts.jsonl"),
        )
        self.assertEqual("unknown", harness_sample_review_commands.review_command_for("docs/ai/unknown.jsonl"))

    def test_dedicated_slots_prefer_explicit_gap_id_with_default_fallback(self) -> None:
        spec = harness_sample_slots.LEDGERS[0]

        self.assertEqual("GAP-GUARDRAIL-PREFLIGHT-WARNING", harness_sample_slots.gap_for_record(spec, {}))
        self.assertEqual(
            "GAP-GUARDRAIL-PREFLIGHT-WARNING",
            harness_sample_slots.gap_for_record(spec, {"gap_id": "GAP-GUARDRAIL-PREFLIGHT-WARNING"}),
        )

    def test_dedicated_slot_rejects_gap_id_mismatched_to_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            ledger = Path(temp_dir) / "preflight.jsonl"
            ledger.write_text(
                '{"schema_version":"pre-tool-use-preflight-sample/v1","id":"PRE-SAMPLE-test",'
                '"gap_id":"GAP-RUNTIME-LOOP-SCOPE-WARNING","outcome":"pending"}\n',
                encoding="utf-8",
            )
            spec = harness_sample_slots.LedgerSpec(
                "pretooluse-preflight-test",
                ledger,
                "pre-tool-use-preflight-sample/v1",
                "GAP-GUARDRAIL-PREFLIGHT-WARNING",
            )
            errors: list[str] = []
            warnings: list[str] = []

            slots = harness_sample_slots.load_slots(spec, {}, errors, warnings)

        self.assertEqual("GAP-RUNTIME-LOOP-SCOPE-WARNING", slots[0].gap_id)
        self.assertTrue(any("gap_id must be GAP-GUARDRAIL-PREFLIGHT-WARNING" in error for error in errors))

    def test_pending_review_blockers_treat_tbd_prefixed_values_as_placeholders(self) -> None:
        blockers = harness_sample_slots.pending_review_blockers_for_record(
            {
                "schema_version": "harness-sample-gap-evidence/v1",
                "outcome": "pending",
                "no_external_claim": True,
                "sample_summary": "TBD: bounded summary.",
                "decision": "TBD: owner decision.",
                "action_taken": ["none"],
            }
        )

        self.assertEqual(
            (
                "sample_summary must be meaningful text",
                "decision must be meaningful text",
                "action_taken must include a meaningful value",
            ),
            blockers,
        )

    def test_pending_review_blockers_include_sample_boundary_drift(self) -> None:
        blockers = harness_sample_slots.pending_review_blockers_for_record(
            {
                "schema_version": "harness-sample-gap-evidence/v1",
                "outcome": "pending",
                "source_type": "real-workflow-run",
                "local_only": True,
                "no_external_claim": False,
                "sample_summary": "Bounded summary.",
                "decision": "Keep pending.",
                "action_taken": ["Recorded bounded evidence."],
            }
        )

        self.assertEqual(
            (
                "no_external_claim must stay true for pending shared gap evidence",
                "real pending gap evidence must set local_only=false",
            ),
            blockers,
        )


if __name__ == "__main__":
    unittest.main()
