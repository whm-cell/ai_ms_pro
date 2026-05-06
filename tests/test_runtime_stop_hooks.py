from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex" / "hooks"))

import runtime_traceability  # noqa: E402
import stop_runtime_observation  # noqa: E402
import stop_runtime_session  # noqa: E402


class RuntimeStopHooksTest(unittest.TestCase):
    def setUp(self) -> None:
        runtime_traceability.load_traceability_catalog.cache_clear()

    def test_stop_observation_auto_discovers_traceability_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            observation_dir = Path(tempdir) / "observations"
            original_dir = stop_runtime_observation.OBSERVATION_DIR
            original_git_status_paths = stop_runtime_observation.git_status_paths
            try:
                stop_runtime_observation.OBSERVATION_DIR = observation_dir
                stop_runtime_observation.git_status_paths = lambda: ["apps/harness-trace-console/main.js"]

                stop_runtime_observation.append_observation({"session_id": "session-auto-observation"})

                files = list(observation_dir.glob("*.jsonl"))
                self.assertEqual(len(files), 1)
                payload = json.loads(files[0].read_text(encoding="utf-8").strip())
                self.assertEqual(payload["requirement_ids"], ["REQ-004", "REQ-005", "REQ-006"])
                self.assertEqual(payload["workstream_ids"], ["WS-02"])
                self.assertEqual(payload["traceability_source"], "module-path")
            finally:
                stop_runtime_observation.OBSERVATION_DIR = original_dir
                stop_runtime_observation.git_status_paths = original_git_status_paths

    def test_stop_session_auto_discovers_traceability_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            session_dir = Path(tempdir) / "sessions"
            original_dir = stop_runtime_session.SESSION_DIR
            original_git_branch = stop_runtime_session.git_branch
            original_git_status_paths = stop_runtime_session.git_status_paths
            try:
                stop_runtime_session.SESSION_DIR = session_dir
                stop_runtime_session.git_branch = lambda: "test-branch"
                stop_runtime_session.git_status_paths = lambda: ["apps/harness-trace-console/main.js"]

                stop_runtime_session.write_session_snapshot({"session_id": "session-auto-session"})

                files = list(session_dir.glob("*.md"))
                self.assertEqual(len(files), 1)
                text = files[0].read_text(encoding="utf-8")
                self.assertIn("- Requirement IDs：REQ-004, REQ-005, REQ-006", text)
                self.assertIn("- Workstream IDs：WS-02", text)
                self.assertIn("- Traceability Source：module-path", text)
                self.assertIn("## 行为护栏快照", text)
                self.assertIn("Success Criteria：待主 Agent 补充可验证的完成条件", text)
            finally:
                stop_runtime_session.SESSION_DIR = original_dir
                stop_runtime_session.git_branch = original_git_branch
                stop_runtime_session.git_status_paths = original_git_status_paths


if __name__ == "__main__":
    unittest.main()
