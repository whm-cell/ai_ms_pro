from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_stage_checkpoints  # noqa: E402


VALID_RECORD = {
    "schema_version": "stage-checkpoint/v1",
    "id": "CP-2026-05-24-demo-checkpoint",
    "stage": "STAGE-00",
    "status": "in_progress",
    "updated_at": "2026-05-24",
    "goal": "Land a verifiable checkpoint artifact.",
    "owner_surface": "docs/ai/checkpoints/stage-checkpoints.jsonl",
    "resume_prompt": "Continue from the checkpoint evidence and next_action.",
    "next_action": "Collect one real resume sample.",
    "requirement_ids": ["未绑定"],
    "workstream_ids": ["未绑定"],
    "artifact_paths": ["docs/ai/checkpoints/stage-checkpoints.jsonl"],
    "evidence": [
        {
            "kind": "check",
            "ref": ".codex/hooks/run_with_repo_python.sh scripts/check_stage_checkpoints.py",
            "status": "pending",
            "note": "Sample command remains advisory until run.",
        }
    ],
}


def write_checkpoints(*records: dict[str, object] | str) -> Path:
    temp_dir = tempfile.TemporaryDirectory(dir=ROOT)
    path = Path(temp_dir.name) / "stage-checkpoints.jsonl"
    lines = [record if isinstance(record, str) else json.dumps(record) for record in records]
    path.write_text("\n".join(lines), encoding="utf-8")
    write_checkpoints.cleanups.append(temp_dir)
    return path


write_checkpoints.cleanups = []  # type: ignore[attr-defined]


