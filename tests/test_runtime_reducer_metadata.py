from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".codex" / "hooks"))
sys.path.insert(0, str(ROOT / "scripts"))

import reduce_runtime_observations  # noqa: E402
import runtime_traceability  # noqa: E402
import stop_runtime_observation  # noqa: E402


class RuntimeReducerMetadataTest(unittest.TestCase):
    def setUp(self) -> None:
        runtime_traceability.load_traceability_catalog.cache_clear()

    def test_reducer_preserves_auto_discovered_requirement_and_workstream_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            observation_dir = Path(tempdir) / "observations"
            original_dir = stop_runtime_observation.OBSERVATION_DIR
            original_git_status_paths = stop_runtime_observation.git_status_paths
            try:
                stop_runtime_observation.OBSERVATION_DIR = observation_dir
                stop_runtime_observation.git_status_paths = lambda: ["apps/harness-trace-console/main.js"]

                stop_runtime_observation.append_observation({"session_id": "session-auto-reducer"})

                observation_file = next(observation_dir.glob("*.jsonl"))
                entries = reduce_runtime_observations.load_observations(observation_file)
                selected = reduce_runtime_observations.select_entries(entries, limit=20)
                markdown = reduce_runtime_observations.render_handoff_draft(
                    observation_file=observation_file,
                    entries=entries,
                    selected=selected,
                    stage="stage-00",
                    task="runtime-auto-discovery-test",
                    title="Runtime Auto Discovery Draft",
                    requirement_ids=[],
                    workstream_ids=[],
                )

                self.assertIn("Requirement IDs：REQ-004, REQ-005, REQ-006", markdown)
                self.assertIn("Workstream IDs：WS-02", markdown)
            finally:
                stop_runtime_observation.OBSERVATION_DIR = original_dir
                stop_runtime_observation.git_status_paths = original_git_status_paths


if __name__ == "__main__":
    unittest.main()
