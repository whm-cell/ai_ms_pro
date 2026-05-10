from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex" / "hooks"))
sys.path.insert(0, str(ROOT / "scripts"))

import check_agent_trace_schema  # noqa: E402
import runtime_trace_producer  # noqa: E402
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

                trace_files = list((observation_dir / "agent-traces").glob("*.agent-trace.jsonl"))
                self.assertEqual(len(trace_files), 1)
                self.assertEqual(
                    check_agent_trace_schema.validate_trace(
                        check_agent_trace_schema.DEFAULT_SCHEMA,
                        trace_files[0],
                    ),
                    [],
                )
                trace_record = json.loads(trace_files[0].read_text(encoding="utf-8").strip())
                self.assertEqual(trace_record["schema_version"], "agent-trace/v1")
                self.assertIsNone(trace_record["parent_span_id"])
                self.assertTrue(trace_record["start_time"].endswith("Z"))
                self.assertEqual(trace_record["end_time"], trace_record["start_time"])
            finally:
                stop_runtime_observation.OBSERVATION_DIR = original_dir
                stop_runtime_observation.git_status_paths = original_git_status_paths

    def test_stop_trace_producer_uses_stable_ids_and_utc_timestamps(self) -> None:
        observation = {
            "timestamp": "2026-05-10T12:00:00+08:00",
            "event": "Stop",
            "source": "codex-stop-hook",
            "session_id": "session-stable-trace",
            "agent": "main",
            "changed_paths": [" docs/ai/working-context.md "],
            "changed_path_count": 1,
            "requirement_ids": [" REQ-001 "],
            "workstream_ids": [" WS-01 "],
        }

        first_record = runtime_trace_producer.build_stop_trace_record(observation)
        second_record = runtime_trace_producer.build_stop_trace_record(observation)

        self.assertEqual(first_record["trace_id"], second_record["trace_id"])
        self.assertEqual(first_record["span_id"], second_record["span_id"])
        self.assertEqual(first_record["start_time"], "2026-05-10T04:00:00Z")
        self.assertEqual(first_record["requirement_ids"], ["REQ-001"])
        self.assertEqual(first_record["workstream_ids"], ["WS-01"])
        self.assertEqual(first_record["attributes"]["changed_paths"], ["docs/ai/working-context.md"])
        self.assertNotIn("session_id", first_record["attributes"])
        self.assertNotIn("cwd", first_record["attributes"])

    def test_stop_trace_producer_filters_invalid_traceability_ids(self) -> None:
        observation = {
            "timestamp": "2026-05-10T12:00:00+08:00",
            "event": "Stop",
            "session_id": "session-invalid-ids",
            "agent": "main",
            "requirement_ids": ["REQ-001", "REQ-1", "not-a-req"],
            "workstream_ids": ["WS-01", "WS-1", "not-a-ws"],
        }

        record = runtime_trace_producer.build_stop_trace_record(observation)

        self.assertEqual(record["requirement_ids"], ["REQ-001"])
        self.assertEqual(record["workstream_ids"], ["WS-01"])

    def test_stop_observation_redacts_sensitive_prompt_and_transcript_path(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            observation_dir = Path(tempdir) / "observations"
            original_dir = stop_runtime_observation.OBSERVATION_DIR
            original_git_status_paths = stop_runtime_observation.git_status_paths
            try:
                stop_runtime_observation.OBSERVATION_DIR = observation_dir
                stop_runtime_observation.git_status_paths = lambda: ["docs/ai/working-context.md"]

                stop_runtime_observation.append_observation(
                    {
                        "session_id": "session-sensitive-observation",
                        "prompt": "Use password=plainsecret and sk-abcdefghijklmnopqrstuvwxyz123456 for user@example.com",
                        "transcript_path": "/Users/alice/.codex/sessions/rollout-sensitive.jsonl",
                    }
                )

                payload = json.loads(next(observation_dir.glob("*.jsonl")).read_text(encoding="utf-8").strip())
                rendered = json.dumps(payload, ensure_ascii=False)
                self.assertIn("[REDACTED_SECRET]", rendered)
                self.assertIn("[REDACTED_OPENAI_KEY]", rendered)
                self.assertIn("[REDACTED_EMAIL]", rendered)
                self.assertIn("[REDACTED_PATH]/rollout-sensitive.jsonl", rendered)
                self.assertNotIn("plainsecret", rendered)
                self.assertNotIn("sk-abcdefghijklmnopqrstuvwxyz123456", rendered)
                self.assertNotIn("user@example.com", rendered)
                self.assertNotIn("/Users/alice", rendered)
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

    def test_stop_session_redacts_sensitive_prompt_and_transcript_path(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            session_dir = Path(tempdir) / "sessions"
            original_dir = stop_runtime_session.SESSION_DIR
            original_git_branch = stop_runtime_session.git_branch
            original_git_status_paths = stop_runtime_session.git_status_paths
            try:
                stop_runtime_session.SESSION_DIR = session_dir
                stop_runtime_session.git_branch = lambda: "test-branch"
                stop_runtime_session.git_status_paths = lambda: ["docs/ai/working-context.md"]

                stop_runtime_session.write_session_snapshot(
                    {
                        "session_id": "session-sensitive-session",
                        "prompt": "Token token=secret-token-value and phone 13812345678",
                        "transcript_path": "/Users/alice/.codex/sessions/rollout-sensitive.jsonl",
                    }
                )

                text = next(session_dir.glob("*.md")).read_text(encoding="utf-8")
                self.assertIn("[REDACTED_SECRET]", text)
                self.assertIn("[REDACTED_PHONE]", text)
                self.assertIn("[REDACTED_PATH]/rollout-sensitive.jsonl", text)
                self.assertNotIn("secret-token-value", text)
                self.assertNotIn("13812345678", text)
                self.assertNotIn("/Users/alice", text)
            finally:
                stop_runtime_session.SESSION_DIR = original_dir
                stop_runtime_session.git_branch = original_git_branch
                stop_runtime_session.git_status_paths = original_git_status_paths


if __name__ == "__main__":
    unittest.main()
