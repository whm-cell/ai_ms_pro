from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_env_template_sync  # noqa: E402


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class EnvTemplateSyncTest(unittest.TestCase):
    def test_missing_template_key_fails_unless_warning_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / ".env.example", "API_KEY=\nMODEL_NAME=demo\n")
            write(root / ".env", "API_KEY=local-secret-value\n")

            report = check_env_template_sync.build_report(
                root=root,
                template=".env.example",
                env=".env",
            )

        self.assertEqual(report.missing_keys, ["MODEL_NAME"])
        self.assertEqual(check_env_template_sync.exit_code(report, warning_only=False), 1)
        self.assertEqual(check_env_template_sync.exit_code(report, warning_only=True), 0)

    def test_render_report_does_not_print_env_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / ".env.example", "API_KEY=\n")
            write(root / ".env", "API_KEY=local-secret-value\nEXTRA_TOKEN=extra-secret\n")

            report = check_env_template_sync.build_report(
                root=root,
                template=".env.example",
                env=".env",
            )
            rendered = check_env_template_sync.render_report(report)

        self.assertIn("EXTRA_TOKEN", rendered)
        self.assertNotIn("local-secret-value", rendered)
        self.assertNotIn("extra-secret", rendered)

    def test_config_disabled_is_noop(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = check_env_template_sync.build_report(root=Path(tmp))

        self.assertFalse(report.enabled)
        self.assertEqual(report.errors, [])


if __name__ == "__main__":
    unittest.main()
