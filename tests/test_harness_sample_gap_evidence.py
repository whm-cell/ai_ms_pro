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
        "id": "GAP-SAMPLE-2026-05-24-otlp-local-pilot",
        "gap_id": "GAP-TRACE-OTLP-PILOT-BURNIN",
        "sampled_at": "2026-05-24",
        "source_type": "local-interop-run",
        "outcome": "accepted",
        "local_only": True,
        "no_external_claim": True,
        "false_positive": False,
        "network_exported": True,
        "endpoint_scope": "local-capture-server",
        "remote_status": "http-2xx",
        "sample_summary": "Bounded OTLP HTTP JSON pilot posted to localhost capture server.",
        "decision": "Count as local pilot only; keep hosted interop gaps open.",
        "boundary_note": "No raw payload, transcript, or runtime path is recorded.",
        "action_taken": ["validated explicit endpoint"],
        "evidence_refs": ["tests/test_agent_trace_export.py::test_otlp_http_json_send_requires_explicit_endpoint"],
        "checker_refs": ["scripts/export_agent_trace.py"],
    }
    record.update(overrides)
    return record


class HarnessSampleGapEvidenceTest(unittest.TestCase):
    def test_default_ledger_counts_otlp_local_pilot(self) -> None:
        report = check_harness_sample_gap_evidence.build_report()

        self.assertEqual(report.errors, [])
        self.assertEqual(report.accepted_local_by_gap["GAP-TRACE-OTLP-PILOT-BURNIN"], 1)
        self.assertEqual(report.accepted_real_by_gap.get("GAP-TRACE-OTLP-PILOT-BURNIN", 0), 0)
        self.assertEqual(report.accepted_real_by_gap["GAP-GUARDRAIL-SOURCE-BOUNDARY"], 2)
        self.assertEqual(report.accepted_real_by_gap["GAP-SEC-CONTROL-MATRIX-BURNIN"], 2)

    def test_rejects_raw_runtime_material(self) -> None:
        path = write_jsonl([valid_record(id="GAP-SAMPLE-2026-05-24-raw-runtime", evidence_refs=[".codex/runtime/x.jsonl"])])

        report = check_harness_sample_gap_evidence.build_report(path)

        self.assertTrue(any("must not reference local runtime material" in error for error in report.errors))

    def test_accepts_existing_evidence_refs_with_selectors(self) -> None:
        path = write_jsonl(
            [
                valid_record(
                    id="GAP-SAMPLE-2026-05-24-evidence-selectors",
                    evidence_refs=[
                        "tests/test_agent_trace_export.py::test_otlp_http_json_send_requires_explicit_endpoint",
                        "docs/ai/standards/agent-trace-schema.md#local-export-adapter",
                        "docs/ai/standards/harness-sample-gap-evidence.jsonl:1",
                    ],
                )
            ]
        )

        report = check_harness_sample_gap_evidence.build_report(path)

        self.assertEqual([], report.errors)

    def test_rejects_missing_evidence_refs(self) -> None:
        path = write_jsonl(
            [
                valid_record(
                    id="GAP-SAMPLE-2026-05-24-missing-evidence-ref",
                    evidence_refs=["docs/ai/missing-gap-evidence.md"],
                )
            ]
        )

        report = check_harness_sample_gap_evidence.build_report(path)

        self.assertIn("line 1: evidence_refs item does not exist: docs/ai/missing-gap-evidence.md", report.errors)

    def test_rejects_absolute_or_escaping_evidence_refs(self) -> None:
        path = write_jsonl(
            [
                valid_record(
                    id="GAP-SAMPLE-2026-05-24-bad-evidence-ref",
                    evidence_refs=["/tmp/evidence.md", "../outside.md"],
                )
            ]
        )

        report = check_harness_sample_gap_evidence.build_report(path)

        text = "\n".join(report.errors)
        self.assertIn("line 1: evidence_refs items must be repo-relative paths: /tmp/evidence.md", text)
        self.assertIn("line 1: evidence_refs item escapes repository scope: ../outside.md", text)

    def test_rejects_accepted_otlp_without_network_export(self) -> None:
        path = write_jsonl([valid_record(id="GAP-SAMPLE-2026-05-24-no-network", network_exported=False)])

        report = check_harness_sample_gap_evidence.build_report(path)

        self.assertTrue(any("network_exported=true" in error for error in report.errors))

    def test_rejects_unknown_gap_id(self) -> None:
        path = write_jsonl([valid_record(id="GAP-SAMPLE-2026-05-24-unknown-gap", gap_id="GAP-UNKNOWN")])

        report = check_harness_sample_gap_evidence.build_report(path)

        self.assertTrue(any("unknown gap_id" in error for error in report.errors))

    def test_synthetic_accepted_sample_warns_but_does_not_count(self) -> None:
        path = write_jsonl(
            [
                valid_record(
                    id="GAP-SAMPLE-2026-05-24-synthetic",
                    gap_id="GAP-GUARDRAIL-CONFIRMATION",
                    source_type="synthetic-regression",
                    local_only=False,
                    network_exported=False,
                    endpoint_scope="none",
                    remote_status="none",
                )
            ]
        )

        report = check_harness_sample_gap_evidence.build_report(path)

        self.assertEqual(report.accepted_real_sample_count, 0)
        self.assertEqual(report.accepted_local_sample_count, 0)
        self.assertTrue(any("synthetic samples do not count" in warning for warning in report.warnings))


if __name__ == "__main__":
    unittest.main()
