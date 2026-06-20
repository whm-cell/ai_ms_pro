from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_harness_placeholder_replacement  # noqa: E402


def write_candidate(payload: dict[str, object]) -> Path:
    temp = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".jsonl")
    with temp:
        temp.write(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")
    return Path(temp.name)


def preflight_candidate(**overrides: object) -> dict[str, object]:
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
        "outcome": "pending",
        "false_positive": False,
        "action_taken": ["Recorded bounded-output decision and kept the sample pending for separate review."],
        "evidence_refs": ["docs/ai/standards/pre-tool-use-preflight.md"],
        "note": "Replacement candidate only; remains pending until a separate acceptance review.",
    }
    payload.update(overrides)
    return payload


def loop_candidate(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "schema_version": "loop-scope-monitor-sample/v1",
        "id": "LOOP-SAMPLE-2026-05-24-real-long-session-pending",
        "gap_id": "GAP-RUNTIME-LOOP-SCOPE-WARNING",
        "sampled_at": "2026-05-24",
        "source_type": "real-session",
        "task_summary": "Bounded real long-session Stop warning review after repeated validation.",
        "triggered_findings": ["validation-loop"],
        "monitor_recommendations": ["shrink-validation"],
        "outcome": "pending",
        "false_positive": False,
        "action_taken": ["Narrowed the validation command set and kept the sample pending for separate review."],
        "evidence_refs": ["docs/ai/standards/loop-scope-monitor.md"],
        "note": "Replacement candidate only; remains pending until a separate acceptance review.",
    }
    payload.update(overrides)
    return payload


