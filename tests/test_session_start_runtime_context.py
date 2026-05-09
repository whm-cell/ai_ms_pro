from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex" / "hooks"))

import session_start_runtime_context  # noqa: E402


class SessionStartRuntimeContextTest(unittest.TestCase):
    def test_session_start_redacts_existing_runtime_session_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            session_dir = Path(tempdir) / "sessions"
            session_dir.mkdir()
            session_file = session_dir / "2026-05-08_main_main_session-sensitive.md"
            session_file.write_text(
                "\n".join(
                    [
                        "# Runtime Session 记录",
                        "",
                        "## 当前目标",
                        "",
                        "- Continue with token=secret-token-value for user@example.com",
                        "",
                        "## 下次 Resume 提示",
                        "",
                        "- Read /Users/alice/.codex/sessions/rollout-sensitive.jsonl",
                    ]
                ),
                encoding="utf-8",
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


if __name__ == "__main__":
    unittest.main()
