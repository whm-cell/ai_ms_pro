from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_code_shape  # noqa: E402


class CodeShapeInitialCommitTest(unittest.TestCase):
    def setUp(self) -> None:
        self.config = check_code_shape.Config(
            include=("scripts/*.py",),
            exclude=(),
            python_file=check_code_shape.Limit(warn=350, error=500),
            python_function=check_code_shape.Limit(warn=80, error=120),
            python_class=check_code_shape.Limit(warn=250, error=350),
            shell_file=check_code_shape.Limit(warn=120, error=200),
        )

    def test_added_file_is_treated_as_existing_on_initial_commit(self) -> None:
        diff_result = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=b"A\tscripts/example.py\n",
            stderr=b"",
        )
        show_result = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=b"print('hello')\n",
            stderr=b"",
        )

        with mock.patch.object(check_code_shape, "repo_has_commits", return_value=False):
            with mock.patch.object(check_code_shape, "run_git", side_effect=[diff_result, show_result]):
                candidates = check_code_shape.load_staged_candidates(self.config)

        self.assertEqual(len(candidates), 1)
        self.assertFalse(candidates[0].is_new)

    def test_added_file_stays_new_after_first_commit(self) -> None:
        diff_result = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=b"A\tscripts/example.py\n",
            stderr=b"",
        )
        show_result = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout=b"print('hello')\n",
            stderr=b"",
        )

        with mock.patch.object(check_code_shape, "repo_has_commits", return_value=True):
            with mock.patch.object(check_code_shape, "run_git", side_effect=[diff_result, show_result]):
                candidates = check_code_shape.load_staged_candidates(self.config)

        self.assertEqual(len(candidates), 1)
        self.assertTrue(candidates[0].is_new)


if __name__ == "__main__":
    unittest.main()
