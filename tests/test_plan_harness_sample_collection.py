from __future__ import annotations

import json
import subprocess
import sys
import unittest
from io import StringIO
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import harness_sample_templates  # noqa: E402
import plan_harness_sample_collection  # noqa: E402


class HarnessSampleCollectionPlanTest(unittest.TestCase):
    def test_default_queue_excludes_accepted_local_and_includes_approved_future_work(self) -> None:
        items = plan_harness_sample_collection.build_queue()
        ids = {item.gap_id for item in items}
        by_id = {item.gap_id: item for item in items}

        self.assertIn("GAP-GUARDRAIL-PREFLIGHT-WARNING", ids)
        self.assertIn("GAP-RUNTIME-LOOP-SCOPE-WARNING", ids)
        self.assertEqual("review-upgrade-decision", by_id["GAP-WORKFLOW-TASK-PROFILE-AUDIT"].ledger_action)
        self.assertEqual("review-upgrade-decision", by_id["GAP-AGENTIC-SANDBOX-HONESTY"].ledger_action)
        self.assertEqual("review-upgrade-decision", by_id["GAP-GUARDRAIL-SOURCE-BOUNDARY"].ledger_action)
        self.assertEqual("review-upgrade-decision", by_id["GAP-SEC-CONTROL-MATRIX-BURNIN"].ledger_action)
        self.assertEqual(
            "ledger accepted real=2; accepted cross-task resume samples=0/2",
            by_id["GAP-RUNTIME-STAGE-CHECKPOINT-RESUME"].readiness_metric_delta,
        )
        self.assertEqual(
            "ledger accepted real=3; accepted real local trace summary task classes=1/3",
            by_id["GAP-TRACE-LOCAL-SUMMARY-BURNIN"].readiness_metric_delta,
        )
        self.assertNotIn("GAP-TRACE-OTLP-PILOT-BURNIN", ids)
        self.assertIn("GAP-TRACE-REMOTE-INTEROP", ids)
        self.assertEqual("append-new-pending-slot", by_id["GAP-TRACE-REMOTE-INTEROP"].ledger_action)
        self.assertEqual("real-interop-run", by_id["GAP-TRACE-REMOTE-INTEROP"].source_type_needed)
        self.assertEqual("requires-approved-remote-interop", by_id["GAP-TRACE-REMOTE-INTEROP"].capture_gate)

    def test_preflight_target_uses_dedicated_sample_ledger(self) -> None:
        item = next(
            item
            for item in plan_harness_sample_collection.build_queue()
            if item.gap_id == "GAP-GUARDRAIL-PREFLIGHT-WARNING"
        )

        self.assertEqual(item.priority, "P0")
        self.assertEqual(item.readiness, "ready-for-upgrade-discussion")
        self.assertEqual(item.source_metric, "accepted real preflight warning samples")
        self.assertEqual(item.accepted_count, 2)
        self.assertEqual(item.upgrade_discussion_target, 2)
        self.assertEqual("", item.readiness_metric_delta)
        self.assertEqual(item.target_artifact, "docs/ai/standards/harness-upgrade-decisions.jsonl")
        self.assertIn("check_harness_upgrade_decisions.py", item.review_command)
        self.assertEqual("not-applicable", item.replacement_review_command)
        self.assertEqual("not-applicable", item.append_review_command)
        self.assertEqual("not-applicable", item.outcome_review_command)
        self.assertIn("check_harness_upgrade_decision_candidate.py", item.upgrade_decision_review_command)
        self.assertEqual("not-applicable", item.contract_precondition_review_command)
        self.assertIsNone(item.contract_blocker_state)
        self.assertEqual(item.pending_slot_status, "none")
        self.assertEqual(item.pending_slot_count, 0)
        self.assertEqual((), item.pending_review_states)
        self.assertEqual((), item.pending_slot_refs)
        self.assertEqual((), item.pending_review_blockers)
        self.assertEqual("review-upgrade-decision", item.ledger_action)
        self.assertEqual(item.source_type_needed, "upgrade-decision")
        self.assertEqual("upgrade-decision-review", item.capture_gate)
        self.assertIn("bounded keep/promote/defer", item.capture_gate_detail)
        self.assertIn("accepted real warning samples: 2", item.current_evidence)

    def test_include_all_shows_local_and_future_boundaries(self) -> None:
        items = plan_harness_sample_collection.build_queue(include_future=True, include_accepted=True)
        by_id = {item.gap_id: item for item in items}

        self.assertEqual(by_id["GAP-TRACE-OTLP-PILOT-BURNIN"].readiness, "local-sample-only")
        self.assertEqual(by_id["GAP-TRACE-OTLP-PILOT-BURNIN"].accepted_count, 1)
        self.assertEqual(by_id["GAP-TRACE-OTLP-PILOT-BURNIN"].source_type_needed, "local-only")
        self.assertEqual(by_id["GAP-TRACE-OTLP-PILOT-BURNIN"].capture_gate, "no-sample-collection")
        self.assertEqual(by_id["GAP-TRACE-OTLP-PILOT-BURNIN"].ledger_action, "no-sample-collection")
        self.assertEqual(by_id["GAP-TRACE-OTLP-PILOT-BURNIN"].append_review_command, "not-applicable")
        self.assertEqual(by_id["GAP-TRACE-OTLP-PILOT-BURNIN"].contract_precondition_review_command, "not-applicable")
        self.assertIn("do not append another sample", by_id["GAP-TRACE-OTLP-PILOT-BURNIN"].boundary)
        self.assertEqual(by_id["GAP-TRACE-REMOTE-INTEROP"].source_type_needed, "real-interop-run")
        self.assertEqual(by_id["GAP-TRACE-REMOTE-INTEROP"].capture_gate, "requires-approved-remote-interop")
        self.assertEqual(by_id["GAP-TRACE-REMOTE-INTEROP"].ledger_action, "append-new-pending-slot")
        self.assertEqual(by_id["GAP-TRACE-REMOTE-INTEROP"].readiness, "needs-first-real-sample")
        self.assertEqual(
            "docs/ai/standards/harness-sample-gap-evidence.jsonl",
            by_id["GAP-TRACE-REMOTE-INTEROP"].target_artifact,
        )
        self.assertIn("check_harness_sample_gap_evidence.py", by_id["GAP-TRACE-REMOTE-INTEROP"].review_command)
        self.assertIn(
            "check_harness_sample_append.py <candidate-jsonl>",
            by_id["GAP-TRACE-REMOTE-INTEROP"].append_review_command,
        )
        self.assertEqual("not-applicable", by_id["GAP-TRACE-REMOTE-INTEROP"].contract_precondition_review_command)
        self.assertIn(
            "ADR-017",
            by_id["GAP-TRACE-REMOTE-INTEROP"].trigger,
        )
        self.assertEqual("not-applicable", by_id["GAP-TRACE-REMOTE-INTEROP"].replacement_review_command)
        self.assertEqual("not-applicable", by_id["GAP-TRACE-REMOTE-INTEROP"].outcome_review_command)
        self.assertEqual("not-applicable", by_id["GAP-TRACE-REMOTE-INTEROP"].upgrade_decision_review_command)
        self.assertIsNone(by_id["GAP-TRACE-REMOTE-INTEROP"].contract_blocker_state)
        self.assertIn("do not claim hosted", by_id["GAP-TRACE-REMOTE-INTEROP"].boundary)
        self.assertEqual(by_id["GAP-AGENTIC-CASCADE-STOP"].priority, "P2")
        self.assertEqual(by_id["GAP-AGENTIC-CASCADE-STOP"].source_type_needed, "real-incident")
        self.assertEqual(by_id["GAP-AGENTIC-CASCADE-STOP"].capture_gate, "requires-approved-bounded-incident")
        self.assertEqual(by_id["GAP-AGENTIC-CASCADE-STOP"].ledger_action, "append-new-pending-slot")
        self.assertEqual(
            "docs/ai/security/agentic-red-team-samples.jsonl",
            by_id["GAP-AGENTIC-CASCADE-STOP"].target_artifact,
        )
        self.assertIn("ADR-016", by_id["GAP-AGENTIC-CASCADE-STOP"].trigger)
        self.assertEqual(by_id["GAP-WORKFLOW-TASK-PROFILE-AUDIT"].readiness, "ready-for-upgrade-discussion")
        self.assertEqual(by_id["GAP-WORKFLOW-TASK-PROFILE-AUDIT"].source_type_needed, "upgrade-decision")
        self.assertEqual(by_id["GAP-WORKFLOW-TASK-PROFILE-AUDIT"].capture_gate, "upgrade-decision-review")
        self.assertEqual(by_id["GAP-WORKFLOW-TASK-PROFILE-AUDIT"].ledger_action, "review-upgrade-decision")
        self.assertEqual(
            "docs/ai/standards/harness-upgrade-decisions.jsonl",
            by_id["GAP-WORKFLOW-TASK-PROFILE-AUDIT"].target_artifact,
        )
        self.assertIn(
            "check_harness_upgrade_decisions.py",
            by_id["GAP-WORKFLOW-TASK-PROFILE-AUDIT"].review_command,
        )
        self.assertIn(
            "check_harness_upgrade_decision_candidate.py <candidate-jsonl>",
            by_id["GAP-WORKFLOW-TASK-PROFILE-AUDIT"].upgrade_decision_review_command,
        )
        self.assertEqual("not-applicable", by_id["GAP-WORKFLOW-TASK-PROFILE-AUDIT"].replacement_review_command)
        self.assertEqual("not-applicable", by_id["GAP-WORKFLOW-TASK-PROFILE-AUDIT"].append_review_command)
        self.assertEqual("not-applicable", by_id["GAP-WORKFLOW-TASK-PROFILE-AUDIT"].outcome_review_command)
        self.assertEqual("not-applicable", by_id["GAP-WORKFLOW-TASK-PROFILE-AUDIT"].contract_precondition_review_command)
        self.assertIn("do not append more samples", by_id["GAP-WORKFLOW-TASK-PROFILE-AUDIT"].boundary)
        self.assertIn(
            "more real tasks outside the initial simple/complex/0-1-stage profile set",
            by_id["GAP-WORKFLOW-TASK-PROFILE-AUDIT"].evidence_needed,
        )
        self.assertEqual(by_id["GAP-AGENTIC-SANDBOX-HONESTY"].readiness, "ready-for-upgrade-discussion")
        self.assertEqual(by_id["GAP-AGENTIC-SANDBOX-HONESTY"].source_type_needed, "upgrade-decision")
        self.assertEqual(by_id["GAP-AGENTIC-SANDBOX-HONESTY"].ledger_action, "review-upgrade-decision")
        self.assertIn(
            "native sandbox, hosted trace, MCP, A2A, or external-provider boundary evidence before promotion",
            by_id["GAP-AGENTIC-SANDBOX-HONESTY"].evidence_needed,
        )

    def test_area_filter_limits_queue(self) -> None:
        items = plan_harness_sample_collection.build_queue({"agentic-red-team"})
        by_id = {item.gap_id: item for item in items}

        self.assertTrue(items)
        self.assertTrue(all(item.area == "agentic-red-team" for item in items))
        self.assertEqual("upgrade-decision", by_id["GAP-AGENTIC-SANDBOX-HONESTY"].source_type_needed)
        self.assertTrue(all(item.source_type_needed in {"real-incident", "upgrade-decision"} for item in items))

    def test_gap_id_filter_limits_queue(self) -> None:
        items = plan_harness_sample_collection.build_queue(gap_ids={"GAP-GUARDRAIL-PREFLIGHT-WARNING"})

        self.assertEqual(1, len(items))
        self.assertEqual("GAP-GUARDRAIL-PREFLIGHT-WARNING", items[0].gap_id)

    def test_no_pending_slot_uses_append_new_pending_action(self) -> None:
        item = plan_harness_sample_collection.build_queue(gap_ids={"GAP-GUARDRAIL-CONFIRMATION"})[0]

        self.assertEqual("none", item.pending_slot_status)
        self.assertEqual("append-new-pending-slot", item.ledger_action)
        self.assertEqual("requires-user-confirmed-high-impact-action", item.capture_gate)
        self.assertIn("check_harness_sample_append.py", item.append_review_command)
        self.assertEqual("not-applicable", item.replacement_review_command)
        self.assertEqual("not-applicable", item.outcome_review_command)
        self.assertEqual("not-applicable", item.upgrade_decision_review_command)
        self.assertEqual("not-applicable", item.contract_precondition_review_command)

    def test_priority_filter_limits_queue(self) -> None:
        items = plan_harness_sample_collection.build_queue(
            priorities={"P0"},
            actionable_only=True,
            pending_state="without-review-ready-pending",
        )

        self.assertEqual([], [item.gap_id for item in items])
        self.assertTrue(all(item.priority == "P0" for item in items))

    def test_ledger_action_filter_targets_placeholder_fill_lane(self) -> None:
        items = plan_harness_sample_collection.build_queue(
            actionable_only=True,
            ledger_actions={"fill-existing-placeholder"},
        )

        self.assertEqual(
            ["GAP-RUNTIME-LOOP-SCOPE-WARNING"],
            [item.gap_id for item in items],
        )
        self.assertTrue(all(item.ledger_action == "fill-existing-placeholder" for item in items))

    def test_ledger_action_filter_targets_contract_preconditions(self) -> None:
        items = plan_harness_sample_collection.build_queue(
            include_future=True,
            ledger_actions={"define-contract-precondition"},
        )

        self.assertEqual(
            [],
            sorted(item.gap_id for item in items),
        )

    def test_ledger_action_filter_targets_local_only_no_collection(self) -> None:
        items = plan_harness_sample_collection.build_queue(
            include_accepted=True,
            ledger_actions={"no-sample-collection"},
        )

        self.assertEqual(["GAP-TRACE-OTLP-PILOT-BURNIN"], [item.gap_id for item in items])
        self.assertEqual("local-only", items[0].source_type_needed)

    def test_ledger_action_filter_targets_ready_gap_upgrade_decision(self) -> None:
        items = plan_harness_sample_collection.build_queue(
            ledger_actions={"review-upgrade-decision"},
        )

        self.assertEqual(
            [
                "GAP-GUARDRAIL-PREFLIGHT-WARNING",
                "GAP-GUARDRAIL-SOURCE-BOUNDARY",
                "GAP-SEC-CONTROL-MATRIX-BURNIN",
                "GAP-AGENTIC-SANDBOX-HONESTY",
                "GAP-WORKFLOW-SIMPLE-SKIP",
                "GAP-WORKFLOW-TASK-PROFILE-AUDIT",
            ],
            [item.gap_id for item in items],
        )
        self.assertTrue(all(item.source_type_needed == "upgrade-decision" for item in items))
        self.assertTrue(
            all(item.target_artifact == "docs/ai/standards/harness-upgrade-decisions.jsonl" for item in items)
        )
        by_id = {item.gap_id: item for item in items}
        self.assertIn("source-boundary samples from PRD", "\n".join(by_id["GAP-GUARDRAIL-SOURCE-BOUNDARY"].evidence_needed))
        self.assertIn("reviewer cost evidence", "\n".join(by_id["GAP-SEC-CONTROL-MATRIX-BURNIN"].evidence_needed))

    def test_capture_gate_filter_targets_real_event_preconditions(self) -> None:
        items = plan_harness_sample_collection.build_queue(
            include_future=True,
            capture_gates={"requires-cross-task-resume", "requires-approved-remote-interop"},
        )

        self.assertEqual(
            ["GAP-RUNTIME-STAGE-CHECKPOINT-RESUME", "GAP-TRACE-REMOTE-INTEROP"],
            [item.gap_id for item in items],
        )
        self.assertEqual(
            ["requires-cross-task-resume", "requires-approved-remote-interop"],
            [item.capture_gate for item in items],
        )

    def test_readiness_filter_targets_first_sample_blockers(self) -> None:
        items = plan_harness_sample_collection.build_queue(
            include_future=True,
            include_accepted=True,
            readinesses={"needs-first-real-sample"},
        )

        self.assertEqual(11, len(items))
        self.assertTrue(all(item.readiness == "needs-first-real-sample" for item in items))
        self.assertIn("GAP-TRACE-REMOTE-INTEROP", {item.gap_id for item in items})
        self.assertNotIn("GAP-TRACE-LOCAL-SUMMARY-BURNIN", {item.gap_id for item in items})
        self.assertNotIn("GAP-WORKFLOW-TASK-PROFILE-AUDIT", {item.gap_id for item in items})
        by_id = {item.gap_id: item for item in items}
        self.assertEqual(
            "ledger accepted real=2; accepted cross-task resume samples=0/2",
            by_id["GAP-RUNTIME-STAGE-CHECKPOINT-RESUME"].readiness_metric_delta,
        )

    def test_readiness_filter_targets_more_sample_blockers(self) -> None:
        items = plan_harness_sample_collection.build_queue(
            include_future=True,
            include_accepted=True,
            readinesses={"needs-more-real-samples"},
        )

        self.assertEqual(
            ["GAP-GUARDRAIL-CONFIRMATION", "GAP-TRACE-LOCAL-SUMMARY-BURNIN"],
            [item.gap_id for item in items],
        )
        self.assertTrue(all(item.readiness == "needs-more-real-samples" for item in items))

    def test_readiness_cli_filter_reports_matching_capture_card(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/plan_harness_sample_collection.py",
                "--readiness",
                "needs-more-real-samples",
                "--capture-card",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertIn("GAP-TRACE-LOCAL-SUMMARY-BURNIN", result.stdout)
        self.assertIn("Readiness: needs-more-real-samples", result.stdout)
        self.assertIn(
            "Readiness metric delta: ledger accepted real=3; accepted real local trace summary task classes=1/3",
            result.stdout,
        )
        self.assertNotIn("GAP-TRACE-REMOTE-INTEROP", result.stdout)

    def test_local_sample_readiness_cli_filter_reports_no_collection_card(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/plan_harness_sample_collection.py",
                "--include-accepted",
                "--readiness",
                "local-sample-only",
                "--capture-card",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertIn("GAP-TRACE-OTLP-PILOT-BURNIN", result.stdout)
        self.assertIn("Readiness: local-sample-only", result.stdout)
        self.assertIn("Ledger action: `no-sample-collection`", result.stdout)
        self.assertIn("No sample collection action:", result.stdout)
        self.assertNotIn("GAP-TRACE-REMOTE-INTEROP", result.stdout)

    def test_capture_gate_cli_filter_reports_matching_capture_card(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/plan_harness_sample_collection.py",
                "--capture-gate",
                "requires-approved-remote-interop",
                "--capture-card",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertIn("GAP-TRACE-REMOTE-INTEROP", result.stdout)
        self.assertIn("Capture gate: `requires-approved-remote-interop`", result.stdout)
        self.assertNotIn("GAP-RUNTIME-STAGE-CHECKPOINT-RESUME", result.stdout)

    def test_actionable_without_pending_filter_targets_open_sample_slots(self) -> None:
        items = plan_harness_sample_collection.build_queue(
            include_future=True,
            include_accepted=True,
            actionable_only=True,
            pending_state="without-pending",
        )
        ids = {item.gap_id for item in items}

        self.assertEqual(12, len(items))
        self.assertIn("GAP-RUNTIME-STAGE-CHECKPOINT-RESUME", ids)
        self.assertIn("GAP-TRACE-LOCAL-SUMMARY-BURNIN", ids)
        self.assertIn("GAP-TRACE-REMOTE-INTEROP", ids)
        self.assertIn("GAP-AGENTIC-CASCADE-STOP", ids)
        self.assertNotIn("GAP-AGENTIC-SANDBOX-HONESTY", ids)
        self.assertNotIn("GAP-GUARDRAIL-SOURCE-BOUNDARY", ids)
        self.assertNotIn("GAP-SEC-CONTROL-MATRIX-BURNIN", ids)
        self.assertNotIn("GAP-WORKFLOW-SIMPLE-SKIP", ids)
        self.assertNotIn("GAP-WORKFLOW-TASK-PROFILE-AUDIT", ids)
        self.assertNotIn("GAP-GUARDRAIL-PREFLIGHT-WARNING", ids)
        self.assertNotIn("GAP-RUNTIME-LOOP-SCOPE-WARNING", ids)
        self.assertNotIn("GAP-TRACE-OTLP-PILOT-BURNIN", ids)
        self.assertTrue(all(plan_harness_sample_collection.is_actionable_sample_item(item) for item in items))

    def test_actionable_without_review_ready_filter_keeps_placeholder_slots_open(self) -> None:
        items = plan_harness_sample_collection.build_queue(
            include_future=True,
            include_accepted=True,
            actionable_only=True,
            pending_state="without-review-ready-pending",
        )
        ids = {item.gap_id for item in items}

        self.assertEqual(13, len(items))
        self.assertNotIn("GAP-GUARDRAIL-PREFLIGHT-WARNING", ids)
        self.assertIn("GAP-RUNTIME-LOOP-SCOPE-WARNING", ids)
        self.assertIn("GAP-RUNTIME-STAGE-CHECKPOINT-RESUME", ids)
        self.assertIn("GAP-TRACE-LOCAL-SUMMARY-BURNIN", ids)
        self.assertIn("GAP-TRACE-REMOTE-INTEROP", ids)
        self.assertIn("GAP-AGENTIC-CASCADE-STOP", ids)
        self.assertNotIn("GAP-AGENTIC-SANDBOX-HONESTY", ids)
        self.assertNotIn("GAP-GUARDRAIL-SOURCE-BOUNDARY", ids)
        self.assertNotIn("GAP-SEC-CONTROL-MATRIX-BURNIN", ids)
        self.assertNotIn("GAP-WORKFLOW-SIMPLE-SKIP", ids)
        self.assertNotIn("GAP-WORKFLOW-TASK-PROFILE-AUDIT", ids)
        self.assertNotIn("GAP-TRACE-OTLP-PILOT-BURNIN", ids)
        self.assertTrue(all(plan_harness_sample_collection.is_actionable_sample_item(item) for item in items))

    def test_actionable_with_pending_filter_targets_existing_pending_slots(self) -> None:
        items = plan_harness_sample_collection.build_queue(
            actionable_only=True,
            pending_state="with-pending",
        )

        self.assertEqual(
            [
                "GAP-RUNTIME-LOOP-SCOPE-WARNING",
            ],
            [item.gap_id for item in items],
        )

    def test_actionable_pending_review_state_filters_split_review_ready_and_placeholder_slots(self) -> None:
        review_ready_items = plan_harness_sample_collection.build_queue(
            actionable_only=True,
            pending_state="with-review-ready-pending",
        )
        placeholder_items = plan_harness_sample_collection.build_queue(
            actionable_only=True,
            pending_state="with-placeholder-pending",
        )

        self.assertEqual([], [item.gap_id for item in review_ready_items])
        self.assertEqual(
            ["GAP-RUNTIME-LOOP-SCOPE-WARNING"],
            [item.gap_id for item in placeholder_items],
        )

    def test_capture_card_expands_evidence_and_boundary(self) -> None:
        items = plan_harness_sample_collection.build_queue(gap_ids={"GAP-RUNTIME-LOOP-SCOPE-WARNING"})

        with mock.patch("sys.stdout", new=StringIO()) as output:
            plan_harness_sample_collection.emit_capture_cards(items)

        text = output.getvalue()
        self.assertIn("# Harness Sample Capture Cards", text)
        self.assertIn("Metric: accepted real loop/scope warning samples", text)
        self.assertIn("Current / upgrade target: 0/2", text)
        self.assertIn("Target artifact: `docs/ai/standards/loop-scope-monitor-samples.jsonl`", text)
        self.assertIn("Review command: `.codex/hooks/run_with_repo_python.sh scripts/check_loop_scope_monitor_samples.py`", text)
        self.assertIn(
            "Lane review command: `.codex/hooks/run_with_repo_python.sh "
            "scripts/check_harness_placeholder_replacement.py <candidate-jsonl>`",
            text,
        )
        self.assertIn("Pending slots: `placeholder` (1)", text)
        self.assertIn("Ledger action: `fill-existing-placeholder`", text)
        self.assertIn(
            "Pending slot refs: LOOP-SAMPLE-2026-05-24-real-long-session-pending @ "
            "docs/ai/standards/loop-scope-monitor-samples.jsonl:2",
            text,
        )
        self.assertIn("Pending review blockers: triggered_findings must include a meaningful value", text)
        self.assertIn("Capture gate: `replace-placeholder-after-real-event`", text)
        self.assertIn("matching real event", text)
        self.assertIn("monitor recommendation", text)
        self.assertIn("no raw runtime paths", text)

    def test_upgrade_decision_capture_card_expands_next_evidence(self) -> None:
        items = plan_harness_sample_collection.build_queue(
            gap_ids={"GAP-WORKFLOW-TASK-PROFILE-AUDIT"},
            ledger_actions={"review-upgrade-decision"},
        )

        with mock.patch("sys.stdout", new=StringIO()) as output:
            plan_harness_sample_collection.emit_capture_cards(items)

        text = output.getvalue()
        self.assertIn("Ledger action: `review-upgrade-decision`", text)
        self.assertIn("Capture gate: `upgrade-decision-review`", text)
        self.assertIn("Next evidence needed:", text)
        self.assertIn("more real tasks outside the initial simple/complex/0-1-stage profile set", text)
        self.assertIn("false-positive review for profile selection disputes", text)
        self.assertNotIn("Evidence to capture:", text)

    def test_markdown_queue_includes_review_command(self) -> None:
        items = plan_harness_sample_collection.build_queue(gap_ids={"GAP-GUARDRAIL-PREFLIGHT-WARNING"})

        with mock.patch("sys.stdout", new=StringIO()) as output:
            plan_harness_sample_collection.emit_markdown(items)

        text = output.getvalue()
        self.assertIn("- queued gaps: 1", text)
        self.assertIn("- priority counts: P0=1", text)
        self.assertIn("- readiness counts: ready-for-upgrade-discussion=1", text)
        self.assertIn("- pending slot status counts: none=1", text)
        self.assertIn("- ledger action counts: review-upgrade-decision=1", text)
        self.assertIn("- capture gate counts: upgrade-decision-review=1", text)
        self.assertIn("Review command", text)
        self.assertIn("Lane review command", text)
        self.assertIn("Metric delta", text)
        self.assertIn("Pending slots", text)
        self.assertIn("Ledger action", text)
        self.assertIn("none (0)", text)
        self.assertIn("check_harness_upgrade_decisions.py", text)
        self.assertIn("check_harness_upgrade_decision_candidate.py <candidate-jsonl>", text)

    def test_markdown_queue_summary_counts_default_lanes(self) -> None:
        items = plan_harness_sample_collection.build_queue()

        with mock.patch("sys.stdout", new=StringIO()) as output:
            plan_harness_sample_collection.emit_markdown(items)

        text = output.getvalue()
        self.assertIn("- queued gaps: 19", text)
        self.assertIn("- priority counts: P0=1, P1=8, P2=9, P3=1", text)
        self.assertIn(
            "- readiness counts: needs-first-real-sample=11, needs-more-real-samples=2, ready-for-upgrade-discussion=6",
            text,
        )
        self.assertIn("- pending slot status counts: none=18, placeholder=1", text)
        self.assertIn(
            "- ledger action counts: append-new-pending-slot=12, fill-existing-placeholder=1, review-upgrade-decision=6",
            text,
        )
        self.assertIn("replace-placeholder-after-real-event=1", text)
        self.assertIn("upgrade-decision-review=6", text)

    def test_empty_filtered_capture_card_reports_empty_state(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/plan_harness_sample_collection.py",
                "--gap-id",
                "GAP-DOES-NOT-EXIST",
                "--capture-card",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertIn("# Harness Sample Capture Cards", result.stdout)
        self.assertIn("No harness sample collection items matched the selected scope/filter.", result.stdout)
        self.assertIn("does not accept evidence, reject evidence, or prove the gap is complete", result.stdout)

    def test_empty_sample_template_scope_returns_success_without_jsonl(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/plan_harness_sample_collection.py",
                "--gap-id",
                "GAP-DOES-NOT-EXIST",
                "--sample-template",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertEqual("", result.stdout)

    def test_remote_future_capture_card_names_remote_interop_evidence_collection(self) -> None:
        items = plan_harness_sample_collection.build_queue(
            gap_ids={"GAP-TRACE-REMOTE-INTEROP"},
            include_future=True,
        )

        with mock.patch("sys.stdout", new=StringIO()) as output:
            plan_harness_sample_collection.emit_capture_cards(items)

        text = output.getvalue()
        self.assertIn("Source type needed: `real-interop-run`", text)
        self.assertIn("Capture gate: `requires-approved-remote-interop`", text)
        self.assertIn("ADR-017 remote interop probe qualifies", text)
        self.assertIn(
            "Review command: `.codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_gap_evidence.py`",
            text,
        )
        self.assertIn(
            "Lane review command: `.codex/hooks/run_with_repo_python.sh "
            "scripts/check_harness_sample_append.py <candidate-jsonl>`",
            text,
        )
        self.assertIn("ADR-017", text)
        self.assertIn("future-work contract status: approved-for-sampling", text)
        self.assertIn("future-work missing ADR refs: false", text)
        self.assertIn("Allowed by contract record", text)
        self.assertIn("Evidence to capture:", text)
        self.assertNotIn("Contract fields to define:", text)

    def test_cli_json_exposes_lane_specific_review_commands(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/plan_harness_sample_collection.py",
                "--include-future",
                "--ledger-action",
                "define-contract-precondition",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        data = json.loads(result.stdout)

        self.assertEqual(
            set(),
            {item["gap_id"] for item in data},
        )

    def test_cli_json_exposes_readiness_metric_delta(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/plan_harness_sample_collection.py",
                "--capture-gate",
                "requires-cross-task-resume",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        data = json.loads(result.stdout)

        self.assertEqual(1, len(data))
        self.assertEqual("GAP-RUNTIME-STAGE-CHECKPOINT-RESUME", data[0]["gap_id"])
        self.assertEqual(
            "ledger accepted real=2; accepted cross-task resume samples=0/2",
            data[0]["readiness_metric_delta"],
        )

    def test_preflight_sample_template_is_upgrade_decision_draft(self) -> None:
        item = plan_harness_sample_collection.build_queue(gap_ids={"GAP-GUARDRAIL-PREFLIGHT-WARNING"})[0]

        template = harness_sample_templates.sample_template(item, "2026-05-24")

        self.assertEqual("harness-upgrade-decision/v1", template["schema_version"])
        self.assertEqual("HUD-2026-06-17-preflight-warning-keep-advisory", template["id"])
        self.assertEqual("GAP-GUARDRAIL-PREFLIGHT-WARNING", template["gap_id"])
        self.assertEqual("defer-until-more-evidence", template["decision"])
        self.assertEqual("ready-for-upgrade-discussion", template["readiness_at_decision"])
        self.assertEqual(2, template["accepted_count"])
        self.assertEqual(2, template["upgrade_discussion_target"])

    def test_loop_scope_sample_template_reuses_existing_placeholder_id(self) -> None:
        item = plan_harness_sample_collection.build_queue(gap_ids={"GAP-RUNTIME-LOOP-SCOPE-WARNING"})[0]

        template = harness_sample_templates.sample_template(item, "2026-05-24")

        self.assertEqual("loop-scope-monitor-sample/v1", template["schema_version"])
        self.assertEqual("LOOP-SAMPLE-2026-05-24-real-long-session-pending", template["id"])
        self.assertEqual("GAP-RUNTIME-LOOP-SCOPE-WARNING", template["gap_id"])
        self.assertEqual("pending", template["outcome"])
        self.assertEqual("real-session", template["source_type"])
        self.assertIn("Fill existing pending placeholder row", template["note"])
        self.assertIn("do not append a duplicate row", template["note"])

    def test_generic_sample_template_routes_guardrail_confirmation_to_user_action(self) -> None:
        item = plan_harness_sample_collection.build_queue(gap_ids={"GAP-GUARDRAIL-CONFIRMATION"})[0]

        template = harness_sample_templates.sample_template(item, "2026-05-24")

        self.assertEqual("harness-sample-gap-evidence/v1", template["schema_version"])
        self.assertEqual("GAP-GUARDRAIL-CONFIRMATION", template["gap_id"])
        self.assertEqual("pending", template["outcome"])
        self.assertEqual("real-user-action", template["source_type"])

    def test_approved_remote_future_gap_template_is_pending_interop_evidence(self) -> None:
        item = plan_harness_sample_collection.build_queue(
            gap_ids={"GAP-TRACE-REMOTE-INTEROP"},
            include_future=True,
        )[0]

        template = harness_sample_templates.sample_template(item, "2026-05-24")

        self.assertEqual("harness-sample-gap-evidence/v1", template["schema_version"])
        self.assertEqual("GAP-TRACE-REMOTE-INTEROP", template["gap_id"])
        self.assertEqual("pending", template["outcome"])
        self.assertEqual("real-interop-run", template["source_type"])
        self.assertEqual("external-test-endpoint", template["endpoint_scope"])
        self.assertEqual("not-sent", template["remote_status"])
        self.assertIs(False, template["network_exported"])
        self.assertIs(True, template["no_external_claim"])

    def test_ready_gap_template_is_upgrade_decision_draft(self) -> None:
        item = plan_harness_sample_collection.build_queue(
            gap_ids={"GAP-WORKFLOW-TASK-PROFILE-AUDIT"},
        )[0]

        template = harness_sample_templates.sample_template(item, "2026-05-24")

        self.assertEqual("harness-upgrade-decision/v1", template["schema_version"])
        self.assertEqual("HUD-2026-05-24-task-profile-audit-keep-advisory", template["id"])
        self.assertEqual("GAP-WORKFLOW-TASK-PROFILE-AUDIT", template["gap_id"])
        self.assertEqual("defer-until-more-evidence", template["decision"])
        self.assertEqual("ready-for-upgrade-discussion", template["readiness_at_decision"])
        self.assertEqual(3, template["accepted_count"])
        self.assertEqual(3, template["upgrade_discussion_target"])
        self.assertIn("more real tasks outside", "\n".join(item.next_evidence_needed))
        self.assertIn("docs/ai/standards/task-profile-audit-sample.jsonl", template["evidence_refs"])
        self.assertIn("next_evidence_needed", template)
        self.assertIn("more real tasks outside", "\n".join(template["next_evidence_needed"]))
        self.assertIs(True, template["no_raw_runtime"])

    def test_red_team_ready_gap_template_uses_red_team_evidence_refs(self) -> None:
        item = plan_harness_sample_collection.build_queue(
            gap_ids={"GAP-AGENTIC-SANDBOX-HONESTY"},
        )[0]

        template = harness_sample_templates.sample_template(item, "2026-05-25")

        self.assertEqual("harness-upgrade-decision/v1", template["schema_version"])
        self.assertEqual("HUD-2026-05-25-sandbox-honesty-keep-advisory", template["id"])
        self.assertEqual("GAP-AGENTIC-SANDBOX-HONESTY", template["gap_id"])
        self.assertEqual("defer-until-more-evidence", template["decision"])
        self.assertEqual(2, template["accepted_count"])
        self.assertEqual(2, template["upgrade_discussion_target"])
        self.assertIn("docs/ai/security/agentic-red-team-samples.jsonl", template["evidence_refs"])
        self.assertIn("external-provider boundary evidence", "\n".join(template["next_evidence_needed"]))
        self.assertNotIn("docs/ai/standards/task-profile-audit-sample.jsonl", template["evidence_refs"])

    def test_approved_agentic_future_gap_template_is_red_team_pending_evidence(self) -> None:
        item = plan_harness_sample_collection.build_queue(
            gap_ids={"GAP-AGENTIC-CASCADE-STOP"},
            include_future=True,
        )[0]

        template = harness_sample_templates.sample_template(item, "2026-05-24")

        self.assertEqual("agentic-red-team-sample/v1", template["schema_version"])
        self.assertEqual("GAP-AGENTIC-CASCADE-STOP", item.gap_id)
        self.assertEqual("real-incident", template["source_type"])
        self.assertEqual("cascade-autonomy", template["risk_family"])
        self.assertEqual("pending", template["outcome"])


if __name__ == "__main__":
    unittest.main()
