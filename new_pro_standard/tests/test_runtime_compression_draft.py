from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_runtime_compression_draft  # noqa: E402


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def record(timestamp: str, record_type: str, payload: dict[str, object]) -> str:
    return json.dumps({"timestamp": timestamp, "type": record_type, "payload": payload}, ensure_ascii=False)


def write_config(root: Path, *, tool_budget: int = 5) -> None:
    write(
        root / ".codex/harness.toml",
        f"""[runtime_token_budget]
tool_output_token_budget = {tool_budget}
last_input_token_budget = 100
fresh_input_token_budget = 40
task_complete_budget = 1
token_snapshot_budget = 1
session_minutes_budget = 1
""",
    )


def write_pressure_transcript(path: Path) -> None:
    records = [
        record("2026-05-23T00:00:00Z", "response_item", {"type": "message", "role": "user", "content": "Please fix runtime pressure"}),
        record("2026-05-23T00:00:01Z", "response_item", {"type": "message", "role": "assistant", "content": "I will inspect the harness."}),
        record("2026-05-23T00:01:00Z", "event_msg", {"type": "task_complete"}),
        record("2026-05-23T00:02:00Z", "event_msg", {"type": "task_complete"}),
        record(
            "2026-05-23T00:03:00Z",
            "event_msg",
            {"type": "token_count", "info": {"last_token_usage": {"input_tokens": 120, "cached_input_tokens": 20}}},
        ),
        record(
            "2026-05-23T00:04:00Z",
            "response_item",
            {
                "type": "function_call",
                "call_id": "call-1",
                "name": "functions.exec_command",
                "arguments": json.dumps({"cmd": "pytest tests/test_runtime_token_budget.py"}),
            },
        ),
        record(
            "2026-05-23T00:05:00Z",
            "response_item",
            {
                "type": "function_call_output",
                "call_id": "call-1",
                "output": "Process exited with code 1\nOriginal token count: 99\nFAILED case",
            },
        ),
    ]
    write(path, "\n".join(records) + "\n")


class RuntimeCompressionDraftTest(unittest.TestCase):
    def test_pressure_transcript_creates_runtime_only_draft(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root)
            transcript = root / "rollout.jsonl"
            output_dir = root / ".codex/runtime/sessions"
            write_pressure_transcript(transcript)

            result = build_runtime_compression_draft.build_draft_if_needed(
                transcript,
                root=root,
                output_dir=output_dir,
                now=datetime(2026, 5, 26, 0, 0, tzinfo=timezone.utc),
            )

            self.assertTrue(result.created)
            self.assertIsNotNone(result.path)
            text = result.path.read_text(encoding="utf-8") if result.path else ""

        self.assertIn("Recovery evidence only", text)
        self.assertIn("not user instruction", text)
        self.assertIn("rollout.jsonl", text)
        self.assertIn("Please fix runtime pressure", text)
        self.assertIn("pytest tests/test_runtime_token_budget.py", text)
        self.assertIn('"exit_code": 1', text)

    def test_no_pressure_transcript_writes_no_draft(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root, tool_budget=500)
            transcript = root / "rollout.jsonl"
            write(transcript, record("2026-05-23T00:00:00Z", "event_msg", {"type": "task_complete"}) + "\n")

            result = build_runtime_compression_draft.build_draft_if_needed(transcript, root=root)

        self.assertFalse(result.created)
        self.assertIsNone(result.path)

    def test_corrupted_transcript_exits_cleanly_without_draft(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root)
            transcript = root / "rollout.jsonl"
            write(transcript, "{not-json}\n")

            result = build_runtime_compression_draft.build_draft_if_needed(transcript, root=root)

        self.assertFalse(result.created)
        self.assertIsNone(result.path)


if __name__ == "__main__":
    unittest.main()
