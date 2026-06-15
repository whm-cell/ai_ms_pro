from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_agent_run_provenance  # noqa: E402


VALID_RECORD = {
    "schema_version": "agent-run-provenance/v1",
    "id": "ARP-2026-05-29-local-provenance-standard",
    "recorded_at": "2026-05-29",
    "task_profile": "complex",
    "task_summary": "Add a local-first agent-run provenance standard for harness maintenance.",
    "requirement_ids": ["REQ-003"],
    "workstream_ids": ["WS-01"],
    "platform_boundary": "local-with-ci-evidence",
    "authority": {
        "actor": "main-agent",
        "authority_level": "canonical-writer",
        "canonical_write": True,
        "allowed_outputs": ["docs/ai canonical summaries", "repo-local checker output"],
    },
    "changed_files": [
        "docs/ai/standards/agent-run-provenance.md",
        "scripts/check_agent_run_provenance.py",
    ],
    "tool_contracts": ["check_tool_contracts"],
    "validation": [
        {
            "command": ".codex/hooks/run_with_repo_python.sh scripts/check_agent_run_provenance.py",
            "outcome": "pass",
            "evidence_refs": ["scripts/check_agent_run_provenance.py"],
        }
    ],
    "claim_boundaries": {
        "claims": [
            {
                "state": "verified-local",
                "summary": "The checker validates local JSONL records and referenced repo files.",
            }
        ],
        "unknown_or_plan_limited": ["GitHub branch protection remains private-Free UNKNOWN."],
        "not_claimed": ["GitHub Copilot cloud agent tasks are not part of this local-first standard."],
    },
    "evidence_refs": ["docs/ai/tool-contracts/contracts.json", "scripts/check_agent_run_provenance.py"],
    "decision_summary": "Keep provenance local-first and evidence-bound.",
}


UNBOUND_RECORD = {
    **VALID_RECORD,
    "id": "ARP-2026-05-29-unbound-task",
    "requirement_ids": ["unbound"],
    "workstream_ids": ["unbound"],
}


def write_records(*records: dict[str, object] | str) -> Path:
    temp_dir = tempfile.TemporaryDirectory(dir=ROOT)
    path = Path(temp_dir.name) / "agent-run-provenance.jsonl"
    lines = [record if isinstance(record, str) else json.dumps(record) for record in records]
    path.write_text("\n".join(lines), encoding="utf-8")
    write_records.cleanups.append(temp_dir)
    return path


write_records.cleanups = []  # type: ignore[attr-defined]


class AgentRunProvenanceTest(unittest.TestCase):
    def tearDown(self) -> None:
        while write_records.cleanups:  # type: ignore[attr-defined]
            write_records.cleanups.pop().cleanup()  # type: ignore[attr-defined]

    def test_repository_sample_passes(self) -> None:
        report = check_agent_run_provenance.build_report()

        self.assertEqual([], report.errors)
        self.assertGreaterEqual(report.record_count, 1)
        self.assertIn("check_agent_run_provenance", report.referenced_tool_contracts)

    def test_valid_record_passes(self) -> None:
        report = check_agent_run_provenance.build_report(write_records(VALID_RECORD))

        self.assertEqual([], report.errors)
        self.assertEqual(1, report.canonical_write_count)
        self.assertEqual(1, report.local_first_count)

    def test_unbound_traceability_passes_when_both_sides_unbound(self) -> None:
        report = check_agent_run_provenance.build_report(write_records(UNBOUND_RECORD))

        self.assertEqual([], report.errors)

    def test_rejects_mismatched_unbound_traceability(self) -> None:
        record = {**VALID_RECORD, "requirement_ids": ["unbound"], "workstream_ids": ["WS-01"]}

        report = check_agent_run_provenance.build_report(write_records(record))

        self.assertTrue(any("must be bound or unbound together" in error for error in report.errors))

    def test_rejects_unknown_tool_contract(self) -> None:
        record = {**VALID_RECORD, "tool_contracts": ["github-copilot-cloud-agent-task"]}

        report = check_agent_run_provenance.build_report(write_records(record))

        self.assertTrue(any("unknown tool contract" in error for error in report.errors))

    def test_rejects_cloud_boundary_as_platform_boundary(self) -> None:
        record = {**VALID_RECORD, "platform_boundary": "github-copilot-cloud-agent"}

        report = check_agent_run_provenance.build_report(write_records(record))

        self.assertTrue(any("platform_boundary must be one of" in error for error in report.errors))

    def test_rejects_raw_runtime_material(self) -> None:
        record = {
            **VALID_RECORD,
            "transcript_path": ".codex/runtime/sessions/raw.jsonl",
            "evidence_refs": [".codex/runtime/observations/raw.jsonl"],
        }

        report = check_agent_run_provenance.build_report(write_records(record))

        text = "\n".join(report.errors)
        self.assertIn("forbidden raw runtime key: transcript_path", text)
        self.assertIn("must not reference local runtime material", text)

    def test_rejects_non_canonical_authority_writing_canonical_docs(self) -> None:
        record = {
            **VALID_RECORD,
            "authority": {
                **VALID_RECORD["authority"],
                "authority_level": "draft-only",
                "canonical_write": True,
            },
        }

        report = check_agent_run_provenance.build_report(write_records(record))

        self.assertTrue(any("only canonical-writer authority" in error for error in report.errors))

    def test_cli_json_output_is_stable(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_agent_run_provenance.py"), "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn('"record_count"', result.stdout)
        self.assertIn('"referenced_tool_contracts"', result.stdout)
        self.assertIn('"errors": []', result.stdout)


if __name__ == "__main__":
    unittest.main()
