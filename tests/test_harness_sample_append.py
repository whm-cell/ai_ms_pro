from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_harness_sample_append  # noqa: E402


def write_candidate(payload: dict[str, object]) -> Path:
    temp = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".jsonl")
    with temp:
        temp.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
    return Path(temp.name)


def generic_candidate(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
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
        "sample_summary": "Scheduled security evidence workflow run captured bounded pass/warn/fail metadata.",
        "decision": "Keep as a pending real sample until a separate owner review changes the outcome.",
        "boundary_note": "Bounded check metadata only; no raw logs, prompts, secrets, or external payload bodies.",
        "action_taken": ["Recorded workflow result and kept the sample pending for review."],
        "evidence_refs": ["docs/ai/security/security-evidence-triage.md"],
        "checker_refs": ["scripts/check_harness_sample_gap_evidence.py"],
    }
    payload.update(overrides)
    return payload


def red_team_candidate(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": "agentic-red-team-sample/v1",
        "id": "REDTEAM-SAMPLE-2026-05-24-memory-poisoning-real",
        "sampled_at": "2026-05-24",
        "control_ids": ["AC-04"],
        "risk_family": "memory-poisoning",
        "source_type": "real-incident",
        "outcome": "pending",
        "local_only": True,
        "no_external_claim": True,
        "false_positive": False,
        "adversarial_summary": "Recovered context contained instruction-like material and required bounded handling.",
        "decision": "Keep recovered context as evidence only and do not promote instruction-like text.",
        "action_taken": ["Recorded bounded incident summary and kept the sample pending for review."],
        "replay_commands": ["none"],
        "evidence_refs": ["docs/ai/security/agentic-red-team-samples.md"],
        "checker_refs": ["scripts/check_agentic_red_team_samples.py"],
        "upgrade_signal": "none",
        "false_positive_rule": "False positive only if reviewer confirms the text was inert quoted evidence.",
        "note": "Pending real incident candidate; no prompt, transcript, or raw runtime material included.",
    }
    payload.update(overrides)
    return payload


def local_trace_candidate(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": "local-trace-summary-sample/v1",
        "id": "TRACE-SUMMARY-SAMPLE-2026-05-24-docs-review-real",
        "gap_id": "GAP-TRACE-LOCAL-SUMMARY-BURNIN",
        "sampled_at": "2026-05-24",
        "source_type": "real-local-report",
        "outcome": "pending",
        "summary_format": "json",
        "no_network": True,
        "local_only": True,
        "false_positive": False,
        "task_class": "docs-review",
        "task_summary": "Local trace summary generated for a docs review task class.",
        "observation_count": 1,
        "trace_record_count": 0,
        "trace_count": 0,
        "promotion_needed_count": 0,
        "warning_count": 0,
        "redaction_states": ["redacted"],
        "key_findings": ["Recorded bounded no-network summary evidence for a non-harness task class."],
        "action_taken": ["Kept the sample pending for separate review."],
        "evidence_refs": ["docs/ai/standards/local-trace-summary.md"],
        "note": "Pending local trace summary candidate with bounded counts only.",
    }
    payload.update(overrides)
    return payload


def checkpoint_resume_candidate(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": "stage-checkpoint-resume-sample/v1",
        "id": "CP-SAMPLE-2026-05-25-cross-task-real",
        "gap_id": "GAP-RUNTIME-STAGE-CHECKPOINT-RESUME",
        "checkpoint_id": "CP-2026-05-24-agentic-harness-g2-checkpoint",
        "resumed_at": "2026-05-25",
        "task_summary": "Used a stage checkpoint to resume a bounded non-harness task.",
        "resume_scope": "cross-task",
        "used_checkpoint": True,
        "outcome": "pending",
        "avoided_rework": ["Skipped repeated repository orientation by following the checkpoint next_action."],
        "missed_validation_prevented": ["Kept the checkpoint checker in the verification list."],
        "missing_fields": ["none"],
        "false_positive_notes": ["none"],
        "evidence_refs": ["docs/ai/checkpoints/stage-checkpoints.jsonl"],
        "note": "Pending cross-task resume candidate; no raw runtime material included.",
    }
    payload.update(overrides)
    return payload


