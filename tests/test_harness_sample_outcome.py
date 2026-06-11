from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_harness_sample_outcome  # noqa: E402
import harness_sample_slots  # noqa: E402


def write_candidate(payload: dict[str, object]) -> Path:
    temp = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".jsonl")
    with temp:
        temp.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
    return Path(temp.name)


def generic_outcome_candidate(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": "harness-sample-gap-evidence/v1",
        "id": "GAP-SAMPLE-2026-05-24-sec-scheduled-run-real",
        "gap_id": "GAP-SEC-SCHEDULED-RUN",
        "sampled_at": "2026-05-24",
        "source_type": "real-workflow-run",
        "outcome": "accepted",
        "local_only": False,
        "no_external_claim": True,
        "false_positive": False,
        "network_exported": False,
        "endpoint_scope": "none",
        "remote_status": "none",
        "sample_summary": "Scheduled security evidence workflow run captured bounded pass/warn/fail metadata.",
        "decision": "Accept as a bounded real sample for the scheduled security evidence gap.",
        "boundary_note": "Bounded check metadata only; no raw logs, prompts, secrets, or external payload bodies.",
        "action_taken": ["Recorded workflow result and owner review decision."],
        "evidence_refs": ["docs/ai/security/security-evidence-triage.md"],
        "checker_refs": ["scripts/check_harness_sample_gap_evidence.py"],
    }
    payload.update(overrides)
    return payload


def pending_generic_record(**overrides: object) -> dict[str, object]:
    payload = generic_outcome_candidate(outcome="pending")
    payload.update(overrides)
    return payload


def preflight_outcome_candidate(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": "pre-tool-use-preflight-sample/v1",
        "id": "PRE-SAMPLE-2026-05-24-real-tool-call-pending",
        "gap_id": "GAP-GUARDRAIL-PREFLIGHT-WARNING",
        "sampled_at": "2026-05-24",
        "source_type": "real-tool-call",
        "task_summary": "Bounded real preflight warning review before a large-output command.",
        "risk_summary": "The preflight warning gave the operator a chance to bound output before execution.",
        "hook_result": "warned",
        "triggered_findings": ["unbounded-large-output"],
        "operator_decisions": ["bounded-output"],
        "outcome": "accepted",
        "false_positive": False,
        "action_taken": ["Recorded bounded-output decision after review."],
        "evidence_refs": ["docs/ai/standards/pre-tool-use-preflight.md"],
        "note": "Outcome candidate only; no raw command or output stored.",
    }
    payload.update(overrides)
    return payload


