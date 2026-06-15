from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import playwright_smoke_utils  # noqa: E402


class PlaywrightSmokeUtilsTest(unittest.TestCase):
    def test_windows_prefers_cmd_launcher(self) -> None:
        self.assertEqual(
            playwright_smoke_utils.npx_candidate_names("nt"),
            ("npx.cmd", "npx.exe", "npx.bat", "npx"),
        )

    def test_posix_uses_plain_npx(self) -> None:
        self.assertEqual(playwright_smoke_utils.npx_candidate_names("posix"), ("npx",))

    def test_resolve_npx_uses_first_available_candidate(self) -> None:
        seen: list[str] = []

        def fake_which(name: str) -> str | None:
            seen.append(name)
            if name == "npx.exe":
                return "/toolchain/npx.exe"
            return None

        with mock.patch.object(playwright_smoke_utils.shutil, "which", side_effect=fake_which):
            self.assertEqual(playwright_smoke_utils.resolve_npx_command("nt"), "/toolchain/npx.exe")

        self.assertEqual(seen, ["npx.cmd", "npx.exe"])

    def test_resolve_npx_reports_missing_launcher(self) -> None:
        with mock.patch.object(playwright_smoke_utils.shutil, "which", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "npx is required"):
                playwright_smoke_utils.resolve_npx_command("posix")


if __name__ == "__main__":
    unittest.main()
