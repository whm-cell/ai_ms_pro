from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:
    tomllib = None  # type: ignore[assignment]


CONFIG_PATH = ".codex/harness.toml"
CODE_SUFFIXES = {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".json"}
EXCLUDED_PARTS = {
    ".git",
    ".next",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "coverage",
    "dist",
    "node_modules",
    "out",
}
DEFAULT_SCAN_ROOTS = ("app", "apps", "components", "pages", "src")
DEFAULT_FIXTURE_PATHS = (
    "__fixtures__/**",
    "__mocks__/**",
    "fixtures/**",
    "mocks/**",
    "mock-data/**",
    "stories/fixtures/**",
    "tests/fixtures/**",
    "dev-seeds/**",
)
DEFAULT_ALLOWED_CONSUMERS = (
    "**/*.stories.*",
    "**/*.test.*",
    "**/*.spec.*",
    "tests/**",
)
DEFAULT_MANIFEST_REQUIRED_PATHS = ("fixtures/**", "mocks/**", "mock-data/**", "dev-seeds/**")
DEFAULT_SCENARIO_MANIFEST_PATHS = ("mock-data/scenarios.jsonl", "mocks/scenarios.jsonl")
DEFAULT_RUNTIME_IMPORT_DENIED_PATHS = (
    "fixtures/**",
    "mocks/**",
    "mock-data/**",
    "dev-seeds/**",
    "__fixtures__/**",
    "__mocks__/**",
)
DEFAULT_IMPORT_ALIAS_PREFIXES = ("@/", "~/")


@dataclass(frozen=True)
class MockDataBoundaryConfig:
    enabled: bool
    scan_roots: tuple[str, ...]
    fixture_paths: tuple[str, ...]
    allowed_mock_consumer_paths: tuple[str, ...]
    manifest_required_paths: tuple[str, ...]
    scenario_manifest_paths: tuple[str, ...]
    runtime_import_denied_paths: tuple[str, ...]
    import_alias_prefixes: tuple[str, ...]
    max_inline_object_items: int
    max_inline_array_from_length: int
    max_inline_lines: int


@dataclass(frozen=True)
class MockDataFinding:
    path: str
    line: int
    code: str
    message: str
    suggested_layer: str = ""
    suggested_paths: tuple[str, ...] = ()
    doc_ref: str = "docs/ai/standards/mock-data-boundary.md"


@dataclass(frozen=True)
class MockDataBoundaryReport:
    enabled: bool
    scanned_files: list[str]
    findings: list[MockDataFinding]
    errors: list[str]


def load_config(root: Path, errors: list[str]) -> MockDataBoundaryConfig | None:
    config_path = root / CONFIG_PATH
    data: dict[str, Any] = {}
    if config_path.exists():
        raw_text = config_path.read_text(encoding="utf-8")
        try:
            data = load_toml(raw_text).get("mock_data_boundary", {})
        except ValueError as exc:
            errors.append(f"invalid TOML in {CONFIG_PATH}: {exc}")
            return None
    if data is None:
        data = {}
    if not isinstance(data, dict):
        errors.append("[mock_data_boundary] must be a table")
        return None
    try:
        return MockDataBoundaryConfig(
            enabled=bool_value(data.get("enabled"), default=False, label="mock_data_boundary.enabled"),
            scan_roots=string_tuple(
                data.get("scan_roots"),
                default=DEFAULT_SCAN_ROOTS,
                label="mock_data_boundary.scan_roots",
            ),
            fixture_paths=string_tuple(
                data.get("fixture_paths"),
                default=DEFAULT_FIXTURE_PATHS,
                label="mock_data_boundary.fixture_paths",
            ),
            allowed_mock_consumer_paths=string_tuple(
                data.get("allowed_mock_consumer_paths"),
                default=DEFAULT_ALLOWED_CONSUMERS,
                label="mock_data_boundary.allowed_mock_consumer_paths",
            ),
            manifest_required_paths=string_tuple(
                data.get("manifest_required_paths"),
                default=DEFAULT_MANIFEST_REQUIRED_PATHS,
                label="mock_data_boundary.manifest_required_paths",
            ),
            scenario_manifest_paths=string_tuple(
                data.get("scenario_manifest_paths"),
                default=DEFAULT_SCENARIO_MANIFEST_PATHS,
                label="mock_data_boundary.scenario_manifest_paths",
            ),
            runtime_import_denied_paths=string_tuple(
                data.get("runtime_import_denied_paths"),
                default=DEFAULT_RUNTIME_IMPORT_DENIED_PATHS,
                label="mock_data_boundary.runtime_import_denied_paths",
            ),
            import_alias_prefixes=string_tuple(
                data.get("import_alias_prefixes"),
                default=DEFAULT_IMPORT_ALIAS_PREFIXES,
                label="mock_data_boundary.import_alias_prefixes",
            ),
            max_inline_object_items=positive_int(
                data.get("max_inline_object_items"),
                default=3,
                label="mock_data_boundary.max_inline_object_items",
            ),
            max_inline_array_from_length=positive_int(
                data.get("max_inline_array_from_length"),
                default=12,
                label="mock_data_boundary.max_inline_array_from_length",
            ),
            max_inline_lines=positive_int(
                data.get("max_inline_lines"),
                default=40,
                label="mock_data_boundary.max_inline_lines",
            ),
        )
    except ValueError as exc:
        errors.append(str(exc))
        return None


def load_toml(raw_text: str) -> dict[str, Any]:
    if tomllib is not None:
        try:
            return tomllib.loads(raw_text)
        except tomllib.TOMLDecodeError as exc:
            raise ValueError(str(exc)) from exc
    return {}


def bool_value(value: object, *, default: bool, label: str) -> bool:
    if value is None:
        return default
    if not isinstance(value, bool):
        raise ValueError(f"{label} must be a boolean")
    return value


def positive_int(value: object, *, default: int, label: str) -> int:
    if value is None:
        return default
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ValueError(f"{label} must be a positive integer")
    return value


def string_tuple(value: object, *, default: tuple[str, ...], label: str) -> tuple[str, ...]:
    if value is None:
        return default
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{label} must be a list of strings")
    return tuple(value)


def iter_scan_files(root: Path, config: MockDataBoundaryConfig, errors: list[str]) -> list[Path]:
    files: list[Path] = []
    root = root.resolve()
    for entry in scan_root_entries(config):
        path = (root / entry).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            errors.append(f"mock_data_boundary.scan_roots path escapes repository root: {entry}")
            continue
        if not path.exists():
            continue
        candidates = [path] if path.is_file() else path.rglob("*")
        files.extend(
            item.resolve()
            for item in candidates
            if item.is_file() and item.suffix in CODE_SUFFIXES and not is_excluded(item)
        )
    return sorted(set(files))


def scan_root_entries(config: MockDataBoundaryConfig) -> tuple[str, ...]:
    entries = set(config.scan_roots)
    for pattern in config.manifest_required_paths:
        root = pattern.split("*", 1)[0].rstrip("/")
        if root:
            entries.add(root)
    return tuple(sorted(entries))


def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDED_PARTS for part in path.parts)


def is_fixture_path(path: str, config: MockDataBoundaryConfig) -> bool:
    return matches_any(path, config.fixture_paths)


def matches_any(path: str, patterns: tuple[str, ...]) -> bool:
    for pattern in patterns:
        if fnmatch(path, pattern):
            return True
        if pattern.endswith("/**") and path.startswith(pattern[:-3] + "/"):
            return True
    return False


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
