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
import python_runtime_selector  # noqa: E402
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

    def test_bootstrap_uses_parent_env_python_before_path_python(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            root = parent / "project"
            root.mkdir()
            env_python = write_fake_python(parent, "python-from-env", "3.12.11")
            (parent / ".env").write_text(
                f"CODEX_HARNESS_PYTHON={env_python}\n",
                encoding="utf-8",
            )
            versions = {(str(env_python),): (3, 12, 11)}

            with mock.patch.dict(os.environ, {}, clear=True):
                with mock.patch.object(bootstrap_harness, "ROOT", root):
                    with mock.patch.object(bootstrap_harness, "all_commands_on_path", return_value=[]):
                        with mock.patch.object(
                            bootstrap_harness,
                            "python_version",
                            side_effect=lambda command: versions.get(tuple(command)),
                        ):
                            with mock.patch.object(
                                bootstrap_harness,
                                "is_runnable_python",
                                side_effect=lambda command: command == [str(env_python)],
                            ):
                                command = bootstrap_harness.resolve_bootstrap_python(None)

        self.assertEqual(command, [str(env_python)])

    def test_bootstrap_uses_parent_env_pyenv_version_before_system_python(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            root = parent / "project"
            root.mkdir()
            pyenv_python = write_fake_python(parent, "pyenv-python", "3.12.11")
            (parent / ".env").write_text("PYENV_VERSION=3.12.11\n", encoding="utf-8")
            versions = {
                (str(pyenv_python),): (3, 12, 11),
                ("/usr/bin/python3",): (3, 9, 6),
            }

            with mock.patch.dict(os.environ, {}, clear=True):
                with mock.patch.object(bootstrap_harness, "ROOT", root):
                    with mock.patch.object(
                        bootstrap_harness,
                        "pyenv_python_commands",
                        return_value=[[str(pyenv_python)]],
                    ):
                        with mock.patch.object(
                            bootstrap_harness,
                            "all_commands_on_path",
                            return_value=["/usr/bin/python3"],
                        ):
                            with mock.patch.object(
                                bootstrap_harness,
                                "python_version",
                                side_effect=lambda command: versions.get(tuple(command)),
                            ):
                                command = bootstrap_harness.resolve_bootstrap_python(None)

        self.assertEqual(command, [str(pyenv_python)])

    def test_runtime_selector_reads_parent_env_pyenv_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            root = parent / "project"
            root.mkdir()
            pyenv_python = write_fake_python(parent, "pyenv-python", "3.12.11")
            (parent / ".env").write_text("PYENV_VERSION=3.12.11\n", encoding="utf-8")

            def pyenv_for(root_arg: Path, version: str | None) -> list[str] | None:
                self.assertEqual(root_arg, root)
                if version == "3.12.11":
                    return [str(pyenv_python)]
                return None

            with mock.patch.object(
                python_runtime_selector,
                "pyenv_python_command",
                side_effect=pyenv_for,
            ):
                commands = python_runtime_selector.pyenv_python_commands(root)

        self.assertEqual(commands, [[str(pyenv_python)]])

    def test_run_hook_windows_path_scans_python_exe_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old_python = write_fake_python(root / "old", "python.exe", "3.9.6")
            new_python = write_fake_python(root / "new", "python.exe", "3.11.13")
            path_value = os.pathsep.join([str(old_python.parent), str(new_python.parent)])
            versions = {
                (str(old_python),): (3, 9, 6),
                (str(new_python),): (3, 11, 13),
            }

            with mock.patch.dict(os.environ, {"PATH": path_value, "PATHEXT": ".EXE"}, clear=True):
                with mock.patch.object(run_hook.platform, "system", return_value="Windows"):
                    with mock.patch.object(run_hook, "python_prefixes", return_value=[]):
                        with mock.patch.object(
                            run_hook,
                            "all_commands_on_path",
                            return_value=[str(old_python), str(new_python)],
                        ):
                            with mock.patch.object(
                                run_hook,
                                "python_version",
                                side_effect=lambda command: versions.get(tuple(command)),
                            ):
                                command = run_hook.resolve_python_command()

        self.assertEqual(command, [str(new_python)])

    def test_bootstrap_windows_path_scans_python_exe_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old_python = write_fake_python(root / "old", "python.exe", "3.9.6")
            new_python = write_fake_python(root / "new", "python.exe", "3.11.13")
            path_value = os.pathsep.join([str(old_python.parent), str(new_python.parent)])
            versions = {
                (str(old_python),): (3, 9, 6),
                (str(new_python),): (3, 11, 13),
            }

            with mock.patch.dict(os.environ, {"PATH": path_value, "PATHEXT": ".EXE"}, clear=True):
                with mock.patch.object(bootstrap_harness, "is_windows_host", return_value=True):
                    with mock.patch.object(
                        bootstrap_harness,
                        "all_commands_on_path",
                        return_value=[str(old_python), str(new_python)],
                    ):
                        with mock.patch.object(
                            bootstrap_harness,
                            "python_version",
                            side_effect=lambda command: versions.get(tuple(command)),
                        ):
                            command = bootstrap_harness.resolve_bootstrap_python(None)

        self.assertEqual(command, [str(new_python)])

    def test_powershell_runners_use_version_scored_fallback(self) -> None:
        runner_paths = [
            ROOT / ".codex" / "hooks" / "run_with_repo_python.ps1",
        ]
        starter_runner = ROOT / "new_pro_standard" / ".codex" / "hooks" / "run_with_repo_python.ps1"
        if starter_runner.exists():
            runner_paths.append(starter_runner)

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
