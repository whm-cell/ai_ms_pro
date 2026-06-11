from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_harness_upgrade_decisions as decisions  # noqa: E402


VALID_RECORD = {
    "schema_version": "harness-upgrade-decision/v1",
    "id": "HUD-test-task-profile",
    "gap_id": "GAP-WORKFLOW-TASK-PROFILE-AUDIT",
    "decision": "keep-advisory",
    "decided_at": "2026-05-24",
    "readiness_at_decision": "ready-for-upgrade-discussion",
    "source_metric": "accepted real task-profile classes",
    "accepted_count": 3,
    "upgrade_discussion_target": 3,
    "false_positive_review": "0 accepted false positives.",
    "repair_path": "Update the explicit audit record or narrow the read surface.",
    "cost_review": "Low local runtime and bounded reviewer cost while advisory.",
    "reviewer_burden": "Do not force heavy audit artifacts for every simple task.",
    "rationale": "Keep advisory after the first profile-coverage threshold.",
    "decision_ref": "docs/ai/harness-open-items.md",
    "evidence_refs": ["docs/ai/standards/task-profile-audit-sample.jsonl"],
    "next_evidence_needed": [
        "more real tasks outside the initial profile set",
        "false-positive review for profile selection disputes",
    ],
    "no_raw_runtime": True,
}


def write_decisions(*records: dict[str, object] | str) -> Path:
    temp_dir = tempfile.TemporaryDirectory(dir=ROOT)
    path = Path(temp_dir.name) / "harness-upgrade-decisions.jsonl"
    lines = [record if isinstance(record, str) else json.dumps(record) for record in records]
    path.write_text("\n".join(lines), encoding="utf-8")
    write_decisions.cleanups.append(temp_dir)
    return path


write_decisions.cleanups = []  # type: ignore[attr-defined]


