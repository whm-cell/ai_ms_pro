from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "governance-and-smoke.yml"
sys.path.insert(0, str(ROOT / "scripts"))

import check_harness_burn_in_readiness  # noqa: E402
import harness_collection_command_coverage as command_coverage  # noqa: E402


class GovernanceWorkflowSampleOutputsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow_text = WORKFLOW.read_text(encoding="utf-8")
        cls.readiness_report = check_harness_burn_in_readiness.build_report(
            include_future=True,
            include_accepted=True,
        )

    def workflow_step(self, name: str) -> str:
        marker = f"      - name: {name}\n"
        start = self.workflow_text.index(marker)
        end = self.workflow_text.find("\n      - name:", start + len(marker))
        if end == -1:
            end = len(self.workflow_text)
        return self.workflow_text[start:end]

    def assert_workflow_contains_commands(self, commands: tuple[str, ...]) -> None:
        for command in commands:
            self.assertIn(command, self.workflow_text)

    def assert_workflow_contains_summary_sections(self, sections: tuple[str, ...]) -> None:
        for section in sections:
            self.assertIn(section, self.workflow_text)

    def test_workflow_summary_covers_active_real_sample_collection_filters(self) -> None:
        for capture_gate in command_coverage.real_sample_capture_gate_values(self.readiness_report):
            self.assert_workflow_contains_commands(
                command_coverage.workflow_capture_gate_summary_commands(capture_gate)
            )
            self.assert_workflow_contains_summary_sections(
                command_coverage.workflow_capture_gate_summary_sections(capture_gate)
            )

        for ledger_action in command_coverage.real_sample_ledger_action_values(self.readiness_report):
            self.assert_workflow_contains_commands(
                command_coverage.workflow_real_sample_ledger_action_summary_commands(ledger_action)
            )
            self.assert_workflow_contains_summary_sections(
                command_coverage.workflow_real_sample_ledger_action_summary_sections(ledger_action)
            )

        for readiness in command_coverage.real_sample_readiness_values(self.readiness_report):
            self.assert_workflow_contains_commands(
                command_coverage.workflow_real_sample_readiness_summary_commands(readiness)
            )
            self.assert_workflow_contains_summary_sections(
                command_coverage.workflow_real_sample_readiness_summary_sections(readiness)
            )

        for area in command_coverage.real_sample_area_values(self.readiness_report):
            self.assert_workflow_contains_commands(
                command_coverage.workflow_real_sample_area_summary_commands(area)
            )
            self.assert_workflow_contains_summary_sections(
                command_coverage.workflow_real_sample_area_summary_sections(area)
            )

        for priority in command_coverage.real_sample_priority_values(self.readiness_report):
            self.assert_workflow_contains_commands(
                command_coverage.workflow_real_sample_priority_summary_commands(priority)
            )
            self.assert_workflow_contains_summary_sections(
                command_coverage.workflow_real_sample_priority_summary_sections(priority)
            )

    def test_pending_sample_slot_audit_surfaces_full_lane_outputs(self) -> None:
        step = self.workflow_step("Run harness pending sample slot audit")

        self.assertIn("run: |", step)
        self.assertIn(
            "python3 scripts/check_harness_pending_samples.py --include-future --include-accepted > "
            "/tmp/harness-pending-samples.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_pending_samples.py --include-future --include-accepted --json > "
            "/tmp/harness-pending-samples.json",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_pending_samples.py --capture-focus > "
            "/tmp/harness-pending-capture-focus.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_pending_samples.py --capture-focus --capture-focus-limit 0 > "
            "/tmp/harness-pending-capture-focus-all.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-area agentic-red-team --capture-focus-limit 0 > "
            "/tmp/harness-pending-capture-focus-area-agentic-red-team.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-area ai-guardrail --capture-focus-limit 0 > "
            "/tmp/harness-pending-capture-focus-area-ai-guardrail.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-area runtime-durability --capture-focus-limit 0 > "
            "/tmp/harness-pending-capture-focus-area-runtime-durability.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-area security-evidence --capture-focus-limit 0 > "
            "/tmp/harness-pending-capture-focus-area-security-evidence.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-area trace-interop --capture-focus-limit 0 > "
            "/tmp/harness-pending-capture-focus-area-trace-interop.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-area workflow-skills --capture-focus-limit 0 > "
            "/tmp/harness-pending-capture-focus-area-workflow-skills.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-priority P0 --capture-focus-limit 0 > "
            "/tmp/harness-pending-capture-focus-priority-p0.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-priority P1 --capture-focus-limit 0 > "
            "/tmp/harness-pending-capture-focus-priority-p1.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-priority P2 --capture-focus-limit 0 > "
            "/tmp/harness-pending-capture-focus-priority-p2.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-priority P3 --capture-focus-limit 0 > "
            "/tmp/harness-pending-capture-focus-priority-p3.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-ledger-action append-new-pending-slot --capture-focus-limit 0 > "
            "/tmp/harness-pending-capture-focus-append-new-pending-slot.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-ledger-action fill-existing-placeholder --capture-focus-limit 0 > "
            "/tmp/harness-pending-capture-focus-fill-existing-placeholder.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-gate requires-approved-remote-interop --capture-focus-limit 0 > "
            "/tmp/harness-pending-capture-focus-remote-interop.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-gate requires-approved-bounded-incident --capture-focus-limit 0 > "
            "/tmp/harness-pending-capture-focus-approved-bounded-incident.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-gate replace-placeholder-after-real-event --capture-focus-limit 0 > "
            "/tmp/harness-pending-capture-focus-placeholder-replacement.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-gate requires-security-workflow-event --capture-focus-limit 0 > "
            "/tmp/harness-pending-capture-focus-security-event.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-gate requires-bounded-real-incident --capture-focus-limit 0 > "
            "/tmp/harness-pending-capture-focus-bounded-real-incident.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-gate requires-workflow-task-event --capture-focus-limit 0 > "
            "/tmp/harness-pending-capture-focus-workflow-task-event.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-gate requires-cross-task-resume --capture-focus-limit 0 > "
            "/tmp/harness-pending-capture-focus-cross-task-resume.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-gate requires-distinct-task-class-report --capture-focus-limit 0 > "
            "/tmp/harness-pending-capture-focus-distinct-task-class-report.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-gate requires-user-confirmed-high-impact-action --capture-focus-limit 0 > "
            "/tmp/harness-pending-capture-focus-user-confirmed-high-impact-action.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-readiness needs-first-real-sample --capture-focus-limit 0 > "
            "/tmp/harness-pending-capture-focus-needs-first-real-sample.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-readiness needs-more-real-samples --capture-focus-limit 0 > "
            "/tmp/harness-pending-capture-focus-needs-more-real-samples.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_pending_samples.py --review-state placeholder --review-cards > "
            "/tmp/harness-pending-review-cards.md",
            step,
        )
        self.assertIn("### Harness pending sample lanes", step)
        self.assertIn("cat /tmp/harness-pending-samples.md", step)
        self.assertIn("### Harness pending next capture focus", step)
        self.assertIn("cat /tmp/harness-pending-capture-focus.md", step)
        self.assertIn("### Harness pending next capture focus (all matching lanes)", step)
        self.assertIn("cat /tmp/harness-pending-capture-focus-all.md", step)
        self.assertIn("### Harness pending next capture focus (area agentic-red-team)", step)
        self.assertIn("cat /tmp/harness-pending-capture-focus-area-agentic-red-team.md", step)
        self.assertIn("### Harness pending next capture focus (area ai-guardrail)", step)
        self.assertIn("cat /tmp/harness-pending-capture-focus-area-ai-guardrail.md", step)
        self.assertIn("### Harness pending next capture focus (area runtime-durability)", step)
        self.assertIn("cat /tmp/harness-pending-capture-focus-area-runtime-durability.md", step)
        self.assertIn("### Harness pending next capture focus (area security-evidence)", step)
        self.assertIn("cat /tmp/harness-pending-capture-focus-area-security-evidence.md", step)
        self.assertIn("### Harness pending next capture focus (area trace-interop)", step)
        self.assertIn("cat /tmp/harness-pending-capture-focus-area-trace-interop.md", step)
        self.assertIn("### Harness pending next capture focus (area workflow-skills)", step)
        self.assertIn("cat /tmp/harness-pending-capture-focus-area-workflow-skills.md", step)
        self.assertIn("### Harness pending next capture focus (priority P0)", step)
        self.assertIn("cat /tmp/harness-pending-capture-focus-priority-p0.md", step)
        self.assertIn("### Harness pending next capture focus (priority P1)", step)
        self.assertIn("cat /tmp/harness-pending-capture-focus-priority-p1.md", step)
        self.assertIn("### Harness pending next capture focus (priority P2)", step)
        self.assertIn("cat /tmp/harness-pending-capture-focus-priority-p2.md", step)
        self.assertIn("### Harness pending next capture focus (priority P3)", step)
        self.assertIn("cat /tmp/harness-pending-capture-focus-priority-p3.md", step)
        self.assertIn("### Harness pending next capture focus (append new pending slot)", step)
        self.assertIn("cat /tmp/harness-pending-capture-focus-append-new-pending-slot.md", step)
        self.assertIn("### Harness pending next capture focus (fill existing placeholder)", step)
        self.assertIn("cat /tmp/harness-pending-capture-focus-fill-existing-placeholder.md", step)
        self.assertIn("### Harness pending next capture focus (remote interop)", step)
        self.assertIn("cat /tmp/harness-pending-capture-focus-remote-interop.md", step)
        self.assertIn("### Harness pending next capture focus (approved bounded incident)", step)
        self.assertIn("cat /tmp/harness-pending-capture-focus-approved-bounded-incident.md", step)
        self.assertIn("### Harness pending next capture focus (placeholder replacement)", step)
        self.assertIn("cat /tmp/harness-pending-capture-focus-placeholder-replacement.md", step)
        self.assertIn("### Harness pending next capture focus (security workflow event)", step)
        self.assertIn("cat /tmp/harness-pending-capture-focus-security-event.md", step)
        self.assertIn("### Harness pending next capture focus (bounded real incident)", step)
        self.assertIn("cat /tmp/harness-pending-capture-focus-bounded-real-incident.md", step)
        self.assertIn("### Harness pending next capture focus (workflow task event)", step)
        self.assertIn("cat /tmp/harness-pending-capture-focus-workflow-task-event.md", step)
        self.assertIn("### Harness pending next capture focus (cross-task resume)", step)
        self.assertIn("cat /tmp/harness-pending-capture-focus-cross-task-resume.md", step)
        self.assertIn("### Harness pending next capture focus (distinct task class report)", step)
        self.assertIn("cat /tmp/harness-pending-capture-focus-distinct-task-class-report.md", step)
        self.assertIn("### Harness pending next capture focus (user confirmed high impact action)", step)
        self.assertIn("cat /tmp/harness-pending-capture-focus-user-confirmed-high-impact-action.md", step)
        self.assertIn("### Harness pending next capture focus (needs first real sample)", step)
        self.assertIn("cat /tmp/harness-pending-capture-focus-needs-first-real-sample.md", step)
        self.assertIn("### Harness pending next capture focus (needs more real samples)", step)
        self.assertIn("cat /tmp/harness-pending-capture-focus-needs-more-real-samples.md", step)
        self.assertIn("### Harness pending placeholder review cards", step)
        self.assertIn("cat /tmp/harness-pending-review-cards.md", step)
        self.assertIn('>> "$GITHUB_STEP_SUMMARY"', step)

    def test_collection_planner_surfaces_markdown_and_json_outputs(self) -> None:
        step = self.workflow_step("Run harness sample collection planner")

        self.assertIn("run: |", step)
        self.assertIn(
            "python3 scripts/plan_harness_sample_collection.py > /tmp/harness-sample-collection.md",
            step,
        )
        self.assertIn(
            "python3 scripts/plan_harness_sample_collection.py --json > /tmp/harness-sample-collection.json",
            step,
        )
        self.assertIn(
            "python3 scripts/plan_harness_sample_collection.py --ledger-action append-new-pending-slot "
            "--capture-card > /tmp/harness-sample-collection-append-new-pending-slot.md",
            step,
        )
        self.assertIn(
            "python3 scripts/plan_harness_sample_collection.py --ledger-action fill-existing-placeholder "
            "--capture-card > /tmp/harness-sample-collection-fill-existing-placeholder.md",
            step,
        )
        self.assertIn(
            "python3 scripts/plan_harness_sample_collection.py "
            "--capture-gate requires-approved-remote-interop --capture-card > "
            "/tmp/harness-sample-collection-remote-interop.md",
            step,
        )
        self.assertIn(
            "python3 scripts/plan_harness_sample_collection.py "
            "--capture-gate requires-approved-bounded-incident --capture-card > "
            "/tmp/harness-sample-collection-approved-bounded-incident.md",
            step,
        )
        self.assertIn(
            "python3 scripts/plan_harness_sample_collection.py "
            "--capture-gate replace-placeholder-after-real-event --capture-card > "
            "/tmp/harness-sample-collection-placeholder-replacement.md",
            step,
        )
        self.assertIn(
            "python3 scripts/plan_harness_sample_collection.py "
            "--capture-gate requires-security-workflow-event --capture-card > "
            "/tmp/harness-sample-collection-security-event.md",
            step,
        )
        self.assertIn(
            "python3 scripts/plan_harness_sample_collection.py "
            "--capture-gate requires-bounded-real-incident --capture-card > "
            "/tmp/harness-sample-collection-bounded-real-incident.md",
            step,
        )
        self.assertIn(
            "python3 scripts/plan_harness_sample_collection.py "
            "--capture-gate requires-workflow-task-event --capture-card > "
            "/tmp/harness-sample-collection-workflow-task-event.md",
            step,
        )
        self.assertIn(
            "python3 scripts/plan_harness_sample_collection.py "
            "--capture-gate requires-cross-task-resume --capture-card > "
            "/tmp/harness-sample-collection-cross-task-resume.md",
            step,
        )
        self.assertIn(
            "python3 scripts/plan_harness_sample_collection.py "
            "--capture-gate requires-distinct-task-class-report --capture-card > "
            "/tmp/harness-sample-collection-distinct-task-class-report.md",
            step,
        )
        self.assertIn(
            "python3 scripts/plan_harness_sample_collection.py "
            "--capture-gate requires-user-confirmed-high-impact-action --capture-card > "
            "/tmp/harness-sample-collection-user-confirmed-high-impact-action.md",
            step,
        )
        self.assertIn(
            "python3 scripts/plan_harness_sample_collection.py --ledger-action review-upgrade-decision "
            "--capture-card > /tmp/harness-sample-collection-upgrade-decision-review.md",
            step,
        )
        self.assertIn(
            "python3 scripts/plan_harness_sample_collection.py --readiness needs-more-real-samples "
            "--capture-card > /tmp/harness-sample-collection-needs-more-real-samples.md",
            step,
        )
        self.assertIn(
            "python3 scripts/plan_harness_sample_collection.py --readiness needs-first-real-sample "
            "--capture-card > /tmp/harness-sample-collection-needs-first-real-sample.md",
            step,
        )
        self.assertIn(
            "python3 scripts/plan_harness_sample_collection.py --readiness ready-for-upgrade-discussion "
            "--capture-card > /tmp/harness-sample-collection-ready-for-upgrade-discussion.md",
            step,
        )
        self.assertIn(
            "python3 scripts/plan_harness_sample_collection.py --include-accepted --readiness local-sample-only "
            "--capture-card > /tmp/harness-sample-collection-local-sample-only.md",
            step,
        )
        self.assertIn("### Harness sample collection queue", step)
        self.assertIn("cat /tmp/harness-sample-collection.md", step)
        self.assertIn("### Harness sample collection queue (append new pending slot)", step)
        self.assertIn("cat /tmp/harness-sample-collection-append-new-pending-slot.md", step)
        self.assertIn("### Harness sample collection queue (fill existing placeholder)", step)
        self.assertIn("cat /tmp/harness-sample-collection-fill-existing-placeholder.md", step)
        self.assertIn("### Harness sample collection queue (remote interop)", step)
        self.assertIn("cat /tmp/harness-sample-collection-remote-interop.md", step)
        self.assertIn("### Harness sample collection queue (approved bounded incident)", step)
        self.assertIn("cat /tmp/harness-sample-collection-approved-bounded-incident.md", step)
        self.assertIn("### Harness sample collection queue (placeholder replacement)", step)
        self.assertIn("cat /tmp/harness-sample-collection-placeholder-replacement.md", step)
        self.assertIn("### Harness sample collection queue (security workflow event)", step)
        self.assertIn("cat /tmp/harness-sample-collection-security-event.md", step)
        self.assertIn("### Harness sample collection queue (bounded real incident)", step)
        self.assertIn("cat /tmp/harness-sample-collection-bounded-real-incident.md", step)
        self.assertIn("### Harness sample collection queue (workflow task event)", step)
        self.assertIn("cat /tmp/harness-sample-collection-workflow-task-event.md", step)
        self.assertIn("### Harness sample collection queue (cross-task resume)", step)
        self.assertIn("cat /tmp/harness-sample-collection-cross-task-resume.md", step)
        self.assertIn("### Harness sample collection queue (distinct task class report)", step)
        self.assertIn("cat /tmp/harness-sample-collection-distinct-task-class-report.md", step)
        self.assertIn("### Harness sample collection queue (user confirmed high impact action)", step)
        self.assertIn("cat /tmp/harness-sample-collection-user-confirmed-high-impact-action.md", step)
        self.assertIn("### Harness sample collection queue (upgrade decision review)", step)
        self.assertIn("cat /tmp/harness-sample-collection-upgrade-decision-review.md", step)
        self.assertIn("### Harness sample collection queue (needs first real sample)", step)
        self.assertIn("cat /tmp/harness-sample-collection-needs-first-real-sample.md", step)
        self.assertIn("### Harness sample collection queue (needs more real samples)", step)
        self.assertIn("cat /tmp/harness-sample-collection-needs-more-real-samples.md", step)
        self.assertIn("### Harness sample collection queue (ready for upgrade discussion)", step)
        self.assertIn("cat /tmp/harness-sample-collection-ready-for-upgrade-discussion.md", step)
        self.assertIn("### Harness sample collection queue (local sample only)", step)
        self.assertIn("cat /tmp/harness-sample-collection-local-sample-only.md", step)
        self.assertIn('>> "$GITHUB_STEP_SUMMARY"', step)

    def test_sample_gap_collector_surfaces_markdown_and_json_outputs(self) -> None:
        step = self.workflow_step("Run harness sample gap collector")

        self.assertIn("run: |", step)
        self.assertIn(
            "python3 scripts/collect_harness_sample_gaps.py > /tmp/harness-sample-gaps.md",
            step,
        )
        self.assertIn(
            "python3 scripts/collect_harness_sample_gaps.py --json > /tmp/harness-sample-gaps.json",
            step,
        )
        self.assertIn("### Harness sample gaps", step)
        self.assertIn("cat /tmp/harness-sample-gaps.md", step)
        self.assertIn('>> "$GITHUB_STEP_SUMMARY"', step)

    def test_sample_followup_coverage_surfaces_markdown_and_json_outputs(self) -> None:
        step = self.workflow_step("Run harness sample follow-up coverage audit")

        self.assertIn("run: |", step)
        self.assertIn(
            "python3 scripts/check_harness_sample_followup_coverage.py > "
            "/tmp/harness-sample-followup-coverage.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_sample_followup_coverage.py --json > "
            "/tmp/harness-sample-followup-coverage.json",
            step,
        )
        self.assertIn("### Harness sample follow-up coverage", step)
        self.assertIn("cat /tmp/harness-sample-followup-coverage.md", step)
        self.assertIn('>> "$GITHUB_STEP_SUMMARY"', step)

    def test_warning_sample_code_alignment_runs_in_workflow(self) -> None:
        step = self.workflow_step("Run warning sample code alignment check")

        self.assertIn("run: python3 scripts/check_warning_sample_code_alignment.py", step)

    def test_harness_collection_config_check_runs_in_workflow(self) -> None:
        step = self.workflow_step("Run harness collection config checks")

        self.assertIn("run: python3 scripts/check_harness_collection_config.py", step)

    def test_burn_in_ledger_audit_surfaces_markdown_and_json_outputs(self) -> None:
        step = self.workflow_step("Run check burn-in ledger audit")

        self.assertIn("run: |", step)
        self.assertIn("python3 scripts/check_burn_in_ledger.py > /tmp/check-burn-in-ledger.md", step)
        self.assertIn("python3 scripts/check_burn_in_ledger.py --json > /tmp/check-burn-in-ledger.json", step)
        self.assertIn("### Check burn-in ledger", step)
        self.assertIn("cat /tmp/check-burn-in-ledger.md", step)
        self.assertIn('>> "$GITHUB_STEP_SUMMARY"', step)

    def test_burn_in_upgrade_decision_audit_surfaces_markdown_and_json_outputs(self) -> None:
        step = self.workflow_step("Run check burn-in upgrade decision audit")

        self.assertIn("run: |", step)
        self.assertIn(
            "python3 scripts/check_burn_in_upgrade_decisions.py > /tmp/check-burn-in-upgrade-decisions.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_burn_in_upgrade_decisions.py --json > /tmp/check-burn-in-upgrade-decisions.json",
            step,
        )
        self.assertIn("### Check burn-in upgrade decisions", step)
        self.assertIn("cat /tmp/check-burn-in-upgrade-decisions.md", step)
        self.assertIn('>> "$GITHUB_STEP_SUMMARY"', step)

    def test_burn_in_readiness_audit_surfaces_inclusive_outputs(self) -> None:
        step = self.workflow_step("Run harness burn-in readiness audit")

        self.assertIn("run: |", step)
        self.assertIn(
            "python3 scripts/check_harness_burn_in_readiness.py --include-future --include-accepted > "
            "/tmp/harness-burn-in-readiness.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --json > "
            "/tmp/harness-burn-in-readiness.json",
            step,
        )
        for area in command_coverage.real_sample_area_values(self.readiness_report):
            self.assertIn(
                "python3 scripts/check_harness_burn_in_readiness.py --include-future --include-accepted "
                f"--area {area} > /tmp/harness-burn-in-readiness-area-{area}.md",
                step,
            )
        for priority in command_coverage.real_sample_priority_values(self.readiness_report):
            self.assertIn(
                "python3 scripts/check_harness_burn_in_readiness.py --include-future --include-accepted "
                f"--priority {priority} > /tmp/harness-burn-in-readiness-priority-{priority.lower()}.md",
                step,
            )
        self.assertIn(
            "python3 scripts/check_harness_burn_in_readiness.py --include-future --include-accepted "
            "--capture-gate requires-approved-remote-interop > /tmp/harness-burn-in-readiness-remote-interop.md",
            step,
        )
        focused_capture_gate_outputs = {
            "requires-approved-bounded-incident": "approved-bounded-incident",
            "replace-placeholder-after-real-event": "placeholder-replacement",
            "requires-security-workflow-event": "security-event",
            "requires-bounded-real-incident": "bounded-real-incident",
            "requires-workflow-task-event": "workflow-task-event",
            "requires-cross-task-resume": "cross-task-resume",
            "requires-distinct-task-class-report": "distinct-task-class-report",
            "requires-user-confirmed-high-impact-action": "user-confirmed-high-impact-action",
            "upgrade-decision-review": "upgrade-decision-review",
        }
        for capture_gate, output_slug in focused_capture_gate_outputs.items():
            self.assertIn(
                "python3 scripts/check_harness_burn_in_readiness.py --include-future --include-accepted "
                f"--capture-gate {capture_gate} > /tmp/harness-burn-in-readiness-{output_slug}.md",
                step,
            )
        self.assertIn(
            "python3 scripts/check_harness_burn_in_readiness.py --include-future --include-accepted "
            "--readiness needs-first-real-sample > /tmp/harness-burn-in-readiness-needs-first-real-sample.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_burn_in_readiness.py --include-future --include-accepted "
            "--readiness needs-more-real-samples > /tmp/harness-burn-in-readiness-needs-more-real-samples.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_burn_in_readiness.py --include-future --include-accepted "
            "--readiness ready-for-upgrade-discussion > "
            "/tmp/harness-burn-in-readiness-ready-for-upgrade-discussion.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_burn_in_readiness.py --include-future --include-accepted "
            "--readiness local-sample-only > /tmp/harness-burn-in-readiness-local-sample-only.md",
            step,
        )
        self.assertIn("### Harness burn-in readiness", step)
        self.assertIn("cat /tmp/harness-burn-in-readiness.md", step)
        for area in command_coverage.real_sample_area_values(self.readiness_report):
            self.assertIn(f"### Harness burn-in readiness (area {area})", step)
            self.assertIn(f"cat /tmp/harness-burn-in-readiness-area-{area}.md", step)
        for priority in command_coverage.real_sample_priority_values(self.readiness_report):
            self.assertIn(f"### Harness burn-in readiness (priority {priority})", step)
            self.assertIn(
                f"cat /tmp/harness-burn-in-readiness-priority-{priority.lower()}.md",
                step,
            )
        self.assertIn("### Harness burn-in readiness (remote interop)", step)
        self.assertIn("cat /tmp/harness-burn-in-readiness-remote-interop.md", step)
        focused_capture_gate_sections = {
            "approved bounded incident": "approved-bounded-incident",
            "placeholder replacement": "placeholder-replacement",
            "security workflow event": "security-event",
            "bounded real incident": "bounded-real-incident",
            "workflow task event": "workflow-task-event",
            "cross-task resume": "cross-task-resume",
            "distinct task class report": "distinct-task-class-report",
            "user confirmed high impact action": "user-confirmed-high-impact-action",
            "upgrade decision review": "upgrade-decision-review",
        }
        for label, output_slug in focused_capture_gate_sections.items():
            self.assertIn(f"### Harness burn-in readiness ({label})", step)
            self.assertIn(f"cat /tmp/harness-burn-in-readiness-{output_slug}.md", step)
        self.assertIn("### Harness burn-in readiness (needs first real sample)", step)
        self.assertIn("cat /tmp/harness-burn-in-readiness-needs-first-real-sample.md", step)
        self.assertIn("### Harness burn-in readiness (needs more real samples)", step)
        self.assertIn("cat /tmp/harness-burn-in-readiness-needs-more-real-samples.md", step)
        self.assertIn("### Harness burn-in readiness (ready for upgrade discussion)", step)
        self.assertIn("cat /tmp/harness-burn-in-readiness-ready-for-upgrade-discussion.md", step)
        self.assertIn("### Harness burn-in readiness (local sample only)", step)
        self.assertIn("cat /tmp/harness-burn-in-readiness-local-sample-only.md", step)
        self.assertIn('>> "$GITHUB_STEP_SUMMARY"', step)

    def test_upgrade_decision_audit_surfaces_markdown_and_json_outputs(self) -> None:
        step = self.workflow_step("Run harness upgrade decision audit")

        self.assertIn("run: |", step)
        self.assertIn(
            "python3 scripts/check_harness_upgrade_decisions.py > /tmp/harness-upgrade-decisions.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_upgrade_decisions.py --json > "
            "/tmp/harness-upgrade-decisions.json",
            step,
        )
        self.assertIn("### Harness upgrade decisions", step)
        self.assertIn("cat /tmp/harness-upgrade-decisions.md", step)
        self.assertIn('>> "$GITHUB_STEP_SUMMARY"', step)

    def test_sample_template_drift_checks_surface_focused_readiness_outputs(self) -> None:
        step = self.workflow_step("Run harness sample template drift checks")

        self.assertIn("run: |", step)
        self.assertIn(
            "python3 scripts/check_harness_sample_templates.py > /tmp/harness-sample-templates.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_sample_templates.py --ledger-action append-new-pending-slot > "
            "/tmp/harness-sample-templates-append-new-pending-slot.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_sample_templates.py --ledger-action fill-existing-placeholder > "
            "/tmp/harness-sample-templates-fill-existing-placeholder.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_sample_templates.py "
            "--capture-gate requires-approved-remote-interop > "
            "/tmp/harness-sample-templates-remote-interop.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_sample_templates.py "
            "--capture-gate requires-approved-bounded-incident > "
            "/tmp/harness-sample-templates-approved-bounded-incident.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_sample_templates.py "
            "--capture-gate replace-placeholder-after-real-event > "
            "/tmp/harness-sample-templates-placeholder-replacement.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_sample_templates.py "
            "--capture-gate requires-security-workflow-event > "
            "/tmp/harness-sample-templates-security-event.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_sample_templates.py "
            "--capture-gate requires-bounded-real-incident > "
            "/tmp/harness-sample-templates-bounded-real-incident.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_sample_templates.py "
            "--capture-gate requires-workflow-task-event > "
            "/tmp/harness-sample-templates-workflow-task-event.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_sample_templates.py "
            "--capture-gate requires-cross-task-resume > "
            "/tmp/harness-sample-templates-cross-task-resume.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_sample_templates.py "
            "--capture-gate requires-distinct-task-class-report > "
            "/tmp/harness-sample-templates-distinct-task-class-report.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_sample_templates.py "
            "--capture-gate requires-user-confirmed-high-impact-action > "
            "/tmp/harness-sample-templates-user-confirmed-high-impact-action.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_sample_templates.py --ledger-action review-upgrade-decision > "
            "/tmp/harness-sample-templates-upgrade-decision-review.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_sample_templates.py --readiness needs-first-real-sample > "
            "/tmp/harness-sample-templates-needs-first-real-sample.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_sample_templates.py --readiness needs-more-real-samples > "
            "/tmp/harness-sample-templates-needs-more-real-samples.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_sample_templates.py --readiness ready-for-upgrade-discussion > "
            "/tmp/harness-sample-templates-ready-for-upgrade-discussion.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_sample_templates.py --readiness local-sample-only > "
            "/tmp/harness-sample-templates-local-sample-only.md",
            step,
        )
        self.assertIn("### Harness sample template drift", step)
        self.assertIn("cat /tmp/harness-sample-templates.md", step)
        self.assertIn("### Harness sample template drift (append new pending slot)", step)
        self.assertIn("cat /tmp/harness-sample-templates-append-new-pending-slot.md", step)
        self.assertIn("### Harness sample template drift (fill existing placeholder)", step)
        self.assertIn("cat /tmp/harness-sample-templates-fill-existing-placeholder.md", step)
        self.assertIn("### Harness sample template drift (remote interop)", step)
        self.assertIn("cat /tmp/harness-sample-templates-remote-interop.md", step)
        self.assertIn("### Harness sample template drift (approved bounded incident)", step)
        self.assertIn("cat /tmp/harness-sample-templates-approved-bounded-incident.md", step)
        self.assertIn("### Harness sample template drift (placeholder replacement)", step)
        self.assertIn("cat /tmp/harness-sample-templates-placeholder-replacement.md", step)
        self.assertIn("### Harness sample template drift (security workflow event)", step)
        self.assertIn("cat /tmp/harness-sample-templates-security-event.md", step)
        self.assertIn("### Harness sample template drift (bounded real incident)", step)
        self.assertIn("cat /tmp/harness-sample-templates-bounded-real-incident.md", step)
        self.assertIn("### Harness sample template drift (workflow task event)", step)
        self.assertIn("cat /tmp/harness-sample-templates-workflow-task-event.md", step)
        self.assertIn("### Harness sample template drift (cross-task resume)", step)
        self.assertIn("cat /tmp/harness-sample-templates-cross-task-resume.md", step)
        self.assertIn("### Harness sample template drift (distinct task class report)", step)
        self.assertIn("cat /tmp/harness-sample-templates-distinct-task-class-report.md", step)
        self.assertIn("### Harness sample template drift (user confirmed high impact action)", step)
        self.assertIn("cat /tmp/harness-sample-templates-user-confirmed-high-impact-action.md", step)
        self.assertIn("### Harness sample template drift (upgrade decision review)", step)
        self.assertIn("cat /tmp/harness-sample-templates-upgrade-decision-review.md", step)
        self.assertIn("### Harness sample template drift (needs first real sample)", step)
        self.assertIn("cat /tmp/harness-sample-templates-needs-first-real-sample.md", step)
        self.assertIn("### Harness sample template drift (needs more real samples)", step)
        self.assertIn("cat /tmp/harness-sample-templates-needs-more-real-samples.md", step)
        self.assertIn("### Harness sample template drift (ready for upgrade discussion)", step)
        self.assertIn("cat /tmp/harness-sample-templates-ready-for-upgrade-discussion.md", step)
        self.assertIn("### Harness sample template drift (local sample only)", step)
        self.assertIn("cat /tmp/harness-sample-templates-local-sample-only.md", step)
        self.assertIn('>> "$GITHUB_STEP_SUMMARY"', step)

    def test_sample_intake_bundle_surfaces_full_and_summary_outputs(self) -> None:
        step = self.workflow_step("Run harness sample intake bundle")

        self.assertIn("run: |", step)
        self.assertIn(
            "python3 scripts/build_harness_sample_intake_bundle.py > "
            "/tmp/harness-sample-intake-bundle.md",
            step,
        )
        self.assertIn(
            "python3 scripts/build_harness_sample_intake_bundle.py --json > "
            "/tmp/harness-sample-intake-bundle.json",
            step,
        )
        self.assertIn(
            "python3 scripts/build_harness_sample_intake_bundle.py --summary > "
            "/tmp/harness-sample-intake-summary.md",
            step,
        )
        self.assertIn(
            "python3 scripts/build_harness_sample_intake_bundle.py --ledger-action append-new-pending-slot "
            "--summary > /tmp/harness-sample-intake-append-new-pending-slot.md",
            step,
        )
        self.assertIn(
            "python3 scripts/build_harness_sample_intake_bundle.py --ledger-action fill-existing-placeholder "
            "--summary > /tmp/harness-sample-intake-fill-existing-placeholder.md",
            step,
        )
        self.assertIn(
            "python3 scripts/build_harness_sample_intake_bundle.py "
            "--capture-gate requires-approved-remote-interop --summary > "
            "/tmp/harness-sample-intake-remote-interop.md",
            step,
        )
        self.assertIn(
            "python3 scripts/build_harness_sample_intake_bundle.py "
            "--capture-gate requires-approved-bounded-incident --summary > "
            "/tmp/harness-sample-intake-approved-bounded-incident.md",
            step,
        )
        self.assertIn(
            "python3 scripts/build_harness_sample_intake_bundle.py "
            "--capture-gate replace-placeholder-after-real-event --summary > "
            "/tmp/harness-sample-intake-placeholder-replacement.md",
            step,
        )
        self.assertIn(
            "python3 scripts/build_harness_sample_intake_bundle.py "
            "--capture-gate requires-security-workflow-event --summary > "
            "/tmp/harness-sample-intake-security-event.md",
            step,
        )
        self.assertIn(
            "python3 scripts/build_harness_sample_intake_bundle.py "
            "--capture-gate requires-bounded-real-incident --summary > "
            "/tmp/harness-sample-intake-bounded-real-incident.md",
            step,
        )
        self.assertIn(
            "python3 scripts/build_harness_sample_intake_bundle.py "
            "--capture-gate requires-workflow-task-event --summary > "
            "/tmp/harness-sample-intake-workflow-task-event.md",
            step,
        )
        self.assertIn(
            "python3 scripts/build_harness_sample_intake_bundle.py "
            "--capture-gate requires-cross-task-resume --summary > "
            "/tmp/harness-sample-intake-cross-task-resume.md",
            step,
        )
        self.assertIn(
            "python3 scripts/build_harness_sample_intake_bundle.py "
            "--capture-gate requires-distinct-task-class-report --summary > "
            "/tmp/harness-sample-intake-distinct-task-class-report.md",
            step,
        )
        self.assertIn(
            "python3 scripts/build_harness_sample_intake_bundle.py "
            "--capture-gate requires-user-confirmed-high-impact-action --summary > "
            "/tmp/harness-sample-intake-user-confirmed-high-impact-action.md",
            step,
        )
        self.assertIn(
            "python3 scripts/build_harness_sample_intake_bundle.py --ledger-action review-upgrade-decision "
            "--summary > /tmp/harness-sample-intake-upgrade-decision-review.md",
            step,
        )
        self.assertIn(
            "python3 scripts/build_harness_sample_intake_bundle.py --readiness needs-more-real-samples "
            "--summary > /tmp/harness-sample-intake-needs-more-real-samples.md",
            step,
        )
        self.assertIn(
            "python3 scripts/build_harness_sample_intake_bundle.py --readiness needs-first-real-sample "
            "--summary > /tmp/harness-sample-intake-needs-first-real-sample.md",
            step,
        )
        self.assertIn(
            "python3 scripts/build_harness_sample_intake_bundle.py --readiness ready-for-upgrade-discussion "
            "--summary > /tmp/harness-sample-intake-ready-for-upgrade-discussion.md",
            step,
        )
        self.assertIn("### Harness sample intake bundle", step)
        self.assertIn("cat /tmp/harness-sample-intake-summary.md", step)
        self.assertIn("### Harness sample intake bundle (append new pending slot)", step)
        self.assertIn("cat /tmp/harness-sample-intake-append-new-pending-slot.md", step)
        self.assertIn("### Harness sample intake bundle (fill existing placeholder)", step)
        self.assertIn("cat /tmp/harness-sample-intake-fill-existing-placeholder.md", step)
        self.assertIn("### Harness sample intake bundle (remote interop)", step)
        self.assertIn("cat /tmp/harness-sample-intake-remote-interop.md", step)
        self.assertIn("### Harness sample intake bundle (approved bounded incident)", step)
        self.assertIn("cat /tmp/harness-sample-intake-approved-bounded-incident.md", step)
        self.assertIn("### Harness sample intake bundle (placeholder replacement)", step)
        self.assertIn("cat /tmp/harness-sample-intake-placeholder-replacement.md", step)
        self.assertIn("### Harness sample intake bundle (security workflow event)", step)
        self.assertIn("cat /tmp/harness-sample-intake-security-event.md", step)
        self.assertIn("### Harness sample intake bundle (bounded real incident)", step)
        self.assertIn("cat /tmp/harness-sample-intake-bounded-real-incident.md", step)
        self.assertIn("### Harness sample intake bundle (workflow task event)", step)
        self.assertIn("cat /tmp/harness-sample-intake-workflow-task-event.md", step)
        self.assertIn("### Harness sample intake bundle (cross-task resume)", step)
        self.assertIn("cat /tmp/harness-sample-intake-cross-task-resume.md", step)
        self.assertIn("### Harness sample intake bundle (distinct task class report)", step)
        self.assertIn("cat /tmp/harness-sample-intake-distinct-task-class-report.md", step)
        self.assertIn("### Harness sample intake bundle (user confirmed high impact action)", step)
        self.assertIn("cat /tmp/harness-sample-intake-user-confirmed-high-impact-action.md", step)
        self.assertIn("### Harness sample intake bundle (upgrade decision review)", step)
        self.assertIn("cat /tmp/harness-sample-intake-upgrade-decision-review.md", step)
        self.assertIn("### Harness sample intake bundle (needs first real sample)", step)
        self.assertIn("cat /tmp/harness-sample-intake-needs-first-real-sample.md", step)
        self.assertIn("### Harness sample intake bundle (needs more real samples)", step)
        self.assertIn("cat /tmp/harness-sample-intake-needs-more-real-samples.md", step)
        self.assertIn("### Harness sample intake bundle (ready for upgrade discussion)", step)
        self.assertIn("cat /tmp/harness-sample-intake-ready-for-upgrade-discussion.md", step)
        self.assertIn('>> "$GITHUB_STEP_SUMMARY"', step)

    def test_future_work_contract_check_surfaces_markdown_and_json_outputs(self) -> None:
        step = self.workflow_step("Run harness future-work contract checks")

        self.assertIn("run: |", step)
        self.assertIn(
            "python3 scripts/check_harness_future_work_contracts.py > /tmp/harness-future-work-contracts.md",
            step,
        )
        self.assertIn(
            "python3 scripts/check_harness_future_work_contracts.py --json > "
            "/tmp/harness-future-work-contracts.json",
            step,
        )
        self.assertIn("### Harness future-work contract preconditions", step)
        self.assertIn("cat /tmp/harness-future-work-contracts.md", step)
        self.assertIn('>> "$GITHUB_STEP_SUMMARY"', step)


if __name__ == "__main__":
    unittest.main()
