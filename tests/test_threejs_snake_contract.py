from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_threejs_snake_contract as contract  # noqa: E402


class ThreeJsSnakeContractTest(unittest.TestCase):
    def test_current_app_contract_is_valid(self) -> None:
        self.assertEqual(contract.validate(), [])

    def test_missing_smoke_method_is_reported(self) -> None:
        main_js = contract.MAIN_PATH.read_text(encoding="utf-8")
        errors: list[str] = []

        contract.validate_main_js(main_js.replace("placeFoodAhead()", "placeFoodNearby()"), errors)

        self.assertIn("main.js smoke API missing methods: placeFoodAhead", errors)

    def test_missing_dom_id_is_reported(self) -> None:
        html = contract.INDEX_PATH.read_text(encoding="utf-8")
        summary = contract.parse_html(html.replace('id="score"', 'id="points"'))
        errors: list[str] = []

        contract.validate_html(summary, errors)

        self.assertIn("index.html missing required DOM ids: score", errors)

    def test_missing_app_file_is_reported(self) -> None:
        original_style_path = contract.STYLE_PATH
        missing_path = ROOT / "apps" / "threejs-snake" / "missing-style.css"
        try:
            contract.STYLE_PATH = missing_path
            errors = contract.validate()
        finally:
            contract.STYLE_PATH = original_style_path

        self.assertEqual(errors, [f"required app file missing: {missing_path.relative_to(ROOT)}"])


if __name__ == "__main__":
    unittest.main()
