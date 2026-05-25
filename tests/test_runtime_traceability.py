from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex" / "hooks"))

import runtime_traceability  # noqa: E402


class RuntimeTraceabilityTest(unittest.TestCase):
    def setUp(self) -> None:
        runtime_traceability.load_traceability_catalog.cache_clear()

    def test_auto_discovers_threejs_workstream_from_module_path(self) -> None:
        requirement_ids, workstream_ids, source = runtime_traceability.resolve_runtime_traceability(
            [],
            [],
            [],
            [],
            ["apps/threejs-snake/main.js"],
        )

        self.assertEqual(requirement_ids, ["REQ-001", "REQ-002", "REQ-003"])
        self.assertEqual(workstream_ids, ["WS-01"])
        self.assertEqual(source, "module-path")

    def test_auto_discovers_trace_console_workstream_from_module_path(self) -> None:
        requirement_ids, workstream_ids, source = runtime_traceability.resolve_runtime_traceability(
            [],
            [],
            [],
            [],
            ["apps/harness-trace-console/main.js"],
        )

        self.assertEqual(requirement_ids, ["REQ-004", "REQ-005", "REQ-006"])
        self.assertEqual(workstream_ids, ["WS-02"])
        self.assertEqual(source, "module-path")

    def test_expands_explicit_requirement_to_workstream(self) -> None:
        requirement_ids, workstream_ids, source = runtime_traceability.resolve_runtime_traceability(
            ["REQ-006"],
            [],
            [],
            [],
            ["docs/ai/working-context.md"],
        )

        self.assertEqual(requirement_ids, ["REQ-006"])
        self.assertEqual(workstream_ids, ["WS-02"])
        self.assertEqual(source, "payload,matrix-expansion")

    def test_normalized_requirement_path_maps_back_to_workstream(self) -> None:
        requirement_ids, workstream_ids, source = runtime_traceability.resolve_runtime_traceability(
            [],
            [],
            [],
            [],
            ["docs/requirements/normalized/REQ-001-threejs-snake-core-gameplay.md"],
        )

        self.assertEqual(requirement_ids, ["REQ-001"])
        self.assertEqual(workstream_ids, ["WS-01"])
        self.assertEqual(source, "changed-path:req,module-path")

    def test_ambiguous_working_context_path_stays_unbound(self) -> None:
        requirement_ids, workstream_ids, source = runtime_traceability.resolve_runtime_traceability(
            [],
            [],
            [],
            [],
            ["docs/ai/working-context.md"],
        )

        self.assertEqual(requirement_ids, [])
        self.assertEqual(workstream_ids, [])
        self.assertEqual(source, "unbound")

    def test_unknown_changed_path_stays_unbound(self) -> None:
        requirement_ids, workstream_ids, source = runtime_traceability.resolve_runtime_traceability(
            [],
            [],
            [],
            [],
            ["--使用细节/新项目初始化约束提示词.md"],
        )

        self.assertEqual(requirement_ids, [])
        self.assertEqual(workstream_ids, [])
        self.assertEqual(source, "unbound")


if __name__ == "__main__":
    unittest.main()
