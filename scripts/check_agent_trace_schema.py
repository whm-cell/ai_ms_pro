#!/usr/bin/env python3

from __future__ import annotations

import argparse
from datetime import datetime
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = ROOT / "docs" / "ai" / "standards" / "agent-trace.schema.json"
DEFAULT_SAMPLE = ROOT / "docs" / "ai" / "standards" / "agent-trace-sample.jsonl"
SUPPORTED_SCHEMA = "http://json-schema.org/draft-07/schema#"


class ValidationError(ValueError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate repo-local agent trace schema and JSONL samples.")
    parser.add_argument("--schema", default=str(DEFAULT_SCHEMA), help="Path to Draft-07 JSON Schema.")
    parser.add_argument("--sample", default=str(DEFAULT_SAMPLE), help="Path to JSONL trace sample.")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"{path}: schema must be a JSON object")
    return value


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValidationError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise ValidationError(f"{path}:{line_number}: record must be an object")
        records.append(value)
    if not records:
        raise ValidationError(f"{path}: sample must contain at least one record")
    return records


def json_type(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int) and not isinstance(value, bool):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def type_matches(value: Any, expected: Any) -> bool:
    expected_types = expected if isinstance(expected, list) else [expected]
    actual = json_type(value)
    return any(
        actual == item or (item == "number" and actual == "integer")
        for item in expected_types
    )


def validate_schema_shape(schema: dict[str, Any]) -> None:
    if schema.get("$schema") != SUPPORTED_SCHEMA:
        raise ValidationError(f"schema $schema must be {SUPPORTED_SCHEMA}")
    if schema.get("type") != "object":
        raise ValidationError("schema root type must be object")
    required = schema.get("required")
    properties = schema.get("properties")
    if not isinstance(required, list) or not required:
        raise ValidationError("schema required must be a non-empty list")
    if not isinstance(properties, dict) or not properties:
        raise ValidationError("schema properties must be a non-empty object")
    for field in required:
        if field not in properties:
            raise ValidationError(f"schema required field has no property: {field}")


def validate_object(value: dict[str, Any], schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []
    for field in schema.get("required", []):
        if field not in value:
            errors.append(f"{path}.{field}: missing required field")
    properties = schema.get("properties", {})
    additional = schema.get("additionalProperties", True)
    for key, item in value.items():
        field_schema = properties.get(key)
        if field_schema is None:
            if additional is False:
                errors.append(f"{path}.{key}: unexpected field")
            elif isinstance(additional, dict):
                errors.extend(validate_value(item, additional, f"{path}.{key}"))
            continue
        errors.extend(validate_value(item, field_schema, f"{path}.{key}"))
    return errors


def validate_value(value: Any, schema: dict[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    expected_type = schema.get("type")
    if expected_type is not None and not type_matches(value, expected_type):
        return [f"{path}: expected {expected_type}, got {json_type(value)}"]
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: expected one of {schema['enum']!r}")
    if isinstance(value, str):
        errors.extend(validate_string(value, schema, path))
        errors.extend(validate_format(value, schema, path))
    if isinstance(value, list):
        errors.extend(validate_array(value, schema, path))
    if isinstance(value, dict):
        errors.extend(validate_object(value, schema, path))
    return errors


def validate_string(value: str, schema: dict[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    if len(value) < schema.get("minLength", 0):
        errors.append(f"{path}: shorter than minLength")
    if "maxLength" in schema and len(value) > schema["maxLength"]:
        errors.append(f"{path}: longer than maxLength")
    if "pattern" in schema and not re.search(schema["pattern"], value):
        errors.append(f"{path}: does not match pattern {schema['pattern']!r}")
    return errors


def validate_format(value: str, schema: dict[str, Any], path: str) -> list[str]:
    if schema.get("format") != "date-time":
        return []
    if not value.endswith("Z"):
        return [f"{path}: expected RFC3339 UTC timestamp ending with Z"]
    try:
        datetime.fromisoformat(value.removesuffix("Z") + "+00:00")
    except ValueError:
        return [f"{path}: invalid RFC3339 date-time"]
    return []


def validate_array(value: list[Any], schema: dict[str, Any], path: str) -> list[str]:
    errors: list[str] = []
    item_schema = schema.get("items")
    if isinstance(item_schema, dict):
        for index, item in enumerate(value):
            errors.extend(validate_value(item, item_schema, f"{path}[{index}]"))
    if schema.get("uniqueItems"):
        encoded = [json.dumps(item, sort_keys=True) for item in value]
        if len(encoded) != len(set(encoded)):
            errors.append(f"{path}: duplicate items")
    return errors


def validate_parent_links(records: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    span_ids: dict[str, int] = {}
    for index, record in enumerate(records, start=1):
        span_id = record.get("span_id")
        if not isinstance(span_id, str):
            continue
        if span_id in span_ids:
            errors.append(f"record {index}: duplicate span_id {span_id!r}")
        span_ids[span_id] = index
    for index, record in enumerate(records, start=1):
        span_id = record.get("span_id")
        parent = record.get("parent_span_id")
        if parent is None:
            continue
        if parent == span_id:
            errors.append(f"record {index}: parent_span_id must not reference itself")
        elif parent not in span_ids:
            errors.append(f"record {index}: parent_span_id {parent!r} does not exist")
    return errors


def validate_trace(schema_path: Path, sample_path: Path) -> list[str]:
    schema = load_json(schema_path)
    validate_schema_shape(schema)
    records = load_jsonl(sample_path)
    errors: list[str] = []
    for index, record in enumerate(records, start=1):
        errors.extend(f"record {index}: {error}" for error in validate_object(record, schema))
    errors.extend(validate_parent_links(records))
    return errors


def main() -> int:
    args = parse_args()
    try:
        errors = validate_trace(Path(args.schema), Path(args.sample))
    except ValidationError as exc:
        print(f"agent trace schema check failed: {exc}", file=sys.stderr)
        return 1
    if errors:
        print("agent trace schema check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("agent trace schema check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
