from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import subprocess

from mock_data_boundary_lib import CONFIG_PATH, load_toml


ROOT = Path(__file__).resolve().parents[1]
CODE_SUFFIXES = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".rs", ".go"}
EXCLUDED_PARTS = {".git", ".mypy_cache", ".next", ".pytest_cache", ".ruff_cache", "__pycache__", "coverage", "dist", "node_modules", "out"}
DEFAULT_SCAN_ROOTS = (".codex/hooks", "app", "apps", "components", "lib", "packages", "pages", "scripts", "src")
DEFAULT_REUSE_THRESHOLD = 4
DEFAULT_NEW_FILE_MIN_LINES = 80
GENERIC_TOKENS = {"check", "data", "helpers", "index", "lib", "main", "script", "test", "tests", "util", "utils"}
RETIREMENT_MARKERS = {"demo", "deprecated", "dev", "fixture", "legacy", "mock", "old", "seed", "smoke", "v1"}
SYMBOL_RE = re.compile(
    r"^\s*(?:export\s+)?(?:async\s+)?(?:def|class|function|const|let|var)\s+([A-Za-z_][A-Za-z0-9_]*)",
    re.MULTILINE,
)
WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9]*")


@dataclass(frozen=True)
class ReuseRetirementConfig:
    enabled: bool
    scan_roots: tuple[str, ...]
    new_file_min_lines: int
    reuse_score_threshold: int
    max_candidates: int
    retirement_markers: tuple[str, ...]


@dataclass(frozen=True)
class CodeRecord:
    path: str
    line_count: int
    tokens: tuple[str, ...]
    symbols: tuple[str, ...]


@dataclass(frozen=True)
class ReuseRetirementFinding:
    path: str
    line: int
    code: str
    message: str
    candidates: tuple[str, ...] = ()
    doc_ref: str = "docs/ai/standards/reuse-retirement-boundary.md"


@dataclass(frozen=True)
class ReuseRetirementReport:
    enabled: bool
    changed_files: list[str]
    scanned_files: int
    findings: list[ReuseRetirementFinding]
    errors: list[str]


def build_report(
    root: Path = ROOT,
    *,
    base: str = "origin/main",
    files: tuple[str, ...] | None = None,
) -> ReuseRetirementReport:
    root = root.resolve()
    errors: list[str] = []
    config = load_config(root, errors)
    if not config.enabled:
        return ReuseRetirementReport(False, [], 0, [], errors)
    changed = changed_files(root, base, files, errors)
    records = records_by_path(root, config, errors)
    findings = review_findings(config, changed, records)
    return ReuseRetirementReport(True, changed, len(records), findings, errors)


def load_config(root: Path, errors: list[str]) -> ReuseRetirementConfig:
    config_path = root / CONFIG_PATH
    table: object = {}
    if config_path.exists():
        try:
            table = load_toml(config_path.read_text(encoding="utf-8")).get("reuse_retirement", {})
        except ValueError as exc:
            errors.append(f"invalid TOML in {CONFIG_PATH}: {exc}")
    if table is None:
        table = {}
    if not isinstance(table, dict):
        errors.append("[reuse_retirement] must be a table")
        table = {}
    return ReuseRetirementConfig(
        enabled=bool_value(
            table.get("enabled"),
            default=False,
            errors=errors,
            label="reuse_retirement.enabled",
        ),
        scan_roots=string_tuple(
            table.get("scan_roots"),
            DEFAULT_SCAN_ROOTS,
            errors,
            "reuse_retirement.scan_roots",
        ),
        new_file_min_lines=positive_int(
            table.get("new_file_min_lines"),
            DEFAULT_NEW_FILE_MIN_LINES,
            errors,
            "reuse_retirement.new_file_min_lines",
        ),
        reuse_score_threshold=positive_int(
            table.get("reuse_score_threshold"),
            DEFAULT_REUSE_THRESHOLD,
            errors,
            "reuse_retirement.reuse_score_threshold",
        ),
        max_candidates=positive_int(
            table.get("max_candidates"),
            5,
            errors,
            "reuse_retirement.max_candidates",
        ),
        retirement_markers=string_tuple(
            table.get("retirement_markers"),
            tuple(sorted(RETIREMENT_MARKERS)),
            errors,
            "reuse_retirement.retirement_markers",
        ),
    )


