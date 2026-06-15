from __future__ import annotations

import json
import sys
import unittest
from io import StringIO
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import plan_harness_sample_collection  # noqa: E402


class HarnessSampleCollectionPlanTest(unittest.TestCase):
    def test_default_queue_uses_empty_generic_ledger_review_gate(self) -> None:
        items = plan_harness_sample_collection.build_queue()
        by_id = {item.gap_id: item for item in items}

        self.assertIn("GAP-GUARDRAIL-CONFIRMATION", by_id)
        self.assertNotIn("GAP-TRACE-REMOTE-INTEROP", by_id)
        self.assertEqual("P1", by_id["GAP-GUARDRAIL-CONFIRMATION"].priority)
        self.assertEqual(
            "docs/ai/standards/harness-sample-gap-evidence.jsonl",
            by_id["GAP-GUARDRAIL-CONFIRMATION"].target_artifact,
        )
        self.assertIn("check_harness_sample_gap_evidence.py", by_id["GAP-GUARDRAIL-CONFIRMATION"].review_command)
        self.assertIn("Bounded evidence only", by_id["GAP-GUARDRAIL-CONFIRMATION"].boundary)

    def test_include_future_keeps_remote_interop_contract_boundary(self) -> None:
        items = plan_harness_sample_collection.build_queue(include_future=True)
        by_id = {item.gap_id: item for item in items}

        remote = by_id["GAP-TRACE-REMOTE-INTEROP"]
        self.assertEqual("needs-contract-or-adr-first", remote.readiness)
        self.assertEqual("contract-precondition-first", remote.capture_gate)
        self.assertEqual("define-contract-precondition", remote.ledger_action)
        self.assertIn("Future-work contract precondition", remote.boundary)

    def test_gap_id_filter_limits_queue(self) -> None:
        items = plan_harness_sample_collection.build_queue(gap_ids={"GAP-WORKFLOW-CROSS-WS"})

        self.assertEqual(["GAP-WORKFLOW-CROSS-WS"], [item.gap_id for item in items])

    def test_sample_template_emits_pending_not_accepted_rows(self) -> None:
        item = plan_harness_sample_collection.build_queue(gap_ids={"GAP-GUARDRAIL-CONFIRMATION"})[0]

        with mock.patch("sys.stdout", new=StringIO()) as output:
            plan_harness_sample_collection.emit_sample_templates([item])

        payload = json.loads(output.getvalue())
        self.assertEqual("pending", payload["outcome"])
        self.assertEqual("GAP-GUARDRAIL-CONFIRMATION", payload["gap_id"])
        self.assertTrue(payload["no_external_claim"])
        self.assertEqual(["docs/ai/standards/harness-sample-gap-evidence.md"], payload["evidence_refs"])

    def test_empty_filtered_markdown_is_successful_and_explicit(self) -> None:
        with mock.patch("sys.stdout", new=StringIO()) as output:
            plan_harness_sample_collection.emit_markdown([])

        self.assertIn("No harness sample collection items matched", output.getvalue())


if __name__ == "__main__":
    unittest.main()
