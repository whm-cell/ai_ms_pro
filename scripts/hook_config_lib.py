#!/usr/bin/env python3

from __future__ import annotations

import json
import platform
from pathlib import Path


def render_hooks_config(*, root: Path, system: str | None = None) -> str:
    resolved_root = root.resolve()
    current_system = (system or platform.system()).strip() or platform.system()
    runner_command = resolve_runner_command(root=resolved_root, system=current_system)

    config = {
        "hooks": {
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


def resolve_runner_command(*, root: Path, system: str) -> str:
    normalized_system = system.lower()
    if normalized_system == "windows":
        return "powershell -NoProfile -ExecutionPolicy Bypass -File .codex/hooks/run_hook.ps1"
    return ".codex/hooks/run_hook.py"
