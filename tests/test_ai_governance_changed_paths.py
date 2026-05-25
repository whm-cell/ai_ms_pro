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

        self.assertTrue(changed_paths.is_runtime_state_file(raw_log))
        self.assertFalse(changed_paths.is_runtime_state_file(readme))


if __name__ == "__main__":
    unittest.main()
