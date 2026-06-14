#!/usr/bin/env python3

from __future__ import annotations

import ast
import re
from dataclasses import dataclass


DEFAULT_ENABLED = False
DEFAULT_ENV_TEMPLATE_PATHS: tuple[str, ...] = ()
DEFAULT_LOCAL_ENV_PATHS = (".env", ".env.local")
DEFAULT_REGISTRY_PATHS: tuple[str, ...] = ()
DEFAULT_SCAN_ROOTS: tuple[str, ...] = ()
DEFAULT_ALLOWED_LITERAL_PATHS: tuple[str, ...] = ()
DEFAULT_SECRET_KEY_PATTERNS: tuple[str, ...] = ()
DEFAULT_CONFIG_KEY_PATTERNS: tuple[str, ...] = ()
DEFAULT_LITERAL_PATTERNS: tuple[str, ...] = ()


@dataclass(frozen=True)
class ConfigContractsConfig:
    enabled: bool
    env_template_paths: tuple[str, ...]
    local_env_paths: tuple[str, ...]
    registry_paths: tuple[str, ...]
    scan_roots: tuple[str, ...]
    allowed_literal_paths: tuple[str, ...]
    secret_key_patterns: tuple[str, ...]
    config_key_patterns: tuple[str, ...]
    literal_patterns: tuple[str, ...]


def load_config_contracts(raw_value: object) -> ConfigContractsConfig:
    if raw_value is None:
        raw_value = {}
    if not isinstance(raw_value, dict):
        raise ValueError("[config_contracts] must be a table")

    return ConfigContractsConfig(
        enabled=bool_value(raw_value.get("enabled"), default=DEFAULT_ENABLED, label="enabled"),
        env_template_paths=string_tuple(
            raw_value.get("env_template_paths"),
            default=DEFAULT_ENV_TEMPLATE_PATHS,
            label="env_template_paths",
        ),
        local_env_paths=string_tuple(
            raw_value.get("local_env_paths"),
            default=DEFAULT_LOCAL_ENV_PATHS,
            label="local_env_paths",
        ),
        registry_paths=string_tuple(
            raw_value.get("registry_paths"),
            default=DEFAULT_REGISTRY_PATHS,
            label="registry_paths",
        ),
        scan_roots=string_tuple(
            raw_value.get("scan_roots"),
            default=DEFAULT_SCAN_ROOTS,
            label="scan_roots",
        ),
        allowed_literal_paths=string_tuple(
            raw_value.get("allowed_literal_paths"),
            default=DEFAULT_ALLOWED_LITERAL_PATHS,
            label="allowed_literal_paths",
        ),
        secret_key_patterns=string_tuple(
            raw_value.get("secret_key_patterns"),
            default=DEFAULT_SECRET_KEY_PATTERNS,
            label="secret_key_patterns",
        ),
        config_key_patterns=string_tuple(
            raw_value.get("config_key_patterns"),
            default=DEFAULT_CONFIG_KEY_PATTERNS,
            label="config_key_patterns",
        ),
        literal_patterns=string_tuple(
            raw_value.get("literal_patterns"),
            default=DEFAULT_LITERAL_PATTERNS,
            label="literal_patterns",
        ),
    )


def parse_config_contracts_section(section_text: str) -> dict[str, object]:
    values: dict[str, object] = {}
    if (enabled := parse_bool(section_text, "enabled")) is not None:
        values["enabled"] = enabled
    for key in (
        "env_template_paths",
        "local_env_paths",
        "registry_paths",
        "scan_roots",
        "allowed_literal_paths",
        "secret_key_patterns",
        "config_key_patterns",
        "literal_patterns",
    ):
        if value := parse_string_array(section_text, key):
            values[key] = value
    return values


def string_tuple(value: object, *, default: tuple[str, ...], label: str) -> tuple[str, ...]:
    if value is None:
        return default
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"config_contracts.{label} must be a list of strings")
    return tuple(value)


def bool_value(value: object, *, default: bool, label: str) -> bool:
    if value is None:
        return default
    if not isinstance(value, bool):
        raise ValueError(f"config_contracts.{label} must be a boolean")
    return value


def parse_bool(section_text: str, key: str) -> bool | None:
    match = re.search(rf"(?m)^\s*{re.escape(key)}\s*=\s*(true|false)\s*$", section_text)
    if not match:
        return None
    return match.group(1) == "true"


def parse_string_array(section_text: str, key: str) -> list[str] | None:
    match = re.search(rf"(?m)^\s*{re.escape(key)}\s*=\s*", section_text)
    if not match:
        return None
    parsed = ast.literal_eval(extract_array_literal(section_text, start=match.end(), key=key))
    if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
        raise ValueError(f"{key} must be a list of strings")
    return parsed


def extract_array_literal(section_text: str, *, start: int, key: str) -> str:
    index = start
    while index < len(section_text) and section_text[index].isspace():
        index += 1
    if index >= len(section_text) or section_text[index] != "[":
        raise ValueError(f"{key} must be a list")

    depth = 0
    quote = ""
    escape = False
    for position in range(index, len(section_text)):
        char = section_text[position]
        if quote:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == quote:
                quote = ""
            continue
        if char in ("'", '"'):
            quote = char
        elif char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                return section_text[index : position + 1]
    raise ValueError(f"could not parse {key}")
