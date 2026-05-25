from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_local_trace_summary_samples  # noqa: E402


VALID_REAL_RECORD = {
    "schema_version": "local-trace-summary-sample/v1",
    "id": "TRACE-SUMMARY-SAMPLE-2026-05-24-real-json-report",
    "sampled_at": "2026-05-24",
    "source_type": "real-local-report",
    "outcome": "accepted",
    "summary_format": "json",
    "task_class": "harness-hardening",
    "task_summary": "Run local no-network runtime trace summary over current observation files.",
    "no_network": True,
    "local_only": True,
    "observation_count": 55,
    "trace_record_count": 55,
    "trace_count": 14,
    "promotion_needed_count": 55,
    "warning_count": 1,
    "redaction_states": ["redacted", "not_applicable"],
    "key_findings": ["Report stayed bounded and showed promotion review pressure."],
    "action_taken": ["Kept report advisory and recorded burn-in sample."],
    "evidence_refs": ["scripts/summarize_runtime_traces.py", "tests/test_summarize_runtime_traces.py"],
    "false_positive": False,
    "note": "Bounded sample without raw runtime paths.",
}


SYNTHETIC_RECORD = {
    "schema_version": "local-trace-summary-sample/v1",
    "id": "TRACE-SUMMARY-SAMPLE-2026-05-24-synthetic-redaction",
    "sampled_at": "2026-05-24",
    "source_type": "synthetic-regression",
    "outcome": "accepted",
    "summary_format": "markdown",
    "task_class": "synthetic-regression",
    "task_summary": "Unit-test fixture proves sensitive runtime fields stay out of rendered summary.",
    "no_network": True,
    "local_only": True,
    "observation_count": 1,
    "trace_record_count": 0,
    "trace_count": 0,
    "promotion_needed_count": 1,
    "warning_count": 1,
    "redaction_states": ["unknown"],
    "key_findings": ["Regression covers bounded markdown and redaction behavior."],
    "action_taken": ["Kept unit regression coverage."],
    "evidence_refs": ["tests/test_summarize_runtime_traces.py"],
    "false_positive": False,
    "note": "Synthetic regression only; not counted as real burn-in evidence.",
}


def write_samples(*records: dict[str, object] | str) -> Path:
    temp_dir = tempfile.TemporaryDirectory(dir=ROOT)
    path = Path(temp_dir.name) / "local-trace-summary-samples.jsonl"
    lines = [record if isinstance(record, str) else json.dumps(record) for record in records]
    path.write_text("\n".join(lines), encoding="utf-8")
    write_samples.cleanups.append(temp_dir)
    return path


write_samples.cleanups = []  # type: ignore[attr-defined]


class LocalTraceSummarySamplesTest(unittest.TestCase):
    def tearDown(self) -> None:
        while write_samples.cleanups:  # type: ignore[attr-defined]
            write_samples.cleanups.pop().cleanup()  # type: ignore[attr-defined]

    def test_repository_samples_pass(self) -> None:
        report = check_local_trace_summary_samples.build_report()

        self.assertEqual(report.errors, [])
        self.assertGreaterEqual(report.real_report_count, 3)
        self.assertGreaterEqual(report.accepted_real_report_count, 3)
        self.assertEqual(1, report.accepted_real_task_class_count)
        self.assertEqual(3, report.accepted_real_task_classes["harness-hardening"])

    def test_counts_real_reports(self) -> None:
        report = check_local_trace_summary_samples.build_report(write_samples(VALID_REAL_RECORD, SYNTHETIC_RECORD))

        self.assertEqual(report.errors, [])
        self.assertEqual(report.real_report_count, 1)
        self.assertEqual(report.accepted_real_report_count, 1)
        self.assertEqual({"harness-hardening": 1}, report.accepted_real_task_classes)

    def test_rejects_missing_evidence_ref(self) -> None:
        record = {**VALID_REAL_RECORD, "evidence_refs": ["docs/ai/standards/missing-trace-summary-evidence.md"]}

        report = check_local_trace_summary_samples.build_report(write_samples(record))

        self.assertTrue(any("evidence_refs item does not exist" in error for error in report.errors))

    def test_rejects_raw_runtime_material(self) -> None:
        record = {
            **VALID_REAL_RECORD,
            "transcript_path": ".codex/runtime/sessions/raw.jsonl",
            "evidence_refs": [".codex/runtime/observations/raw.jsonl"],
        }

        report = check_local_trace_summary_samples.build_report(write_samples(record))

        text = "\n".join(report.errors)
        self.assertIn("forbidden raw runtime key: transcript_path", text)
        self.assertIn("must not reference local runtime material", text)

    def test_accepted_samples_must_be_local_no_network(self) -> None:
        record = {**VALID_REAL_RECORD, "no_network": False}

        report = check_local_trace_summary_samples.build_report(write_samples(record))

        self.assertTrue(any("no_network=true" in error for error in report.errors))

    def test_rejects_bad_counts_and_redaction_states(self) -> None:
        record = {**VALID_REAL_RECORD, "observation_count": -1, "redaction_states": ["leaked"]}

        report = check_local_trace_summary_samples.build_report(write_samples(record))

        text = "\n".join(report.errors)
        self.assertIn("observation_count must be a non-negative integer", text)
        self.assertIn("redaction_states has invalid values", text)

    def test_real_reports_require_task_class(self) -> None:
        record = {key: value for key, value in VALID_REAL_RECORD.items() if key != "task_class"}

        report = check_local_trace_summary_samples.build_report(write_samples(record))

        self.assertTrue(any("task_class must be non-empty text" in error for error in report.errors))

    def test_accepted_real_reports_reject_placeholder_task_class(self) -> None:
        record = {**VALID_REAL_RECORD, "task_class": "TBD"}

        report = check_local_trace_summary_samples.build_report(write_samples(record))

        self.assertTrue(any("must use a concrete task_class" in error for error in report.errors))

    def test_pending_real_reports_allow_placeholder_task_class(self) -> None:
        record = {**VALID_REAL_RECORD, "outcome": "pending", "task_class": "TBD"}

        report = check_local_trace_summary_samples.build_report(write_samples(record))

        self.assertEqual([], report.errors)

    def test_cli_json_output_is_stable(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_local_trace_summary_samples.py"), "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn('"accepted_real_report_count"', result.stdout)
        self.assertIn('"accepted_real_task_class_count"', result.stdout)
        self.assertIn('"errors": []', result.stdout)


if __name__ == "__main__":
    unittest.main()
