#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

from change_triggered_followup_rules import HARNESS_SAMPLE_GAP_COMMANDS
from check_change_triggered_followups import build_followups
from harness_sample_followup_coverage_config import DISCOVERY_PATTERNS, REQUIRED_COMMANDS


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FOLLOWUP = "harness-sample-gap-evidence"



@dataclass(frozen=True)
class CoverageAudit:
    checked_paths: tuple[str, ...]
    missing_followup_paths: tuple[str, ...]
    missing_commands: tuple[str, ...]
    unrequired_routed_commands: tuple[str, ...]
    routed_missing_commands: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not (
            self.missing_followup_paths
            or self.missing_commands
            or self.unrequired_routed_commands
            or self.routed_missing_commands
        )

    @property
    def errors(self) -> tuple[str, ...]:
        errors: list[str] = []
        errors.extend(f"{path}: missing {REQUIRED_FOLLOWUP} follow-up" for path in self.missing_followup_paths)
        errors.extend(f"missing required command constant: {command}" for command in self.missing_commands)
        errors.extend(
            f"routed command missing from required coverage: {command}" for command in self.unrequired_routed_commands
        )
        errors.extend(f"missing routed follow-up command: {command}" for command in self.routed_missing_commands)
        return tuple(errors)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit sample-gap change-triggered follow-up coverage.")
    parser.add_argument("--root", default=str(ROOT), help="Repository root to inspect.")
    parser.add_argument("--files", nargs="*", help="Explicit repo-relative paths to audit instead of discovery.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def normalize(path: str) -> str:
    normalized = path.replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def discover_paths(root: Path = ROOT) -> tuple[str, ...]:
    found: set[str] = set()
    for pattern in DISCOVERY_PATTERNS:
        if any(char in pattern for char in "*?["):
            for path in root.glob(pattern):
                if path.is_file():
                    found.add(path.relative_to(root).as_posix())
            continue
        if (root / pattern).is_file():
            found.add(pattern)
    return tuple(sorted(found))


def followup_commands_for(path: str) -> tuple[str, ...]:
    for followup in build_followups((path,)):
        if followup.name == REQUIRED_FOLLOWUP:
            return followup.commands
    return ()


def audit(paths: tuple[str, ...]) -> CoverageAudit:
    normalized = tuple(sorted({normalize(path) for path in paths if path}))
    missing_followup = tuple(path for path in normalized if not followup_commands_for(path))
    missing_commands = tuple(command for command in REQUIRED_COMMANDS if command not in HARNESS_SAMPLE_GAP_COMMANDS)
    unrequired_routed = tuple(command for command in HARNESS_SAMPLE_GAP_COMMANDS if command not in REQUIRED_COMMANDS)

    probe_commands = followup_commands_for("scripts/change_triggered_harness_sample_rules.py")
    routed_missing = tuple(command for command in REQUIRED_COMMANDS if command not in probe_commands)

    return CoverageAudit(
        checked_paths=normalized,
        missing_followup_paths=missing_followup,
        missing_commands=missing_commands,
        unrequired_routed_commands=unrequired_routed,
        routed_missing_commands=routed_missing,
    )


def to_payload(result: CoverageAudit) -> dict[str, object]:
    return {
        "ok": result.ok,
        "required_followup": REQUIRED_FOLLOWUP,
        "checked_paths": result.checked_paths,
        "checked_path_count": len(result.checked_paths),
        "required_commands": REQUIRED_COMMANDS,
        "missing_followup_paths": result.missing_followup_paths,
        "missing_commands": result.missing_commands,
        "unrequired_routed_commands": result.unrequired_routed_commands,
        "routed_missing_commands": result.routed_missing_commands,
        "errors": result.errors,
    }


def emit_text(result: CoverageAudit) -> None:
    print("Harness sample follow-up coverage audit:")
    print(f"- checked paths: {len(result.checked_paths)}")
    print(f"- required follow-up: {REQUIRED_FOLLOWUP}")
    print(f"- routed commands: {len(HARNESS_SAMPLE_GAP_COMMANDS)}")
    print(f"- required commands: {len(REQUIRED_COMMANDS)}")
    if result.ok:
        print("ERRORS: none")
        return
    print("ERRORS:")
    for error in result.errors:
        print(f"- {error}")


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    paths = tuple(normalize(path) for path in args.files) if args.files is not None else discover_paths(root)
    result = audit(paths)
    if args.json:
        print(json.dumps(to_payload(result), ensure_ascii=False, indent=2))
    else:
        emit_text(result)
    return 0 if result.ok else 1


if __name__ == "__main__":
    sys.exit(main())
