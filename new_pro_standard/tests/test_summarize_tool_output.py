from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import summarize_tool_output  # noqa: E402


def write(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


class SummarizeToolOutputTest(unittest.TestCase):
    def test_large_file_outputs_summary_not_full_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "large.log"
            lines = [f"ordinary line {index}" for index in range(1, 121)]
            lines[1] = "Error: first failure"
            lines[49] = "SECRET_MIDDLE_PAYLOAD_SHOULD_NOT_APPEAR"
            write(path, lines)
            raw_size = path.stat().st_size

            summary = summarize_tool_output.build_summary(path, tail_lines=5)
            rendered = summarize_tool_output.render_markdown(summary)

        self.assertIn("Tool Output Summary", rendered)
        self.assertIn("L2: Error: first failure", rendered)
        self.assertIn("L120: ordinary line 120", rendered)
        self.assertNotIn("SECRET_MIDDLE_PAYLOAD_SHOULD_NOT_APPEAR", rendered)
        self.assertLess(len(rendered), raw_size)

    def test_error_matches_include_line_numbers_and_truncation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "failures.log"
            write(path, [f"FAILED case {index}" for index in range(1, 6)])

            summary = summarize_tool_output.build_summary(path, max_matches=2, tail_lines=0)
            rendered = summarize_tool_output.render_markdown(summary)

        self.assertEqual(summary.match_count, 5)
        self.assertTrue(summary.matches_truncated)
        self.assertIn("L1: FAILED case 1", rendered)
        self.assertIn("L2: FAILED case 2", rendered)
        self.assertNotIn("L3: FAILED case 3", rendered.split("## Tail", 1)[0])
        self.assertIn("truncated: yes", rendered)

    def test_around_line_outputs_requested_window(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "window.log"
            write(path, [f"line {index}" for index in range(1, 11)])

            summary = summarize_tool_output.build_summary(path, around=[5], context=2, tail_lines=0)
            rendered = summarize_tool_output.render_markdown(summary)

        self.assertIn("Window Around Line 5", rendered)
        self.assertIn("actual range: 3-7", rendered)
        self.assertIn("L3: line 3", rendered)
        self.assertIn("L7: line 7", rendered)

    def test_around_line_clamps_out_of_range_window(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "window.log"
            write(path, [f"line {index}" for index in range(1, 11)])

            summary = summarize_tool_output.build_summary(path, around=[99], context=2, tail_lines=0)
            rendered = summarize_tool_output.render_markdown(summary)

        self.assertIn("Window Around Line 99", rendered)
        self.assertIn("actual range: 8-10", rendered)
        self.assertIn("L8: line 8", rendered)
        self.assertIn("L10: line 10", rendered)

    def test_long_single_line_is_truncated_in_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "base64.log"
            long_payload = "Error: " + ("A" * 5000)
            write(path, [long_payload])

            summary = summarize_tool_output.build_summary(path, max_line_chars=40, tail_lines=1)
            rendered = summarize_tool_output.render_markdown(summary)

        self.assertIn("truncated; original chars=5007", rendered)
        self.assertIn("L1: Error: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", rendered)
        self.assertNotIn("A" * 200, rendered)
        self.assertTrue(summary.matches[0].truncated)
        self.assertEqual(summary.matches[0].original_chars, 5007)

    def test_max_line_chars_controls_match_text_length(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "short-limit.log"
            write(path, ["FAILED " + ("x" * 100)])

            summary = summarize_tool_output.build_summary(path, max_line_chars=12, tail_lines=0)

        self.assertEqual(summary.matches[0].text, "FAILED xxxxx")
        self.assertTrue(summary.matches[0].truncated)

    def test_json_output_has_stable_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "json.log"
            write(path, ["ok", "Traceback: boom", "tail"])
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "summarize_tool_output.py"),
                    "--input",
                    str(path),
                    "--json",
                    "--tail-lines",
                    "1",
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
                "bytes",
                "estimated_tokens",
                "line_count",
                "match_count",
                "matches",
                "matches_truncated",
                "output_truncated",
                "path",
                "pattern",
                "tail",
                "windows",
                "windows_omitted",
            ],
        )
        self.assertEqual(payload["matches"][0]["line"], 2)
        self.assertEqual(payload["matches"][0]["original_chars"], 15)
        self.assertFalse(payload["matches"][0]["truncated"])
        self.assertEqual(payload["tail"]["lines"][0]["line"], 3)
        self.assertEqual(payload["tail"]["lines"][0]["original_chars"], 4)
        self.assertFalse(payload["tail"]["lines"][0]["truncated"])
        self.assertFalse(payload["output_truncated"])
        self.assertEqual(payload["windows_omitted"], 0)

    def test_markdown_respects_max_output_chars_and_window_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "many-windows.log"
            write(path, [f"line {index} " + ("x" * 80) for index in range(1, 80)])

            summary = summarize_tool_output.build_summary(
                path,
                around=[5, 15, 25, 35, 45],
                context=2,
                tail_lines=10,
            )
            rendered = summarize_tool_output.render_markdown(
                summary,
                max_output_chars=900,
                max_windows=2,
            )

        self.assertLessEqual(len(rendered), 900)
        self.assertIn("windows: 2 / 5 (omitted: 3)", rendered)
        self.assertIn("Tool output summary truncated", rendered)

    def test_json_respects_max_output_chars_and_reports_omitted_windows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "large-json.log"
            write(path, ["FAILED " + ("x" * 200) for _ in range(50)])

            summary = summarize_tool_output.build_summary(
                path,
                around=[2, 4, 6, 8],
                context=1,
                tail_lines=20,
            )
            rendered = summarize_tool_output.render_json(
                summary,
                max_output_chars=1100,
                max_windows=1,
            )

        payload = json.loads(rendered)
        self.assertLessEqual(len(rendered), 1100)
        self.assertTrue(payload["output_truncated"])
        self.assertGreaterEqual(payload["windows_omitted"], 3)


if __name__ == "__main__":
    unittest.main()
