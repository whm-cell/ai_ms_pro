from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import ai_governance_changed_paths as changed_paths  # noqa: E402


class AiGovernanceChangedPathsTest(unittest.TestCase):
    def test_runtime_tool_outputs_are_runtime_state_files(self) -> None:
        raw_log = ROOT / ".codex/runtime/tool-outputs/build.log"
        readme = ROOT / ".codex/runtime/tool-outputs/README.md"
        template = ROOT / ".codex/runtime/sessions/_template.md"
        keep = ROOT / ".codex/runtime/new-area/.gitkeep"
        future_runtime_file = ROOT / ".codex/runtime/async-verification/status.json"

        self.assertTrue(changed_paths.is_runtime_state_file(raw_log))
        self.assertFalse(changed_paths.is_runtime_state_file(readme))
        self.assertFalse(changed_paths.is_runtime_state_file(template))
        self.assertFalse(changed_paths.is_runtime_state_file(keep))
        self.assertTrue(changed_paths.is_runtime_state_file(future_runtime_file))

    def test_runtime_index_cleanup_deletions_are_allowed(self) -> None:
        runtime_file = ROOT / ".codex/runtime/tool-outputs/build.log"

        self.assertFalse(changed_paths.is_blocking_staged_runtime_change("D", runtime_file))
        self.assertTrue(changed_paths.is_blocking_staged_runtime_change("A", runtime_file))


if __name__ == "__main__":
    unittest.main()
