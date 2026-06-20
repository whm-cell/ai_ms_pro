#!/usr/bin/env python3

from __future__ import annotations

import textwrap


def render_harness_config() -> str:
    return "".join(
        (
            render_base_harness_config(),
            render_mock_data_boundary_config(),
            render_data_activation_config(),
            render_reuse_retirement_config(),
            render_context_budget_config(),
        )
    )


def render_base_harness_config() -> str:
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

        [config_contracts]
        enabled = true
        env_template_paths = []
        local_env_paths = [
          ".env",
          ".env.local",
        ]
        registry_paths = []
        scan_roots = [
          "scripts",
          ".codex/hooks",
        ]
        allowed_literal_paths = []
        secret_key_patterns = []
        config_key_patterns = []
        literal_patterns = []
        """
    )


def render_mock_data_boundary_config() -> str:
    return textwrap.dedent(
        """\
        [mock_data_boundary]
        enabled = true
        scan_roots = [
          "app",
          "apps",
          "components",
          "pages",
          "src",
        ]
        fixture_paths = [
          "__fixtures__/**",
          "__mocks__/**",
          "fixtures/**",
          "mocks/**",
          "mock-data/**",
          "stories/fixtures/**",
          "tests/fixtures/**",
          "dev-seeds/**",
        ]
        allowed_mock_consumer_paths = [
          "**/*.stories.*",
          "**/*.test.*",
          "**/*.spec.*",
          "tests/**",
        ]
        manifest_required_paths = [
          "fixtures/**",
          "mocks/**",
          "mock-data/**",
          "dev-seeds/**",
        ]
        scenario_manifest_paths = [
          "mock-data/scenarios.jsonl",
          "mocks/scenarios.jsonl",
        ]
        runtime_import_denied_paths = [
          "fixtures/**",
          "mocks/**",
          "mock-data/**",
          "dev-seeds/**",
          "__fixtures__/**",
          "__mocks__/**",
        ]
        import_alias_prefixes = [
          "@/",
          "~/",
        ]
        max_inline_object_items = 3
        max_inline_array_from_length = 12
        max_inline_lines = 40
        """
    )


def render_data_activation_config() -> str:
    return textwrap.dedent(
        """\
        [data_activation]
        enabled = true
        mode = "smoke"
        """
    )


def render_reuse_retirement_config() -> str:
    return textwrap.dedent(
        """\
        [reuse_retirement]
        enabled = true
        scan_roots = [
          ".codex/hooks",
          "app",
          "apps",
          "components",
          "lib",
          "packages",
          "pages",
          "scripts",
          "src",
        ]
        new_file_min_lines = 80
        reuse_score_threshold = 4
        max_candidates = 5
        retirement_markers = [
          "demo",
          "deprecated",
          "dev",
          "fixture",
          "legacy",
          "mock",
          "old",
          "seed",
          "smoke",
          "v1",
        ]
        """
    )


def render_context_budget_config() -> str:
    return textwrap.dedent(
        """\
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
