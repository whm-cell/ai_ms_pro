from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex" / "hooks"))

import runtime_traceability  # noqa: E402
import runtime_traceability_catalog  # noqa: E402


class RuntimeTraceabilityTest(unittest.TestCase):
    def setUp(self) -> None:
        self.original_catalog_root = runtime_traceability_catalog.ROOT
        self.original_runtime_root = runtime_traceability.ROOT
        self.original_matrix_path = runtime_traceability_catalog.TRACEABILITY_MATRIX_PATH
        self.original_workstream_dir = runtime_traceability_catalog.WORKSTREAM_DIR
        runtime_traceability.load_traceability_catalog.cache_clear()

    def tearDown(self) -> None:
        runtime_traceability_catalog.ROOT = self.original_catalog_root
        runtime_traceability.ROOT = self.original_runtime_root
        runtime_traceability_catalog.TRACEABILITY_MATRIX_PATH = self.original_matrix_path
        runtime_traceability_catalog.WORKSTREAM_DIR = self.original_workstream_dir
        runtime_traceability.load_traceability_catalog.cache_clear()

    def configure_temp_catalog(self, root: Path) -> None:
        matrix = root / "docs" / "requirements" / "traceability-matrix.md"
        workstream_dir = root / "docs" / "requirements" / "workstreams"
        workstream_doc = workstream_dir / "WS-01-demo.md"
        (root / "apps" / "demo").mkdir(parents=True, exist_ok=True)
        matrix.parent.mkdir(parents=True, exist_ok=True)
        workstream_dir.mkdir(parents=True, exist_ok=True)
        matrix.write_text(
            "\n".join(
                [
                    "# 需求追踪矩阵",
                    "",
                    "## 矩阵",
                    "",
                    "| 原始文档 | 标准化需求 | 工作流 | 开发阶段 | 当前状态 | 验收/测试 |",
                    "| --- | --- | --- | --- | --- | --- |",
                    "| REQDOC-01 | REQ-001 | WS-01 | STAGE-00 | 待开始 | smoke |",
                ]
            ),
            encoding="utf-8",
        )
        workstream_doc.write_text(
            "\n".join(
                [
                    "# Demo Workstream",
                    "",
                    "工作流编号：WS-01",
                    "",
                    "## 主要模块",
                    "",
                    "- `apps/demo`",
                ]
            ),
            encoding="utf-8",
        )
        runtime_traceability_catalog.ROOT = root
        runtime_traceability.ROOT = root
        runtime_traceability_catalog.TRACEABILITY_MATRIX_PATH = matrix
        runtime_traceability_catalog.WORKSTREAM_DIR = workstream_dir
        runtime_traceability.load_traceability_catalog.cache_clear()

    def test_infers_workstream_from_portable_module_mapping(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            self.configure_temp_catalog(Path(tempdir))

            requirement_ids, workstream_ids, source = runtime_traceability.resolve_runtime_traceability(
                [],
                [],
                [],
                [],
                ["apps/demo/main.py"],
            )

        self.assertEqual(requirement_ids, ["REQ-001"])
        self.assertEqual(workstream_ids, ["WS-01"])
        self.assertEqual(source, "module-path")

    def test_expands_explicit_requirement_to_workstream(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            self.configure_temp_catalog(Path(tempdir))

            requirement_ids, workstream_ids, source = runtime_traceability.resolve_runtime_traceability(
                ["REQ-001"],
                [],
                [],
                [],
                ["docs/ai/working-context.md"],
            )

        self.assertEqual(requirement_ids, ["REQ-001"])
        self.assertEqual(workstream_ids, ["WS-01"])
        self.assertEqual(source, "payload,matrix-expansion")

    def test_unknown_changed_path_stays_unbound(self) -> None:
        requirement_ids, workstream_ids, source = runtime_traceability.resolve_runtime_traceability(
            [],
            [],
            [],
            [],
            ["apps/not-yet-mapped/main.py"],
        )

        self.assertEqual(requirement_ids, [])
        self.assertEqual(workstream_ids, [])
        self.assertEqual(source, "unbound")


if __name__ == "__main__":
    unittest.main()
