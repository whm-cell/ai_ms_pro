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
    def test_render_darwin_and_linux_use_python_launcher_path(self) -> None:
        for system in ("Darwin", "Linux"):
            with self.subTest(system=system):
                rendered = render_hooks_config(root=ROOT, system=system)
                config = json.loads(rendered)
                pre_tool_commands = [
                    hook["command"] for hook in config["hooks"]["PreToolUse"][0]["hooks"]
                ]
                self.assertEqual(
                    pre_tool_commands,
                    [".codex/hooks/run_hook.py pre_tool_use_preflight.py"],
                )
                commands = [hook["command"] for hook in config["hooks"]["Stop"][0]["hooks"]]
                self.assertEqual(
                    commands,
                    [
                        ".codex/hooks/run_hook.py stop_runtime_observation.py",
                        ".codex/hooks/run_hook.py stop_runtime_session.py",
                        ".codex/hooks/run_hook.py stop_runtime_token_pressure.py",
                        ".codex/hooks/run_hook.py stop_loop_scope_monitor.py",
                        ".codex/hooks/run_hook.py stop_ai_docs_check.py",
                    ],
                )
                self.assertTrue(
                    all("powershell" not in command.lower() for command in [*pre_tool_commands, *commands])
                )

    def test_render_windows_uses_powershell_launcher(self) -> None:
        rendered = render_hooks_config(root=ROOT, system="Windows")
        config = json.loads(rendered)
        command = config["hooks"]["Stop"][0]["hooks"][0]["command"]
        self.assertIn("powershell -NoProfile -ExecutionPolicy Bypass -File", command)
        self.assertIn("run_hook.ps1", command)

    def test_bootstrap_uses_shared_renderer(self) -> None:
        rendered = bootstrap_harness.render_hooks_config()
        self.assertEqual(rendered, render_hooks_config(root=ROOT))


if __name__ == "__main__":
    unittest.main()
