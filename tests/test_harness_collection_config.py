from __future__ import annotations

import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_harness_collection_config as collection_config  # noqa: E402


class HarnessCollectionConfigTest(unittest.TestCase):
    def test_repository_collection_config_is_valid(self) -> None:
        report = collection_config.audit()

        self.assertTrue(report.ok, "\n".join(report.errors))
        self.assertEqual(report.gap_count, 20)
        self.assertEqual(report.future_gap_count, 2)
        self.assertGreaterEqual(report.configured_target_count, 4)
        self.assertGreaterEqual(report.active_capture_gate_count, 9)
        self.assertGreaterEqual(report.real_sample_capture_gate_count, 8)
        self.assertEqual(report.real_sample_area_count, 6)
        self.assertEqual(report.real_sample_priority_count, 3)
        self.assertEqual(report.real_sample_ledger_action_count, 2)
        self.assertEqual(report.real_sample_readiness_count, 2)
        self.assertFalse(
            any("GAP-AGENTIC-CASCADE-STOP" in error for error in report.errors),
            "\n".join(report.errors),
        )

    def test_unknown_dedicated_target_gap_is_reported(self) -> None:
        targets = dict(collection_config.config.DEDICATED_TARGETS)
        targets["GAP-UNKNOWN"] = "docs/ai/standards/harness-sample-gap-evidence.jsonl"

        with patch.object(collection_config.config, "DEDICATED_TARGETS", targets):
            report = collection_config.audit()

        self.assertFalse(report.ok)
        self.assertIn("DEDICATED_TARGETS: unknown gap id: GAP-UNKNOWN", report.errors)

    def test_invalid_priority_value_is_reported(self) -> None:
        priorities = dict(collection_config.config.PRIORITIES)
        priorities["GAP-GUARDRAIL-PREFLIGHT-WARNING"] = "P9"

        with patch.object(collection_config.config, "PRIORITIES", priorities):
            report = collection_config.audit()

        self.assertFalse(report.ok)
        self.assertIn("PRIORITIES: invalid priority value: P9", report.errors)

    def test_future_work_gap_requires_explicit_trigger(self) -> None:
        triggers = dict(collection_config.config.TRIGGERS)
        triggers.pop("GAP-TRACE-REMOTE-INTEROP")

        with patch.object(collection_config.config, "TRIGGERS", triggers):
            report = collection_config.audit()

        self.assertFalse(report.ok)
        self.assertIn(
            "TRIGGERS: approved future-work gap needs explicit sample trigger: GAP-TRACE-REMOTE-INTEROP",
            report.errors,
        )

    def test_unapproved_future_work_gap_cannot_use_dedicated_target(self) -> None:
        targets = dict(collection_config.config.DEDICATED_TARGETS)
        targets["GAP-TRACE-REMOTE-INTEROP"] = "docs/ai/standards/harness-sample-gap-evidence.jsonl"
        report_state = SimpleNamespace(
            contract_states=(
                SimpleNamespace(
                    gap_id="GAP-AGENTIC-CASCADE-STOP",
                    contract_id="FWC-GAP-AGENTIC-CASCADE-STOP",
                    status="approved-for-sampling",
                    contract_kind="bounded-local-incident",
                    sample_collection_allowed=True,
                    adr_required=True,
                    adr_refs=["docs/ai/adr/ADR-016-agentic-cascade-stop-boundary.md"],
                    missing_adr_refs=(),
                    required_decision_fields=[],
                    next_action="Capture a bounded local incident.",
                    review_command="review",
                    sample_collection_boundary="Allowed by contract record.",
                    evidence_refs=[],
                ),
                SimpleNamespace(
                    gap_id="GAP-TRACE-REMOTE-INTEROP",
                    contract_id="FWC-GAP-TRACE-REMOTE-INTEROP",
                    status="needs-contract-or-adr-first",
                    contract_kind="remote-interop",
                    sample_collection_allowed=False,
                    adr_required=True,
                    adr_refs=[],
                    missing_adr_refs=("docs/ai/adr/ADR-017-trace-remote-interop-boundary.md",),
                    required_decision_fields=[],
                    next_action="Define remote interop contract first.",
                    review_command="review",
                    sample_collection_boundary="Remote interop sample collection remains blocked.",
                    evidence_refs=[],
                ),
            )
        )

        with (
            patch.object(collection_config.config, "DEDICATED_TARGETS", targets),
            patch.object(collection_config.future_contracts, "build_report", return_value=report_state),
        ):
            report = collection_config.audit()

        self.assertFalse(report.ok)
        self.assertIn(
            "DEDICATED_TARGETS: future-work gap must use future contract target "
            "until sample collection is approved: GAP-TRACE-REMOTE-INTEROP",
            report.errors,
        )

    def test_missing_review_command_is_reported(self) -> None:
        with patch.object(collection_config.review_commands, "REVIEW_COMMANDS_BY_LEDGER", {}):
            report = collection_config.audit()

        self.assertFalse(report.ok)
        self.assertTrue(any(error.startswith("review command missing for target:") for error in report.errors))

    def test_active_capture_gate_missing_from_choices_is_reported(self) -> None:
        capture_gates = tuple(
            gate
            for gate in collection_config.config.CAPTURE_GATES
            if gate != "requires-approved-remote-interop"
        )

        with patch.object(collection_config.config, "CAPTURE_GATES", capture_gates):
            report = collection_config.audit()

        self.assertFalse(report.ok)
        self.assertIn(
            "CAPTURE_GATES: active capture gate missing from choices: requires-approved-remote-interop",
            report.errors,
        )

    def test_real_sample_capture_gate_requires_focused_command_package(self) -> None:
        missing_command = (
            ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
            "--capture-gate requires-approved-remote-interop --capture-card"
        )
        commands = tuple(
            command
            for command in collection_config.HARNESS_SAMPLE_GAP_COMMANDS
            if command != missing_command
        )

        with patch.object(collection_config, "HARNESS_SAMPLE_GAP_COMMANDS", commands):
            report = collection_config.audit()

        self.assertFalse(report.ok)
        self.assertIn(
            "HARNESS_SAMPLE_GAP_COMMANDS: missing focused capture-gate command: "
            f"requires-approved-remote-interop -> {missing_command}",
            report.errors,
        )

    def test_real_sample_ledger_action_requires_focused_command_package(self) -> None:
        missing_command = (
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
            "--capture-focus --capture-focus-ledger-action append-new-pending-slot --capture-focus-limit 0"
        )
        commands = tuple(
            command
            for command in collection_config.HARNESS_SAMPLE_GAP_COMMANDS
            if command != missing_command
        )

        with patch.object(collection_config, "HARNESS_SAMPLE_GAP_COMMANDS", commands):
            report = collection_config.audit()

        self.assertFalse(report.ok)
        self.assertIn(
            "HARNESS_SAMPLE_GAP_COMMANDS: missing focused ledger-action command: "
            f"append-new-pending-slot -> {missing_command}",
            report.errors,
        )

    def test_real_sample_readiness_requires_focused_command_package(self) -> None:
        missing_command = (
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py "
            "--include-future --include-accepted --readiness needs-first-real-sample --json"
        )
        commands = tuple(
            command
            for command in collection_config.HARNESS_SAMPLE_GAP_COMMANDS
            if command != missing_command
        )

        with patch.object(collection_config, "HARNESS_SAMPLE_GAP_COMMANDS", commands):
            report = collection_config.audit()

        self.assertFalse(report.ok)
        self.assertIn(
            "HARNESS_SAMPLE_GAP_COMMANDS: missing focused readiness command: "
            f"needs-first-real-sample -> {missing_command}",
            report.errors,
        )

    def test_real_sample_area_requires_focused_command_package(self) -> None:
        missing_command = (
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
            "--capture-focus --capture-focus-area trace-interop"
        )
        commands = tuple(
            command
            for command in collection_config.HARNESS_SAMPLE_GAP_COMMANDS
            if command != missing_command
        )

        with patch.object(collection_config, "HARNESS_SAMPLE_GAP_COMMANDS", commands):
            report = collection_config.audit()

        self.assertFalse(report.ok)
        self.assertIn(
            "HARNESS_SAMPLE_GAP_COMMANDS: missing focused area command: "
            f"trace-interop -> {missing_command}",
            report.errors,
        )

    def test_real_sample_area_requires_readiness_command_package(self) -> None:
        missing_command = (
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py "
            "--include-future --include-accepted --area trace-interop --json"
        )
        commands = tuple(
            command
            for command in collection_config.HARNESS_SAMPLE_GAP_COMMANDS
            if command != missing_command
        )

        with patch.object(collection_config, "HARNESS_SAMPLE_GAP_COMMANDS", commands):
            report = collection_config.audit()

        self.assertFalse(report.ok)
        self.assertIn(
            "HARNESS_SAMPLE_GAP_COMMANDS: missing focused area command: "
            f"trace-interop -> {missing_command}",
            report.errors,
        )

    def test_real_sample_area_requires_planner_template_and_intake_commands(self) -> None:
        missing_command = (
            ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
            "--area trace-interop --summary"
        )
        commands = tuple(
            command
            for command in collection_config.HARNESS_SAMPLE_GAP_COMMANDS
            if command != missing_command
        )

        with patch.object(collection_config, "HARNESS_SAMPLE_GAP_COMMANDS", commands):
            report = collection_config.audit()

        self.assertFalse(report.ok)
        self.assertIn(
            "HARNESS_SAMPLE_GAP_COMMANDS: missing focused area command: "
            f"trace-interop -> {missing_command}",
            report.errors,
        )

    def test_real_sample_priority_requires_focused_command_package(self) -> None:
        missing_command = (
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_pending_samples.py "
            "--capture-focus --capture-focus-priority P3"
        )
        commands = tuple(
            command
            for command in collection_config.HARNESS_SAMPLE_GAP_COMMANDS
            if command != missing_command
        )

        with patch.object(collection_config, "HARNESS_SAMPLE_GAP_COMMANDS", commands):
            report = collection_config.audit()

        self.assertFalse(report.ok)
        self.assertIn(
            "HARNESS_SAMPLE_GAP_COMMANDS: missing focused priority command: "
            f"P3 -> {missing_command}",
            report.errors,
        )

    def test_real_sample_priority_requires_readiness_command_package(self) -> None:
        missing_command = (
            ".codex/hooks/run_with_repo_python.sh scripts/check_harness_burn_in_readiness.py "
            "--include-future --include-accepted --priority P3 --json"
        )
        commands = tuple(
            command
            for command in collection_config.HARNESS_SAMPLE_GAP_COMMANDS
            if command != missing_command
        )

        with patch.object(collection_config, "HARNESS_SAMPLE_GAP_COMMANDS", commands):
            report = collection_config.audit()

        self.assertFalse(report.ok)
        self.assertIn(
            "HARNESS_SAMPLE_GAP_COMMANDS: missing focused priority command: "
            f"P3 -> {missing_command}",
            report.errors,
        )

    def test_real_sample_priority_requires_planner_template_and_intake_commands(self) -> None:
        missing_command = (
            ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
            "--priority P3 --capture-card"
        )
        commands = tuple(
            command
            for command in collection_config.HARNESS_SAMPLE_GAP_COMMANDS
            if command != missing_command
        )

        with patch.object(collection_config, "HARNESS_SAMPLE_GAP_COMMANDS", commands):
            report = collection_config.audit()

        self.assertFalse(report.ok)
        self.assertIn(
            "HARNESS_SAMPLE_GAP_COMMANDS: missing focused priority command: "
            f"P3 -> {missing_command}",
            report.errors,
        )

    def test_real_sample_area_requires_capture_focus_choice(self) -> None:
        areas = tuple(
            area
            for area in collection_config.command_coverage.capture_focus.CAPTURE_FOCUS_AREAS
            if area != "trace-interop"
        )

        with patch.object(collection_config.command_coverage.capture_focus, "CAPTURE_FOCUS_AREAS", areas):
            report = collection_config.audit()

        self.assertFalse(report.ok)
        self.assertIn(
            "CAPTURE_FOCUS_AREAS: active real-sample area missing from choices: trace-interop",
            report.errors,
        )

    def test_real_sample_priority_requires_capture_focus_choice(self) -> None:
        priorities = tuple(
            priority
            for priority in collection_config.command_coverage.capture_focus.CAPTURE_FOCUS_PRIORITIES
            if priority != "P3"
        )

        with patch.object(collection_config.command_coverage.capture_focus, "CAPTURE_FOCUS_PRIORITIES", priorities):
            report = collection_config.audit()

        self.assertFalse(report.ok)
        self.assertIn(
            "CAPTURE_FOCUS_PRIORITIES: active real-sample priority missing from choices: P3",
            report.errors,
        )

    def test_real_sample_ledger_action_requires_capture_focus_choice(self) -> None:
        ledger_actions = tuple(
            action
            for action in collection_config.command_coverage.capture_focus.CAPTURE_FOCUS_LEDGER_ACTIONS
            if action != "append-new-pending-slot"
        )

        with patch.object(
            collection_config.command_coverage.capture_focus,
            "CAPTURE_FOCUS_LEDGER_ACTIONS",
            ledger_actions,
        ):
            report = collection_config.audit()

        self.assertFalse(report.ok)
        self.assertIn(
            "CAPTURE_FOCUS_LEDGER_ACTIONS: active real-sample ledger action missing from choices: "
            "append-new-pending-slot",
            report.errors,
        )

    def test_text_output_lists_no_errors_for_current_repo(self) -> None:
        output = io.StringIO()

        with redirect_stdout(output):
            collection_config.emit_text(collection_config.audit())

        text = output.getvalue()
        self.assertIn("Harness collection config audit:", text)
        self.assertIn("- active capture gates:", text)
        self.assertIn("- real-sample capture gates:", text)
        self.assertIn("- real-sample areas:", text)
        self.assertIn("- real-sample priorities:", text)
        self.assertIn("- real-sample ledger actions:", text)
        self.assertIn("- real-sample readiness states:", text)
        self.assertIn("ERRORS: none", text)


if __name__ == "__main__":
    unittest.main()
