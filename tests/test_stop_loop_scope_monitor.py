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

import stop_loop_scope_monitor  # noqa: E402


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def record(record_type: str, payload: dict[str, object]) -> str:
    return json.dumps({"type": record_type, "payload": payload}, ensure_ascii=False)


def tool_call(call_id: str, command: str) -> str:
    return record(
        "response_item",
        {
            "type": "function_call",
            "call_id": call_id,
            "name": "exec_command",
            "arguments": json.dumps({"cmd": command}),
        },
    )


def tool_output(call_id: str, output: str) -> str:
    return record(
        "response_item",
        {
            "type": "function_call_output",
            "call_id": call_id,
            "output": output,
        },
    )


class StopLoopScopeMonitorTest(unittest.TestCase):
    def test_flags_repeated_command_without_raw_output(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            transcript = Path(tempdir) / "rollout.jsonl"
            write(
                transcript,
                "\n".join(
                    [
                        tool_call("call-1", "python3 tests/test_runtime_token_budget.py"),
                        tool_output("call-1", "ok"),
                        tool_call("call-2", "python3 tests/test_runtime_token_budget.py"),
                        tool_output("call-2", "ok"),
                        tool_call("call-3", "python3 tests/test_runtime_token_budget.py"),
                        tool_output("call-3", "ok"),
                    ]
                )
                + "\n",
            )

            context = stop_loop_scope_monitor.build_additional_context(
                {"transcript_path": str(transcript)},
                root=Path(tempdir),
            )

        self.assertIn("Repeated tool command 3x", context)
        self.assertIn("python3 tests/test_runtime_token_budget.py", context)
        self.assertIn("Finding codes: `repeated-command`", context)
        self.assertIn("Recommended sample actions: `inspect-repeated-command`", context)
        self.assertIn("check_harness_placeholder_replacement.py <candidate-jsonl>", context)
        self.assertLessEqual(len(context), stop_loop_scope_monitor.MAX_ADDITIONAL_CONTEXT_CHARS)

    def test_flags_repeated_failed_output(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            transcript = Path(tempdir) / "rollout.jsonl"
            write(
                transcript,
                "\n".join(
                    [
                        tool_call("call-1", "pytest tests/test_demo.py"),
                        tool_output("call-1", "FAILED tests/test_demo.py::test_demo"),
                        tool_call("call-2", "pytest tests/test_demo.py"),
                        tool_output("call-2", "FAILED tests/test_demo.py::test_demo"),
                    ]
                )
                + "\n",
            )

            context = stop_loop_scope_monitor.build_additional_context(
                {"transcriptPath": str(transcript)},
                root=Path(tempdir),
            )

        self.assertIn("Repeated failed output 2x", context)
        self.assertIn("pytest tests/test_demo.py", context)

    def test_flags_validation_loop(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            transcript = Path(tempdir) / "rollout.jsonl"
            lines = []
            for index in range(6):
                lines.append(tool_call(f"call-{index}", f"python3 tests/test_{index}.py"))
                lines.append(tool_output(f"call-{index}", "ok"))
            write(transcript, "\n".join(lines) + "\n")

            context = stop_loop_scope_monitor.build_additional_context(
                {"transcript_path": str(transcript)},
                root=Path(tempdir),
            )

        self.assertIn("Validation/test commands ran 6 times", context)

    def test_flags_prompt_churn(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            transcript = Path(tempdir) / "rollout.jsonl"
            write(
                transcript,
                "\n".join(
                    record("event_msg", {"prompt": f"new unrelated task {index}"})
                    for index in range(4)
                )
                + "\n",
            )

            context = stop_loop_scope_monitor.build_additional_context(
                {"transcript_path": str(transcript)},
                root=Path(tempdir),
            )

        self.assertIn("Multiple distinct user/task prompt clusters", context)

    def test_missing_transcript_and_no_findings_are_silent(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            missing = stop_loop_scope_monitor.build_additional_context(
                {"transcript_path": str(root / "missing.jsonl")},
                root=root,
            )
            transcript = root / "rollout.jsonl"
            write(transcript, tool_call("call-1", "python3 tests/test_runtime_token_budget.py") + "\n")
            clean = stop_loop_scope_monitor.build_additional_context(
                {"transcript_path": str(transcript)},
                root=root,
            )

        self.assertEqual(missing, "")
        self.assertEqual(clean, "")

    def test_main_without_transcript_prints_nothing_and_exits_zero(self) -> None:
        original_stdin = sys.stdin
        try:
            sys.stdin = io.StringIO("{}")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = stop_loop_scope_monitor.main()
        finally:
            sys.stdin = original_stdin

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), "")

    def test_hook_output_is_warning_only(self) -> None:
        output = json.loads(stop_loop_scope_monitor.render_hook_output("context"))

        self.assertEqual(output["hookSpecificOutput"]["hookEventName"], "Stop")
        self.assertEqual(output["hookSpecificOutput"]["additionalContext"], "context")
        self.assertNotIn("continue", output)


if __name__ == "__main__":
    unittest.main()
