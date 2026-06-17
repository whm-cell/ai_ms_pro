from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_tool_contracts  # noqa: E402


def valid_contract(**overrides: object) -> dict[str, object]:
    contract: dict[str, object] = {
        "name": "demo_tool",
        "purpose": "Demonstrate a valid tool contract.",
        "path": "scripts/check_tool_contracts.py",
        "command": "python3 scripts/check_tool_contracts.py",
        "inputs": ["registry JSON"],
        "outputs": ["stdout report", "process exit code"],
        "side_effects": ["read_repo"],
        "permissions": ["read-repo"],
        "timeout_seconds": 30,
        "destructive": False,
        "externally_visible": False,
        "automation_mode": "assistive",
        "verification_commands": ["python3 scripts/check_tool_contracts.py"],
    }
    contract.update(overrides)
    return contract


def registry(*contracts: dict[str, object]) -> dict[str, object]:
    return {"schema_version": 1, "contracts": list(contracts)}


class ToolContractValidationTest(unittest.TestCase):
    def errors_for(self, *contracts: dict[str, object]) -> list[str]:
        return check_tool_contracts.validate_registry(registry(*contracts), root=ROOT).errors

    def test_repository_registry_is_valid(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        result = check_tool_contracts.validate_registry(data, root=ROOT)
        self.assertEqual(result.errors, [])

    def test_stop_runtime_observation_contract_is_local_trace_writer(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "stop_runtime_observation")

        self.assertIn("write_runtime", contract["side_effects"])
        self.assertIn("write-runtime", contract["permissions"])
        self.assertIn(".agent-trace.jsonl", "\n".join(contract["outputs"]))
        self.assertFalse(contract["destructive"])
        self.assertFalse(contract["externally_visible"])
        self.assertIn("scripts/check_agent_trace_schema.py", "\n".join(contract["verification_commands"]))

    def test_otlp_pilot_contract_defaults_to_no_network_export(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "export_agent_trace_otlp_pilot")

        self.assertIn("--format otlp-http-json", contract["command"])
        self.assertEqual(contract["side_effects"], ["read_repo"])
        self.assertFalse(contract["externally_visible"])
        self.assertIn("--send", contract["dangerous_flags"])
        self.assertIn("network_exported evidence flag", "\n".join(contract["outputs"]))
        self.assertEqual(contract["transport"], "otlp-http-json")
        self.assertEqual(contract["local_vs_remote"], "local-pilot-to-remote-ready")

    def test_runtime_execution_snapshot_contract_is_local_checkpoint_only(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "check_runtime_execution_snapshots")

        self.assertEqual(contract["side_effects"], ["read_repo", "read_runtime"])
        self.assertEqual(contract["local_vs_remote"], "local-only")
        self.assertIn(".codex/runtime/execution-snapshots/*.json", contract["inputs"])

    def test_remote_trace_interop_contract_stays_pilot_by_default(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "verify_remote_trace_interop")

        self.assertEqual(contract["transport"], "otlp-http-json")
        self.assertEqual(contract["local_vs_remote"], "bounded-remote-interop")
        self.assertIn("--verified-remote", contract["dangerous_flags"])
        self.assertIn("does not auto-upgrade pilot-remote", contract["notes"])
        self.assertIn("loopback", contract["notes"])

    def test_ci_agent_contract_is_advisory_pr_only(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "check_ci_agent_contract")

        self.assertEqual(contract["side_effects"], ["read_repo"])
        self.assertEqual(contract["automation_mode"], "ci")
        self.assertFalse(contract["destructive"])
        self.assertFalse(contract["externally_visible"])
        self.assertEqual(contract["local_vs_remote"], "local-only")
        self.assertIn("docs/ai/standards/ci-agent-contract.sample.jsonl", contract["inputs"])
        self.assertIn("referenced tool contract list", "\n".join(contract["outputs"]))
        self.assertIn("tests/test_ci_agent_contract.py", "\n".join(contract["verification_commands"]))
        self.assertIn("pull_request-only", contract["notes"])
        self.assertIn("pull_request_target", contract["notes"])
        self.assertIn("does not create or prove any CI agent workflow", contract["notes"])

    def test_external_harness_decisions_contract_is_no_effect_audit(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "check_external_harness_decisions")

        self.assertEqual(contract["side_effects"], ["read_repo"])
        self.assertEqual(contract["automation_mode"], "ci")
        self.assertFalse(contract["destructive"])
        self.assertFalse(contract["externally_visible"])
        self.assertEqual(contract["local_vs_remote"], "local-only")
        self.assertIn("docs/ai/standards/external-harness-decisions.jsonl", contract["inputs"])
        self.assertIn("active decision area list", "\n".join(contract["outputs"]))
        self.assertIn("tests/test_external_harness_decisions.py", "\n".join(contract["verification_commands"]))
        self.assertIn("hosted trace/eval", contract["notes"])
        self.assertIn("verified remote without operator review", contract["notes"])
        self.assertIn("native sandbox", contract["notes"])
        self.assertIn("MCP/A2A runtime", contract["notes"])
        self.assertIn("real CI agent workflow", contract["notes"])
        self.assertIn("does not send network probes", contract["notes"])

    def test_local_execution_policy_wrapper_contract_is_not_native_sandbox(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "run_sandboxed_command")

        self.assertEqual(contract["side_effects"], ["read_repo", "write_runtime"])
        self.assertEqual(contract["automation_mode"], "assistive")
        self.assertFalse(contract["destructive"])
        self.assertFalse(contract["externally_visible"])
        self.assertIn("scripts/run_sandboxed_command.py -- python3 --version", contract["command"])
        self.assertIn("write-runtime", contract["permissions"])
        self.assertIn("execute-local-command", contract["permissions"])
        self.assertIn(".codex/runtime/tool-outputs/*.meta.json", contract["outputs"])
        self.assertIn("tests.test_execution_sandbox_wrapper", "\n".join(contract["verification_commands"]))
        self.assertIn("not a native OS sandbox", contract["sandbox_requirement"])
        self.assertIn("native_sandbox=false", contract["notes"])
        self.assertIn("not proof", contract["notes"])

    def test_runtime_trace_summary_contract_is_local_read_only(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "summarize_runtime_traces")

        self.assertEqual(contract["side_effects"], ["read_runtime"])
        self.assertEqual(contract["permissions"], ["read-runtime"])
        self.assertEqual(contract["automation_mode"], "ci")
        self.assertFalse(contract["destructive"])
        self.assertFalse(contract["externally_visible"])
        self.assertIn("tests/test_summarize_runtime_traces.py", "\n".join(contract["verification_commands"]))

    def test_loop_triage_contract_is_no_write_assistive_summary(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "summarize_loop_triage")

        self.assertEqual(contract["side_effects"], ["read_repo", "read_runtime"])
        self.assertEqual(contract["automation_mode"], "assistive")
        self.assertFalse(contract["destructive"])
        self.assertFalse(contract["externally_visible"])
        self.assertIn("operator-reviewed next-action candidates", contract["outputs"])
        self.assertIn("tests/test_summarize_loop_triage.py", "\n".join(contract["verification_commands"]))
        self.assertIn("bounded loop layer", contract["notes"])
        self.assertIn("does not write ledgers", contract["notes"])
        self.assertIn("does not", contract["notes"])

    def test_mock_data_boundary_contract_is_review_required_no_write(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "check_mock_data_boundary")

        self.assertEqual(contract["side_effects"], ["read_repo"])
        self.assertEqual(contract["automation_mode"], "assistive")
        self.assertFalse(contract["destructive"])
        self.assertFalse(contract["externally_visible"])
        self.assertIn(".codex/harness.toml", contract["inputs"])
        self.assertIn("mock data scenario manifests", contract["inputs"])
        self.assertIn("suggested_layer", "\n".join(contract["outputs"]))
        self.assertIn("--strict", contract["dangerous_flags"])
        self.assertIn("tests/test_mock_data_boundary.py", "\n".join(contract["verification_commands"]))
        self.assertIn("review-required", contract["notes"])
        self.assertIn("mock-data-scenario/v1", contract["notes"])
        self.assertIn("unseeded fixture factories", contract["notes"])
        self.assertIn("does not install MSW/Prism/Playwright", contract["notes"])
        self.assertIn("does not auto-delete old code", contract["notes"])

    def test_data_activation_contract_is_review_required_no_write(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "check_data_activation")

        self.assertEqual(contract["side_effects"], ["read_repo"])
        self.assertEqual(contract["automation_mode"], "assistive")
        self.assertFalse(contract["destructive"])
        self.assertFalse(contract["externally_visible"])
        self.assertIn(".codex/harness.toml", contract["inputs"])
        self.assertIn("mock data scenario manifests", contract["inputs"])
        self.assertIn("bounded evidence refs", contract["inputs"])
        self.assertIn("--strict", contract["dangerous_flags"])
        self.assertIn("tests/test_data_activation.py", "\n".join(contract["verification_commands"]))
        self.assertIn("review-required", contract["notes"])
        self.assertIn("shadow-real", contract["notes"])
        self.assertIn("real_adapter_path", contract["notes"])
        self.assertIn("does not migrate data", contract["notes"])

    def test_burn_in_ledger_contract_is_shape_only(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "check_burn_in_ledger")

        self.assertEqual(contract["side_effects"], ["read_repo"])
        self.assertEqual(contract["automation_mode"], "ci")
        self.assertFalse(contract["destructive"])
        self.assertFalse(contract["externally_visible"])
        self.assertIn("docs/ai/check-burn-in-ledger.md", contract["inputs"])
        self.assertIn("remaining sample slots", "\n".join(contract["outputs"]))
        self.assertIn("checks needing samples", "\n".join(contract["outputs"]))
        self.assertIn("upgrade-eligible checks", "\n".join(contract["outputs"]))
        self.assertIn("upgrade_review_needed_checks", "\n".join(contract["outputs"]))
        self.assertIn("accepted_samples", "\n".join(contract["outputs"]))
        self.assertIn("evidence_refs", "\n".join(contract["outputs"]))
        self.assertIn("upgrade_review_needed", "\n".join(contract["outputs"]))
        self.assertIn("next_evidence", "\n".join(contract["outputs"]))
        self.assertIn("--json", "\n".join(contract["verification_commands"]))
        self.assertIn("tests/test_governance_workflow_sample_outputs.py", "\n".join(contract["verification_commands"]))
        self.assertIn("tests/test_check_burn_in_ledger.py", "\n".join(contract["verification_commands"]))
        self.assertIn("GitHub step summary", contract["notes"])
        self.assertIn("decision_counts", contract["notes"])
        self.assertIn("total_remaining_samples", contract["notes"])
        self.assertIn("checks_needing_samples", contract["notes"])
        self.assertIn("upgrade_eligible_checks", contract["notes"])
        self.assertIn("upgrade_review_needed_checks", contract["notes"])
        self.assertIn("evidence_refs", contract["notes"])
        self.assertIn("existing repo-relative", contract["notes"])
        self.assertIn("markdown anchors, pytest node ids, and JSONL line selectors", contract["notes"])
        self.assertIn("2/2 keep-candidate", contract["notes"])
        self.assertIn("only means the sample target is met", contract["notes"])
        self.assertIn("blocking-candidate calibration", contract["notes"])
        self.assertIn("does not generate samples", contract["notes"])

    def test_burn_in_upgrade_decisions_contract_is_no_write_review(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "check_burn_in_upgrade_decisions")

        self.assertEqual(contract["side_effects"], ["read_repo"])
        self.assertEqual(contract["automation_mode"], "ci")
        self.assertFalse(contract["destructive"])
        self.assertFalse(contract["externally_visible"])
        self.assertIn("docs/ai/standards/check-burn-in-upgrade-decisions.jsonl", contract["inputs"])
        self.assertIn("upgrade_review_needed_checks", "\n".join(contract["outputs"]))
        self.assertIn("missing and extra upgrade decision checks", "\n".join(contract["outputs"]))
        self.assertIn("--json", "\n".join(contract["verification_commands"]))
        self.assertIn("tests/test_burn_in_upgrade_decisions.py", "\n".join(contract["verification_commands"]))
        self.assertIn("tests/test_governance_workflow_sample_outputs.py", "\n".join(contract["verification_commands"]))
        self.assertIn("tests/test_change_triggered_followups.py", "\n".join(contract["verification_commands"]))
        self.assertIn("no-write decision audit", contract["notes"])
        self.assertIn("GitHub step summary", contract["notes"])
        self.assertIn("upgrade_review_needed_checks", contract["notes"])
        self.assertIn("stale accepted_samples", contract["notes"])
        self.assertIn("existing repo-relative paths", contract["notes"])
        self.assertIn("markdown anchors, pytest node ids, and JSONL line selectors", contract["notes"])
        self.assertIn("forbids local runtime references", contract["notes"])
        self.assertIn("does not change check levels", contract["notes"])

    def test_generic_gap_evidence_contract_is_local_advisory(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "check_harness_sample_gap_evidence")

        self.assertEqual(contract["side_effects"], ["read_repo"])
        self.assertFalse(contract["destructive"])
        self.assertFalse(contract["externally_visible"])
        self.assertIn("docs/ai/standards/harness-sample-gap-evidence.jsonl", contract["inputs"])
        self.assertIn("remote interop boundary findings", contract["outputs"])
        self.assertIn("tests/test_harness_sample_gap_evidence.py", "\n".join(contract["verification_commands"]))
        self.assertIn("source_type real-interop-run", contract["notes"])
        self.assertIn("evidence_refs", contract["notes"])
        self.assertIn("existing repo-relative paths", contract["notes"])
        self.assertIn("path selectors", contract["notes"])
        self.assertIn("does not prove hosted collector", contract["notes"])

    def test_sample_followup_coverage_contract_is_drift_audit_only(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "check_harness_sample_followup_coverage")

        self.assertEqual(contract["side_effects"], ["read_repo"])
        self.assertEqual(contract["permissions"], ["read-repo"])
        self.assertEqual(contract["automation_mode"], "ci")
        self.assertFalse(contract["destructive"])
        self.assertFalse(contract["externally_visible"])
        self.assertIn("scripts/change_triggered_harness_sample_rules.py", contract["inputs"])
        self.assertIn("scripts/harness_sample_followup_coverage_config.py", "\n".join(contract["inputs"]))
        self.assertIn(".github/workflows/governance-and-smoke.yml", contract["inputs"])
        self.assertIn("template record helpers", "\n".join(contract["inputs"]))
        self.assertIn("readiness routing helpers including scripts/harness_burn_in_readiness_routing.py", contract["inputs"])
        self.assertIn("missing follow-up paths", contract["outputs"])
        self.assertIn("missing required command routes", contract["outputs"])
        self.assertIn("routed commands missing from required coverage", contract["outputs"])
        self.assertIn("--json", "\n".join(contract["verification_commands"]))
        self.assertIn("tests/test_harness_sample_followup_coverage.py", "\n".join(contract["verification_commands"]))
        self.assertIn("advisory drift audit", contract["notes"])
        self.assertIn("REQUIRED_COMMANDS exactly covers the routed HARNESS_SAMPLE_GAP_COMMANDS", contract["notes"])
        self.assertIn("empty-scope regression", contract["notes"])
        self.assertIn("unfiltered intake/readiness baselines", contract["notes"])
        self.assertIn("intake JSON output", contract["notes"])
        self.assertIn("future/local-inclusive state", contract["notes"])
        self.assertIn("local-sample-only template skip", contract["notes"])
        self.assertIn("readiness next-collection routing commands", contract["notes"])
        self.assertIn("workflow-output test command", contract["notes"])
        self.assertIn(
            "active area / active priority planner-template-intake-readiness-pending focus commands",
            contract["notes"],
        )
        self.assertIn("GitHub step summary", contract["notes"])
        self.assertIn("does not execute those commands", contract["notes"])
        self.assertIn("create evidence", contract["notes"])

    def test_warning_sample_code_alignment_contract_is_drift_audit_only(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "check_warning_sample_code_alignment")

        self.assertEqual(contract["side_effects"], ["read_repo"])
        self.assertEqual(contract["permissions"], ["read-repo"])
        self.assertEqual(contract["automation_mode"], "ci")
        self.assertFalse(contract["destructive"])
        self.assertFalse(contract["externally_visible"])
        self.assertIn(".codex/hooks/pre_tool_use_preflight.py", contract["inputs"])
        self.assertIn(".codex/hooks/stop_loop_scope_monitor.py", contract["inputs"])
        self.assertIn("scripts/check_pre_tool_use_preflight_samples.py", contract["inputs"])
        self.assertIn("scripts/check_loop_scope_monitor_samples.py", contract["inputs"])
        self.assertIn("emitted hook finding codes", contract["outputs"])
        self.assertIn("Stop recommendation mapping coverage", contract["outputs"])
        self.assertIn("--json", "\n".join(contract["verification_commands"]))
        self.assertIn("tests/test_warning_sample_code_alignment.py", "\n".join(contract["verification_commands"]))
        self.assertIn("advisory drift check", contract["notes"])
        self.assertIn("does not collect evidence", contract["notes"])
        self.assertIn("accept pending samples", contract["notes"])

    def test_harness_collection_config_contract_is_routing_drift_only(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "check_harness_collection_config")

        self.assertEqual(contract["side_effects"], ["read_repo"])
        self.assertEqual(contract["permissions"], ["read-repo"])
        self.assertEqual(contract["automation_mode"], "ci")
        self.assertFalse(contract["destructive"])
        self.assertFalse(contract["externally_visible"])
        self.assertIn("scripts/collect_harness_sample_gaps.py", "\n".join(contract["inputs"]))
        self.assertIn("scripts/harness_sample_collection_config.py", "\n".join(contract["inputs"]))
        self.assertIn("scripts/harness_sample_review_commands.py", "\n".join(contract["inputs"]))
        self.assertIn("scripts/check_harness_burn_in_readiness.py", "\n".join(contract["inputs"]))
        self.assertIn("scripts/change_triggered_harness_sample_rules.py", "\n".join(contract["inputs"]))
        self.assertIn("scripts/harness_collection_command_coverage.py", "\n".join(contract["inputs"]))
        self.assertIn("scripts/harness_collection_command_templates.py", "\n".join(contract["inputs"]))
        self.assertIn("unknown gap id errors", contract["outputs"])
        self.assertIn("missing review command errors", contract["outputs"])
        self.assertIn("active capture gate choice errors", contract["outputs"])
        self.assertIn("missing focused area command errors", contract["outputs"])
        self.assertIn("missing focused priority command errors", contract["outputs"])
        self.assertIn("missing focused capture-gate command errors", contract["outputs"])
        self.assertIn("missing focused ledger-action command errors", contract["outputs"])
        self.assertIn("missing focused readiness command errors", contract["outputs"])
        self.assertIn("--json", "\n".join(contract["verification_commands"]))
        self.assertIn("tests/test_harness_collection_config.py", "\n".join(contract["verification_commands"]))
        self.assertIn("advisory routing drift check", contract["notes"])
        self.assertIn("active capture-gate choice", contract["notes"])
        self.assertIn("focused area command drift", contract["notes"])
        self.assertIn("focused priority command drift", contract["notes"])
        self.assertIn("focused capture-gate command drift", contract["notes"])
        self.assertIn("focused ledger-action command drift", contract["notes"])
        self.assertIn("focused readiness command drift", contract["notes"])
        self.assertIn("planner, template, intake, readiness, and pending-focus focused commands", contract["notes"])
        self.assertIn("HARNESS_SAMPLE_GAP_COMMANDS", contract["notes"])
        self.assertIn("without collecting samples", contract["notes"])
        self.assertIn("accepting evidence", contract["notes"])

    def test_sample_gap_collector_contract_is_report_only(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "collect_harness_sample_gaps")

        self.assertEqual(contract["side_effects"], ["none"])
        self.assertEqual(contract["automation_mode"], "ci")
        self.assertFalse(contract["destructive"])
        self.assertFalse(contract["externally_visible"])
        self.assertIn("--json", "\n".join(contract["verification_commands"]))
        self.assertIn("tests/test_governance_workflow_sample_outputs.py", "\n".join(contract["verification_commands"]))
        self.assertIn("GitHub step summary", contract["notes"])
        self.assertIn("does not create evidence", contract["notes"])

    def test_sample_collection_plan_contract_is_planning_only(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "plan_harness_sample_collection")

        self.assertEqual(contract["side_effects"], ["read_repo"])
        self.assertEqual(contract["permissions"], ["read-repo"])
        self.assertFalse(contract["destructive"])
        self.assertFalse(contract["externally_visible"])
        self.assertIn("readiness accounting from scripts/check_harness_burn_in_readiness.py", contract["inputs"])
        self.assertIn("collection routing constants from scripts/harness_sample_collection_config.py", contract["inputs"])
        self.assertIn("collection item routing helpers from scripts/harness_sample_collection_items.py", contract["inputs"])
        self.assertIn("future-work contract state from scripts/check_harness_future_work_contracts.py", contract["inputs"])
        self.assertIn("pending sample slot inventory from scripts/harness_sample_slots.py", contract["inputs"])
        self.assertIn("pending sample summary helper from scripts/harness_sample_pending_summaries.py", contract["inputs"])
        self.assertIn("sample review command routing from scripts/harness_sample_review_commands.py", contract["inputs"])
        self.assertIn("collection lane command routing from scripts/harness_collection_lane_commands.py", contract["inputs"])
        self.assertIn("target checker command", "\n".join(contract["outputs"]))
        self.assertIn("readiness_metric_delta", "\n".join(contract["outputs"]))
        self.assertIn("next evidence needed", "\n".join(contract["outputs"]))
        self.assertIn("capture gate", "\n".join(contract["outputs"]))
        self.assertIn("replacement_review_command", "\n".join(contract["outputs"]))
        self.assertIn("append_review_command", "\n".join(contract["outputs"]))
        self.assertIn("outcome_review_command", "\n".join(contract["outputs"]))
        self.assertIn("upgrade_decision_review_command", "\n".join(contract["outputs"]))
        self.assertIn("contract_precondition_review_command", "\n".join(contract["outputs"]))
        self.assertIn("contract_blocker_state", "\n".join(contract["outputs"]))
        self.assertIn("review blockers", "\n".join(contract["outputs"]))
        self.assertIn("area, priority", "\n".join(contract["outputs"]))
        self.assertIn("readiness scoped queue filters", "\n".join(contract["outputs"]))
        self.assertIn("ledger-action", "\n".join(contract["outputs"]))
        self.assertIn("queue summary counts", "\n".join(contract["outputs"]))
        self.assertIn("empty filtered", "\n".join(contract["outputs"]))
        self.assertIn(
            "optional JSONL sample, upgrade-decision, or future-work contract template stdout",
            contract["outputs"],
        )
        self.assertIn("--sample-template", "\n".join(contract["verification_commands"]))
        self.assertIn("--priority P0 --capture-card", "\n".join(contract["verification_commands"]))
        self.assertIn("--ledger-action append-new-pending-slot --capture-card", "\n".join(contract["verification_commands"]))
        self.assertIn("--ledger-action fill-existing-placeholder --capture-card", "\n".join(contract["verification_commands"]))
        self.assertIn("--ledger-action review-upgrade-decision --capture-card", "\n".join(contract["verification_commands"]))
        self.assertIn(
            "--include-future --ledger-action define-contract-precondition --capture-card",
            "\n".join(contract["verification_commands"]),
        )
        self.assertIn("--actionable-only --pending-state without-pending", "\n".join(contract["verification_commands"]))
        self.assertIn(
            "--actionable-only --pending-state without-review-ready-pending",
            "\n".join(contract["verification_commands"]),
        )
        self.assertIn("--gap-id GAP-AGENTIC-CASCADE-STOP --capture-card", "\n".join(contract["verification_commands"]))
        self.assertIn("--gap-id GAP-TRACE-REMOTE-INTEROP --capture-card", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-gate requires-approved-remote-interop --capture-card", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-gate requires-approved-bounded-incident --capture-card", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-gate replace-placeholder-after-real-event --capture-card", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-gate requires-security-workflow-event --capture-card", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-gate requires-bounded-real-incident --capture-card", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-gate requires-workflow-task-event --capture-card", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-gate requires-cross-task-resume --capture-card", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-gate requires-distinct-task-class-report --capture-card", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-gate requires-user-confirmed-high-impact-action --capture-card", "\n".join(contract["verification_commands"]))
        self.assertIn("--readiness needs-first-real-sample --capture-card", "\n".join(contract["verification_commands"]))
        self.assertIn("--readiness needs-more-real-samples --capture-card", "\n".join(contract["verification_commands"]))
        self.assertIn(
            "--readiness ready-for-upgrade-discussion --capture-card",
            "\n".join(contract["verification_commands"]),
        )
        self.assertIn(
            "--include-accepted --readiness local-sample-only --capture-card",
            "\n".join(contract["verification_commands"]),
        )
        self.assertIn("--gap-id GAP-DOES-NOT-EXIST --capture-card", "\n".join(contract["verification_commands"]))
        self.assertIn("scripts/plan_harness_sample_collection.py --json", "\n".join(contract["verification_commands"]))
        self.assertIn(
            "--include-future --ledger-action define-contract-precondition --json",
            "\n".join(contract["verification_commands"]),
        )
        self.assertIn("tests/test_governance_workflow_sample_outputs.py", "\n".join(contract["verification_commands"]))
        self.assertIn("tests/test_plan_harness_sample_collection.py", "\n".join(contract["verification_commands"]))
        self.assertIn("target checker command", contract["notes"])
        self.assertIn("readiness_metric_delta", contract["notes"])
        self.assertIn("readiness satisfaction", contract["notes"])
        self.assertIn("capture_gate/capture_gate_detail", contract["notes"])
        self.assertIn("cross-task resume", contract["notes"])
        self.assertIn("lane-specific review command fields", contract["notes"])
        self.assertIn("replacement_review_command", contract["notes"])
        self.assertIn("append_review_command", contract["notes"])
        self.assertIn("outcome_review_command", contract["notes"])
        self.assertIn("upgrade_decision_review_command", contract["notes"])
        self.assertIn("contract_precondition_review_command", contract["notes"])
        self.assertIn("Empty filtered markdown or capture-card scopes", contract["notes"])
        self.assertIn("contract_blocker_state", contract["notes"])
        self.assertIn("blocked lanes stay machine-routable without approving sampling", contract["notes"])
        self.assertIn("Approved future-work gaps with sample_collection_allowed=true", contract["notes"])
        self.assertIn("bounded cascade-stop incident capture", contract["notes"])
        self.assertIn("check_harness_upgrade_decision_candidate.py <candidate-jsonl>", contract["notes"])
        self.assertIn("reuse the existing upgrade decision id", contract["notes"])
        self.assertIn("Next evidence needed", contract["notes"])
        self.assertIn("per-gap evidence_needed", contract["notes"])
        self.assertIn("check_harness_future_work_contract_candidate.py <candidate-jsonl>", contract["notes"])
        self.assertIn("reuse the existing contract id", contract["notes"])
        self.assertIn("do not infer review routing from ledger_action", contract["notes"])
        self.assertIn("pending slot review blockers", contract["notes"])
        self.assertIn("queue summary counts", contract["notes"])
        self.assertIn("does not collect real samples", contract["notes"])
        self.assertIn("area/priority/ledger-action/actionable/pending-state/capture-gate/readiness filters", contract["notes"])
        self.assertIn("gaps without pending slots, gaps without review-ready pending slots", contract["notes"])
        self.assertIn("--capture-gate", contract["notes"])
        self.assertIn("--readiness needs-first-real-sample", contract["notes"])
        self.assertIn("--readiness needs-more-real-samples", contract["notes"])
        self.assertIn("--readiness ready-for-upgrade-discussion", contract["notes"])
        self.assertIn("--include-accepted --readiness local-sample-only", contract["notes"])
        self.assertIn(
            "active-area, active-priority, append-new-pending-slot, fill-existing-placeholder, remote interop, approved bounded incident, placeholder replacement, security workflow event, bounded real incident, workflow task event, cross-task resume, distinct task-class local trace report, user-confirmed high-impact action, upgrade decision review, needs-first-real-sample, needs-more-real-samples, ready-for-upgrade-discussion, and local-sample-only capture-card views",
            contract["notes"],
        )
        self.assertIn("placeholder-fill work", contract["notes"])
        self.assertIn("reuse the existing pending sample id", contract["notes"])
        self.assertIn("replacement drafts, not append drafts", contract["notes"])
        self.assertIn("review-upgrade-decision", contract["notes"])
        self.assertIn("bounded keep/promote/defer decision drafts", contract["notes"])
        self.assertIn("future-work contract precondition review", contract["notes"])
        self.assertIn("placeholder pending rows still need real events", contract["notes"])
        self.assertIn("GitHub step summary", contract["notes"])

    def test_sample_template_contract_is_drift_check_only(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "check_harness_sample_templates")

        self.assertEqual(contract["side_effects"], ["read_repo"])
        self.assertFalse(contract["destructive"])
        self.assertFalse(contract["externally_visible"])
        self.assertIn("generated pending templates, review-ready pending outcome candidates", "\n".join(contract["inputs"]))
        self.assertIn("outcome candidate helper from scripts/harness_sample_outcome_templates.py", contract["inputs"])
        self.assertIn("outcome review gate from scripts/check_harness_sample_outcome.py", contract["inputs"])
        self.assertIn("area, priority", "\n".join(contract["outputs"]))
        self.assertIn("ledger-action", "\n".join(contract["outputs"]))
        self.assertIn("capture-gate", "\n".join(contract["outputs"]))
        self.assertIn("readiness scoped template filters", "\n".join(contract["outputs"]))
        self.assertIn("capture gate counts", "\n".join(contract["outputs"]))
        self.assertIn("skipped no-sample-collection count and gap ids", "\n".join(contract["outputs"]))
        self.assertIn("outcome candidate validation for review-existing-pending-slot", contract["outputs"])
        self.assertIn("--actionable-only --pending-state without-pending", "\n".join(contract["verification_commands"]))
        self.assertIn(
            "--actionable-only --pending-state without-review-ready-pending",
            "\n".join(contract["verification_commands"]),
        )
        self.assertIn("--ledger-action append-new-pending-slot", "\n".join(contract["verification_commands"]))
        self.assertIn("--ledger-action fill-existing-placeholder", "\n".join(contract["verification_commands"]))
        self.assertIn("--ledger-action review-existing-pending-slot", "\n".join(contract["verification_commands"]))
        self.assertIn("--ledger-action review-upgrade-decision", "\n".join(contract["verification_commands"]))
        self.assertIn("--area workflow-skills --priority P2", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-gate requires-approved-remote-interop", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-gate requires-approved-bounded-incident", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-gate replace-placeholder-after-real-event", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-gate requires-security-workflow-event", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-gate requires-bounded-real-incident", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-gate requires-workflow-task-event", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-gate requires-cross-task-resume", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-gate requires-distinct-task-class-report", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-gate requires-user-confirmed-high-impact-action", "\n".join(contract["verification_commands"]))
        self.assertIn("--readiness needs-first-real-sample", "\n".join(contract["verification_commands"]))
        self.assertIn("--readiness needs-more-real-samples", "\n".join(contract["verification_commands"]))
        self.assertIn("--readiness ready-for-upgrade-discussion", "\n".join(contract["verification_commands"]))
        self.assertIn("--readiness local-sample-only", "\n".join(contract["verification_commands"]))
        self.assertIn("tests/test_harness_sample_templates.py", "\n".join(contract["verification_commands"]))
        self.assertIn("does not append evidence", contract["notes"])
        self.assertIn("replacement draft shape", contract["notes"])
        self.assertIn("review-ready pending outcome candidate shape", contract["notes"])
        self.assertIn("generated from the original pending ledger row", contract["notes"])
        self.assertIn("check_harness_sample_outcome.py", contract["notes"])
        self.assertIn("area/priority/ledger-action/actionable/pending-state/capture-gate/readiness filtered queues", contract["notes"])
        self.assertIn("--readiness needs-first-real-sample", contract["notes"])
        self.assertIn("--readiness needs-more-real-samples", contract["notes"])
        self.assertIn("--readiness ready-for-upgrade-discussion", contract["notes"])
        self.assertIn("Local-only no-sample-collection rows are skipped and reported", contract["notes"])
        self.assertIn(
            "active-area and active-priority focused reports, append-new-pending-slot, fill-existing-placeholder, remote interop, approved bounded incident, placeholder replacement, security workflow event, bounded real incident, workflow task event, cross-task resume, distinct task-class local trace report, user-confirmed high-impact action, upgrade decision review, needs-first-real-sample, needs-more-real-samples, ready-for-upgrade-discussion, and local-sample-only focused reports",
            contract["notes"],
        )
        self.assertIn("GitHub step summary", contract["notes"])
        self.assertIn("capture_gate_counts", contract["notes"])
        self.assertIn("capture_gate/capture_gate_detail", contract["notes"])
        self.assertIn("blocked future-work contract draft shape", contract["notes"])
        self.assertIn("approved future-work pending sample draft shape", contract["notes"])
        self.assertIn("upgrade-decision draft shape", contract["notes"])

    def test_sample_intake_bundle_contract_is_stdout_only(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "build_harness_sample_intake_bundle")

        self.assertEqual(contract["side_effects"], ["read_repo"])
        self.assertEqual(contract["permissions"], ["read-repo"])
        self.assertEqual(contract["automation_mode"], "assistive")
        self.assertFalse(contract["destructive"])
        self.assertFalse(contract["externally_visible"])
        self.assertIn("collection queue from scripts/plan_harness_sample_collection.py", contract["inputs"])
        self.assertIn("generated pending templates, outcome candidates", "\n".join(contract["inputs"]))
        self.assertIn("outcome candidate helper from scripts/harness_sample_outcome_templates.py", contract["inputs"])
        self.assertIn("sample review command routing from scripts/harness_sample_review_commands.py", contract["inputs"])
        self.assertIn("collection lane command routing from scripts/harness_collection_lane_commands.py", contract["inputs"])
        self.assertIn("markdown rendering helpers from scripts/harness_sample_intake_render.py", contract["inputs"])
        self.assertIn("stdout markdown intake bundle grouped by target artifact", contract["outputs"])
        self.assertIn("compact markdown summary", "\n".join(contract["outputs"]))
        self.assertIn("target checker command", "\n".join(contract["outputs"]))
        self.assertIn("readiness_metric_delta", "\n".join(contract["outputs"]))
        self.assertIn("evidence_needed capture checklist", "\n".join(contract["outputs"]))
        self.assertIn("ready-gap next evidence needed", "\n".join(contract["outputs"]))
        self.assertIn("capture gate", "\n".join(contract["outputs"]))
        self.assertIn("placeholder replacement review command", "\n".join(contract["outputs"]))
        self.assertIn("pending append review command", "\n".join(contract["outputs"]))
        self.assertIn("dedicated outcome_review_command", "\n".join(contract["outputs"]))
        self.assertIn("outcome candidate write mode", "\n".join(contract["outputs"]))
        self.assertIn("dedicated upgrade_decision_review_command", "\n".join(contract["outputs"]))
        self.assertIn("dedicated contract_precondition_review_command", "\n".join(contract["outputs"]))
        self.assertIn("contract_blocker_state", "\n".join(contract["outputs"]))
        self.assertIn("area, priority", "\n".join(contract["outputs"]))
        self.assertIn("ledger-action", "\n".join(contract["outputs"]))
        self.assertIn("readiness scoped bundle filters", "\n".join(contract["outputs"]))
        self.assertIn("readiness counts", "\n".join(contract["outputs"]))
        self.assertIn("empty filtered", "\n".join(contract["outputs"]))
        self.assertIn("pending slot status", "\n".join(contract["outputs"]))
        self.assertIn("review blockers", "\n".join(contract["outputs"]))
        self.assertIn("--summary", "\n".join(contract["verification_commands"]))
        self.assertIn("--area ai-guardrail --priority P0 --summary", "\n".join(contract["verification_commands"]))
        self.assertIn("--ledger-action append-new-pending-slot --summary", "\n".join(contract["verification_commands"]))
        self.assertIn("--ledger-action fill-existing-placeholder --summary", "\n".join(contract["verification_commands"]))
        self.assertIn("--ledger-action review-existing-pending-slot --summary", "\n".join(contract["verification_commands"]))
        self.assertIn("--ledger-action review-upgrade-decision --summary", "\n".join(contract["verification_commands"]))
        self.assertIn(
            "--ledger-action define-contract-precondition --summary",
            "\n".join(contract["verification_commands"]),
        )
        self.assertIn("--gap-id GAP-AGENTIC-CASCADE-STOP --summary", "\n".join(contract["verification_commands"]))
        self.assertIn("--gap-id GAP-TRACE-REMOTE-INTEROP --summary", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-gate requires-approved-remote-interop --summary", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-gate requires-approved-bounded-incident --summary", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-gate replace-placeholder-after-real-event --summary", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-gate requires-security-workflow-event --summary", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-gate requires-bounded-real-incident --summary", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-gate requires-workflow-task-event --summary", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-gate requires-cross-task-resume --summary", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-gate requires-distinct-task-class-report --summary", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-gate requires-user-confirmed-high-impact-action --summary", "\n".join(contract["verification_commands"]))
        self.assertIn("--readiness needs-first-real-sample --summary", "\n".join(contract["verification_commands"]))
        self.assertIn("--readiness needs-more-real-samples --summary", "\n".join(contract["verification_commands"]))
        self.assertIn("--readiness ready-for-upgrade-discussion --summary", "\n".join(contract["verification_commands"]))
        self.assertIn("--gap-id GAP-DOES-NOT-EXIST --summary", "\n".join(contract["verification_commands"]))
        self.assertIn("--json", "\n".join(contract["verification_commands"]))
        self.assertIn("tests/test_harness_sample_intake_bundle.py", "\n".join(contract["verification_commands"]))
        self.assertIn("without-review-ready-pending queue", contract["notes"])
        self.assertIn("Empty filtered text or summary scopes", contract["notes"])
        self.assertIn("area/priority/gap/ledger-action/pending-state/capture-gate/readiness filters", contract["notes"])
        self.assertIn(
            "readiness states such as needs-first-real-sample, needs-more-real-samples, or ready-for-upgrade-discussion",
            contract["notes"],
        )
        self.assertIn("target checker command", contract["notes"])
        self.assertIn("readiness_metric_delta", contract["notes"])
        self.assertIn("readiness metric delta", contract["notes"])
        self.assertIn("capture_gate/capture_gate_detail", contract["notes"])
        self.assertIn("evidence_needed capture checklist", contract["notes"])
        self.assertIn("review blockers", contract["notes"])
        self.assertIn("ledger refs", contract["notes"])
        self.assertIn("reuses the existing pending sample id", contract["notes"])
        self.assertIn("replacement write mode", contract["notes"])
        self.assertIn("check_harness_placeholder_replacement.py <candidate-jsonl>", contract["notes"])
        self.assertIn("check_harness_sample_append.py <candidate-jsonl>", contract["notes"])
        self.assertIn("approved future-work gaps", contract["notes"])
        self.assertIn("check_harness_sample_outcome.py <candidate-jsonl>", contract["notes"])
        self.assertIn("outcome_review_command", contract["notes"])
        self.assertIn("outcome candidate generated from the original pending row", contract["notes"])
        self.assertIn("outcome candidate write mode", contract["notes"])
        self.assertIn("outcome review, not sample acceptance", contract["notes"])
        self.assertIn("check_harness_upgrade_decision_candidate.py <candidate-jsonl>", contract["notes"])
        self.assertIn("check_harness_upgrade_decisions.py", contract["notes"])
        self.assertIn("upgrade_decision_review_command", contract["notes"])
        self.assertIn("next_evidence_needed", contract["notes"])
        self.assertIn("Upgrade Decision Review tables", contract["notes"])
        self.assertIn("check_harness_future_work_contracts.py", contract["notes"])
        self.assertIn("check_harness_future_work_contract_candidate.py <candidate-jsonl>", contract["notes"])
        self.assertIn("contract_precondition_review_command", contract["notes"])
        self.assertIn("contract_blocker_state", contract["notes"])
        self.assertIn("missing ADR refs", contract["notes"])
        self.assertIn("sample collection boundary", contract["notes"])
        self.assertIn("contract precondition review", contract["notes"])
        self.assertIn(
            "dedicated append/replacement/outcome/upgrade-decision/contract-precondition review sections",
            contract["notes"],
        )
        self.assertIn("Capture Checklist", contract["notes"])
        self.assertIn("Capture Gates", contract["notes"])
        self.assertIn("readiness counts", contract["notes"])
        self.assertIn(
            "active-area and active-priority focused summaries, append-new-pending-slot, fill-existing-placeholder, remote interop, approved bounded incident, placeholder replacement, security workflow event, bounded real incident, workflow task event, cross-task resume, distinct task-class local trace report, user-confirmed high-impact action, upgrade decision review, needs-first-real-sample, needs-more-real-samples, and ready-for-upgrade-discussion focused summaries",
            contract["notes"],
        )
        self.assertIn("contract blocker state", contract["notes"])
        self.assertIn("GitHub step summary", contract["notes"])
        self.assertIn("does not write ledgers", contract["notes"])
        self.assertIn("count templates as burn-in evidence", contract["notes"])

    def test_placeholder_replacement_contract_is_no_write_review_gate(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "check_harness_placeholder_replacement")

        self.assertEqual(contract["side_effects"], ["read_repo"])
        self.assertEqual(contract["permissions"], ["read-repo"])
        self.assertEqual(contract["automation_mode"], "assistive")
        self.assertFalse(contract["destructive"])
        self.assertFalse(contract["externally_visible"])
        self.assertIn("single JSON or one-record JSONL replacement candidate", contract["inputs"])
        self.assertIn("pending sample slot inventory from scripts/harness_sample_slots.py", contract["inputs"])
        self.assertIn("target checker routing from scripts/check_harness_sample_templates.py", contract["inputs"])
        self.assertIn("target placeholder ledger ref", contract["outputs"])
        self.assertIn("current readiness, source metric, and current / target", contract["outputs"])
        self.assertIn("current fill-existing-placeholder capture_gate and capture_gate_detail", contract["outputs"])
        self.assertIn("current evidence_needed checklist, trigger, and boundary", contract["outputs"])
        self.assertIn(
            "lane-specific focused planner and intake commands with --ledger-action fill-existing-placeholder",
            contract["outputs"],
        )
        self.assertIn("review-ready state and blockers", contract["outputs"])
        self.assertIn("next outcome review command after replacement", contract["outputs"])
        self.assertIn("tests/test_harness_placeholder_replacement.py", "\n".join(contract["verification_commands"]))
        self.assertIn("existing pending placeholder sample id", contract["notes"])
        self.assertIn("fill-existing-placeholder lane", contract["notes"])
        self.assertIn("readiness, source_metric, current_to_target", contract["notes"])
        self.assertIn("capture_gate", contract["notes"])
        self.assertIn("exact readiness metric", contract["notes"])
        self.assertIn("evidence_needed", contract["notes"])
        self.assertIn("real-event precondition", contract["notes"])
        self.assertIn("lane-specific focused planner/intake commands", contract["notes"])
        self.assertIn("--ledger-action fill-existing-placeholder", contract["notes"])
        self.assertIn("outcome=pending", contract["notes"])
        self.assertIn("pending boundary blockers", contract["notes"])
        self.assertIn("no_external_claim", contract["notes"])
        self.assertIn("local_only", contract["notes"])
        self.assertIn("no_network", contract["notes"])
        self.assertIn("check_harness_sample_outcome.py <candidate-jsonl>", contract["notes"])
        self.assertIn("next separate review", contract["notes"])
        self.assertIn("does not append rows", contract["notes"])
        self.assertIn("accept samples", contract["notes"])

    def test_sample_append_contract_is_no_write_review_gate(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "check_harness_sample_append")

        self.assertEqual(contract["side_effects"], ["read_repo"])
        self.assertEqual(contract["permissions"], ["read-repo"])
        self.assertEqual(contract["automation_mode"], "assistive")
        self.assertFalse(contract["destructive"])
        self.assertFalse(contract["externally_visible"])
        self.assertIn("single JSON or one-record JSONL append candidate", contract["inputs"])
        self.assertIn("current append-new-pending-slot queue", "\n".join(contract["inputs"]))
        self.assertIn("target ledger and review command", contract["outputs"])
        self.assertIn("current readiness, source metric, and current / target", contract["outputs"])
        self.assertIn("current capture_gate and capture_gate_detail", contract["outputs"])
        self.assertIn("current evidence_needed checklist, trigger, and boundary", contract["outputs"])
        self.assertIn(
            "lane-specific focused planner and intake commands with --ledger-action append-new-pending-slot",
            contract["outputs"],
        )
        self.assertIn("next outcome review command after append", contract["outputs"])
        self.assertIn("duplicate sample id findings", contract["outputs"])
        self.assertIn("tests/test_harness_sample_append.py", "\n".join(contract["verification_commands"]))
        self.assertIn("--ledger-action append-new-pending-slot", "\n".join(contract["verification_commands"]))
        self.assertIn("append-new-pending-slot lane", contract["notes"])
        self.assertIn("readiness, source_metric, current_to_target", contract["notes"])
        self.assertIn("capture_gate", contract["notes"])
        self.assertIn("exact readiness metric", contract["notes"])
        self.assertIn("evidence_needed", contract["notes"])
        self.assertIn("real-event precondition", contract["notes"])
        self.assertIn("lane-specific focused planner/intake commands", contract["notes"])
        self.assertIn("--ledger-action append-new-pending-slot", contract["notes"])
        self.assertIn("sample id that does not already exist", contract["notes"])
        self.assertIn("outcome=pending", contract["notes"])
        self.assertIn("no_external_claim drift", contract["notes"])
        self.assertIn("local_only mismatches", contract["notes"])
        self.assertIn("red-team pending samples", contract["notes"])
        self.assertIn("no_network/local_only drift", contract["notes"])
        self.assertIn("check_harness_sample_outcome.py <candidate-jsonl>", contract["notes"])
        self.assertIn("next separate review", contract["notes"])
        self.assertIn("does not write ledgers", contract["notes"])
        self.assertIn("accept samples", contract["notes"])

    def test_sample_outcome_contract_is_no_write_review_gate(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "check_harness_sample_outcome")

        self.assertEqual(contract["side_effects"], ["read_repo"])
        self.assertEqual(contract["permissions"], ["read-repo"])
        self.assertEqual(contract["automation_mode"], "assistive")
        self.assertFalse(contract["destructive"])
        self.assertFalse(contract["externally_visible"])
        self.assertIn("single JSON or one-record JSONL outcome candidate", contract["inputs"])
        self.assertIn("existing sample slot inventory from scripts/harness_sample_slots.py", contract["inputs"])
        self.assertIn("current review-existing-pending-slot queue", "\n".join(contract["inputs"]))
        self.assertIn("target review command routing", "\n".join(contract["inputs"]))
        self.assertIn("target pending row ledger ref", contract["outputs"])
        self.assertIn("target pending review state", contract["outputs"])
        self.assertIn("current review-existing-pending-slot ledger_action", "\n".join(contract["outputs"]))
        self.assertIn("current capture_gate and capture_gate_detail", "\n".join(contract["outputs"]))
        self.assertIn("lane-specific focused planner and intake commands", "\n".join(contract["outputs"]))
        self.assertIn("lane-specific focused planner/intake commands", contract["notes"])
        self.assertIn("current evidence_needed checklist, trigger, and boundary", "\n".join(contract["outputs"]))
        self.assertIn("stable evidence field findings", contract["outputs"])
        self.assertIn("burn-in counted flag", contract["outputs"])
        self.assertIn("tests/test_harness_sample_outcome.py", "\n".join(contract["verification_commands"]))
        self.assertIn("--review-state review-ready --review-cards", "\n".join(contract["verification_commands"]))
        self.assertIn("review-ready pending row", contract["notes"])
        self.assertIn("current review-existing-pending-slot lane", contract["notes"])
        self.assertIn("--pending-state with-review-ready-pending", contract["notes"])
        self.assertIn("ledger_action, readiness, source_metric, current_to_target", contract["notes"])
        self.assertIn("capture_gate", contract["notes"])
        self.assertIn("evidence_needed", contract["notes"])
        self.assertIn("still in outcome-review scope", contract["notes"])
        self.assertIn("accepted or rejected", contract["notes"])
        self.assertIn("Direct placeholder-to-accepted changes are rejected", contract["notes"])
        self.assertIn("sample boundary fields valid", contract["notes"])
        self.assertIn("stable evidence fields unchanged", contract["notes"])
        self.assertIn("stable evidence field rewrites", contract["notes"])
        self.assertIn("no_external_claim", contract["notes"])
        self.assertIn("local_only", contract["notes"])
        self.assertIn("no_network drift", contract["notes"])
        self.assertIn("does not write ledgers", contract["notes"])
        self.assertIn("burn_in_counted is true only for accepted real evidence", contract["notes"])

    def test_pending_sample_contract_is_inventory_only(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "check_harness_pending_samples")

        self.assertEqual(contract["side_effects"], ["read_repo"])
        self.assertEqual(contract["automation_mode"], "ci")
        self.assertFalse(contract["destructive"])
        self.assertFalse(contract["externally_visible"])
        self.assertIn("docs/ai/security/agentic-red-team-samples.jsonl", contract["inputs"])
        self.assertIn("pending sample report builder from scripts/harness_pending_sample_report.py", contract["inputs"])
        self.assertIn("pending review card helper from scripts/harness_pending_review_cards.py", contract["inputs"])
        self.assertIn("next capture focus helper from scripts/harness_pending_capture_focus.py", contract["inputs"])
        self.assertIn(
            "collection lane command routing from scripts/harness_collection_lane_commands.py",
            contract["inputs"],
        )
        self.assertIn("sample review command routing from scripts/harness_sample_review_commands.py", contract["inputs"])
        self.assertIn("collection queue from scripts/plan_harness_sample_collection.py", contract["inputs"])
        self.assertIn("actionable sample gap counts", contract["outputs"])
        self.assertIn("ledger action counts", "\n".join(contract["outputs"]))
        self.assertIn("placeholder review blockers for pending slots", contract["outputs"])
        self.assertIn("actionable without review-ready pending counts and lists", contract["outputs"])
        self.assertIn("contract-blocked, ready upgrade-decision, and local-only gap lists", contract["outputs"])
        self.assertIn("ready upgrade-decision next evidence by gap", "\n".join(contract["outputs"]))
        self.assertIn("per-gap contract_blocker_states", "\n".join(contract["outputs"]))
        self.assertIn("next collection lane commands", "\n".join(contract["outputs"]))
        self.assertIn("next capture focus", "\n".join(contract["outputs"]))
        self.assertIn("lane-specific focused planner, intake, lane review commands", "\n".join(contract["outputs"]))
        self.assertIn("current ledger_action", "\n".join(contract["outputs"]))
        self.assertIn("capture_gate/capture_gate_detail", "\n".join(contract["outputs"]))
        self.assertIn("evidence-needed checklist", "\n".join(contract["outputs"]))
        self.assertIn("area / priority / ledger-action", "\n".join(contract["outputs"]))
        self.assertIn("readiness filters", "\n".join(contract["outputs"]))
        self.assertIn("per-entry readiness metric delta", "\n".join(contract["outputs"]))
        self.assertIn("readiness bucket counts", "\n".join(contract["outputs"]))
        self.assertIn("shown/available counts", "\n".join(contract["outputs"]))
        self.assertIn("hidden gap ids", "\n".join(contract["outputs"]))
        self.assertIn("pending slot refs", "\n".join(contract["outputs"]))
        self.assertIn("pending review blockers", "\n".join(contract["outputs"]))
        self.assertIn("placeholder replacement review command", "\n".join(contract["outputs"]))
        self.assertIn("pending append review command", "\n".join(contract["outputs"]))
        self.assertIn("upgrade-decision review command", "\n".join(contract["outputs"]))
        self.assertIn("outcome review command", "\n".join(contract["outputs"]))
        self.assertIn("filtered by gap or review state", "\n".join(contract["outputs"]))
        self.assertIn(
            "ledger_action, capture_gate/capture_gate_detail, trigger, and evidence-needed checklist",
            "\n".join(contract["outputs"]),
        )
        self.assertIn("compact next capture focus cards", "\n".join(contract["outputs"]))
        self.assertIn("empty filtered text output", "\n".join(contract["outputs"]))
        self.assertIn("--gap-id GAP-DOES-NOT-EXIST", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-focus", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-focus --capture-focus-limit 0", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-focus --capture-focus-area agentic-red-team", "\n".join(contract["verification_commands"]))
        self.assertIn("--capture-focus --capture-focus-priority P2", "\n".join(contract["verification_commands"]))
        self.assertIn(
            "--capture-focus --capture-focus-ledger-action append-new-pending-slot --capture-focus-limit 0",
            "\n".join(contract["verification_commands"]),
        )
        self.assertIn(
            "--capture-focus --capture-focus-ledger-action fill-existing-placeholder",
            "\n".join(contract["verification_commands"]),
        )
        self.assertIn(
            "--capture-focus --capture-focus-ledger-action fill-existing-placeholder --capture-focus-limit 0",
            "\n".join(contract["verification_commands"]),
        )
        self.assertIn(
            "--capture-focus --capture-focus-gate requires-approved-remote-interop",
            "\n".join(contract["verification_commands"]),
        )
        self.assertIn(
            "--capture-focus --capture-focus-gate requires-approved-bounded-incident",
            "\n".join(contract["verification_commands"]),
        )
        self.assertIn(
            "--capture-focus --capture-focus-gate replace-placeholder-after-real-event",
            "\n".join(contract["verification_commands"]),
        )
        self.assertIn(
            "--capture-focus --capture-focus-gate requires-security-workflow-event",
            "\n".join(contract["verification_commands"]),
        )
        self.assertIn(
            "--capture-focus --capture-focus-gate requires-bounded-real-incident",
            "\n".join(contract["verification_commands"]),
        )
        self.assertIn(
            "--capture-focus --capture-focus-gate requires-workflow-task-event",
            "\n".join(contract["verification_commands"]),
        )
        self.assertIn(
            "--capture-focus --capture-focus-gate requires-cross-task-resume",
            "\n".join(contract["verification_commands"]),
        )
        self.assertIn(
            "--capture-focus --capture-focus-gate requires-distinct-task-class-report",
            "\n".join(contract["verification_commands"]),
        )
        self.assertIn(
            "--capture-focus --capture-focus-gate requires-user-confirmed-high-impact-action",
            "\n".join(contract["verification_commands"]),
        )
        self.assertIn(
            "--capture-focus --capture-focus-readiness needs-first-real-sample",
            "\n".join(contract["verification_commands"]),
        )
        self.assertIn(
            "--capture-focus --capture-focus-readiness needs-more-real-samples",
            "\n".join(contract["verification_commands"]),
        )
        self.assertIn("--gap-id GAP-WORKFLOW-TASK-PROFILE-AUDIT --capture-focus", "\n".join(contract["verification_commands"]))
        self.assertIn("--review-cards", "\n".join(contract["verification_commands"]))
        self.assertIn("--gap-id GAP-GUARDRAIL-PREFLIGHT-WARNING --review-cards", "\n".join(contract["verification_commands"]))
        self.assertIn("--review-state placeholder --review-cards", "\n".join(contract["verification_commands"]))
        self.assertIn("--review-state review-ready --review-cards", "\n".join(contract["verification_commands"]))
        self.assertIn("--include-future --include-accepted", "\n".join(contract["verification_commands"]))
        self.assertIn("--include-future --include-accepted --json", "\n".join(contract["verification_commands"]))
        self.assertIn("tests/test_governance_workflow_sample_outputs.py", "\n".join(contract["verification_commands"]))
        self.assertIn("tests/test_harness_pending_samples.py", "\n".join(contract["verification_commands"]))
        self.assertIn("separates actionable sample gaps", contract["notes"])
        self.assertIn("actionable gaps without review-ready pending", contract["notes"])
        self.assertIn("placeholder rows remain visible", contract["notes"])
        self.assertIn("no_external_claim drift", contract["notes"])
        self.assertIn("red-team pending boundary drift", contract["notes"])
        self.assertIn("local trace no_network/local_only drift", contract["notes"])
        self.assertIn("groups queued and actionable gaps by ledger action", contract["notes"])
        self.assertIn("contract_blocker_states", contract["notes"])
        self.assertIn("missing ADR refs", contract["notes"])
        self.assertIn("sample collection boundary", contract["notes"])
        self.assertIn("Approved future-work gaps are counted as actionable sample gaps", contract["notes"])
        self.assertIn("check_harness_placeholder_replacement.py <candidate-jsonl>", contract["notes"])
        self.assertIn("check_harness_sample_append.py <candidate-jsonl>", contract["notes"])
        self.assertIn("check_harness_sample_outcome.py <candidate-jsonl>", contract["notes"])
        self.assertIn("check_harness_upgrade_decision_candidate.py <candidate-jsonl>", contract["notes"])
        self.assertIn("next collection lane commands", contract["notes"])
        self.assertIn("ready_upgrade_decision_next_evidence_by_gap", contract["notes"])
        self.assertIn("keep-advisory follow-up evidence", contract["notes"])
        self.assertIn("next_capture_focus", contract["notes"])
        self.assertIn("capture_gate", contract["notes"])
        self.assertIn("capture_gate_detail", contract["notes"])
        self.assertIn("evidence_needed checklist", contract["notes"])
        self.assertIn("next_capture_focus_area_filter", contract["notes"])
        self.assertIn("next_capture_focus_priority_filter", contract["notes"])
        self.assertIn("next_capture_focus_ledger_action_filter", contract["notes"])
        self.assertIn("next_capture_focus_capture_gate_filter", contract["notes"])
        self.assertIn("next_capture_focus_readiness_filter", contract["notes"])
        self.assertIn("next_capture_focus_available_count", contract["notes"])
        self.assertIn("next_capture_focus_truncated", contract["notes"])
        self.assertIn("next_capture_focus_hidden_gap_ids", contract["notes"])
        self.assertIn("next_capture_focus_available_area_counts", contract["notes"])
        self.assertIn("next_capture_focus_available_priority_counts", contract["notes"])
        self.assertIn("next_capture_focus_available_ledger_action_counts", contract["notes"])
        self.assertIn("next_capture_focus_available_capture_gate_counts", contract["notes"])
        self.assertIn("next_capture_focus_available_readiness_counts", contract["notes"])
        self.assertIn("pending_slot_refs", contract["notes"])
        self.assertIn("pending_review_blockers", contract["notes"])
        self.assertIn("readiness_metric_delta", contract["notes"])
        self.assertIn("standalone focus card", contract["notes"])
        self.assertIn("lane-specific focused planner/intake/review commands", contract["notes"])
        self.assertIn("current ledger_action", contract["notes"])
        self.assertIn("--capture-focus mode", contract["notes"])
        self.assertIn(
            "--capture-focus-area, --capture-focus-priority, --capture-focus-ledger-action, "
            "--capture-focus-gate, and --capture-focus-readiness filters",
            contract["notes"],
        )
        self.assertIn("--capture-focus-limit 0 expands all matching actionable capture lanes", contract["notes"])
        self.assertIn("shown/available focus count", contract["notes"])
        self.assertIn("area / priority / ledger-action / capture-gate / readiness bucket counts", contract["notes"])
        self.assertIn("truncation status", contract["notes"])
        self.assertIn("hidden gap ids", contract["notes"])
        self.assertIn("roadmap area, target artifact, target checker", contract["notes"])
        self.assertIn("placeholder row refs and blockers", contract["notes"])
        self.assertIn("future-work contract preconditions", contract["notes"])
        self.assertIn("focused by gap id or review state", contract["notes"])
        self.assertIn("bind pending slots to checker commands", contract["notes"])
        self.assertIn("ledger_action, capture_gate/capture_gate_detail, trigger, evidence_needed checklist", contract["notes"])
        self.assertIn("real-event precondition without opening capture focus", contract["notes"])
        self.assertIn("replacement review commands", contract["notes"])
        self.assertIn("outcome review commands", contract["notes"])
        self.assertIn("review blockers", contract["notes"])
        self.assertIn("remote-interop capture focus", contract["notes"])
        self.assertIn("append-new-pending-slot capture focus", contract["notes"])
        self.assertIn("fill-existing-placeholder capture focus", contract["notes"])
        self.assertIn("approved-bounded-incident capture focus", contract["notes"])
        self.assertIn("placeholder-replacement capture focus", contract["notes"])
        self.assertIn("security-workflow-event capture focus", contract["notes"])
        self.assertIn("bounded-real-incident capture focus", contract["notes"])
        self.assertIn("workflow-task-event capture focus", contract["notes"])
        self.assertIn("cross-task-resume capture focus", contract["notes"])
        self.assertIn("distinct-task-class-report capture focus", contract["notes"])
        self.assertIn("user-confirmed-high-impact-action capture focus", contract["notes"])
        self.assertIn("GitHub step summary", contract["notes"])
        self.assertIn("Empty filtered text output", contract["notes"])
        self.assertIn("does not collect samples", contract["notes"])
        self.assertIn("approve future-work sampling", contract["notes"])
        self.assertIn("accept pending slots", contract["notes"])

    def test_future_work_contract_is_precondition_only(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "check_harness_future_work_contracts")

        self.assertEqual(contract["side_effects"], ["read_repo"])
        self.assertEqual(contract["automation_mode"], "ci")
        self.assertFalse(contract["destructive"])
        self.assertFalse(contract["externally_visible"])
        self.assertIn("docs/ai/standards/harness-future-work-contracts.jsonl", contract["inputs"])
        self.assertIn("per-gap contract_states", "\n".join(contract["outputs"]))
        self.assertIn("--json", "\n".join(contract["verification_commands"]))
        self.assertIn("tests/test_governance_workflow_sample_outputs.py", "\n".join(contract["verification_commands"]))
        self.assertIn("tests/test_harness_future_work_contracts.py", "\n".join(contract["verification_commands"]))
        self.assertIn("tests/test_harness_future_work_contract_candidate.py", "\n".join(contract["verification_commands"]))
        self.assertIn("GitHub step summary", contract["notes"])
        self.assertIn("duplicate gap_id rows", contract["notes"])
        self.assertIn("replace the existing row", contract["notes"])
        self.assertIn("missing ADR refs", contract["notes"])
        self.assertIn("sample collection boundary", contract["notes"])
        self.assertIn("review command", contract["notes"])
        self.assertIn("approved-for-sampling", contract["notes"])
        self.assertIn("existing adopted repo ADR", contract["notes"])
        self.assertIn("auth_model", contract["notes"])
        self.assertIn("endpoint_or_authority_scope", contract["notes"])
        self.assertIn("redaction_or_boundary_model", contract["notes"])
        self.assertIn("cost_or_stop_boundary", contract["notes"])
        self.assertIn("does not prove remote interop", contract["notes"])
        self.assertIn("bounded pending-sample path", contract["notes"])
        self.assertIn("accept samples", contract["notes"])

    def test_future_work_contract_candidate_is_no_write_review_gate(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "check_harness_future_work_contract_candidate")

        self.assertEqual(contract["side_effects"], ["read_repo"])
        self.assertEqual(contract["permissions"], ["read-repo"])
        self.assertEqual(contract["automation_mode"], "assistive")
        self.assertFalse(contract["destructive"])
        self.assertFalse(contract["externally_visible"])
        self.assertIn("single JSON or one-record JSONL future-work contract candidate", contract["inputs"])
        self.assertIn("current define-contract-precondition queue", "\n".join(contract["inputs"]))
        self.assertIn("may be empty when all current future-work contracts are approved", "\n".join(contract["inputs"]))
        self.assertIn("harness_future_work_contract_context.py", "\n".join(contract["inputs"]))
        self.assertIn("target current contract row and status", "\n".join(contract["outputs"]))
        self.assertIn("candidate sample_collection_allowed", "\n".join(contract["outputs"]))
        self.assertIn("ledger_action, readiness, source_metric, and current_to_target", "\n".join(contract["outputs"]))
        self.assertIn("current capture_gate and capture_gate_detail", "\n".join(contract["outputs"]))
        self.assertIn("current evidence_needed, trigger, and boundary", "\n".join(contract["outputs"]))
        self.assertIn("lane-specific focused planner and intake commands", "\n".join(contract["outputs"]))
        self.assertIn("next full contract audit command", "\n".join(contract["outputs"]))
        self.assertIn("<candidate-jsonl>", contract["command"])
        self.assertIn("tests/test_harness_future_work_contract_candidate.py", "\n".join(contract["verification_commands"]))
        self.assertIn("no-write contract candidate review gate", contract["notes"])
        self.assertIn("current_to_target", contract["notes"])
        self.assertIn("capture_gate", contract["notes"])
        self.assertIn("lane-specific focused planner/intake commands", contract["notes"])
        self.assertIn("append-new-pending-slot", contract["notes"])
        self.assertIn("empty generic intake scope", contract["notes"])
        self.assertIn("reuse the existing contract id", contract["notes"])
        self.assertIn("replace the row instead of appending", contract["notes"])
        self.assertIn("approved-for-sampling", contract["notes"])
        self.assertIn("existing adopted ADR coverage checks", contract["notes"])
        self.assertIn("auth_model", contract["notes"])
        self.assertIn("endpoint_or_authority_scope", contract["notes"])
        self.assertIn("redaction_or_boundary_model", contract["notes"])
        self.assertIn("cost_or_stop_boundary", contract["notes"])
        self.assertIn("does not write ledgers", contract["notes"])
        self.assertIn("Approved rows that have left the contract-precondition lane", contract["notes"])
        self.assertIn("current define-contract-precondition queue may be empty", contract["notes"])
        self.assertIn("collect samples", contract["notes"])
        self.assertIn("full check_harness_future_work_contracts.py audit still has to pass", contract["notes"])

    def test_upgrade_decisions_contract_is_advisory_only(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "check_harness_upgrade_decisions")

        self.assertEqual(contract["side_effects"], ["read_repo"])
        self.assertEqual(contract["permissions"], ["read-repo"])
        self.assertEqual(contract["automation_mode"], "ci")
        self.assertFalse(contract["destructive"])
        self.assertFalse(contract["externally_visible"])
        self.assertIn("docs/ai/standards/harness-upgrade-decisions.jsonl", contract["inputs"])
        self.assertIn("readiness accounting from scripts/check_harness_burn_in_readiness.py", contract["inputs"])
        self.assertIn("ready gap ids and decided ready gap ids", contract["outputs"])
        self.assertIn("missing and extra upgrade decision gap ids", contract["outputs"])
        self.assertIn("decision counts by decision", contract["outputs"])
        self.assertIn("next evidence needed by ready gap", contract["outputs"])
        self.assertIn("--json", "\n".join(contract["verification_commands"]))
        self.assertIn("tests/test_harness_upgrade_decisions.py", "\n".join(contract["verification_commands"]))
        self.assertIn("advisory decision audit", contract["notes"])
        self.assertIn("ready-for-upgrade-discussion", contract["notes"])
        self.assertIn("source metric, accepted count, and upgrade target", contract["notes"])
        self.assertIn("next_evidence_needed", contract["notes"])
        self.assertIn("existing repo-relative paths", contract["notes"])
        self.assertIn("markdown anchors, pytest node ids, and JSONL line selectors", contract["notes"])
        self.assertIn("forbids local runtime references", contract["notes"])
        self.assertIn("machine-readable", contract["notes"])
        self.assertIn("does not write ledgers", contract["notes"])
        self.assertIn("upgrade any check", contract["notes"])

    def test_upgrade_decision_candidate_is_no_write_review_gate(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "check_harness_upgrade_decision_candidate")

        self.assertEqual(contract["side_effects"], ["read_repo"])
        self.assertEqual(contract["permissions"], ["read-repo"])
        self.assertEqual(contract["automation_mode"], "assistive")
        self.assertFalse(contract["destructive"])
        self.assertFalse(contract["externally_visible"])
        self.assertIn("single JSON or one-record JSONL upgrade-decision candidate", contract["inputs"])
        self.assertIn("current review-upgrade-decision queue", "\n".join(contract["inputs"]))
        self.assertIn("harness_upgrade_decision_context.py", "\n".join(contract["inputs"]))
        self.assertIn("target current decision row and decision", "\n".join(contract["outputs"]))
        self.assertIn("candidate readiness snapshot counts", "\n".join(contract["outputs"]))
        self.assertIn("ledger_action, readiness, source_metric, and current_to_target", "\n".join(contract["outputs"]))
        self.assertIn("current capture_gate and capture_gate_detail", "\n".join(contract["outputs"]))
        self.assertIn("current evidence_needed, trigger, and boundary", "\n".join(contract["outputs"]))
        self.assertIn("lane-specific focused planner and intake commands", "\n".join(contract["outputs"]))
        self.assertIn("candidate next evidence needed list", "\n".join(contract["outputs"]))
        self.assertIn("next full upgrade decision audit command", "\n".join(contract["outputs"]))
        self.assertIn("<candidate-jsonl>", contract["command"])
        self.assertIn("tests/test_harness_upgrade_decision_candidate.py", "\n".join(contract["verification_commands"]))
        self.assertIn("no-write upgrade decision candidate review gate", contract["notes"])
        self.assertIn("next_evidence_needed", contract["notes"])
        self.assertIn("current_to_target", contract["notes"])
        self.assertIn("capture_gate", contract["notes"])
        self.assertIn("lane-specific focused planner/intake commands", contract["notes"])
        self.assertIn("--ledger-action review-upgrade-decision", contract["notes"])
        self.assertIn("reuse the existing decision id", contract["notes"])
        self.assertIn("replace the row instead of appending", contract["notes"])
        self.assertIn("does not write ledgers", contract["notes"])
        self.assertIn("upgrade checks", contract["notes"])
        self.assertIn("full check_harness_upgrade_decisions.py audit still has to pass", contract["notes"])

    def test_burn_in_readiness_contract_is_advisory_only(self) -> None:
        data = check_tool_contracts.load_registry(check_tool_contracts.DEFAULT_REGISTRY)
        contracts = data["contracts"]
        contract = next(item for item in contracts if item["name"] == "check_harness_burn_in_readiness")

        self.assertEqual(contract["side_effects"], ["read_repo"])
        self.assertEqual(contract["automation_mode"], "ci")
        self.assertFalse(contract["destructive"])
        self.assertFalse(contract["externally_visible"])
        self.assertIn(
            "accepted-real/readiness delta helper from scripts/harness_burn_in_readiness_deltas.py",
            contract["inputs"],
        )
        self.assertIn(
            "upgrade decision snapshot helper from scripts/harness_upgrade_decision_status.py",
            contract["inputs"],
        )
        self.assertIn("docs/ai/standards/harness-upgrade-decisions.jsonl", contract["inputs"])
        self.assertIn("optional JSON report", contract["outputs"])
        self.assertIn("ready-gap upgrade decision counts", contract["outputs"])
        self.assertIn("per-gap upgrade decision status and decision ref", contract["outputs"])
        self.assertIn("ready gap ids without upgrade decisions", contract["outputs"])
        self.assertIn("ready next evidence needed by gap", contract["outputs"])
        self.assertIn("active area, priority, gap-id, capture-gate, and readiness filters", contract["outputs"])
        self.assertIn("per-gap target artifact and target checker command", contract["outputs"])
        self.assertIn(
            "per-gap ledger action, lane-specific focused planner command, "
            "lane-specific focused intake command, and lane review command",
            contract["outputs"],
        )
        self.assertIn("area and priority counts", contract["outputs"])
        self.assertIn("capture gate counts", contract["outputs"])
        self.assertIn("accepted real/readiness metric deltas", contract["outputs"])
        self.assertIn("readiness and capture-gate gap-id maps for summary handoff", contract["outputs"])
        self.assertIn("per-gap capture gate and capture gate detail", contract["outputs"])
        self.assertIn("future-work contract state evidence", "\n".join(contract["outputs"]))
        commands = "\n".join(contract["verification_commands"])
        self.assertIn("--include-future --include-accepted", commands)
        self.assertIn("--include-future --include-accepted --json", commands)
        for area in (
            "agentic-red-team",
            "ai-guardrail",
            "runtime-durability",
            "security-evidence",
            "trace-interop",
            "workflow-skills",
        ):
            self.assertIn(
                f"--include-future --include-accepted --area {area} --json",
                commands,
            )
        for priority in ("P0", "P1", "P2", "P3"):
            self.assertIn(
                f"--include-future --include-accepted --priority {priority} --json",
                commands,
            )
        self.assertIn(
            "--include-future --include-accepted --gap-id GAP-TRACE-REMOTE-INTEROP --json",
            commands,
        )
        self.assertIn(
            "--include-future --include-accepted --capture-gate requires-approved-remote-interop --json",
            commands,
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
                f"--include-future --include-accepted --capture-gate {capture_gate} --json",
                commands,
            )
        self.assertIn(
            "--include-future --include-accepted --readiness needs-first-real-sample --json",
            commands,
        )
        self.assertIn(
            "--include-future --include-accepted --readiness needs-more-real-samples --json",
            commands,
        )
        self.assertIn(
            "--include-future --include-accepted --readiness ready-for-upgrade-discussion --json",
            commands,
        )
        self.assertIn(
            "--include-future --include-accepted --readiness local-sample-only --json",
            commands,
        )
        self.assertIn("tests/test_governance_workflow_sample_outputs.py", commands)
        self.assertIn("tests/test_harness_burn_in_readiness.py", commands)
        self.assertIn("GitHub step summary", contract["notes"])
        self.assertIn("--area and --priority filters narrow the audit", contract["notes"])
        self.assertIn("--gap-id narrows it to one or more exact gaps", contract["notes"])
        self.assertIn("--capture-gate narrows it to one or more real-event preconditions", contract["notes"])
        self.assertIn("--readiness narrows it to one or more readiness states", contract["notes"])
        self.assertIn("local-sample-only", contract["notes"])
        self.assertIn("zero matching readiness items", contract["notes"])
        self.assertIn("accepted_real_readiness_metric_deltas", contract["notes"])
        self.assertIn("ledger accepted real counts differ from the exact readiness metric", contract["notes"])
        self.assertIn("readiness_gap_ids", contract["notes"])
        self.assertIn("capture_gate_gap_ids", contract["notes"])
        self.assertIn("exact remaining gap ids", contract["notes"])
        self.assertIn("target artifact, target checker command, ledger action", contract["notes"])
        self.assertIn(
            "lane-specific focused planner command, lane-specific focused intake command, and lane review command",
            contract["notes"],
        )
        self.assertIn("generic intake command that returns an empty lane", contract["notes"])
        self.assertIn("Next Collection Commands", contract["notes"])
        self.assertIn("no-write append, replacement, upgrade-decision, contract-precondition", contract["notes"])
        self.assertIn(
            "focused active area, active priority, real capture-gate, upgrade-decision-review, needs-first-real-sample, needs-more-real-samples, ready-for-upgrade-discussion, and local-sample-only",
            contract["notes"],
        )
        self.assertIn("current upgrade decision status", contract["notes"])
        self.assertIn("ready_next_evidence_needed_by_gap", contract["notes"])
        self.assertIn("next_evidence_needed", contract["notes"])
        self.assertIn("keep-advisory follow-up evidence", contract["notes"])
        self.assertIn("missing ADR refs", contract["notes"])
        self.assertIn("sample collection boundary", contract["notes"])
        self.assertIn("approved future-work contracts with complete ADR refs", contract["notes"])
        self.assertIn("strict keep/promote/defer validation remains", contract["notes"])
        self.assertIn("does not collect samples", contract["notes"])

    def test_requires_unique_names(self) -> None:
        errors = self.errors_for(valid_contract(), valid_contract())

        self.assertTrue(any("duplicate name" in error for error in errors))

    def test_rejects_missing_required_field(self) -> None:
        contract = valid_contract()
        del contract["purpose"]

        errors = self.errors_for(contract)

        self.assertTrue(any("missing required field purpose" in error for error in errors))

    def test_rejects_missing_entrypoint_and_verification_path(self) -> None:
        errors = self.errors_for(
            valid_contract(
                path="scripts/missing_tool.py",
                verification_commands=["python3 scripts/missing_tool.py"],
            )
        )

        text = "\n".join(errors)
        self.assertIn("path does not exist", text)
        self.assertIn("references missing path scripts/missing_tool.py", text)

    def test_rejects_unknown_enums_and_bad_timeout(self) -> None:
        errors = self.errors_for(
            valid_contract(
                side_effects=["read_repo", "magic"],
                automation_mode="autopilot",
                timeout_seconds=0,
            )
        )

        text = "\n".join(errors)
        self.assertIn("unknown side_effects value magic", text)
        self.assertIn("automation_mode must be one of", text)
        self.assertIn("timeout_seconds must be between", text)

    def test_rejects_destructive_default_without_human_confirmation(self) -> None:
        errors = self.errors_for(valid_contract(destructive=True))

        text = "\n".join(errors)
        self.assertIn("destructive default command must use human_confirmed", text)
        self.assertIn("human-confirmation-required", text)

    def test_allows_destructive_default_with_required_gate(self) -> None:
        errors = self.errors_for(
            valid_contract(
                destructive=True,
                automation_mode="human_confirmed",
                permissions=["read-repo", "human-confirmation-required"],
            )
        )

        self.assertEqual(errors, [])

    def test_rejects_externally_visible_unattended_default(self) -> None:
        errors = self.errors_for(valid_contract(externally_visible=True, automation_mode="ci"))

        self.assertTrue(any("externally visible default command" in error for error in errors))

    def test_external_write_side_effect_requires_visible_flag(self) -> None:
        errors = self.errors_for(valid_contract(side_effects=["network_write"]))

        self.assertTrue(any("require externally_visible=true" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
