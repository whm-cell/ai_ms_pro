from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_config_contract  # noqa: E402


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_config(root: Path, body: str) -> None:
    write(root / ".codex/harness.toml", "[config_contracts]\n" + body)


class ConfigContractTest(unittest.TestCase):
    def test_registry_path_escape_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(
                root,
                """enabled = true
registry_paths = ["../outside.ts"]
scan_roots = []
allowed_literal_paths = []
env_template_paths = []
local_env_paths = []
secret_key_patterns = []
config_key_patterns = []
literal_patterns = []
""",
            )

            report = check_config_contract.build_report(root)

        self.assertTrue(any("escapes repository root" in error for error in report.errors))

    def test_config_key_outside_registry_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "lib/providerConfig.ts", "export const key = 'DASHSCOPE_API_KEY';\n")
            write(root / "app/page.ts", "const key = 'DASHSCOPE_API_KEY';\n")
            write_config(
                root,
                """enabled = true
registry_paths = ["lib/providerConfig.ts"]
scan_roots = ["app", "lib"]
allowed_literal_paths = []
env_template_paths = []
local_env_paths = []
secret_key_patterns = []
config_key_patterns = ["DASHSCOPE_API_KEY"]
literal_patterns = []
""",
            )

            report = check_config_contract.build_report(root)

        self.assertEqual(len(report.errors), 1)
        self.assertIn("app/page.ts:1", report.errors[0])
        self.assertIn("config_key_patterns[1]", report.errors[0])

    def test_literal_outside_allowed_path_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "lib/providerConfig.ts", "export const model = 'qwen3.7-max';\n")
            write(root / "lib/service.ts", "const model = 'qwen3.7-max';\n")
            write_config(
                root,
                """enabled = true
registry_paths = ["lib/providerConfig.ts"]
scan_roots = ["lib"]
allowed_literal_paths = []
env_template_paths = []
local_env_paths = []
secret_key_patterns = []
config_key_patterns = []
literal_patterns = ["qwen[0-9A-Za-z_.-]+"]
""",
            )

            report = check_config_contract.build_report(root)

        self.assertEqual(len(report.errors), 1)
        self.assertIn("lib/service.ts:1", report.errors[0])
        self.assertIn("literal_patterns[1]", report.errors[0])

    def test_allowed_registry_can_contain_patterns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "lib/providerConfig.ts", "export const model = 'qwen3.7-max';\n")
            write_config(
                root,
                """enabled = true
registry_paths = ["lib/providerConfig.ts"]
scan_roots = ["lib"]
allowed_literal_paths = []
env_template_paths = []
local_env_paths = []
secret_key_patterns = []
config_key_patterns = []
literal_patterns = ["qwen[0-9A-Za-z_.-]+"]
""",
            )

            report = check_config_contract.build_report(root)

        self.assertEqual(report.errors, [])

    def test_sensitive_template_value_error_does_not_print_value(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / ".env.example", "API_SECRET=real-template-secret\n")
            write_config(
                root,
                """enabled = true
registry_paths = []
scan_roots = []
allowed_literal_paths = []
env_template_paths = [".env.example"]
local_env_paths = []
secret_key_patterns = ["SECRET"]
config_key_patterns = []
literal_patterns = []
""",
            )

            report = check_config_contract.build_report(root)
            rendered = check_config_contract.render_report(report)

        self.assertIn("API_SECRET", rendered)
        self.assertNotIn("real-template-secret", rendered)


if __name__ == "__main__":
    unittest.main()
