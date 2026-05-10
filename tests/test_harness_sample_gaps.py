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
    def test_filters_by_area(self) -> None:
        gaps = collect_harness_sample_gaps.select_gaps({"workflow-skills"})

        self.assertTrue(gaps)
        self.assertTrue(all(gap.area == "workflow-skills" for gap in gaps))

    def test_markdown_mentions_pending_real_samples(self) -> None:
        with mock.patch("sys.stdout", new=StringIO()) as output:
            collect_harness_sample_gaps.emit_markdown(list(collect_harness_sample_gaps.GAPS))

        text = output.getvalue()
        self.assertIn("GAP-GUARDRAIL-CONFIRMATION", text)
        self.assertIn("GAP-SEC-CONTROL-MATRIX-BURNIN", text)
        self.assertIn("GAP-TRACE-OTLP-PILOT-BURNIN", text)
        self.assertIn("pending-real-sample", text)


if __name__ == "__main__":
    unittest.main()
