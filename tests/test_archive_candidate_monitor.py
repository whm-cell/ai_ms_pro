from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_archive_candidates  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
