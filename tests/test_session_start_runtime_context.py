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
                    "需求与工作流标识": "- " + ("REQ-010 " * 200),
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
