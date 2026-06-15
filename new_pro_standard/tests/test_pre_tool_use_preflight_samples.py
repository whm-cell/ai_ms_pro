from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_pre_tool_use_preflight_samples  # noqa: E402


VALID_REAL_RECORD = {
    "schema_version": "pre-tool-use-preflight-sample/v1",
    "id": "PRE-SAMPLE-2026-05-24-real-large-output",
    "sampled_at": "2026-05-24",
    "source_type": "real-tool-call",
    "task_summary": "Preflight warned before a likely large local inspection command.",
    "risk_summary": "Large local output risk was reduced by bounding output.",
    "hook_result": "warned",
    "triggered_findings": ["unbounded-large-output"],
    "operator_decisions": ["bounded-output"],
    "outcome": "accepted",
    "false_positive": False,
    "action_taken": ["Added max_output_tokens before rerunning the inspection."],
    "evidence_refs": ["tests/test_pre_tool_use_preflight.py"],
    "note": "Bounded sample without raw command or transcript path.",
}


SYNTHETIC_RECORD = {
    "schema_version": "pre-tool-use-preflight-sample/v1",
    "id": "PRE-SAMPLE-2026-05-24-synthetic-destructive",
    "sampled_at": "2026-05-24",
    "source_type": "synthetic-regression",
    "task_summary": "Unit-test fixture proves destructive command warning shape stays warning-only.",
    "risk_summary": "Destructive command pattern remains advisory and does not emit continue=false.",
    "hook_result": "warned",
    "triggered_findings": ["destructive-command"],
    "operator_decisions": ["explicit-confirmation"],
    "outcome": "accepted",
    "false_positive": False,
    "action_taken": ["Kept unit regression coverage for warning-only destructive commands."],
    "evidence_refs": ["tests/test_pre_tool_use_preflight.py"],
    "note": "Synthetic regression only; not counted as real burn-in evidence.",
}


def write_samples(*records: dict[str, object] | str) -> Path:
    temp_dir = tempfile.TemporaryDirectory(dir=ROOT)
    path = Path(temp_dir.name) / "pre-tool-use-preflight-samples.jsonl"
    lines = [record if isinstance(record, str) else json.dumps(record) for record in records]
    path.write_text("\n".join(lines), encoding="utf-8")
    write_samples.cleanups.append(temp_dir)
    return path


write_samples.cleanups = []  # type: ignore[attr-defined]


class PreToolUsePreflightSamplesTest(unittest.TestCase):
    def tearDown(self) -> None:
        while write_samples.cleanups:  # type: ignore[attr-defined]
            write_samples.cleanups.pop().cleanup()  # type: ignore[attr-defined]

    def test_repository_samples_pass(self) -> None:
        report = check_pre_tool_use_preflight_samples.build_report()

        self.assertEqual(report.errors, [])
        self.assertEqual(0, report.record_count)
        self.assertEqual(0, report.accepted_real_sample_count)
        self.assertTrue(report.warnings)

    def test_counts_real_warning_samples(self) -> None:
        report = check_pre_tool_use_preflight_samples.build_report(write_samples(VALID_REAL_RECORD, SYNTHETIC_RECORD))

        self.assertEqual(report.errors, [])
        self.assertEqual(report.real_sample_count, 1)
        self.assertEqual(report.accepted_real_sample_count, 1)
        self.assertEqual(report.accepted_real_warning_sample_count, 1)

    def test_rejects_missing_evidence_ref(self) -> None:
        record = {**VALID_REAL_RECORD, "evidence_refs": ["docs/ai/standards/missing-preflight-evidence.md"]}

        report = check_pre_tool_use_preflight_samples.build_report(write_samples(record))

        self.assertTrue(any("evidence_refs item does not exist" in error for error in report.errors))

    def test_rejects_raw_command_and_runtime_material(self) -> None:
        record = {
            **VALID_REAL_RECORD,
            "cmd": "git diff",
            "evidence_refs": [".codex/runtime/tool-outputs/raw.log"],
        }

        report = check_pre_tool_use_preflight_samples.build_report(write_samples(record))

        text = "\n".join(report.errors)
        self.assertIn("forbidden raw tool key: cmd", text)
        self.assertIn("must not reference local runtime material", text)

    def test_accepted_warning_samples_require_decision_action_and_evidence(self) -> None:
        record = {
            **VALID_REAL_RECORD,
            "operator_decisions": ["none"],
            "action_taken": ["none"],
            "evidence_refs": ["none"],
        }

        report = check_pre_tool_use_preflight_samples.build_report(write_samples(record))

        text = "\n".join(report.errors)
        self.assertIn("accepted samples need action_taken", text)
        self.assertIn("accepted samples need evidence_refs", text)
        self.assertIn("accepted warning samples need operator_decisions", text)

    def test_rejects_silent_sample_with_findings(self) -> None:
        record = {**VALID_REAL_RECORD, "hook_result": "silent"}

        report = check_pre_tool_use_preflight_samples.build_report(write_samples(record))

        self.assertTrue(any("silent samples must use" in error for error in report.errors))

    def test_rejects_bad_ids_dates_and_mixed_none(self) -> None:
        record = {
            **VALID_REAL_RECORD,
            "id": "bad",
            "sampled_at": "2026/05/24",
            "triggered_findings": ["none", "unbounded-large-output"],
        }

        report = check_pre_tool_use_preflight_samples.build_report(write_samples(record))

        text = "\n".join(report.errors)
        self.assertIn("id must match", text)
        self.assertIn("sampled_at must use YYYY-MM-DD", text)
        self.assertIn("cannot mix none", text)

    def test_cli_json_output_is_stable(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_pre_tool_use_preflight_samples.py"), "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn('"accepted_real_warning_sample_count"', result.stdout)
        self.assertIn('"errors": []', result.stdout)


if __name__ == "__main__":
    unittest.main()
