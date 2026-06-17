from __future__ import annotations

import tempfile
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_mock_data_boundary  # noqa: E402


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_config(root: Path, body: str = "") -> None:
    write(
        root / ".codex/harness.toml",
        "[mock_data_boundary]\n"
        "enabled = true\n"
        'scan_roots = ["app", "fixtures", "mocks", "mock-data", "tests"]\n'
        'fixture_paths = ["fixtures/**", "mocks/**", "mock-data/**", "tests/fixtures/**"]\n'
        'allowed_mock_consumer_paths = ["tests/**", "**/*.stories.*"]\n'
        "max_inline_object_items = 3\n"
        "max_inline_array_from_length = 12\n"
        "max_inline_lines = 40\n"
        + body,
    )


def manifest_row(data_path: str, row_id: str = "users") -> str:
    return (
        '{"schema":"mock-data-scenario/v1",'
        f'"id":"{row_id}",'
        f'"data_paths":["{data_path}"],'
        '"surface":"dev",'
        '"source_truth":"manual-seed",'
        '"adapter":"fixture",'
        '"owner":"ai",'
        '"expires_at":"2026-12-31"}\n'
    )


def activation_manifest_row(data_path: str, activation_state: str = "shadow-real") -> str:
    return (
        '{"schema":"mock-data-scenario/v1",'
        '"id":"users",'
        f'"data_paths":["{data_path}"],'
        '"surface":"dev",'
        '"source_truth":"manual-seed",'
        '"adapter":"fixture",'
        '"owner":"ai",'
        '"expires_at":"2026-12-31",'
        f'"activation_state":"{activation_state}",'
        '"real_adapter_path":"app/usersAdapter.ts",'
        '"activation_evidence_refs":["docs/ai/working-context.md"],'
        '"retire_when":"real adapter smoke passes"}\n'
    )


