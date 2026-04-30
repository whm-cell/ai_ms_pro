from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex" / "hooks"))
sys.path.insert(0, str(ROOT / "scripts"))

import bootstrap_harness  # noqa: E402
import run_hook  # noqa: E402


def write_fake_python(directory: Path, name: str, version: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / name
    path.write_text(f"#!/bin/sh\nprintf '%s\\n' '{version}'\n", encoding="utf-8")
    path.chmod(0o755)
    return path


class PythonResolutionTest(unittest.TestCase):
    def test_run_hook_prefers_repo_venv_over_launcher_python(self) -> None:
        with mock.patch.object(run_hook.platform, "system", return_value="Darwin"):
            with mock.patch.object(run_hook, "python_prefixes", return_value=[Path("/repo/.codex/.venv")]):
                with mock.patch.object(
                    run_hook,
                    "python_candidates_for_prefix",
                    return_value=["/repo/.codex/.venv/bin/python"],
                ):
                    with mock.patch.object(run_hook, "python_can_run", return_value=True):
                        command = run_hook.resolve_python_command()

        self.assertEqual(command, ["/repo/.codex/.venv/bin/python"])

    def test_run_hook_chooses_path_python_311_over_macos_system_39(self) -> None:
        versions = {
            ("/usr/bin/python3",): (3, 9, 6),
            ("/Users/coolm/.pyenv/shims/python3",): (3, 11, 13),
        }

        def version_for(command: list[str]) -> tuple[int, int, int] | None:
            return versions.get(tuple(command))

        with mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch.object(run_hook.platform, "system", return_value="Darwin"):
                with mock.patch.object(run_hook, "python_prefixes", return_value=[]):
                    with mock.patch.object(
                        run_hook,
                        "all_commands_on_path",
                        return_value=[
                            "/usr/bin/python3",
                            "/Users/coolm/.pyenv/shims/python3",
                        ],
                    ):
                        with mock.patch.object(run_hook, "python_version", side_effect=version_for):
                            command = run_hook.resolve_python_command()

        self.assertEqual(command, ["/Users/coolm/.pyenv/shims/python3"])

    def test_bootstrap_chooses_path_python_311_over_launcher_python(self) -> None:
        versions = {
            ("/usr/bin/python3",): (3, 9, 6),
            ("/Users/coolm/.pyenv/shims/python3",): (3, 11, 13),
            (sys.executable,): (3, 9, 6),
        }

        def version_for(command: list[str]) -> tuple[int, int, int] | None:
            return versions.get(tuple(command))

        with mock.patch.dict(os.environ, {}, clear=True):
            with mock.patch.object(
                bootstrap_harness,
                "all_commands_on_path",
                return_value=[
                    "/usr/bin/python3",
                    "/Users/coolm/.pyenv/shims/python3",
                ],
            ):
                with mock.patch.object(bootstrap_harness, "python_version", side_effect=version_for):
                    command = bootstrap_harness.resolve_bootstrap_python(None)

        self.assertEqual(command, ["/Users/coolm/.pyenv/shims/python3"])

    def test_run_hook_windows_path_scans_python_exe_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old_python = write_fake_python(root / "old", "python.exe", "3.9.6")
            new_python = write_fake_python(root / "new", "python.exe", "3.11.13")
            path_value = os.pathsep.join([str(old_python.parent), str(new_python.parent)])

            with mock.patch.dict(os.environ, {"PATH": path_value, "PATHEXT": ".EXE"}, clear=True):
                with mock.patch.object(run_hook.platform, "system", return_value="Windows"):
                    with mock.patch.object(run_hook, "python_prefixes", return_value=[]):
                        command = run_hook.resolve_python_command()

        self.assertEqual(command, [str(new_python)])

    def test_bootstrap_windows_path_scans_python_exe_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old_python = write_fake_python(root / "old", "python.exe", "3.9.6")
            new_python = write_fake_python(root / "new", "python.exe", "3.11.13")
            path_value = os.pathsep.join([str(old_python.parent), str(new_python.parent)])

            with mock.patch.dict(os.environ, {"PATH": path_value, "PATHEXT": ".EXE"}, clear=True):
                with mock.patch.object(bootstrap_harness, "is_windows_host", return_value=True):
                    command = bootstrap_harness.resolve_bootstrap_python(None)

        self.assertEqual(command, [str(new_python)])

    def test_powershell_runners_use_version_scored_fallback(self) -> None:
        runner_paths = [
            ROOT / ".codex" / "hooks" / "run_with_repo_python.ps1",
            ROOT / "new_pro_standard" / ".codex" / "hooks" / "run_with_repo_python.ps1",
        ]

        for path in runner_paths:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertIn("Get-PythonVersionScore", text)
                self.assertIn("Select-BestPythonCommand", text)
                self.assertIn('foreach ($name in @("python3", "python"))', text)
                self.assertIn('New-PythonCommand -Command $py.Source -Args @("-3")', text)
                self.assertIn("Get-CommonWindowsPythonCandidates", text)


if __name__ == "__main__":
    unittest.main()
