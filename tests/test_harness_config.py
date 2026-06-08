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
        self.assertEqual(config.context_budget.default_surface_warning_percent, 80)
        self.assertEqual(config.context_budget.default_surface_high_warning_percent, 90)
        self.assertEqual(config.context_budget.stage_status_line_budget, 120)
        self.assertEqual(config.context_budget.skill_description_word_budget, 30)
        self.assertFalse(config.prototype_design_brief.enabled)
        self.assertFalse(config.prototype_design_brief.artifact_review_enabled)
        self.assertEqual(
            config.prototype_design_brief.brief_path,
            "docs/ai/prototypes/prototype-design-brief.md",
        )

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
default_surface_warning_percent = 70
default_surface_high_warning_percent = 85
always_on_doc_line_budget = 120
stage_status_line_budget = 80
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
        self.assertEqual(config.context_budget.default_surface_warning_percent, 70)
        self.assertEqual(config.context_budget.default_surface_high_warning_percent, 85)
        self.assertEqual(config.context_budget.always_on_doc_line_budget, 120)
        self.assertEqual(config.context_budget.stage_status_line_budget, 80)
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

    def test_loads_prototype_design_brief_feature_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / ".codex/harness.toml",
                """[prototype_design_brief]
enabled = true
artifact_review_enabled = true
brief_path = "docs/ai/prototypes/prototype-design-brief.md"
artifact_dir = "docs/ai/prototypes/custom"
prototype_page_path = "app/prototype/custom/page.tsx"
prototype_route = "/prototype/custom"
fixture_paths = ["lib/prototype/customFixture.ts"]
required_states = ["empty", "permission_denied"]
""",
            )

            config = harness_config.load_harness_config(root).prototype_design_brief

        self.assertTrue(config.enabled)
        self.assertTrue(config.artifact_review_enabled)
        self.assertEqual(config.artifact_dir, "docs/ai/prototypes/custom")
        self.assertEqual(config.fixture_paths, ("lib/prototype/customFixture.ts",))
        self.assertEqual(config.required_states, ("empty", "permission_denied"))

    def test_artifact_review_requires_base_feature_enabled(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / ".codex/harness.toml",
                """[prototype_design_brief]
enabled = false
artifact_review_enabled = true
artifact_dir = "docs/ai/prototypes/custom"
prototype_page_path = "app/prototype/custom/page.tsx"
prototype_route = "/prototype/custom"
required_states = ["empty"]
""",
            )

            with self.assertRaisesRegex(
                harness_config.HarnessConfigError,
                "artifact_review_enabled requires",
            ):
                harness_config.load_harness_config(root)

    def test_governance_checks_follow_prototype_feature_flags(self) -> None:
        disabled = harness_config.PrototypeDesignBriefConfig(
            enabled=False,
            artifact_review_enabled=False,
            brief_path="docs/ai/prototypes/prototype-design-brief.md",
            artifact_dir="",
            prototype_page_path="",
            prototype_route="",
            fixture_paths=(),
            required_states=(),
        )
        brief_only = harness_config.PrototypeDesignBriefConfig(
            enabled=True,
            artifact_review_enabled=False,
            brief_path="docs/ai/prototypes/prototype-design-brief.md",
            artifact_dir="",
            prototype_page_path="",
            prototype_route="",
            fixture_paths=(),
            required_states=(),
        )
        artifact_enabled = harness_config.PrototypeDesignBriefConfig(
            enabled=True,
            artifact_review_enabled=True,
            brief_path="docs/ai/prototypes/prototype-design-brief.md",
            artifact_dir="docs/ai/prototypes/custom",
            prototype_page_path="app/prototype/custom/page.tsx",
            prototype_route="/prototype/custom",
            fixture_paths=("lib/prototype/customFixture.ts",),
            required_states=("empty",),
        )

        disabled_labels = [label for label, _path in check_ai_governance.governance_check_specs(disabled)]
        brief_labels = [label for label, _path in check_ai_governance.governance_check_specs(brief_only)]
        artifact_labels = [label for label, _path in check_ai_governance.governance_check_specs(artifact_enabled)]

        self.assertNotIn("prototype-brief", disabled_labels)
        self.assertIn("prototype-brief", brief_labels)
        self.assertIn("prototype-artifact", artifact_labels)

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
default_surface_warning_percent = 75
default_surface_high_warning_percent = 88
always_on_doc_line_budget = 100
stage_status_line_budget = 70
skill_description_word_budget = 25
skill_body_line_budget = 240
adr_count_budget = 8
mcp_server_budget = 3

[prototype_design_brief]
enabled = true
artifact_review_enabled = false
brief_path = "docs/ai/prototypes/custom.md"
"""
        with mock.patch.object(harness_config, "tomllib", None):
            parsed = harness_config.load_toml_config(raw_text)

        self.assertEqual(parsed["checks"]["required_ai_docs"], ["AGENTS.md"])
        self.assertEqual(parsed["context_surface"]["active_handoff_budget"], 7)
        self.assertEqual(parsed["context_surface"]["archive_candidate_min_score"], 8)
        self.assertFalse(parsed["context_surface"]["warn_at_budget"])
        self.assertEqual(parsed["context_budget"]["default_surface_token_budget"], 900)
        self.assertEqual(parsed["context_budget"]["default_surface_warning_percent"], 75)
        self.assertEqual(parsed["context_budget"]["default_surface_high_warning_percent"], 88)
        self.assertEqual(parsed["context_budget"]["stage_status_line_budget"], 70)
        self.assertEqual(parsed["context_budget"]["mcp_server_budget"], 3)
        self.assertTrue(parsed["prototype_design_brief"]["enabled"])
        self.assertEqual(
            parsed["prototype_design_brief"]["brief_path"],
            "docs/ai/prototypes/custom.md",
        )

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
