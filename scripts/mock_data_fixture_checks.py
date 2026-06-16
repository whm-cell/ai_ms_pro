from __future__ import annotations

import json
from pathlib import Path
import re

from mock_data_boundary_lib import MockDataBoundaryConfig, MockDataFinding, matches_any, relative
from mock_data_manifest import SUGGESTED_SCENARIO_PATHS


FIXTURE_ARRAY_ASSIGN_RE = re.compile(
    r"(?P<prefix>(?:export\s+)?(?:const|let|var)\s+)(?P<name>[A-Za-z_$][\w$]*)(?:\s*:\s*[^=]+)?\s*=\s*\[",
    re.MULTILINE,
)
FIXTURE_ARRAY_FROM_RE = re.compile(
    r"(?:const|let|var)\s+(?P<name>[A-Za-z_$][\w$]*)(?:\s*:\s*[^=]+)?\s*=\s*Array\.from\(\s*\{\s*length\s*:\s*(?P<count>\d+)",
    re.MULTILINE,
)
FAKER_RE = re.compile(r"\bfaker\.")
FAKER_SEED_RE = re.compile(r"\bfaker\.seed\s*\(")


def scan_fixture_file(
    root: Path,
    path: Path,
    text: str,
    config: MockDataBoundaryConfig,
    manifest_paths: set[str],
) -> list[MockDataFinding]:
    rel_path = relative(path, root)
    findings: list[MockDataFinding] = []
    if matches_any(rel_path, config.manifest_required_paths) and fixture_requires_manifest(path, text, config):
        if rel_path not in manifest_paths:
            findings.append(
                MockDataFinding(
                    path=rel_path,
                    line=1,
                    code="fixture-without-scenario-manifest",
                    message="large fixture data must be bound to a mock-data-scenario/v1 manifest row",
                    suggested_layer="scenario-manifest",
                    suggested_paths=config.scenario_manifest_paths,
                )
            )
    findings.extend(scan_unseeded_fixture_factory(root, path, text))
    return findings


def fixture_requires_manifest(path: Path, text: str, config: MockDataBoundaryConfig) -> bool:
    if path.suffix == ".json":
        try:
            value = json.loads(text)
        except json.JSONDecodeError:
            return False
        return isinstance(value, list) and len(value) > config.max_inline_object_items
    for match in FIXTURE_ARRAY_ASSIGN_RE.finditer(text):
        block = bracket_block(text, match.end() - 1)
        if not block:
            continue
        if count_object_items(block) > config.max_inline_object_items or block.count("\n") + 1 > config.max_inline_lines:
            return True
    for match in FIXTURE_ARRAY_FROM_RE.finditer(text):
        if int(match.group("count")) > config.max_inline_array_from_length:
            return True
    return False


def scan_unseeded_fixture_factory(root: Path, path: Path, text: str) -> list[MockDataFinding]:
    math_random_at = text.find("Math.random(")
    if math_random_at >= 0:
        return [
            finding(
                root,
                path,
                text,
                math_random_at,
                "fixture/scenario factory uses Math.random(); prefer deterministic seed data",
            )
        ]
    faker_match = FAKER_RE.search(text)
    if faker_match and not FAKER_SEED_RE.search(text):
        return [
            finding(
                root,
                path,
                text,
                faker_match.start(),
                "fixture/scenario factory uses faker without faker.seed(); add deterministic seed",
            )
        ]
    return []


def bracket_block(text: str, start: int) -> str:
    depth = 0
    in_string: str | None = None
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == in_string:
                in_string = None
            continue
        if char in {"'", '"', "`"}:
            in_string = char
            continue
        if char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return ""


def count_object_items(block: str) -> int:
    return sum(1 for line in block.splitlines() if line.strip().startswith("{"))


def finding(root: Path, path: Path, text: str, offset: int, message: str) -> MockDataFinding:
    return MockDataFinding(
        path=relative(path, root),
        line=text.count("\n", 0, offset) + 1,
        code="unseeded-fixture-factory",
        message=message,
        suggested_layer="deterministic-scenario-factory",
        suggested_paths=SUGGESTED_SCENARIO_PATHS,
    )
