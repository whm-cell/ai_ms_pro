from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex" / "hooks"))

import stop_runtime_token_pressure  # noqa: E402


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


def write_pressure_transcript(path: Path, *, large_outputs: int = 1) -> None:
    records = [
        record("2026-05-23T00:00:00Z", "event_msg", {"type": "task_complete"}),
        record("2026-05-23T00:01:00Z", "event_msg", {"type": "task_complete"}),
        record(
            "2026-05-23T00:02:00Z",
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
            "2026-05-23T00:03:00Z",
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
    ]
    for index in range(large_outputs):
        call_id = f"call-{index}"
        records.append(
            record(
                "2026-05-23T00:04:00Z",
                "response_item",
                {
                    "type": "function_call",
                    "call_id": call_id,
                    "name": "exec_command",
                    "arguments": '{"cmd":"full log"}',
                },
            )
        )
        records.append(
            record(
                "2026-05-23T00:05:00Z",
                "response_item",
                {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": f"Original token count: {99 + index}\nFULL_LOG_SHOULD_NOT_APPEAR",
                },
            )
        )
    write(path, "\n".join(records) + "\n")


class StopRuntimeTokenPressureTest(unittest.TestCase):
    def test_emits_bounded_additional_context_without_raw_output(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            write_config(root)
            transcript = root / "rollout.jsonl"
            write_pressure_transcript(transcript)

            context = stop_runtime_token_pressure.build_additional_context(
                {"transcript_path": str(transcript)},
                root=root,
            )

        self.assertIn("Runtime token pressure detected", context)
        self.assertIn("Runtime compression draft", context)
        self.assertIn("Draft:", context)
        self.assertIn("runtime-only recovery draft", context)
        self.assertNotIn("FULL_LOG_SHOULD_NOT_APPEAR", context)
        self.assertLessEqual(len(context), stop_runtime_token_pressure.MAX_ADDITIONAL_CONTEXT_CHARS)

        output = json.loads(stop_runtime_token_pressure.render_hook_output(context))
        self.assertEqual(output["hookSpecificOutput"]["hookEventName"], "Stop")
        self.assertEqual(output["hookSpecificOutput"]["additionalContext"], context)
        self.assertNotIn("continue", output)

    def test_writes_runtime_compression_draft_for_pressure(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            write_config(root)
            transcript = root / "rollout.jsonl"
            write_pressure_transcript(transcript, large_outputs=5)

            context = stop_runtime_token_pressure.build_additional_context(
                {"transcriptPath": str(transcript)},
                root=root,
            )

            drafts = list((root / ".codex/runtime/sessions").glob("*_runtime-compression.md"))

        self.assertIn("Draft:", context)
        self.assertEqual(len(drafts), 1)

    def test_missing_transcript_is_silent(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            context = stop_runtime_token_pressure.build_additional_context(
                {"transcript_path": str(Path(tempdir) / "missing.jsonl")},
                root=Path(tempdir),
            )

        self.assertEqual(context, "")

    def test_no_warnings_is_silent(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            write_config(root, tool_budget=500)
            transcript = root / "rollout.jsonl"
            write(
                transcript,
                record(
                    "2026-05-23T00:00:00Z",
                    "event_msg",
                    {
                        "type": "token_count",
                        "info": {
                            "last_token_usage": {
                                "input_tokens": 10,
                                "cached_input_tokens": 9,
                            }
                        },
                    },
                )
                + "\n",
            )

            context = stop_runtime_token_pressure.build_additional_context(
                {"transcript_path": str(transcript)},
                root=root,
            )

        self.assertEqual(context, "")

    def test_corrupted_transcript_is_silent(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            write_config(root)
            transcript = root / "rollout.jsonl"
            write(transcript, "{not-json}\n")

            context = stop_runtime_token_pressure.build_additional_context(
                {"transcript_path": str(transcript)},
                root=root,
            )

        self.assertEqual(context, "")

    def test_main_without_transcript_prints_nothing_and_exits_zero(self) -> None:
        original_stdin = sys.stdin
        try:
            sys.stdin = io.StringIO("{}")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = stop_runtime_token_pressure.main()
        finally:
            sys.stdin = original_stdin

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
