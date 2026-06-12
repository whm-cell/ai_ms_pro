#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path


def render_hooks_config(*, root: Path, system: str | None = None) -> str:
    runner_command = resolve_runner_command(root=root.resolve(), system=system)

    config = {
        "hooks": {
            "PreToolUse": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"{runner_command} pre_tool_use_preflight.py",
                            "statusMessage": "Checking tool preflight risks",
                            "timeout": 30,
                        }
                    ],
                }
            ],
            "SessionStart": [
                {
                    "matcher": "startup|resume",
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"{runner_command} session_start_runtime_context.py",
                            "statusMessage": "Loading runtime session context",
                            "timeout": 30,
                        }
                    ],
                }
            ],
            "Stop": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"{runner_command} stop_runtime_observation.py",
                            "statusMessage": "Capturing runtime observations",
                            "timeout": 30,
                        },
                        {
                            "type": "command",
                            "command": f"{runner_command} stop_runtime_session.py",
                            "statusMessage": "Persisting runtime session snapshot",
                            "timeout": 30,
                        },
                        {
                            "type": "command",
                            "command": f"{runner_command} stop_runtime_token_pressure.py",
                            "statusMessage": "Checking runtime token pressure",
                            "timeout": 30,
                        },
                        {
                            "type": "command",
                            "command": f"{runner_command} stop_loop_scope_monitor.py",
                            "statusMessage": "Checking loop and scope drift",
                            "timeout": 30,
                        },
                        {
                            "type": "command",
                            "command": f"{runner_command} stop_ai_docs_check.py",
                            "statusMessage": "Checking AI docs governance",
                            "timeout": 30,
                        },
                    ]
                }
            ],
        }
    }
    return json.dumps(config, ensure_ascii=False, indent=2) + "\n"


def resolve_runner_command(*, root: Path, system: str | None = None) -> str:
    _ = (root, system)
    return ".codex/hooks/run_hook.cmd"
