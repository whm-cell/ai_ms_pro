#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Pattern

from harness_config import (
    ConfigContractsConfig,
    HarnessConfigError,
    load_harness_config,
    resolve_repo_paths,
)


ROOT = Path(__file__).resolve().parents[1]
CODE_SUFFIXES = {
    ".cjs",
    ".js",
    ".jsx",
    ".json",
    ".mjs",
    ".ps1",
    ".py",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".yaml",
    ".yml",
}
EXCLUDED_DIR_NAMES = {
    ".git",
    ".mypy_cache",
    ".next",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "coverage",
    "dist",
    "node_modules",
    "output",
}
EXCLUDED_PATH_PARTS = ((".codex", ".venv"), (".codex", "runtime"))
HARNESS_CONFIG_PATH = ".codex/harness.toml"


@dataclass(frozen=True)
class ConfigContractReport:
    enabled: bool
    scanned_files: list[str]
    errors: list[str]
    warnings: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check that config keys, sensitive key names, and literals stay inside declared config registries.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args()


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def compile_patterns(
    patterns: tuple[str, ...],
    *,
    label: str,
    errors: list[str],
) -> list[Pattern[str]]:
    compiled: list[Pattern[str]] = []
    for index, pattern in enumerate(patterns, start=1):
        try:
            compiled.append(re.compile(pattern))
        except re.error as exc:
            errors.append(f"{label}[{index}] invalid regex: {exc}")
    return compiled


def resolve_existing_paths(
    root: Path,
    entries: tuple[str, ...],
    *,
    label: str,
    errors: list[str],
) -> list[Path]:
    resolved: list[Path] = []
    try:
        paths = resolve_repo_paths(root, entries, config_label=label)
    except HarnessConfigError as exc:
        errors.append(str(exc))
        return resolved
    for path in paths:
        if not path.exists():
            errors.append(f"{label} path missing: {relative(path, root)}")
            continue
        resolved.append(path)
    return resolved


def is_excluded(path: Path) -> bool:
    parts = path.parts
    if any(part in EXCLUDED_DIR_NAMES for part in parts):
        return True
    return any(all(item in parts for item in excluded) for excluded in EXCLUDED_PATH_PARTS)


def iter_scan_files(root: Path, scan_roots: tuple[str, ...], errors: list[str]) -> list[Path]:
    files: list[Path] = []
    roots = resolve_existing_paths(root, scan_roots, label="config_contracts.scan_roots", errors=errors)
    for scan_root in roots:
        candidates = [scan_root] if scan_root.is_file() else list(scan_root.rglob("*"))
        for path in candidates:
            if not path.is_file() or is_excluded(path) or path.suffix not in CODE_SUFFIXES:
                continue
            files.append(path.resolve())
    return sorted(set(files))


def line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def env_assignments(path: Path) -> dict[str, str]:
    assignments: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key.strip()):
            assignments[key.strip()] = value.strip().strip("\"'")
    return assignments


def sensitive_template_value_errors(
    *,
    root: Path,
    template_paths: list[Path],
    secret_patterns: list[Pattern[str]],
) -> list[str]:
    errors: list[str] = []
    if not secret_patterns:
        return errors
    for path in template_paths:
        for key, value in env_assignments(path).items():
            if value and any(pattern.search(key) for pattern in secret_patterns):
                errors.append(
                    f"env template contains non-empty sensitive key value: {relative(path, root)} -> {key}"
                )
    return errors


def scan_disallowed_patterns(
    *,
    root: Path,
    files: list[Path],
    allowed_paths: set[Path],
    pattern_groups: tuple[tuple[str, list[Pattern[str]]], ...],
) -> list[str]:
    errors: list[str] = []
    for path in files:
        if path.resolve() in allowed_paths:
            continue
        text = path.read_text(encoding="utf-8")
        for label, patterns in pattern_groups:
            for index, pattern in enumerate(patterns, start=1):
                for match in pattern.finditer(text):
                    errors.append(
                        f"{label}[{index}] matched outside config contract boundary: "
                        f"{relative(path, root)}:{line_number(text, match.start())}"
                    )
    return errors


def load_config(root: Path, errors: list[str]) -> ConfigContractsConfig | None:
    try:
        return load_harness_config(root).config_contracts
    except HarnessConfigError as exc:
        errors.append(str(exc))
        return None


def build_report(root: Path = ROOT) -> ConfigContractReport:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    config = load_config(root, errors)
    if config is None or not config.enabled:
        return ConfigContractReport(False, [], errors, warnings)

    secret_patterns = compile_patterns(config.secret_key_patterns, label="secret_key_patterns", errors=errors)
    config_patterns = compile_patterns(config.config_key_patterns, label="config_key_patterns", errors=errors)
    literal_patterns = compile_patterns(config.literal_patterns, label="literal_patterns", errors=errors)
    registry_paths = resolve_existing_paths(
        root,
        config.registry_paths,
        label="config_contracts.registry_paths",
        errors=errors,
    )
    allowed_paths = set(registry_paths)
    allowed_paths.update(
        resolve_existing_paths(
            root,
            config.allowed_literal_paths,
            label="config_contracts.allowed_literal_paths",
            errors=errors,
        )
    )
    template_paths = resolve_existing_paths(
        root,
        config.env_template_paths,
        label="config_contracts.env_template_paths",
        errors=errors,
    )
    allowed_paths.update(template_paths)
    harness_config_path = root / HARNESS_CONFIG_PATH
    if harness_config_path.exists():
        allowed_paths.add(harness_config_path.resolve())

    files = iter_scan_files(root, config.scan_roots, errors)
    errors.extend(
        sensitive_template_value_errors(
            root=root,
            template_paths=template_paths,
            secret_patterns=secret_patterns,
        )
    )
    errors.extend(
        scan_disallowed_patterns(
            root=root,
            files=files,
            allowed_paths={path.resolve() for path in allowed_paths},
            pattern_groups=(
                ("secret_key_patterns", secret_patterns),
                ("config_key_patterns", config_patterns),
                ("literal_patterns", literal_patterns),
            ),
        )
    )

    return ConfigContractReport(
        enabled=True,
        scanned_files=[relative(path, root) for path in files],
        errors=errors,
        warnings=warnings,
    )


def render_report(report: ConfigContractReport) -> str:
    lines = ["Config contract boundary check"]
    if not report.enabled:
        lines.append("Disabled")
        return "\n".join(lines)
    lines.append(f"Scanned files: {len(report.scanned_files)}")
    lines.extend(f"ERROR: {message}" for message in report.errors)
    lines.extend(f"WARN: {message}" for message in report.warnings)
    if not report.errors:
        lines.append("OK")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    report = build_report()
    if args.json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print(render_report(report))
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
