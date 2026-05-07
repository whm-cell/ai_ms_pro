from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_context_budget  # noqa: E402


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class ContextBudgetAuditTest(unittest.TestCase):
    def test_report_warns_for_expensive_default_surface_and_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / ".codex/harness.toml",
                """[context_surface]
active_handoff_budget = 1
archive_candidate_min_score = 3
warn_at_budget = true

[context_budget]
default_surface_token_budget = 10
default_surface_warning_percent = 80
default_surface_high_warning_percent = 90
always_on_doc_line_budget = 2
stage_status_line_budget = 2
skill_description_word_budget = 3
skill_body_line_budget = 3
adr_count_budget = 1
mcp_server_budget = 1
""",
            )
            repeated = "- repeat this important instruction across files to find duplicated guidance\n"
            write(root / "AGENTS.md", repeated * 3)
            write(root / "docs/ai/index.md", repeated)
            write(
                root / "docs/ai/working-context.md",
                """# Working Context

- Active Status Source: docs/ai/status/stage-00.md
""",
            )
            write(root / "docs/ai/status/stage-00.md", "# Status\n\n" + ("x" * 200))
            write(root / "docs/ai/handoffs/active/current.md", "# Handoff\n")
            write(root / "docs/ai/adr/ADR-001.md", "# ADR 1\n")
            write(root / "docs/ai/adr/ADR-002.md", "# ADR 2\n")
            write(
                root / ".agents/skills/example/SKILL.md",
                """---
name: example
description: this description is intentionally too long
---

# Example

- body
- body
- body
- body
""",
            )

            report = check_context_budget.build_report(root=root)

        warning_text = "\n".join(report.warnings)
        self.assertIn("Default context surface exceeds budget", warning_text)
        self.assertIn("Always-on document AGENTS.md is long", warning_text)
        self.assertIn("Stage status docs/ai/status/stage-00.md reached compression", warning_text)
        self.assertIn("Active handoffs reached", warning_text)
        self.assertIn("ADR count reached budget", warning_text)
        self.assertIn("Skill description is long", warning_text)
        self.assertIn("Skill body is long", warning_text)
        self.assertTrue(report.duplicate_instructions)

    def test_default_surface_warns_at_percentage_thresholds_before_hard_budget(self) -> None:
        config = check_context_budget.ContextBudgetConfig(
            default_surface_token_budget=100,
            default_surface_warning_percent=80,
            default_surface_high_warning_percent=90,
            always_on_doc_line_budget=300,
            stage_status_line_budget=120,
            skill_description_word_budget=30,
            skill_body_line_budget=400,
            adr_count_budget=15,
            mcp_server_budget=10,
        )

        low_warnings = check_context_budget.build_warnings(
            report_items=[
                check_context_budget.SurfaceItem(
                    path="AGENTS.md",
                    lines=1,
                    estimated_tokens=85,
                )
            ],
            skills=[],
            duplicates=[],
            config=config,
            active_handoff_count=0,
            active_handoff_budget=5,
            adr_count=0,
            mcp_count=0,
        )
        high_warnings = check_context_budget.build_warnings(
            report_items=[
                check_context_budget.SurfaceItem(
                    path="AGENTS.md",
                    lines=1,
                    estimated_tokens=91,
                )
            ],
            skills=[],
            duplicates=[],
            config=config,
            active_handoff_count=0,
            active_handoff_budget=5,
            adr_count=0,
            mcp_count=0,
        )

        self.assertIn("Default context surface reached warning threshold", "\n".join(low_warnings))
        self.assertIn(
            "Default context surface reached high warning threshold",
            "\n".join(high_warnings),
        )


if __name__ == "__main__":
    unittest.main()
