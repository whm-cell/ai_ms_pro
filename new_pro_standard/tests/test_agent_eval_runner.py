from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_agent_eval_dataset  # noqa: E402


def eval_item(expected_outcome: str = "pass") -> dict[str, object]:
    return {
        "id": "EVAL-999-runner-demo",
        "title": "Runner demo",
        "category": "simple-code",
        "expected_checks": [
            {
                "command": "python3 tests/test_agent_eval_dataset.py",
                "expected_outcome": expected_outcome,
                "rationale": "Run focused dataset validator tests.",
            }
        ],
        "grading_signals": {"pass": ["ok"], "warn": ["review"], "fail": ["broken"]},
        "risk_tags": ["verification-harness"],
    }


def trace_eval_item() -> dict[str, object]:
    item = eval_item()
    item["trace_expectations"] = {
        "schema_version": "agent-trace/v1",
        "producer": "stop_runtime_observation",
        "required_event": "stop_runtime_observation",
        "required_kinds": ["event"],
        "required_attributes": ["source", "traceability_source", "changed_path_count"],
        "required_redaction_states": ["redacted", "not_applicable"],
        "evidence_artifacts": ["docs/ai/standards/agent-trace-sample.jsonl"],
        "tool_contracts": ["stop_runtime_observation"],
        "notes": "Use the sample trace as local evidence.",
    }
    return item


class AgentEvalRunnerTest(unittest.TestCase):
    def test_dry_run_marks_checks_not_run(self) -> None:
        with mock.patch("run_agent_eval_dataset.subprocess.run") as mocked_run:
            result = run_agent_eval_dataset.run_eval(eval_item(), dry_run=True, timeout=10)

        mocked_run.assert_not_called()
        self.assertEqual(result.grade, "not-run")
        self.assertEqual(result.checks[0].returncode, None)
        self.assertEqual(result.checks[0].grade, "not-run")

    def test_dry_run_reports_trace_expectations_without_reading_artifacts(self) -> None:
        with mock.patch("run_agent_eval_dataset.subprocess.run") as mocked_run:
            result = run_agent_eval_dataset.run_eval(trace_eval_item(), dry_run=True, timeout=10)

        mocked_run.assert_not_called()
        self.assertEqual(result.grade, "not-run")
        self.assertIsNotNone(result.trace_evidence)
        self.assertEqual(result.trace_evidence.grade, "not-run")
        self.assertEqual(result.trace_evidence.trace_artifacts, ["docs/ai/standards/agent-trace-sample.jsonl"])

    def test_successful_pass_check_grades_pass(self) -> None:
        completed = run_agent_eval_dataset.subprocess.CompletedProcess(args=[], returncode=0, stdout="ok", stderr="")

        with mock.patch("run_agent_eval_dataset.subprocess.run", return_value=completed):
            result = run_agent_eval_dataset.run_eval(eval_item(), dry_run=False, timeout=10)

        self.assertEqual(result.grade, "pass")
        self.assertEqual(result.checks[0].stdout_tail, "ok")

    def test_review_expected_check_grades_review_required(self) -> None:
        completed = run_agent_eval_dataset.subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")

        with mock.patch("run_agent_eval_dataset.subprocess.run", return_value=completed):
            result = run_agent_eval_dataset.run_eval(eval_item("review-required"), dry_run=False, timeout=10)

        self.assertEqual(result.grade, "review-required")

    def test_nonzero_returncode_fails(self) -> None:
        completed = run_agent_eval_dataset.subprocess.CompletedProcess(args=[], returncode=2, stdout="", stderr="bad")

        with mock.patch("run_agent_eval_dataset.subprocess.run", return_value=completed):
            result = run_agent_eval_dataset.run_eval(eval_item(), dry_run=False, timeout=10)

        self.assertEqual(result.grade, "fail")
        self.assertEqual(result.checks[0].stderr_tail, "bad")

    def test_execute_binds_matching_trace_evidence_to_eval_result(self) -> None:
        completed = run_agent_eval_dataset.subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr="")

        with mock.patch("run_agent_eval_dataset.subprocess.run", return_value=completed):
            result = run_agent_eval_dataset.run_eval(trace_eval_item(), dry_run=False, timeout=10)

        self.assertEqual(result.grade, "pass")
        self.assertIsNotNone(result.trace_evidence)
        self.assertEqual(result.trace_evidence.grade, "pass")
        self.assertEqual(result.trace_evidence.matched_records, 1)
        self.assertEqual(result.trace_evidence.trace_ids, ["trace-stop-observation-sample"])
        self.assertEqual(result.trace_evidence.redaction_states, ["redacted"])


if __name__ == "__main__":
    unittest.main()