class MockDataBoundaryTest(unittest.TestCase):
    def test_inline_mock_array_in_page_requires_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root)
            write(
                root / "app/page.tsx",
                """
export const mockUsers = [
  { id: "1" },
  { id: "2" },
  { id: "3" },
  { id: "4" },
];
""",
            )

            report = check_mock_data_boundary.build_report(root)

        self.assertEqual(len(report.findings), 1)
        self.assertEqual(report.findings[0].code, "inline-mock-array")
        self.assertIn("app/page.tsx", report.findings[0].path)

    def test_fixture_path_allows_large_mock_data_with_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root)
            write(
                root / "fixtures/users.ts",
                """
export const mockUsers = [
  { id: "1" },
  { id: "2" },
  { id: "3" },
  { id: "4" },
];
""",
            )
            write(root / "mock-data/scenarios.jsonl", manifest_row("fixtures/users.ts"))

            report = check_mock_data_boundary.build_report(root)

        self.assertEqual(report.findings, [])

    def test_manifest_allows_data_activation_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root)
            write(root / "app/usersAdapter.ts", "export const adapter = true;\n")
            write(root / "mock-data/users.ts", "export const users = [{ id: '1' }];\n")
            write(root / "mock-data/scenarios.jsonl", activation_manifest_row("mock-data/users.ts"))
            write(root / "docs/ai/working-context.md", "# Context\n")

            report = check_mock_data_boundary.build_report(root)

        self.assertEqual(report.findings, [])

    def test_manifest_rejects_invalid_activation_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root)
            write(root / "mock-data/users.ts", "export const users = [{ id: '1' }];\n")
            write(root / "mock-data/scenarios.jsonl", activation_manifest_row("mock-data/users.ts", "prod"))

            report = check_mock_data_boundary.build_report(root)

        self.assertEqual(len(report.findings), 1)
        self.assertEqual(report.findings[0].code, "invalid-scenario-manifest-row")

    def test_large_fixture_without_manifest_requires_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root)
            write(
                root / "mock-data/users.ts",
                """
export const users = [
  { id: "1" },
  { id: "2" },
  { id: "3" },
  { id: "4" },
];
""",
            )

            report = check_mock_data_boundary.build_report(root)

        self.assertEqual(len(report.findings), 1)
        self.assertEqual(report.findings[0].code, "fixture-without-scenario-manifest")
        self.assertEqual(report.findings[0].suggested_layer, "scenario-manifest")

    def test_large_array_from_mock_requires_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root)
            write(root / "app/page.tsx", "const mockRows = Array.from({ length: 80 }, (_, index) => ({ id: index }));\n")

            report = check_mock_data_boundary.build_report(root)

        self.assertEqual(len(report.findings), 1)
        self.assertEqual(report.findings[0].code, "large-generated-mock")

    def test_runtime_mock_like_import_requires_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root)
            write(root / "app/page.tsx", "import { users } from '../fixtures/mockUsers';\n")

            report = check_mock_data_boundary.build_report(root)

        self.assertEqual(len(report.findings), 1)
        self.assertEqual(report.findings[0].code, "mock-import-in-runtime-path")

    def test_runtime_fixture_import_requires_review_without_mock_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root)
            write(root / "app/page.tsx", "import { users } from '../fixtures/users';\n")
            write(root / "fixtures/users.ts", "export const users = [{ id: '1' }];\n")

            report = check_mock_data_boundary.build_report(root)

        self.assertEqual(len(report.findings), 1)
        self.assertEqual(report.findings[0].code, "mock-import-in-runtime-path")
        self.assertEqual(report.findings[0].suggested_layer, "network-handler-or-adapter")

    def test_runtime_alias_mock_import_requires_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root)
            write(root / "app/page.tsx", "import { handlers } from '@/mocks/handlers';\n")
            write(root / "mocks/handlers.ts", "export const handlers = [];\n")

            report = check_mock_data_boundary.build_report(root)

        self.assertEqual(len(report.findings), 1)
        self.assertEqual(report.findings[0].code, "mock-import-in-runtime-path")

    def test_test_file_can_import_mock_like_module(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root)
            write(root / "tests/page.test.tsx", "import { users } from '../fixtures/mockUsers';\n")

            report = check_mock_data_boundary.build_report(root)

        self.assertEqual(report.findings, [])

    def test_manifest_missing_path_requires_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root)
            write(root / "mock-data/scenarios.jsonl", manifest_row("mock-data/missing.ts"))

            report = check_mock_data_boundary.build_report(root)

        self.assertEqual(len(report.findings), 1)
        self.assertEqual(report.findings[0].code, "missing-scenario-data-path")

    def test_manifest_duplicate_id_and_path_require_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root)
            write(root / "mock-data/users.ts", "export const users = [{ id: '1' }];\n")
            write(
                root / "mock-data/scenarios.jsonl",
                manifest_row("mock-data/users.ts", row_id="users") + manifest_row("mock-data/users.ts", row_id="users"),
            )

            report = check_mock_data_boundary.build_report(root)

        codes = {finding.code for finding in report.findings}
        self.assertIn("duplicate-scenario-manifest-id", codes)
        self.assertIn("duplicate-scenario-data-path", codes)

    def test_fixture_factory_with_math_random_requires_seed_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root)
            write(root / "mock-data/users.ts", "export const user = { id: Math.random() };\n")

            report = check_mock_data_boundary.build_report(root)

        self.assertEqual(len(report.findings), 1)
        self.assertEqual(report.findings[0].code, "unseeded-fixture-factory")

    def test_fixture_factory_with_unseeded_faker_requires_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root)
            write(root / "mock-data/users.ts", "export const user = { name: faker.person.fullName() };\n")

            report = check_mock_data_boundary.build_report(root)

        self.assertEqual(len(report.findings), 1)
        self.assertEqual(report.findings[0].code, "unseeded-fixture-factory")

    def test_fixture_factory_with_seeded_faker_is_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root)
            write(root / "mock-data/users.ts", "faker.seed(42);\nexport const user = { name: faker.person.fullName() };\n")

            report = check_mock_data_boundary.build_report(root)

        self.assertEqual(report.findings, [])

    def test_strict_mode_would_fail_on_findings(self) -> None:
        report = check_mock_data_boundary.MockDataBoundaryReport(
            enabled=True,
            scanned_files=["app/page.tsx"],
            findings=[
                check_mock_data_boundary.MockDataFinding(
                    path="app/page.tsx",
                    line=1,
                    code="inline-mock-array",
                    message="move inline mock-like data",
                )
            ],
            errors=[],
        )

        self.assertIn("REVIEW:", check_mock_data_boundary.render_report(report))

    def test_json_fields_include_suggestions(self) -> None:
        finding = check_mock_data_boundary.MockDataFinding(
            path="app/page.tsx",
            line=1,
            code="inline-mock-array",
            message="move inline mock-like data",
            suggested_layer="scenario-factory",
            suggested_paths=("mock-data/scenarios.jsonl",),
        )

        self.assertEqual(finding.suggested_layer, "scenario-factory")
        self.assertIn("mock-data/scenarios.jsonl", finding.suggested_paths)
        self.assertIn("docs/ai/standards/mock-data-boundary.md", finding.doc_ref)

    def test_repository_config_smoke(self) -> None:
        report = check_mock_data_boundary.build_report(ROOT)

        self.assertTrue(report.enabled)
        self.assertEqual(report.errors, [])


if __name__ == "__main__":
    unittest.main()
