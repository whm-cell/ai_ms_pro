from __future__ import annotations

import io
import json
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_harness_sample_intake_bundle  # noqa: E402
import harness_sample_templates  # noqa: E402


class HarnessSampleIntakeBundleTest(unittest.TestCase):
    def test_default_bundle_uses_current_sample_date(self) -> None:
        with patch.object(harness_sample_templates, "default_sampled_at", return_value="2026-05-25"):
            report = build_harness_sample_intake_bundle.build_report(gap_ids={"GAP-SEC-SCHEDULED-RUN"})

        self.assertEqual([], report.errors)
        self.assertEqual("2026-05-25", report.sampled_at)
        entry = report.targets[0].entries[0]
        self.assertEqual("GAP-SAMPLE-2026-05-25-sec-scheduled-run", entry.template["id"])
        self.assertEqual("2026-05-25", entry.template["sampled_at"])

    def test_default_bundle_groups_actionable_without_review_ready_pending_templates(self) -> None:
        report = build_harness_sample_intake_bundle.build_report("2026-05-24")
        ids = {entry.gap_id for target in report.targets for entry in target.entries}
        targets = {target.target_artifact: target.entry_count for target in report.targets}

        self.assertEqual([], report.errors)
        self.assertEqual(13, report.item_count)
        self.assertEqual(5, report.target_count)
        self.assertEqual({"P1": 6, "P2": 6, "P3": 1}, report.priority_counts)
        self.assertEqual({"none": 12, "placeholder": 1}, report.pending_slot_status_counts)
        self.assertEqual({"append-new-pending-slot": 12, "fill-existing-placeholder": 1}, report.ledger_action_counts)
        self.assertEqual({"needs-first-real-sample": 11, "needs-more-real-samples": 2}, report.readiness_counts)
        self.assertEqual(
            {
                "replace-placeholder-after-real-event": 1,
                "requires-approved-bounded-incident": 1,
                "requires-approved-remote-interop": 1,
                "requires-bounded-real-incident": 3,
                "requires-cross-task-resume": 1,
                "requires-distinct-task-class-report": 1,
                "requires-security-workflow-event": 2,
                "requires-user-confirmed-high-impact-action": 1,
                "requires-workflow-task-event": 2,
            },
            report.capture_gate_counts,
        )
        self.assertEqual({"placeholder": 13}, report.template_review_state_counts)
        self.assertEqual(6, report.schema_counts["harness-sample-gap-evidence/v1"])
        self.assertEqual(4, report.schema_counts["agentic-red-team-sample/v1"])
        self.assertEqual(1, report.schema_counts["local-trace-summary-sample/v1"])
        self.assertEqual(1, report.schema_counts["loop-scope-monitor-sample/v1"])
        self.assertEqual(1, report.schema_counts["stage-checkpoint-resume-sample/v1"])
        self.assertEqual(6, targets["docs/ai/standards/harness-sample-gap-evidence.jsonl"])
        self.assertEqual(4, targets["docs/ai/security/agentic-red-team-samples.jsonl"])
        self.assertEqual(1, targets["docs/ai/standards/loop-scope-monitor-samples.jsonl"])
        self.assertEqual(1, targets["docs/ai/standards/local-trace-summary-samples.jsonl"])
        self.assertEqual(1, targets["docs/ai/checkpoints/resume-samples.jsonl"])
        self.assertNotIn("docs/ai/standards/task-profile-audit-sample.jsonl", targets)
        self.assertNotIn("GAP-GUARDRAIL-PREFLIGHT-WARNING", ids)
        self.assertIn("GAP-RUNTIME-LOOP-SCOPE-WARNING", ids)
        self.assertIn("GAP-TRACE-LOCAL-SUMMARY-BURNIN", ids)
        self.assertIn("GAP-AGENTIC-CASCADE-STOP", ids)
        self.assertIn("GAP-TRACE-REMOTE-INTEROP", ids)
        self.assertNotIn("GAP-AGENTIC-SANDBOX-HONESTY", ids)
        self.assertNotIn("GAP-GUARDRAIL-SOURCE-BOUNDARY", ids)
        self.assertNotIn("GAP-WORKFLOW-SIMPLE-SKIP", ids)
        self.assertNotIn("GAP-TRACE-OTLP-PILOT-BURNIN", ids)
        entries = {entry.gap_id: entry for target in report.targets for entry in target.entries}
        self.assertEqual("placeholder", entries["GAP-RUNTIME-LOOP-SCOPE-WARNING"].pending_slot_status)
        self.assertIn(
            "check_harness_placeholder_replacement.py <candidate-jsonl>",
            entries["GAP-RUNTIME-LOOP-SCOPE-WARNING"].replacement_review_command,
        )
        self.assertEqual(
            "LOOP-SAMPLE-2026-05-24-real-long-session-pending",
            entries["GAP-RUNTIME-LOOP-SCOPE-WARNING"].template["id"],
        )
        self.assertEqual("none", entries["GAP-TRACE-LOCAL-SUMMARY-BURNIN"].pending_slot_status)
        self.assertEqual(
            "ledger accepted real=3; accepted real local trace summary task classes=1/3",
            entries["GAP-TRACE-LOCAL-SUMMARY-BURNIN"].readiness_metric_delta,
        )
        self.assertEqual("append-new-pending-slot", entries["GAP-TRACE-LOCAL-SUMMARY-BURNIN"].ledger_action)
        self.assertEqual("placeholder", entries["GAP-TRACE-LOCAL-SUMMARY-BURNIN"].template_review_state)
        self.assertIn(
            "observation_count/trace_record_count/trace_count must include real report counts",
            entries["GAP-TRACE-LOCAL-SUMMARY-BURNIN"].template_review_blockers,
        )
        self.assertIn("summary format", entries["GAP-TRACE-LOCAL-SUMMARY-BURNIN"].evidence_needed)
        self.assertEqual("not-applicable", entries["GAP-TRACE-LOCAL-SUMMARY-BURNIN"].replacement_review_command)
        self.assertEqual("not-applicable", entries["GAP-TRACE-LOCAL-SUMMARY-BURNIN"].outcome_review_command)
        self.assertIn(
            "check_harness_sample_append.py <candidate-jsonl>",
            entries["GAP-TRACE-LOCAL-SUMMARY-BURNIN"].append_review_command,
        )
        for target in report.targets:
            for entry in target.entries:
                self.assertEqual([], entry.validation_errors)
                self.assertEqual("pending", entry.template["outcome"])
                if entry.target_artifact != "docs/ai/security/agentic-red-team-samples.jsonl":
                    self.assertEqual(entry.gap_id, entry.template["gap_id"])

        checkpoint_entry = entries["GAP-RUNTIME-STAGE-CHECKPOINT-RESUME"]
        self.assertEqual("accepted cross-task resume samples", checkpoint_entry.source_metric)
        self.assertEqual(
            "ledger accepted real=2; accepted cross-task resume samples=0/2",
            checkpoint_entry.readiness_metric_delta,
        )
        self.assertEqual(0, checkpoint_entry.accepted_count)
        self.assertEqual(2, checkpoint_entry.upgrade_discussion_target)
        self.assertEqual("0/2", checkpoint_entry.current_to_target)
        self.assertEqual("requires-cross-task-resume", checkpoint_entry.capture_gate)
        self.assertEqual("placeholder", checkpoint_entry.template_review_state)
        self.assertIn(
            "stage checkpoint pending samples must replace the template checkpoint_id",
            checkpoint_entry.template_review_blockers,
        )
        self.assertIn(
            "avoided_rework must include a meaningful value",
            checkpoint_entry.template_review_blockers,
        )

    def test_gap_filter_limits_bundle(self) -> None:
        report = build_harness_sample_intake_bundle.build_report(
            "2026-05-24",
            {"GAP-WORKFLOW-TASK-PROFILE-AUDIT"},
        )

        self.assertEqual([], report.errors)
        self.assertEqual(0, report.item_count)
        self.assertEqual(0, report.target_count)

    def test_area_priority_and_pending_state_filters_limit_bundle(self) -> None:
        report = build_harness_sample_intake_bundle.build_report(
            "2026-05-24",
            areas={"ai-guardrail"},
            priorities={"P1"},
            pending_state="without-pending",
        )
        ids = {entry.gap_id for target in report.targets for entry in target.entries}

        self.assertEqual([], report.errors)
        self.assertEqual(1, report.item_count)
        self.assertEqual({"GAP-GUARDRAIL-CONFIRMATION"}, ids)
        self.assertEqual({"P1": 1}, report.priority_counts)
        self.assertEqual({"none": 1}, report.pending_slot_status_counts)
        self.assertEqual({"append-new-pending-slot": 1}, report.ledger_action_counts)

    def test_capture_gate_filter_limits_bundle(self) -> None:
        report = build_harness_sample_intake_bundle.build_report(
            "2026-05-24",
            capture_gates={"requires-cross-task-resume"},
        )
        ids = {entry.gap_id for target in report.targets for entry in target.entries}

        self.assertEqual([], report.errors)
        self.assertEqual(1, report.item_count)
        self.assertEqual({"GAP-RUNTIME-STAGE-CHECKPOINT-RESUME"}, ids)
        self.assertEqual({"requires-cross-task-resume": 1}, report.capture_gate_counts)
        self.assertEqual({"append-new-pending-slot": 1}, report.ledger_action_counts)

    def test_readiness_filter_limits_bundle(self) -> None:
        report = build_harness_sample_intake_bundle.build_report(
            "2026-05-24",
            readinesses={"needs-more-real-samples"},
        )
        ids = {entry.gap_id for target in report.targets for entry in target.entries}

        self.assertEqual([], report.errors)
        self.assertEqual(2, report.item_count)
        self.assertEqual({"GAP-GUARDRAIL-CONFIRMATION", "GAP-TRACE-LOCAL-SUMMARY-BURNIN"}, ids)
        self.assertEqual({"needs-more-real-samples": 2}, report.readiness_counts)
        self.assertEqual({"append-new-pending-slot": 2}, report.ledger_action_counts)

    def test_ledger_action_filter_limits_bundle_to_placeholder_fills(self) -> None:
        report = build_harness_sample_intake_bundle.build_report(
            "2026-05-24",
            ledger_actions={"fill-existing-placeholder"},
        )
        ids = {entry.gap_id for target in report.targets for entry in target.entries}

        self.assertEqual([], report.errors)
        self.assertEqual(1, report.item_count)
        self.assertEqual({"GAP-RUNTIME-LOOP-SCOPE-WARNING"}, ids)
        self.assertEqual({"fill-existing-placeholder": 1}, report.ledger_action_counts)
        self.assertEqual({"placeholder": 1}, report.template_review_state_counts)
        self.assertTrue(
            all(
                entry.pending_slot_status == "placeholder"
                for target in report.targets
                for entry in target.entries
            )
        )

    def test_ledger_action_filter_reports_empty_contract_preconditions_after_approval(self) -> None:
        report = build_harness_sample_intake_bundle.build_report(
            "2026-05-24",
            ledger_actions={"define-contract-precondition"},
        )

        self.assertEqual([], report.errors)
        self.assertEqual(0, report.item_count)
        self.assertEqual(0, report.target_count)
        self.assertEqual({}, report.priority_counts)
        self.assertEqual({}, report.pending_slot_status_counts)
        self.assertEqual({}, report.ledger_action_counts)
        self.assertEqual({}, report.capture_gate_counts)
        self.assertEqual({}, report.schema_counts)
        self.assertEqual({}, report.template_review_state_counts)

    def test_ledger_action_filter_includes_ready_gap_upgrade_decision(self) -> None:
        report = build_harness_sample_intake_bundle.build_report(
            "2026-05-24",
            ledger_actions={"review-upgrade-decision"},
        )
        entries = {entry.gap_id: entry for target in report.targets for entry in target.entries}

        self.assertEqual([], report.errors)
        self.assertEqual(6, report.item_count)
        self.assertEqual(1, report.target_count)
        self.assertEqual({"P0": 1, "P1": 2, "P2": 3}, report.priority_counts)
        self.assertEqual({"none": 6}, report.pending_slot_status_counts)
        self.assertEqual({"review-upgrade-decision": 6}, report.ledger_action_counts)
        self.assertEqual({"upgrade-decision-review": 6}, report.capture_gate_counts)
        self.assertEqual({"harness-upgrade-decision/v1": 6}, report.schema_counts)
        self.assertEqual({"not-applicable": 6}, report.template_review_state_counts)
        self.assertIn("GAP-GUARDRAIL-PREFLIGHT-WARNING", entries)
        self.assertIn("GAP-AGENTIC-SANDBOX-HONESTY", entries)
        self.assertIn("GAP-GUARDRAIL-SOURCE-BOUNDARY", entries)
        self.assertIn("GAP-SEC-CONTROL-MATRIX-BURNIN", entries)
        self.assertIn("GAP-WORKFLOW-SIMPLE-SKIP", entries)
        entry = entries["GAP-WORKFLOW-TASK-PROFILE-AUDIT"]
        self.assertEqual("docs/ai/standards/harness-upgrade-decisions.jsonl", entry.target_artifact)
        self.assertEqual("harness-upgrade-decision/v1", entry.schema_version)
        self.assertEqual("ready-for-upgrade-discussion", entry.readiness)
        self.assertEqual("review-upgrade-decision", entry.ledger_action)
        self.assertEqual("upgrade-decision-review", entry.capture_gate)
        self.assertIn("check_harness_upgrade_decisions.py", entry.review_command)
        self.assertEqual("not-applicable", entry.append_review_command)
        self.assertEqual("not-applicable", entry.replacement_review_command)
        self.assertEqual("not-applicable", entry.outcome_review_command)
        self.assertIn("check_harness_upgrade_decision_candidate.py <candidate-jsonl>", entry.upgrade_decision_review_command)
        self.assertEqual("not-applicable", entry.contract_precondition_review_command)
        self.assertIn(
            "more real tasks outside the initial simple/complex/0-1-stage profile set",
            entry.evidence_needed,
        )
        self.assertEqual("defer-until-more-evidence", entry.template["decision"])
        self.assertIn("next_evidence_needed", entry.template)
        self.assertIn("more real tasks outside", "\n".join(entry.template["next_evidence_needed"]))

    def test_ready_readiness_filter_includes_upgrade_decision_lane(self) -> None:
        report = build_harness_sample_intake_bundle.build_report(
            "2026-05-24",
            readinesses={"ready-for-upgrade-discussion"},
        )

        self.assertEqual([], report.errors)
        self.assertEqual(6, report.item_count)
        self.assertEqual({"ready-for-upgrade-discussion": 6}, report.readiness_counts)
        self.assertEqual({"review-upgrade-decision": 6}, report.ledger_action_counts)
        self.assertEqual({"upgrade-decision-review": 6}, report.capture_gate_counts)
        self.assertEqual({"harness-upgrade-decision/v1": 6}, report.schema_counts)

    def test_text_output_declares_stdout_only_and_no_ledger_writes(self) -> None:
        report = build_harness_sample_intake_bundle.build_report(
            "2026-05-24",
            {"GAP-WORKFLOW-TASK-PROFILE-AUDIT"},
        )
        output = io.StringIO()

        with redirect_stdout(output):
            build_harness_sample_intake_bundle.emit_text(report)

        text = output.getvalue()
        self.assertIn("stdout-only", text)
        self.assertIn("does not write ledgers", text)
        self.assertIn("- draft templates: 0", text)
        self.assertIn("- target artifacts: 0", text)
        self.assertIn("No harness sample intake entries matched the selected scope/filter.", text)
        self.assertIn("does not accept evidence, write ledgers, or prove the gap is complete", text)
        self.assertNotIn("append review command", text)
        self.assertNotIn("GAP-WORKFLOW-TASK-PROFILE-AUDIT", text)

    def test_summary_output_reports_empty_filtered_scope(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/build_harness_sample_intake_bundle.py",
                "--gap-id",
                "GAP-DOES-NOT-EXIST",
                "--summary",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertIn("# Harness Sample Intake Summary", result.stdout)
        self.assertIn("- draft templates: 0", result.stdout)
        self.assertIn("No harness sample intake entries matched the selected scope/filter.", result.stdout)
        self.assertIn("does not accept evidence, write ledgers, or prove the gap is complete", result.stdout)
        self.assertNotIn("| Priority | Gap |", result.stdout)

    def test_summary_output_can_filter_by_capture_gate(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/build_harness_sample_intake_bundle.py",
                "--capture-gate",
                "requires-approved-remote-interop",
                "--summary",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertIn("# Harness Sample Intake Summary", result.stdout)
        self.assertIn("- draft templates: 1", result.stdout)
        self.assertIn("GAP-TRACE-REMOTE-INTEROP", result.stdout)
        self.assertIn("`requires-approved-remote-interop`", result.stdout)
        self.assertNotIn("GAP-RUNTIME-STAGE-CHECKPOINT-RESUME", result.stdout)

    def test_text_output_marks_placeholder_fill_templates_as_replacements(self) -> None:
        report = build_harness_sample_intake_bundle.build_report(
            "2026-05-24",
            {"GAP-RUNTIME-LOOP-SCOPE-WARNING"},
        )
        output = io.StringIO()

        with redirect_stdout(output):
            build_harness_sample_intake_bundle.emit_text(report)

        text = output.getvalue()
        self.assertIn("ledger action: `fill-existing-placeholder`", text)
        self.assertIn("template write mode: replace existing pending placeholder row", text)
        self.assertIn("do not append duplicate", text)
        self.assertIn("replacement review command", text)
        self.assertIn("check_harness_placeholder_replacement.py <candidate-jsonl>", text)
        self.assertIn('"id":"LOOP-SAMPLE-2026-05-24-real-long-session-pending"', text)

    def test_cli_json_emits_machine_readable_report(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/build_harness_sample_intake_bundle.py",
                "--area",
                "runtime-durability",
                "--priority",
                "P1",
                "--ledger-action",
                "fill-existing-placeholder",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        data = json.loads(result.stdout)

        self.assertEqual(1, data["item_count"])
        self.assertEqual(1, data["target_count"])
        self.assertEqual({"P1": 1}, data["priority_counts"])
        self.assertEqual({"placeholder": 1}, data["pending_slot_status_counts"])
        self.assertEqual({"fill-existing-placeholder": 1}, data["ledger_action_counts"])
        self.assertEqual({"needs-first-real-sample": 1}, data["readiness_counts"])
        self.assertEqual({"replace-placeholder-after-real-event": 1}, data["capture_gate_counts"])
        self.assertEqual({"placeholder": 1}, data["template_review_state_counts"])
        self.assertEqual([], data["errors"])
        loop = next(
            entry
            for target in data["targets"]
            for entry in target["entries"]
            if entry["gap_id"] == "GAP-RUNTIME-LOOP-SCOPE-WARNING"
        )
        self.assertEqual("placeholder", loop["pending_slot_status"])
        self.assertEqual("fill-existing-placeholder", loop["ledger_action"])
        self.assertEqual(1, loop["pending_slot_count"])
        self.assertEqual("GAP-RUNTIME-LOOP-SCOPE-WARNING", loop["template"]["gap_id"])
        self.assertEqual("accepted real loop/scope warning samples", loop["source_metric"])
        self.assertEqual(0, loop["accepted_count"])
        self.assertEqual(2, loop["upgrade_discussion_target"])
        self.assertEqual("0/2", loop["current_to_target"])
        self.assertEqual("", loop["readiness_metric_delta"])
        self.assertEqual("replace-placeholder-after-real-event", loop["capture_gate"])
        self.assertIn("matching real event", loop["capture_gate_detail"])
        self.assertIn("check_loop_scope_monitor_samples.py", loop["review_command"])
        self.assertIn("check_harness_placeholder_replacement.py", loop["replacement_review_command"])
        self.assertEqual("not-applicable", loop["append_review_command"])
        self.assertEqual("not-applicable", loop["outcome_review_command"])
        self.assertEqual("not-applicable", loop["upgrade_decision_review_command"])
        self.assertEqual("not-applicable", loop["contract_precondition_review_command"])
        self.assertEqual("placeholder", loop["template_review_state"])
        self.assertIn("action_taken must include a meaningful value", loop["template_review_blockers"])
        self.assertIn("monitor recommendation", loop["evidence_needed"])
        self.assertEqual("placeholder", loop["pending_slots"][0]["review_state"])
        self.assertIn("review_blockers", loop["pending_slots"][0])

    def test_cli_json_reports_empty_contract_precondition_lane_after_approval(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/build_harness_sample_intake_bundle.py",
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
        self.assertEqual({}, data["ledger_action_counts"])
        self.assertEqual({}, data["capture_gate_counts"])
        self.assertEqual({}, data["template_review_state_counts"])
        self.assertEqual([], data["targets"])

    def test_cli_json_exposes_upgrade_decision_review_command(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/build_harness_sample_intake_bundle.py",
                "--ledger-action",
                "review-upgrade-decision",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        data = json.loads(result.stdout)
        entries = {entry["gap_id"]: entry for target in data["targets"] for entry in target["entries"]}
        entry = entries["GAP-WORKFLOW-TASK-PROFILE-AUDIT"]

        self.assertEqual("GAP-WORKFLOW-TASK-PROFILE-AUDIT", entry["gap_id"])
        self.assertEqual("review-upgrade-decision", entry["ledger_action"])
        self.assertEqual("upgrade-decision-review", entry["capture_gate"])
        self.assertEqual("not-applicable", entry["append_review_command"])
        self.assertEqual("not-applicable", entry["replacement_review_command"])
        self.assertEqual("not-applicable", entry["outcome_review_command"])
        self.assertIn("check_harness_upgrade_decision_candidate.py <candidate-jsonl>", entry["upgrade_decision_review_command"])
        self.assertEqual("not-applicable", entry["contract_precondition_review_command"])
        self.assertEqual("not-applicable", entry["template_review_state"])
        self.assertIn("more real tasks outside", "\n".join(entry["evidence_needed"]))

    def test_summary_renders_outcome_review_lane_when_present(self) -> None:
        base_report = build_harness_sample_intake_bundle.build_report(
            "2026-05-24",
            {"GAP-RUNTIME-LOOP-SCOPE-WARNING"},
        )
        base_target = base_report.targets[0]
        base_entry = base_target.entries[0]
        outcome_entry = replace(
            base_entry,
            ledger_action="review-existing-pending-slot",
            pending_slot_status="review-ready",
            replacement_review_command="not-applicable",
            append_review_command="not-applicable",
            outcome_review_command=(
                ".codex/hooks/run_with_repo_python.sh "
                "scripts/check_harness_sample_outcome.py <candidate-jsonl>"
            ),
        )
        report = replace(
            base_report,
            item_count=1,
            target_count=1,
            ledger_action_counts={"review-existing-pending-slot": 1},
            pending_slot_status_counts={"review-ready": 1},
            targets=[replace(base_target, entry_count=1, entries=[outcome_entry])],
        )
        output = io.StringIO()

        with redirect_stdout(output):
            build_harness_sample_intake_bundle.emit_summary(report)

        text = output.getvalue()
        self.assertIn("Pending Outcome Review", text)
        self.assertIn("GAP-RUNTIME-LOOP-SCOPE-WARNING", text)
        self.assertIn("LOOP-SAMPLE-2026-05-24-real-long-session-pending", text)
        self.assertIn("check_harness_sample_outcome.py <candidate-jsonl>", text)

    def test_text_output_marks_outcome_templates_as_existing_row_candidates(self) -> None:
        base_report = build_harness_sample_intake_bundle.build_report(
            "2026-05-24",
            {"GAP-RUNTIME-LOOP-SCOPE-WARNING"},
        )
        base_target = base_report.targets[0]
        base_entry = base_target.entries[0]
        outcome_entry = replace(
            base_entry,
            ledger_action="review-existing-pending-slot",
            pending_slot_status="review-ready",
            replacement_review_command="not-applicable",
            append_review_command="not-applicable",
            outcome_review_command=(
                ".codex/hooks/run_with_repo_python.sh "
                "scripts/check_harness_sample_outcome.py <candidate-jsonl>"
            ),
            template={**base_entry.template, "outcome": "rejected"},
        )
        report = replace(
            base_report,
            item_count=1,
            target_count=1,
            ledger_action_counts={"review-existing-pending-slot": 1},
            pending_slot_status_counts={"review-ready": 1},
            targets=[replace(base_target, entry_count=1, entries=[outcome_entry])],
        )
        output = io.StringIO()

        with redirect_stdout(output):
            build_harness_sample_intake_bundle.emit_text(report)

        text = output.getvalue()
        self.assertIn("template write mode: outcome candidate for existing pending row", text)
        self.assertIn("do not append duplicate evidence", text)
        self.assertIn('"outcome":"rejected"', text)

    def test_summary_cli_omits_template_bodies(self) -> None:
        result = subprocess.run(
            [sys.executable, "scripts/build_harness_sample_intake_bundle.py", "--summary"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertIn("# Harness Sample Intake Summary", result.stdout)
        self.assertIn("priority counts", result.stdout)
        self.assertIn("pending slot status counts", result.stdout)
        self.assertIn("ledger action counts", result.stdout)
        self.assertIn("capture gate counts", result.stdout)
        self.assertIn("readiness counts", result.stdout)
        self.assertIn("draft review state counts", result.stdout)
        self.assertIn(
            "| Priority | Gap | Readiness | Metric | Current / Target | Metric Delta | Pending slots | Ledger action | Target |",
            result.stdout,
        )
        self.assertIn(
            "accepted cross-task resume samples | 0/2 | ledger accepted real=2; accepted cross-task resume samples=0/2",
            result.stdout,
        )
        self.assertIn(
            "accepted real local trace summary task classes | 1/3 | ledger accepted real=3; accepted real local trace summary task classes=1/3",
            result.stdout,
        )
        self.assertIn("GAP-RUNTIME-LOOP-SCOPE-WARNING", result.stdout)
        self.assertIn("fill-existing-placeholder", result.stdout)
        self.assertIn("placeholder (1)", result.stdout)
        self.assertIn("Pending Slot Blockers", result.stdout)
        self.assertIn("Draft Template Review", result.stdout)
        self.assertIn("stage checkpoint pending samples must replace the template checkpoint_id", result.stdout)
        self.assertIn("triggered_findings must include a meaningful value", result.stdout)
        self.assertIn("Capture Gates", result.stdout)
        self.assertIn("requires-cross-task-resume", result.stdout)
        self.assertIn("replace-placeholder-after-real-event", result.stdout)
        self.assertIn("Capture Checklist", result.stdout)
        self.assertIn("finding code; monitor recommendation", result.stdout)
        self.assertIn("summary format; promotion count", result.stdout)
        self.assertIn("Placeholder Replacement Review", result.stdout)
        self.assertIn("check_harness_placeholder_replacement.py <candidate-jsonl>", result.stdout)
        self.assertIn("Pending Append Review", result.stdout)
        self.assertIn("check_harness_sample_append.py <candidate-jsonl>", result.stdout)
        self.assertIn("Review command", result.stdout)
        self.assertIn("check_loop_scope_monitor_samples.py", result.stdout)
        self.assertNotIn("```json", result.stdout)

    def test_summary_output_can_filter_by_readiness(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/build_harness_sample_intake_bundle.py",
                "--readiness",
                "needs-more-real-samples",
                "--summary",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertIn("# Harness Sample Intake Summary", result.stdout)
        self.assertIn("- draft templates: 2", result.stdout)
        self.assertIn("readiness counts: {'needs-more-real-samples': 2}", result.stdout)
        self.assertIn("GAP-GUARDRAIL-CONFIRMATION", result.stdout)
        self.assertIn("GAP-TRACE-LOCAL-SUMMARY-BURNIN", result.stdout)
        self.assertIn(
            "ledger accepted real=3; accepted real local trace summary task classes=1/3",
            result.stdout,
        )
        self.assertNotIn("GAP-TRACE-REMOTE-INTEROP", result.stdout)

    def test_summary_cli_reports_empty_contract_precondition_lane_after_approval(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/build_harness_sample_intake_bundle.py",
                "--ledger-action",
                "define-contract-precondition",
                "--summary",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertIn("- draft templates: 0", result.stdout)
        self.assertIn("No harness sample intake entries matched the selected scope/filter.", result.stdout)
        self.assertNotIn("Contract Precondition Review", result.stdout)
        self.assertNotIn("```json", result.stdout)

    def test_summary_cli_reports_upgrade_decision_lane(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/build_harness_sample_intake_bundle.py",
                "--ledger-action",
                "review-upgrade-decision",
                "--summary",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertIn("- draft templates: 6", result.stdout)
        self.assertIn("review-upgrade-decision", result.stdout)
        self.assertIn("GAP-GUARDRAIL-SOURCE-BOUNDARY", result.stdout)
        self.assertIn("GAP-GUARDRAIL-PREFLIGHT-WARNING", result.stdout)
        self.assertIn("GAP-SEC-CONTROL-MATRIX-BURNIN", result.stdout)
        self.assertIn("GAP-AGENTIC-SANDBOX-HONESTY", result.stdout)
        self.assertIn("GAP-WORKFLOW-SIMPLE-SKIP", result.stdout)
        self.assertIn("GAP-WORKFLOW-TASK-PROFILE-AUDIT", result.stdout)
        self.assertIn("docs/ai/standards/harness-upgrade-decisions.jsonl", result.stdout)
        self.assertIn("Upgrade Decision Review", result.stdout)
        self.assertIn("check_harness_upgrade_decision_candidate.py <candidate-jsonl>", result.stdout)
        self.assertIn("check_harness_upgrade_decisions.py", result.stdout)
        self.assertIn("source-boundary samples from PRD", result.stdout)
        self.assertIn("native sandbox, hosted trace, MCP, A2A", result.stdout)
        self.assertNotIn("```json", result.stdout)

    def test_summary_cli_can_filter_ready_upgrade_readiness(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/build_harness_sample_intake_bundle.py",
                "--readiness",
                "ready-for-upgrade-discussion",
                "--summary",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertIn("- draft templates: 6", result.stdout)
        self.assertIn("readiness counts: {'ready-for-upgrade-discussion': 6}", result.stdout)
        self.assertIn("Upgrade Decision Review", result.stdout)
        self.assertIn("check_harness_upgrade_decision_candidate.py <candidate-jsonl>", result.stdout)
        self.assertIn("GAP-WORKFLOW-SIMPLE-SKIP", result.stdout)
        self.assertIn("GAP-WORKFLOW-TASK-PROFILE-AUDIT", result.stdout)
        self.assertNotIn("```json", result.stdout)


if __name__ == "__main__":
    unittest.main()
