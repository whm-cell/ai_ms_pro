from __future__ import annotations

import tempfile
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_data_activation  # noqa: E402


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_config(root: Path, mode: str = "smoke", enabled: bool = True, extra: str = "") -> None:
    enabled_text = "true" if enabled else "false"
    write(
        root / ".codex/harness.toml",
        "[data_activation]\n"
        f"enabled = {enabled_text}\n"
        f'mode = "{mode}"\n\n'
        "[mock_data_boundary]\n"
        "enabled = true\n"
        'scan_roots = ["app", "mock-data", "tests"]\n'
        'fixture_paths = ["mock-data/**", "tests/fixtures/**"]\n'
        'allowed_mock_consumer_paths = ["tests/**", "**/*.stories.*"]\n'
        'manifest_required_paths = ["mock-data/**"]\n'
        'scenario_manifest_paths = ["mock-data/scenarios.jsonl"]\n'
        'runtime_import_denied_paths = ["mock-data/**"]\n'
        'import_alias_prefixes = ["@/"]\n'
        "max_inline_object_items = 3\n"
        "max_inline_array_from_length = 12\n"
        "max_inline_lines = 40\n"
        + extra,
    )


def manifest_row(
    *,
    surface: str = "dev",
    activation_state: str = "smoke",
    real_adapter_path: str = "",
    retire_when: str = "",
    evidence_refs: list[str] | None = None,
) -> str:
    fields = [
        '"schema":"mock-data-scenario/v1"',
        '"id":"users"',
        '"data_paths":["mock-data/users.ts"]',
        f'"surface":"{surface}"',
        '"source_truth":"manual-seed"',
        '"adapter":"fixture"',
        '"owner":"ai"',
        '"expires_at":"2026-12-31"',
        f'"activation_state":"{activation_state}"',
    ]
    if real_adapter_path:
        fields.append(f'"real_adapter_path":"{real_adapter_path}"')
    if retire_when:
        fields.append(f'"retire_when":"{retire_when}"')
    if evidence_refs is not None:
        fields.append('"activation_evidence_refs":[' + ",".join(f'"{item}"' for item in evidence_refs) + "]")
    return "{" + ",".join(fields) + "}\n"


class DataActivationTest(unittest.TestCase):
    def test_missing_config_is_noop(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = check_data_activation.build_report(Path(tmp))

        self.assertFalse(report.enabled)
        self.assertEqual(report.errors, [])
        self.assertEqual(report.findings, [])

    def test_invalid_mode_reports_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / ".codex/harness.toml", '[data_activation]\nenabled = true\nmode = "prod"\n')

            report = check_data_activation.build_report(root)

        self.assertIn("data_activation.mode", "\n".join(report.errors))

    def test_smoke_mode_allows_existing_fixture_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root, mode="smoke")
            write(root / "mock-data/users.ts", "export const users = [{ id: '1' }];\n")
            write(root / "mock-data/scenarios.jsonl", manifest_row())

            report = check_data_activation.build_report(root)

        self.assertEqual(report.errors, [])
        self.assertEqual(report.findings, [])

    def test_shadow_real_requires_adapter_and_retirement_plan_for_dev_demo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root, mode="shadow-real")
            write(root / "mock-data/users.ts", "export const users = [{ id: '1' }];\n")
            write(root / "mock-data/scenarios.jsonl", manifest_row())

            report = check_data_activation.build_report(root)

        codes = {item.code for item in report.findings}
        self.assertIn("missing-real-adapter-path", codes)
        self.assertIn("missing-retire-when", codes)

    def test_shadow_real_accepts_adapter_and_retirement_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root, mode="shadow-real")
            write(root / "app/usersAdapter.ts", "export async function loadUsers() { return []; }\n")
            write(root / "mock-data/users.ts", "export const users = [{ id: '1' }];\n")
            write(
                root / "mock-data/scenarios.jsonl",
                manifest_row(real_adapter_path="app/usersAdapter.ts", retire_when="adapter smoke passes"),
            )

            report = check_data_activation.build_report(root)

        self.assertEqual(report.findings, [])

    def test_real_mode_finds_runtime_mock_usage_and_unretired_dev_scenario(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root, mode="real")
            write(
                root / "app/page.tsx",
                "import { users } from '@/mock-data/users';\n"
                "export const mockRows = [\n"
                "  { id: 1 },\n"
                "  { id: 2 },\n"
                "  { id: 3 },\n"
                "  { id: 4 },\n"
                "];\n",
            )
            write(root / "mock-data/users.ts", "export const users = [{ id: '1' }];\n")
            write(root / "mock-data/scenarios.jsonl", manifest_row())

            report = check_data_activation.build_report(root)

        codes = {item.code for item in report.findings}
        self.assertIn("scenario-not-retired-for-real-mode", codes)
        self.assertIn("mock-import-in-runtime-path", codes)
        self.assertIn("inline-mock-array", codes)

    def test_real_mode_allows_test_story_or_contract_sample_smoke_data(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root, mode="real")
            write(root / "mock-data/users.ts", "export const users = [{ id: '1' }];\n")
            write(root / "mock-data/scenarios.jsonl", manifest_row(surface="contract-sample"))

            report = check_data_activation.build_report(root)

        self.assertEqual(report.findings, [])

    def test_real_mode_requires_retired_evidence_refs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_config(root, mode="real")
            write(root / "app/usersAdapter.ts", "export async function loadUsers() { return []; }\n")
            write(root / "mock-data/users.ts", "export const users = [{ id: '1' }];\n")
            write(
                root / "mock-data/scenarios.jsonl",
                manifest_row(
                    activation_state="retired",
                    real_adapter_path="app/usersAdapter.ts",
                    retire_when="adapter smoke passes",
                ),
            )

            report = check_data_activation.build_report(root)

        self.assertEqual([item.code for item in report.findings], ["missing-activation-evidence"])

    def test_strict_mode_returns_failure_on_findings(self) -> None:
        report = check_data_activation.DataActivationReport(
            enabled=True,
            mode="real",
            scenario_count=1,
            real_mode_mock_findings=0,
            findings=[
                check_data_activation.DataActivationFinding(
                    path="mock-data/scenarios.jsonl",
                    line=1,
                    code="scenario-not-retired-for-real-mode",
                    message="dev/demo scenario must be retired before real mode",
                )
            ],
            errors=[],
        )

        self.assertIn("REVIEW:", check_data_activation.render_report(report))

    def test_repository_config_smoke(self) -> None:
        report = check_data_activation.build_report(ROOT)

        self.assertTrue(report.enabled)
        self.assertEqual(report.mode, "smoke")
        self.assertEqual(report.errors, [])


if __name__ == "__main__":
    unittest.main()
