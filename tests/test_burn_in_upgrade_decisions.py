from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_burn_in_ledger  # noqa: E402
import check_burn_in_upgrade_decisions  # noqa: E402


def valid_record(**overrides: object) -> dict[str, object]:
    record: dict[str, object] = {
        "schema_version": "check-burn-in-upgrade-decision/v1",
        "id": "CBUD-test-demo",
        "check": "demo.py",
        "decision": "keep-candidate",
        "decided_at": "2026-05-25",
        "current_decision_at_review": "keep-candidate",
        "accepted_samples": 2,
        "sample_target": 2,
        "false_positive_review": "0 accepted false positives.",
        "repair_path": "Fix the contract drift and rerun the checker.",
        "cost_review": "Low local runtime; medium reviewer cost.",
        "reviewer_burden": "Keep reviewer burden advisory until broader samples exist.",
        "rationale": "Sample target is met, but diversity remains narrow.",
        "decision_ref": "docs/ai/check-burn-in-ledger.md",
        "evidence_refs": ["docs/ai/check-burn-in-ledger.md"],
        "next_evidence_needed": ["more diverse samples"],
        "no_raw_runtime": True,
    }
    record.update(overrides)
    return record


def write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    import json

    path.write_text("\n".join(json.dumps(record) for record in records) + "\n", encoding="utf-8")


class BurnInUpgradeDecisionsTest(unittest.TestCase):
    def test_repository_decisions_cover_review_needed_checks(self) -> None:
        report = check_burn_in_upgrade_decisions.build_report()

        self.assertEqual([], report.errors)
        self.assertEqual(["check_code_shape.py", "check_tool_contracts.py"], report.upgrade_review_needed_checks)
        self.assertEqual(["check_code_shape.py", "check_tool_contracts.py"], report.decided_checks)
        self.assertEqual({"keep-candidate": 2}, report.decision_counts)
        self.assertIn("check_code_shape.py", report.next_evidence_needed_by_check)
        self.assertIn("check_tool_contracts.py", report.next_evidence_needed_by_check)

    def test_reports_missing_review_decision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            decisions = Path(tmp) / "decisions.jsonl"
            decisions.write_text("", encoding="utf-8")

            report = check_burn_in_upgrade_decisions.build_report(decisions)

        self.assertIn("missing upgrade decision for review-needed check: check_code_shape.py", report.errors)
        self.assertIn("missing upgrade decision for review-needed check: check_tool_contracts.py", report.errors)

    def test_validates_snapshot_against_current_row(self) -> None:
        row = check_burn_in_ledger.BurnInLedgerRow(
            check="demo.py",
            accepted_samples=2,
            sample_target=2,
            remaining_samples=0,
            evidence_refs=["evidence.md"],
            false_positives="0",
            repair_path="fix",
            cost="low",
            current_decision="keep-candidate",
            next_evidence="upgrade decision review",
            upgrade_eligible=True,
            upgrade_review_needed=True,
        )
        with tempfile.TemporaryDirectory() as tmp:
            decisions = Path(tmp) / "decisions.jsonl"
            write_jsonl(decisions, [valid_record(accepted_samples=1)])
            with mock.patch.object(
                check_burn_in_upgrade_decisions.check_burn_in_ledger,
                "validate",
                return_value=check_burn_in_ledger.LedgerResult(
                    registry_path="registry.md",
                    ledger_path="ledger.md",
                    blocking_candidate_count=1,
                    ledger_row_count=1,
                    decision_counts={"keep-candidate": 1},
                    total_remaining_samples=0,
                    checks_needing_samples=[],
                    upgrade_eligible_checks=["demo.py"],
                    upgrade_review_needed_checks=["demo.py"],
                    rows=[row],
                    errors=[],
                ),
            ):
                report = check_burn_in_upgrade_decisions.build_report(decisions)

        self.assertIn("line 1: accepted_samples is stale: expected 2, got 1", report.errors)

    def test_rejects_raw_runtime_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            decisions = Path(tmp) / "decisions.jsonl"
            write_jsonl(decisions, [valid_record(evidence_refs=[".codex/runtime/sessions/raw.jsonl"])])

            report = check_burn_in_upgrade_decisions.build_report(decisions)

        self.assertTrue(any("must not reference local runtime material" in error for error in report.errors))

    def test_requires_existing_repo_relative_evidence_refs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            decisions = Path(tmp) / "decisions.jsonl"
            write_jsonl(decisions, [valid_record(evidence_refs=["missing-decision-evidence.md"])])

            report = check_burn_in_upgrade_decisions.build_report(decisions)

        self.assertIn("line 1: evidence_refs item does not exist: missing-decision-evidence.md", report.errors)

    def test_allows_existing_evidence_refs_with_selectors(self) -> None:
        row = check_burn_in_ledger.BurnInLedgerRow(
            check="demo.py",
            accepted_samples=2,
            sample_target=2,
            remaining_samples=0,
            evidence_refs=["docs/ai/check-burn-in-ledger.md#candidate-ledger"],
            false_positives="0",
            repair_path="fix",
            cost="low",
            current_decision="keep-candidate",
            next_evidence="upgrade decision review",
            upgrade_eligible=True,
            upgrade_review_needed=True,
        )
        with tempfile.TemporaryDirectory() as tmp:
            decisions = Path(tmp) / "decisions.jsonl"
            write_jsonl(
                decisions,
                [
                    valid_record(
                        evidence_refs=[
                            "docs/ai/check-burn-in-ledger.md#candidate-ledger",
                            "tests/test_burn_in_upgrade_decisions.py::BurnInUpgradeDecisionsTest",
                            "docs/ai/standards/check-burn-in-upgrade-decisions.jsonl:1",
                        ]
                    )
                ],
            )
            with mock.patch.object(
                check_burn_in_upgrade_decisions.check_burn_in_ledger,
                "validate",
                return_value=check_burn_in_ledger.LedgerResult(
                    registry_path="registry.md",
                    ledger_path="ledger.md",
                    blocking_candidate_count=1,
                    ledger_row_count=1,
                    decision_counts={"keep-candidate": 1},
                    total_remaining_samples=0,
                    checks_needing_samples=[],
                    upgrade_eligible_checks=["demo.py"],
                    upgrade_review_needed_checks=["demo.py"],
                    rows=[row],
                    errors=[],
                ),
            ):
                report = check_burn_in_upgrade_decisions.build_report(decisions)

        self.assertEqual([], report.errors)

    def test_rejects_absolute_or_escaping_evidence_refs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            decisions = Path(tmp) / "decisions.jsonl"
            write_jsonl(decisions, [valid_record(evidence_refs=["/tmp/evidence.md", "../outside.md"])])

            report = check_burn_in_upgrade_decisions.build_report(decisions)

        text = "\n".join(report.errors)
        self.assertIn("line 1: evidence_refs items must be repo-relative paths: /tmp/evidence.md", text)
        self.assertIn("line 1: evidence_refs item escapes repository scope: ../outside.md", text)

    def test_cli_json_output_is_stable(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_burn_in_upgrade_decisions.py"), "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn('"upgrade_review_needed_checks"', result.stdout)
        self.assertIn('"decision_counts"', result.stdout)
        self.assertIn('"next_evidence_needed_by_check"', result.stdout)
        self.assertIn('"errors": []', result.stdout)


if __name__ == "__main__":
    unittest.main()
