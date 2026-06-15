from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_ci_agent_contract  # noqa: E402


VALID_RECORD = {
    "schema_version": "ci-agent-contract/v1",
    "id": "CIAC-2026-06-06-test",
    "recorded_at": "2026-06-06",
    "purpose": "Describe bounded advisory CI agent use without adding a real workflow.",
    "event": {"execution_triggers": ["pull_request"]},
    "permissions": {
        "profile": "default-minimal",
        "human_confirmed": False,
        "scopes": {
            "contents": "read",
            "pull-requests": "read",
            "checks": "read",
            "id-token": "none",
        },
    },
    "capabilities": {
        "secrets": False,
        "oidc": False,
        "repository_writes": False,
        "pr_comments": False,
        "pr_labels": False,
        "merge": False,
        "release": False,
        "deploy": False,
        "external_send": False,
    },
    "bounded_inputs": ["pull request diff metadata", "repo files needed by read-only checks"],
    "bounded_outputs": ["process exit code", "stdout audit report"],
    "tool_contracts": ["check_ai_governance", "check_tool_contracts"],
    "claim_boundary": {
        "no_hosted_cloud_agent_claim": True,
        "no_remote_enforcement_claim": True,
        "no_real_agent_workflow_claim": True,
        "summary": "Advisory contract only.",
    },
    "evidence_refs": [
        "docs/ai/standards/ci-agent-contract.md",
        "scripts/check_ci_agent_contract.py",
        "tests/test_ci_agent_contract.py",
    ],
}


def write_records(*records: dict[str, object] | str) -> Path:
    temp_dir = tempfile.TemporaryDirectory(dir=ROOT)
    path = Path(temp_dir.name) / "ci-agent-contract.jsonl"
    lines = [record if isinstance(record, str) else json.dumps(record) for record in records]
    path.write_text("\n".join(lines), encoding="utf-8")
    write_records.cleanups.append(temp_dir)
    return path


write_records.cleanups = []  # type: ignore[attr-defined]


class CIAgentContractTest(unittest.TestCase):
    def tearDown(self) -> None:
        while write_records.cleanups:  # type: ignore[attr-defined]
            write_records.cleanups.pop().cleanup()  # type: ignore[attr-defined]

    def test_repository_sample_passes(self) -> None:
        report = check_ci_agent_contract.build_report()

        self.assertEqual([], report.errors)
        self.assertEqual(1, report.record_count)
        self.assertIn("check_tool_contracts", report.referenced_tool_contracts)

    def test_valid_record_passes(self) -> None:
        report = check_ci_agent_contract.build_report(write_records(VALID_RECORD))

        self.assertEqual([], report.errors)

    def test_rejects_pull_request_target_execution(self) -> None:
        record = {**VALID_RECORD, "event": {"execution_triggers": ["pull_request_target"]}}

        report = check_ci_agent_contract.build_report(write_records(record))

        self.assertTrue(any("pull_request_target is forbidden" in error for error in report.errors))
        self.assertTrue(any("execution_triggers must be exactly" in error for error in report.errors))

    def test_rejects_extra_execution_trigger(self) -> None:
        record = {**VALID_RECORD, "event": {"execution_triggers": ["pull_request", "workflow_dispatch"]}}

        report = check_ci_agent_contract.build_report(write_records(record))

        self.assertTrue(any("execution_triggers must be exactly" in error for error in report.errors))

    def test_rejects_write_permissions_without_human_confirmation(self) -> None:
        permissions = {
            **VALID_RECORD["permissions"],
            "profile": "write",
            "scopes": {"contents": "write", "pull-requests": "read"},
        }
        record = {**VALID_RECORD, "permissions": permissions}

        report = check_ci_agent_contract.build_report(write_records(record))

        text = "\n".join(report.errors)
        self.assertIn("permissions.profile must be read-only/default-minimal", text)
        self.assertIn("permissions.scopes.contents must not request write permission", text)

    def test_rejects_oidc_and_secrets(self) -> None:
        record = {
            **VALID_RECORD,
            "permissions": {
                **VALID_RECORD["permissions"],
                "scopes": {"contents": "read", "id-token": "read"},
            },
            "capabilities": {**VALID_RECORD["capabilities"], "secrets": True, "oidc": True},
        }

        report = check_ci_agent_contract.build_report(write_records(record))

        text = "\n".join(report.errors)
        self.assertIn("permissions.scopes.id-token must disable OIDC/id-token", text)
        self.assertIn("capabilities.secrets is forbidden", text)
        self.assertIn("capabilities.oidc is forbidden", text)

    def test_rejects_repository_and_pr_side_effects(self) -> None:
        record = {
            **VALID_RECORD,
            "capabilities": {
                **VALID_RECORD["capabilities"],
                "repository_writes": True,
                "pr_comments": True,
                "pr_labels": True,
                "merge": True,
                "release": True,
                "deploy": True,
                "external_send": True,
            },
        }

        report = check_ci_agent_contract.build_report(write_records(record))

        text = "\n".join(report.errors)
        for field in ("repository_writes", "pr_comments", "pr_labels", "merge", "release", "deploy", "external_send"):
            self.assertIn(f"capabilities.{field} is forbidden", text)

    def test_rejects_missing_bounded_io_and_unknown_tool_contract(self) -> None:
        record = {
            **VALID_RECORD,
            "bounded_inputs": [],
            "bounded_outputs": [],
            "tool_contracts": ["missing_contract"],
        }

        report = check_ci_agent_contract.build_report(write_records(record))

        text = "\n".join(report.errors)
        self.assertIn("bounded_inputs must be a non-empty list", text)
        self.assertIn("bounded_outputs must be a non-empty list", text)
        self.assertIn("unknown tool contract: missing_contract", text)

    def test_rejects_hosted_or_remote_claim_boundaries(self) -> None:
        record = {
            **VALID_RECORD,
            "claim_boundary": {
                **VALID_RECORD["claim_boundary"],
                "no_hosted_cloud_agent_claim": False,
                "no_remote_enforcement_claim": False,
            },
        }

        report = check_ci_agent_contract.build_report(write_records(record))

        text = "\n".join(report.errors)
        self.assertIn("claim_boundary.no_hosted_cloud_agent_claim must be true", text)
        self.assertIn("claim_boundary.no_remote_enforcement_claim must be true", text)

    def test_cli_json_output_is_stable(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_ci_agent_contract.py"), "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn('"record_count": 1', result.stdout)
        self.assertIn('"referenced_tool_contracts"', result.stdout)
        self.assertIn('"errors": []', result.stdout)


if __name__ == "__main__":
    unittest.main()
