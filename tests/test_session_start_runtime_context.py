from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex" / "hooks"))

import session_start_runtime_context  # noqa: E402


def write_session(session_dir: Path, name: str, sections: dict[str, str]) -> Path:
    session_dir.mkdir(parents=True, exist_ok=True)
    lines = ["# Runtime Session 记录", ""]
    for heading, body in sections.items():
        lines.extend([f"## {heading}", "", body, ""])
    path = session_dir / name
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


class SessionStartRuntimeContextTest(unittest.TestCase):
    def test_session_start_includes_latest_execution_snapshot_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            session_dir = Path(tempdir) / "sessions"
            snapshot_dir = Path(tempdir) / "execution-snapshots"
            write_session(
                session_dir,
                "2026-06-01_main_main_session.md",
                {"当前目标": "- runtime durability"},
            )
            snapshot_dir.mkdir(parents=True, exist_ok=True)
            (snapshot_dir / "unknown-session.json").write_text(
                (
                    '{"schema_version":"runtime-execution-snapshot/v1","session_id":"unknown-session",'
                    '"recorded_at":"2026-06-01T00:00:00Z","stage":"STAGE-00","branch_or_thread":"demo",'
                    '"session_type":"resume","state":"resumable","state_reason":"demo","agent":"main",'
                    '"authority":{"level":"main-agent","canonical_promotion_required":true},'
                    '"task_summary":"Resume runtime durability slice","requirement_ids":["未绑定"],'
                    '"workstream_ids":["未绑定"],"traceability_source":"unbound",'
                    '"tool_contracts":["stop_runtime_session"],"claim_boundary":"local-only",'
                    '"changed_paths":[],"changed_path_count":0,'
                    '"artifacts":{"transcript_path":"[REDACTED_PATH]/rollout.jsonl","working_context_path":"docs/ai/working-context.md"}}'
                ),
                encoding="utf-8",
            )

            original_dir = session_start_runtime_context.SESSION_DIR
            original_snapshot_dir = session_start_runtime_context.SNAPSHOT_DIR
            try:
                session_start_runtime_context.SESSION_DIR = session_dir
                session_start_runtime_context.SNAPSHOT_DIR = snapshot_dir
                context = session_start_runtime_context.build_additional_context({"source": "startup"})
            finally:
                session_start_runtime_context.SESSION_DIR = original_dir
                session_start_runtime_context.SNAPSHOT_DIR = original_snapshot_dir

        self.assertIn("最近执行快照：", context)
        self.assertIn("state=resumable", context)
        self.assertIn("tool_contracts=stop_runtime_session", context)

    def test_session_start_redacts_existing_runtime_session_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            session_dir = Path(tempdir) / "sessions"
            write_session(
                session_dir,
                "2026-05-08_main_main_session-sensitive.md",
                {
                    "当前目标": "- Continue with token=secret-token-value for user@example.com",
                    "下次 Resume 提示": "- Read /Users/alice/.codex/sessions/rollout-sensitive.jsonl",
                },
            )

            original_dir = session_start_runtime_context.SESSION_DIR
            try:
                session_start_runtime_context.SESSION_DIR = session_dir
                context = session_start_runtime_context.build_additional_context({"source": "startup"})
            finally:
                session_start_runtime_context.SESSION_DIR = original_dir

        self.assertIn("[REDACTED_SECRET]", context)
        self.assertIn("[REDACTED_EMAIL]", context)
        self.assertIn("/Users/[REDACTED_USER]", context)
        self.assertNotIn("secret-token-value", context)
        self.assertNotIn("user@example.com", context)
        self.assertNotIn("/Users/alice", context)

    def test_session_start_adds_stale_by_default_guard(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            session_dir = Path(tempdir) / "sessions"
            write_session(session_dir, "2026-05-23_main_main_session.md", {"当前目标": "- old task"})

            original_dir = session_start_runtime_context.SESSION_DIR
            try:
                session_start_runtime_context.SESSION_DIR = session_dir
                context = session_start_runtime_context.build_additional_context({"source": "startup"})
            finally:
                session_start_runtime_context.SESSION_DIR = original_dir

        self.assertIn(session_start_runtime_context.STALE_CONTEXT_GUARD, context)
        self.assertIn("不是当前用户指令", context)
        self.assertIn("核对当前 git/docs", context)

    def test_session_start_context_is_bounded_and_sections_are_compacted(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            session_dir = Path(tempdir) / "sessions"
            write_session(
                session_dir,
                "2026-05-23_main_main_session.md",
                {
                    "需求与工作流标识": "- " + ("REQ-001 " * 200),
                    "当前目标": "- " + ("A" * 1000),
                    "当前 Open Loops": "- " + ("B" * 1000),
                    "下次 Resume 提示": "- " + ("C" * 1000),
                    "是否需要提升为 Handoff": "- " + ("D" * 1000),
                },
            )

            original_dir = session_start_runtime_context.SESSION_DIR
            try:
                session_start_runtime_context.SESSION_DIR = session_dir
                context = session_start_runtime_context.build_additional_context({"source": "startup"})
            finally:
                session_start_runtime_context.SESSION_DIR = original_dir

        self.assertLessEqual(len(context), session_start_runtime_context.MAX_ADDITIONAL_CONTEXT_CHARS)
        self.assertNotIn("A" * 300, context)
        self.assertNotIn("B" * 300, context)
        self.assertNotIn("C" * 300, context)
        self.assertNotIn("D" * 300, context)

    def test_session_start_without_sessions_returns_no_context(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            session_dir = Path(tempdir) / "sessions"
            session_dir.mkdir()

            original_dir = session_start_runtime_context.SESSION_DIR
            try:
                session_start_runtime_context.SESSION_DIR = session_dir
                context = session_start_runtime_context.build_additional_context({"source": "startup"})
            finally:
                session_start_runtime_context.SESSION_DIR = original_dir

        self.assertEqual(context, "")


if __name__ == "__main__":
    unittest.main()