def review_ready_slot() -> harness_sample_slots.SampleSlot:
    return harness_sample_slots.SampleSlot(
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


def outcome_queue_item(**overrides: object) -> SimpleNamespace:
    payload: dict[str, object] = {
        "gap_id": "GAP-SEC-SCHEDULED-RUN",
        "ledger_action": "review-existing-pending-slot",
        "readiness": "needs-first-real-sample",
        "source_metric": "accepted real generic gap samples",
        "accepted_count": 0,
        "upgrade_discussion_target": 2,
        "capture_gate": "requires-security-workflow-event",
        "capture_gate_detail": "Only a real PR, release, dependency, scheduled security, CodeQL, SBOM, or dependency-review event qualifies.",
        "evidence_needed": ["PR or release URL", "check run result", "owner decision"],
        "trigger": "Capture the next scheduled security evidence workflow run.",
        "boundary": "Bounded evidence only; no raw runtime paths, prompts, full command output, or external payload bodies.",
    }
    payload.update(overrides)
    return SimpleNamespace(**payload)


class HarnessSampleOutcomeTest(unittest.TestCase):
    def assert_candidate_report(self, payload: dict[str, object]) -> check_harness_sample_outcome.SampleOutcomeReport:
        path = write_candidate(payload)
        try:
            with (
                patch.object(check_harness_sample_outcome.harness_sample_slots, "load_all_slots", return_value=[review_ready_slot()]),
                patch.object(check_harness_sample_outcome, "load_target_record", return_value=pending_generic_record()),
                patch.object(
                    check_harness_sample_outcome.harness_sample_outcome_context.plan_harness_sample_collection,
                    "build_queue",
                    return_value=[outcome_queue_item()],
                ),
            ):
                report = check_harness_sample_outcome.build_report(path)
        finally:
            path.unlink(missing_ok=True)
        self.assertEqual([], report.inventory_errors)
        self.assertEqual([], report.checker_errors)
        self.assertEqual([], report.errors)
        self.assertTrue(report.outcome_change_allowed)
        self.assertEqual("review-ready", report.target_review_state)
        self.assertEqual("review-existing-pending-slot", report.ledger_action)
        return report

    def test_accepted_real_candidate_targets_existing_review_ready_pending_row(self) -> None:
        report = self.assert_candidate_report(generic_outcome_candidate())

        self.assertEqual("GAP-SAMPLE-2026-05-24-sec-scheduled-run-real", report.sample_id)
        self.assertEqual("GAP-SEC-SCHEDULED-RUN", report.gap_id)
        self.assertEqual("accepted", report.outcome)
        self.assertEqual("real", report.evidence_class)
        self.assertTrue(report.burn_in_counted)
        self.assertEqual("docs/ai/standards/harness-sample-gap-evidence.jsonl", report.target_ledger)
        self.assertIn("check_harness_sample_gap_evidence.py", report.review_command)
        self.assertEqual("needs-first-real-sample", report.readiness)
        self.assertEqual("accepted real generic gap samples", report.source_metric)
        self.assertEqual("0/2", report.current_to_target)
        self.assertEqual("requires-security-workflow-event", report.capture_gate)
        self.assertIn("real PR", report.capture_gate_detail)
        self.assertIn("owner decision", report.evidence_needed)
        self.assertIn("scheduled security evidence", report.trigger)
        self.assertIn("Bounded evidence only", report.boundary)
        self.assertEqual(
            ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
            "--gap-id GAP-SEC-SCHEDULED-RUN --ledger-action review-existing-pending-slot --capture-card",
            report.planner_command,
        )
        self.assertEqual(
            ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
            "--gap-id GAP-SEC-SCHEDULED-RUN --ledger-action review-existing-pending-slot "
            "--pending-state with-review-ready-pending --summary",
            report.intake_command,
        )

    def test_rejected_candidate_is_allowed_but_not_burn_in_counted(self) -> None:
        report = self.assert_candidate_report(
            generic_outcome_candidate(
                outcome="rejected",
                decision="Reject this candidate after bounded owner review.",
                action_taken=["Recorded rejection reason."],
            )
        )

        self.assertEqual("rejected", report.outcome)
        self.assertFalse(report.burn_in_counted)

    def test_rejects_direct_outcome_change_from_placeholder_row(self) -> None:
        path = write_candidate(preflight_outcome_candidate())
        try:
            report = check_harness_sample_outcome.build_report(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertFalse(report.outcome_change_allowed)
        self.assertFalse(report.burn_in_counted)
        self.assertEqual("placeholder", report.target_review_state)
        self.assertIn("target pending slot must be review-ready", "\n".join(report.errors))

    def test_rejects_candidate_that_stays_pending(self) -> None:
        path = write_candidate(generic_outcome_candidate(outcome="pending"))
        try:
            with (
                patch.object(check_harness_sample_outcome.harness_sample_slots, "load_all_slots", return_value=[review_ready_slot()]),
                patch.object(check_harness_sample_outcome, "load_target_record", return_value=pending_generic_record()),
                patch.object(
                    check_harness_sample_outcome.harness_sample_outcome_context.plan_harness_sample_collection,
                    "build_queue",
                    return_value=[outcome_queue_item()],
                ),
            ):
                report = check_harness_sample_outcome.build_report(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertFalse(report.outcome_change_allowed)
        self.assertIn("must change outcome to accepted or rejected", "\n".join(report.errors))

    def test_rejects_candidate_that_fails_target_checker(self) -> None:
        path = write_candidate(generic_outcome_candidate(action_taken=["none"]))
        try:
            with (
                patch.object(check_harness_sample_outcome.harness_sample_slots, "load_all_slots", return_value=[review_ready_slot()]),
                patch.object(check_harness_sample_outcome, "load_target_record", return_value=pending_generic_record()),
                patch.object(
                    check_harness_sample_outcome.harness_sample_outcome_context.plan_harness_sample_collection,
                    "build_queue",
                    return_value=[outcome_queue_item()],
                ),
            ):
                report = check_harness_sample_outcome.build_report(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertFalse(report.outcome_change_allowed)
        self.assertFalse(report.burn_in_counted)
        self.assertIn("accepted samples need action_taken", "\n".join(report.checker_errors))

    def test_rejects_rejected_outcome_candidate_with_boundary_drift(self) -> None:
        path = write_candidate(
            generic_outcome_candidate(
                outcome="rejected",
                no_external_claim=False,
                local_only=True,
                decision="Reject this candidate after bounded owner review.",
                action_taken=["Recorded rejection reason."],
            )
        )
        try:
            with (
                patch.object(check_harness_sample_outcome.harness_sample_slots, "load_all_slots", return_value=[review_ready_slot()]),
                patch.object(check_harness_sample_outcome, "load_target_record", return_value=pending_generic_record()),
                patch.object(
                    check_harness_sample_outcome.harness_sample_outcome_context.plan_harness_sample_collection,
                    "build_queue",
                    return_value=[outcome_queue_item()],
                ),
            ):
                report = check_harness_sample_outcome.build_report(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertFalse(report.outcome_change_allowed)
        errors = "\n".join(report.errors)
        self.assertIn("outcome candidate boundary invalid: no_external_claim must stay true", errors)
        self.assertIn("outcome candidate boundary invalid: real pending gap evidence must set local_only=false", errors)

    def test_rejects_outcome_candidate_that_changes_stable_evidence_field(self) -> None:
        path = write_candidate(
            generic_outcome_candidate(
                sample_summary="Changed summary after the pending row was already captured.",
            )
        )
        try:
            with (
                patch.object(check_harness_sample_outcome.harness_sample_slots, "load_all_slots", return_value=[review_ready_slot()]),
                patch.object(check_harness_sample_outcome, "load_target_record", return_value=pending_generic_record()),
                patch.object(
                    check_harness_sample_outcome.harness_sample_outcome_context.plan_harness_sample_collection,
                    "build_queue",
                    return_value=[outcome_queue_item()],
                ),
            ):
                report = check_harness_sample_outcome.build_report(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertFalse(report.outcome_change_allowed)
        self.assertIn(
            "outcome candidate changed stable evidence field sample_summary",
            "\n".join(report.errors),
        )

    def test_cli_json_reports_outcome_change_allowed(self) -> None:
        path = write_candidate(generic_outcome_candidate())
        try:
            with (
                patch.object(check_harness_sample_outcome.harness_sample_slots, "load_all_slots", return_value=[review_ready_slot()]),
                patch.object(check_harness_sample_outcome, "load_target_record", return_value=pending_generic_record()),
                patch.object(
                    check_harness_sample_outcome.harness_sample_outcome_context.plan_harness_sample_collection,
                    "build_queue",
                    return_value=[outcome_queue_item()],
                ),
            ):
                report = check_harness_sample_outcome.build_report(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertTrue(report.outcome_change_allowed)
        self.assertEqual("accepted", report.outcome)
        self.assertEqual("review-existing-pending-slot", report.ledger_action)
        data = check_harness_sample_outcome.asdict(report)
        self.assertIn("--ledger-action review-existing-pending-slot", data["planner_command"])
        self.assertIn("--pending-state with-review-ready-pending", data["intake_command"])

    def test_rejects_review_ready_candidate_outside_current_outcome_lane(self) -> None:
        path = write_candidate(generic_outcome_candidate())
        try:
            with (
                patch.object(check_harness_sample_outcome.harness_sample_slots, "load_all_slots", return_value=[review_ready_slot()]),
                patch.object(check_harness_sample_outcome, "load_target_record", return_value=pending_generic_record()),
                patch.object(
                    check_harness_sample_outcome.harness_sample_outcome_context.plan_harness_sample_collection,
                    "build_queue",
                    return_value=[],
                ),
            ):
                report = check_harness_sample_outcome.build_report(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertFalse(report.outcome_change_allowed)
        self.assertIn("no current collection queue item found", "\n".join(report.errors))

    def test_cli_fails_without_existing_pending_row(self) -> None:
        path = write_candidate(generic_outcome_candidate())
        try:
            result = subprocess.run(
                [sys.executable, "scripts/check_harness_sample_outcome.py", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
        finally:
            path.unlink(missing_ok=True)

        self.assertNotEqual(0, result.returncode)
        data = json.loads(result.stdout)
        self.assertFalse(data["outcome_change_allowed"])
        self.assertIn("does not match an existing pending sample row", "\n".join(data["errors"]))


if __name__ == "__main__":
    unittest.main()
