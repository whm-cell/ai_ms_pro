from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import summarize_runtime_traces  # noqa: E402


def write_jsonl(path: Path, records: list[dict[str, object] | str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [item if isinstance(item, str) else json.dumps(item) for item in records]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def observation(**overrides: object) -> dict[str, object]:
    record: dict[str, object] = {
        "timestamp": "2026-05-23T10:00:00+08:00",
        "event": "Stop",
        "source": "codex-stop-hook",
        "session_id": "SECRET_SESSION_SHOULD_NOT_APPEAR",
        "agent": "main",
        "cwd": "/secret/cwd/SHOULD_NOT_APPEAR",
        "prompt_preview": "SECRET_PROMPT_SHOULD_NOT_APPEAR",
        "changed_paths": ["docs/ai/index.md", "scripts/demo.py"],
        "changed_path_count": 2,
        "docs_changed": True,
        "runtime_only_changes": False,
        "requirement_ids": ["REQ-007"],
        "workstream_ids": ["WS-01"],
        "traceability_source": "changed-path:req",
        "needs_governance_promotion": True,
    }
    record.update(overrides)
    return record


def trace(**overrides: object) -> dict[str, object]:
    record: dict[str, object] = {
        "schema_version": "agent-trace/v1",
        "trace_id": "trace-demo",
        "span_id": "span-demo",
        "name": "codex stop runtime observation",
        "kind": "event",
        "event": "stop_runtime_observation",
        "start_time": "2026-05-23T02:00:00Z",
        "end_time": "2026-05-23T02:00:00Z",
        "status": {"code": "ok"},
        "agent": {"name": "codex-stop-hook", "role": "main"},
        "attributes": {
            "changed_path_count": 2,
            "docs_changed": True,
            "runtime_only_changes": False,
            "needs_governance_promotion": True,
            "changed_paths": ["docs/ai/index.md"],
        },
        "requirement_ids": ["REQ-007"],
        "workstream_ids": ["WS-01"],
        "redaction": {"state": "redacted", "rule": "runtime sanitizer applied"},
    }
    record.update(overrides)
    return record


class SummarizeRuntimeTracesTest(unittest.TestCase):
    def test_summary_counts_observations_traces_and_distributions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime_dir = Path(tmp)
            write_jsonl(runtime_dir / "2026-05-23.jsonl", [observation()])
            write_jsonl(runtime_dir / "agent-traces" / "2026-05-23.agent-trace.jsonl", [trace()])

            summary = summarize_runtime_traces.build_summary(runtime_dir, top=5)

        self.assertEqual(summary.observation_count, 1)
        self.assertEqual(summary.trace_record_count, 1)
        self.assertEqual(summary.session_count, 1)
        self.assertEqual(summary.trace_count, 1)
        self.assertEqual(summary.promotion_needed_count, 1)
        self.assertEqual(summary.requirement_ids[0].value, "REQ-007")
        self.assertEqual(summary.workstream_ids[0].value, "WS-01")
        self.assertEqual(summary.changed_paths[0].value, "docs/ai/index.md")

    def test_markdown_is_bounded_and_excludes_sensitive_runtime_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime_dir = Path(tmp)
            records = [observation(changed_paths=[f"file-{index}.py" for index in range(20)])]
            write_jsonl(runtime_dir / "2026-05-23.jsonl", records)

            summary = summarize_runtime_traces.build_summary(runtime_dir, top=3)
            rendered = summarize_runtime_traces.render_markdown(summary)

        self.assertIn("Runtime Trace Summary", rendered)
        self.assertIn("needs governance promotion: 1", rendered)
        self.assertIn("file-0.py", rendered)
        self.assertNotIn("file-4.py", rendered)
        self.assertNotIn("SECRET_SESSION_SHOULD_NOT_APPEAR", rendered)
        self.assertNotIn("SECRET_PROMPT_SHOULD_NOT_APPEAR", rendered)
        self.assertNotIn("/secret/cwd", rendered)

    def test_invalid_jsonl_is_counted_not_raised(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime_dir = Path(tmp)
            write_jsonl(runtime_dir / "2026-05-23.jsonl", [observation(), "{not-json"])

            summary = summarize_runtime_traces.build_summary(runtime_dir)

        self.assertEqual(summary.observation_count, 1)
        self.assertEqual(summary.invalid_jsonl_lines, 1)
        self.assertTrue(any("could not be parsed" in item for item in summary.warnings))

    def test_trace_only_input_still_contributes_governance_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime_dir = Path(tmp)
            write_jsonl(runtime_dir / "agent-traces" / "2026-05-23.agent-trace.jsonl", [trace()])

            summary = summarize_runtime_traces.build_summary(runtime_dir)

        self.assertEqual(summary.observation_count, 0)
        self.assertEqual(summary.trace_record_count, 1)
        self.assertEqual(summary.promotion_needed_count, 1)
        self.assertEqual(summary.changed_paths[0].value, "docs/ai/index.md")

    def test_missing_runtime_dir_returns_empty_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            summary = summarize_runtime_traces.build_summary(Path(tmp) / "missing")

        self.assertEqual(summary.observation_count, 0)
        self.assertEqual(summary.trace_record_count, 0)
        self.assertEqual(summary.warnings, [])

    def test_json_output_has_stable_top_level_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime_dir = Path(tmp)
            write_jsonl(runtime_dir / "2026-05-23.jsonl", [observation()])
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "summarize_runtime_traces.py"),
                    "--runtime-dir",
                    str(runtime_dir),
                    "--json",
                ],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                check=True,
            )

        payload = json.loads(result.stdout)
        self.assertEqual(
            sorted(payload),
            [
                "agent_roles",
                "changed_paths",
                "docs_changed_count",
                "invalid_jsonl_lines",
                "missing_traceability_count",
                "observation_count",
                "observation_events",
                "observation_files",
                "promotion_needed_count",
                "recent_observations",
                "redaction_states",
                "requirement_ids",
                "runtime_dir",
                "runtime_only_count",
                "session_count",
                "trace_count",
                "trace_events",
                "trace_files",
                "trace_record_count",
                "trace_statuses",
                "warnings",
                "workstream_ids",
            ],
        )
        self.assertNotIn("SECRET_SESSION_SHOULD_NOT_APPEAR", result.stdout)
        self.assertEqual(payload["recent_observations"][0]["changed_path_count"], 2)


if __name__ == "__main__":
    unittest.main()