class HarnessPlaceholderReplacementTest(unittest.TestCase):
    def assert_candidate_report(self, payload: dict[str, object]) -> check_harness_placeholder_replacement.PlaceholderReplacementReport:
        path = write_candidate(payload)
        try:
            report = check_harness_placeholder_replacement.build_report(path)
        finally:
            path.unlink(missing_ok=True)
        self.assertEqual([], report.inventory_errors)
        self.assertEqual([], report.checker_errors)
        self.assertEqual([], report.errors)
        self.assertTrue(report.replacement_allowed)
        self.assertEqual("review-ready", report.replacement_review_state)
        return report

    def test_loop_replacement_candidate_exposes_review_context(self) -> None:
        report = self.assert_candidate_report(loop_candidate())

        self.assertEqual("LOOP-SAMPLE-2026-05-24-real-long-session-pending", report.sample_id)
        self.assertEqual("GAP-RUNTIME-LOOP-SCOPE-WARNING", report.gap_id)
        self.assertEqual("docs/ai/standards/loop-scope-monitor-samples.jsonl", report.target_ledger)
        self.assertEqual("fill-existing-placeholder", report.ledger_action)
        self.assertEqual("needs-first-real-sample", report.readiness)
        self.assertEqual("accepted real loop/scope warning samples", report.source_metric)
        self.assertEqual("0/2", report.current_to_target)
        self.assertEqual("replace-placeholder-after-real-event", report.capture_gate)
        self.assertIn("matching real event", report.capture_gate_detail)
        self.assertIn("monitor recommendation", report.evidence_needed)
        self.assertIn("real Stop loop/scope warning", report.trigger)
        self.assertIn("Bounded evidence only", report.boundary)
        self.assertEqual(
            ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
            "--gap-id GAP-RUNTIME-LOOP-SCOPE-WARNING --ledger-action fill-existing-placeholder --capture-card",
            report.planner_command,
        )
        self.assertEqual(
            ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
            "--gap-id GAP-RUNTIME-LOOP-SCOPE-WARNING --ledger-action fill-existing-placeholder --summary",
            report.intake_command,
        )
        self.assertEqual(2, report.target_line)
        self.assertEqual("placeholder", report.target_review_state)
        self.assertIn("check_harness_sample_outcome.py", report.next_outcome_review_command)

    def test_loop_scope_replacement_candidate_targets_existing_placeholder(self) -> None:
        report = self.assert_candidate_report(loop_candidate())

        self.assertEqual("LOOP-SAMPLE-2026-05-24-real-long-session-pending", report.sample_id)
        self.assertEqual("GAP-RUNTIME-LOOP-SCOPE-WARNING", report.gap_id)
        self.assertEqual("docs/ai/standards/loop-scope-monitor-samples.jsonl", report.target_ledger)
        self.assertEqual("fill-existing-placeholder", report.ledger_action)
        self.assertEqual("needs-first-real-sample", report.readiness)
        self.assertEqual("accepted real loop/scope warning samples", report.source_metric)
        self.assertEqual("0/2", report.current_to_target)
        self.assertEqual("replace-placeholder-after-real-event", report.capture_gate)
        self.assertIn("monitor recommendation", report.evidence_needed)
        self.assertIn("real Stop loop/scope warning", report.trigger)
        self.assertEqual(2, report.target_line)
        self.assertEqual("placeholder", report.target_review_state)

    def test_rejects_new_sample_id_that_would_append_duplicate_gap_work(self) -> None:
        path = write_candidate(
            loop_candidate(id="LOOP-SAMPLE-2026-05-24-new-real-long-session")
        )
        try:
            report = check_harness_placeholder_replacement.build_report(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertFalse(report.replacement_allowed)
        self.assertIn(
            "candidate id does not match an existing pending sample placeholder",
            "\n".join(report.errors),
        )

    def test_rejects_candidate_that_skips_separate_acceptance_review(self) -> None:
        path = write_candidate(loop_candidate(outcome="accepted"))
        try:
            report = check_harness_placeholder_replacement.build_report(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertFalse(report.replacement_allowed)
        self.assertEqual("not-applicable", report.next_outcome_review_command)
        self.assertIn("outcome must remain pending", "\n".join(report.errors))

    def test_rejects_candidate_that_is_still_placeholder(self) -> None:
        path = write_candidate(loop_candidate(action_taken=["none"]))
        try:
            report = check_harness_placeholder_replacement.build_report(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertFalse(report.replacement_allowed)
        self.assertEqual("placeholder", report.replacement_review_state)
        self.assertIn("action_taken must include a meaningful value", report.replacement_review_blockers)
        self.assertIn("must be review-ready", "\n".join(report.errors))

    def test_cli_json_reports_replacement_allowed(self) -> None:
        path = write_candidate(loop_candidate())
        try:
            result = subprocess.run(
                [sys.executable, "scripts/check_harness_placeholder_replacement.py", str(path), "--json"],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
        finally:
            path.unlink(missing_ok=True)

        data = json.loads(result.stdout)
        self.assertTrue(data["replacement_allowed"])
        self.assertEqual("review-ready", data["replacement_review_state"])
        self.assertEqual("docs/ai/standards/loop-scope-monitor-samples.jsonl", data["target_ledger"])
        self.assertEqual("needs-first-real-sample", data["readiness"])
        self.assertEqual("accepted real loop/scope warning samples", data["source_metric"])
        self.assertEqual("0/2", data["current_to_target"])
        self.assertEqual("replace-placeholder-after-real-event", data["capture_gate"])
        self.assertIn("monitor recommendation", data["evidence_needed"])
        self.assertIn("real", data["trigger"].lower())
        self.assertIn("plan_harness_sample_collection.py --gap-id GAP-RUNTIME-LOOP-SCOPE-WARNING", data["planner_command"])
        self.assertIn("--ledger-action fill-existing-placeholder", data["planner_command"])
        self.assertIn("build_harness_sample_intake_bundle.py --gap-id GAP-RUNTIME-LOOP-SCOPE-WARNING", data["intake_command"])
        self.assertIn("--ledger-action fill-existing-placeholder", data["intake_command"])
        self.assertIn("check_harness_sample_outcome.py", data["next_outcome_review_command"])


if __name__ == "__main__":
    unittest.main()
