#!/usr/bin/env python3

from __future__ import annotations

import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bootstrap a minimal Codex-first harness control plane for a new repository.",
    )
    parser.add_argument(
        "--project-name",
        default="New Project",
        help="Project name used in starter documents. Default: New Project.",
    )
    parser.add_argument(
        "--stage-label",
        default="STAGE-00",
        help="Initial stage label for starter docs. Default: STAGE-00.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing starter files if they already exist.",
    )
    parser.add_argument(
        "--skip-venv",
        action="store_true",
        help="Skip creating or refreshing the repo-local Python virtual environment.",
    )
    parser.add_argument(
        "--python",
        help="Explicit Python executable to use for creating the repo-local virtual environment.",
    )
    parser.add_argument(
        "--strict-python-deps",
        action="store_true",
        help="Fail bootstrap when Python dependency installation fails. Default behavior is best-effort.",
    )
    return parser.parse_args()
