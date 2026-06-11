from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_harness_future_work_contract_candidate as candidate_review  # noqa: E402


def write_candidate(record: dict[str, object]) -> Path:
    temp = tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".jsonl")
    with temp:
        temp.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
    return Path(temp.name)


def remote_contract_candidate() -> dict[str, object]:
    return {
        "schema_version": "harness-future-work-contract/v1",
        "id": "FWC-2026-05-24-trace-remote-interop",
        "gap_id": "GAP-TRACE-REMOTE-INTEROP",
        "status": "needs-adr",
        "contract_kind": "remote-interop",
        "adr_required": True,
        "adr_refs": ["none"],
        "sample_collection_allowed": False,
        "no_external_claim": True,
        "auth_model": "TBD auth boundary.",
        "endpoint_or_authority_scope": "TBD endpoint boundary.",
        "redaction_or_boundary_model": "TBD redaction boundary.",
        "cost_or_stop_boundary": "TBD cost boundary.",
        "decision": "No samples before ADR.",
        "evidence_refs": ["docs/ai/agentic-harness-gap-roadmap.md"],
        "note": "Contract candidate only.",
    }


class HarnessFutureWorkContractCandidateTest(unittest.TestCase):
    def test_approved_remote_contract_is_no_longer_in_candidate_lane(self) -> None:
        template = remote_contract_candidate()
        path = write_candidate(template)
        try:
            report = candidate_review.build_report(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertEqual([], report.checker_errors)
        self.assertFalse(report.review_allowed)
        self.assertEqual("FWC-2026-05-24-trace-remote-interop", report.contract_id)
        self.assertEqual(report.contract_id, report.current_contract_id)
        self.assertEqual(1, report.current_contract_line)
        self.assertFalse(report.sample_collection_allowed)
        self.assertTrue(report.missing_adr_refs)
        self.assertEqual("append-new-pending-slot", report.ledger_action)
        self.assertEqual("needs-first-real-sample", report.readiness)
        self.assertEqual("accepted real generic gap samples", report.source_metric)
        self.assertEqual("0/2", report.current_to_target)
        self.assertEqual("requires-approved-remote-interop", report.capture_gate)
        self.assertIn("ADR-017", report.capture_gate_detail)
        self.assertIn("endpoint", " ".join(report.evidence_needed))
        self.assertIn("redaction", " ".join(report.evidence_needed))
        self.assertIn("remote interop probe", report.trigger)
        self.assertIn("Bounded evidence", report.boundary)
        self.assertEqual(
            ".codex/hooks/run_with_repo_python.sh scripts/plan_harness_sample_collection.py "
            "--gap-id GAP-TRACE-REMOTE-INTEROP --ledger-action append-new-pending-slot --capture-card",
            report.planner_command,
        )
        self.assertEqual(
            ".codex/hooks/run_with_repo_python.sh scripts/build_harness_sample_intake_bundle.py "
            "--gap-id GAP-TRACE-REMOTE-INTEROP --ledger-action append-new-pending-slot --summary",
            report.intake_command,
        )
        self.assertTrue(any("current queue lane is append-new-pending-slot" in error for error in report.errors))
        self.assertIn("check_harness_future_work_contract_candidate.py", report.candidate_review_command)
        self.assertIn("check_harness_future_work_contracts.py", report.next_contract_audit_command)

    def test_rejects_draft_id_that_would_duplicate_existing_gap(self) -> None:
        template = remote_contract_candidate()
        template["id"] = "FWC-DRAFT-2026-05-24-trace-remote-interop"
        path = write_candidate(template)
        try:
            report = candidate_review.build_report(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertFalse(report.review_allowed)
        self.assertTrue(any("replace the row instead of appending a duplicate" in error for error in report.errors))

    def test_rejects_approved_sampling_without_concrete_adr_ref(self) -> None:
        template = remote_contract_candidate()
        template["status"] = "approved-for-sampling"
        template["sample_collection_allowed"] = True
        path = write_candidate(template)
        try:
            report = candidate_review.build_report(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertFalse(report.review_allowed)
        self.assertTrue(any("approved sampling requires concrete adr_refs" in error for error in report.checker_errors))

    def test_rejects_approved_sampling_with_missing_adr_ref(self) -> None:
        template = remote_contract_candidate()
        template["status"] = "approved-for-sampling"
        template["sample_collection_allowed"] = True
        template["adr_refs"] = ["docs/ai/adr/ADR-999-missing.md"]
        path = write_candidate(template)
        try:
            report = candidate_review.build_report(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertFalse(report.review_allowed)
        self.assertTrue(any("approved sampling adr_ref does not exist" in error for error in report.checker_errors))

    def test_rejects_candidate_when_current_queue_item_is_missing(self) -> None:
        template = remote_contract_candidate()
        path = write_candidate(template)
        try:
            with patch(
                "check_harness_future_work_contract_candidate."
                "harness_future_work_contract_context.plan_harness_sample_collection.build_queue",
                return_value=[],
            ):
                report = candidate_review.build_report(path)
        finally:
            path.unlink(missing_ok=True)

        self.assertFalse(report.review_allowed)
        self.assertTrue(
            any("no current collection queue item found for define-contract-precondition lane" in error for error in report.errors)
        )

    def test_cli_json_output_reports_candidate_state(self) -> None:
        template = remote_contract_candidate()
        path = write_candidate(template)
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/check_harness_future_work_contract_candidate.py",
                    str(path),
                    "--json",
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
        finally:
            path.unlink(missing_ok=True)
        data = json.loads(result.stdout)

        self.assertNotEqual(0, result.returncode)
        self.assertFalse(data["review_allowed"])
        self.assertEqual("GAP-TRACE-REMOTE-INTEROP", data["gap_id"])
        self.assertEqual("needs-adr", data["status"])
        self.assertEqual("append-new-pending-slot", data["ledger_action"])
        self.assertEqual("requires-approved-remote-interop", data["capture_gate"])
        self.assertIn("evidence_needed", data)
        self.assertIn("--ledger-action append-new-pending-slot", data["planner_command"])
        self.assertIn("--ledger-action append-new-pending-slot", data["intake_command"])
        self.assertTrue(any("current queue lane is append-new-pending-slot" in error for error in data["errors"]))
        self.assertIn("check_harness_future_work_contracts.py", data["next_contract_audit_command"])


if __name__ == "__main__":
    unittest.main()
