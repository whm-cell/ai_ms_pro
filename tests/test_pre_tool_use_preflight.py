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


def command_context(command: str) -> str:
    return pre_tool_use_preflight.build_additional_context(
        {
            "tool_name": "functions.exec_command",
            "tool_input": {"cmd": command},
        }
    )


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
        self.assertIn("Bounded alternatives:", context)
        self.assertIn("scripts/capture_tool_output.py", context)
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
        self.assertIn("git diff --stat", context)

    def test_rg_warning_suggests_bounded_searches(self) -> None:
        context = pre_tool_use_preflight.build_additional_context(
            {
                "tool_name": "functions.exec_command",
                "tool_input": {"cmd": "rg TODO ."},
            }
        )

        self.assertIn("Bounded alternatives:", context)
        self.assertIn("scripts/capture_tool_output.py", context)
        self.assertIn("rg -n -m 20 TODO .", context)
        self.assertIn("rg -l TODO .", context)

    def test_recursive_grep_warning_suggests_bounded_searches(self) -> None:
        context = pre_tool_use_preflight.build_additional_context(
            {
                "tool_name": "functions.exec_command",
                "tool_input": {"cmd": "grep -R TODO ."},
            }
        )

        self.assertIn("unbounded-large-output", context)
        self.assertIn("scripts/capture_tool_output.py", context)
        self.assertIn('grep -R -n -m 20 "pattern" path/', context)

    def test_secret_env_warning_is_distinct(self) -> None:
        context = pre_tool_use_preflight.build_additional_context(
            {
                "tool_name": "functions.exec_command",
                "tool_input": {"cmd": "env"},
            }
        )

        self.assertIn("sensitive-output", context)
        self.assertIn("printenv PATH", context)

    def test_token_budget_docs_do_not_trigger_sensitive_output(self) -> None:
        context = command_context("sed -n '1,260p' scripts/runtime_token_budget_core.py")

        self.assertIn("unbounded-large-output", context)
        self.assertNotIn("sensitive-output", context)
        self.assertEqual(
            command_context("sed -n '1,120p' .agents/skills/harness-maintenance/references/runtime-token-budget.md"),
            "",
        )

    def test_sensitive_token_file_read_still_warns(self) -> None:
        context = command_context("sed -n '1,20p' github-token.txt")

        self.assertIn("sensitive-output", context)
        self.assertIn("printenv PATH", context)

    def test_log_commands_warn_unless_bounded(self) -> None:
        context = pre_tool_use_preflight.build_additional_context(
            {
                "tool_name": "functions.exec_command",
                "tool_input": {"cmd": "docker logs api"},
            }
        )

        self.assertIn("unbounded-large-output", context)
        self.assertIn("scripts/capture_tool_output.py", context)
        self.assertIn("docker logs --tail 200 <container>", context)

        bounded = pre_tool_use_preflight.build_additional_context(
            {
                "tool_name": "functions.exec_command",
                "tool_input": {"cmd": "docker logs --tail 100 api"},
            }
        )
        self.assertEqual(bounded, "")

    def test_verbose_test_warning_uses_log_artifact(self) -> None:
        context = pre_tool_use_preflight.build_additional_context(
            {
                "tool_name": "functions.exec_command",
                "tool_input": {"cmd": "pytest -vv tests"},
            }
        )

        self.assertIn("long-running-output", context)
        self.assertIn("scripts/capture_tool_output.py", context)

    def test_numbered_full_file_read_warns_as_large_output(self) -> None:
        context = command_context("nl -ba docs/ai/handoffs/active/stage-04-profile-dev-published-writeback-sync.md")

        self.assertIn("unbounded-large-output", context)
        self.assertIn("numbered-output", context)
        self.assertIn("nl -ba <target-file> | sed -n '1,120p'", context)
        self.assertEqual(command_context("nl -ba docs/ai/plan.md | sed -n '90,160p'"), "")

    def test_large_sed_windows_and_dense_docs_warn(self) -> None:
        contexts = [
            command_context("sed -n '1,220p' docs/ai/plan.md"),
            command_context("sed -n '42,130p' docs/requirements/traceability-matrix.md"),
        ]

        for context in contexts:
            self.assertIn("unbounded-large-output", context)
            self.assertIn("sed -n '1,120p' <target-file>", context)

        self.assertEqual(command_context("sed -n '1,60p' docs/requirements/traceability-matrix.md"), "")

    def test_shell_glob_loop_warns_as_large_output(self) -> None:
        context = command_context("for f in docs/ai/adr/ADR-*.md; do sed -n '1,20p' \"$f\"; done")

        self.assertIn("unbounded-large-output", context)
        self.assertIn("loop-output", context)

    def test_common_project_large_output_commands_warn(self) -> None:
        commands = [
            "go test ./... -v",
            "mvn test",
            "make test",
            "pip install -v package",
            "tail -f app.log",
            "gh api --paginate repos/owner/repo/issues",
            "fd TODO .",
        ]
        for command in commands:
            with self.subTest(command=command):
                context = pre_tool_use_preflight.build_additional_context(
                    {
                        "tool_name": "functions.exec_command",
                        "tool_input": {"cmd": command},
                    }
                )

                self.assertIn("scripts/capture_tool_output.py", context)

    def test_capture_wrapper_command_is_silent(self) -> None:
        context = pre_tool_use_preflight.build_additional_context(
            {
                "tool_name": "functions.exec_command",
                "tool_input": {
                    "cmd": "python3 scripts/capture_tool_output.py --slug tests -- pytest -vv tests",
                },
            }
        )

        self.assertEqual(context, "")

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
