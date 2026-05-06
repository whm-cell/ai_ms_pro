#!/usr/bin/env python3

from __future__ import annotations

import argparse
import ast
import fnmatch
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

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
class Config:
    include: tuple[str, ...]
    exclude: tuple[str, ...]
    python_file: Limit
    python_function: Limit
    python_class: Limit
    shell_file: Limit

@dataclass(frozen=True)
class Candidate:
    path: str
    kind: str
    is_new: bool
    text: str

@dataclass(frozen=True)
class DefinitionShape:
    qualname: str
    lines: int

class ShapeVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.stack: list[str] = []
        self.functions: list[DefinitionShape] = []
        self.classes: list[DefinitionShape] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.classes.append(DefinitionShape(self._qualname(node.name), self._lines(node)))
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.functions.append(DefinitionShape(self._qualname(node.name), self._lines(node)))
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.functions.append(DefinitionShape(self._qualname(node.name), self._lines(node)))
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def _qualname(self, name: str) -> str:
        return ".".join([*self.stack, name]) if self.stack else name

    @staticmethod
    def _lines(node: ast.AST) -> int:
        start = getattr(node, "lineno", 0)
        end = getattr(node, "end_lineno", start)
        return end - start + 1


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
    return Config(
        include=tuple(scope["include"]),
        exclude=tuple(scope["exclude"]),
        python_file=Limit(**thresholds["python_file"]),
        python_function=Limit(**thresholds["python_function"]),
        python_class=Limit(**thresholds["python_class"]),
        shell_file=Limit(**thresholds["shell_file"]),
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
    if pure.suffix == ".sh" or path == ".githooks/pre-commit":
        return "shell"
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
        text = decode_text((ROOT / path).read_bytes(), path)
        candidates.append(Candidate(path=path, kind=kind, is_new=False, text=text))
    return candidates


def collect_python_shapes(text: str) -> tuple[list[DefinitionShape], list[DefinitionShape]]:
    tree = ast.parse(text)
    visitor = ShapeVisitor()
    visitor.visit(tree)
    return visitor.functions, visitor.classes


def summarize(items: list[DefinitionShape], limit: int) -> str:
    offenders = [item for item in items if item.lines > limit]
    offenders.sort(key=lambda item: item.lines, reverse=True)
    preview = ", ".join(f"{item.qualname} ({item.lines})" for item in offenders[:3])
    if len(offenders) > 3:
        preview += f", +{len(offenders) - 3} more"
    return preview


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


def check_candidate(
    candidate: Candidate,
    config: Config,
    errors: list[str],
    warnings: list[str],
) -> None:
    line_count = len(candidate.text.splitlines())
    if candidate.kind == "python":
        add_length_findings(
            errors,
            warnings,
            path=candidate.path,
            label="Python file",
            limit=config.python_file,
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
        return

    add_length_findings(
        errors,
        warnings,
        path=candidate.path,
        label="shell file",
        limit=config.shell_file,
        actual=line_count,
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
