from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_agentic_red_team_samples  # noqa: E402


VALID_RECORD = {
    "schema_version": "agentic-red-team-sample/v1",
    "id": "REDTEAM-SAMPLE-2026-05-24-tool-output-injection",
    "sampled_at": "2026-05-24",
    "control_ids": ["AC-09"],
    "risk_family": "tool-output-injection",
    "source_type": "local-replay",
    "outcome": "accepted",
    "local_only": True,
    "no_external_claim": True,
    "false_positive": False,
    "adversarial_summary": "Tool output includes instruction-like text and should be scanned as data.",
    "decision": "Keep output untrusted; checker reports the instruction-like phrase.",
    "action_taken": ["Preserved bounded replay in unit tests."],
    "replay_commands": ["python3 tests/test_skill_catalog.py"],
    "evidence_refs": ["tests/test_skill_catalog.py", "scripts/check_skill_catalog.py"],
    "checker_refs": ["scripts/check_skill_catalog.py --check-output"],
    "upgrade_signal": "weak",
    "false_positive_rule": "A finding is false-positive only after reviewer confirms the matched text is inert quoted evidence.",
    "note": "Local replay only; no external tool or MCP interop is claimed.",
}


SYNTHETIC_RECORD = {
    **VALID_RECORD,
    "id": "REDTEAM-SAMPLE-2026-05-24-synthetic-memory-poisoning",
    "control_ids": ["AC-10"],
    "risk_family": "memory-poisoning",
    "source_type": "synthetic-regression",
    "adversarial_summary": "Recovered context contains instruction-like text.",
}


def write_samples(*records: dict[str, object] | str) -> Path:
    temp_dir = tempfile.TemporaryDirectory(dir=ROOT)
    path = Path(temp_dir.name) / "agentic-red-team-samples.jsonl"
    lines = [record if isinstance(record, str) else json.dumps(record) for record in records]
    path.write_text("\n".join(lines), encoding="utf-8")
    write_samples.cleanups.append(temp_dir)
    return path


write_samples.cleanups = []  # type: ignore[attr-defined]


class AgenticRedTeamSamplesTest(unittest.TestCase):
    def tearDown(self) -> None:
        while write_samples.cleanups:  # type: ignore[attr-defined]
            write_samples.cleanups.pop().cleanup()  # type: ignore[attr-defined]

    def test_repository_samples_pass(self) -> None:
        report = check_agentic_red_team_samples.build_report()

        self.assertEqual(report.errors, [])
        self.assertEqual(0, report.accepted_replay_or_real_count)
        self.assertEqual(0, report.accepted_real_incident_count)
        self.assertEqual({}, report.accepted_by_risk)
        self.assertEqual({}, report.accepted_real_by_risk)
        self.assertTrue(report.warnings)
        self.assertEqual(check_agentic_red_team_samples.REQUIRED_RISKS, check_agentic_red_team_samples.RISKS)

    def test_counts_local_replay_samples(self) -> None:
        report = check_agentic_red_team_samples.build_report(write_samples(VALID_RECORD, SYNTHETIC_RECORD))

        self.assertEqual(report.errors, [])
        self.assertEqual(report.accepted_replay_or_real_count, 1)
        self.assertEqual(report.accepted_by_risk, {"tool-output-injection": 1})
        self.assertEqual(report.accepted_real_by_risk, {})

    def test_accepts_existing_evidence_ref_selector(self) -> None:
        record = {**VALID_RECORD, "evidence_refs": ["tests/test_skill_catalog.py::test_placeholder"]}

        report = check_agentic_red_team_samples.build_report(write_samples(record))

        self.assertEqual(report.errors, [])

    def test_rejects_missing_evidence_ref(self) -> None:
        record = {**VALID_RECORD, "evidence_refs": ["docs/ai/security/missing-red-team-evidence.md"]}

        report = check_agentic_red_team_samples.build_report(write_samples(record))

        self.assertTrue(any("evidence_refs item does not exist" in error for error in report.errors))

    def test_rejects_raw_runtime_material(self) -> None:
        record = {
            **VALID_RECORD,
            "transcript_path": ".codex/runtime/sessions/raw.jsonl",
            "evidence_refs": [".codex/runtime/observations/raw.jsonl"],
        }

        report = check_agentic_red_team_samples.build_report(write_samples(record))

        text = "\n".join(report.errors)
        self.assertIn("forbidden raw context key: transcript_path", text)
        self.assertIn("must not reference local runtime material", text)

    def test_accepted_samples_must_not_claim_external_coverage(self) -> None:
        record = {**VALID_RECORD, "no_external_claim": False}

        report = check_agentic_red_team_samples.build_report(write_samples(record))

        self.assertTrue(any("no_external_claim=true" in error for error in report.errors))

    def test_rejects_candidate_upgrade_without_real_incident(self) -> None:
        record = {**VALID_RECORD, "upgrade_signal": "candidate"}

        report = check_agentic_red_team_samples.build_report(write_samples(record))

        self.assertTrue(any("requires a real-incident sample" in error for error in report.errors))

    def test_cli_json_output_is_stable(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_agentic_red_team_samples.py"), "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn('"accepted_replay_or_real_count"', result.stdout)
        self.assertIn('"accepted_real_by_risk"', result.stdout)
        self.assertIn('"errors": []', result.stdout)


if __name__ == "__main__":
    unittest.main()
