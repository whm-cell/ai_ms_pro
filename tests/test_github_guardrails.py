from __future__ import annotations

import sys
import subprocess
import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_github_guardrails  # noqa: E402


class GitHubGuardrailsTest(unittest.TestCase):
    def test_security_evidence_workflow_is_expected(self) -> None:
        self.assertIn(
            ".github/workflows/security-evidence.yml",
            check_github_guardrails.EXPECTED_WORKFLOWS,
        )
        expected = check_github_guardrails.EXPECTED_WORKFLOWS[".github/workflows/security-evidence.yml"]
        self.assertEqual(expected["jobs"], {"security-evidence"})
        self.assertIn("Run OpenSSF Scorecard", expected["tokens"])

    def test_recommended_actions_call_out_unknown_remote_enforcement(self) -> None:
        checks = [
            check_github_guardrails.Check(
                name="branch protection",
                status="UNKNOWN",
                detail="HTTP 403",
            ),
            check_github_guardrails.Check(
                name="branch rulesets",
                status="UNKNOWN",
                detail="HTTP 403",
            ),
        ]

        actions = check_github_guardrails.recommended_actions(checks)

        self.assertEqual(len(actions), 2)
        self.assertIn("could not be proven", actions[0])
        self.assertIn("Keep OPEN-01 blocked", actions[1])

    def test_recommended_actions_call_out_private_free_plan_limit(self) -> None:
        plan_limit = "Upgrade to GitHub Pro or make this repository public to enable this feature. (HTTP 403)"
        checks = [
            check_github_guardrails.Check(
                name="branch protection",
                status="UNKNOWN",
                detail=plan_limit,
            ),
            check_github_guardrails.Check(
                name="branch rulesets",
                status="UNKNOWN",
                detail=plan_limit,
            ),
        ]

        actions = check_github_guardrails.recommended_actions(checks)

        self.assertEqual(len(actions), 2)
        self.assertIn("Private GitHub Free plan limit", actions[0])
        self.assertIn("keep local/CI evidence gates", actions[0])
        self.assertIn("future upgrade path", actions[1])

    def test_required_checks_from_nested_payload(self) -> None:
        payload = {
            "rules": [
                {
                    "parameters": {
                        "required_status_checks": [
                            {"context": "governance"},
                            {"name": "smoke"},
                            "dependency-review",
                        ],
                    },
                },
                {"contexts": ["windows-hook-runtime"]},
            ],
        }

        checks = check_github_guardrails.required_checks_from_payload(payload)

        self.assertEqual(
            checks,
            {"governance", "smoke", "dependency-review", "windows-hook-runtime"},
        )

    def test_orphan_gitlink_check_warns_without_gitmodules_mapping(self) -> None:
        def fake_run(cmd: list[str], root: Path) -> subprocess.CompletedProcess[str]:
            if cmd == ["git", "ls-files", "-s"]:
                return subprocess.CompletedProcess(
                    cmd,
                    0,
                    stdout="160000 4e3786368b2720a38ec0510f5473b1c55fe97fd9 0\toutput/rehearsal\n",
                    stderr="",
                )
            self.fail(f"unexpected command: {cmd}")

        with TemporaryDirectory() as tmp, patch("github_guardrails.local_checks.run", fake_run):
            check = check_github_guardrails.orphan_gitlink_check(Path(tmp))

        self.assertEqual(check.status, "WARN")
        self.assertIn("output/rehearsal", check.detail)


if __name__ == "__main__":
    unittest.main()
