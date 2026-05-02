from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_ai_governance  # noqa: E402
import harness_config  # noqa: E402


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class HarnessConfigTest(unittest.TestCase):
    def test_defaults_when_config_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = harness_config.load_harness_config(Path(tmp))

        self.assertEqual(config.checks.required_ai_docs[0], "AGENTS.md")
        self.assertEqual(config.context_surface.active_handoff_budget, 5)
        self.assertEqual(config.context_surface.archive_candidate_min_score, 3)
        self.assertTrue(config.context_surface.warn_at_budget)
        self.assertEqual(config.context_budget.default_surface_token_budget, 6500)
        self.assertEqual(config.context_budget.skill_description_word_budget, 30)

    def test_context_surface_overrides_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / ".codex/harness.toml",
                """[checks]
required_ai_docs = ["AGENTS.md"]
required_requirements_docs = ["docs/requirements/traceability-matrix.md"]

[context_surface]
active_handoff_budget = 4
archive_candidate_min_score = 6
warn_at_budget = false

[context_budget]
default_surface_token_budget = 1000
always_on_doc_line_budget = 120
skill_description_word_budget = 20
skill_body_line_budget = 250
adr_count_budget = 9
mcp_server_budget = 4
""",
            )

            config = harness_config.load_harness_config(root)

        self.assertEqual(config.checks.required_ai_docs, ("AGENTS.md",))
        self.assertEqual(config.context_surface.active_handoff_budget, 4)
        self.assertEqual(config.context_surface.archive_candidate_min_score, 6)
        self.assertFalse(config.context_surface.warn_at_budget)
        self.assertEqual(config.context_budget.default_surface_token_budget, 1000)
        self.assertEqual(config.context_budget.always_on_doc_line_budget, 120)
        self.assertEqual(config.context_budget.skill_description_word_budget, 20)
        self.assertEqual(config.context_budget.skill_body_line_budget, 250)
        self.assertEqual(config.context_budget.adr_count_budget, 9)
        self.assertEqual(config.context_budget.mcp_server_budget, 4)

    def test_rejects_repo_escaping_required_doc_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            with self.assertRaises(harness_config.HarnessConfigError):
                harness_config.resolve_repo_paths(
                    root,
                    ("../outside.md",),
                    config_label="checks.required_ai_docs",
                )

    def test_minimal_parser_handles_checks_and_context_surface(self) -> None:
        raw_text = """[checks]
required_ai_docs = [
  "AGENTS.md",
]
required_requirements_docs = ["docs/requirements/traceability-matrix.md"]

[context_surface]
active_handoff_budget = 7
archive_candidate_min_score = 8
warn_at_budget = false

[context_budget]
default_surface_token_budget = 900
always_on_doc_line_budget = 100
skill_description_word_budget = 25
skill_body_line_budget = 240
adr_count_budget = 8
mcp_server_budget = 3
"""
        with mock.patch.object(harness_config, "tomllib", None):
            parsed = harness_config.load_toml_config(raw_text)

        self.assertEqual(parsed["checks"]["required_ai_docs"], ["AGENTS.md"])
        self.assertEqual(parsed["context_surface"]["active_handoff_budget"], 7)
        self.assertEqual(parsed["context_surface"]["archive_candidate_min_score"], 8)
        self.assertFalse(parsed["context_surface"]["warn_at_budget"])
        self.assertEqual(parsed["context_budget"]["default_surface_token_budget"], 900)
        self.assertEqual(parsed["context_budget"]["mcp_server_budget"], 3)

    def test_budget_warning_can_fire_at_or_over_budget(self) -> None:
        config = harness_config.ContextSurfaceConfig(
            active_handoff_budget=5,
            archive_candidate_min_score=3,
            warn_at_budget=True,
        )

        warnings = check_ai_governance.context_surface_budget_warnings(
            count=5,
            label="Active handoff count",
            config=config,
        )

        self.assertEqual(len(warnings), 1)
        self.assertIn("5 >= 5", warnings[0])

    def test_budget_warning_can_wait_until_over_budget(self) -> None:
        config = harness_config.ContextSurfaceConfig(
            active_handoff_budget=5,
            archive_candidate_min_score=3,
            warn_at_budget=False,
        )

        self.assertEqual(
            check_ai_governance.context_surface_budget_warnings(
                count=5,
                label="Active handoff count",
                config=config,
            ),
            [],
        )
        self.assertTrue(
            check_ai_governance.context_surface_budget_warnings(
                count=6,
                label="Active handoff count",
                config=config,
            )
        )


if __name__ == "__main__":
    unittest.main()
