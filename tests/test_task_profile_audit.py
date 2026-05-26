from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_task_profile_audit  # noqa: E402


SIMPLE_RECORD = {
    "schema_version": "task-profile-audit-sample/v1",
    "id": "SAMPLE-001-simple",
    "source_type": "real-task",
    "outcome": "accepted",
    "profile": "simple",
    "task_summary": "Narrow checker fix.",
    "read_files": [
        "AGENTS.md",
        "docs/ai/index.md",
        "docs/ai/working-context.md",
        "scripts/check_change_triggered_followups.py",
        "tests/test_change_triggered_followups.py",
    ],
    "changed_files": [
        "scripts/check_change_triggered_followups.py",
        "tests/test_change_triggered_followups.py",
    ],
    "verification_commands": [
        "python3 tests/test_change_triggered_followups.py",
        ".codex/hooks/run_with_repo_python.sh scripts/check_code_shape.py --staged",
    ],
    "traceability_note": "not-applicable: narrow checker fix did not change requirement mapping.",
    "false_positive": False,
    "process_tax_note": "Simple task stayed within a small read and verification surface.",
    "evidence_refs": ["tests/test_task_profile_audit.py"],
}


COMPLEX_RECORD = {
    "schema_version": "task-profile-audit-sample/v1",
    "id": "SAMPLE-002-complex",
    "source_type": "real-task",
    "outcome": "accepted",
    "profile": "complex",
    "task_summary": "Requirement-backed harness change.",
    "read_files": [
        "AGENTS.md",
        "docs/ai/index.md",
        "docs/ai/working-context.md",
        "docs/requirements/index.md",
        "docs/requirements/traceability-matrix.md",
        "docs/ai/status/stage-00-runtime-harness-foundation.md",
        "scripts/check_requirements_shape.py",
        "tests/test_requirements_shape.py",
    ],
    "changed_files": [
        "docs/requirements/normalized/REQ-001-threejs-snake-core-gameplay.md",
        "scripts/check_requirements_shape.py",
    ],
    "verification_commands": [
        "python3 tests/test_requirements_shape.py",
        ".codex/hooks/run_with_repo_python.sh scripts/check_requirements_shape.py",
        ".codex/hooks/run_with_repo_python.sh scripts/check_ai_governance.py",
    ],
    "requirement_ids": ["REQ-001"],
    "workstream_ids": ["WS-01"],
    "false_positive": False,
    "process_tax_note": "Complex task kept traceability and governance checks in scope.",
    "evidence_refs": ["tests/test_task_profile_audit.py"],
}


def write_audit(*records: dict[str, object] | str) -> Path:
    temp_dir = tempfile.TemporaryDirectory(dir=ROOT)
    path = Path(temp_dir.name) / "task-profile-audit.jsonl"
    lines: list[str] = []
    for record in records:
        lines.append(record if isinstance(record, str) else json.dumps(record))
    path.write_text("\n".join(lines), encoding="utf-8")
    write_audit.cleanups.append(temp_dir)
    return path


write_audit.cleanups = []  # type: ignore[attr-defined]


class TaskProfileAuditTest(unittest.TestCase):
    def tearDown(self) -> None:
        while write_audit.cleanups:  # type: ignore[attr-defined]
            write_audit.cleanups.pop().cleanup()  # type: ignore[attr-defined]

    def test_repository_sample_passes(self) -> None:
        report = check_task_profile_audit.build_report()

        self.assertEqual(report.errors, [])
        self.assertGreaterEqual(report.record_count, 2)
        self.assertGreaterEqual(report.accepted_real_sample_count, 1)
        self.assertGreaterEqual(report.accepted_real_profiles.get("simple", 0), 1)
        self.assertGreaterEqual(report.accepted_real_profiles.get("complex", 0), 1)
        self.assertGreaterEqual(report.accepted_real_profiles.get("0-1-stage", 0), 1)

    def test_accepts_simple_and_complex_records(self) -> None:
        report = check_task_profile_audit.build_report(write_audit(SIMPLE_RECORD, COMPLEX_RECORD))

        self.assertEqual(report.errors, [])
        self.assertEqual(report.record_count, 2)
        self.assertEqual(report.real_sample_count, 2)
        self.assertEqual(report.accepted_real_profiles, {"simple": 1, "complex": 1})

    def test_rejects_missing_evidence_ref(self) -> None:
        record = {**SIMPLE_RECORD, "evidence_refs": ["docs/ai/standards/missing-task-profile-evidence.md"]}

        report = check_task_profile_audit.build_report(write_audit(record))

        self.assertTrue(any("evidence_refs item does not exist" in error for error in report.errors))

    def test_simple_profile_rejects_heavy_surfaces(self) -> None:
        record = {
            **SIMPLE_RECORD,
            "read_files": [*SIMPLE_RECORD["read_files"], "docs/requirements/traceability-matrix.md"],
        }

        report = check_task_profile_audit.build_report(write_audit(record))

        self.assertTrue(any("simple profile read heavy surfaces" in error for error in report.errors))

    def test_complex_profile_requires_traceability_closure(self) -> None:
        record = {
            **COMPLEX_RECORD,
            "read_files": [
                item for item in COMPLEX_RECORD["read_files"] if item != "docs/requirements/traceability-matrix.md"
            ],
            "requirement_ids": [],
            "workstream_ids": [],
        }

        report = check_task_profile_audit.build_report(write_audit(record))

        self.assertTrue(any("complex profile needs traceability" in error for error in report.errors))

    def test_governance_changes_require_governance_check(self) -> None:
        record = {
            **COMPLEX_RECORD,
            "changed_files": ["docs/ai/agentic-harness-gap-roadmap.md"],
            "verification_commands": ["python3 tests/test_task_profile_audit.py"],
        }

        report = check_task_profile_audit.build_report(write_audit(record))

        self.assertTrue(any("check_ai_governance.py" in error for error in report.errors))

    def test_rejects_raw_runtime_material(self) -> None:
        record = {
            **SIMPLE_RECORD,
            "transcript_path": ".codex/runtime/sessions/raw.jsonl",
            "evidence_refs": [".codex/runtime/observations/raw.jsonl"],
        }

        report = check_task_profile_audit.build_report(write_audit(record))

        text = "\n".join(report.errors)
        self.assertIn("forbidden raw runtime key: transcript_path", text)
        self.assertIn("must not reference local runtime material", text)

    def test_rejects_missing_burn_in_metadata(self) -> None:
        record = {key: value for key, value in SIMPLE_RECORD.items() if key != "source_type"}

        report = check_task_profile_audit.build_report(write_audit(record))

        self.assertTrue(any("source_type must be one of" in error for error in report.errors))

    def test_zero_one_stage_requires_planning_surfaces(self) -> None:
        record = {**SIMPLE_RECORD, "id": "SAMPLE-003-zero-one", "profile": "0-1-stage"}

        report = check_task_profile_audit.build_report(write_audit(record))

        text = "\n".join(report.errors)
        self.assertIn("docs/requirements/index.md", text)
        self.assertIn("stage status read", text)
        self.assertIn("workstream read", text)

    def test_cli_json_output_is_stable(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_task_profile_audit.py"), "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn('"record_count"', result.stdout)
        self.assertIn('"accepted_real_sample_count"', result.stdout)
        self.assertIn('"errors": []', result.stdout)


if __name__ == "__main__":
    unittest.main()
