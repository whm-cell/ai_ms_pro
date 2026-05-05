from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_github_guardrails  # noqa: E402


class GitHubGuardrailsTest(unittest.TestCase):
    def test_security_evidence_workflow_is_expected(self) -> None:
        self.assertIn(
            ".github/workflows/security-evidence.yml",
            check_github_guardrails.EXPECTED_WORKFLOWS,
        )

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


if __name__ == "__main__":
    unittest.main()
