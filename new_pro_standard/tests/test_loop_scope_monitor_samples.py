from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_loop_scope_monitor_samples  # noqa: E402


VALID_REAL_RECORD = {
    "schema_version": "loop-scope-monitor-sample/v1",
    "id": "LOOP-SAMPLE-2026-05-24-real-warning",
    "sampled_at": "2026-05-24",
    "source_type": "real-session",
    "task_summary": "Long harness-maintenance session produced a validation-loop warning.",
    "triggered_findings": ["validation-loop"],
    "monitor_recommendations": ["checkpoint", "shrink-validation"],
    "outcome": "accepted",
    "false_positive": False,
    "action_taken": ["Recorded a checkpoint before continuing verification."],
    "evidence_refs": ["docs/ai/checkpoints/resume-samples.jsonl"],
    "note": "Bounded sample without raw transcript paths.",
}


SYNTHETIC_RECORD = {
    "schema_version": "loop-scope-monitor-sample/v1",
    "id": "LOOP-SAMPLE-2026-05-24-synthetic-repeated-command",
    "sampled_at": "2026-05-24",
    "source_type": "synthetic-regression",
    "task_summary": "Unit-test fixture proves repeated-command warning shape stays bounded.",
    "triggered_findings": ["repeated-command"],
    "monitor_recommendations": ["inspect-repeated-command"],
    "outcome": "accepted",
    "false_positive": False,
    "action_taken": ["Kept unit regression coverage for repeated commands."],
    "evidence_refs": ["tests/test_stop_loop_scope_monitor.py"],
    "note": "Synthetic regression only; not counted as real burn-in evidence.",
}


def write_samples(*records: dict[str, object] | str) -> Path:
    temp_dir = tempfile.TemporaryDirectory(dir=ROOT)
    path = Path(temp_dir.name) / "loop-scope-monitor-samples.jsonl"
    lines = [record if isinstance(record, str) else json.dumps(record) for record in records]
    path.write_text("\n".join(lines), encoding="utf-8")
    write_samples.cleanups.append(temp_dir)
    return path


write_samples.cleanups = []  # type: ignore[attr-defined]


class LoopScopeMonitorSamplesTest(unittest.TestCase):
    def tearDown(self) -> None:
        while write_samples.cleanups:  # type: ignore[attr-defined]
            write_samples.cleanups.pop().cleanup()  # type: ignore[attr-defined]

    def test_repository_samples_pass(self) -> None:
        report = check_loop_scope_monitor_samples.build_report()

        self.assertEqual(report.errors, [])
        self.assertEqual(0, report.record_count)
        self.assertEqual(0, report.accepted_real_sample_count)
        self.assertTrue(report.warnings)

    def test_counts_real_warning_samples(self) -> None:
        report = check_loop_scope_monitor_samples.build_report(write_samples(VALID_REAL_RECORD, SYNTHETIC_RECORD))

        self.assertEqual(report.errors, [])
        self.assertEqual(report.real_sample_count, 1)
        self.assertEqual(report.accepted_real_sample_count, 1)
        self.assertEqual(report.accepted_warning_sample_count, 1)

    def test_rejects_missing_evidence_ref(self) -> None:
        record = {**VALID_REAL_RECORD, "evidence_refs": ["docs/ai/standards/missing-loop-evidence.md"]}

        report = check_loop_scope_monitor_samples.build_report(write_samples(record))

        self.assertTrue(any("evidence_refs item does not exist" in error for error in report.errors))

    def test_rejects_raw_runtime_material(self) -> None:
        record = {
            **VALID_REAL_RECORD,
            "transcript_path": ".codex/runtime/sessions/raw.jsonl",
            "evidence_refs": [".codex/runtime/observations/demo.jsonl"],
        }

        report = check_loop_scope_monitor_samples.build_report(write_samples(record))

        text = "\n".join(report.errors)
        self.assertIn("forbidden raw runtime key: transcript_path", text)
        self.assertIn("must not reference local runtime material", text)

    def test_accepted_samples_require_action_and_evidence(self) -> None:
        record = {**VALID_REAL_RECORD, "action_taken": ["none"], "evidence_refs": ["none"]}

        report = check_loop_scope_monitor_samples.build_report(write_samples(record))

        text = "\n".join(report.errors)
        self.assertIn("accepted samples need action_taken", text)
        self.assertIn("accepted samples need evidence_refs", text)

    def test_rejects_bad_ids_dates_and_mixed_none(self) -> None:
        record = {
            **VALID_REAL_RECORD,
            "id": "bad",
            "sampled_at": "2026/05/24",
            "triggered_findings": ["none", "validation-loop"],
        }

        report = check_loop_scope_monitor_samples.build_report(write_samples(record))

        text = "\n".join(report.errors)
        self.assertIn("id must match", text)
        self.assertIn("sampled_at must use YYYY-MM-DD", text)
        self.assertIn("cannot mix none", text)

    def test_cli_json_output_is_stable(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_loop_scope_monitor_samples.py"), "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn('"accepted_warning_sample_count"', result.stdout)
        self.assertIn('"errors": []', result.stdout)


if __name__ == "__main__":
    unittest.main()
