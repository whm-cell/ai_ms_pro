from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_harness_sample_gap_evidence  # noqa: E402


def write_jsonl(records: list[dict[str, object]]) -> Path:
    temp = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".jsonl")
    with temp:
        for record in records:
            temp.write(json.dumps(record) + "\n")
    return Path(temp.name)


def valid_record(**overrides: object) -> dict[str, object]:
    record: dict[str, object] = {
        "schema_version": "harness-sample-gap-evidence/v1",
        "id": "GAP-SAMPLE-2026-05-26-high-impact-action",
        "gap_id": "GAP-STARTER-HIGH-IMPACT-ACTION",
        "sampled_at": "2026-05-26",
        "source_type": "real-user-action",
        "outcome": "accepted",
        "local_only": True,
        "no_external_claim": True,
        "false_positive": False,
        "network_exported": False,
        "endpoint_scope": "none",
        "remote_status": "none",
        "sample_summary": "Bounded confirmation sample from a new project action.",
        "decision": "Count as real only for the new project gap after review.",
        "boundary_note": "No raw transcript, prompt, runtime path, or old-project ledger row is recorded.",
        "action_taken": ["operator confirmed the bounded action"],
        "evidence_refs": ["docs/ai/harness-real-sample-watchlist.md"],
        "checker_refs": ["scripts/check_harness_sample_gap_evidence.py"],
    }
    record.update(overrides)
    return record


class HarnessSampleGapEvidenceTest(unittest.TestCase):
    def test_default_starter_ledger_is_empty_and_valid(self) -> None:
        report = check_harness_sample_gap_evidence.build_report()

        self.assertEqual([], report.errors)
        self.assertEqual(0, report.record_count)
        self.assertEqual(0, report.accepted_real_sample_count)
        self.assertEqual({}, report.accepted_by_gap)

    def test_counts_accepted_real_candidate(self) -> None:
        path = write_jsonl([valid_record()])

        report = check_harness_sample_gap_evidence.build_report(path)

        self.assertEqual([], report.errors)
        self.assertEqual(1, report.accepted_real_sample_count)
        self.assertEqual(1, report.accepted_real_by_gap["GAP-STARTER-HIGH-IMPACT-ACTION"])

    def test_rejects_synthetic_accepted_evidence(self) -> None:
        path = write_jsonl(
            [
                valid_record(
                    id="GAP-SAMPLE-2026-05-26-synthetic",
                    source_type="synthetic-regression",
                )
            ]
        )

        report = check_harness_sample_gap_evidence.build_report(path)

        self.assertTrue(any("synthetic samples must not be accepted" in error for error in report.errors))
        self.assertEqual(0, report.accepted_real_sample_count)

    def test_rejects_unknown_gap_id(self) -> None:
        path = write_jsonl([valid_record(id="GAP-SAMPLE-2026-05-26-unknown-gap", gap_id="GAP-UNKNOWN")])

        report = check_harness_sample_gap_evidence.build_report(path)

        self.assertTrue(any("unknown gap_id" in error for error in report.errors))

    def test_rejects_runtime_material_refs(self) -> None:
        path = write_jsonl(
            [
                valid_record(
                    id="GAP-SAMPLE-2026-05-26-runtime-ref",
                    evidence_refs=[".codex/runtime/observations/sample.jsonl"],
                )
            ]
        )

        report = check_harness_sample_gap_evidence.build_report(path)

        self.assertTrue(any("must not reference local runtime material" in error for error in report.errors))

    def test_rejects_missing_evidence_ref(self) -> None:
        path = write_jsonl(
            [
                valid_record(
                    id="GAP-SAMPLE-2026-05-26-missing-ref",
                    evidence_refs=["docs/ai/missing-sample-evidence.md"],
                )
            ]
        )

        report = check_harness_sample_gap_evidence.build_report(path)

        self.assertIn("line 1: evidence_refs item does not exist: docs/ai/missing-sample-evidence.md", report.errors)


if __name__ == "__main__":
    unittest.main()