class HarnessUpgradeDecisionTest(unittest.TestCase):
    def tearDown(self) -> None:
        while write_decisions.cleanups:  # type: ignore[attr-defined]
            write_decisions.cleanups.pop().cleanup()  # type: ignore[attr-defined]

    def test_repository_decisions_cover_ready_gaps(self) -> None:
        report = decisions.build_report()

        self.assertEqual([], report.errors)
        self.assertEqual(
            [
                "GAP-AGENTIC-SANDBOX-HONESTY",
                "GAP-GUARDRAIL-SOURCE-BOUNDARY",
                "GAP-SEC-CONTROL-MATRIX-BURNIN",
                "GAP-WORKFLOW-SIMPLE-SKIP",
                "GAP-WORKFLOW-TASK-PROFILE-AUDIT",
            ],
            report.ready_gap_ids,
        )
        self.assertEqual(
            [
                "GAP-AGENTIC-SANDBOX-HONESTY",
                "GAP-GUARDRAIL-SOURCE-BOUNDARY",
                "GAP-SEC-CONTROL-MATRIX-BURNIN",
                "GAP-WORKFLOW-SIMPLE-SKIP",
                "GAP-WORKFLOW-TASK-PROFILE-AUDIT",
            ],
            report.decided_ready_gap_ids,
        )
        self.assertEqual({"keep-advisory": 5}, report.decision_counts)
        self.assertIn("GAP-WORKFLOW-TASK-PROFILE-AUDIT", report.next_evidence_needed_by_gap)
        self.assertIn(
            "more real tasks outside the initial simple/complex/0-1-stage profile set",
            report.next_evidence_needed_by_gap["GAP-WORKFLOW-TASK-PROFILE-AUDIT"],
        )
        self.assertIn(
            "native sandbox, hosted trace, MCP, A2A, or external-provider boundary evidence before promotion",
            report.next_evidence_needed_by_gap["GAP-AGENTIC-SANDBOX-HONESTY"],
        )

    def test_missing_decision_for_ready_gap_fails(self) -> None:
        report = decisions.build_report(write_decisions())

        self.assertIn("missing upgrade decision for ready gap: GAP-AGENTIC-SANDBOX-HONESTY", report.errors)
        self.assertIn("missing upgrade decision for ready gap: GAP-GUARDRAIL-SOURCE-BOUNDARY", report.errors)
        self.assertIn("missing upgrade decision for ready gap: GAP-SEC-CONTROL-MATRIX-BURNIN", report.errors)
        self.assertIn("missing upgrade decision for ready gap: GAP-WORKFLOW-TASK-PROFILE-AUDIT", report.errors)

    def test_stale_snapshot_fails(self) -> None:
        record = {**VALID_RECORD, "accepted_count": 2}

        report = decisions.build_report(write_decisions(record))

        self.assertTrue(any("accepted_count is stale" in error for error in report.errors))

    def test_decision_for_non_ready_gap_fails(self) -> None:
        record = {**VALID_RECORD, "id": "HUD-test-preflight", "gap_id": "GAP-GUARDRAIL-PREFLIGHT-WARNING"}

        report = decisions.build_report(write_decisions(record))

        text = "\n".join(report.errors)
        self.assertIn("gap is not currently ready for upgrade discussion", text)
        self.assertIn("upgrade decision exists for gap that is not currently ready", text)

    def test_rejects_raw_runtime_material(self) -> None:
        record = {**VALID_RECORD, "evidence_refs": [".codex/runtime/observations/raw.jsonl"]}

        report = decisions.build_report(write_decisions(record))

        self.assertTrue(any("must not reference local runtime material" in error for error in report.errors))

    def test_requires_existing_repo_relative_evidence_refs(self) -> None:
        record = {**VALID_RECORD, "evidence_refs": ["missing-upgrade-decision-evidence.md"]}

        report = decisions.build_report(write_decisions(record))

        self.assertIn(
            "line 1: evidence_refs item does not exist: missing-upgrade-decision-evidence.md",
            report.errors,
        )

    def test_allows_existing_evidence_refs_with_selectors(self) -> None:
        record = {
            **VALID_RECORD,
            "evidence_refs": [
                "docs/ai/standards/task-profile-audit-sample.jsonl:1",
                "tests/test_harness_upgrade_decisions.py::HarnessUpgradeDecisionTest",
                "docs/ai/agentic-harness-gap-roadmap.md#p2-task-profile-audit",
            ],
        }

        report = decisions.build_report(write_decisions(record))

        self.assertFalse(any("evidence_refs item does not exist" in error for error in report.errors))

    def test_rejects_absolute_or_escaping_evidence_refs(self) -> None:
        record = {**VALID_RECORD, "evidence_refs": ["/tmp/evidence.md", "../outside.md"]}

        report = decisions.build_report(write_decisions(record))

        text = "\n".join(report.errors)
        self.assertIn("line 1: evidence_refs items must be repo-relative paths: /tmp/evidence.md", text)
        self.assertIn("line 1: evidence_refs item escapes repository scope: ../outside.md", text)

    def test_requires_next_evidence_needed(self) -> None:
        record = {**VALID_RECORD}
        record.pop("next_evidence_needed")

        report = decisions.build_report(write_decisions(record))

        self.assertTrue(any("next_evidence_needed must be a non-empty list" in error for error in report.errors))

    def test_rejects_duplicate_gap_decisions(self) -> None:
        duplicate = {**VALID_RECORD, "id": "HUD-test-task-profile-second"}

        report = decisions.build_report(write_decisions(VALID_RECORD, duplicate))

        self.assertTrue(any("duplicate gap_id: GAP-WORKFLOW-TASK-PROFILE-AUDIT" in error for error in report.errors))

    def test_cli_json_output_is_stable(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_harness_upgrade_decisions.py"), "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        payload = json.loads(result.stdout)

        self.assertEqual([], payload["errors"])
        self.assertEqual(5, payload["ready_gap_count"])
        self.assertEqual({"keep-advisory": 5}, payload["decision_counts"])
        self.assertIn("next_evidence_needed_by_gap", payload)
        self.assertIn("GAP-SEC-CONTROL-MATRIX-BURNIN", payload["next_evidence_needed_by_gap"])


if __name__ == "__main__":
    unittest.main()
