from __future__ import annotations

import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_harness_sample_templates  # noqa: E402
import harness_sample_outcome_templates  # noqa: E402
import harness_sample_templates  # noqa: E402
import plan_harness_sample_collection  # noqa: E402


def review_ready_item() -> plan_harness_sample_collection.CollectionItem:
    return plan_harness_sample_collection.CollectionItem(
        gap_id="GAP-SEC-SCHEDULED-RUN",
        area="security-evidence",
        priority="P1",
        readiness="needs-first-real-sample",
        source_metric="accepted real generic gap samples",
        accepted_count=0,
        upgrade_discussion_target=2,
        readiness_metric_delta="",
        target_artifact="docs/ai/standards/harness-sample-gap-evidence.jsonl",
        review_command=".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_gap_evidence.py",
        replacement_review_command="not-applicable",
        append_review_command="not-applicable",
        outcome_review_command=".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_outcome.py <candidate-jsonl>",
        upgrade_decision_review_command="not-applicable",
        contract_precondition_review_command="not-applicable",
        pending_slot_status="review-ready",
        pending_slot_count=1,
        pending_review_states=("review-ready",),
        pending_slot_refs=(
            "GAP-SAMPLE-2026-05-24-sec-scheduled-run-real @ "
            "docs/ai/standards/harness-sample-gap-evidence.jsonl:2",
        ),
        pending_review_blockers=(),
        ledger_action="review-existing-pending-slot",
        contract_blocker_state=None,
        source_type_needed="real-sample",
        capture_gate="requires-real-event",
        capture_gate_detail="Only a real event matching the trigger and evidence checklist qualifies.",
        trigger="Review existing pending row.",
        evidence_needed=["owner decision"],
        next_evidence_needed=[],
        current_evidence=["generic ledger records: 1"],
        boundary="Bounded evidence only.",
    )


def pending_generic_record() -> dict[str, object]:
    return {
        "schema_version": "harness-sample-gap-evidence/v1",
        "id": "GAP-SAMPLE-2026-05-24-sec-scheduled-run-real",
        "gap_id": "GAP-SEC-SCHEDULED-RUN",
        "sampled_at": "2026-05-24",
        "source_type": "real-workflow-run",
        "outcome": "pending",
        "local_only": False,
        "no_external_claim": True,
        "false_positive": False,
        "network_exported": False,
        "endpoint_scope": "none",
        "remote_status": "none",
        "sample_summary": "Scheduled security evidence workflow run captured bounded metadata.",
        "decision": "Owner review pending.",
        "boundary_note": "Bounded metadata only.",
        "action_taken": ["Recorded bounded workflow result."],
        "evidence_refs": ["docs/ai/security/security-evidence-triage.md"],
        "checker_refs": ["scripts/check_harness_sample_gap_evidence.py"],
    }


