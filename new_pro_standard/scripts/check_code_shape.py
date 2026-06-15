#!/usr/bin/env python3

from __future__ import annotations

import argparse
import fnmatch
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from code_shape_ast import DefinitionShape, collect_python_shapes, summarize

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore[import-not-found]

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / ".codex" / "code_shape.toml"

@dataclass(frozen=True)
class Limit:
    warn: int
    error: int

@dataclass(frozen=True)
class FileOverride:
    name: str
    patterns: tuple[str, ...]
    kinds: tuple[str, ...]
    limit: Limit

@dataclass(frozen=True)
class Config:
    include: tuple[str, ...]
    exclude: tuple[str, ...]
    python_file: Limit
    python_function: Limit
    python_class: Limit
    shell_file: Limit
    typescript_file: Limit
    javascript_file: Limit
    stylesheet_file: Limit
    sql_file: Limit
    rust_file: Limit
    powershell_file: Limit
    file_overrides: tuple[FileOverride, ...]

@dataclass(frozen=True)
class Candidate:
    path: str
    kind: str
    is_new: bool
    text: str

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check staged or repo-wide code-shape budgets."
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Check files from the Git index instead of the working tree.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Check tracked and untracked files that match the code-shape scope.",
    )
    args = parser.parse_args()
    if args.staged == args.all:
        parser.error("Specify exactly one of --staged or --all.")
    return args

def load_config() -> Config:
    data = tomllib.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    scope = data["scope"]
    thresholds = data["thresholds"]
    file_overrides = tuple(
        FileOverride(
            name=item["name"],
            patterns=tuple(item["patterns"]),
            kinds=tuple(item.get("kinds", ())),
            limit=Limit(warn=item["warn"], error=item["error"]),
        )
        for item in data.get("file_overrides", ())
    )
    return Config(
        include=tuple(scope["include"]),
        exclude=tuple(scope["exclude"]),
        python_file=Limit(**thresholds["python_file"]),
        python_function=Limit(**thresholds["python_function"]),
        python_class=Limit(**thresholds["python_class"]),
        shell_file=Limit(**thresholds["shell_file"]),
        typescript_file=Limit(**thresholds.get("typescript_file", thresholds["python_file"])),
        javascript_file=Limit(**thresholds.get("javascript_file", thresholds.get("typescript_file", thresholds["python_file"]))),
        stylesheet_file=Limit(**thresholds.get("stylesheet_file", thresholds["shell_file"])),
        sql_file=Limit(**thresholds.get("sql_file", thresholds["shell_file"])),
        rust_file=Limit(**thresholds.get("rust_file", thresholds.get("typescript_file", thresholds["python_file"]))),
        powershell_file=Limit(**thresholds.get("powershell_file", thresholds["shell_file"])),
        file_overrides=file_overrides,
    )

def run_git(args: list[str]) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=str(ROOT),
        capture_output=True,
        check=False,
    )

def repo_has_commits() -> bool:
    result = run_git(["rev-parse", "--verify", "HEAD"])
    return result.returncode == 0


def decode_text(blob: bytes, path: str) -> str:
    try:
        return blob.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{path} is not valid UTF-8 text: {exc}") from exc

def path_matches(path: str, config: Config) -> bool:
    if not any(fnmatch.fnmatchcase(path, pattern) for pattern in config.include):
        return False
    if any(fnmatch.fnmatchcase(path, pattern) for pattern in config.exclude):
        return False
    return True

def detect_kind(path: str) -> str | None:
    pure = PurePosixPath(path)
    if pure.suffix == ".py":
        return "python"
    if pure.suffix in {".ts", ".tsx"}:
        return "typescript"
    if pure.suffix in {".js", ".jsx", ".mjs", ".cjs"}:
        return "javascript"
    if pure.suffix in {".css", ".scss"}:
        return "stylesheet"
    if pure.suffix == ".sql":
        return "sql"
    if pure.suffix == ".rs":
        return "rust"
    if pure.suffix == ".sh" or path == ".githooks/pre-commit":
        return "shell"
    if pure.suffix == ".ps1":
        return "powershell"
    return None


def load_staged_candidates(config: Config) -> list[Candidate]:
    result = run_git(["diff", "--cached", "--name-status", "--diff-filter=ACMR", "--relative"])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace").strip())

    initial_commit = not repo_has_commits()
    candidates: list[Candidate] = []
    for raw_line in result.stdout.decode("utf-8").splitlines():
        if not raw_line.strip():
            continue
        parts = raw_line.split("\t")
        status = parts[0][0]
        path = parts[-1].replace("\\", "/")
        if not path_matches(path, config):
            continue
        kind = detect_kind(path)
        if kind is None:
            continue
        blob = run_git(["show", f":{path}"])
        if blob.returncode != 0:
            raise RuntimeError(blob.stderr.decode("utf-8", errors="replace").strip())
        candidates.append(
            Candidate(
                path=path,
                kind=kind,
                is_new=status == "A" and not initial_commit,
                text=decode_text(blob.stdout, path),
            )
        )
    return candidates

