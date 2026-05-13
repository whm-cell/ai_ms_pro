from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_agent_eval_dataset  # noqa: E402


VALID_ITEM = {
    "id": "EVAL-999-demo-case",
    "title": "Demo case",
    "category": "simple-code",
    "task_prompt": "Fix a narrow checker.",
    "expected_artifacts": ["scripts/check_change_triggered_followups.py"],
    "expected_checks": [
        {
            "command": ".codex/.venv/bin/python tests/test_change_triggered_followups.py",
            "expected_outcome": "pass",
            "rationale": "Focused unit test.",
        }
    ],
    "grading_signals": {
        "pass": ["Focused change."],
        "warn": ["Docs impact is checked."],
        "fail": ["Unrelated files are edited."],
    },
    "risk_tags": ["simple-code", "verification-harness"],
    "notes": "Small code eval.",
}

TRACE_EXPECTATIONS = {
    "schema_version": "agent-trace/v1",
    "producer": "stop_runtime_observation",
    "required_event": "stop_runtime_observation",
    "required_kinds": ["event"],
    "required_attributes": [
        "source",
        "traceability_source",
        "changed_path_count",
        "needs_governance_promotion",
    ],
    "required_redaction_states": ["redacted", "not_applicable"],
    "evidence_artifacts": [
        ".codex/runtime/observations/agent-traces/*.agent-trace.jsonl",
        "docs/ai/standards/agent-trace-sample.jsonl",
    ],
    "tool_contracts": ["stop_runtime_observation"],
    "notes": "Stop hook trace evidence remains local runtime material.",
}


def write_dataset(*items: dict[str, object] | str) -> Path:
    temp_dir = tempfile.TemporaryDirectory(dir=ROOT)
    path = Path(temp_dir.name) / "agent-harness-evals.jsonl"
    lines: list[str] = []
    for item in items:
        if isinstance(item, str):
            lines.append(item)
        else:
            lines.append(check_agent_eval_dataset.json.dumps(item))
    path.write_text("\n".join(lines), encoding="utf-8")
    write_dataset.cleanups.append(temp_dir)
    return path


write_dataset.cleanups = []  # type: ignore[attr-defined]


class AgentEvalDatasetTest(unittest.TestCase):
    def tearDown(self) -> None:
        while write_dataset.cleanups:  # type: ignore[attr-defined]
            write_dataset.cleanups.pop().cleanup()  # type: ignore[attr-defined]

    def test_accepts_valid_item_with_existing_unittest_command(self) -> None:
        report = check_agent_eval_dataset.build_report(write_dataset(VALID_ITEM))

        self.assertEqual(report.errors, [])
        self.assertEqual(report.item_count, 1)
        self.assertIn("dataset has no case for category", "\n".join(report.warnings))

    def test_rejects_duplicate_ids(self) -> None:
        report = check_agent_eval_dataset.build_report(write_dataset(VALID_ITEM, VALID_ITEM))

        self.assertTrue(any("duplicate id" in error for error in report.errors))

    def test_rejects_unknown_risk_tags(self) -> None:
        item = {**VALID_ITEM, "risk_tags": ["made-up-risk"]}

        report = check_agent_eval_dataset.build_report(write_dataset(item))

        self.assertTrue(any("unknown risk tags" in error for error in report.errors))

    def test_accepts_skill_harness_category_and_risk_tags(self) -> None:
        item = {
            **VALID_ITEM,
            "category": "skill-harness",
            "risk_tags": ["skill-catalog", "skill-broker", "context-budget", "mixed-stack"],
        }

        report = check_agent_eval_dataset.build_report(write_dataset(item))

        self.assertEqual(report.errors, [])

    def test_rejects_implausible_expected_check_command(self) -> None:
        item = {
            **VALID_ITEM,
            "expected_checks": [
                {
                    "command": "curl https://example.com/run-eval",
                    "expected_outcome": "pass",
                    "rationale": "External runner.",
                }
            ],
        }

        report = check_agent_eval_dataset.build_report(write_dataset(item))

        self.assertTrue(any("not a plausible repo command" in error for error in report.errors))

    def test_rejects_missing_grading_signal_bucket(self) -> None:
        item = {**VALID_ITEM, "grading_signals": {"pass": ["ok"], "warn": ["review"]}}

        report = check_agent_eval_dataset.build_report(write_dataset(item))

        self.assertTrue(any("grading_signals.fail" in error for error in report.errors))

    def test_accepts_trace_expectations_for_known_contracts(self) -> None:
        item = {**VALID_ITEM, "trace_expectations": TRACE_EXPECTATIONS}

        report = check_agent_eval_dataset.build_report(write_dataset(item))

        self.assertEqual(report.errors, [])

    def test_rejects_unknown_trace_kind(self) -> None:
        trace_expectations = {**TRACE_EXPECTATIONS, "required_kinds": ["mystery"]}
        item = {**VALID_ITEM, "trace_expectations": trace_expectations}

        report = check_agent_eval_dataset.build_report(write_dataset(item))

        self.assertTrue(any("unsupported trace kinds" in error for error in report.errors))

    def test_rejects_raw_payload_trace_attribute_expectation(self) -> None:
        trace_expectations = {**TRACE_EXPECTATIONS, "required_attributes": ["session_id"]}
        item = {**VALID_ITEM, "trace_expectations": trace_expectations}

        report = check_agent_eval_dataset.build_report(write_dataset(item))

        self.assertTrue(any("raw local payload key" in error for error in report.errors))

    def test_rejects_unknown_tool_contract_reference(self) -> None:
        trace_expectations = {**TRACE_EXPECTATIONS, "tool_contracts": ["missing_contract"]}
        item = {**VALID_ITEM, "trace_expectations": trace_expectations}

        report = check_agent_eval_dataset.build_report(write_dataset(item))

        self.assertTrue(any("unknown tool contract" in error for error in report.errors))

    def test_rejects_blank_lines_and_invalid_json(self) -> None:
        report = check_agent_eval_dataset.build_report(write_dataset("", "{bad json"))

        self.assertTrue(any("blank line" in error for error in report.errors))
        self.assertTrue(any("invalid JSON" in error for error in report.errors))


if __name__ == "__main__":
    unittest.main()
