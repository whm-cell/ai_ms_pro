from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_agent_productization_readiness as readiness  # noqa: E402


class AgentProductizationReadinessTest(unittest.TestCase):
    def test_repository_records_are_valid_but_review_required(self) -> None:
        report = readiness.build_report()

        self.assertEqual(report.errors, [])
        self.assertEqual(report.capability_count, 12)
        self.assertIn("ai-ms-pro-harness-control-plane", report.targets)
        self.assertIn("APR-01", report.mvp_capabilities)
        self.assertIn("APR-12", report.mature_capabilities)
        self.assertGreaterEqual(len(report.review_findings), 1)
        self.assertEqual(report.status_counts.get("covered"), 1)
        self.assertEqual(report.status_counts.get("deferred"), 1)

    def test_rejects_missing_assessment_for_capability(self) -> None:
        model = {
            "schema_version": "agent-productization-readiness/v1",
            "id": "demo",
            "updated_at": "2026-06-12",
            "status": "review-required",
            "claim_boundary": {
                "review_required_only": True,
                "no_product_agent_platform_claim": True,
                "no_hosted_runtime_claim": True,
                "no_external_effect_claim": True,
                "no_blocking_upgrade_without_real_samples": True,
            },
            "capabilities": [capability("APR-01"), capability("APR-02")],
        }
        assessment_rows = [assessment("APR-01")]

        report = report_for(model, assessment_rows)

        self.assertTrue(any("missing assessment rows for APR-02" in error for error in report.errors))

    def test_rejects_raw_runtime_evidence_refs(self) -> None:
        model = valid_model()
        record = assessment("APR-01")
        record["evidence_refs"] = [".codex/runtime/sessions/example.md"]

        report = report_for(model, [record])

        self.assertTrue(any("raw runtime artifacts" in error for error in report.errors))

    def test_rejects_unknown_capability_id(self) -> None:
        model = valid_model()
        record = assessment("APR-99")

        report = report_for(model, [record])

        self.assertTrue(any("unknown capability id" in error for error in report.errors))


def report_for(
    model: dict[str, object],
    assessments: list[dict[str, object]],
) -> readiness.ReadinessReport:
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        model_path = temp_path / "model.json"
        assessment_path = temp_path / "assessment.jsonl"
        model_path.write_text(json.dumps(model), encoding="utf-8")
        assessment_path.write_text(
            "\n".join(json.dumps(record, separators=(",", ":")) for record in assessments) + "\n",
            encoding="utf-8",
        )
        return readiness.build_report(model_path, assessment_path)


def valid_model() -> dict[str, object]:
    return {
        "schema_version": "agent-productization-readiness/v1",
        "id": "demo",
        "updated_at": "2026-06-12",
        "status": "review-required",
        "claim_boundary": {
            "review_required_only": True,
            "no_product_agent_platform_claim": True,
            "no_hosted_runtime_claim": True,
            "no_external_effect_claim": True,
            "no_blocking_upgrade_without_real_samples": True,
        },
        "capabilities": [capability("APR-01")],
    }


def capability(capability_id: str) -> dict[str, object]:
    return {
        "id": capability_id,
        "slug": "demo-capability",
        "name": "Demo Capability",
        "mvp_required": True,
        "mature_required": True,
        "why": "This capability demonstrates the model shape.",
        "acceptance_signals": ["Signal exists."],
        "recommended_surfaces": ["docs/ai/check-registry.md"],
        "source_basis": ["unit test"],
        "level": "review-required",
    }


def assessment(capability_id: str) -> dict[str, object]:
    return {
        "schema_version": "agent-productization-assessment/v1",
        "target_id": "demo-agent",
        "target_type": "unit-test-target",
        "assessed_at": "2026-06-12",
        "capability_id": capability_id,
        "status": "partial",
        "evidence_refs": ["docs/ai/check-registry.md"],
        "current_evidence": "The unit test has bounded evidence.",
        "gap": "The demo target remains partial.",
        "next_action": "Keep the readiness row review-required.",
        "claim_boundary": {
            "local_first": True,
            "no_product_agent_platform_claim": True,
            "no_hosted_runtime_claim": True,
        },
    }


if __name__ == "__main__":
    unittest.main()
