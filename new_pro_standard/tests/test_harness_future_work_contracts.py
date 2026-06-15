from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_harness_future_work_contracts as future_contracts  # noqa: E402


VALID_CONTRACTS = """\
{"schema_version":"harness-future-work-contract/v1","id":"FWC-test-remote","gap_id":"GAP-TRACE-REMOTE-INTEROP","status":"needs-adr","contract_kind":"remote-interop","adr_required":true,"adr_refs":["none"],"sample_collection_allowed":false,"no_external_claim":true,"auth_model":"TBD auth.","endpoint_or_authority_scope":"TBD endpoint.","redaction_or_boundary_model":"TBD redaction.","cost_or_stop_boundary":"TBD cost.","decision":"No samples before ADR.","evidence_refs":["docs/ai/agentic-harness-gap-roadmap.md"],"note":"No external claim."}
{"schema_version":"harness-future-work-contract/v1","id":"FWC-test-cascade","gap_id":"GAP-AGENTIC-CASCADE-STOP","status":"needs-adr","contract_kind":"agentic-control","adr_required":true,"adr_refs":["none"],"sample_collection_allowed":false,"no_external_claim":true,"auth_model":"TBD authority.","endpoint_or_authority_scope":"TBD delegation.","redaction_or_boundary_model":"TBD redaction.","cost_or_stop_boundary":"TBD stop.","decision":"No samples before ADR.","evidence_refs":["docs/ai/agentic-harness-gap-roadmap.md"],"note":"No real incident claim."}
"""


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def approved_remote_contract_with_adr(adr_ref: str) -> str:
    lines = VALID_CONTRACTS.splitlines()
    first = lines[0]
    first = first.replace('"status":"needs-adr"', '"status":"approved-for-sampling"')
    first = first.replace('"adr_refs":["none"]', f'"adr_refs":["{adr_ref}"]')
    first = first.replace('"sample_collection_allowed":false', '"sample_collection_allowed":true')
    return "\n".join([first, lines[1]]) + "\n"


class HarnessFutureWorkContractsTest(unittest.TestCase):
    def test_repository_contracts_cover_future_work_gaps_with_approved_sampling_paths(self) -> None:
        report = future_contracts.build_report()

        self.assertEqual([], report.errors)
        self.assertEqual(2, report.future_gap_count)
        self.assertEqual(2, report.contract_count)
        self.assertEqual(0, report.approved_for_sampling_count)
        self.assertEqual(2, report.blocked_until_adr_count)
        self.assertEqual([], report.missing_contracts)
        states = {state.gap_id: state for state in report.contract_states}
        self.assertEqual({"GAP-TRACE-REMOTE-INTEROP", "GAP-AGENTIC-CASCADE-STOP"}, set(states))
        self.assertFalse(states["GAP-TRACE-REMOTE-INTEROP"].sample_collection_allowed)
        self.assertTrue(states["GAP-TRACE-REMOTE-INTEROP"].missing_adr_refs)
        self.assertIn("auth_model", states["GAP-TRACE-REMOTE-INTEROP"].required_decision_fields)
        self.assertIn("check_harness_future_work_contracts.py", states["GAP-TRACE-REMOTE-INTEROP"].review_command)
        self.assertIn("Blocked because sample_collection_allowed=false", states["GAP-TRACE-REMOTE-INTEROP"].sample_collection_boundary)
        self.assertFalse(states["GAP-AGENTIC-CASCADE-STOP"].sample_collection_allowed)
        self.assertTrue(states["GAP-AGENTIC-CASCADE-STOP"].missing_adr_refs)
        self.assertIn("Blocked because sample_collection_allowed=false", states["GAP-AGENTIC-CASCADE-STOP"].sample_collection_boundary)

    def test_reports_missing_future_gap_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "contracts.jsonl"
            write(path, "\n".join(VALID_CONTRACTS.splitlines()[:1]) + "\n")

            report = future_contracts.build_report(path)

        self.assertIn("missing future-work contract for gap: GAP-AGENTIC-CASCADE-STOP", report.errors)
        states = {state.gap_id: state for state in report.contract_states}
        self.assertEqual("missing-contract", states["GAP-AGENTIC-CASCADE-STOP"].status)
        self.assertEqual("missing", states["GAP-AGENTIC-CASCADE-STOP"].contract_id)
        self.assertFalse(states["GAP-AGENTIC-CASCADE-STOP"].sample_collection_allowed)

    def test_rejects_non_approved_contract_that_allows_sampling(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "contracts.jsonl"
            write(path, VALID_CONTRACTS.replace('"sample_collection_allowed":false', '"sample_collection_allowed":true', 1))

            report = future_contracts.build_report(path)

        self.assertTrue(any("non-approved contracts must set sample_collection_allowed=false" in error for error in report.errors))

    def test_rejects_duplicate_gap_contract_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "contracts.jsonl"
            duplicate = VALID_CONTRACTS.splitlines()[0].replace("FWC-test-remote", "FWC-test-remote-copy")
            write(path, VALID_CONTRACTS + duplicate + "\n")

            report = future_contracts.build_report(path)

        self.assertTrue(any("duplicate gap_id: GAP-TRACE-REMOTE-INTEROP" in error for error in report.errors))

    def test_approved_sampling_requires_concrete_adr_ref(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "contracts.jsonl"
            text = VALID_CONTRACTS.replace('"status":"needs-adr"', '"status":"approved-for-sampling"', 1)
            text = text.replace('"sample_collection_allowed":false', '"sample_collection_allowed":true', 1)
            write(path, text)

            report = future_contracts.build_report(path)

        self.assertTrue(any("approved sampling requires concrete adr_refs" in error for error in report.errors))

    def test_approved_sampling_requires_repo_adr_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "contracts.jsonl"
            write(path, approved_remote_contract_with_adr("docs/ai/harness-open-items.md"))

            report = future_contracts.build_report(path)

        self.assertTrue(any("approved sampling adr_ref must be a repo ADR path" in error for error in report.errors))

    def test_approved_sampling_requires_existing_adr_ref(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "contracts.jsonl"
            write(path, approved_remote_contract_with_adr("docs/ai/adr/ADR-999-missing.md"))

            report = future_contracts.build_report(path)

        self.assertTrue(any("approved sampling adr_ref does not exist" in error for error in report.errors))

    def test_approved_sampling_requires_adopted_adr_with_contract_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "contracts.jsonl"
            write(path, approved_remote_contract_with_adr("docs/ai/adr/ADR-014-context-budget-audit.md"))

            report = future_contracts.build_report(path)

        self.assertTrue(any("approved sampling adr_ref does not exist" in error for error in report.errors))

    def test_cli_json_output_is_stable(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_harness_future_work_contracts.py"), "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn('"future_gap_count": 2', result.stdout)
        self.assertIn('"approved_for_sampling_count": 0', result.stdout)
        data = json.loads(result.stdout)
        state = data["contract_states"][0]
        self.assertIn("next_action", state)
        self.assertIn("review_command", state)
        self.assertIn("missing_adr_refs", state)
        self.assertIn("sample_collection_boundary", state)


if __name__ == "__main__":
    unittest.main()
