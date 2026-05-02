from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_ai_governance  # noqa: E402


class GovernanceStageAlignmentTest(unittest.TestCase):
    def test_matching_matrix_stage_has_no_mismatch(self) -> None:
        rows = [
            {
                "requirement_id": "REQ-001",
                "workstream_id": "WS-01",
                "stage_token": "STAGE-00",
            }
        ]

        mismatches = check_ai_governance.stage_alignment_mismatches(
            rows=rows,
            requirement_ids=["REQ-001"],
            workstream_ids=["WS-01"],
            current_stage="STAGE-00",
        )

        self.assertEqual(mismatches, [])

    def test_different_matrix_stage_is_reported(self) -> None:
        rows = [
            {
                "requirement_id": "REQ-001",
                "workstream_id": "WS-01",
                "stage_token": "STAGE-01",
            }
        ]

        mismatches = check_ai_governance.stage_alignment_mismatches(
            rows=rows,
            requirement_ids=["REQ-001"],
            workstream_ids=["WS-01"],
            current_stage="STAGE-00",
        )

        self.assertEqual(mismatches, ["REQ-001/WS-01=STAGE-01"])

    def test_unrelated_rows_are_ignored(self) -> None:
        rows = [
            {
                "requirement_id": "REQ-999",
                "workstream_id": "WS-99",
                "stage_token": "STAGE-01",
            }
        ]

        mismatches = check_ai_governance.stage_alignment_mismatches(
            rows=rows,
            requirement_ids=["REQ-001"],
            workstream_ids=["WS-01"],
            current_stage="STAGE-00",
        )

        self.assertEqual(mismatches, [])


if __name__ == "__main__":
    unittest.main()