def changed_files(
    root: Path,
    base: str,
    explicit: tuple[str, ...] | None,
    errors: list[str],
) -> list[str]:
    if explicit is not None:
        return sorted(path for path in explicit if is_code_path(path))
    paths: set[str] = set()
    commands = (
        ["git", "diff", "--name-only", "--diff-filter=AM", f"{base}...HEAD"],
        ["git", "diff", "--name-only", "--diff-filter=AM", "--cached"],
        ["git", "diff", "--name-only", "--diff-filter=AM"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    )
    for command in commands:
        try:
            result = subprocess.run(
                command,
                cwd=str(root),
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                check=False,
            )
        except OSError as exc:
            errors.append(f"could not run {' '.join(command)}: {exc}")
            continue
        if result.returncode == 0:
            paths.update(path for path in result.stdout.splitlines() if is_code_path(path))
    return sorted(paths)


def records_by_path(
    root: Path,
    config: ReuseRetirementConfig,
    errors: list[str],
) -> dict[str, CodeRecord]:
    records: dict[str, CodeRecord] = {}
    for scan_root in config.scan_roots:
        base = (root / scan_root).resolve()
        if not base.exists():
            continue
        if not is_under_root(base, root):
            errors.append(f"reuse_retirement.scan_roots path escapes repository root: {scan_root}")
            continue
        for path in iter_code_files(base):
            rel = relative(path, root)
            records[rel] = code_record(path, rel)
    return records


def review_findings(
    config: ReuseRetirementConfig,
    changed: list[str],
    records: dict[str, CodeRecord],
) -> list[ReuseRetirementFinding]:
    findings: list[ReuseRetirementFinding] = []
    for path in changed:
        record = records.get(path)
        if record is None:
            continue
        reuse = reuse_candidates(config, record, records)
        if reuse and record.line_count >= config.new_file_min_lines:
            findings.append(
                ReuseRetirementFinding(
                    path=path,
                    line=1,
                    code="reuse-review-candidate",
                    message="new or expanded code resembles existing repo code; review whether to reuse or extract before adding another implementation",
                    candidates=tuple(candidate.path for candidate in reuse[: config.max_candidates]),
                )
            )
        retire = retirement_candidates(config, record, records)
        if retire:
            findings.append(
                ReuseRetirementFinding(
                    path=path,
                    line=1,
                    code="retirement-review-candidate",
                    message="changed code may supersede older smoke/mock/legacy paths; review retire_now, keep_with_reason, or replace_by before leaving stale code behind",
                    candidates=tuple(candidate.path for candidate in retire[: config.max_candidates]),
                )
            )
    return findings


def reuse_candidates(
    config: ReuseRetirementConfig,
    target: CodeRecord,
    records: dict[str, CodeRecord],
) -> list[CodeRecord]:
    scored: list[tuple[int, CodeRecord]] = []
    for candidate in records.values():
        if candidate.path == target.path:
            continue
        score = similarity_score(target, candidate)
        if score >= config.reuse_score_threshold:
            scored.append((score, candidate))
    return [record for _, record in sorted(scored, key=lambda item: (-item[0], item[1].path))]


def retirement_candidates(
    config: ReuseRetirementConfig,
    target: CodeRecord,
    records: dict[str, CodeRecord],
) -> list[CodeRecord]:
    markers = set(config.retirement_markers)
    target_tokens = set(target.tokens)
    candidates: list[CodeRecord] = []
    for candidate in records.values():
        if candidate.path == target.path:
            continue
        candidate_tokens = set(candidate.tokens)
        shared_specific_tokens = (target_tokens - markers) & (candidate_tokens - markers)
        if markers & candidate_tokens and len(shared_specific_tokens) >= 2:
            candidates.append(candidate)
    return sorted(candidates, key=lambda item: item.path)


def similarity_score(left: CodeRecord, right: CodeRecord) -> int:
    token_score = len(set(left.tokens) & set(right.tokens))
    symbol_score = len(set(left.symbols) & set(right.symbols)) * 2
    return token_score + symbol_score


def code_record(path: Path, rel: str) -> CodeRecord:
    text = path.read_text(encoding="utf-8", errors="ignore")
    symbols = tuple(sorted(set(SYMBOL_RE.findall(text))))
    tokens = tuple(sorted(set(path_tokens(Path(rel)) | symbol_tokens(symbols))))
    return CodeRecord(rel, len(text.splitlines()), tokens, symbols)


def path_tokens(path: Path) -> set[str]:
    parts = [path.stem, *path.parts[:-1]]
    return {token for part in parts for token in split_tokens(part) if token not in GENERIC_TOKENS}


def symbol_tokens(symbols: tuple[str, ...]) -> set[str]:
    return {token for symbol in symbols for token in split_tokens(symbol) if token not in GENERIC_TOKENS}


def split_tokens(value: str) -> set[str]:
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    return {match.group(0).lower() for match in WORD_RE.finditer(normalized.replace("-", "_"))}


def iter_code_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and is_code_path(path.as_posix())
        and not (set(path.parts) & EXCLUDED_PARTS)
    )


def is_code_path(path: str) -> bool:
    return Path(path).suffix in CODE_SUFFIXES


def is_under_root(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def bool_value(value: object, *, default: bool, errors: list[str], label: str) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    errors.append(f"{label} must be a boolean")
    return default


def positive_int(value: object, default: int, errors: list[str], label: str) -> int:
    if value is None:
        return default
    if isinstance(value, int) and not isinstance(value, bool) and value > 0:
        return value
    errors.append(f"{label} must be a positive integer")
    return default


def string_tuple(
    value: object,
    default: tuple[str, ...],
    errors: list[str],
    label: str,
) -> tuple[str, ...]:
    if value is None:
        return default
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return tuple(value)
    errors.append(f"{label} must be a list of strings")
    return default
