from __future__ import annotations

from dataclasses import dataclass, field


DEFAULT_TOOL_OUTPUT_TOKEN_BUDGET = 5000
DEFAULT_LAST_INPUT_TOKEN_BUDGET = 100000
DEFAULT_FRESH_INPUT_TOKEN_BUDGET = 50000
DEFAULT_TASK_COMPLETE_BUDGET = 8
DEFAULT_TOKEN_SNAPSHOT_BUDGET = 160
DEFAULT_SESSION_MINUTES_BUDGET = 90

CONFIG_KEYS = {
    "tool_output_token_budget": DEFAULT_TOOL_OUTPUT_TOKEN_BUDGET,
    "last_input_token_budget": DEFAULT_LAST_INPUT_TOKEN_BUDGET,
    "fresh_input_token_budget": DEFAULT_FRESH_INPUT_TOKEN_BUDGET,
    "task_complete_budget": DEFAULT_TASK_COMPLETE_BUDGET,
    "token_snapshot_budget": DEFAULT_TOKEN_SNAPSHOT_BUDGET,
    "session_minutes_budget": DEFAULT_SESSION_MINUTES_BUDGET,
}


@dataclass(frozen=True)
class RuntimeTokenBudgetConfig:
    tool_output_token_budget: int = DEFAULT_TOOL_OUTPUT_TOKEN_BUDGET
    last_input_token_budget: int = DEFAULT_LAST_INPUT_TOKEN_BUDGET
    fresh_input_token_budget: int = DEFAULT_FRESH_INPUT_TOKEN_BUDGET
    task_complete_budget: int = DEFAULT_TASK_COMPLETE_BUDGET
    token_snapshot_budget: int = DEFAULT_TOKEN_SNAPSHOT_BUDGET
    session_minutes_budget: int = DEFAULT_SESSION_MINUTES_BUDGET


@dataclass(frozen=True)
class ToolOutputFinding:
    line: int
    estimated_tokens: int
    tool_name: str
    arguments_preview: str


@dataclass(frozen=True)
class TranscriptReport:
    path: str
    line_count: int = 0
    task_complete_count: int = 0
    token_snapshot_count: int = 0
    elapsed_minutes: int = 0
    max_last_input_tokens: int = 0
    max_last_cached_tokens: int = 0
    max_fresh_input_tokens: int = 0
    max_tool_output_tokens: int = 0
    tool_output_findings: list[ToolOutputFinding] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RuntimeTokenBudgetReport:
    config: RuntimeTokenBudgetConfig
    transcripts: list[TranscriptReport]
    warnings: list[str]