class HarnessSampleAppendTest(unittest.TestCase):
    def assert_candidate_report(self, payload: dict[str, object]) -> check_harness_sample_append.SampleAppendReport:
        path = write_candidate(payload)
        try:
            report = check_harness_sample_append.build_report(path)
        finally:
            path.unlink(missing_ok=True)
        self.assertEqual([], report.inventory_errors)
        self.assertEqual([], report.checker_errors)
        self.assertEqual([], report.errors)
        self.assertTrue(report.append_allowed)
        self.assertEqual("review-ready", report.append_review_state)
        return report

    def test_generic_gap_candidate_targets_append_lane(self) -> None:
        report = self.assert_candidate_report(generic_candidate())

        self.assertEqual("GAP-SAMPLE-2026-05-24-sec-scheduled-run-real", report.sample_id)
        self.assertEqual("GAP-SEC-SCHEDULED-RUN", report.gap_id)
        self.assertEqual("append-new-pending-slot", report.ledger_action)
        self.assertEqual("needs-first-real-sample", report.readiness)
        self.assertEqual("accepted real generic gap samples", report.source_metric)
        self.assertEqual("0/2", report.current_to_target)
        self.assertEqual("docs/ai/standards/harness-sample-gap-evidence.jsonl", report.target_ledger)
        self.assertEqual("requires-security-workflow-event", report.capture_gate)
        self.assertIn("real PR, release, dependency", report.capture_gate_detail)
        self.assertIn("workflow run URL", report.evidence_needed)
        self.assertIn("scheduled or manually dispatched", report.trigger)
        self.assertIn("Bounded evidence only", report.boundary)
        self.assertEqual(
            ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
            "--gap-id GAP-SEC-SCHEDULED-RUN --ledger-action append-new-pending-slot --capture-card",
            report.planner_command,
        )
        self.assertEqual(
            ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
            "--gap-id GAP-SEC-SCHEDULED-RUN --ledger-action append-new-pending-slot --summary",
            report.intake_command,
        )
        self.assertIn("check_harness_sample_gap_evidence.py", report.review_command)
        self.assertIn("check_harness_sample_outcome.py", report.next_outcome_review_command)

    def test_red_team_candidate_can_derive_gap_from_risk_family(self) -> None:
        report = self.assert_candidate_report(red_team_candidate())

        self.assertEqual("GAP-AGENTIC-MEMORY-POISONING", report.gap_id)
        self.assertEqual("docs/ai/security/agentic-red-team-samples.jsonl", report.target_ledger)
        self.assertEqual("real-incident", report.source_type)
        self.assertEqual("requires-bounded-real-incident", report.capture_gate)
        self.assertIn("bounded real incident summary", report.capture_gate_detail)
        self.assertIn("poisoning pattern", report.evidence_needed)
        self.assertIn("Bounded incident summary only", report.boundary)
        self.assertIn("check_agentic_red_team_samples.py", report.review_command)

    def test_rejects_duplicate_sample_id(self) -> None:
        path = write_candidate(generic_candidate(id="GAP-SAMPLE-2026-05-24-otlp-local-pilot"))
        try:
            report = check_harness_sample_append.build_report(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertFalse(report.append_allowed)
        self.assertEqual("not-applicable", report.next_outcome_review_command)
        self.assertIn("candidate id already exists in sample ledgers", "\n".join(report.errors))

    def test_rejects_gap_that_should_fill_placeholder_instead(self) -> None:
        payload = {
            "schema_version": "pre-tool-use-preflight-sample/v1",
            "id": "PRE-SAMPLE-2026-05-24-new-preflight-sample",
            "gap_id": "GAP-GUARDRAIL-PREFLIGHT-WARNING",
            "sampled_at": "2026-05-24",
            "source_type": "real-tool-call",
            "task_summary": "Bounded real preflight warning review.",
            "risk_summary": "The warning changed the bounded-output decision.",
            "hook_result": "warned",
            "triggered_findings": ["unbounded-large-output"],
            "operator_decisions": ["bounded-output"],
            "outcome": "pending",
            "false_positive": False,
            "action_taken": ["Kept output bounded and left the sample pending for review."],
            "evidence_refs": ["docs/ai/standards/pre-tool-use-preflight.md"],
            "note": "Append candidate should be rejected because a placeholder already exists.",
        }
        path = write_candidate(payload)
        try:
            report = check_harness_sample_append.build_report(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertFalse(report.append_allowed)
        self.assertIn("ledger_action=review-upgrade-decision", "\n".join(report.errors))

    def test_rejects_candidate_that_is_still_placeholder(self) -> None:
        path = write_candidate(generic_candidate(sample_summary="TBD: bounded sample summary.", action_taken=["none"]))
        try:
            report = check_harness_sample_append.build_report(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertFalse(report.append_allowed)
        self.assertEqual("placeholder", report.append_review_state)
        self.assertIn("sample_summary must be meaningful text", report.append_review_blockers)
        self.assertIn("action_taken must include a meaningful value", report.append_review_blockers)
        self.assertIn("must be review-ready", "\n".join(report.errors))

    def test_rejects_generic_candidate_with_external_claim_boundary_drift(self) -> None:
        path = write_candidate(generic_candidate(no_external_claim=False))
        try:
            report = check_harness_sample_append.build_report(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertFalse(report.append_allowed)
        self.assertEqual("placeholder", report.append_review_state)
        self.assertIn("no_external_claim must stay true", "\n".join(report.append_review_blockers))
        self.assertIn("must be review-ready", "\n".join(report.errors))

    def test_rejects_red_team_candidate_with_boundary_drift(self) -> None:
        path = write_candidate(red_team_candidate(no_external_claim=False, local_only=False))
        try:
            report = check_harness_sample_append.build_report(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertFalse(report.append_allowed)
        self.assertEqual("placeholder", report.append_review_state)
        blockers = "\n".join(report.append_review_blockers)
        self.assertIn("red-team pending samples must set local_only=true", blockers)
        self.assertIn("red-team pending samples must set no_external_claim=true", blockers)

    def test_rejects_local_trace_candidate_with_network_boundary_drift(self) -> None:
        path = write_candidate(local_trace_candidate(no_network=False, local_only=False))
        try:
            report = check_harness_sample_append.build_report(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertFalse(report.append_allowed)
        self.assertEqual("placeholder", report.append_review_state)
        blockers = "\n".join(report.append_review_blockers)
        self.assertIn("local trace summary pending samples must set no_network=true", blockers)
        self.assertIn("local trace summary pending samples must set local_only=true", blockers)

    def test_checkpoint_resume_candidate_targets_append_lane(self) -> None:
        report = self.assert_candidate_report(checkpoint_resume_candidate())

        self.assertEqual("CP-SAMPLE-2026-05-25-cross-task-real", report.sample_id)
        self.assertEqual("GAP-RUNTIME-STAGE-CHECKPOINT-RESUME", report.gap_id)
        self.assertEqual("append-new-pending-slot", report.ledger_action)
        self.assertEqual("needs-first-real-sample", report.readiness)
        self.assertEqual("accepted cross-task resume samples", report.source_metric)
        self.assertEqual("0/2", report.current_to_target)
        self.assertEqual("docs/ai/checkpoints/resume-samples.jsonl", report.target_ledger)
        self.assertIn("check_stage_checkpoints.py", report.review_command)

    def test_rejects_checkpoint_resume_candidate_that_keeps_template_checkpoint(self) -> None:
        path = write_candidate(
            checkpoint_resume_candidate(checkpoint_id="CP-2026-05-24-agentic-harness-burnin")
        )
        try:
            report = check_harness_sample_append.build_report(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertFalse(report.append_allowed)
        self.assertEqual("placeholder", report.append_review_state)
        self.assertIn("replace the template checkpoint_id", "\n".join(report.append_review_blockers))

    def test_rejects_checkpoint_resume_candidate_that_is_not_cross_task(self) -> None:
        path = write_candidate(checkpoint_resume_candidate(resume_scope="same-task"))
        try:
            report = check_harness_sample_append.build_report(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertFalse(report.append_allowed)
        self.assertEqual("placeholder", report.append_review_state)
        self.assertIn("resume_scope=cross-task", "\n".join(report.append_review_blockers))

    def test_cli_json_reports_append_allowed(self) -> None:
        path = write_candidate(generic_candidate())
        try:
            result = subprocess.run(
                [sys.executable, "scripts/check_harness_sample_append.py", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
        finally:
            path.unlink(missing_ok=True)

        data = json.loads(result.stdout)
        self.assertTrue(data["append_allowed"])
        self.assertEqual("review-ready", data["append_review_state"])
        self.assertEqual("docs/ai/standards/harness-sample-gap-evidence.jsonl", data["target_ledger"])
        self.assertEqual("needs-first-real-sample", data["readiness"])
        self.assertEqual("accepted real generic gap samples", data["source_metric"])
        self.assertEqual("0/2", data["current_to_target"])
        self.assertEqual("requires-security-workflow-event", data["capture_gate"])
        self.assertIn("workflow run URL", data["evidence_needed"])
        self.assertIn("bounded", data["boundary"].lower())
        self.assertIn("plan_harness_sample_collection.py --gap-id GAP-SEC-SCHEDULED-RUN", data["planner_command"])
        self.assertIn("--ledger-action append-new-pending-slot", data["planner_command"])
        self.assertIn("build_harness_sample_intake_bundle.py --gap-id GAP-SEC-SCHEDULED-RUN", data["intake_command"])
        self.assertIn("--ledger-action append-new-pending-slot", data["intake_command"])
        self.assertIn("check_harness_sample_outcome.py", data["next_outcome_review_command"])


if __name__ == "__main__":
    unittest.main()
