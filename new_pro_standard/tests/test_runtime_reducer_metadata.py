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

                self.assertIn("Requirement IDs：未绑定", markdown)
                self.assertIn("Workstream IDs：未绑定", markdown)
                self.assertIn("## Next Best Work Review", markdown)
                self.assertIn("Decision：continue | re-scope | split | pivot | park | cancel | ask-user", markdown)
            finally:
                stop_runtime_observation.OBSERVATION_DIR = original_dir
                stop_runtime_observation.git_status_paths = original_git_status_paths

    def test_reducer_redacts_sensitive_prompt_previews_from_existing_observations(self) -> None:
        with tempfile.TemporaryDirectory() as tempdir:
            observation_file = Path(tempdir) / "observations.jsonl"
            observation_file.write_text(
                (
                    '{"session_id":"session-sensitive-reducer",'
                    '"needs_governance_promotion":true,'
                    '"prompt_preview":"api_key=plain-api-key sk-abcdefghijklmnopqrstuvwxyz123456 user@example.com",'
                    '"changed_paths":["docs/ai/working-context.md"]}\n'
                ),
                encoding="utf-8",
            )

            entries = reduce_runtime_observations.load_observations(observation_file)
            selected = reduce_runtime_observations.select_entries(entries, limit=20)
            markdown = reduce_runtime_observations.render_handoff_draft(
                observation_file=observation_file,
                entries=entries,
                selected=selected,
                stage="stage-00",
                task="runtime-redaction-test",
                title="Runtime Redaction Draft",
                requirement_ids=[],
                workstream_ids=[],
            )

            self.assertIn("[REDACTED_SECRET]", markdown)
            self.assertIn("[REDACTED_OPENAI_KEY]", markdown)
            self.assertIn("[REDACTED_EMAIL]", markdown)
            self.assertNotIn("plain-api-key", markdown)
            self.assertNotIn("sk-abcdefghijklmnopqrstuvwxyz123456", markdown)
            self.assertNotIn("user@example.com", markdown)


if __name__ == "__main__":
    unittest.main()