def load_all_candidates(config: Config) -> list[Candidate]:
    result = run_git(["ls-files", "--cached", "--others", "--exclude-standard"])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace").strip())

    candidates: list[Candidate] = []
    for raw_path in result.stdout.decode("utf-8").splitlines():
        path = raw_path.replace("\\", "/")
        if not path_matches(path, config):
            continue
        kind = detect_kind(path)
        if kind is None:
            continue
        candidate_path = ROOT / path
        if not candidate_path.exists():
            continue
        text = decode_text(candidate_path.read_bytes(), path)
        candidates.append(Candidate(path=path, kind=kind, is_new=False, text=text))
    return candidates


def add_length_findings(
    errors: list[str],
    warnings: list[str],
    *,
    path: str,
    label: str,
    limit: Limit,
    actual: int,
    is_new: bool,
) -> None:
    if actual > limit.error and is_new:
        errors.append(
            f"new {label} {path} has {actual} lines (> {limit.error}). "
            "Split responsibilities before adding it."
        )
        return
    if actual > limit.warn:
        prefix = "new" if is_new else "existing"
        warnings.append(
            f"{prefix} {label} {path} has {actual} lines (> {limit.warn}). "
            "Keep the file small enough to stay easy to split and review."
        )

def add_definition_findings(
    errors: list[str],
    warnings: list[str],
    *,
    path: str,
    label: str,
    limit: Limit,
    items: list[DefinitionShape],
    is_new: bool,
) -> None:
    over_error = [item for item in items if item.lines > limit.error]
    over_warn = [item for item in items if limit.warn < item.lines <= limit.error]
    if over_error and is_new:
        errors.append(
            f"new {label} in {path} exceeds {limit.error} lines: "
            f"{summarize(over_error, limit.error)}"
        )
    elif over_error:
        warnings.append(
            f"existing {label} in {path} already exceeds the hard ceiling {limit.error}: "
            f"{summarize(over_error, limit.error)}"
        )
    if over_warn:
        prefix = "new" if is_new else "existing"
        warnings.append(
            f"{prefix} {label} in {path} exceeds the warning threshold {limit.warn}: "
            f"{summarize(over_warn, limit.warn)}"
        )

def check_python_candidate(
    candidate: Candidate,
    config: Config,
    errors: list[str],
    warnings: list[str],
) -> None:
    line_count = len(candidate.text.splitlines())
    label, limit = file_budget(candidate, config)
    add_length_findings(
        errors,
        warnings,
        path=candidate.path,
        label=label,
        limit=limit,
        actual=line_count,
        is_new=candidate.is_new,
    )
    functions, classes = collect_python_shapes(candidate.text)
    add_definition_findings(
        errors,
        warnings,
        path=candidate.path,
        label="function/method",
        limit=config.python_function,
        items=functions,
        is_new=candidate.is_new,
    )
    add_definition_findings(
        errors,
        warnings,
        path=candidate.path,
        label="class",
        limit=config.python_class,
        items=classes,
        is_new=candidate.is_new,
    )

def simple_kind_budget(candidate: Candidate, config: Config) -> tuple[str, Limit]:
    if candidate.kind == "python":
        return ("Python file", config.python_file)
    if candidate.kind == "typescript":
        return ("TypeScript file", config.typescript_file)
    if candidate.kind == "javascript":
        return ("JavaScript file", config.javascript_file)
    if candidate.kind == "stylesheet":
        return ("stylesheet file", config.stylesheet_file)
    if candidate.kind == "sql":
        return ("SQL file", config.sql_file)
    if candidate.kind == "rust":
        return ("Rust file", config.rust_file)
    if candidate.kind == "powershell":
        return ("PowerShell file", config.powershell_file)
    return ("shell file", config.shell_file)

def file_budget(candidate: Candidate, config: Config) -> tuple[str, Limit]:
    label, limit = simple_kind_budget(candidate, config)
    for override in config.file_overrides:
        if candidate.kind not in override.kinds:
            continue
        if any(fnmatch.fnmatchcase(candidate.path, pattern) for pattern in override.patterns):
            return (f"{label} ({override.name})", override.limit)
    return (label, limit)

def check_candidate(
    candidate: Candidate,
    config: Config,
    errors: list[str],
    warnings: list[str],
) -> None:
    if candidate.kind == "python":
        check_python_candidate(candidate, config, errors, warnings)
        return

    label, limit = file_budget(candidate, config)
    add_length_findings(
        errors,
        warnings,
        path=candidate.path,
        label=label,
        limit=limit,
        actual=len(candidate.text.splitlines()),
        is_new=candidate.is_new,
    )

def main() -> int:
    args = parse_args()
    config = load_config()
    errors: list[str] = []
    warnings: list[str] = []

    try:
        candidates = (
            load_staged_candidates(config) if args.staged else load_all_candidates(config)
        )
        for candidate in candidates:
            check_candidate(candidate, config, errors, warnings)
    except (RuntimeError, ValueError, SyntaxError) as exc:
        print("Code shape checks: FAILED")
        print(f"ERROR: {exc}")
        return 1

    if errors:
        print("Code shape checks: FAILED")
        for message in errors:
            print(f"ERROR: {message}")
        for message in warnings:
            print(f"WARN: {message}")
        return 1

    print("Code shape checks: OK")
    if not candidates:
        message = "INFO: No staged files matched the code-shape scope."
        if args.all:
            message = "INFO: No files matched the code-shape scope."
        print(message)
    for message in warnings:
        print(f"WARN: {message}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
