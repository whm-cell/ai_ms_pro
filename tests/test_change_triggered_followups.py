from __future__ import annotations

import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_change_triggered_followups  # noqa: E402


class ChangeTriggeredFollowupsTest(unittest.TestCase):
    def followup_names(self, *files: str) -> set[str]:
        followups = check_change_triggered_followups.build_followups(tuple(files))
        return {item.name for item in followups}

    def markdown_for(self, *files: str) -> str:
        followups = check_change_triggered_followups.build_followups(tuple(files))
        output = io.StringIO()
        with redirect_stdout(output):
            check_change_triggered_followups.emit_markdown(tuple(files), followups)
        return output.getvalue()

    def test_agents_change_triggers_governance_and_budget(self) -> None:
        names = self.followup_names("AGENTS.md")

        self.assertIn("governance-surface", names)
        self.assertIn("default-context-budget", names)

    def test_github_change_triggers_guardrails(self) -> None:
        names = self.followup_names(".github/workflows/governance-and-smoke.yml")

        self.assertIn("github-guardrails", names)
        self.assertIn("high-impact-agent-actions", names)
        self.assertIn("harness-sample-gap-evidence", names)
        self.assertIn("python-linter", names)
        self.assertIn("config-contract-boundary", names)

    def test_python_linter_config_change_triggers_linter_check(self) -> None:
        names = self.followup_names("pyproject.toml")

        self.assertEqual(names, {"python-linter"})

    def test_python_linter_dependency_change_triggers_linter_check(self) -> None:
        names = self.followup_names(".codex/requirements.txt")

        self.assertEqual(names, {"python-linter"})

    def test_supply_chain_workflow_triggers_security_evidence(self) -> None:
        names = self.followup_names(".github/workflows/security-evidence.yml")

        self.assertIn("github-guardrails", names)
        self.assertIn("supply-chain-evidence", names)

    def test_requirements_change_triggers_traceability(self) -> None:
        names = self.followup_names("docs/requirements/source/REQDOC-001.md")

        self.assertIn("governance-surface", names)
        self.assertIn("requirements-traceability", names)

    def test_requirements_checker_helper_triggers_traceability(self) -> None:
        names = self.followup_names("scripts/requirements_technical_assumptions.py")

        self.assertIn("requirements-traceability", names)
        self.assertIn("harness-code-shape", names)

    def test_skill_change_triggers_discoverability_and_budget(self) -> None:
        names = self.followup_names(".agents/skills/harness-maintenance/SKILL.md")

        self.assertIn("default-context-budget", names)
        self.assertIn("repo-local-skills", names)

    def test_codex_skill_change_triggers_catalog_discoverability_and_budget(self) -> None:
        names = self.followup_names(".codex/skills/ui-ux-pro-max/SKILL.md")

        self.assertIn("default-context-budget", names)
        self.assertIn("repo-local-skills", names)

    def test_skill_catalog_change_triggers_catalog_discoverability_and_budget(self) -> None:
        names = self.followup_names(".codex/skills.catalog.json")

        self.assertIn("default-context-budget", names)
        self.assertIn("repo-local-skills", names)

    def test_harness_config_change_triggers_runtime_token_budget(self) -> None:
        names = self.followup_names(".codex/harness.toml")

        self.assertIn("governance-surface", names)
        self.assertIn("runtime-token-budget", names)
        self.assertIn("config-contract-boundary", names)
        self.assertIn("mock-data-boundary", names)
        self.assertIn("reuse-retirement-boundary", names)

    def test_env_template_change_triggers_config_contract(self) -> None:
        followups = check_change_triggered_followups.build_followups((".env.example",))
        names = {item.name for item in followups}
        config_contract = next(item for item in followups if item.name == "config-contract-boundary")

        self.assertIn("config-contract-boundary", names)
        self.assertIn("scripts/check_config_contract.py", "\n".join(config_contract.commands))
        self.assertIn("scripts/check_env_template_sync.py --warning-only", "\n".join(config_contract.commands))

    def test_provider_registry_change_triggers_config_contract(self) -> None:
        names = self.followup_names("lib/xhs/ai/providerConfig.ts")

        self.assertIn("config-contract-boundary", names)

    def test_frontend_page_change_triggers_mock_data_boundary(self) -> None:
        followups = check_change_triggered_followups.build_followups(("app/dashboard/page.tsx",))
        names = {item.name for item in followups}
        mock_boundary = next(item for item in followups if item.name == "mock-data-boundary")

        self.assertIn("mock-data-boundary", names)
        self.assertIn("scripts/check_mock_data_boundary.py", "\n".join(mock_boundary.commands))
        self.assertIn("scripts/check_data_activation.py", "\n".join(mock_boundary.commands))
        self.assertEqual(mock_boundary.level, "review-required")

    def test_fixture_change_triggers_mock_data_boundary(self) -> None:
        names = self.followup_names("fixtures/users.ts")

        self.assertIn("mock-data-boundary", names)

    def test_mock_boundary_helper_change_triggers_contract_and_boundary(self) -> None:
        names = self.followup_names(
            "scripts/mock_data_boundary_lib.py",
            "scripts/mock_data_manifest.py",
            "scripts/mock_data_fixture_checks.py",
            "scripts/check_data_activation.py",
        )

        self.assertIn("mock-data-boundary", names)
        self.assertIn("tool-contract-registry", names)
        self.assertIn("harness-code-shape", names)

    def test_code_change_triggers_reuse_retirement_review(self) -> None:
        followups = check_change_triggered_followups.build_followups(("scripts/new_checker.py",))
        names = {item.name for item in followups}
        reuse = next(item for item in followups if item.name == "reuse-retirement-boundary")

        self.assertIn("reuse-retirement-boundary", names)
        self.assertIn("scripts/check_reuse_retirement.py", "\n".join(reuse.commands))
        self.assertEqual(reuse.level, "review-required")

    def test_reuse_retirement_checker_change_triggers_contract(self) -> None:
        names = self.followup_names("scripts/check_reuse_retirement.py")

        self.assertIn("reuse-retirement-boundary", names)
        self.assertIn("tool-contract-registry", names)
        self.assertIn("harness-code-shape", names)

    def test_reuse_retirement_core_change_triggers_contract(self) -> None:
        names = self.followup_names("scripts/reuse_retirement_core.py")

        self.assertIn("reuse-retirement-boundary", names)
        self.assertIn("tool-contract-registry", names)
        self.assertIn("harness-code-shape", names)

    def test_deployment_env_template_change_triggers_config_contract(self) -> None:
        names = self.followup_names("services/internal_auth/deployment.env.example")

        self.assertIn("config-contract-boundary", names)

    def test_enterprise_boundary_skill_change_triggers_review(self) -> None:
        followups = check_change_triggered_followups.build_followups(
            (".agents/skills/enterprise-code-boundary-maintenance/SKILL.md",)
        )
        names = {item.name for item in followups}
        enterprise = next(item for item in followups if item.name == "enterprise-code-boundaries")

        self.assertIn("enterprise-code-boundaries", names)
        self.assertIn("repo-local-skills", names)
        self.assertIn("scripts/check_repo_skills.py", "\n".join(enterprise.commands))

    def test_enterprise_boundary_standards_trigger_review(self) -> None:
        for path in (
            "docs/ai/standards/logging-redaction-boundary.md",
            "docs/ai/standards/error-contract-boundary.md",
            "docs/ai/standards/runtime-side-effect-boundary.md",
        ):
            names = self.followup_names(path)

            self.assertIn("governance-surface", names)
            self.assertIn("enterprise-code-boundaries", names)

    def test_logger_error_provider_client_and_api_route_trigger_enterprise_boundary(self) -> None:
        for path in (
            "lib/xhs/logging/logger.ts",
            "lib/xhs/errors/modelError.ts",
            "lib/xhs/ai/provider.ts",
            "lib/xhs/clients/bailianClient.ts",
            "app/api/generate/route.ts",
        ):
            names = self.followup_names(path)

            self.assertIn("enterprise-code-boundaries", names)

    def test_enterprise_boundary_rule_helper_triggers_enterprise_boundary(self) -> None:
        names = self.followup_names("scripts/change_triggered_enterprise_boundary_rules.py")

        self.assertIn("enterprise-code-boundaries", names)
        self.assertIn("harness-code-shape", names)

    def test_runtime_token_script_change_triggers_runtime_budget(self) -> None:
        names = self.followup_names("scripts/check_runtime_token_budget.py")

        self.assertIn("runtime-token-budget", names)
        self.assertIn("harness-code-shape", names)

    def test_tool_output_summary_change_triggers_runtime_budget(self) -> None:
        names = self.followup_names("scripts/summarize_tool_output.py")

        self.assertIn("runtime-token-budget", names)
        self.assertIn("harness-code-shape", names)

    def test_pre_tool_preflight_change_triggers_high_impact_review(self) -> None:
        followups = check_change_triggered_followups.build_followups((".codex/hooks/pre_tool_use_preflight.py",))
        names = {item.name for item in followups}
        preflight = next(item for item in followups if item.name == "pre-tool-use-preflight-samples")

        self.assertIn("high-impact-agent-actions", names)
        self.assertIn("pre-tool-use-preflight-samples", names)
        self.assertIn("harness-code-shape", names)
        self.assertIn("scripts/check_warning_sample_code_alignment.py", "\n".join(preflight.commands))
        self.assertIn("tests/test_warning_sample_code_alignment.py", "\n".join(preflight.commands))

    def test_pre_tool_preflight_samples_change_triggers_sample_check(self) -> None:
        names = self.followup_names("docs/ai/standards/pre-tool-use-preflight-samples.jsonl")

        self.assertIn("governance-surface", names)
        self.assertIn("pre-tool-use-preflight-samples", names)
        self.assertIn("high-impact-agent-actions", names)

    def test_stop_runtime_token_pressure_change_triggers_runtime_budget(self) -> None:
        names = self.followup_names(".codex/hooks/stop_runtime_token_pressure.py")

        self.assertIn("runtime-token-budget", names)
        self.assertIn("harness-code-shape", names)

    def test_stop_loop_scope_monitor_change_triggers_runtime_budget(self) -> None:
        followups = check_change_triggered_followups.build_followups((".codex/hooks/stop_loop_scope_monitor.py",))
        names = {item.name for item in followups}
        loop_scope = next(item for item in followups if item.name == "loop-scope-monitor-samples")

        self.assertIn("runtime-token-budget", names)
        self.assertIn("loop-scope-monitor-samples", names)
        self.assertIn("harness-code-shape", names)
        self.assertIn("scripts/check_warning_sample_code_alignment.py", "\n".join(loop_scope.commands))
        self.assertIn("tests/test_warning_sample_code_alignment.py", "\n".join(loop_scope.commands))

    def test_loop_scope_monitor_samples_change_triggers_sample_check(self) -> None:
        names = self.followup_names("docs/ai/standards/loop-scope-monitor-samples.jsonl")

        self.assertIn("governance-surface", names)
        self.assertIn("loop-scope-monitor-samples", names)

    def test_warning_sample_alignment_change_triggers_both_warning_sample_checks(self) -> None:
        followups = check_change_triggered_followups.build_followups(
            ("scripts/check_warning_sample_code_alignment.py",)
        )
        names = {item.name for item in followups}
        preflight = next(item for item in followups if item.name == "pre-tool-use-preflight-samples")
        loop_scope = next(item for item in followups if item.name == "loop-scope-monitor-samples")

        self.assertIn("pre-tool-use-preflight-samples", names)
        self.assertIn("loop-scope-monitor-samples", names)
        self.assertIn("harness-code-shape", names)
        self.assertIn("scripts/check_warning_sample_code_alignment.py", "\n".join(preflight.commands))
        self.assertIn("scripts/check_warning_sample_code_alignment.py", "\n".join(loop_scope.commands))

    def test_runtime_tool_output_artifact_triggers_runtime_budget(self) -> None:
        names = self.followup_names(".codex/runtime/tool-outputs/demo.log")

        self.assertIn("runtime-token-budget", names)

    def test_stage_checkpoint_change_triggers_checkpoint_check(self) -> None:
        names = self.followup_names("docs/ai/checkpoints/stage-checkpoints.jsonl")

        self.assertIn("governance-surface", names)
        self.assertIn("stage-checkpoints", names)

    def test_runtime_execution_snapshot_change_triggers_checkpoint_check(self) -> None:
        names = self.followup_names(".codex/runtime/execution-snapshots/demo.json")

        self.assertIn("stage-checkpoints", names)

    def test_task_outcome_eval_change_triggers_standard_eval_followup(self) -> None:
        names = self.followup_names("docs/ai/evals/task-outcome-evals.jsonl")

        self.assertIn("governance-surface", names)
        self.assertIn("standard-agent-eval", names)

    def test_harness_python_triggers_code_shape(self) -> None:
        names = self.followup_names("scripts/check_github_guardrails.py")

        self.assertIn("github-guardrails", names)
        self.assertIn("harness-code-shape", names)

    def test_agent_trace_standard_change_triggers_trace_check(self) -> None:
        names = self.followup_names("docs/ai/standards/agent-trace-schema.md")

        self.assertIn("governance-surface", names)
        self.assertIn("agent-trace-standard", names)

    def test_runtime_trace_summary_change_triggers_trace_check(self) -> None:
        followups = check_change_triggered_followups.build_followups(("scripts/summarize_runtime_traces.py",))
        names = {item.name for item in followups}
        trace = next(item for item in followups if item.name == "agent-trace-standard")

        self.assertIn("agent-trace-standard", names)
        self.assertIn("local-trace-summary-samples", names)
        self.assertIn("harness-code-shape", names)
        self.assertIn("local summary smoke", trace.ci_coverage)

    def test_remote_trace_report_change_triggers_trace_check(self) -> None:
        names = self.followup_names("docs/ai/standards/trace-remote-interop-report.sample.json")

        self.assertIn("governance-surface", names)
        self.assertIn("agent-trace-standard", names)

    def test_local_trace_summary_sample_change_triggers_sample_check(self) -> None:
        names = self.followup_names("docs/ai/standards/local-trace-summary-samples.jsonl")

        self.assertIn("governance-surface", names)
        self.assertIn("local-trace-summary-samples", names)

    def test_agent_eval_dataset_change_triggers_eval_check(self) -> None:
        names = self.followup_names("docs/ai/evals/agent-harness-evals.jsonl")

        self.assertIn("governance-surface", names)
        self.assertIn("standard-agent-eval", names)

    def test_agent_run_provenance_change_triggers_provenance_check(self) -> None:
        names = self.followup_names("docs/ai/standards/agent-run-provenance-sample.jsonl")

        self.assertIn("governance-surface", names)
        self.assertIn("agent-run-provenance", names)

    def test_ci_agent_contract_change_triggers_contract_check(self) -> None:
        names = self.followup_names("docs/ai/standards/ci-agent-contract.sample.jsonl")

        self.assertIn("governance-surface", names)
        self.assertIn("ci-agent-contract", names)

    def test_external_harness_decisions_change_triggers_decision_check(self) -> None:
        followups = check_change_triggered_followups.build_followups(
            ("docs/ai/standards/external-harness-decisions.jsonl",)
        )
        names = {item.name for item in followups}
        decision = next(item for item in followups if item.name == "external-harness-decisions")

        self.assertIn("governance-surface", names)
        self.assertIn("external-harness-decisions", names)
        self.assertIn("scripts/check_external_harness_decisions.py", "\n".join(decision.commands))

    def test_agent_productization_readiness_change_triggers_readiness_check(self) -> None:
        followups = check_change_triggered_followups.build_followups(
            ("docs/ai/standards/agent-productization-readiness-assessment.jsonl",)
        )
        names = {item.name for item in followups}
        readiness = next(item for item in followups if item.name == "agent-productization-readiness")

        self.assertIn("governance-surface", names)
        self.assertIn("agent-productization-readiness", names)
        self.assertIn("scripts/check_agent_productization_readiness.py", "\n".join(readiness.commands))
        self.assertEqual(readiness.level, "review-required")

    def test_agent_productization_readiness_helper_triggers_readiness_check(self) -> None:
        names = self.followup_names("scripts/agent_productization_readiness.py")

        self.assertIn("agent-productization-readiness", names)
        self.assertIn("harness-code-shape", names)

    def test_local_execution_policy_wrapper_change_triggers_wrapper_checks(self) -> None:
        followups = check_change_triggered_followups.build_followups(("scripts/run_sandboxed_command.py",))
        names = {item.name for item in followups}
        wrapper = next(item for item in followups if item.name == "local-execution-policy-wrapper")

        self.assertIn("local-execution-policy-wrapper", names)
        self.assertIn("tool-contract-registry", names)
        self.assertIn("harness-code-shape", names)
        self.assertIn("tests.test_execution_sandbox_wrapper", "\n".join(wrapper.commands))

    def test_prototype_design_brief_change_triggers_prototype_checks(self) -> None:
        followups = check_change_triggered_followups.build_followups(
            ("docs/ai/templates/prototype-design-brief.md",)
        )
        names = {item.name for item in followups}
        prototype = next(item for item in followups if item.name == "prototype-design-brief")

        self.assertIn("governance-surface", names)
        self.assertIn("prototype-design-brief", names)
        self.assertIn("scripts/check_prototype_design_brief.py", "\n".join(prototype.commands))

    def test_prototype_checker_change_triggers_code_shape_and_tests(self) -> None:
        followups = check_change_triggered_followups.build_followups(("scripts/check_prototype_design_brief.py",))
        names = {item.name for item in followups}
        prototype = next(item for item in followups if item.name == "prototype-design-brief")

        self.assertIn("prototype-design-brief", names)
        self.assertIn("harness-code-shape", names)
        self.assertIn("tests/test_prototype_design_brief.py", "\n".join(prototype.commands))

    def test_next_best_work_review_change_triggers_review_checks(self) -> None:
        followups = check_change_triggered_followups.build_followups(("scripts/ai_governance_next_best_work.py",))
        names = {item.name for item in followups}
        review = next(item for item in followups if item.name == "next-best-work-review")
        commands = "\n".join(review.commands)

        self.assertIn("next-best-work-review", names)
        self.assertIn("harness-code-shape", names)
        self.assertIn("tests/test_next_best_work_review.py", commands)
        self.assertIn("scripts/check_ai_governance.py", commands)

    def test_next_best_work_template_change_triggers_review_checks(self) -> None:
        names = self.followup_names("docs/ai/templates/next-best-work-review.md")

        self.assertIn("governance-surface", names)
        self.assertIn("next-best-work-review", names)

    def test_agentic_red_team_sample_change_triggers_sample_check(self) -> None:
        names = self.followup_names("docs/ai/security/agentic-red-team-samples.jsonl")

        self.assertIn("governance-surface", names)
        self.assertIn("agentic-red-team-samples", names)
        self.assertIn("supply-chain-evidence", names)

    def test_harness_sample_template_change_triggers_template_drift_check(self) -> None:
        followups = check_change_triggered_followups.build_followups(
            ("scripts/harness_sample_templates.py", "scripts/harness_sample_template_records.py")
        )
        names = {item.name for item in followups}
        sample_gap = next(item for item in followups if item.name == "harness-sample-gap-evidence")

        self.assertIn("harness-sample-gap-evidence", names)
        self.assertIn("harness-code-shape", names)
        self.assertIn("scripts/check_harness_sample_templates.py", "\n".join(sample_gap.commands))
        self.assertIn("tests/test_harness_sample_templates.py", "\n".join(sample_gap.commands))
        self.assertIn(
            "scripts/plan_harness_sample_collection.py "
            "--capture-gate replace-placeholder-after-real-event --capture-card",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/plan_harness_sample_collection.py "
            "--capture-gate requires-approved-bounded-incident --capture-card",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/plan_harness_sample_collection.py "
            "--capture-gate requires-security-workflow-event --capture-card",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/plan_harness_sample_collection.py "
            "--capture-gate requires-bounded-real-incident --capture-card",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/plan_harness_sample_collection.py "
            "--capture-gate requires-workflow-task-event --capture-card",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/plan_harness_sample_collection.py "
            "--capture-gate requires-cross-task-resume --capture-card",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/plan_harness_sample_collection.py "
            "--capture-gate requires-distinct-task-class-report --capture-card",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/plan_harness_sample_collection.py "
            "--capture-gate requires-user-confirmed-high-impact-action --capture-card",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/plan_harness_sample_collection.py --ledger-action review-upgrade-decision --capture-card",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/plan_harness_sample_collection.py --ledger-action append-new-pending-slot --capture-card",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/plan_harness_sample_collection.py --ledger-action fill-existing-placeholder --capture-card",
            "\n".join(sample_gap.commands),
        )
        self.assertIn("scripts/plan_harness_sample_collection.py --readiness needs-first-real-sample", "\n".join(sample_gap.commands))
        self.assertIn("scripts/plan_harness_sample_collection.py --readiness needs-more-real-samples", "\n".join(sample_gap.commands))
        self.assertIn(
            "scripts/plan_harness_sample_collection.py --readiness ready-for-upgrade-discussion",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/plan_harness_sample_collection.py --include-accepted --readiness local-sample-only",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/check_harness_sample_templates.py --capture-gate replace-placeholder-after-real-event",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/check_harness_sample_templates.py --capture-gate requires-approved-bounded-incident",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/check_harness_sample_templates.py --capture-gate requires-security-workflow-event",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/check_harness_sample_templates.py --capture-gate requires-bounded-real-incident",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/check_harness_sample_templates.py --capture-gate requires-workflow-task-event",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/check_harness_sample_templates.py --capture-gate requires-cross-task-resume",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/check_harness_sample_templates.py --capture-gate requires-distinct-task-class-report",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/check_harness_sample_templates.py --capture-gate requires-user-confirmed-high-impact-action",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/check_harness_sample_templates.py --ledger-action review-upgrade-decision",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/check_harness_sample_templates.py --ledger-action append-new-pending-slot",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/check_harness_sample_templates.py --ledger-action fill-existing-placeholder",
            "\n".join(sample_gap.commands),
        )
        self.assertIn("scripts/check_harness_sample_templates.py --readiness needs-first-real-sample", "\n".join(sample_gap.commands))
        self.assertIn("scripts/check_harness_sample_templates.py --readiness needs-more-real-samples", "\n".join(sample_gap.commands))
        self.assertIn(
            "scripts/check_harness_sample_templates.py --readiness ready-for-upgrade-discussion",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/check_harness_sample_templates.py --readiness local-sample-only",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/build_harness_sample_intake_bundle.py "
            "--capture-gate replace-placeholder-after-real-event --summary",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/build_harness_sample_intake_bundle.py "
            "--capture-gate requires-approved-bounded-incident --summary",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/build_harness_sample_intake_bundle.py "
            "--capture-gate requires-security-workflow-event --summary",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/build_harness_sample_intake_bundle.py "
            "--capture-gate requires-bounded-real-incident --summary",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/build_harness_sample_intake_bundle.py "
            "--capture-gate requires-workflow-task-event --summary",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/build_harness_sample_intake_bundle.py "
            "--capture-gate requires-cross-task-resume --summary",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/build_harness_sample_intake_bundle.py "
            "--capture-gate requires-distinct-task-class-report --summary",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/build_harness_sample_intake_bundle.py "
            "--capture-gate requires-user-confirmed-high-impact-action --summary",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/build_harness_sample_intake_bundle.py --readiness needs-first-real-sample --summary",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/build_harness_sample_intake_bundle.py --readiness needs-more-real-samples --summary",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/build_harness_sample_intake_bundle.py --readiness ready-for-upgrade-discussion --summary",
            "\n".join(sample_gap.commands),
        )
        self.assertIn("tests/test_harness_sample_gaps.py", "\n".join(sample_gap.commands))
        self.assertIn("scripts/build_harness_sample_intake_bundle.py", "\n".join(sample_gap.commands))
        self.assertIn("scripts/build_harness_sample_intake_bundle.py --summary", "\n".join(sample_gap.commands))
        self.assertIn(
            "scripts/build_harness_sample_intake_bundle.py --ledger-action define-contract-precondition --summary",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/build_harness_sample_intake_bundle.py --ledger-action review-upgrade-decision --summary",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/build_harness_sample_intake_bundle.py --ledger-action append-new-pending-slot --summary",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/build_harness_sample_intake_bundle.py --ledger-action fill-existing-placeholder --summary",
            "\n".join(sample_gap.commands),
        )
        self.assertIn("scripts/build_harness_sample_intake_bundle.py --json", "\n".join(sample_gap.commands))
        self.assertIn("tests/test_harness_sample_intake_bundle.py", "\n".join(sample_gap.commands))
        self.assertIn("scripts/check_harness_placeholder_replacement.py <candidate-jsonl>", "\n".join(sample_gap.commands))
        self.assertIn("tests/test_harness_placeholder_replacement.py", "\n".join(sample_gap.commands))
        self.assertIn("scripts/check_harness_sample_append.py <candidate-jsonl>", "\n".join(sample_gap.commands))
        self.assertIn("tests/test_harness_sample_append.py", "\n".join(sample_gap.commands))
        self.assertIn("scripts/check_harness_sample_outcome.py <candidate-jsonl>", "\n".join(sample_gap.commands))
        self.assertIn("tests/test_harness_sample_outcome.py", "\n".join(sample_gap.commands))
        self.assertIn(
            "scripts/check_harness_future_work_contract_candidate.py <candidate-jsonl>",
            "\n".join(sample_gap.commands),
        )
        self.assertIn("tests/test_harness_future_work_contract_candidate.py", "\n".join(sample_gap.commands))
        self.assertIn(
            "scripts/check_harness_upgrade_decision_candidate.py <candidate-jsonl>",
            "\n".join(sample_gap.commands),
        )
        self.assertIn("tests/test_harness_upgrade_decision_candidate.py", "\n".join(sample_gap.commands))
        self.assertIn("scripts/check_harness_burn_in_readiness.py", "\n".join(sample_gap.commands))
        self.assertIn("scripts/check_harness_collection_config.py", "\n".join(sample_gap.commands))
        self.assertIn("scripts/check_harness_pending_samples.py", "\n".join(sample_gap.commands))
        self.assertIn("scripts/check_harness_future_work_contracts.py", "\n".join(sample_gap.commands))
        self.assertIn("scripts/check_harness_upgrade_decisions.py", "\n".join(sample_gap.commands))
        self.assertIn("scripts/check_harness_sample_followup_coverage.py", "\n".join(sample_gap.commands))
        self.assertIn("tests/test_harness_sample_followup_coverage.py", "\n".join(sample_gap.commands))

    def test_harness_sample_review_command_change_triggers_intake_and_pending_checks(self) -> None:
        followups = check_change_triggered_followups.build_followups(("scripts/harness_sample_review_commands.py",))
        sample_gap = next(item for item in followups if item.name == "harness-sample-gap-evidence")
        commands = "\n".join(sample_gap.commands)

        self.assertIn("scripts/build_harness_sample_intake_bundle.py", commands)
        self.assertIn("scripts/build_harness_sample_intake_bundle.py --summary", commands)
        self.assertIn("scripts/check_harness_pending_samples.py", commands)
        self.assertIn("tests/test_harness_pending_samples.py", commands)

    def test_harness_placeholder_replacement_change_triggers_placeholder_review_checks(self) -> None:
        followups = check_change_triggered_followups.build_followups(("scripts/check_harness_placeholder_replacement.py",))
        names = {item.name for item in followups}
        sample_gap = next(item for item in followups if item.name == "harness-sample-gap-evidence")
        commands = "\n".join(sample_gap.commands)

        self.assertIn("harness-sample-gap-evidence", names)
        self.assertIn("harness-code-shape", names)
        self.assertIn("scripts/check_harness_placeholder_replacement.py <candidate-jsonl>", commands)
        self.assertIn("tests/test_harness_placeholder_replacement.py", commands)
        self.assertIn("scripts/check_harness_pending_samples.py", commands)

    def test_harness_sample_intake_render_change_triggers_intake_checks(self) -> None:
        followups = check_change_triggered_followups.build_followups(("scripts/harness_sample_intake_render.py",))
        names = {item.name for item in followups}
        sample_gap = next(item for item in followups if item.name == "harness-sample-gap-evidence")
        commands = "\n".join(sample_gap.commands)

        self.assertIn("harness-sample-gap-evidence", names)
        self.assertIn("harness-code-shape", names)
        self.assertIn("scripts/build_harness_sample_intake_bundle.py --summary", commands)
        self.assertIn("scripts/build_harness_sample_intake_bundle.py --json", commands)
        self.assertIn("tests/test_harness_sample_intake_bundle.py", commands)

    def test_harness_collection_lane_command_change_triggers_pending_lane_checks(self) -> None:
        followups = check_change_triggered_followups.build_followups(("scripts/harness_collection_lane_commands.py",))
        names = {item.name for item in followups}
        sample_gap = next(item for item in followups if item.name == "harness-sample-gap-evidence")
        commands = "\n".join(sample_gap.commands)

        self.assertIn("harness-sample-gap-evidence", names)
        self.assertIn("harness-code-shape", names)
        self.assertIn("scripts/check_harness_pending_samples.py", commands)
        self.assertIn("tests/test_harness_pending_samples.py", commands)
        self.assertIn("scripts/build_harness_sample_intake_bundle.py --summary", commands)
        self.assertIn(
            "scripts/build_harness_sample_intake_bundle.py --ledger-action define-contract-precondition --summary",
            commands,
        )
        self.assertIn(
            "scripts/build_harness_sample_intake_bundle.py --ledger-action review-upgrade-decision --summary",
            commands,
        )
        self.assertIn(
            "scripts/build_harness_sample_intake_bundle.py --ledger-action append-new-pending-slot --summary",
            commands,
        )
        self.assertIn(
            "scripts/build_harness_sample_intake_bundle.py --ledger-action fill-existing-placeholder --summary",
            commands,
        )

    def test_harness_collection_config_change_triggers_planner_checks(self) -> None:
        followups = check_change_triggered_followups.build_followups(("scripts/harness_sample_collection_config.py",))
        names = {item.name for item in followups}
        sample_gap = next(item for item in followups if item.name == "harness-sample-gap-evidence")
        commands = "\n".join(sample_gap.commands)

        self.assertIn("harness-sample-gap-evidence", names)
        self.assertIn("harness-code-shape", names)
        self.assertIn("scripts/plan_harness_sample_collection.py", commands)
        self.assertIn("tests/test_plan_harness_sample_collection.py", commands)
        self.assertIn("scripts/check_harness_sample_templates.py", commands)
        self.assertIn("scripts/check_harness_collection_config.py", commands)

    def test_harness_collection_items_change_triggers_planner_checks(self) -> None:
        followups = check_change_triggered_followups.build_followups(("scripts/harness_sample_collection_items.py",))
        names = {item.name for item in followups}
        sample_gap = next(item for item in followups if item.name == "harness-sample-gap-evidence")
        commands = "\n".join(sample_gap.commands)

        self.assertIn("harness-sample-gap-evidence", names)
        self.assertIn("harness-code-shape", names)
        self.assertIn("scripts/plan_harness_sample_collection.py", commands)
        self.assertIn("tests/test_plan_harness_sample_collection.py", commands)
        self.assertIn("scripts/check_harness_sample_templates.py", commands)

    def test_harness_capture_gate_helper_change_triggers_planner_checks(self) -> None:
        followups = check_change_triggered_followups.build_followups(("scripts/harness_sample_capture_gates.py",))
        names = {item.name for item in followups}
        sample_gap = next(item for item in followups if item.name == "harness-sample-gap-evidence")
        commands = "\n".join(sample_gap.commands)

        self.assertIn("harness-sample-gap-evidence", names)
        self.assertIn("harness-code-shape", names)
        self.assertIn("scripts/plan_harness_sample_collection.py", commands)
        self.assertIn("scripts/check_harness_burn_in_readiness.py", commands)
        self.assertIn("tests/test_harness_burn_in_readiness.py", commands)

    def test_harness_readiness_render_change_triggers_readiness_checks(self) -> None:
        followups = check_change_triggered_followups.build_followups(("scripts/harness_burn_in_readiness_render.py",))
        names = {item.name for item in followups}
        sample_gap = next(item for item in followups if item.name == "harness-sample-gap-evidence")
        commands = "\n".join(sample_gap.commands)

        self.assertIn("harness-sample-gap-evidence", names)
        self.assertIn("harness-code-shape", names)
        self.assertIn("scripts/check_harness_burn_in_readiness.py", commands)
        self.assertIn("tests/test_harness_burn_in_readiness.py", commands)

    def test_harness_readiness_type_change_triggers_readiness_checks(self) -> None:
        followups = check_change_triggered_followups.build_followups(("scripts/harness_burn_in_readiness_types.py",))
        names = {item.name for item in followups}
        sample_gap = next(item for item in followups if item.name == "harness-sample-gap-evidence")
        commands = "\n".join(sample_gap.commands)

        self.assertIn("harness-sample-gap-evidence", names)
        self.assertIn("harness-code-shape", names)
        self.assertIn("scripts/check_harness_burn_in_readiness.py", commands)
        self.assertIn("scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --readiness", commands)
        self.assertIn(
            "scripts/check_harness_burn_in_readiness.py --include-future --include-accepted "
            "--readiness needs-more-real-samples",
            commands,
        )
        self.assertIn(
            "scripts/check_harness_burn_in_readiness.py --include-future --include-accepted "
            "--readiness ready-for-upgrade-discussion",
            commands,
        )
        self.assertIn("tests/test_harness_burn_in_readiness.py", commands)

    def test_harness_readiness_delta_change_triggers_readiness_checks(self) -> None:
        followups = check_change_triggered_followups.build_followups(("scripts/harness_burn_in_readiness_deltas.py",))
        names = {item.name for item in followups}
        sample_gap = next(item for item in followups if item.name == "harness-sample-gap-evidence")
        commands = "\n".join(sample_gap.commands)

        self.assertIn("harness-sample-gap-evidence", names)
        self.assertIn("harness-code-shape", names)
        self.assertIn("scripts/check_harness_burn_in_readiness.py", commands)
        self.assertIn("tests/test_harness_burn_in_readiness.py", commands)

    def test_harness_readiness_cli_change_triggers_readiness_checks(self) -> None:
        followups = check_change_triggered_followups.build_followups(("scripts/harness_burn_in_readiness_cli.py",))
        names = {item.name for item in followups}
        sample_gap = next(item for item in followups if item.name == "harness-sample-gap-evidence")
        commands = "\n".join(sample_gap.commands)

        self.assertIn("harness-sample-gap-evidence", names)
        self.assertIn("harness-code-shape", names)
        self.assertIn("scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --area", commands)
        self.assertIn("scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --priority", commands)
        self.assertIn("scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --readiness", commands)
        self.assertIn(
            "scripts/check_harness_burn_in_readiness.py --include-future --include-accepted "
            "--readiness needs-more-real-samples",
            commands,
        )
        self.assertIn(
            "scripts/check_harness_burn_in_readiness.py --include-future --include-accepted "
            "--readiness ready-for-upgrade-discussion",
            commands,
        )
        self.assertIn("tests/test_harness_burn_in_readiness.py", commands)

    def test_harness_readiness_filter_change_triggers_readiness_checks(self) -> None:
        followups = check_change_triggered_followups.build_followups(("scripts/harness_burn_in_readiness_filters.py",))
        names = {item.name for item in followups}
        sample_gap = next(item for item in followups if item.name == "harness-sample-gap-evidence")
        commands = "\n".join(sample_gap.commands)

        self.assertIn("harness-sample-gap-evidence", names)
        self.assertIn("harness-code-shape", names)
        self.assertIn("scripts/check_harness_burn_in_readiness.py", commands)
        self.assertIn("scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --area", commands)
        self.assertIn("scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --priority", commands)
        self.assertIn("scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --gap-id", commands)
        self.assertIn("scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --capture-gate", commands)
        self.assertIn(
            "scripts/check_harness_burn_in_readiness.py --include-future --include-accepted "
            "--capture-gate upgrade-decision-review",
            commands,
        )
        self.assertIn("scripts/check_harness_burn_in_readiness.py --include-future --include-accepted --readiness", commands)
        self.assertIn("tests/test_harness_burn_in_readiness.py", commands)

    def test_harness_collection_render_change_triggers_planner_checks(self) -> None:
        followups = check_change_triggered_followups.build_followups(("scripts/harness_sample_collection_render.py",))
        names = {item.name for item in followups}
        sample_gap = next(item for item in followups if item.name == "harness-sample-gap-evidence")
        commands = "\n".join(sample_gap.commands)

        self.assertIn("harness-sample-gap-evidence", names)
        self.assertIn("harness-code-shape", names)
        self.assertIn("scripts/plan_harness_sample_collection.py", commands)
        self.assertIn("tests/test_plan_harness_sample_collection.py", commands)
        self.assertIn("scripts/check_harness_pending_samples.py", commands)

    def test_harness_gap_collector_change_triggers_collector_checks(self) -> None:
        followups = check_change_triggered_followups.build_followups(("scripts/collect_harness_sample_gaps.py",))
        names = {item.name for item in followups}
        sample_gap = next(item for item in followups if item.name == "harness-sample-gap-evidence")
        commands = "\n".join(sample_gap.commands)

        self.assertIn("harness-sample-gap-evidence", names)
        self.assertIn("harness-code-shape", names)
        self.assertIn("scripts/collect_harness_sample_gaps.py", commands)
        self.assertIn("tests/test_harness_sample_gaps.py", commands)

    def test_harness_followup_rule_helper_change_triggers_sample_gap_checks(self) -> None:
        followups = check_change_triggered_followups.build_followups(("scripts/change_triggered_harness_sample_rules.py",))
        names = {item.name for item in followups}
        sample_gap = next(item for item in followups if item.name == "harness-sample-gap-evidence")

        self.assertIn("harness-sample-gap-evidence", names)
        self.assertIn("harness-code-shape", names)
        self.assertIn("scripts/check_harness_pending_samples.py", "\n".join(sample_gap.commands))
        self.assertIn("scripts/check_harness_pending_samples.py --capture-focus", "\n".join(sample_gap.commands))
        self.assertIn(
            "scripts/check_harness_pending_samples.py --capture-focus --capture-focus-limit 0",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/check_harness_pending_samples.py --capture-focus --capture-focus-area agentic-red-team",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/check_harness_pending_samples.py --capture-focus --capture-focus-priority P2",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/check_harness_pending_samples.py --capture-focus --capture-focus-ledger-action fill-existing-placeholder",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/check_harness_pending_samples.py --capture-focus --capture-focus-ledger-action "
            "append-new-pending-slot --capture-focus-limit 0",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/check_harness_pending_samples.py --capture-focus --capture-focus-ledger-action "
            "fill-existing-placeholder --capture-focus-limit 0",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-gate replace-placeholder-after-real-event",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-gate requires-approved-bounded-incident",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-gate requires-security-workflow-event",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-gate requires-bounded-real-incident",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-gate requires-workflow-task-event",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-gate requires-cross-task-resume",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-gate requires-distinct-task-class-report",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/check_harness_pending_samples.py --capture-focus "
            "--capture-focus-gate requires-user-confirmed-high-impact-action",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/check_harness_pending_samples.py --capture-focus --capture-focus-readiness needs-first-real-sample",
            "\n".join(sample_gap.commands),
        )
        self.assertIn(
            "scripts/check_harness_pending_samples.py --capture-focus --capture-focus-readiness needs-more-real-samples",
            "\n".join(sample_gap.commands),
        )
        self.assertIn("scripts/check_harness_sample_followup_coverage.py", "\n".join(sample_gap.commands))
        self.assertIn("scripts/check_harness_sample_append.py", "\n".join(sample_gap.commands))
        self.assertIn("scripts/check_harness_sample_outcome.py", "\n".join(sample_gap.commands))

    def test_evidence_ref_helper_change_triggers_sample_gap_checks(self) -> None:
        followups = check_change_triggered_followups.build_followups(("scripts/evidence_ref_utils.py",))
        names = {item.name for item in followups}
        sample_gap = next(item for item in followups if item.name == "harness-sample-gap-evidence")
        commands = "\n".join(sample_gap.commands)

        self.assertIn("harness-sample-gap-evidence", names)
        self.assertIn("agentic-red-team-samples", names)
        self.assertIn("local-trace-summary-samples", names)
        self.assertIn("loop-scope-monitor-samples", names)
        self.assertIn("pre-tool-use-preflight-samples", names)
        self.assertIn("stage-checkpoints", names)
        self.assertIn("task-profile-audit", names)
        self.assertIn("harness-upgrade-decisions", names)
        self.assertIn("check-burn-in-ledger", names)
        self.assertIn("check-burn-in-upgrade-decisions", names)
        self.assertIn("harness-code-shape", names)
        self.assertIn("scripts/check_harness_sample_gap_evidence.py", commands)
        self.assertIn("python3 tests/test_harness_sample_gap_evidence.py", commands)

    def test_harness_sample_append_change_triggers_append_review_checks(self) -> None:
        followups = check_change_triggered_followups.build_followups(("scripts/check_harness_sample_append.py",))
        names = {item.name for item in followups}
        sample_gap = next(item for item in followups if item.name == "harness-sample-gap-evidence")
        commands = "\n".join(sample_gap.commands)

        self.assertIn("harness-sample-gap-evidence", names)
        self.assertIn("harness-code-shape", names)
        self.assertIn("scripts/check_harness_sample_append.py <candidate-jsonl>", commands)
        self.assertIn("tests/test_harness_sample_append.py", commands)
        self.assertIn("scripts/check_harness_pending_samples.py", commands)

    def test_harness_sample_review_context_change_triggers_review_checks(self) -> None:
        followups = check_change_triggered_followups.build_followups(("scripts/harness_sample_review_context.py",))
        names = {item.name for item in followups}
        sample_gap = next(item for item in followups if item.name == "harness-sample-gap-evidence")
        commands = "\n".join(sample_gap.commands)

        self.assertIn("harness-sample-gap-evidence", names)
        self.assertIn("harness-code-shape", names)
        self.assertIn("scripts/check_harness_placeholder_replacement.py <candidate-jsonl>", commands)
        self.assertIn("scripts/check_harness_sample_append.py <candidate-jsonl>", commands)
        self.assertIn("tests/test_harness_placeholder_replacement.py", commands)
        self.assertIn("tests/test_harness_sample_append.py", commands)

    def test_harness_sample_outcome_change_triggers_outcome_review_checks(self) -> None:
        followups = check_change_triggered_followups.build_followups(
            (
                "scripts/check_harness_sample_outcome.py",
                "scripts/harness_sample_outcome_context.py",
                "scripts/harness_sample_outcome_validation.py",
            )
        )
        names = {item.name for item in followups}
        sample_gap = next(item for item in followups if item.name == "harness-sample-gap-evidence")
        commands = "\n".join(sample_gap.commands)

        self.assertIn("harness-sample-gap-evidence", names)
        self.assertIn("harness-code-shape", names)
        self.assertIn("scripts/check_harness_sample_outcome.py <candidate-jsonl>", commands)
        self.assertIn("tests/test_harness_sample_outcome.py", commands)
        self.assertIn("scripts/check_harness_pending_samples.py", commands)

    def test_harness_sample_followup_coverage_change_triggers_sample_gap_checks(self) -> None:
        followups = check_change_triggered_followups.build_followups(
            ("scripts/check_harness_sample_followup_coverage.py",)
        )
        names = {item.name for item in followups}
        sample_gap = next(item for item in followups if item.name == "harness-sample-gap-evidence")
        commands = "\n".join(sample_gap.commands)

        self.assertIn("harness-sample-gap-evidence", names)
        self.assertIn("harness-code-shape", names)
        self.assertIn("scripts/check_harness_sample_followup_coverage.py", commands)
        self.assertIn("tests/test_harness_sample_followup_coverage.py", commands)

    def test_harness_sample_slot_inventory_change_triggers_sample_checks(self) -> None:
        names = self.followup_names("scripts/harness_sample_slots.py")

        self.assertIn("harness-sample-gap-evidence", names)
        self.assertIn("harness-code-shape", names)

    def test_harness_sample_pending_summary_change_triggers_sample_checks(self) -> None:
        names = self.followup_names("scripts/harness_sample_pending_summaries.py")

        self.assertIn("harness-sample-gap-evidence", names)
        self.assertIn("harness-code-shape", names)

    def test_harness_pending_sample_report_change_triggers_sample_checks(self) -> None:
        names = self.followup_names("scripts/harness_pending_sample_report.py")

        self.assertIn("harness-sample-gap-evidence", names)
        self.assertIn("harness-code-shape", names)

    def test_harness_pending_readiness_metric_helper_change_triggers_sample_checks(self) -> None:
        names = self.followup_names("scripts/harness_pending_readiness_metrics.py")

        self.assertIn("harness-sample-gap-evidence", names)
        self.assertIn("harness-code-shape", names)

    def test_harness_pending_review_card_helper_change_triggers_sample_checks(self) -> None:
        names = self.followup_names("scripts/harness_pending_review_cards.py")

        self.assertIn("harness-sample-gap-evidence", names)
        self.assertIn("harness-code-shape", names)

    def test_harness_pending_capture_focus_change_triggers_sample_checks(self) -> None:
        names = self.followup_names("scripts/harness_pending_capture_focus.py")

        self.assertIn("harness-sample-gap-evidence", names)
        self.assertIn("harness-code-shape", names)

    def test_harness_pending_capture_focus_helper_changes_trigger_sample_checks(self) -> None:
        for path in (
            "scripts/harness_pending_capture_focus_filters.py",
            "scripts/harness_pending_capture_focus_render.py",
            "scripts/harness_pending_capture_focus_slots.py",
        ):
            with self.subTest(path=path):
                names = self.followup_names(path)

                self.assertIn("harness-sample-gap-evidence", names)
                self.assertIn("harness-code-shape", names)

    def test_tool_contract_change_triggers_contract_check(self) -> None:
        names = self.followup_names("docs/ai/tool-contracts/contracts.json")

        self.assertIn("governance-surface", names)
        self.assertIn("tool-contract-registry", names)

    def test_check_burn_in_ledger_change_triggers_ledger_check(self) -> None:
        followups = check_change_triggered_followups.build_followups(("docs/ai/check-burn-in-ledger.md",))
        names = {item.name for item in followups}
        ledger = next(item for item in followups if item.name == "check-burn-in-ledger")

        self.assertIn("governance-surface", names)
        self.assertIn("check-burn-in-ledger", names)
        self.assertIn("governance job validates ledger coverage", ledger.ci_coverage)

    def test_check_burn_in_script_change_triggers_ledger_and_shape(self) -> None:
        names = self.followup_names("scripts/check_burn_in_ledger.py")

        self.assertIn("check-burn-in-ledger", names)
        self.assertIn("harness-code-shape", names)

    def test_check_burn_in_upgrade_decision_change_triggers_decision_check(self) -> None:
        followups = check_change_triggered_followups.build_followups(
            ("docs/ai/standards/check-burn-in-upgrade-decisions.jsonl",)
        )
        names = {item.name for item in followups}
        decision = next(item for item in followups if item.name == "check-burn-in-upgrade-decisions")

        self.assertIn("governance-surface", names)
        self.assertIn("check-burn-in-upgrade-decisions", names)
        self.assertIn("governance job validates check-level upgrade decision coverage", decision.ci_coverage)

    def test_check_burn_in_upgrade_decision_script_change_triggers_decision_and_shape(self) -> None:
        names = self.followup_names("scripts/check_burn_in_upgrade_decisions.py")

        self.assertIn("check-burn-in-upgrade-decisions", names)
        self.assertIn("harness-code-shape", names)

    def test_task_profile_audit_change_triggers_profile_check(self) -> None:
        names = self.followup_names("docs/ai/standards/task-profile-audit-sample.jsonl")

        self.assertIn("governance-surface", names)
        self.assertIn("task-profile-audit", names)

    def test_harness_upgrade_decision_change_triggers_decision_check(self) -> None:
        followups = check_change_triggered_followups.build_followups(
            ("docs/ai/standards/harness-upgrade-decisions.jsonl",)
        )
        names = {item.name for item in followups}
        upgrade = next(item for item in followups if item.name == "harness-upgrade-decisions")

        self.assertIn("governance-surface", names)
        self.assertIn("harness-upgrade-decisions", names)
        self.assertIn("scripts/check_harness_upgrade_decisions.py", "\n".join(upgrade.commands))

    def test_profile_followup_rule_helper_change_triggers_profile_and_upgrade_checks(self) -> None:
        names = self.followup_names("scripts/change_triggered_profile_rules.py")

        self.assertIn("task-profile-audit", names)
        self.assertIn("harness-upgrade-decisions", names)
        self.assertIn("high-impact-agent-actions", names)
        self.assertIn("harness-code-shape", names)

    def test_starter_change_triggers_starter_sync(self) -> None:
        names = self.followup_names("new_pro_standard/AGENTS.md")

        self.assertIn("starter-sync", names)

    def test_normalize_preserves_dot_directories(self) -> None:
        self.assertEqual(
            check_change_triggered_followups.normalize(".github/workflows/main.yml"),
            ".github/workflows/main.yml",
        )
        self.assertEqual(
            check_change_triggered_followups.normalize("./.agents/skills/demo/SKILL.md"),
            ".agents/skills/demo/SKILL.md",
        )

    def test_parse_status_line_preserves_first_path_character(self) -> None:
        self.assertEqual(
            check_change_triggered_followups.parse_status_line(" M AGENTS.md"),
            "AGENTS.md",
        )
        self.assertEqual(
            check_change_triggered_followups.parse_status_line("?? .github/pull_request_template.md"),
            ".github/pull_request_template.md",
        )

    def test_markdown_summary_lists_followups(self) -> None:
        output = self.markdown_for(".github/workflows/governance-and-smoke.yml")

        self.assertIn("### Change-triggered follow-up suggestions", output)
        self.assertIn("| Follow-up | Level | CI coverage | Reason | Matched files | Commands | References |", output)
        self.assertIn("`github-guardrails`", output)
        self.assertIn("`blocking-candidate`", output)
        self.assertIn("remote enforcement may be UNKNOWN", output)
        self.assertIn("scripts/check_github_guardrails.py", output)
        self.assertIn("python-linter", output)
        self.assertIn("ruff check .codex/hooks scripts tests", output)
        self.assertIn("`harness-sample-gap-evidence`", output)
        self.assertIn("tests/test_governance_workflow_sample_outputs.py", output)
        self.assertIn("Advisory only", output)

    def test_json_payload_includes_registry_fields(self) -> None:
        followup = check_change_triggered_followups.build_followups(("docs/ai/index.md",))[0]

        self.assertEqual(followup.level, "blocking-candidate")
        self.assertIn("governance", followup.ci_coverage)

    def test_supply_chain_rule_is_advisory(self) -> None:
        followups = check_change_triggered_followups.build_followups(("docs/ai/security/demo.md",))
        supply_chain = next(item for item in followups if item.name == "supply-chain-evidence")

        self.assertEqual(supply_chain.level, "advisory")
        self.assertIn("not a required check", supply_chain.ci_coverage)

    def test_agent_action_matrix_triggers_review_required_followup(self) -> None:
        names = self.followup_names("docs/ai/security/agent-action-guardrails.md")

        self.assertIn("governance-surface", names)
        self.assertIn("supply-chain-evidence", names)
        self.assertIn("high-impact-agent-actions", names)

    def test_high_impact_followup_is_review_required_and_advisory(self) -> None:
        followups = check_change_triggered_followups.build_followups((".github/workflows/governance-and-smoke.yml",))
        high_impact = next(item for item in followups if item.name == "high-impact-agent-actions")

        self.assertEqual(high_impact.level, "review-required")
        self.assertIn("explicit user confirmation", high_impact.ci_coverage)

    def test_markdown_summary_handles_no_followups(self) -> None:
        output = self.markdown_for("README.md")

        self.assertIn("- Changed files: 1", output)
        self.assertIn("No specialized follow-up checks suggested.", output)
        self.assertIn("Advisory only", output)


if __name__ == "__main__":
    unittest.main()
