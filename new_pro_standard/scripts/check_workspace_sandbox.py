#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path
from typing import Any


DEFAULT_MANIFEST = "docs/ai/standards/workspace-sandbox-manifest.toml"
REQUIRED_KEYS = {
    "workspace": ("repo_root", "current_cwd", "intent"),
    "sandbox": (
        "writable_roots",
        "network_default",
        "approval_policy",
        "subagent_isolation_rule",
    ),
    "runtime": ("dirs",),
    "outputs": ("dirs",),
    "rehydration": ("inputs",),
    "claims": ("forbidden",),
}
FORBIDDEN_CLAIM_TOKENS = ("openai", "mcp", "a2a", "otlp")
OPEN_NETWORK_VALUES = {"open", "unrestricted", "public", "enabled"}
AUTO_APPROVAL_MARKERS = ("auto external", "automatic external", "without approval")
APPROVAL_DENIAL_MARKERS = ("never", "no ", "not ", "without automatic")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the repo-local workspace sandbox manifest.")
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST, help=f"Manifest path. Default: {DEFAULT_MANIFEST}")
    return parser.parse_args()


def load_manifest(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)
    except FileNotFoundError:
        return None, [f"manifest not found: {path}"]
    except tomllib.TOMLDecodeError as exc:
        return None, [f"manifest TOML is invalid: {exc}"]
    return data, []


def repo_base_for_manifest(manifest_path: Path) -> Path:
    parent = manifest_path.resolve().parent
    return parent.parent if parent.name == ".codex" else Path.cwd().resolve()


def string_list(value: Any) -> list[str] | None:
    if isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value):
        return value
    return None


def resolve_declared_path(value: str, repo_base: Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = repo_base / path
    return path.resolve()


def is_repo_internal(value: str, repo_base: Path) -> bool:
    try:
        resolve_declared_path(value, repo_base).relative_to(repo_base.resolve())
    except ValueError:
        return False
    return True


def has_required_forbidden_claims(claims: list[str]) -> bool:
    combined = " ".join(claims).lower()
    return "external" in combined and all(token in combined for token in FORBIDDEN_CLAIM_TOKENS)


def validate_manifest(data: dict[str, Any], manifest_path: Path) -> list[str]:
    errors: list[str] = []
    repo_base = repo_base_for_manifest(manifest_path)
    if data.get("version") != 1:
        errors.append("version must be 1")

    for section, keys in REQUIRED_KEYS.items():
        value = data.get(section)
        if not isinstance(value, dict):
            errors.append(f"missing section [{section}]")
            continue
        for key in keys:
            if key not in value:
                errors.append(f"missing key [{section}].{key}")

    workspace = data.get("workspace", {})
    sandbox = data.get("sandbox", {})
    runtime = data.get("runtime", {})
    outputs = data.get("outputs", {})
    rehydration = data.get("rehydration", {})
    claims = data.get("claims", {})

    repo_root = workspace.get("repo_root")
    current_cwd = workspace.get("current_cwd")
    writable_roots = string_list(sandbox.get("writable_roots"))
    if isinstance(repo_root, str) and isinstance(current_cwd, str) and writable_roots is not None:
        declared_repo = resolve_declared_path(repo_root, repo_base)
        declared_cwd = resolve_declared_path(current_cwd, repo_base)
        writable_paths = [resolve_declared_path(path, repo_base) for path in writable_roots]
        if declared_repo not in writable_paths and declared_cwd not in writable_paths:
            errors.append("sandbox.writable_roots must include workspace.repo_root or workspace.current_cwd")
    elif "writable_roots" in sandbox:
        errors.append("sandbox.writable_roots must be a non-empty list of strings")

    network_default = sandbox.get("network_default")
    if isinstance(network_default, str) and network_default.strip().lower() in OPEN_NETWORK_VALUES:
        errors.append("sandbox.network_default must not be open")

    approval_policy = sandbox.get("approval_policy")
    if isinstance(approval_policy, str):
        normalized_policy = approval_policy.replace("-", " ").replace("_", " ").lower()
        requires_auto_external = any(marker in normalized_policy for marker in AUTO_APPROVAL_MARKERS)
        denies_auto_external = any(marker in normalized_policy for marker in APPROVAL_DENIAL_MARKERS)
        if requires_auto_external and not denies_auto_external:
            errors.append("sandbox.approval_policy must not require automatic external permissions")

    for section_name, section in (
        ("runtime", runtime),
        ("outputs", outputs),
        ("rehydration", rehydration),
    ):
        key = "inputs" if section_name == "rehydration" else "dirs"
        paths = string_list(section.get(key))
        if paths is None:
            if key in section:
                errors.append(f"{section_name}.{key} must be a non-empty list of strings")
            continue
        for path in paths:
            if not is_repo_internal(path, repo_base):
                errors.append(f"{section_name}.{key} contains path outside repo: {path}")

    forbidden_claims = string_list(claims.get("forbidden"))
    if forbidden_claims is None:
        if "forbidden" in claims:
            errors.append("claims.forbidden must be a non-empty list of strings")
    elif not has_required_forbidden_claims(forbidden_claims):
        errors.append("claims.forbidden must prohibit external OpenAI/MCP/A2A/OTLP interop claims")

    return errors


def main() -> int:
    args = parse_args()
    manifest_path = Path(args.manifest)
    data, errors = load_manifest(manifest_path)
    if data is not None:
        errors.extend(validate_manifest(data, manifest_path))

    if errors:
        print("Workspace sandbox manifest failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Workspace sandbox manifest OK: {manifest_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
