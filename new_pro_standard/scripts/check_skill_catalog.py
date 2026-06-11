#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ".codex/skills.catalog.json"
LOCK_PATH = ".codex/skills.lock.json"
SKILL_ROOTS = (".agents/skills", ".codex/skills")
RAW_DESCRIPTION_WORD_BUDGET = 80
DISCOVERY_DESCRIPTION_WORD_BUDGET = 40
OUTPUT_BYTE_BUDGET = 32_000
PROXY_TRUST_VALUES = {"proxy", "vendor"}
TRUST_VALUES = {"first-party", "local", "proxy", "vendor", "third-party", "unknown"}
RISK_VALUES = {"low", "medium", "high", "unknown"}
PERMISSION_KEYS = ("write_files", "execute_commands", "network", "external_services")
SOURCE_URL_KEYS = ("source_url", "url")
SOURCE_REVISION_KEYS = ("source_commit", "commit", "source_hash", "hash")
INSTRUCTION_LIKE_PATTERNS = (
    re.compile(r"\b(ignore|disregard)\s+(all\s+)?(previous|prior|above)\s+instructions\b", re.I),
    re.compile(r"\b(system|developer|assistant)\s*[_ -]?\s*(override|prompt|instruction)s?\b", re.I),
    re.compile(r"\bBEGIN\s+(SYSTEM|DEVELOPER|TOOL|SKILL)\s+(PROMPT|INSTRUCTIONS?)\b", re.I),
    re.compile(r"\btool\s*call\s*:\s*\{", re.I),
    re.compile(r"\bexfiltrate\b|\bsteal\s+(secrets?|tokens?|keys?)\b", re.I),
)
@dataclass(frozen=True)
class Skill:
    name: str; path: Path; repo_path: str; description: str; word_count: int
@dataclass(frozen=True)
class SkillCatalogReport:
    skills: list[Skill]; catalog_entries: dict[str, dict[str, object]]
    lock_entries: dict[str, dict[str, object]]; errors: list[str]; warnings: list[str]
@dataclass(frozen=True)
class OutputCheckReport:
    path: str; original_bytes: int; truncated: bool; scanned_bytes: int; findings: list[str]
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit repo-local skill catalog metadata.")
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures.")
    parser.add_argument(
        "--raw-description-words", type=int, default=RAW_DESCRIPTION_WORD_BUDGET,
        help="Word budget for SKILL.md frontmatter descriptions.",
    )
    parser.add_argument(
        "--discovery-description-words", type=int, default=DISCOVERY_DESCRIPTION_WORD_BUDGET,
        help="Word budget for catalog discovery_description.",
    )
    parser.add_argument("--check-output", help="Scan tool/skill output for instructions.")
    parser.add_argument(
        "--output-bytes", type=int, default=OUTPUT_BYTE_BUDGET,
        help="Maximum bytes to scan with --check-output.",
    )
    return parser.parse_args()
def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()
def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]", text))
def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    metadata: dict[str, str] = {}
    current_key = ""
    current_value: list[str] = []
    for raw_line in parts[1].splitlines():
        if raw_line.startswith((" ", "\t")) and current_key:
            current_value.append(raw_line.strip())
            continue
        if current_key:
            metadata[current_key] = " ".join(current_value).strip().strip("'\"")
        if ":" not in raw_line:
            current_key = ""
            current_value = []
            continue
        key, value = raw_line.split(":", 1)
        current_key = key.strip()
        current_value = [value.strip()]
    if current_key:
        metadata[current_key] = " ".join(current_value).strip().strip("'\"")
    return metadata
def discover_skills(root: Path, errors: list[str]) -> list[Skill]:
    skills: list[Skill] = []
    for rel_root in SKILL_ROOTS:
        for path in sorted((root / rel_root).rglob("SKILL.md")):
            try:
                metadata = frontmatter(path.read_text(encoding="utf-8"))
            except OSError as exc:
                errors.append(f"could not read {relative(path, root)}: {exc}")
                continue
            description = metadata.get("description", "").strip()
            skills.append(
                Skill(
                    name=metadata.get("name") or path.parent.name,
                    path=path,
                    repo_path=relative(path, root),
                    description=description,
                    word_count=word_count(description),
                )
            )
    return skills
def load_metadata_file(
    root: Path, rel_path: str, errors: list[str]
) -> dict[str, dict[str, object]]:
    path = root / rel_path
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{rel_path} is not valid JSON: {exc}")
        return {}
    if not isinstance(raw, dict):
        errors.append(f"{rel_path} must be a JSON object keyed by skill name")
        return {}
    entries: dict[str, dict[str, object]] = {}
    for name, entry in raw.items():
        if not isinstance(name, str) or not name:
            errors.append(f"{rel_path} contains a non-string skill name")
        elif not isinstance(entry, dict):
            errors.append(f"{rel_path} entry {name} must be an object")
        else:
            entries[name] = entry
    return entries
