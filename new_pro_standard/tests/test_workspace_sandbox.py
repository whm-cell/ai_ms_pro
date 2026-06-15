from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_workspace_sandbox  # noqa: E402


VALID_MANIFEST = """
version = 1

[workspace]
repo_root = "."
current_cwd = "."
intent = "Operate inside this repository."

[sandbox]
writable_roots = ["."]
network_default = "restricted"
approval_policy = "never-auto-external-permission"
subagent_isolation_rule = "Subagents use compact packets and declared roots only."

[runtime]
dirs = [".codex/runtime", ".codex/runtime/sessions"]

[outputs]
dirs = ["output"]

[rehydration]
inputs = ["AGENTS.md", "docs/ai/index.md", ".codex/runtime/sessions"]

[claims]
forbidden = [
  "Do not claim external OpenAI interop.",
  "Do not claim external MCP interop.",
  "Do not claim external A2A interop.",
  "Do not claim external OTLP interop.",
]
"""


class WorkspaceSandboxManifestTest(unittest.TestCase):
    def manifest_path(self, text: str) -> Path:
        temp_dir = tempfile.TemporaryDirectory(dir=ROOT)
        self.addCleanup(temp_dir.cleanup)
        workspace = Path(temp_dir.name)
        manifest_dir = workspace / ".codex"
        manifest_dir.mkdir()
        path = manifest_dir / "sandbox-manifest.toml"
        path.write_text(text.strip() + "\n", encoding="utf-8")
        return path

    def errors_for(self, text: str) -> list[str]:
        path = self.manifest_path(text)
        data, errors = check_workspace_sandbox.load_manifest(path)
        self.assertIsNotNone(data)
        errors.extend(check_workspace_sandbox.validate_manifest(data or {}, path))
        return errors

    def test_valid_manifest_passes(self) -> None:
        self.assertEqual(self.errors_for(VALID_MANIFEST), [])

    def test_missing_key_fails(self) -> None:
        manifest = VALID_MANIFEST.replace('intent = "Operate inside this repository."\n', "")

        errors = self.errors_for(manifest)

        self.assertIn("missing key [workspace].intent", errors)

    def test_network_open_fails(self) -> None:
        manifest = VALID_MANIFEST.replace('network_default = "restricted"', 'network_default = "open"')

        errors = self.errors_for(manifest)

        self.assertIn("sandbox.network_default must not be open", errors)

    def test_absolute_path_outside_repo_fails(self) -> None:
        manifest = VALID_MANIFEST.replace('dirs = ["output"]', 'dirs = ["/tmp/workspace-output"]')

        errors = self.errors_for(manifest)

        self.assertIn("outputs.dirs contains path outside repo: /tmp/workspace-output", errors)

    def test_forbidden_claims_missing_fails(self) -> None:
        manifest = VALID_MANIFEST.replace(
            """
forbidden = [
  "Do not claim external OpenAI interop.",
  "Do not claim external MCP interop.",
  "Do not claim external A2A interop.",
  "Do not claim external OTLP interop.",
]
""".strip(),
            'forbidden = ["Do not overstate local checker guarantees."]',
        )

        errors = self.errors_for(manifest)

        self.assertIn(
            "claims.forbidden must prohibit external OpenAI/MCP/A2A/OTLP interop claims",
            errors,
        )


if __name__ == "__main__":
    unittest.main()
