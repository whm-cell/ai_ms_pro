from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_quality_supervisor_protocol  # noqa: E402


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class QualitySupervisorProtocolTest(unittest.TestCase):
    def test_disabled_config_reports_skipped_without_doc_requirements(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            harness_config = root / ".codex" / "harness.toml"
            write(
                harness_config,
                """[quality_supervisor]
enabled = false
default_scope = "material-task"
supervisor_role = "quality-supervisor"
task_profiles = ["medium"]
skip_allowed_for = ["direct-answer"]
""",
            )

            with mock.patch.object(check_quality_supervisor_protocol, "HARNESS_CONFIG", harness_config):
                report = check_quality_supervisor_protocol.build_report()

        self.assertEqual(report.status, "disabled")
        self.assertFalse(report.errors)
        self.assertIn("disabled", report.warnings[0])

    def test_enabled_config_requires_documented_protocol_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            harness_config = root / ".codex" / "harness.toml"
            agents = root / "AGENTS.md"
            standard = root / "docs" / "ai" / "standards" / "quality-supervisor-protocol.md"
            registry = root / "docs" / "ai" / "check-registry.md"
            index = root / "docs" / "ai" / "index.md"
            write(
                harness_config,
                """[quality_supervisor]
enabled = true
default_scope = "material-task"
supervisor_role = "quality-supervisor"
task_profiles = ["medium", "complex"]
skip_allowed_for = ["direct-answer", "tool-unavailable"]
""",
            )
            write(agents, "quality supervisor subagent main agent canonical")
            write(
                standard,
                "quality-supervisor-protocol/v1 hooks cannot spawn subagents "
                "main agent owns canonical writes does not prove",
            )
            write(registry, "check_quality_supervisor_protocol.py review-required")
            write(index, "quality supervisor")

            patches = (
                mock.patch.object(check_quality_supervisor_protocol, "HARNESS_CONFIG", harness_config),
                mock.patch.object(check_quality_supervisor_protocol, "AGENTS_PATH", agents),
                mock.patch.object(check_quality_supervisor_protocol, "STANDARD_PATH", standard),
                mock.patch.object(check_quality_supervisor_protocol, "CHECK_REGISTRY_PATH", registry),
                mock.patch.object(check_quality_supervisor_protocol, "INDEX_PATH", index),
            )
            with patches[0], patches[1], patches[2], patches[3], patches[4]:
                report = check_quality_supervisor_protocol.build_report()

        self.assertEqual(report.status, "enabled")
        self.assertFalse(report.errors)

    def test_invalid_scope_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            harness_config = Path(tmp) / ".codex" / "harness.toml"
            write(
                harness_config,
                """[quality_supervisor]
enabled = false
default_scope = "always"
""",
            )

            with mock.patch.object(check_quality_supervisor_protocol, "HARNESS_CONFIG", harness_config):
                report = check_quality_supervisor_protocol.build_report()

        self.assertIn("default_scope", "\n".join(report.errors))


if __name__ == "__main__":
    unittest.main()
