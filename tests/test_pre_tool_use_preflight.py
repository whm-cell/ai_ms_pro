from __future__ import annotations

import io
import json
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex" / "hooks"))

import pre_tool_use_preflight  # noqa: E402


class PreToolUsePreflightTest(unittest.TestCase):
    def test_flags_unbounded_large_output_command(self) -> None:
        context = pre_tool_use_preflight.build_additional_context(
            {
                "tool_name": "functions.exec_command",
                "tool_input": {"cmd": "ps -axo pid,ppid,command"},
            }
        )

        self.assertIn("Pre-tool advisory", context)
        self.assertIn("Likely large output", context)
        self.assertIn("Finding codes: `unbounded-large-output`", context)
        self.assertIn("check_harness_placeholder_replacement.py <candidate-jsonl>", context)
        self.assertIn(".codex/runtime/tool-outputs/", context)
        self.assertLessEqual(len(context), pre_tool_use_preflight.MAX_ADDITIONAL_CONTEXT_CHARS)

    def test_bounded_large_output_command_is_silent(self) -> None:
        context = pre_tool_use_preflight.build_additional_context(
            {
                "tool_name": "functions.exec_command",
                "tool_input": {
                    "cmd": "ps -axo pid,ppid,command",
                    "max_output_tokens": 1000,
                },
            }
        )

        self.assertEqual(context, "")

    def test_artifact_redirect_large_output_command_is_silent(self) -> None:
        context = pre_tool_use_preflight.build_additional_context(
            {
                "toolName": "functions.exec_command",
                "toolInput": {
                    "cmd": "git diff > .codex/runtime/tool-outputs/20260523-diff.log",
                },
            }
        )

        self.assertEqual(context, "")

    def test_flags_destructive_command_without_blocking(self) -> None:
        context = pre_tool_use_preflight.build_additional_context(
            {
                "tool_name": "functions.exec_command",
                "tool_input": {"cmd": "rm -rf build/cache"},
            }
        )
        output = json.loads(pre_tool_use_preflight.render_hook_output(context))

        self.assertIn("Destructive", context)
        self.assertNotIn("continue", output)
        self.assertEqual(output["hookSpecificOutput"]["hookEventName"], "PreToolUse")

    def test_flags_external_send_tool(self) -> None:
        context = pre_tool_use_preflight.build_additional_context(
            {
                "tool_name": "slack_send_message",
                "tool_input": {"channel": "#general", "text": "ship it"},
            }
        )

        self.assertIn("Externally visible", context)
        self.assertIn("draft", context)

    def test_plain_bounded_command_is_silent(self) -> None:
        context = pre_tool_use_preflight.build_additional_context(
            {
                "tool_name": "functions.exec_command",
                "tool_input": {"cmd": "python3 tests/test_runtime_token_budget.py"},
            }
        )

        self.assertEqual(context, "")

    def test_json_string_arguments_are_supported(self) -> None:
        context = pre_tool_use_preflight.build_additional_context(
            {
                "name": "functions.exec_command",
                "arguments": json.dumps({"cmd": "git diff"}),
            }
        )

        self.assertIn("Likely large output", context)
        self.assertIn("git diff", context)

    def test_main_without_findings_prints_nothing_and_exits_zero(self) -> None:
        original_stdin = sys.stdin
        try:
            sys.stdin = io.StringIO(
                json.dumps(
                    {
                        "tool_name": "functions.exec_command",
                        "tool_input": {"cmd": "python3 tests/test_runtime_token_budget.py"},
                    }
                )
            )
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                exit_code = pre_tool_use_preflight.main()
        finally:
            sys.stdin = original_stdin

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
