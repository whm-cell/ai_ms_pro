from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_burn_in_ledger  # noqa: E402


REGISTRY = """# Check Registry

| Check | Level | CI coverage | 升级条件 |
| --- | --- | --- | --- |
| `demo.py` | `blocking-candidate` | manual | needs evidence |
| `done.py` | `blocking` | ci | done |
"""


LEDGER = """# Check Burn-in Ledger

| Check | Accepted samples | Evidence refs | False positives | Repair path | Cost | Current decision | Next evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `demo.py` | 0/2 | - | 0 accepted | fix demo | low | keep-candidate | two samples |
"""


def write(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


class CheckBurnInLedgerTest(unittest.TestCase):
    def test_repository_ledger_matches_blocking_candidates(self) -> None:
        result = check_burn_in_ledger.validate()

        self.assertEqual(result.errors, [])
        self.assertGreater(result.blocking_candidate_count, 0)
        self.assertEqual(result.blocking_candidate_count, result.ledger_row_count)
        self.assertEqual(result.ledger_row_count, len(result.rows))
        self.assertEqual({"keep-candidate": result.ledger_row_count}, result.decision_counts)
        self.assertEqual(sum(row.remaining_samples for row in result.rows), result.total_remaining_samples)
        self.assertEqual(["check_code_shape.py", "check_tool_contracts.py"], result.upgrade_eligible_checks)
        self.assertEqual(["check_code_shape.py", "check_tool_contracts.py"], result.upgrade_review_needed_checks)
        self.assertNotIn("check_code_shape.py", result.checks_needing_samples)
        self.assertNotIn("check_tool_contracts.py", result.checks_needing_samples)
        code_shape_row = next(row for row in result.rows if row.check == "check_code_shape.py")
        self.assertEqual(2, code_shape_row.accepted_samples)
        self.assertEqual(0, code_shape_row.remaining_samples)
        self.assertTrue(code_shape_row.upgrade_review_needed)
        self.assertIn("scripts/check_burn_in_ledger.py", code_shape_row.evidence_refs)
        self.assertIn("scripts/change_triggered_followup_rules.py", code_shape_row.evidence_refs)
        self.assertIn("docs/ai/changelog/2026-05-25-code-shape-followup-rule-sample.md", code_shape_row.evidence_refs)
        tool_contract_row = next(row for row in result.rows if row.check == "check_tool_contracts.py")
        self.assertEqual(2, tool_contract_row.accepted_samples)
        self.assertEqual(0, tool_contract_row.remaining_samples)
        self.assertTrue(tool_contract_row.upgrade_review_needed)
        self.assertIn("docs/ai/tool-contracts/contracts.json", tool_contract_row.evidence_refs)
        self.assertIn("docs/ai/changelog/2026-05-25-burn-in-ledger-evidence-refs.md", tool_contract_row.evidence_refs)

    def test_validates_required_row_for_each_blocking_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = root / "registry.md"
            ledger = root / "ledger.md"
            write(registry, REGISTRY)
            write(ledger, LEDGER)

            result = check_burn_in_ledger.validate(registry, ledger)

        self.assertEqual(result.errors, [])
        self.assertEqual(1, len(result.rows))
        row = result.rows[0]
        self.assertEqual("demo.py", row.check)
        self.assertEqual(0, row.accepted_samples)
        self.assertEqual(2, row.sample_target)
        self.assertEqual(2, row.remaining_samples)
        self.assertEqual([], row.evidence_refs)
        self.assertEqual("keep-candidate", row.current_decision)
        self.assertEqual("two samples", row.next_evidence)
        self.assertFalse(row.upgrade_eligible)
        self.assertFalse(row.upgrade_review_needed)

    def test_reports_missing_candidate_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = root / "registry.md"
            ledger = root / "ledger.md"
            write(registry, REGISTRY.replace("done.py` | `blocking`", "done.py` | `blocking-candidate`"))
            write(ledger, LEDGER)

            result = check_burn_in_ledger.validate(registry, ledger)

        self.assertIn("missing ledger row for blocking-candidate check: done.py", result.errors)

    def test_reports_bad_sample_format_and_decision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = root / "registry.md"
            ledger = root / "ledger.md"
            write(registry, REGISTRY)
            write(ledger, LEDGER.replace("0/2", "zero").replace("keep-candidate", "maybe"))

            result = check_burn_in_ledger.validate(registry, ledger)

        text = "\n".join(result.errors)
        self.assertIn("Accepted samples must use N/2 format", text)
        self.assertIn("Current decision must be one of", text)

    def test_requires_evidence_refs_for_accepted_samples(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = root / "registry.md"
            ledger = root / "ledger.md"
            write(registry, REGISTRY)
            write(ledger, LEDGER.replace("0/2", "1/2"))

            result = check_burn_in_ledger.validate(registry, ledger)

        self.assertIn("demo.py: accepted samples require Evidence refs", result.errors)

    def test_requires_existing_repo_relative_evidence_refs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = root / "registry.md"
            ledger = root / "ledger.md"
            write(registry, REGISTRY)
            write(ledger, LEDGER.replace("0/2 | -", "1/2 | missing.md"))

            result = check_burn_in_ledger.validate(registry, ledger)

        self.assertIn("demo.py: Evidence refs item does not exist: missing.md", result.errors)

    def test_allows_existing_evidence_refs_with_selectors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = root / "registry.md"
            ledger = root / "ledger.md"
            write(root / "evidence.md", "accepted sample evidence\n")
            write(root / "evidence.jsonl", '{"id":"sample"}\n')
            write(registry, REGISTRY)
            write(
                ledger,
                LEDGER.replace("0/2 | -", "1/2 | evidence.md#sample, evidence.jsonl:1"),
            )

            result = check_burn_in_ledger.validate(registry, ledger)

        self.assertEqual([], result.errors)
        self.assertEqual(["evidence.md#sample", "evidence.jsonl:1"], result.rows[0].evidence_refs)

    def test_rejects_absolute_or_escaping_evidence_refs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = root / "registry.md"
            ledger = root / "ledger.md"
            write(registry, REGISTRY)
            write(ledger, LEDGER.replace("0/2 | -", "1/2 | /tmp/evidence.md, ../outside.md"))

            result = check_burn_in_ledger.validate(registry, ledger)

        text = "\n".join(result.errors)
        self.assertIn("demo.py: Evidence refs items must be repo-relative paths: /tmp/evidence.md", text)
        self.assertIn("demo.py: Evidence refs item escapes repository scope: ../outside.md", text)

    def test_rejects_upgrade_decision_before_two_accepted_samples(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = root / "registry.md"
            ledger = root / "ledger.md"
            write(registry, REGISTRY)
            write(ledger, LEDGER.replace("keep-candidate", "ready-for-adr"))

            result = check_burn_in_ledger.validate(registry, ledger)

        self.assertIn("demo.py: ready-for-adr requires Accepted samples to be 2/2, got 0/2", result.errors)

    def test_rejects_sample_count_above_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = root / "registry.md"
            ledger = root / "ledger.md"
            write(registry, REGISTRY)
            write(ledger, LEDGER.replace("0/2", "3/2"))

            result = check_burn_in_ledger.validate(registry, ledger)

        self.assertIn("demo.py: Accepted samples cannot exceed target: 3/2", result.errors)

    def test_routes_two_of_two_keep_candidate_to_upgrade_decision_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = root / "registry.md"
            ledger = root / "ledger.md"
            write(root / "evidence.md", "accepted sample evidence\n")
            write(registry, REGISTRY)
            write(ledger, LEDGER.replace("0/2 | -", "2/2 | evidence.md"))

            result = check_burn_in_ledger.validate(registry, ledger)

        self.assertIn(
            "demo.py: 2/2 keep-candidate rows must route Next evidence to upgrade decision review",
            result.errors,
        )

    def test_allows_ready_for_adr_at_two_of_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = root / "registry.md"
            ledger = root / "ledger.md"
            write(root / "evidence.md", "accepted sample evidence\n")
            write(registry, REGISTRY)
            write(
                ledger,
                LEDGER.replace("0/2", "2/2")
                .replace(" - | 0 accepted", " evidence.md | 0 accepted")
                .replace("keep-candidate", "ready-for-adr"),
            )

            result = check_burn_in_ledger.validate(registry, ledger)

        self.assertEqual([], result.errors)
        self.assertEqual(["demo.py"], result.upgrade_eligible_checks)
        self.assertEqual(0, result.total_remaining_samples)
        self.assertTrue(result.rows[0].upgrade_eligible)
        self.assertFalse(result.rows[0].upgrade_review_needed)
        self.assertEqual(["evidence.md"], result.rows[0].evidence_refs)

    def test_cli_json_output_is_stable(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_burn_in_ledger.py"), "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=True,
        )

        self.assertIn('"blocking_candidate_count"', result.stdout)
        self.assertIn('"decision_counts"', result.stdout)
        self.assertIn('"total_remaining_samples"', result.stdout)
        self.assertIn('"checks_needing_samples"', result.stdout)
        self.assertIn('"upgrade_eligible_checks"', result.stdout)
        self.assertIn('"upgrade_review_needed_checks"', result.stdout)
        self.assertIn('"rows"', result.stdout)
        self.assertIn('"evidence_refs"', result.stdout)
        self.assertIn('"upgrade_review_needed"', result.stdout)
        self.assertIn('"next_evidence"', result.stdout)
        self.assertIn('"errors": []', result.stdout)


if __name__ == "__main__":
    unittest.main()
