from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_runtime_token_budget  # noqa: E402


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def record(timestamp: str, record_type: str, payload: dict[str, object]) -> str:
    return json.dumps(
        {
            "timestamp": timestamp,
            "type": record_type,
            "payload": payload,
        },
        ensure_ascii=False,
    )


class RuntimeTokenBudgetTest(unittest.TestCase):
    def test_flags_large_tool_outputs_and_cache_miss(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / ".codex/harness.toml",
                """[runtime_token_budget]
tool_output_token_budget = 5
last_input_token_budget = 100
fresh_input_token_budget = 40
task_complete_budget = 1
token_snapshot_budget = 1
session_minutes_budget = 1
""",
            )
            transcript = root / "rollout.jsonl"
            write(
                transcript,
                "\n".join(
                    [
                        record(
                            "2026-05-21T00:00:00Z",
                            "event_msg",
                            {"type": "task_complete"},
                        ),
                        record(
                            "2026-05-21T00:01:00Z",
                            "event_msg",
                            {"type": "task_complete"},
                        ),
                        record(
                            "2026-05-21T00:02:00Z",
                            "event_msg",
                            {
                                "type": "token_count",
                                "info": {
                                    "last_token_usage": {
                                        "input_tokens": 120,
                                        "cached_input_tokens": 20,
                                    }
                                },
                            },
                        ),
                        record(
                            "2026-05-21T00:03:00Z",
                            "event_msg",
                            {
                                "type": "token_count",
                                "info": {
                                    "last_token_usage": {
                                        "input_tokens": 80,
                                        "cached_input_tokens": 70,
                                    }
                                },
                            },
                        ),
                        record(
                            "2026-05-21T00:04:00Z",
                            "response_item",
                            {
                                "type": "function_call",
                                "call_id": "call-1",
                                "name": "exec_command",
                                "arguments": '{"cmd":"rg broad"}',
                            },
                        ),
                        record(
                            "2026-05-21T00:05:00Z",
                            "response_item",
                            {
                                "type": "function_call_output",
                                "call_id": "call-1",
                                "output": "Original token count: 99\nOutput: very large",
                            },
                        ),
                    ]
                )
                + "\n",
            )

            report = check_runtime_token_budget.build_report(
                root=root,
                transcript_paths=[transcript],
            )

        warning_text = "\n".join(report.warnings)
        self.assertIn("last input tokens exceeded budget", warning_text)
        self.assertIn("fresh input tokens exceeded budget", warning_text)
        self.assertIn("task_complete count exceeded budget", warning_text)
        self.assertIn("token snapshot count exceeded budget", warning_text)
        self.assertIn("elapsed minutes exceeded budget", warning_text)
        self.assertIn("tool output exceeded budget", warning_text)
        self.assertEqual(report.transcripts[0].max_tool_output_tokens, 99)
        self.assertEqual(report.transcripts[0].tool_output_findings[0].tool_name, "exec_command")

    def test_no_transcript_is_ci_wiring_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = check_runtime_token_budget.build_report(root=Path(tmp))

        self.assertEqual(report.transcripts, [])
        self.assertEqual(report.warnings, [])
        self.assertIn("no transcript paths supplied", check_runtime_token_budget.render_report(report))


if __name__ == "__main__":
    unittest.main()
