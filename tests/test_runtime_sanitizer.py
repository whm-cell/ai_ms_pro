from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex" / "hooks"))

import runtime_sanitizer  # noqa: E402


class RuntimeSanitizerTest(unittest.TestCase):
    def test_redacts_common_secrets_and_contact_details(self) -> None:
        text = (
            "password=plainsecret api_key=plain-api-key "
            "sk-abcdefghijklmnopqrstuvwxyz123456 user@example.com 13812345678"
        )

        redacted = runtime_sanitizer.compact_text(text)

        self.assertIn("[REDACTED_SECRET]", redacted)
        self.assertIn("[REDACTED_OPENAI_KEY]", redacted)
        self.assertIn("[REDACTED_EMAIL]", redacted)
        self.assertIn("[REDACTED_PHONE]", redacted)
        self.assertNotIn("plainsecret", redacted)
        self.assertNotIn("plain-api-key", redacted)
        self.assertNotIn("sk-abcdefghijklmnopqrstuvwxyz123456", redacted)
        self.assertNotIn("user@example.com", redacted)
        self.assertNotIn("13812345678", redacted)

    def test_transcript_path_keeps_only_redacted_tail(self) -> None:
        redacted = runtime_sanitizer.compact_transcript_path(
            "/Users/alice/.codex/sessions/2026/05/08/rollout-sensitive.jsonl"
        )

        self.assertEqual(redacted, "[REDACTED_PATH]/rollout-sensitive.jsonl")


if __name__ == "__main__":
    unittest.main()