class HarnessSampleTemplateTest(unittest.TestCase):
    def test_default_template_audit_uses_current_sample_date(self) -> None:
        with patch.object(harness_sample_templates, "default_sampled_at", return_value="2026-05-25"):
            report = check_harness_sample_templates.build_report(gap_ids={"GAP-SEC-SCHEDULED-RUN"})

        self.assertEqual([], report.errors)
        self.assertEqual("2026-05-25", report.sampled_at)
        self.assertEqual({"placeholder": 1}, report.template_review_state_counts)

    def test_all_collection_templates_validate_against_target_checkers(self) -> None:
        items = plan_harness_sample_collection.build_queue(include_future=True, include_accepted=True)

        report = check_harness_sample_templates.build_report("2026-05-24")

        self.assertEqual([], report.errors)
        self.assertEqual(len(items) - 1, report.template_count)
        self.assertEqual(1, report.skipped_no_sample_collection_count)
        self.assertEqual(("GAP-TRACE-OTLP-PILOT-BURNIN",), report.skipped_no_sample_collection_gap_ids)
        self.assertNotIn("harness-future-work-contract/v1", report.schema_counts)
        self.assertIn("harness-upgrade-decision/v1", report.schema_counts)
        self.assertIn("harness-sample-gap-evidence/v1", report.schema_counts)
        self.assertIn("pre-tool-use-preflight-sample/v1", report.schema_counts)
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
                "requires-workflow-task-event": 2,
                "upgrade-decision-review": 5,
            },
            report.capture_gate_counts,
        )
        self.assertEqual({"not-applicable": 5, "placeholder": 14}, report.template_review_state_counts)
        self.assertEqual(6, report.schema_counts["harness-sample-gap-evidence/v1"])
        self.assertEqual(4, report.schema_counts["agentic-red-team-sample/v1"])
        self.assertEqual(5, report.schema_counts["harness-upgrade-decision/v1"])

    def test_no_sample_collection_items_do_not_emit_templates(self) -> None:
        item = plan_harness_sample_collection.build_queue(
            gap_ids={"GAP-TRACE-OTLP-PILOT-BURNIN"},
            include_accepted=True,
        )[0]
        output = io.StringIO()

        self.assertFalse(harness_sample_templates.should_emit_sample_template(item))
        with redirect_stdout(output):
            harness_sample_templates.emit_sample_templates([item])
        report = check_harness_sample_templates.build_report(
            "2026-05-24",
            readinesses={"local-sample-only"},
        )

        self.assertEqual("", output.getvalue())
        self.assertEqual(0, report.template_count)
        self.assertEqual(1, report.skipped_no_sample_collection_count)
        self.assertEqual(("GAP-TRACE-OTLP-PILOT-BURNIN",), report.skipped_no_sample_collection_gap_ids)
        self.assertEqual({}, report.capture_gate_counts)

    def test_gap_filter_limits_template_audit(self) -> None:
        report = check_harness_sample_templates.build_report(
            "2026-05-24",
            {"GAP-GUARDRAIL-PREFLIGHT-WARNING"},
        )

        self.assertEqual([], report.errors)
        self.assertEqual(1, report.template_count)
        self.assertEqual("GAP-GUARDRAIL-PREFLIGHT-WARNING", report.validations[0].gap_id)
        self.assertEqual("placeholder", report.validations[0].template_review_state)
        self.assertIn(
            "action_taken must include a meaningful value",
            report.validations[0].template_review_blockers,
        )

    def test_area_and_priority_filters_limit_template_audit(self) -> None:
        report = check_harness_sample_templates.build_report(
            "2026-05-24",
            areas={"workflow-skills"},
            priorities={"P2"},
            actionable_only=True,
            pending_state="without-review-ready-pending",
        )
        ids = {validation.gap_id for validation in report.validations}

        self.assertEqual([], report.errors)
        self.assertEqual(2, report.template_count)
        self.assertEqual(
            {
                "GAP-WORKFLOW-CROSS-WS",
                "GAP-WORKFLOW-PR-OVERLAP",
            },
            ids,
        )

    def test_ledger_action_filter_validates_placeholder_fill_templates(self) -> None:
        report = check_harness_sample_templates.build_report(
            "2026-05-24",
            actionable_only=True,
            ledger_actions={"fill-existing-placeholder"},
        )
        ids = {validation.gap_id for validation in report.validations}

        self.assertEqual([], report.errors)
        self.assertEqual(2, report.template_count)
        self.assertEqual({"placeholder": 2}, report.template_review_state_counts)
        self.assertEqual({"GAP-GUARDRAIL-PREFLIGHT-WARNING", "GAP-RUNTIME-LOOP-SCOPE-WARNING"}, ids)
        self.assertEqual(1, report.schema_counts["pre-tool-use-preflight-sample/v1"])
        self.assertEqual(1, report.schema_counts["loop-scope-monitor-sample/v1"])

    def test_capture_gate_filter_validates_matching_templates(self) -> None:
        report = check_harness_sample_templates.build_report(
            "2026-05-24",
            capture_gates={"requires-approved-remote-interop"},
        )

        self.assertEqual([], report.errors)
        self.assertEqual(1, report.template_count)
        self.assertEqual({"requires-approved-remote-interop": 1}, report.capture_gate_counts)
        self.assertEqual("GAP-TRACE-REMOTE-INTEROP", report.validations[0].gap_id)
        self.assertEqual("requires-approved-remote-interop", report.validations[0].capture_gate)
        self.assertIn("ADR-017 remote interop probe", report.validations[0].capture_gate_detail)
        self.assertEqual("placeholder", report.validations[0].template_review_state)

    def test_readiness_filter_validates_matching_templates(self) -> None:
        report = check_harness_sample_templates.build_report(
            "2026-05-24",
            readinesses={"needs-more-real-samples"},
        )

        self.assertEqual([], report.errors)
        self.assertEqual(1, report.template_count)
        self.assertEqual("GAP-TRACE-LOCAL-SUMMARY-BURNIN", report.validations[0].gap_id)
        self.assertEqual("placeholder", report.validations[0].template_review_state)

    def test_actionable_without_pending_templates_validate_without_blocked_or_local_gaps(self) -> None:
        report = check_harness_sample_templates.build_report(
            "2026-05-24",
            actionable_only=True,
            pending_state="without-pending",
        )
        ids = {validation.gap_id for validation in report.validations}

        self.assertEqual([], report.errors)
        self.assertEqual(12, report.template_count)
        self.assertEqual({"placeholder": 12}, report.template_review_state_counts)
        self.assertEqual(6, report.schema_counts["harness-sample-gap-evidence/v1"])
        self.assertEqual(4, report.schema_counts["agentic-red-team-sample/v1"])
        self.assertEqual(1, report.schema_counts["local-trace-summary-sample/v1"])
        self.assertNotIn("GAP-GUARDRAIL-PREFLIGHT-WARNING", ids)
        self.assertNotIn("GAP-RUNTIME-LOOP-SCOPE-WARNING", ids)
        self.assertNotIn("GAP-GUARDRAIL-SOURCE-BOUNDARY", ids)
        self.assertNotIn("GAP-SEC-CONTROL-MATRIX-BURNIN", ids)
        self.assertNotIn("GAP-WORKFLOW-SIMPLE-SKIP", ids)
        self.assertIn("GAP-TRACE-LOCAL-SUMMARY-BURNIN", ids)
        self.assertIn("GAP-TRACE-REMOTE-INTEROP", ids)
        self.assertNotIn("GAP-TRACE-OTLP-PILOT-BURNIN", ids)
        self.assertNotIn("harness-future-work-contract/v1", report.schema_counts)

    def test_actionable_without_review_ready_templates_include_placeholder_pending_gaps(self) -> None:
        report = check_harness_sample_templates.build_report(
            "2026-05-24",
            actionable_only=True,
            pending_state="without-review-ready-pending",
        )
        ids = {validation.gap_id for validation in report.validations}

        self.assertEqual([], report.errors)
        self.assertEqual(14, report.template_count)
        self.assertEqual({"placeholder": 14}, report.template_review_state_counts)
        self.assertEqual(1, report.schema_counts["pre-tool-use-preflight-sample/v1"])
        self.assertEqual(1, report.schema_counts["loop-scope-monitor-sample/v1"])
        self.assertEqual(1, report.schema_counts["local-trace-summary-sample/v1"])
        self.assertEqual(4, report.schema_counts["agentic-red-team-sample/v1"])
        self.assertIn("GAP-GUARDRAIL-PREFLIGHT-WARNING", ids)
        self.assertIn("GAP-RUNTIME-LOOP-SCOPE-WARNING", ids)
        self.assertNotIn("GAP-GUARDRAIL-SOURCE-BOUNDARY", ids)
        self.assertNotIn("GAP-SEC-CONTROL-MATRIX-BURNIN", ids)
        self.assertNotIn("GAP-WORKFLOW-SIMPLE-SKIP", ids)
        self.assertIn("GAP-TRACE-LOCAL-SUMMARY-BURNIN", ids)
        self.assertIn("GAP-TRACE-REMOTE-INTEROP", ids)
        self.assertIn("GAP-AGENTIC-CASCADE-STOP", ids)

    def test_review_existing_pending_template_is_outcome_candidate_from_pending_row(self) -> None:
        item = review_ready_item()

        with patch.object(harness_sample_outcome_templates, "pending_record_for_item", return_value=pending_generic_record()):
            template = harness_sample_templates.sample_template(item, "2026-05-24")

        self.assertEqual("harness-sample-gap-evidence/v1", template["schema_version"])
        self.assertEqual("GAP-SAMPLE-2026-05-24-sec-scheduled-run-real", template["id"])
        self.assertEqual("GAP-SEC-SCHEDULED-RUN", template["gap_id"])
        self.assertEqual("rejected", template["outcome"])
        self.assertEqual("real-workflow-run", template["source_type"])
        self.assertEqual("Scheduled security evidence workflow run captured bounded metadata.", template["sample_summary"])
        self.assertEqual("Bounded metadata only.", template["boundary_note"])

    def test_review_existing_pending_template_uses_outcome_review_gate(self) -> None:
        item = review_ready_item()

        with (
            patch.object(harness_sample_outcome_templates, "pending_record_for_item", return_value=pending_generic_record()),
            patch.object(check_harness_sample_templates, "outcome_candidate_errors", return_value=[]) as outcome_errors,
        ):
            validation = check_harness_sample_templates.validate_item(item, "2026-05-24")

        self.assertEqual([], validation.errors)
        self.assertEqual("harness-sample-gap-evidence/v1", validation.schema_version)
        self.assertEqual("not-applicable", validation.template_review_state)
        self.assertEqual((), validation.template_review_blockers)
        outcome_errors.assert_called_once()


if __name__ == "__main__":
    unittest.main()
