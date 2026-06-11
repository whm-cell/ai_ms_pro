from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_agent_trace_schema  # noqa: E402


def load_default_schema() -> dict:
    return check_agent_trace_schema.load_json(check_agent_trace_schema.DEFAULT_SCHEMA)


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value), encoding="utf-8")


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(item) for item in records) + "\n", encoding="utf-8")


def base_record(span_id: str, parent_span_id: str | None = None) -> dict:
    return {
        "schema_version": "agent-trace/v1",
        "trace_id": "trace-test-0001",
        "span_id": span_id,
        "parent_span_id": parent_span_id,
        "name": "test span",
        "kind": "check",
        "start_time": "2026-05-10T00:00:00Z",
        "end_time": "2026-05-10T00:00:01Z",
        "status": {"code": "ok"},
        "agent": {"name": "codex", "role": "test"},
        "redaction": {"state": "not_applicable", "rule": "test metadata only"},
    }


class AgentTraceSchemaTest(unittest.TestCase):
    def test_default_sample_validates(self) -> None:
        errors = check_agent_trace_schema.validate_trace(
            check_agent_trace_schema.DEFAULT_SCHEMA,
            check_agent_trace_schema.DEFAULT_SAMPLE,
        )

        self.assertEqual(errors, [])

    def test_default_sample_includes_stop_trace_event(self) -> None:
        records = check_agent_trace_schema.load_jsonl(check_agent_trace_schema.DEFAULT_SAMPLE)
        stop_records = [record for record in records if record.get("event") == "stop_runtime_observation"]

        self.assertEqual(len(stop_records), 1)
        stop_record = stop_records[0]
        self.assertEqual(stop_record["kind"], "event")
        self.assertEqual(stop_record["agent"]["name"], "codex-stop-hook")
        self.assertIn("traceability_source", stop_record["attributes"])
        self.assertIn("needs_governance_promotion", stop_record["attributes"])
        self.assertEqual(stop_record["redaction"]["state"], "redacted")

    def test_missing_required_field_fails_clearly(self) -> None:
        schema = load_default_schema()
        record = base_record("span-root")
        del record["trace_id"]

        errors = check_agent_trace_schema.validate_object(record, schema)

        self.assertIn("$.trace_id: missing required field", errors)

    def test_invalid_parent_link_fails(self) -> None:
        records = [
            base_record("span-root"),
            base_record("span-child", "span-missing"),
        ]

        errors = check_agent_trace_schema.validate_parent_links(records)

        self.assertEqual(errors, ["record 2: parent_span_id 'span-missing' does not exist"])

    def test_invalid_timestamp_fails(self) -> None:
        schema = load_default_schema()
        record = base_record("span-root")
        record["start_time"] = "not-a-date"

        errors = check_agent_trace_schema.validate_object(record, schema)

        self.assertIn("$.start_time: expected RFC3339 UTC timestamp ending with Z", errors)

    def test_non_utc_timestamp_fails(self) -> None:
        schema = load_default_schema()
        record = base_record("span-root")
        record["end_time"] = "2026-05-10T00:00:01+08:00"

        errors = check_agent_trace_schema.validate_object(record, schema)

        self.assertIn("$.end_time: expected RFC3339 UTC timestamp ending with Z", errors)

    def test_schema_shape_rejects_required_field_without_property(self) -> None:
        schema = copy.deepcopy(load_default_schema())
        schema["required"].append("missing_property")

        with self.assertRaises(check_agent_trace_schema.ValidationError):
            check_agent_trace_schema.validate_schema_shape(schema)

    def test_validate_trace_uses_supplied_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            schema_path = temp_path / "schema.json"
            sample_path = temp_path / "sample.jsonl"
            write_json(schema_path, load_default_schema())
            write_jsonl(sample_path, [base_record("span-root"), base_record("span-child", "span-root")])

            errors = check_agent_trace_schema.validate_trace(schema_path, sample_path)

        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
