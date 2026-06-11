from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_prototype_artifact_review  # noqa: E402


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


VALID_TEXT = """
REQ-006 WS-02 ADR-017 /prototype/custom
This artifact does not replace canonical requirements.
surface identity and 页面 grammar are explicit.
state matrix includes empty_state and permission_denied as 关键状态.
Prototype only. No production API. 静态原型 and 不新增生产 API.
Review result: pass
"""


class PrototypeArtifactReviewTest(unittest.TestCase):
    def workspace(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp_dir = tempfile.TemporaryDirectory()
        root = Path(temp_dir.name)
        artifact_dir = root / "docs/ai/prototypes/custom-slice"
        for name in check_prototype_artifact_review.REQUIRED_ARTIFACTS:
            write(artifact_dir / name, f"# {name}\n\n{VALID_TEXT}\n")
        write(
            root / "app/prototype/custom/page.tsx",
            f"export default function Page() {{ return <main>{VALID_TEXT}</main>; }}\n",
        )
        write(root / "lib/prototype/customFixture.ts", f"export const fixture = `{VALID_TEXT}`;\n")
        return temp_dir, root

    def test_complete_artifact_package_passes(self) -> None:
        temp_dir, root = self.workspace()
        self.addCleanup(temp_dir.cleanup)

        report = check_prototype_artifact_review.build_report(
            root=root,
            artifact_dir="docs/ai/prototypes/custom-slice",
            page_path="app/prototype/custom/page.tsx",
            fixture_paths=("lib/prototype/customFixture.ts",),
            prototype_route="/prototype/custom",
            required_states=("empty_state", "permission_denied"),
        )

        self.assertEqual(report.errors, [])
        self.assertEqual(report.completeness_rate, 1.0)

    def test_missing_state_fails(self) -> None:
        temp_dir, root = self.workspace()
        self.addCleanup(temp_dir.cleanup)

        report = check_prototype_artifact_review.build_report(
            root=root,
            artifact_dir="docs/ai/prototypes/custom-slice",
            page_path="app/prototype/custom/page.tsx",
            fixture_paths=("lib/prototype/customFixture.ts",),
            prototype_route="/prototype/custom",
            required_states=("missing_state",),
        )

        self.assertTrue(any("missing_state" in error for error in report.errors))

    def test_tool_specific_consumer_fails(self) -> None:
        temp_dir, root = self.workspace()
        self.addCleanup(temp_dir.cleanup)
        artifact = root / "docs/ai/prototypes/custom-slice/provenance.md"
        artifact.write_text(artifact.read_text(encoding="utf-8") + "\nFigma\n", encoding="utf-8")

        report = check_prototype_artifact_review.build_report(
            root=root,
            artifact_dir="docs/ai/prototypes/custom-slice",
            page_path="app/prototype/custom/page.tsx",
            fixture_paths=("lib/prototype/customFixture.ts",),
            prototype_route="/prototype/custom",
            required_states=("empty_state",),
        )

        self.assertTrue(any("tool-agnostic" in error for error in report.errors))


if __name__ == "__main__":
    unittest.main()