def catalog_entry_enabled(entry: dict[str, object]) -> bool:
    return bool(entry.get("enabled", True))
def first_present(entry: dict[str, object], keys: tuple[str, ...]) -> object:
    return next((entry[key] for key in keys if entry.get(key) not in (None, "")), None)
def resolve_catalog_path(
    root: Path, raw_path: object, label: str
) -> tuple[Path | None, str | None]:
    if not isinstance(raw_path, str) or not raw_path.strip():
        return None, f"{label} must be a non-empty string"
    candidate = (root / raw_path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None, f"{label} escapes repo root: {raw_path}"
    return candidate, None
def validate_metadata_shape(
    entries: dict[str, dict[str, object]], rel_path: str, errors: list[str]
) -> None:
    for name, entry in entries.items():
        label = f"{rel_path}:{name}"
        if "enabled" not in entry:
            errors.append(f"{label}.enabled must be present")
        elif not isinstance(entry["enabled"], bool):
            errors.append(f"{label}.enabled must be a boolean")
        if not catalog_entry_enabled(entry):
            continue
        if not isinstance(first_present(entry, SOURCE_URL_KEYS), str):
            errors.append(f"{label} must include source_url or url")
        if not isinstance(first_present(entry, SOURCE_REVISION_KEYS), str):
            errors.append(f"{label} must include source_commit, commit, source_hash, or hash")
        if not isinstance(entry.get("license"), str) or not str(entry.get("license")).strip():
            errors.append(f"{label}.license must be a non-empty string")
        if str(entry.get("trust", "")).strip().lower() not in TRUST_VALUES:
            errors.append(f"{label}.trust must be one of: {', '.join(sorted(TRUST_VALUES))}")
        if str(entry.get("risk", "")).strip().lower() not in RISK_VALUES:
            errors.append(f"{label}.risk must be one of: {', '.join(sorted(RISK_VALUES))}")
        permissions = entry.get("permissions")
        if not isinstance(permissions, dict):
            errors.append(f"{label}.permissions must be an object")
            continue
        for key in PERMISSION_KEYS:
            if not isinstance(permissions.get(key), bool):
                errors.append(f"{label}.permissions.{key} must be a boolean")
def validate_catalog_paths(
    root: Path,
    catalog: dict[str, dict[str, object]],
    skill_paths_by_name: dict[str, set[str]],
    errors: list[str],
) -> None:
    for name, entry in catalog.items():
        if not catalog_entry_enabled(entry):
            continue
        if "path" in entry:
            path, error = resolve_catalog_path(root, entry["path"], f"{name}.path")
            if error:
                errors.append(error)
            elif not path.exists():
                errors.append(f"{name}.path does not exist: {entry['path']}")
            elif path.name != "SKILL.md":
                errors.append(f"{name}.path must point at a SKILL.md file: {entry['path']}")
            elif relative(path, root) not in skill_paths_by_name.get(name, set()):
                errors.append(f"{name}.path does not match a discovered skill named {name}")
        if str(entry.get("trust", "")).strip().lower() in PROXY_TRUST_VALUES:
            vendor_path, error = resolve_catalog_path(root, entry.get("vendor_path"), f"{name}.vendor_path")
            if error:
                errors.append(error)
            elif not vendor_path.exists():
                errors.append(f"{name}.vendor_path does not exist: {entry['vendor_path']}")
def validate_catalog_descriptions(
    catalog: dict[str, dict[str, object]], discovery_budget: int, errors: list[str]
) -> None:
    for name, entry in catalog.items():
        if not catalog_entry_enabled(entry):
            continue
        description = entry.get("discovery_description", "")
        if not isinstance(description, str) or not description.strip():
            errors.append(f"{name}.discovery_description must be a non-empty string")
            continue
        actual = word_count(description)
        if actual > discovery_budget:
            errors.append(f"{name}.discovery_description has {actual} words (> {discovery_budget})")
def validate_lock_consistency(
    catalog: dict[str, dict[str, object]],
    lock: dict[str, dict[str, object]],
    errors: list[str],
) -> None:
    for name, entry in catalog.items():
        if not catalog_entry_enabled(entry):
            continue
        if name not in lock:
            errors.append(f"{name} is enabled in {CATALOG_PATH} but missing from {LOCK_PATH}")
            continue
        if first_present(entry, SOURCE_REVISION_KEYS) != first_present(lock[name], SOURCE_REVISION_KEYS):
            errors.append(f"{name} source revision differs between catalog and lock")
def has_valid_proxy_catalog_entry(
    skill: Skill,
    root: Path,
    catalog: dict[str, dict[str, object]],
    discovery_budget: int,
) -> bool:
    entry = catalog.get(skill.name)
    if not entry or not catalog_entry_enabled(entry):
        return False
    description = entry.get("discovery_description", "")
    trust = str(entry.get("trust", "")).strip().lower()
    if trust not in PROXY_TRUST_VALUES or not isinstance(description, str):
        return False
    if word_count(description) > discovery_budget:
        return False
    vendor_path, error = resolve_catalog_path(root, entry.get("vendor_path"), f"{skill.name}.vendor_path")
    if error or vendor_path is None or not vendor_path.exists():
        return False
    if "path" not in entry:
        return True
    path, error = resolve_catalog_path(root, entry["path"], f"{skill.name}.path")
    return error is None and path == skill.path
def validate_duplicate_names(skills: list[Skill], errors: list[str]) -> None:
    by_name: dict[str, list[str]] = {}
    for skill in skills:
        by_name.setdefault(skill.name, []).append(skill.repo_path)
    for name, paths in sorted(by_name.items()):
        if len(paths) > 1:
            errors.append(f"duplicate skill name {name}: {', '.join(paths)}")
def check_output_text(text: str) -> list[str]:
    findings: list[str] = []
    for pattern in INSTRUCTION_LIKE_PATTERNS:
        if match := pattern.search(text):
            findings.append(f"instruction-like output matched: {match.group(0)}")
    return findings
def check_output_file(path: Path, *, byte_budget: int = OUTPUT_BYTE_BUDGET) -> OutputCheckReport:
    if byte_budget < 1:
        raise ValueError("byte_budget must be positive")
    raw = path.read_bytes()
    scanned = raw[:byte_budget]
    return OutputCheckReport(
        path=str(path),
        original_bytes=len(raw),
        truncated=len(raw) > byte_budget,
        scanned_bytes=len(scanned),
        findings=check_output_text(scanned.decode("utf-8", errors="replace")),
    )
def build_report(
    root: Path,
    *,
    raw_description_budget: int = RAW_DESCRIPTION_WORD_BUDGET,
    discovery_budget: int = DISCOVERY_DESCRIPTION_WORD_BUDGET,
) -> SkillCatalogReport:
    errors: list[str] = []
    warnings: list[str] = []
    root = root.resolve()
    catalog = load_metadata_file(root, CATALOG_PATH, errors)
    lock = load_metadata_file(root, LOCK_PATH, errors)
    skills = discover_skills(root, errors)
    validate_duplicate_names(skills, errors)
    paths_by_name: dict[str, set[str]] = {}
    for skill in skills:
        paths_by_name.setdefault(skill.name, set()).add(skill.repo_path)
    validate_catalog_paths(root, catalog, paths_by_name, errors)
    validate_metadata_shape(catalog, CATALOG_PATH, errors)
    validate_metadata_shape(lock, LOCK_PATH, errors)
    if lock:
        validate_lock_consistency(catalog, lock, errors)
    validate_catalog_descriptions(catalog, discovery_budget, errors)
    for skill in skills:
        if skill.word_count <= raw_description_budget:
            continue
        if has_valid_proxy_catalog_entry(skill, root, catalog, discovery_budget):
            continue
        warnings.append(
            f"{skill.repo_path} description has {skill.word_count} words "
            f"(> {raw_description_budget}); add a short {CATALOG_PATH} "
            "vendor/proxy entry instead of using raw SKILL.md as discovery text"
        )
    return SkillCatalogReport(skills, catalog, lock, errors, warnings)
def print_text_report(report: SkillCatalogReport, root: Path) -> None:
    print("Skill catalog checks:")
    print(f"- Repo root: {root}")
    print(f"- Catalog: {CATALOG_PATH}")
    print(f"- Lock: {LOCK_PATH}")
    print(f"- Skills discovered: {len(report.skills)}")
    for skill in report.skills:
        print(f"- {skill.name}: {skill.repo_path}; description_words={skill.word_count}")
    for message in report.errors:
        print(f"ERROR: {message}")
    for message in report.warnings:
        print(f"WARN: {message}")
def print_output_report(report: OutputCheckReport, json_output: bool) -> None:
    if json_output:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
        return
    print("Skill output check:")
    print(f"- File: {report.path}")
    print(f"- Original bytes: {report.original_bytes}")
    print(f"- Scanned bytes: {report.scanned_bytes}")
    print(f"- Truncated: {report.truncated}")
    for finding in report.findings:
        print(f"ERROR: {finding}")
def main() -> int:
    args = parse_args()
    if args.check_output:
        output_report = check_output_file(Path(args.check_output).expanduser().resolve(), byte_budget=args.output_bytes)
        print_output_report(output_report, args.json)
        return 1 if output_report.findings else 0
    root = Path(args.root).expanduser().resolve()
    report = build_report(
        root,
        raw_description_budget=args.raw_description_words,
        discovery_budget=args.discovery_description_words,
    )
    if args.json:
        payload = asdict(report)
        for skill in payload["skills"]:
            skill["path"] = str(skill["path"])
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_text_report(report, root)
    return 1 if report.errors or (args.strict and report.warnings) else 0
if __name__ == "__main__": sys.exit(main())
