from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_prototype_design_brief  # noqa: E402


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def valid_brief() -> str:
    return """# Prototype Design Brief

## Project Metadata

This design projection does not replace canonical requirements.
Prototype handoff is tool agnostic.

## Source Truth

- Requirement IDs: REQ-006
- Workstream IDs: WS-02
- ADR IDs: ADR-017
- Traceability source: [Traceability](../../requirements/traceability-matrix.md)
- Requirement docs: [REQ-006](../../requirements/normalized/REQ-006-demo.md)
- Workstream docs: [WS-02](../../requirements/workstreams/WS-02-demo.md)
- Decision docs: [ADR-017](../adr/ADR-017-demo.md)

## Product Scope

Product scope.

## Target Surfaces

Surface identity for app and admin surface.

## Page Map

Page map.

## Critical States

Critical state matrix includes blocked and error states.

## Boundary Rules

Scope and permission boundaries. Fail-closed when selected dependencies fail.

## Non-Goals

Non-goals.

## Prototype Handoff

Prototype artifact review will verify handoff output.

## Review And Sync Rules

Run checker after artifact review.
"""


class PrototypeDesignBriefTest(unittest.TestCase):
    def workspace(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        write(
            root / "docs/requirements/traceability-matrix.md",
            "| 原始文档 | 标准化需求 | 工作流 | 开发阶段 | 当前状态 | 验收/测试 |\n"
            "| --- | --- | --- | --- | --- | --- |\n"
            "| REQDOC-001 | REQ-006 Demo | WS-02 | STAGE-00 | planned | pending |\n",
        )
        write(root / "docs/requirements/normalized/REQ-006-demo.md", "# REQ-006 Demo\n")
        write(root / "docs/requirements/workstreams/WS-02-demo.md", "# WS-02 Demo\n")
        write(root / "docs/ai/adr/ADR-017-demo.md", "# ADR-017 Demo\n")
        return temp_dir, root

    def test_complete_brief_has_zero_drift(self) -> None:
        temp_dir, root = self.workspace()
        self.addCleanup(temp_dir.cleanup)
        brief_path = root / "docs/ai/prototypes/prototype-design-brief.md"
        write(brief_path, valid_brief())

        report = check_prototype_design_brief.build_report(root=root, brief_path=brief_path)

        self.assertEqual(report.errors, [])
        self.assertEqual(report.completeness_rate, 1.0)
        self.assertEqual(report.drift_rate, 0.0)

    def test_unknown_traceability_id_and_missing_link_count_as_drift(self) -> None:
        temp_dir, root = self.workspace()
        self.addCleanup(temp_dir.cleanup)
        brief_path = root / "docs/ai/prototypes/prototype-design-brief.md"
        write(
            brief_path,
            valid_brief().replace("REQ-006", "REQ-999", 1)
            + "\n[Missing](../../requirements/normalized/REQ-999-missing.md)\n",
        )

        report = check_prototype_design_brief.build_report(root=root, brief_path=brief_path)

        self.assertGreater(report.drift_rate, 0)
        self.assertTrue(any("REQ-999" in error for error in report.errors))
        self.assertTrue(any("link target missing" in error for error in report.errors))

    def test_source_truth_unbound_is_error(self) -> None:
        temp_dir, root = self.workspace()
        self.addCleanup(temp_dir.cleanup)
        brief_path = root / "docs/ai/prototypes/prototype-design-brief.md"
        write(brief_path, valid_brief().replace("- Requirement IDs: REQ-006", "- Requirement IDs: 未绑定", 1))

        report = check_prototype_design_brief.build_report(root=root, brief_path=brief_path)

        self.assertTrue(any("Source Truth" in error for error in report.errors))


if __name__ == "__main__":
    unittest.main()
