from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_harness_upgrade_decision_candidate as candidate_review  # noqa: E402
import harness_sample_templates  # noqa: E402
import plan_harness_sample_collection  # noqa: E402


def write_candidate(record: dict[str, object]) -> Path:
    temp = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".jsonl")
    with temp:
        temp.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
    return Path(temp.name)


class HarnessUpgradeDecisionCandidateTest(unittest.TestCase):
    def test_generated_upgrade_decision_template_replaces_existing_row(self) -> None:
        item = plan_harness_sample_collection.build_queue(
            gap_ids={"GAP-WORKFLOW-TASK-PROFILE-AUDIT"},
        )[0]
        template = harness_sample_templates.sample_template(item, "2026-05-24")
        path = write_candidate(template)
        try:
            report = candidate_review.build_report(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertEqual([], report.errors)
        self.assertEqual([], report.checker_errors)
        self.assertEqual([], report.inventory_errors)
        self.assertTrue(report.review_allowed)
        self.assertEqual("HUD-2026-05-24-task-profile-audit-keep-advisory", report.decision_id)
        self.assertEqual(report.decision_id, report.current_decision_id)
        self.assertEqual(1, report.current_decision_line)
        self.assertEqual("keep-advisory", report.current_decision)
        self.assertEqual("defer-until-more-evidence", report.decision)
        self.assertEqual(3, report.accepted_count)
        self.assertEqual(3, report.upgrade_discussion_target)
        self.assertEqual("review-upgrade-decision", report.ledger_action)
        self.assertEqual("ready-for-upgrade-discussion", report.readiness)
        self.assertEqual("accepted real task-profile classes", report.source_metric)
        self.assertEqual("3/3", report.current_to_target)
        self.assertEqual("upgrade-decision-review", report.capture_gate)
        self.assertIn("Review a bounded", report.capture_gate_detail)
        self.assertIn("more real tasks outside", "\n".join(report.current_evidence_needed))
        self.assertIn("Upgrade decision", report.boundary)
        self.assertEqual(
            ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
            "--gap-id GAP-WORKFLOW-TASK-PROFILE-AUDIT --ledger-action review-upgrade-decision --capture-card",
            report.planner_command,
        )
        self.assertEqual(
            ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
            "--gap-id GAP-WORKFLOW-TASK-PROFILE-AUDIT --ledger-action review-upgrade-decision --summary",
            report.intake_command,
        )
        self.assertIn("more real tasks outside", "\n".join(report.next_evidence_needed))
        self.assertIn("check_harness_upgrade_decision_candidate.py", report.candidate_review_command)
        self.assertIn("check_harness_upgrade_decisions.py", report.next_decision_audit_command)

    def test_rejects_draft_id_that_would_duplicate_existing_gap(self) -> None:
        item = plan_harness_sample_collection.build_queue(
            gap_ids={"GAP-WORKFLOW-TASK-PROFILE-AUDIT"},
        )[0]
        template = harness_sample_templates.sample_template(item, "2026-05-24")
        template["id"] = "HUD-DRAFT-2026-05-24-workflow-task-profile-audit"
        path = write_candidate(template)
        try:
            report = candidate_review.build_report(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertFalse(report.review_allowed)
        self.assertTrue(any("replace the row instead of appending a duplicate" in error for error in report.errors))

    def test_rejects_stale_readiness_snapshot(self) -> None:
        item = plan_harness_sample_collection.build_queue(
            gap_ids={"GAP-WORKFLOW-TASK-PROFILE-AUDIT"},
        )[0]
        template = harness_sample_templates.sample_template(item, "2026-05-24")
        template["accepted_count"] = 2
        path = write_candidate(template)
        try:
            report = candidate_review.build_report(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertFalse(report.review_allowed)
        self.assertTrue(any("accepted_count is stale" in error for error in report.checker_errors))

    def test_rejects_candidate_outside_current_upgrade_decision_lane(self) -> None:
        item = plan_harness_sample_collection.build_queue(
            gap_ids={"GAP-WORKFLOW-TASK-PROFILE-AUDIT"},
        )[0]
        template = harness_sample_templates.sample_template(item, "2026-05-24")
        path = write_candidate(template)
        try:
            with patch(
                "check_harness_upgrade_decision_candidate."
                "harness_upgrade_decision_context.plan_harness_sample_collection.build_queue",
                return_value=[],
            ):
                report = candidate_review.build_report(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertFalse(report.review_allowed)
        self.assertTrue(
            any("no current collection queue item found for review-upgrade-decision lane" in error for error in report.errors)
        )

    def test_cli_json_output_reports_candidate_state(self) -> None:
        item = plan_harness_sample_collection.build_queue(
            gap_ids={"GAP-WORKFLOW-TASK-PROFILE-AUDIT"},
        )[0]
        template = harness_sample_templates.sample_template(item, "2026-05-24")
        path = write_candidate(template)
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/check_harness_upgrade_decision_candidate.py",
                    str(path),
                    "--json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
            )
        finally:
            path.unlink(missing_ok=True)
        data = json.loads(result.stdout)

        self.assertTrue(data["review_allowed"])
        self.assertEqual("GAP-WORKFLOW-TASK-PROFILE-AUDIT", data["gap_id"])
        self.assertEqual("defer-until-more-evidence", data["decision"])
        self.assertEqual("keep-advisory", data["current_decision"])
        self.assertEqual("review-upgrade-decision", data["ledger_action"])
        self.assertEqual("ready-for-upgrade-discussion", data["readiness"])
        self.assertEqual("3/3", data["current_to_target"])
        self.assertEqual("upgrade-decision-review", data["capture_gate"])
        self.assertIn("current_evidence_needed", data)
        self.assertIn("--ledger-action review-upgrade-decision", data["planner_command"])
        self.assertIn("--ledger-action review-upgrade-decision", data["intake_command"])
        self.assertIn("next_evidence_needed", data)
        self.assertIn("profile", "\n".join(data["next_evidence_needed"]))
        self.assertIn("check_harness_upgrade_decisions.py", data["next_decision_audit_command"])


if __name__ == "__main__":
    unittest.main()
