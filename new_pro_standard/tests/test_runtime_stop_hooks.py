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
import runtime_traceability  # noqa: E402
import runtime_traceability_catalog  # noqa: E402
import stop_runtime_observation  # noqa: E402
import stop_runtime_session  # noqa: E402


class RuntimeStopHooksTest(unittest.TestCase):
    def setUp(self) -> None:
        self.original_catalog_root = runtime_traceability_catalog.ROOT
        self.original_runtime_root = runtime_traceability.ROOT
        self.original_matrix_path = runtime_traceability_catalog.TRACEABILITY_MATRIX_PATH
        self.original_workstream_dir = runtime_traceability_catalog.WORKSTREAM_DIR
        runtime_traceability.load_traceability_catalog.cache_clear()

    def tearDown(self) -> None:
        runtime_traceability_catalog.ROOT = self.original_catalog_root
        runtime_traceability.ROOT = self.original_runtime_root
        runtime_traceability_catalog.TRACEABILITY_MATRIX_PATH = self.original_matrix_path
        runtime_traceability_catalog.WORKSTREAM_DIR = self.original_workstream_dir
        runtime_traceability.load_traceability_catalog.cache_clear()

    def configure_temp_catalog(self, root: Path) -> None:
        matrix = root / "docs" / "requirements" / "traceability-matrix.md"
        workstream_dir = root / "docs" / "requirements" / "workstreams"
        (root / "apps" / "demo").mkdir(parents=True, exist_ok=True)
        matrix.parent.mkdir(parents=True, exist_ok=True)
        workstream_dir.mkdir(parents=True, exist_ok=True)
        matrix.write_text(
            "\n".join(
                [
                    "# 需求追踪矩阵",
                    "",
                    "## 矩阵",
                    "",
                    "| 原始文档 | 标准化需求 | 工作流 | 开发阶段 | 当前状态 | 验收/测试 |",
                    "| --- | --- | --- | --- | --- | --- |",
                    "| REQDOC-01 | REQ-001 | WS-01 | STAGE-00 | 待开始 | smoke |",
                ]
            ),
            encoding="utf-8",
        )
        (workstream_dir / "WS-01-demo.md").write_text(
            "\n".join(
                [
                    "# Demo Workstream",
                    "",
                    "工作流编号：WS-01",
                    "",
                    "## 主要模块",
                    "",
                    "- `apps/demo`",
                ]
            ),
            encoding="utf-8",
        )
        runtime_traceability_catalog.ROOT = root
        runtime_traceability.ROOT = root
        runtime_traceability_catalog.TRACEABILITY_MATRIX_PATH = matrix
        runtime_traceability_catalog.WORKSTREAM_DIR = workstream_dir
        runtime_traceability.load_traceability_catalog.cache_clear()

    def test_stop_observation_writes_sanitized_trace_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            temp_root = Path(tempdir)
            self.configure_temp_catalog(temp_root)
            observation_dir = temp_root / "observations"
            original_dir = stop_runtime_observation.OBSERVATION_DIR
            original_git_status_paths = stop_runtime_observation.git_status_paths
            try:
                stop_runtime_observation.OBSERVATION_DIR = observation_dir
                stop_runtime_observation.git_status_paths = lambda: ["apps/demo/main.py"]

                stop_runtime_observation.append_observation(
                    {
                        "session_id": "session-auto-observation",
                        "prompt": "Use password=plainsecret for user@example.com",
                        "transcript_path": "/Users/alice/.codex/sessions/rollout-sensitive.jsonl",
                    }
                )

                payload = json.loads(next(observation_dir.glob("*.jsonl")).read_text(encoding="utf-8").strip())
                rendered = json.dumps(payload, ensure_ascii=False)
                self.assertEqual(payload["requirement_ids"], ["REQ-001"])
                self.assertEqual(payload["workstream_ids"], ["WS-01"])
                self.assertEqual(payload["traceability_source"], "module-path")
                self.assertIn("[REDACTED_SECRET]", rendered)
                self.assertIn("[REDACTED_EMAIL]", rendered)
                self.assertIn("[REDACTED_PATH]/rollout-sensitive.jsonl", rendered)
                self.assertNotIn("plainsecret", rendered)
                self.assertNotIn("user@example.com", rendered)
                trace_file = next((observation_dir / "agent-traces").glob("*.agent-trace.jsonl"))
                self.assertEqual(
                    check_agent_trace_schema.validate_trace(
                        check_agent_trace_schema.DEFAULT_SCHEMA,
                        trace_file,
                    ),
                    [],
                )
            finally:
                stop_runtime_observation.OBSERVATION_DIR = original_dir
                stop_runtime_observation.git_status_paths = original_git_status_paths

    def test_stop_session_snapshot_uses_runtime_traceability(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            temp_root = Path(tempdir)
            self.configure_temp_catalog(temp_root)
            session_dir = temp_root / "sessions"
            original_dir = stop_runtime_session.SESSION_DIR
            original_git_branch = stop_runtime_session.git_branch
            original_git_status_paths = stop_runtime_session.git_status_paths
            try:
                stop_runtime_session.SESSION_DIR = session_dir
                stop_runtime_session.git_branch = lambda: "test-branch"
                stop_runtime_session.git_status_paths = lambda: ["apps/demo/main.py"]

                stop_runtime_session.write_session_snapshot({"session_id": "session-auto-session"})

                text = next(session_dir.glob("*.md")).read_text(encoding="utf-8")
                self.assertIn("- Requirement IDs：REQ-001", text)
                self.assertIn("- Workstream IDs：WS-01", text)
                self.assertIn("- Traceability Source：module-path", text)
                self.assertIn("## 行为护栏快照", text)
            finally:
                stop_runtime_session.SESSION_DIR = original_dir
                stop_runtime_session.git_branch = original_git_branch
                stop_runtime_session.git_status_paths = original_git_status_paths


if __name__ == "__main__":
    unittest.main()
