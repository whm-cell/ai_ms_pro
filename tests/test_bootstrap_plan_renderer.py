import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import bootstrap_harness  # noqa: E402
import bootstrap_plan_renderer  # noqa: E402


class BootstrapPlanRendererTests(unittest.TestCase):
    def test_bootstrap_harness_keeps_render_plan_entrypoint(self) -> None:
        rendered = bootstrap_harness.render_plan("Demo Project", "STAGE-99")

        self.assertEqual(
            rendered,
            bootstrap_plan_renderer.render_plan("Demo Project", "STAGE-99"),
        )
        self.assertIn(
            "- 为 `Demo Project` 建立最小可用的 Codex-first harness 控制面",
            rendered,
        )
        self.assertIn(
            "- 阶段文档更新后检查 [AI 文档入口索引](./index.md)",
            rendered,
        )
        self.assertTrue(rendered.endswith("\n"))


if __name__ == "__main__":
    unittest.main()
