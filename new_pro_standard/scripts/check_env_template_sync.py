#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from harness_config import HarnessConfigError, load_harness_config, resolve_repo_paths


ROOT = Path(__file__).resolve().parents[1]
KEY_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=")


@dataclass(frozen=True)
class EnvTemplateSyncReport:
    enabled: bool
    template_paths: list[str]
    local_env_paths: list[str]
    template_key_count: int
    local_key_count: int
    missing_keys: list[str]
    extra_keys: list[str]
    errors: list[str]
    warnings: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check local env key drift against env templates without reading or printing values.",
    )
    parser.add_argument("--template", help="Template env file path.")
    parser.add_argument("--env", help="Local env file path.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument(
        "--warning-only",
        action="store_true",
        help="Return success even when local env keys are missing.",
    )
    return parser.parse_args()


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def read_env_keys(path: Path) -> set[str]:
    keys: set[str] = set()
    if not path.exists():
        return keys
    for line in path.read_text(encoding="utf-8").splitlines():
        if match := KEY_RE.match(line):
            keys.add(match.group(1))
    return keys


def configured_paths(
    root: Path,
    template: str | None,
    env: str | None,
) -> tuple[bool, list[Path], list[Path], list[str]]:
    errors: list[str] = []
    if template or env:
        template_paths = resolve_repo_paths(
            root,
            (template or ".env.example",),
            config_label="env template",
        )
        env_paths = resolve_repo_paths(root, (env or ".env",), config_label="local env")
        return True, template_paths, env_paths, errors

    try:
        config = load_harness_config(root).config_contracts
    except HarnessConfigError as exc:
        return False, [], [], [str(exc)]

    template_paths = resolve_repo_paths(
        root,
        config.env_template_paths,
        config_label="config_contracts.env_template_paths",
    )
    env_paths = resolve_repo_paths(
        root,
        config.local_env_paths,
        config_label="config_contracts.local_env_paths",
    )
    return config.enabled, template_paths, env_paths, errors


def build_report(
    *,
    root: Path = ROOT,
    template: str | None = None,
    env: str | None = None,
) -> EnvTemplateSyncReport:
    root = root.resolve()
    enabled, template_paths, env_paths, errors = configured_paths(root, template, env)
    warnings: list[str] = []

    if not enabled:
        return EnvTemplateSyncReport(False, [], [], 0, 0, [], [], errors, warnings)

    if not template_paths:
        return EnvTemplateSyncReport(True, [], [], 0, 0, [], [], errors, warnings)

    template_keys: set[str] = set()
    local_keys: set[str] = set()
    for path in template_paths:
        if not path.exists():
            errors.append(f"env template file missing: {relative(path, root)}")
        template_keys.update(read_env_keys(path))
    for path in env_paths:
        if not path.exists():
            warnings.append(f"local env file missing: {relative(path, root)}")
        local_keys.update(read_env_keys(path))

    missing = sorted(template_keys - local_keys)
    extra = sorted(local_keys - template_keys)
    if missing:
        errors.append(
            f"local env is missing {len(missing)} template key(s): " + ", ".join(missing)
        )
    if extra:
        warnings.append(
            f"local env has {len(extra)} local-only key(s): " + ", ".join(extra)
        )

    return EnvTemplateSyncReport(
        enabled=True,
        template_paths=[relative(path, root) for path in template_paths],
        local_env_paths=[relative(path, root) for path in env_paths],
        template_key_count=len(template_keys),
        local_key_count=len(local_keys),
        missing_keys=missing,
        extra_keys=extra,
        errors=errors,
        warnings=warnings,
    )


def render_report(report: EnvTemplateSyncReport) -> str:
    lines = ["Env template sync check"]
    if not report.enabled:
        lines.append("Disabled")
        return "\n".join(lines)
    lines.append(
        f"Templates: {', '.join(report.template_paths) or '(none)'} "
        f"({report.template_key_count} keys)"
    )
    lines.append(
        f"Local env paths: {', '.join(report.local_env_paths) or '(none)'} "
        f"({report.local_key_count} keys)"
    )
    lines.extend(f"ERROR: {message}" for message in report.errors)
    lines.extend(f"WARN: {message}" for message in report.warnings)
    if not report.errors:
        lines.append("OK")
    return "\n".join(lines)


def exit_code(report: EnvTemplateSyncReport, *, warning_only: bool) -> int:
    return 0 if warning_only or not report.errors else 1


def main() -> int:
    args = parse_args()
    report = build_report(template=args.template, env=args.env)
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print(render_report(report))
    return exit_code(report, warning_only=args.warning_only)


if __name__ == "__main__":
    raise SystemExit(main())
