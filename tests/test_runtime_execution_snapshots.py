from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex" / "hooks"))
sys.path.insert(0, str(ROOT / "scripts"))

import check_runtime_execution_snapshots  # noqa: E402
import runtime_execution_snapshot  # noqa: E402


class RuntimeExecutionSnapshotTest(unittest.TestCase):
    def test_build_snapshot_defaults_to_resumable_local_only(self) -> None:
        snapshot = runtime_execution_snapshot.build_execution_snapshot(
            payload={},
            session_id="session-demo",
            agent_label="main",
            branch_or_thread="test-branch",
            session_type="new",
            requirement_ids=["REQ-001"],
            workstream_ids=["WS-01"],
            traceability_source="manual",
            changed_paths=["docs/ai/working-context.md"],
            prompt_preview="Ship runtime durability slice",
            transcript_path="[REDACTED_PATH]/rollout.jsonl",
        )

        self.assertEqual(snapshot["schema_version"], "runtime-execution-snapshot/v1")
        self.assertEqual(snapshot["state"], "resumable")
        self.assertEqual(snapshot["claim_boundary"], "local-only")
        self.assertEqual(snapshot["tool_contracts"], ["stop_runtime_observation", "stop_runtime_session"])
        self.assertEqual(snapshot["authority"]["level"], "main-agent")

    def test_snapshot_validator_accepts_written_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            snapshot_dir = Path(tempdir) / "execution-snapshots"
            snapshot = runtime_execution_snapshot.build_execution_snapshot(
                payload={"execution_state": "paused", "tool_contracts": ["stop_runtime_session"]},
                session_id="session-valid",
                agent_label="main",
                branch_or_thread="test-branch",
                session_type="resume",
                requirement_ids=["REQ-001"],
                workstream_ids=["WS-01"],
                traceability_source="manual",
                changed_paths=["docs/ai/working-context.md"],
                prompt_preview="Pause and resume runtime task",
                transcript_path="[REDACTED_PATH]/rollout.jsonl",
            )
            runtime_execution_snapshot.write_snapshot(snapshot, snapshot_dir)

            files = list(snapshot_dir.glob("*.json"))
            self.assertEqual(len(files), 1)
            loaded = json.loads(files[0].read_text(encoding="utf-8"))
            errors = check_runtime_execution_snapshots.validate_snapshot(
                loaded,
                check_runtime_execution_snapshots.load_contract_names(),
                files[0],
            )

        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
