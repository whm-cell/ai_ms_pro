from __future__ import annotations

import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_change_triggered_followups  # noqa: E402


class ChangeTriggeredFollowupsTest(unittest.TestCase):
    def followup_names(self, *files: str) -> set[str]:
        followups = check_change_triggered_followups.build_followups(tuple(files))
        return {item.name for item in followups}

    def markdown_for(self, *files: str) -> str:
        followups = check_change_triggered_followups.build_followups(tuple(files))
        output = io.StringIO()
        with redirect_stdout(output):
            check_change_triggered_followups.emit_markdown(tuple(files), followups)
        return output.getvalue()

    def test_agents_change_triggers_governance_and_budget(self) -> None:
        names = self.followup_names("AGENTS.md")

        self.assertIn("governance-surface", names)
        self.assertIn("default-context-budget", names)

    def test_github_change_triggers_guardrails(self) -> None:
        names = self.followup_names(".github/workflows/governance-and-smoke.yml")

        self.assertEqual(names, {"github-guardrails"})

    def test_requirements_change_triggers_traceability(self) -> None:
        names = self.followup_names("docs/requirements/source/REQDOC-001.md")

        self.assertIn("governance-surface", names)
        self.assertIn("requirements-traceability", names)

    def test_skill_change_triggers_discoverability_and_budget(self) -> None:
        names = self.followup_names(".agents/skills/harness-maintenance/SKILL.md")

        self.assertIn("default-context-budget", names)
        self.assertIn("repo-local-skills", names)

    def test_harness_python_triggers_code_shape(self) -> None:
        names = self.followup_names("scripts/check_github_guardrails.py")

        self.assertIn("github-guardrails", names)
        self.assertIn("harness-code-shape", names)

    def test_starter_change_triggers_starter_sync(self) -> None:
        names = self.followup_names("new_pro_standard/AGENTS.md")

        self.assertIn("starter-sync", names)

    def test_normalize_preserves_dot_directories(self) -> None:
        self.assertEqual(
            check_change_triggered_followups.normalize(".github/workflows/main.yml"),
            ".github/workflows/main.yml",
        )
        self.assertEqual(
            check_change_triggered_followups.normalize("./.agents/skills/demo/SKILL.md"),
            ".agents/skills/demo/SKILL.md",
        )

    def test_parse_status_line_preserves_first_path_character(self) -> None:
        self.assertEqual(
            check_change_triggered_followups.parse_status_line(" M AGENTS.md"),
            "AGENTS.md",
        )
        self.assertEqual(
            check_change_triggered_followups.parse_status_line("?? .github/pull_request_template.md"),
            ".github/pull_request_template.md",
        )

    def test_markdown_summary_lists_followups(self) -> None:
        output = self.markdown_for(".github/workflows/governance-and-smoke.yml")

        self.assertIn("### Change-triggered follow-up suggestions", output)
        self.assertIn("| Follow-up | Reason | Matched files | Commands | References |", output)
        self.assertIn("`github-guardrails`", output)
        self.assertIn("scripts/check_github_guardrails.py", output)
        self.assertIn("Advisory only", output)

    def test_markdown_summary_handles_no_followups(self) -> None:
        output = self.markdown_for("README.md")

        self.assertIn("- Changed files: 1", output)
        self.assertIn("No specialized follow-up checks suggested.", output)
        self.assertIn("Advisory only", output)


if __name__ == "__main__":
    unittest.main()
