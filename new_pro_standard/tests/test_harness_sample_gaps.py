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
    def test_starter_gaps_are_template_scoped(self) -> None:
        gap_ids = {gap.id for gap in collect_harness_sample_gaps.GAPS}

        self.assertIn("GAP-STARTER-HIGH-IMPACT-ACTION", gap_ids)
        self.assertIn("GAP-STARTER-REMOTE-INTEROP", gap_ids)
        self.assertTrue(all(gap_id.startswith("GAP-STARTER-") for gap_id in gap_ids))

    def test_default_selection_excludes_future_work(self) -> None:
        gaps = collect_harness_sample_gaps.select_gaps(set())

        self.assertNotIn("GAP-STARTER-REMOTE-INTEROP", {gap.id for gap in gaps})
        self.assertTrue(all(gap.status == "pending-real-sample" for gap in gaps))

    def test_include_future_adds_remote_interop_boundary(self) -> None:
        gaps = collect_harness_sample_gaps.select_gaps(set(), include_future=True)

        self.assertIn("GAP-STARTER-REMOTE-INTEROP", {gap.id for gap in gaps})

    def test_filters_by_area(self) -> None:
        gaps = collect_harness_sample_gaps.select_gaps({"workflow-skills"})

        self.assertEqual(["GAP-STARTER-WORKFLOW-SKILL"], [gap.id for gap in gaps])

    def test_markdown_mentions_empty_starter_evidence(self) -> None:
        with mock.patch("sys.stdout", new=StringIO()) as output:
            collect_harness_sample_gaps.emit_markdown(list(collect_harness_sample_gaps.GAPS))

        text = output.getvalue()
        self.assertIn("Harness Sample Gaps", text)
        self.assertIn("pending-real-sample", text)
        self.assertIn("future-work", text)

    def test_json_payload_marks_empty_ledger(self) -> None:
        gap = collect_harness_sample_gaps.GAPS[0]
        payload = collect_harness_sample_gaps.gap_dict(gap)

        self.assertEqual(["starter ledger is empty by design"], payload["current_evidence"])


if __name__ == "__main__":
    unittest.main()
