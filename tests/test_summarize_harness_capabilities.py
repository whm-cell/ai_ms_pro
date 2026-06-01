from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import summarize_harness_capabilities  # noqa: E402


class SummarizeHarnessCapabilitiesTest(unittest.TestCase):
    def test_summary_contains_expected_top_level_metrics(self) -> None:
        summary = summarize_harness_capabilities.build_summary()

        self.assertIn("durability_coverage", summary)
        self.assertIn("verified_interop_coverage", summary)
        self.assertIn("task_eval_pass_rate", summary)
        self.assertIn("high_impact_guardrail_confirmation_coverage", summary)


if __name__ == "__main__":
    unittest.main()
