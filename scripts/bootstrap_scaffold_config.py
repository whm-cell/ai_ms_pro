#!/usr/bin/env python3

from __future__ import annotations

import textwrap


def render_harness_config() -> str:
    return textwrap.dedent(
        """\
        [checks]
        required_ai_docs = [
          "AGENTS.md",
          "docs/ai/plan.md",
          "docs/ai/working-context.md",
        ]
        required_requirements_docs = [
          "docs/requirements/traceability-matrix.md",
        ]

        [context_surface]
        active_handoff_budget = 5
        archive_candidate_min_score = 3
        warn_at_budget = true

        [context_budget]
        default_surface_token_budget = 6500
        always_on_doc_line_budget = 300
        skill_description_word_budget = 30
        skill_body_line_budget = 400
        adr_count_budget = 15
        mcp_server_budget = 10
        """
    )


def render_requirements_txt() -> str:
    return textwrap.dedent(
        """\
        # Optional compatibility dependency for Python < 3.11.
        # Bootstrap treats dependency installation as best-effort by default
        # so offline repos can still finish initialization.
        tomli>=2,<3; python_version < "3.11"
        """
    )
