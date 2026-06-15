from __future__ import annotations

import tempfile
import unittest
import importlib.util
from pathlib import Path

import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_archive_candidates  # noqa: E402


def load_starter_archive_module():
    module_path = ROOT / "scripts" / "check_archive_candidates.py"
    spec = importlib.util.spec_from_file_location("starter_check_archive_candidates", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    old_harness_config = sys.modules.get("harness_config")
    old_sys_path = list(sys.path)
    try:
        sys.modules.pop("harness_config", None)
        sys.path.insert(0, str(module_path.parent))
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    finally:
        sys.path[:] = old_sys_path
        if old_harness_config is not None:
            sys.modules["harness_config"] = old_harness_config
        else:
            sys.modules.pop("harness_config", None)
    return module


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class ArchiveCandidateMonitorTest(unittest.TestCase):
    def test_completed_handoff_with_status_coverage_is_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "docs/ai/handoffs/active/stage-00-done.md",
                """# Done Handoff

更新时间：2026-04-01
阶段：stage-00
任务：done-task
状态：已完成

## 当前未完成项

- 无
""",
            )
            write(
                root / "docs/ai/handoffs/active/stage-00-active.md",
                """# Active Handoff

更新时间：2026-04-01
阶段：stage-00
任务：active-task
状态：进行中
""",
            )
            write(
                root / "docs/ai/status/stage-00.md",
                """# Stage Status

更新时间：2026-04-30

done-task has been compressed into this stage status.
""",
            )
            write(
                root / "docs/ai/working-context.md",
                """# Working Context

## 同步元数据

- Active Handoff Sources:
  - docs/ai/handoffs/active/stage-00-done.md
  - docs/ai/handoffs/active/stage-00-active.md
""",
            )

            report = check_archive_candidates.build_report(root=root, budget=5)

        self.assertEqual(report.active_handoff_count, 2)
        self.assertEqual([candidate.path for candidate in report.candidates], ["docs/ai/handoffs/active/stage-00-done.md"])

    def test_unbound_handoff_is_candidate_even_without_status_mention(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "docs/ai/handoffs/active/stage-00-old.md",
                """# Old Handoff

更新时间：2026-04-01
阶段：stage-00
任务：old-task
状态：已完成
""",
            )
            write(
                root / "docs/ai/status/stage-00.md",
                "# Stage Status\n\n更新时间：2026-04-30\n",
            )
            write(
                root / "docs/ai/working-context.md",
                """# Working Context

## 同步元数据

- Active Handoff Sources:
  - docs/ai/handoffs/active/another.md
""",
            )

            report = check_archive_candidates.build_report(root=root, budget=5)

        self.assertEqual(len(report.candidates), 1)
        self.assertIn("working-context 未把它列为默认接力入口", report.candidates[0].reasons)

    def test_context_surface_config_controls_budget_and_min_score(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / ".codex/harness.toml",
                """[context_surface]
active_handoff_budget = 2
archive_candidate_min_score = 6
warn_at_budget = true
""",
            )
            write(
                root / "docs/ai/handoffs/active/stage-00-done.md",
                """# Done Handoff

更新时间：2026-04-01
阶段：stage-00
任务：done-task
状态：已完成
""",
            )
            write(
                root / "docs/ai/handoffs/active/stage-00-active.md",
                """# Active Handoff

更新时间：2026-04-01
阶段：stage-00
任务：active-task
状态：进行中
""",
            )
            write(
                root / "docs/ai/status/stage-00.md",
                """# Stage Status

更新时间：2026-04-30

done-task has been compressed into this stage status.
""",
            )
            write(
                root / "docs/ai/working-context.md",
                """# Working Context

## 同步元数据

- Active Handoff Sources:
  - docs/ai/handoffs/active/stage-00-done.md
  - docs/ai/handoffs/active/stage-00-active.md
""",
            )

            report = check_archive_candidates.build_report(root=root)

        self.assertTrue(report.at_or_over_budget)
        self.assertEqual(report.budget, 2)
        self.assertEqual(report.min_score, 6)
        self.assertEqual([candidate.path for candidate in report.candidates], ["docs/ai/handoffs/active/stage-00-done.md"])

    def test_explicit_budget_and_min_score_override_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / ".codex/harness.toml",
                """[context_surface]
active_handoff_budget = 10
archive_candidate_min_score = 10
warn_at_budget = true
""",
            )
            write(
                root / "docs/ai/handoffs/active/stage-00-done.md",
                """# Done Handoff

更新时间：2026-04-01
阶段：stage-00
任务：done-task
状态：已完成
""",
            )
            write(
                root / "docs/ai/status/stage-00.md",
                """# Stage Status

更新时间：2026-04-30

done-task has been compressed into this stage status.
""",
            )
            write(
                root / "docs/ai/working-context.md",
                """# Working Context

## 同步元数据

- Active Handoff Sources:
  - docs/ai/handoffs/active/stage-00-done.md
""",
            )

            report = check_archive_candidates.build_report(root=root, budget=1, min_score=6)

        self.assertEqual(report.budget, 1)
        self.assertEqual(report.min_score, 6)
        self.assertEqual(len(report.candidates), 1)

    def test_starter_archive_monitor_matches_root_behavior(self) -> None:
        starter_module = load_starter_archive_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "docs/ai/handoffs/active/stage-00-old.md",
                """# Old Handoff

更新时间：2026-04-01
阶段：stage-00
任务：old-task
状态：已完成
""",
            )
            write(root / "docs/ai/status/stage-00.md", "# Stage Status\n")
            write(
                root / "docs/ai/working-context.md",
                """# Working Context

## 同步元数据

- Active Handoff Sources:
  - docs/ai/handoffs/active/another.md
""",
            )

            root_report = check_archive_candidates.build_report(root=root)
            starter_report = starter_module.build_report(root=root)

        self.assertEqual(
            [candidate.path for candidate in root_report.candidates],
            [candidate.path for candidate in starter_report.candidates],
        )
        self.assertEqual(root_report.budget, starter_report.budget)
        self.assertEqual(root_report.min_score, starter_report.min_score)


if __name__ == "__main__":
    unittest.main()
