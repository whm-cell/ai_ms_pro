from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import bootstrap_harness  # noqa: E402
from hook_config_lib import render_hooks_config  # noqa: E402


class HooksConfigRenderTest(unittest.TestCase):
    def test_render_all_systems_use_portable_launcher_path(self) -> None:
        for system in ("Darwin", "Linux", "Windows"):
            with self.subTest(system=system):
                rendered = render_hooks_config(root=ROOT, system=system)
                config = json.loads(rendered)
                pre_tool_commands = [
                    hook["command"] for hook in config["hooks"]["PreToolUse"][0]["hooks"]
                ]
                session_start_commands = [
                    hook["command"] for hook in config["hooks"]["SessionStart"][0]["hooks"]
                ]
                self.assertEqual(
                    pre_tool_commands,
                    [".codex/hooks/run_hook.cmd pre_tool_use_preflight.py"],
                )
                self.assertEqual(
                    session_start_commands,
                    [
                        ".codex/hooks/run_hook.cmd session_start_runtime_context.py",
                        ".codex/hooks/run_hook.cmd session_start_env_template_sync.py",
                    ],
                )
                commands = [hook["command"] for hook in config["hooks"]["Stop"][0]["hooks"]]
                self.assertEqual(
                    commands,
                    [
                        ".codex/hooks/run_hook.cmd stop_runtime_observation.py",
                        ".codex/hooks/run_hook.cmd stop_runtime_session.py",
                        ".codex/hooks/run_hook.cmd stop_runtime_token_pressure.py",
                        ".codex/hooks/run_hook.cmd stop_loop_scope_monitor.py",
                        ".codex/hooks/run_hook.cmd stop_ai_docs_check.py",
                    ],
                )
                self.assertTrue(
                    all(
                        "powershell" not in command.lower()
                        for command in [*pre_tool_commands, *session_start_commands, *commands]
                    )
                )

    def test_render_output_is_system_independent(self) -> None:
        rendered = render_hooks_config(root=ROOT, system="Windows")
        self.assertEqual(rendered, render_hooks_config(root=ROOT, system="Darwin"))
        self.assertEqual(rendered, render_hooks_config(root=ROOT, system="Linux"))

    def test_bootstrap_uses_shared_renderer(self) -> None:
        rendered = bootstrap_harness.render_hooks_config()
        self.assertEqual(rendered, render_hooks_config(root=ROOT))


if __name__ == "__main__":
    unittest.main()
