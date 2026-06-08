from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_external_harness_decisions  # noqa: E402


class ExternalHarnessDecisionValidationTest(unittest.TestCase):
    def test_repository_records_are_valid(self) -> None:
        report = check_external_harness_decisions.build_report()

        self.assertEqual(report.errors, [])
        self.assertEqual(
            set(report.active_areas),
            {"remote-trace-pilot", "external-eval-sandbox", "mcp-a2a", "ci-agent-workflow"},
        )
        self.assertIn("check_tool_contracts", report.referenced_tool_contracts)
        self.assertGreaterEqual(report.source_evidence_count, 4)
        self.assertIn("source-backed-decision-ledger", report.local_upgrade_scopes)
        self.assertEqual(report.default_permission_count, 4)
        self.assertTrue(
            any("bounded local" in scope.lower() for scope in report.default_permission_scopes)
        )

    def test_requires_all_no_claim_boundaries(self) -> None:
        record = valid_record()
        record["claim_boundaries"]["no_native_sandbox_claim"] = False

        report = report_for_records([record])

        self.assertTrue(any("no_native_sandbox_claim must be true" in error for error in report.errors))

    def test_rejects_unknown_tool_contract(self) -> None:
        record = valid_record(tool_contracts=["missing_tool_contract"])

        report = report_for_records([record])

        self.assertTrue(any("unknown tool contract missing_tool_contract" in error for error in report.errors))

    def test_rejects_raw_runtime_evidence_ref(self) -> None:
        record = valid_record(evidence_refs=[".codex/runtime/sessions/example.md"])

        report = report_for_records([record])

        self.assertTrue(any("raw runtime artifacts" in error for error in report.errors))

    def test_requires_all_active_decision_areas(self) -> None:
        report = report_for_records([valid_record()])

        self.assertTrue(any("missing active decision areas" in error for error in report.errors))

    def test_requires_source_evidence(self) -> None:
        record = valid_record()
        record.pop("source_evidence")

        report = report_for_records([record])

        self.assertTrue(any("source_evidence must be a non-empty list" in error for error in report.errors))

    def test_requires_https_source_url(self) -> None:
        record = valid_record(
            source_evidence=[
                {
                    "source_type": "official-doc",
                    "source_date": "2026-06-07 accessed",
                    "url": "http://example.test/source",
                    "positive_signal": True,
                    "finding": "Source describes relevant agent harness behavior.",
                    "local_upgrade_scope": "source-backed-decision-ledger",
                }
            ]
        )

        report = report_for_records([record])

        self.assertTrue(any("url must start with https://" in error for error in report.errors))

    def test_active_records_require_default_permission(self) -> None:
        record = valid_record()
        record.pop("default_permission")

        report = report_for_records([record])

        self.assertTrue(any("active records must include default_permission" in error for error in report.errors))

    def test_default_permission_must_keep_external_effects_blocked(self) -> None:
        record = valid_record()
        permission = record["default_permission"]
        assert isinstance(permission, dict)
        permission["blocked_scope"] = ["native sandbox claim"]

        report = report_for_records([record])

        self.assertTrue(any("hosted trace/eval claim" in error for error in report.errors))


def report_for_records(records: list[dict[str, object]]) -> check_external_harness_decisions.DecisionReport:
    with tempfile.TemporaryDirectory() as temp_dir:
        path = Path(temp_dir) / "records.jsonl"
        path.write_text("\n".join(to_json(record) for record in records) + "\n", encoding="utf-8")
        return check_external_harness_decisions.build_report(path, check_external_harness_decisions.DEFAULT_CONTRACTS)


def to_json(record: dict[str, object]) -> str:
    import json

    return json.dumps(record, separators=(",", ":"))


def valid_record(**overrides: object) -> dict[str, object]:
    record: dict[str, object] = {
        "schema_version": "external-harness-decision/v1",
        "id": "EHD-TEST-remote-trace",
        "recorded_at": "2026-06-07",
        "decision_area": "remote-trace-pilot",
        "decision": "defer-external-send-pending-endpoint",
        "status": "active",
        "requirement_ids": ["unbound"],
        "workstream_ids": ["unbound"],
        "rationale": "No external endpoint is configured for this test record.",
        "bounded_next_action": "Keep local shape validation only.",
        "activation_gates": ["explicit endpoint", "operator review"],
        "claim_boundaries": {
            "no_hosted_trace_or_eval_claim": True,
            "no_verified_remote_claim_without_operator_review": True,
            "no_native_sandbox_claim": True,
            "no_mcp_a2a_runtime_claim": True,
            "no_real_ci_agent_workflow_claim": True,
            "no_external_effect_without_explicit_confirmation": True,
        },
        "tool_contracts": ["check_tool_contracts"],
        "evidence_refs": ["docs/ai/tool-contracts/contracts.json"],
        "source_evidence": [
            {
                "source_type": "official-doc",
                "source_date": "2026-06-07 accessed",
                "url": "https://example.test/source",
                "positive_signal": True,
                "finding": "Source describes relevant agent harness behavior.",
                "local_upgrade_scope": "source-backed-decision-ledger",
            }
        ],
        "default_permission": {
            "policy": "evidence-backed-default-permit",
            "positive_for_current_harness": True,
            "evidence_grade": "first-party-source-backed",
            "permitted_scope": ["Bounded local decision quality improvements."],
            "blocked_scope": [
                "Hosted trace/eval claim remains blocked.",
                "Verified remote claim without operator review remains blocked.",
                "Native sandbox claim remains blocked.",
                "MCP/A2A runtime claim remains blocked.",
                "Real CI agent workflow remains blocked.",
                "External effect without explicit confirmation remains blocked.",
            ],
            "evidence_threshold": ["First-party source evidence with positive_signal=true."],
            "verification_commands": [
                ".codex/hooks/run_with_repo_python.sh scripts/check_external_harness_decisions.py"
            ],
        },
    }
    record.update(overrides)
    return record


if __name__ == "__main__":
    unittest.main()
