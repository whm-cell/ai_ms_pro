from __future__ import annotations

import sys
import unittest
from io import StringIO
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import collect_harness_sample_gaps  # noqa: E402


class HarnessSampleGapsTest(unittest.TestCase):
    def test_generic_gap_catalog_is_template_scoped(self) -> None:
        gap_ids = {gap.id for gap in collect_harness_sample_gaps.GAPS}

        self.assertIn("GAP-GUARDRAIL-CONFIRMATION", gap_ids)
        self.assertIn("GAP-GUARDRAIL-PREFLIGHT-WARNING", gap_ids)
        self.assertIn("GAP-RUNTIME-STAGE-CHECKPOINT-RESUME", gap_ids)
        self.assertIn("GAP-TRACE-REMOTE-INTEROP", gap_ids)
        self.assertTrue(all(gap_id.startswith("GAP-") for gap_id in gap_ids))
        self.assertFalse(any(gap_id.startswith("GAP-STARTER-") for gap_id in gap_ids))

    def test_filters_by_area(self) -> None:
        gaps = collect_harness_sample_gaps.select_gaps({"workflow-skills"})

        self.assertTrue(gaps)
        self.assertTrue(all(gap.area == "workflow-skills" for gap in gaps))
        self.assertIn("GAP-WORKFLOW-CROSS-WS", {gap.id for gap in gaps})

    def test_markdown_mentions_empty_template_evidence(self) -> None:
        with mock.patch("sys.stdout", new=StringIO()) as output:
            collect_harness_sample_gaps.emit_markdown(list(collect_harness_sample_gaps.GAPS))

        text = output.getvalue()
        self.assertIn("Harness Sample Gaps", text)
        self.assertIn("GAP-GUARDRAIL-CONFIRMATION", text)
        self.assertIn("generic ledger records: 0", text)
        self.assertIn("pending-real-sample", text)
        self.assertIn("future-work", text)

    def test_json_payload_includes_current_evidence(self) -> None:
        gap = next(gap for gap in collect_harness_sample_gaps.GAPS if gap.id == "GAP-GUARDRAIL-CONFIRMATION")
        payload = collect_harness_sample_gaps.gap_dict(gap)

        self.assertEqual(
            ["generic ledger records: 0", "accepted real/local samples: real=0, local=0"],
            payload["current_evidence"],
        )

    def test_runtime_gap_current_evidence_is_empty_in_starter(self) -> None:
        checkpoint_gap = next(
            gap for gap in collect_harness_sample_gaps.GAPS if gap.id == "GAP-RUNTIME-STAGE-CHECKPOINT-RESUME"
        )
        loop_gap = next(gap for gap in collect_harness_sample_gaps.GAPS if gap.id == "GAP-RUNTIME-LOOP-SCOPE-WARNING")

        self.assertIn("accepted resume samples: 0", collect_harness_sample_gaps.current_evidence_for(checkpoint_gap))
        self.assertIn("accepted cross-task samples: 0", collect_harness_sample_gaps.current_evidence_for(checkpoint_gap))
        self.assertIn("accepted real warning samples: 0", collect_harness_sample_gaps.current_evidence_for(loop_gap))


if __name__ == "__main__":
    unittest.main()
