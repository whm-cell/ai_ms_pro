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
    def test_default_queue_uses_empty_ledger_review_gate(self) -> None:
        items = plan_harness_sample_collection.build_queue()
        by_id = {item.gap_id: item for item in items}

        self.assertIn("GAP-STARTER-HIGH-IMPACT-ACTION", by_id)
        self.assertNotIn("GAP-STARTER-REMOTE-INTEROP", by_id)
        self.assertEqual("P0", by_id["GAP-STARTER-HIGH-IMPACT-ACTION"].priority)
        self.assertEqual(
            "docs/ai/standards/harness-sample-gap-evidence.jsonl",
            by_id["GAP-STARTER-HIGH-IMPACT-ACTION"].target_artifact,
        )
        self.assertIn("check_harness_sample_gap_evidence.py", by_id["GAP-STARTER-HIGH-IMPACT-ACTION"].review_command)
        self.assertIn("Do not use synthetic fixtures", by_id["GAP-STARTER-HIGH-IMPACT-ACTION"].boundary)

    def test_include_future_keeps_remote_interop_contract_boundary(self) -> None:
        items = plan_harness_sample_collection.build_queue(include_future=True)
        by_id = {item.gap_id: item for item in items}

        remote = by_id["GAP-STARTER-REMOTE-INTEROP"]
        self.assertEqual("future-work", remote.status)
        self.assertEqual("requires-project-adr-or-contract", remote.capture_gate)
        self.assertIn("ADR or contract", remote.boundary)

    def test_gap_id_filter_limits_queue(self) -> None:
        items = plan_harness_sample_collection.build_queue(gap_ids={"GAP-STARTER-WORKFLOW-SKILL"})

        self.assertEqual(["GAP-STARTER-WORKFLOW-SKILL"], [item.gap_id for item in items])

    def test_sample_template_emits_pending_not_accepted_rows(self) -> None:
        item = plan_harness_sample_collection.build_queue(gap_ids={"GAP-STARTER-HIGH-IMPACT-ACTION"})[0]

        with mock.patch("sys.stdout", new=StringIO()) as output:
            plan_harness_sample_collection.emit_templates([item])

        payload = json.loads(output.getvalue())
        self.assertEqual("pending", payload["outcome"])
        self.assertEqual("GAP-STARTER-HIGH-IMPACT-ACTION", payload["gap_id"])
        self.assertTrue(payload["no_external_claim"])
        self.assertEqual(["docs/ai/templates/harness-sample-gap-evidence-record.md"], payload["evidence_refs"])

    def test_empty_filtered_markdown_is_successful_and_explicit(self) -> None:
        with mock.patch("sys.stdout", new=StringIO()) as output:
            plan_harness_sample_collection.emit_markdown([])

        self.assertIn("No sample gaps matched", output.getvalue())


if __name__ == "__main__":
    unittest.main()
