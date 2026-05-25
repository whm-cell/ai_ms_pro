from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_harness_sample_followup_coverage as coverage  # noqa: E402


class HarnessSampleFollowupCoverageTest(unittest.TestCase):
    def test_discovery_targets_sample_gap_control_plane(self) -> None:
        paths = set(coverage.discover_paths(ROOT))

        self.assertIn("scripts/check_harness_sample_followup_coverage.py", paths)
        self.assertIn(".github/workflows/governance-and-smoke.yml", paths)
        self.assertIn("scripts/check_harness_collection_config.py", paths)
        self.assertIn("scripts/evidence_ref_utils.py", paths)
        self.assertIn("scripts/check_harness_sample_append.py", paths)
        self.assertIn("scripts/harness_sample_review_context.py", paths)
        self.assertIn("scripts/check_harness_sample_outcome.py", paths)
        self.assertIn("scripts/harness_sample_outcome_context.py", paths)
        self.assertIn("scripts/harness_sample_outcome_validation.py", paths)
        self.assertIn("scripts/harness_burn_in_readiness_cli.py", paths)
        self.assertIn("scripts/harness_burn_in_readiness_deltas.py", paths)
        self.assertIn("scripts/harness_burn_in_readiness_filters.py", paths)
        self.assertIn("scripts/harness_burn_in_readiness_render.py", paths)
        self.assertIn("scripts/harness_burn_in_readiness_routing.py", paths)
        self.assertIn("scripts/harness_burn_in_readiness_types.py", paths)
        self.assertIn("scripts/harness_sample_boundary.py", paths)
        self.assertIn("scripts/harness_sample_capture_gates.py", paths)
        self.assertIn("scripts/harness_sample_collection_items.py", paths)
        self.assertIn("scripts/harness_sample_collection_render.py", paths)
        self.assertIn("scripts/harness_sample_intake_render.py", paths)
        self.assertIn("scripts/harness_sample_priorities.py", paths)
        self.assertIn("scripts/harness_collection_command_coverage.py", paths)
        self.assertIn("scripts/harness_collection_command_templates.py", paths)
        self.assertIn("scripts/harness_collection_lane_commands.py", paths)
        self.assertIn("scripts/harness_sample_followup_coverage_config.py", paths)
        self.assertIn("scripts/harness_pending_readiness_metrics.py", paths)
        self.assertIn("scripts/harness_pending_capture_focus.py", paths)
        self.assertIn("scripts/harness_pending_capture_focus_filters.py", paths)
        self.assertIn("scripts/harness_pending_capture_focus_render.py", paths)
        self.assertIn("scripts/harness_pending_capture_focus_slots.py", paths)
        self.assertIn("scripts/harness_pending_review_cards.py", paths)
        self.assertIn("scripts/check_harness_upgrade_decision_candidate.py", paths)
        self.assertIn("scripts/harness_future_work_contract_context.py", paths)
        self.assertIn("scripts/harness_upgrade_decision_context.py", paths)
        self.assertIn("tests/test_harness_sample_followup_coverage.py", paths)
        self.assertIn("tests/test_harness_collection_config.py", paths)
        self.assertIn("tests/test_harness_sample_append.py", paths)
        self.assertIn("tests/test_harness_sample_outcome.py", paths)
        self.assertIn("docs/ai/standards/harness-future-work-contracts.jsonl", paths)
        self.assertNotIn("tests/test_harness_config.py", paths)

    def test_current_sample_gap_paths_have_required_followup(self) -> None:
        result = coverage.audit(coverage.discover_paths(ROOT))

        self.assertTrue(result.ok, "\n".join(result.errors))
        self.assertEqual(result.missing_followup_paths, ())

    def test_required_commands_include_coverage_checker(self) -> None:
        result = coverage.audit(("scripts/check_harness_sample_followup_coverage.py",))

        self.assertTrue(result.ok, "\n".join(result.errors))
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_followup_coverage.py",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
            "--gap-id GAP-DOES-NOT-EXIST --capture-card",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
            "--ledger-action append-new-pending-slot --capture-card",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
            "--ledger-action fill-existing-placeholder --capture-card",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
            "--ledger-action review-upgrade-decision --capture-card",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
            "--capture-gate requires-approved-remote-interop --capture-card",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
            "--capture-gate requires-approved-bounded-incident --capture-card",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
            "--capture-gate replace-placeholder-after-real-event --capture-card",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
            "--capture-gate requires-security-workflow-event --capture-card",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
            "--capture-gate requires-bounded-real-incident --capture-card",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
            "--capture-gate requires-workflow-task-event --capture-card",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
            "--capture-gate requires-cross-task-resume --capture-card",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
            "--capture-gate requires-distinct-task-class-report --capture-card",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
            "--capture-gate requires-user-confirmed-high-impact-action --capture-card",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
            "--readiness needs-first-real-sample --capture-card",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
            "--readiness needs-more-real-samples --capture-card",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
            "--readiness ready-for-upgrade-discussion --capture-card",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
            "--include-accepted --readiness local-sample-only --capture-card",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
            "--include-future --include-accepted --json",
            coverage.REQUIRED_COMMANDS,
        )
        for area in (
            "agentic-red-team",
            "ai-guardrail",
            "runtime-durability",
            "security-evidence",
            "trace-interop",
            "workflow-skills",
        ):
            self.assertIn(
                ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
                f"--area {area} --capture-card",
                coverage.REQUIRED_COMMANDS,
            )
            self.assertIn(
                ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py "
                f"--area {area}",
                coverage.REQUIRED_COMMANDS,
            )
            self.assertIn(
                ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
                f"--area {area} --summary",
                coverage.REQUIRED_COMMANDS,
            )
            self.assertIn(
                ".codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py "
                f"--include-future --include-accepted --area {area} --json",
                coverage.REQUIRED_COMMANDS,
            )
        for priority in ("P0", "P1", "P2", "P3"):
            self.assertIn(
                ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
                f"--priority {priority} --capture-card",
                coverage.REQUIRED_COMMANDS,
            )
            self.assertIn(
                ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py "
                f"--priority {priority}",
                coverage.REQUIRED_COMMANDS,
            )
            self.assertIn(
                ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
                f"--priority {priority} --summary",
                coverage.REQUIRED_COMMANDS,
            )
            self.assertIn(
                ".codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py "
                f"--include-future --include-accepted --priority {priority} --json",
                coverage.REQUIRED_COMMANDS,
            )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py "
            "--capture-gate requires-approved-remote-interop",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py "
            "--capture-gate requires-approved-bounded-incident",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py "
            "--capture-gate replace-placeholder-after-real-event",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py "
            "--capture-gate requires-security-workflow-event",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py "
            "--capture-gate requires-bounded-real-incident",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py "
            "--capture-gate requires-workflow-task-event",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py "
            "--capture-gate requires-cross-task-resume",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py "
            "--capture-gate requires-distinct-task-class-report",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py "
            "--capture-gate requires-user-confirmed-high-impact-action",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py "
            "--ledger-action append-new-pending-slot",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py "
            "--ledger-action fill-existing-placeholder",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py "
            "--ledger-action review-upgrade-decision",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py "
            "--readiness needs-first-real-sample",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py "
            "--readiness needs-more-real-samples",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py "
            "--readiness ready-for-upgrade-discussion",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_templates.py "
            "--readiness local-sample-only",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
            "--gap-id GAP-DOES-NOT-EXIST --summary",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
            "--capture-gate requires-approved-remote-interop --summary",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
            "--capture-gate requires-approved-bounded-incident --summary",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
            "--capture-gate replace-placeholder-after-real-event --summary",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
            "--capture-gate requires-security-workflow-event --summary",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
            "--capture-gate requires-bounded-real-incident --summary",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
            "--capture-gate requires-workflow-task-event --summary",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
            "--capture-gate requires-cross-task-resume --summary",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
            "--capture-gate requires-distinct-task-class-report --summary",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
            "--capture-gate requires-user-confirmed-high-impact-action --summary",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
            "--readiness needs-first-real-sample --summary",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
            "--readiness needs-more-real-samples --summary",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
            "--readiness ready-for-upgrade-discussion --summary",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
            "--ledger-action append-new-pending-slot --summary",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
            "--ledger-action fill-existing-placeholder --summary",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py --json",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
            "--gap-id GAP-DOES-NOT-EXIST",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py --capture-focus",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
            "--capture-focus --capture-focus-limit 0",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
            "--capture-focus --capture-focus-area agentic-red-team",
            coverage.REQUIRED_COMMANDS,
        )
        for area in (
            "ai-guardrail",
            "runtime-durability",
            "security-evidence",
            "trace-interop",
            "workflow-skills",
        ):
            self.assertIn(
                ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
                f"--capture-focus --capture-focus-area {area}",
                coverage.REQUIRED_COMMANDS,
            )
        for priority in ("P0", "P1"):
            self.assertIn(
                ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
                f"--capture-focus --capture-focus-priority {priority}",
                coverage.REQUIRED_COMMANDS,
            )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
            "--capture-focus --capture-focus-priority P2",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
            "--capture-focus --capture-focus-priority P3",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
            "--capture-focus --capture-focus-ledger-action append-new-pending-slot --capture-focus-limit 0",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
            "--capture-focus --capture-focus-ledger-action fill-existing-placeholder",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
            "--capture-focus --capture-focus-ledger-action fill-existing-placeholder --capture-focus-limit 0",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
            "--capture-focus --capture-focus-gate requires-approved-remote-interop",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
            "--capture-focus --capture-focus-gate requires-approved-bounded-incident",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
            "--capture-focus --capture-focus-gate replace-placeholder-after-real-event",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
            "--capture-focus --capture-focus-gate requires-security-workflow-event",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
            "--capture-focus --capture-focus-gate requires-bounded-real-incident",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
            "--capture-focus --capture-focus-gate requires-workflow-task-event",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
            "--capture-focus --capture-focus-gate requires-cross-task-resume",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
            "--capture-focus --capture-focus-gate requires-distinct-task-class-report",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
            "--capture-focus --capture-focus-gate requires-user-confirmed-high-impact-action",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
            "--capture-focus --capture-focus-readiness needs-first-real-sample",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
            "--capture-focus --capture-focus-readiness needs-more-real-samples",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
            "--review-state review-ready --review-cards",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
            "--include-future --include-accepted --json",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py "
            "--include-future --include-accepted --json",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py "
            "--include-future --include-accepted --area trace-interop --json",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py "
            "--include-future --include-accepted --priority P2 --json",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py "
            "--include-future --include-accepted --gap-id GAP-TRACE-REMOTE-INTEROP --json",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py "
            "--include-future --include-accepted --capture-gate requires-approved-remote-interop --json",
            coverage.REQUIRED_COMMANDS,
        )
        for capture_gate in (
            "requires-approved-bounded-incident",
            "replace-placeholder-after-real-event",
            "requires-security-workflow-event",
            "requires-bounded-real-incident",
            "requires-workflow-task-event",
            "requires-cross-task-resume",
            "requires-distinct-task-class-report",
            "requires-user-confirmed-high-impact-action",
            "upgrade-decision-review",
        ):
            self.assertIn(
                ".codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py "
                f"--include-future --include-accepted --capture-gate {capture_gate} --json",
                coverage.REQUIRED_COMMANDS,
            )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py "
            "--include-future --include-accepted --readiness needs-first-real-sample --json",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py "
            "--include-future --include-accepted --readiness needs-more-real-samples --json",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py "
            "--include-future --include-accepted --readiness ready-for-upgrade-discussion --json",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py "
            "--include-future --include-accepted --readiness local-sample-only --json",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_append.py <candidate-jsonl>",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
            "--ledger-action define-contract-precondition --summary",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
            "--ledger-action review-upgrade-decision --summary",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_upgrade_decisions.py",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh "
            "scripts/check_harness_upgrade_decision_candidate.py <candidate-jsonl>",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_collection_config.py",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn("python3 tests/test_harness_collection_config.py", coverage.REQUIRED_COMMANDS)
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_sample_outcome.py <candidate-jsonl>",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn(
            ".codex/hooks/run_with_repo_python.sh "
            "scripts/check_harness_future_work_contract_candidate.py <candidate-jsonl>",
            coverage.REQUIRED_COMMANDS,
        )
        self.assertIn("python3 tests/test_harness_sample_append.py", coverage.REQUIRED_COMMANDS)
        self.assertIn("python3 tests/test_harness_sample_outcome.py", coverage.REQUIRED_COMMANDS)
        self.assertIn("python3 tests/test_harness_future_work_contract_candidate.py", coverage.REQUIRED_COMMANDS)
        self.assertIn("python3 tests/test_harness_upgrade_decision_candidate.py", coverage.REQUIRED_COMMANDS)
        self.assertIn("python3 tests/test_harness_sample_followup_coverage.py", coverage.REQUIRED_COMMANDS)
        self.assertIn("python3 tests/test_governance_workflow_sample_outputs.py", coverage.REQUIRED_COMMANDS)
        for command in (
            "python3 tests/test_harness_sample_gap_evidence.py",
            "python3 tests/test_harness_sample_gaps.py",
            "python3 tests/test_plan_harness_sample_collection.py",
            "python3 tests/test_harness_sample_templates.py",
            ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py",
            "python3 tests/test_harness_sample_intake_bundle.py",
            "python3 tests/test_harness_placeholder_replacement.py",
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py",
            "python3 tests/test_harness_burn_in_readiness.py",
            "python3 tests/test_harness_pending_samples.py",
            "python3 tests/test_harness_future_work_contracts.py",
        ):
            self.assertIn(command, coverage.REQUIRED_COMMANDS)

    def test_required_commands_cover_full_routed_command_package(self) -> None:
        missing = tuple(
            command
            for command in coverage.HARNESS_SAMPLE_GAP_COMMANDS
            if command not in coverage.REQUIRED_COMMANDS
        )

        self.assertEqual((), missing)

    def test_explicit_unrelated_path_reports_missing_followup(self) -> None:
        result = coverage.audit(("README.md",))

        self.assertFalse(result.ok)
        self.assertEqual(result.missing_followup_paths, ("README.md",))
        self.assertIn("README.md: missing harness-sample-gap-evidence follow-up", result.errors)

    def test_json_payload_exposes_counts_and_errors(self) -> None:
        result = coverage.audit(("README.md",))
        payload = coverage.to_payload(result)

        self.assertEqual(payload["checked_path_count"], 1)
        self.assertEqual(payload["required_followup"], "harness-sample-gap-evidence")
        self.assertEqual(payload["missing_followup_paths"], ("README.md",))
        self.assertEqual(payload["unrequired_routed_commands"], ())
        self.assertIn("errors", payload)


if __name__ == "__main__":
    unittest.main()
