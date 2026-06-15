from __future__ import annotations


Rule = dict[str, object]
WARNING_SAMPLE_CODE_ALIGNMENT_COMMANDS = (
    ".codex/hooks/run_with_repo_python.sh scripts/check_warning_sample_code_alignment.py",
    "python3 tests/test_warning_sample_code_alignment.py",
)


def rule(
    name: str,
    level: str,
    ci_coverage: str,
    patterns: tuple[str, ...],
    commands: tuple[str, ...],
    references: tuple[str, ...],
    reason: str,
) -> Rule:
    return {
        "name": name,
        "level": level,
        "ci_coverage": ci_coverage,
        "patterns": patterns,
        "commands": commands,
        "references": references,
        "reason": reason,
    }