class StageCheckpointTest(unittest.TestCase):
    def tearDown(self) -> None:
        while write_checkpoints.cleanups:  # type: ignore[attr-defined]
            write_checkpoints.cleanups.pop().cleanup()  # type: ignore[attr-defined]

    def test_repository_checkpoint_sample_passes(self) -> None:
        report = check_stage_checkpoints.build_report()

        self.assertEqual(report.errors, [])
        self.assertEqual(1, report.record_count)
        self.assertEqual(0, report.sample_count)
        self.assertEqual(0, report.accepted_sample_count)
        self.assertEqual(report.accepted_cross_task_sample_count, 0)
        self.assertEqual([], report.warnings)

    def test_accepts_valid_checkpoint(self) -> None:
        report = check_stage_checkpoints.build_report(write_checkpoints(VALID_RECORD))

        self.assertEqual(report.errors, [])

    def test_accepts_valid_resume_sample(self) -> None:
        sample_path = write_checkpoints(
            {
                "schema_version": "stage-checkpoint-resume-sample/v1",
                "id": "CP-SAMPLE-2026-05-24-demo",
                "checkpoint_id": "CP-2026-05-24-demo-checkpoint",
                "resumed_at": "2026-05-24",
                "task_summary": "Used checkpoint to resume a bounded task.",
                "resume_scope": "cross-task",
                "used_checkpoint": True,
                "outcome": "accepted",
                "avoided_rework": ["Reused existing artifact."],
                "missed_validation_prevented": ["Kept focused check in scope."],
                "missing_fields": [],
                "false_positive_notes": [],
                "evidence_refs": ["docs/ai/checkpoints/stage-checkpoints.jsonl"],
                "note": "Bounded resume evidence.",
            }
        )

        report = check_stage_checkpoints.build_report(write_checkpoints(VALID_RECORD), sample_path)

        self.assertEqual(report.errors, [])
        self.assertEqual(report.accepted_sample_count, 1)
        self.assertEqual(report.accepted_cross_task_sample_count, 1)

    def test_resume_sample_rejects_missing_evidence_ref(self) -> None:
        sample_path = write_checkpoints(
            {
                "schema_version": "stage-checkpoint-resume-sample/v1",
                "id": "CP-SAMPLE-2026-05-24-missing-ref",
                "checkpoint_id": "CP-2026-05-24-demo-checkpoint",
                "resumed_at": "2026-05-24",
                "task_summary": "Used checkpoint to resume a bounded task.",
                "resume_scope": "cross-task",
                "used_checkpoint": True,
                "outcome": "accepted",
                "avoided_rework": ["Reused existing artifact."],
                "missed_validation_prevented": ["Kept focused check in scope."],
                "missing_fields": [],
                "false_positive_notes": [],
                "evidence_refs": ["docs/ai/checkpoints/missing-resume-evidence.jsonl"],
                "note": "Bounded resume evidence.",
            }
        )

        report = check_stage_checkpoints.build_report(write_checkpoints(VALID_RECORD), sample_path)

        self.assertTrue(any("evidence_refs item does not exist" in error for error in report.errors))

    def test_rejects_raw_runtime_material(self) -> None:
        record = {
            **VALID_RECORD,
            "artifact_paths": [".codex/runtime/sessions/demo.md"],
            "transcript_path": "/tmp/raw-rollout.jsonl",
        }

        report = check_stage_checkpoints.build_report(write_checkpoints(record))

        text = "\n".join(report.errors)
        self.assertIn("local runtime material", text)
        self.assertIn("forbidden raw runtime key: transcript_path", text)

    def test_complete_checkpoint_requires_finished_evidence(self) -> None:
        record = {**VALID_RECORD, "status": "complete"}

        report = check_stage_checkpoints.build_report(write_checkpoints(record))

        self.assertTrue(any("complete checkpoints cannot have pending" in error for error in report.errors))

    def test_resume_sample_rejects_unknown_checkpoint(self) -> None:
        sample_path = write_checkpoints(
            {
                "schema_version": "stage-checkpoint-resume-sample/v1",
                "id": "CP-SAMPLE-2026-05-24-missing",
                "checkpoint_id": "CP-2026-05-24-missing",
                "resumed_at": "2026-05-24",
                "task_summary": "Bad sample.",
                "resume_scope": "same-task",
                "used_checkpoint": True,
                "outcome": "accepted",
                "avoided_rework": [],
                "missed_validation_prevented": [],
                "missing_fields": [],
                "false_positive_notes": [],
                "evidence_refs": ["docs/ai/checkpoints/stage-checkpoints.jsonl"],
                "note": "Bad sample.",
            }
        )

        report = check_stage_checkpoints.build_report(write_checkpoints(VALID_RECORD), sample_path)

        self.assertTrue(any("unknown checkpoint_id" in error for error in report.errors))

    def test_resume_sample_requires_scope(self) -> None:
        sample_path = write_checkpoints(
            {
                "schema_version": "stage-checkpoint-resume-sample/v1",
                "id": "CP-SAMPLE-2026-05-24-bad-scope",
                "checkpoint_id": "CP-2026-05-24-demo-checkpoint",
                "resumed_at": "2026-05-24",
                "task_summary": "Bad scope sample.",
                "resume_scope": "unclear",
                "used_checkpoint": True,
                "outcome": "accepted",
                "avoided_rework": [],
                "missed_validation_prevented": [],
                "missing_fields": [],
                "false_positive_notes": [],
                "evidence_refs": ["docs/ai/checkpoints/stage-checkpoints.jsonl"],
                "note": "Bad scope sample.",
            }
        )

        report = check_stage_checkpoints.build_report(write_checkpoints(VALID_RECORD), sample_path)

        self.assertTrue(any("resume_scope must be one of" in error for error in report.errors))

    def test_rejects_bad_ids_and_dates(self) -> None:
        record = {
            **VALID_RECORD,
            "id": "demo",
            "stage": "stage-1",
            "updated_at": "05/24/2026",
            "requirement_ids": ["REQ-ABC"],
        }

        report = check_stage_checkpoints.build_report(write_checkpoints(record))

        text = "\n".join(report.errors)
        self.assertIn("id must match", text)
        self.assertIn("stage must match", text)
        self.assertIn("updated_at must use YYYY-MM-DD", text)
        self.assertIn("requirement_ids has invalid ids", text)

    def test_cli_json_output_is_stable(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_stage_checkpoints.py"), "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn('"record_count"', result.stdout)
        self.assertIn('"accepted_sample_count"', result.stdout)
        self.assertIn('"accepted_cross_task_sample_count"', result.stdout)
        self.assertIn('"errors": []', result.stdout)


if __name__ == "__main__":
    unittest.main()
